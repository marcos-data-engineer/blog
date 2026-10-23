#!/usr/bin/env python3
"""
generate_ai_post.py
--------------------
Agente autônomo focado na geração de artigos de alto impacto para o blog
Jekyll/Chirpy (Data Architecture & AI Insights).

Recursos e Resiliência:
  - Carregamento automático de variáveis de ambiente (.env e os.environ)
  - Resiliência Multicamadas: Gemini API -> OpenRouter (Auto & Modelos Grátis) -> Ollama Local
  - Preservação do Front Matter image.path para renderização de thumbnail na Home do Chirpy
  - Artigos densos, profundos e pragmáticos (~1.800 a 2.300 palavras)
  - Suporte completo a MathJax (math: true) e Mermaid (mermaid: true)
  - Tabela comparativa enxuta (3 colunas) sem truncamento lateral
  - Processamento Pillow (PIL) para recorte proporcional em 16:9 (1280x720)

Autor: Marcos Vasconcellos de Andrade
Blog: Data Architecture & AI Insights
"""

import argparse
import datetime
import json
import logging
import os
import re
import sys
import time
import random
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
from zoneinfo import ZoneInfo

# Carregamento automático do arquivo .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from PIL import Image
except ImportError:
    Image = None

import feedparser
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("generate_ai_post")

# ---------------------------------------------------------------------------
# Configuração do Blog e Autoria
# ---------------------------------------------------------------------------
AUTHOR_NAME = "Marcos Vasconcellos de Andrade"
BLOG_NAME = "Data Architecture & AI Insights"
BLOG_URL = "https://marcos-data-engineer.github.io/blog/"
OUTPUT_DIR = "_posts"
TIMEZONE = ZoneInfo("America/Sao_Paulo")

DEFAULT_MODEL = "gemini-2.5-flash"

OPENROUTER_FALLBACK_MODELS = [
    "openrouter/auto",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
]

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL_QUEUE = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "gemma2:9b",
]

TOPIC_KEYWORDS = ["agi", "llm", "jepa", "world model", "rag", "n8n", "lgpd"]

RSS_URLS = [
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]

FEEDPARSER_USER_AGENT = "Mozilla/5.0 (compatible; DataArchitectureAIInsightsBot/1.0)"

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1024&h=1024&fit=crop",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1024&h=1024&fit=crop",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1024&h=1024&fit=crop",
]


def generate_slug(title: str, max_length: int = 70) -> str:
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    slug = re.sub(r"-+", "-", text).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug


def clean_html(raw_html: str) -> str:
    return re.sub(r"<[^>]+>", " ", raw_html).strip()


def process_image_aspect_ratio(
    file_path: str, target_w: int = 1280, target_h: int = 720
):
    if not Image:
        log.warning("⚠️ Pillow (PIL) não instalado. Recorte 16:9 ignorado.")
        return
    try:
        with Image.open(file_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            orig_w, orig_h = img.size
            target_ratio = target_w / target_h
            orig_ratio = orig_w / orig_h

            if orig_ratio > target_ratio:
                crop_w = int(orig_h * target_ratio)
                left = (orig_w - crop_w) // 2
                cropped = img.crop((left, 0, left + crop_w, orig_h))
            else:
                crop_h = int(orig_w / target_ratio)
                top = (orig_h - crop_h) // 2
                cropped = img.crop((0, top, orig_w, top + crop_h))

            resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            resized.save(file_path, "JPEG", quality=92)
            log.info("✂️ Imagem ajustada em 16:9 (1280x720): %s", file_path)
    except Exception as e:
        log.warning("⚠️ Falha ao processar imagem %s: %s", file_path, e)


def ensure_image_download(image_filename: str, prompt_concept: str, slug: str) -> str:
    img_dir = os.path.join("assets", "img", "posts", slug)
    os.makedirs(img_dir, exist_ok=True)
    target_path = os.path.join(img_dir, image_filename)

    if os.path.exists(target_path):
        process_image_aspect_ratio(target_path)
        return target_path

    encoded = urllib.parse.quote(prompt_concept)
    primary_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed={random.randint(100, 999)}&nologo=true"

    log.info("📥 Baixando imagem (%s)...", image_filename)
    for attempt in range(2):
        try:
            time.sleep(3)
            req = urllib.request.Request(
                primary_url, headers={"User-Agent": FEEDPARSER_USER_AGENT}
            )
            with (
                urllib.request.urlopen(req, timeout=30) as resp,
                open(target_path, "wb") as f,
            ):
                f.write(resp.read())
            process_image_aspect_ratio(target_path)
            log.info("✅ Imagem obtida via Pollinations: %s", target_path)
            return target_path
        except Exception as e:
            log.warning(
                "⚠️ Tentativa %d/2 para %s falhou: %s", attempt + 1, image_filename, e
            )

    fallback = random.choice(FALLBACK_IMAGES)
    try:
        log.info("🔄 Acionando fallback validado para %s...", image_filename)
        req = urllib.request.Request(
            fallback, headers={"User-Agent": FEEDPARSER_USER_AGENT}
        )
        with (
            urllib.request.urlopen(req, timeout=30) as resp,
            open(target_path, "wb") as f,
        ):
            f.write(resp.read())
        process_image_aspect_ratio(target_path)
        log.info("✅ Imagem de fallback salva: %s", target_path)
    except Exception as e:
        log.error("❌ Erro no fallback da imagem %s: %s", image_filename, e)

    return target_path


def ensure_post_images(markdown_content: str, slug: str):
    ensure_image_download(
        "cover.jpg",
        "enterprise data center servers glowing blue lights 3d isometric",
        slug,
    )
    pattern = (
        rf"/assets/img/posts/{re.escape(slug)}/([a-zA-Z0-9_\-]+\.(?:jpg|jpeg|png))"
    )
    matches = set(re.findall(pattern, markdown_content))
    for img_name in matches:
        if img_name != "cover.jpg":
            ensure_image_download(
                img_name,
                f"technical infrastructure diagram vector style blue {img_name}",
                slug,
            )


def collect_news(
    rss_urls: list[str],
    keywords: list[str],
    pool_per_feed: int = 5,
    max_items: int = 15,
) -> tuple[str, list[str]]:
    feedparser.USER_AGENT = FEEDPARSER_USER_AGENT
    collected_items: list[str] = []
    used_urls: set[str] = set()

    log.info("📡 Varrendo %d canais de notícias e pesquisas...", len(rss_urls))

    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                continue

            for entry in feed.entries[:pool_per_feed]:
                title = entry.get("title", "Sem título")
                link = entry.get("link", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))

                haystack = (title + " " + summary).lower()
                matches = not keywords or any(k in haystack for k in keywords)

                if matches and link and link not in used_urls:
                    used_urls.add(link)
                    collected_items.append(
                        f"- Título: {title}\n  Resumo: {summary[:300]}\n  URL: {link}"
                    )
        except Exception as e:
            log.warning("Erro ao ler feed %s: %s", url, e)

    log.info("📰 %d fontes coletadas para fundamentação.", len(used_urls))
    return "\n\n".join(collected_items[:max_items]), list(used_urls)


def call_openrouter(api_key: str, model: str, prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": BLOG_URL,
        "X-Title": BLOG_NAME,
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as err:
        err_body = err.read().decode("utf-8", errors="ignore")
        log.warning(
            "⚠️ Detalhe da resposta OpenRouter (%s - %d): %s", model, err.code, err_body
        )
        raise


def call_ollama(model: str, prompt: str) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.6},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    log.info("🦙 Executando geração local no Ollama (%s)...", model)
    with urllib.request.urlopen(req, timeout=300) as response:
        body = json.loads(response.read().decode("utf-8"))
        return body.get("response", "").strip()


def call_llm_with_rotation(client, requested_model: str, prompt: str) -> str:
    # 1. Tentativa via Google Gemini API
    if client:
        log.info("🧠 Solicitando via Google Gemini API: %s...", requested_model)
        try:
            resp = client.models.generate_content(
                model=requested_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=12000,
                    temperature=0.6,
                ),
            )
            if resp and resp.text:
                log.info("✅ Artigo gerado via Gemini API (%s)", requested_model)
                return resp.text.strip()
        except Exception as e:
            log.warning("⚠️ API Gemini falhou/bloqueada: %s", e)

    # 2. Fallback via OpenRouter
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        log.info("🌐 Tentando Fallback via OpenRouter...")
        for or_model in OPENROUTER_FALLBACK_MODELS:
            try:
                log.info("🤖 Testando OpenRouter (%s)...", or_model)
                text = call_openrouter(openrouter_key, or_model, prompt)
                if text and len(text) > 800:
                    log.info(
                        "✅ Artigo gerado com sucesso via OpenRouter (%s)", or_model
                    )
                    return text
            except Exception as ex:
                log.warning("⚠️ OpenRouter (%s) falhou: %s", or_model, ex)
    else:
        log.info("ℹ️ OPENROUTER_API_KEY não detectada. Avançando para fallback local.")

    # 3. Fallback via Ollama Local
    log.info("🔄 Acionando Fallback Local via Ollama (%s)...", OLLAMA_HOST)
    for local_model in OLLAMA_MODEL_QUEUE:
        try:
            text = call_ollama(local_model, prompt)
            if text and len(text) > 600:
                log.info(
                    "✅ Artigo gerado localmente com sucesso via Ollama (%s)",
                    local_model,
                )
                return text
        except Exception as ex:
            log.warning("⚠️ Modelo Ollama (%s) falhou: %s", local_model, ex)

    raise RuntimeError(
        "❌ Todos os provedores (Gemini, OpenRouter e Ollama Local) falharam."
    )


def sanitize_markdown(raw_output: str) -> str:
    text = raw_output.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    idx = text.find("---")
    if idx != -1:
        text = text[idx:].strip()

    text = re.sub(r"Marcos Silva", AUTHOR_NAME, text)
    text = re.sub(
        r"Agente de Geração de Texto",
        "Inteligência Artificial Geral",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\d+paramenosdel", "valores reduzidos", text)

    forbidden_headers = [
        r"##?\s*CITAÇÃO HISTÓRICA.*?\n",
        r"##?\s*DIAGRAMA MERMAID.*?\n",
        r"##?\s*TABELA COMPARATIVA.*?\n",
    ]
    for pattern in forbidden_headers:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text


def build_blog_prompt(title: str, context_news: str, date_front_matter: str) -> str:
    slug = generate_slug(title)
    ticks = "```"
    return f"""Você é {AUTHOR_NAME}, Especialista em Infraestrutura Linux, Automação de Processos e Engenharia de Dados, autor do blog '{BLOG_NAME}'.

INSTRUÇÕES CRÍTICAS DE AUTORIA E ESTILO:
- NOME DO AUTOR: {AUTHOR_NAME}. NUNCA utilize 'Marcos Silva' ou qualquer outro nome.
- CONCEITO DE AGI: AGI significa EXCLUSIVAMENTE 'Inteligência Artificial Geral' (Artificial General Intelligence).
- EXTENSÃO E DENSIDADE: Escreva um ensaio executivo, completo e profundo (~1.800 a 2.300 palavras, tempo de leitura de 6 a 8 minutos). NUNCA resuma ou simplifique o texto.

TÍTULO DO ARTIGO: "{title}"

SAÍDA OBRIGATÓRIA (Sua resposta DEVE começar IMEDIATAMENTE na primeira linha com '---'):
---
layout: post
title: "{title}"
date: {date_front_matter}
categories: [Inteligência Artificial, Engenharia de Dados]
tags: [agi, llm, world-models, jepa, automacao, b2b, dados, linux, lgpd]
description: "Uma análise profunda e pragmática sobre o fim do hype da AGI, as limitações autorregressivas dos LLMs e por que as empresas devem focar em arquiteturas híbridas."
lang: pt-BR
author: marcos
math: true
mermaid: true
image:
  path: /assets/img/posts/{slug}/cover.jpg
  alt: "{title}"
published: true
---

<p class="text-center text-muted mb-4"><small><em>Imagem de capa: Infraestrutura de datacenter e servidores Linux de alto desempenho. (Créditos da imagem: Unsplash / Licença CC BY-SA)</em></small></p>

<blockquote>
"O que é inteligência? Não se trata tanto da capacidade de fazer cálculos, mas sim da habilidade de aprender, adaptar-se e entender a realidade do mundo." - François Chollet
</blockquote>

## A Miragem da AGI e a Realidade dos LLMs Autorregressivos
[Desenvolva em detalhes a matemática da predição de próximo token $$P(x_t \\mid x_{{<t}})$$ e por que estatística não é raciocínio causal nem compreensão pragmática]

## O Plateau do ARC-AGI e a Promessa dos World Models
[Aprofunde a análise sobre o benchmark ARC-AGI de François Chollet, o estancamento de performance com scaling laws puras, e a alternativa dos World Models e arquitetura JEPA de Yann LeCun]

## Arquiteturas Híbridas B2B: O Caminho Pragmático para Inovação
[Explique a combinação de LLMs para extração de intenção + orquestração determinística com n8n/Python/Go + RAG Privado em servidores Linux + conformidade LGPD]

<figure class="my-4">
  <img src="/assets/img/posts/{slug}/figura1.jpg" alt="Fluxo de Dados da Arquitetura Híbrida B2B" class="w-100 rounded" />
  <figcaption class="text-center text-muted mt-2"><small>Fluxo de orquestração híbrida conectando RAG Privado e LLMs locais com total controle de dados. <em>(Imagem: Unsplash / Licença CC BY-SA)</em></small></figcaption>
</figure>

## Diagrama da Arquitetura Híbrida B2B
{ticks}mermaid
graph TD
    A[Usuário / Sistema B2B] --> B[Orquestrador Determinístico n8n / Python]
    B --> C{{Trata Dados Sensíveis ou Privados?}}
    C -- Sim --> D[RAG Privado & Base Vetorial Interna em Linux]
    C -- Não --> E[API Externa / LLM Cloud]
    D --> F[Validação de Segurança & Conformidade LGPD]
    E --> F
    F --> G[Resposta Estruturada para a Aplicação]
{ticks}

## Comparativo: LLM Monolítico vs. Arquitetura Híbrida B2B

| Critério | LLM Monolítico (Hype AGI) | Arquitetura Híbrida B2B (Prática) |
| :--- | :--- | :--- |
| **Soberania de Dados** | Risco de exposição em APIs de terceiros | Total controle on-premise / nuvem privada |
| **Previsibilidade** | Propenso a alucinações não-determinísticas | Lógica de negócios 100% determinística |
| **Custo de Operação** | Escalabilidade cara por token em nuvem | Custos otimizados com infraestrutura própria |
| **Conformidade LGPD** | Complexo devido ao tráfego de dados sensíveis | LGPD por design no perímetro da empresa |

## Conclusão: O Valor Real da Engenharia de Dados
[Sintetize os pontos principais destacando a importância de uma sólida engenharia de dados, automação e infraestrutura Linux]

*Revisado e adaptado por {AUTHOR_NAME} — Arquitetura de Dados & IA.*

## 📚 Referências e Leituras Complementares
- [Chollet, F. (2019). The Measure of Intelligence](https://arxiv.org/abs/1911.01547)
- [LeCun, Y. (2022). A Path Towards Autonomous Machine Intelligence](https://openreview.net/forum?id=BZ5a1r-fZa)
- [BAIR Blog. Data Systems for, of, and by Agents](https://bair.berkeley.edu/)
- [OpenAI. Scaling Storage and Infrastructure for Enterprise LLMs](https://openai.com/index/)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agente autônomo de geração de artigos para o Blog Jekyll/Chirpy"
    )
    parser.add_argument("--title", "-t", help="Título do artigo.")
    parser.add_argument("--keywords", "-k", help="Keywords separadas por vírgula.")
    parser.add_argument(
        "--model", "-m", default=DEFAULT_MODEL, help="Modelo inicial Gemini."
    )
    parser.add_argument("--dry-run", action="store_true", help="Visualiza o prompt.")
    return parser.parse_args()


def main():
    args = parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None

    keywords = (
        [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
        if args.keywords
        else TOPIC_KEYWORDS
    )

    context_news, used_urls = collect_news(RSS_URLS, keywords)
    title = (
        args.title
        or "O Fim do Hype da AGI: Por Que Sua Empresa Deveria Focar em Arquiteturas Híbridas"
    )

    now = datetime.datetime.now(TIMEZONE)
    date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S %z")
    date_filename = now.strftime("%Y-%m-%d")
    time_suffix = now.strftime("%H%M")
    slug = generate_slug(title)

    blog_prompt = build_blog_prompt(title, context_news, date_front_matter)

    if args.dry_run:
        print(blog_prompt)
        return

    log.info("🧠 Gerando artigo no blog em PT-BR...")
    blog_raw = call_llm_with_rotation(client, args.model, blog_prompt)
    blog_content = sanitize_markdown(blog_raw)

    log.info("🖼️ Baixando e processando imagens em 16:9...")
    ensure_post_images(blog_content, slug)

    post_filename = f"{date_filename}-{slug}-{time_suffix}.md"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, post_filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog_content.strip() + "\n")

    log.info("✅ Artigo gerado e salvo com sucesso em: %s", filepath)


if __name__ == "__main__":
    main()
