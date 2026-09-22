"""
generate_ai_post.py
--------------------
Gera um artigo de blog (Jekyll/Chirpy) + post de LinkedIn a partir de
noticias recentes de IA, usando a API do Gemini.

Principais mudancas em relacao a versao anterior:
  1. Filtro de relevancia por palavra-chave nas noticias coletadas
     (em vez de pegar cegamente os 2 primeiros itens de cada feed).
  2. User-Agent + checagem de `feed.bozo` no feedparser, para nao
     perder feeds silenciosamente.
  3. Imagem de capa/figura busca um arquivo REAL no Wikimedia Commons
     (com URL, autor e licenca verificaveis) em vez de pedir ao modelo
     para "inventar" uma citacao Creative Commons.
  4. Duas chamadas separadas ao modelo (post -> depois LinkedIn usando
     o post como contexto), em vez de um unico prompt gigante com um
     delimitador fragil.
  5. `max_output_tokens` explicito e uso do gemini-2.5-pro (o uso e
     semanal, entao o limite diario do free tier nao e o gargalo;
     capacidade de seguir uma instrucao longa e complexa, sim).
  6. Retry com backoff exponencial e checagem defensiva de
     `response.candidates` antes de acessar `response.text`.
  7. Sanitizacao do front matter mais tolerante a preambulo do modelo.
"""

import json
import os
import re
import time
import random
import datetime
import urllib.request
import urllib.parse

import feedparser
from google import genai
from google.genai import types

# --------------------------------------------------------------------------
# Configuracao
# --------------------------------------------------------------------------

MODEL_BLOG = "gemini-2.5-pro"      # melhor em seguir instrucoes longas/complexas
MODEL_LINKEDIN = "gemini-2.5-flash"  # tarefa curta, flash resolve bem e mais rapido

AUTHOR_NAME = "Marcos Vasconcellos"
BLOG_NAME = "Beyond AI Code"
OUTPUT_DIR = "_posts"

MAX_RETRIES = 4
BASE_BACKOFF_SECONDS = 8

# 11 canais de alta reputacao para veracidade e triangulacao de dados
RSS_URLS = [
    # 1. Laboratorios oficiais de IA
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    # 2. Pesquisa cientifica e academica
    "https://rss.arxiv.org/rss/cs.AI",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
    # 3. Open-source, engenharia de dados e MLOps
    "https://huggingface.co/blog/feed.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    # 4. Jornalismo especializado e de mercado
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
]

# Palavras-chave usadas para filtrar itens relevantes ao tema da semana.
# Ajuste esta lista a cada artigo (ex.: troque para termos de outro assunto).
TOPIC_KEYWORDS = [
    "agi", "general intelligence", "reasoning", "scaling law",
    "world model", "autonomous agent", "agentic", "alignment",
    "frontier model", "superintelligence", "chain of thought",
]

FEEDPARSER_USER_AGENT = (
    "Mozilla/5.0 (compatible; BeyondAICodeBot/1.0; "
    "+https://marcos-data-engineer.github.io/blog/)"
)

WIKIMEDIA_QUERY_CANDIDATES = [
    "artificial general intelligence diagram",
    "neural network architecture",
    "artificial intelligence concept",
    "robot brain",
]


# --------------------------------------------------------------------------
# Coleta de noticias (RSS)
# --------------------------------------------------------------------------

def clean_html(raw_html: str) -> str:
    """Remove tags HTML brutas para otimizar a contagem de tokens."""
    return re.sub(r"<[^>]+>", " ", raw_html)


def is_relevant(entry, keywords) -> bool:
    haystack = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(k in haystack for k in keywords)


def collect_news(rss_urls, keywords, pool_per_feed=10, take_per_feed=2):
    """
    Busca cada feed, filtra por relevancia ao topico e monta o buffer
    de contexto que vai para o prompt. Retorna (buffer_de_texto, lista_de_urls_usadas).
    """
    feedparser.USER_AGENT = FEEDPARSER_USER_AGENT

    content_buffer = ""
    used_urls = []

    print(f"Coletando dados de {len(rss_urls)} canais de pesquisa e noticias de IA...")

    for url in rss_urls:
        try:
            feed = feedparser.parse(url)

            if feed.bozo:
                print(f"⚠️ Aviso: feed com problema em {url} -> {feed.bozo_exception}")
                # continua mesmo assim: alguns feeds levantam bozo por detalhes
                # de XML mas ainda trazem `entries` utilizaveis.

            if not feed.entries:
                print(f"⚠️ Aviso: nenhum item retornado por {url} (feed vazio ou bloqueado)")
                continue

            candidates = feed.entries[:pool_per_feed]
            relevant = [e for e in candidates if is_relevant(e, keywords)]

            # Se nada bateu com as palavras-chave, cai para os mais recentes
            # (mantem o feed util mesmo em semanas de pouca cobertura do tema).
            chosen = relevant[:take_per_feed] or candidates[:take_per_feed]

            for entry in chosen:
                title = entry.get("title", "Sem titulo")
                link = entry.get("link", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                content_buffer += f"Title: {title}\nURL: {link}\nSummary: {summary[:350].strip()}\n\n"
                if link:
                    used_urls.append(link)

        except Exception as e:
            print(f"⚠️ Aviso: falha ao ler o feed {url}: {e}")

    return content_buffer, used_urls


# --------------------------------------------------------------------------
# Imagem real via Wikimedia Commons (evita citacao/licenca inventada)
# --------------------------------------------------------------------------

def _wikimedia_api_get(params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{query}",
        headers={"User-Agent": FEEDPARSER_USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_wikimedia_image(query_candidates) -> dict | None:
    """
    Procura um arquivo de imagem real no Wikimedia Commons para as
    consultas dadas (tenta cada uma ate achar um resultado com licenca
    disponivel). Retorna um dict com url da imagem, url da pagina do
    arquivo, autor e licenca -- ou None se nada foi encontrado.
    """
    for query in query_candidates:
        try:
            search = _wikimedia_api_get({
                "action": "query", "list": "search", "srnamespace": 6,
                "srsearch": query, "srlimit": 5, "format": "json",
            })
            hits = search.get("query", {}).get("search", [])
            if not hits:
                continue

            titles = "|".join(h["title"] for h in hits)
            info = _wikimedia_api_get({
                "action": "query", "titles": titles, "prop": "imageinfo",
                "iiprop": "url|extmetadata", "format": "json",
            })
            pages = info.get("query", {}).get("pages", {})
            for page in pages.values():
                imageinfo = (page.get("imageinfo") or [None])[0]
                if not imageinfo:
                    continue
                meta = imageinfo.get("extmetadata", {})
                license_short = meta.get("LicenseShortName", {}).get("value")
                artist = meta.get("Artist", {}).get("value", "Wikimedia Commons")
                if not license_short:
                    continue  # sem licenca clara, pula para nao arriscar atribuicao errada
                artist_clean = re.sub("<[^>]+>", "", artist)
                return {
                    "image_url": imageinfo["url"],
                    "page_url": f"https://commons.wikimedia.org/wiki/{page['title'].replace(' ', '_')}",
                    "license": license_short,
                    "artist": artist_clean,
                    "title": page["title"],
                }
        except Exception as e:
            print(f"⚠️ Aviso: busca no Wikimedia falhou para '{query}': {e}")
    return None


# --------------------------------------------------------------------------
# Geracao de conteudo (Gemini)
# --------------------------------------------------------------------------

def call_gemini(client, model, prompt, max_output_tokens=16000, temperature=0.85):
    """Chama o modelo com retry + backoff exponencial (com jitter)."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                ),
            )
            if not response.candidates:
                raise RuntimeError(
                    "Resposta sem candidatos (possivel bloqueio de safety filter)."
                )
            finish_reason = response.candidates[0].finish_reason
            if finish_reason and str(finish_reason).upper() not in ("STOP", "1"):
                print(f"⚠️ Aviso: finish_reason={finish_reason} (pode indicar corte no output)")
            return response.text.strip()
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = BASE_BACKOFF_SECONDS * (2 ** attempt) + random.uniform(0, 3)
                print(f"⚠️ API indisponivel ({e}). Nova tentativa em {wait:.0f}s "
                      f"({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait)
    raise last_error


def sanitize_markdown(raw_output: str) -> str:
    """
    Remove qualquer preambulo do modelo (ex.: 'Aqui esta o artigo:') e
    cercas de codigo, mantendo apenas do primeiro '---' (inicio do
    front matter) em diante.
    """
    text = raw_output.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()

    idx = text.find("---")
    if idx == -1:
        print("⚠️ Aviso: front matter '---' nao encontrado; salvando output bruto.")
        return text
    return text[idx:].strip()


def build_blog_prompt(content_buffer, image_info, date_front_matter):
    image_block = ""
    if image_info:
        image_block = f"""
A REAL, VERIFIED Creative Commons image is available for this article. Use it as
the front-matter cover AND as the single embedded <figure> in the introduction.
DO NOT invent any other Wikimedia Commons file, filename, or license — use ONLY
the data below, copied exactly:
  - Image URL: {image_info['image_url']}
  - Wikimedia Commons page: {image_info['page_url']}
  - Artist / credit: {image_info['artist']}
  - License: {image_info['license']}
"""
    else:
        image_block = """
No verified Creative Commons image was found this run. Use
https://picsum.photos/seed/agi-architecture/1200/630 as a purely decorative
placeholder image for the front-matter cover, and do NOT attach any Wikimedia
Commons / Creative Commons attribution to it (it is a random stock photo, not
a licensed research image). Do not include an embedded <figure> with a fake
Commons citation anywhere in the article.
"""

    return f"""
You are {AUTHOR_NAME}, a Senior AI Architect, Data Engineer, and Author of the
blog '{BLOG_NAME}'.

Your task is to write a benchmark-quality technical blog post in International
English about Artificial General Intelligence (AGI), analyzing current
frontier research and connecting it as a direct sequel to our foundational
article 'The History of Artificial Intelligence'.

OUTPUT RULES (STRICT):
- Output ONLY the raw Markdown file, starting with the front matter '---'.
- No preamble, no explanation, no "Here is the article" text before or after.
- Do not wrap the output in a code fence.

EDITORIAL & VISUAL REQUIREMENTS (MUST STRICTLY MATCH THE QUALITY OF
'THE HISTORY OF ARTIFICIAL INTELLIGENCE'):

1. FRONT MATTER (JEKYLL / CHIRPY):
---
layout: post
title: "INSERT_DIRECT_TECHNICAL_AGI_TITLE"
date: {date_front_matter}
categories: [Artificial Intelligence, AGI]
tags: [agi, artificial-general-intelligence, llm, ai-history, future-of-ai, data-engineering]
description: "INSERT_AN_ENGAGING_SUMMARY_UP_TO_160_CHARS_ABOUT_THE_ROAD_TO_AGI"
lang: en
author: {AUTHOR_NAME}
image:
  path: INSERT_COVER_IMAGE_URL
  alt: "Conceptual illustration of Artificial General Intelligence and Cognitive Scaling"
published: false
---

2. NARRATIVE BRIDGE:
- Opening quote using <blockquote>...</blockquote> and <cite>...</cite> from a
  prominent scientist, philosopher, or AI pioneer (use a real, verifiable quote).
- Begin the introductory body by building a narrative bridge from 'The History
  of Artificial Intelligence' (which covered Alan Turing, Dartmouth 1956, Deep
  Blue, and Generative AI) to today's race toward AGI.
- Frame the collected news below (scaling laws, world models, reasoning
  chains, autonomous agents, and alignment) as the core pillars for bridging
  Narrow AI to AGI. Only cite facts that are actually supported by the
  collected items — do not invent statistics, paper titles, or benchmarks
  that are not present in the source material below.

3. RICH VISUAL COMPONENTS & EMBEDDED HTML/CSS:
{image_block}
- Embed a custom <style>...</style> inline block (e.g., custom callout boxes,
  an "AGI readiness" card, or a timeline CSS wrapper), matching the visual
  density of the reference article.
- Include at least ONE Mermaid diagram (```mermaid ... ```) depicting an AGI
  cognitive architecture, agentic decision loop, or world-model data flow.
- Include a Markdown comparison table evaluating key metrics (e.g.,
  Reasoning vs. Memory vs. Alignment vs. Compute) across 2–4 approaches
  actually mentioned in the source material.

4. REFERENCES & AUTHOR SIGN-OFF:
- Interweave direct Markdown hyperlinks to the ORIGINAL source URLs from the
  collected news below when referencing specific items. Do not fabricate URLs.
- Conclude strictly with these two closing sections:
  * '## 📚 References and Credits' (itemized list of the source URLs actually
    used above, plus the image credit line if an image was provided).
  * Sign-off line: '*Originally revised and adapted by {AUTHOR_NAME} — Data
    Architecture & AI Insights.*'

Collected Technical News from Verified AI Sources (use only what is relevant
and factually supported by these excerpts):
{content_buffer}
"""


def build_linkedin_prompt(blog_markdown):
    return f"""
You are {AUTHOR_NAME}, author of the blog '{BLOG_NAME}'. You just published the
blog post below. Write ONLY a LinkedIn announcement post in English:

- Punchy, ~150 words, executive tone.
- Bridges the history of AI to the current AGI research frontier covered in
  the post.
- Include 2-3 concrete takeaways from the post (do not invent new facts not
  present in the post).
- End with hashtags: #AGI #ArtificialGeneralIntelligence #DataEngineering #MLOps #FutureOfAI
- End with the call-to-action: "Read the full analysis on {BLOG_NAME}."
- Output ONLY the LinkedIn post text, no preamble, no markdown headers.

--- BLOG POST ---
{blog_markdown}
"""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        raise SystemExit(
            "❌ Defina a variavel de ambiente GEMINI_API_KEY (ou GOOGLE_API_KEY) "
            "antes de rodar este script."
        )

    client = genai.Client()

    content_buffer, used_urls = collect_news(RSS_URLS, TOPIC_KEYWORDS)
    if not content_buffer.strip():
        raise SystemExit(
            "❌ Nenhuma noticia relevante foi coletada nesta execucao. "
            "Verifique os feeds ou ajuste TOPIC_KEYWORDS e rode novamente."
        )

    print(f"📰 {len(used_urls)} itens coletados e usados como contexto.")

    print("🖼️  Buscando imagem real com licenca Creative Commons no Wikimedia Commons...")
    image_info = search_wikimedia_image(WIKIMEDIA_QUERY_CANDIDATES)
    if image_info:
        print(f"   Encontrada: {image_info['title']} ({image_info['license']})")
    else:
        print("   Nenhuma imagem com licenca clara encontrada; usando placeholder decorativo.")

    now = datetime.datetime.now()
    date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S +0000")
    date_filename = now.strftime("%Y-%m-%d")
    time_suffix = now.strftime("%H%M")

    print(f"🧠 Gerando artigo com {MODEL_BLOG}...")
    blog_prompt = build_blog_prompt(content_buffer, image_info, date_front_matter)
    blog_raw = call_gemini(client, MODEL_BLOG, blog_prompt, max_output_tokens=16000)
    blog_content = sanitize_markdown(blog_raw)

    print(f"💼 Gerando post de LinkedIn com {MODEL_LINKEDIN}...")
    linkedin_prompt = build_linkedin_prompt(blog_content)
    linkedin_content = call_gemini(
        client, MODEL_LINKEDIN, linkedin_prompt, max_output_tokens=1200, temperature=0.9
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    post_filename = f"{date_filename}-road-to-agi-{time_suffix}.md"
    with open(os.path.join(OUTPUT_DIR, post_filename), "w", encoding="utf-8") as f:
        f.write(blog_content.strip() + "\n")

    caption_filename = f"{date_filename}-linkedin-agi-caption-{time_suffix}.txt"
    with open(os.path.join(OUTPUT_DIR, caption_filename), "w", encoding="utf-8") as f:
        f.write(linkedin_content.strip() + "\n")

    print(f"✅ Artigo sobre AGI criado com sucesso em: {post_filename}")
    print(f"✅ Legenda para o LinkedIn criada em: {caption_filename}")


if __name__ == "__main__":
    main()