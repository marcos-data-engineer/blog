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
BLOG_NAME = "Arquitetura de Dados & IA"
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
A imagem Creative Commons REAL E VERIFICADA abaixo está disponível para o artigo.
Use-a como capa no front matter E como a única figura incorporada na introdução.
NÃO invente outros arquivos, nomes ou licenças do Wikimedia Commons — use SOMENTE
os dados abaixo, sem alterações:
  - Image URL: {image_info['image_url']}
  - Wikimedia Commons page: {image_info['page_url']}
  - Artist / credit: {image_info['artist']}
  - License: {image_info['license']}
"""
    else:
        image_block = """
Nenhuma imagem Creative Commons verificada foi encontrada nesta execução. Use
https://picsum.photos/seed/agi-architecture/1200/630 apenas como imagem decorativa
de capa no front matter. NÃO atribua a ela licença Creative Commons nem crédito do
Wikimedia Commons: é uma imagem aleatória, não uma imagem de pesquisa licenciada.
Não inclua no artigo nenhuma figura com crédito fictício do Commons.
"""

    return f"""
Você é {AUTHOR_NAME}, arquiteto sênior de IA, engenheiro de dados e autor do
blog '{BLOG_NAME}'.

Escreva um artigo técnico de alta qualidade, em português brasileiro natural,
sobre inteligência artificial geral (AGI). Analise pesquisas atuais de ponta e
conecte o texto como continuação direta do nosso artigo fundamental
'A história da inteligência artificial'.

REGRAS DE SAÍDA (OBRIGATÓRIAS):
- Retorne SOMENTE o arquivo Markdown bruto, começando pelo front matter '---'.
- Não inclua introdução, explicação ou texto como "Aqui está o artigo".
- Não coloque o conteúdo dentro de um bloco de código.

REQUISITOS EDITORIAIS E VISUAIS (MANTENHA A QUALIDADE DE
'A HISTÓRIA DA INTELIGÊNCIA ARTIFICIAL'):

1. FRONT MATTER (JEKYLL / CHIRPY):
---
layout: post
title: "INSIRA_UM_TÍTULO_TÉCNICO_DIRETO_SOBRE_AGI"
date: {date_front_matter}
categories: [Inteligência Artificial, AGI]
tags: [agi, inteligencia-artificial-geral, llm, historia-da-ia, futuro-da-ia, engenharia-de-dados]
description: "INSIRA_UM_RESUMO_ENVOLVENTE_DE_ATÉ_160_CARACTERES_SOBRE_O_CAMINHO_ATÉ_AGI"
lang: pt-BR
author: {AUTHOR_NAME}
image:
  path: INSERT_COVER_IMAGE_URL
  alt: "Ilustração conceitual de inteligência artificial geral e expansão cognitiva"
published: false
---

2. CONEXÃO NARRATIVA:
- Abra com uma citação verificável de cientista, filósofo ou pioneiro da IA,
  usando <blockquote>...</blockquote> e <cite>...</cite>.
- Conecte a introdução a 'A história da inteligência artificial', que aborda
  Alan Turing, Dartmouth em 1956, Deep Blue e IA generativa, e à atual busca por AGI.
- Apresente as notícias coletadas abaixo — leis de escala, modelos de mundo,
  cadeias de raciocínio, agentes autônomos e alinhamento — como possíveis pilares
  para aproximar a IA restrita da AGI. Cite somente fatos sustentados pelas fontes;
  não invente estatísticas, títulos de artigos ou benchmarks.

3. COMPONENTES VISUAIS E HTML/CSS INCORPORADO:
{image_block}
- Incorpore um bloco <style>...</style> próprio (por exemplo, cartões informativos
  ou uma linha do tempo), mantendo densidade visual semelhante à do artigo de referência.
- Inclua pelo menos um diagrama Mermaid (```mermaid ... ```) que represente uma
  arquitetura cognitiva de AGI, o ciclo de decisão de um agente ou o fluxo de um modelo de mundo.
- Inclua uma tabela Markdown comparando métricas relevantes — raciocínio, memória,
  alinhamento e capacidade computacional, por exemplo — entre 2 a 4 abordagens citadas
  nas fontes.

4. REFERÊNCIAS E CRÉDITOS:
- Inclua links Markdown diretos para as URLs ORIGINAIS das notícias abaixo ao
  mencionar cada fonte. Não invente URLs.
- Termine estritamente com estas duas partes:
  * '## 📚 Referências e créditos', com as URLs realmente usadas e o crédito da
    imagem, se houver.
  * Assinatura: '*Revisado e adaptado por {AUTHOR_NAME} — Arquitetura de Dados & IA.*'

Notícias técnicas coletadas de fontes verificadas sobre IA (use apenas o que for
relevante e sustentado pelos trechos abaixo):
{content_buffer}
"""


def build_linkedin_prompt(blog_markdown):
    return f"""
Você é {AUTHOR_NAME}, autor do blog '{BLOG_NAME}', e acabou de publicar o artigo
abaixo. Escreva SOMENTE uma publicação para anunciá-lo no LinkedIn, em português brasileiro:

- Texto direto, com cerca de 150 palavras e tom executivo.
- Conecte a história da IA às pesquisas atuais sobre AGI abordadas no artigo.
- Inclua de 2 a 3 conclusões concretas do artigo, sem inventar fatos.
- Termine com as hashtags: #AGI #InteligenciaArtificial #EngenhariaDeDados #MLOps #FuturoDaIA
- Finalize com a chamada: "Leia a análise completa em {BLOG_NAME}."
- Retorne SOMENTE o texto da publicação, sem introdução ou títulos Markdown.

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