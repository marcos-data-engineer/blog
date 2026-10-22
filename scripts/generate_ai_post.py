#!/usr/bin/env python3
"""
generate_ai_post.py
--------------------
Agente autônomo focado exclusivamente na geração de artigos de alta qualidade
e densidade visual/narrativa para o blog Jekyll/Chirpy (Data Architecture & AI Insights).

Modos de operação:
  - Guiado:   TOPIC_KEYWORDS preenchido -> filtra feeds RSS por tema
  - Autônomo: TOPIC_KEYWORDS vazio -> descobre trending topics nos feeds

Saída:
  - .md -> Artigo completo para Jekyll/Chirpy com suporte a HTML/CSS visual nativo

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
from zoneinfo import ZoneInfo

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
# Configuração de Autoria
# ---------------------------------------------------------------------------
AUTHOR_NAME = "Marcos Vasconcellos de Andrade"
BLOG_NAME = "Data Architecture & AI Insights"
BLOG_URL = "https://marcos-data-engineer.github.io/blog/"
GITHUB_URL = "https://github.com/marcos-data-engineer"
OUTPUT_DIR = "_posts"
TIMEZONE = ZoneInfo("America/Sao_Paulo")

# ---------------------------------------------------------------------------
# Configuração do Modelo e Resiliência
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 5

FIXED_TITLE = None

TOPIC_KEYWORDS = [
    "agi",
    "llm",
    "scaling",
    "world model",
    "jepa",
    "reasoning",
    "intelligence",
]

RSS_URLS = [
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://huggingface.co/blog/feed.xml",
]

FEEDPARSER_USER_AGENT = (
    "Mozilla/5.0 (compatible; DataArchitectureAIInsightsBot/1.0; "
    "+https://marcos-data-engineer.github.io/blog/)"
)


def generate_slug(title: str, max_length: int = 70) -> str:
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    slug = text.strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug


def clean_html(raw_html: str) -> str:
    return re.sub(r"<[^>]+>", " ", raw_html).strip()


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


def call_gemini(
    client,
    model: str,
    prompt: str,
    max_output_tokens: int = 12000,
    temperature: float = 0.7,
) -> str:
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
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            wait = BASE_BACKOFF_SECONDS * (2**attempt) + random.uniform(0, 2)
            log.warning(
                "Tentativa %d/%d falhou (%s). Aguardando %.1fs...",
                attempt + 1,
                MAX_RETRIES,
                e,
                wait,
            )
            time.sleep(wait)

    raise RuntimeError("Falha em todas as tentativas de chamada à API do Gemini.")


def sanitize_markdown(raw_output: str) -> str:
    text = raw_output.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    idx = text.find("---")
    return text[idx:].strip() if idx != -1 else text


def build_blog_prompt(title: str, context_news: str, date_front_matter: str) -> str:
    slug = generate_slug(title)
    return f"""Você é {AUTHOR_NAME}, Especialista em Infraestrutura Linux, Automação de Processos e Engenharia de Dados, autor do blog '{BLOG_NAME}'.

Sua missão é escrever um artigo DENSO, VISUALMENTE RICO e NARRATIVAMENTE ENVOLVENTE em PT-BR para o blog Jekyll/Chirpy.

TÍTULO: "{title}"

═══════════════════════════════════════════════════
REGRAS DE SAÍDA (OBRIGATÓRIAS):
═══════════════════════════════════════════════════
- Retorne APENAS o Markdown bruto, começando direto com '---' (front matter).
- Sem preâmbulos como "Aqui está o artigo".
- Sem code fences (```) envolvendo o documento inteiro.

FRONT MATTER:
---
layout: post
title: "{title}"
date: {date_front_matter}
categories: [Inteligencia Artificial, Engenharia de Dados]
tags: [agi, llm, world-models, jepa, automacao, b2b, dados]
description: "Análise profunda e arquitetural sobre os limites dos LLMs e o futuro das arquiteturas híbridas."
lang: pt-BR
author: marcos
image:
  path: /assets/img/posts/{slug}/cover.jpg
  alt: "{title}"
published: true
---

═══════════════════════════════════════════════════
REQUISITOS EDITORIAIS E DE DESIGN (ALTO PADRÃO CHIRPY):
═══════════════════════════════════════════════════

1. CSS EMBUTIDO DE ESTILIZAÇÃO VISUAL:
Logo após o front matter, inclua um bloco <style> personalizado contendo regras de design para o artigo:
- Estilização de blockquote com borda azul e fundo suave
- Estilização de <figure>, <img> e <figcaption>
- Estilização de caixas de destaque (.callout-box)
- Estilização de tabela comparativa
- Estilização de componentes visuais avançados (como cards de comparação HTML/CSS de arquiteturas ou caixas de conclusão)

2. COMPONENTES VISUAIS OBRIGATÓRIOS NO CORPO DO TEXTO:
- Pelo menos DUAS figuras estilizadas (<figure><img ... /><figcaption>...</figcaption></figure>) com caminhos de imagem Jekyll (/assets/img/posts/{slug}/...) e legendas detalhadas.
- Pelo menos UMA caixa de callout estilizada (<div class="callout-box">) destacando um conceito crítico.
- Pelo menos UM diagrama Mermaid (```mermaid ... ```) representando fluxos arquiteturais (ex: LLM vs JEPA ou Arquitetura Híbrida B2B).
- Pelo menos UMA tabela comparativa em Markdown limpa e alinhada.
- Opcional: Componentes interativos/visuais em HTML/CSS puro (ex: comparativo de camadas, cards de componentes).

3. NARRATIVA E STORYTELLING DE ALTA DENSIDADE:
- Evite tópicos soltos ou resumos superficiais. Escreva em formato de ensaio técnico profundo.
- Comece com uma citação marcante em <blockquote> e uma introdução narrativa instigante.
- Desenvolva argumentos com profundidade: explique o "porquê" matemático/estrutural por trás do gargalo dos LLMs e o funcionamento interno dos Modelos de Mundo (JEPA / Yann LeCun / François Chollet).
- Articule a visão B2B prática: engenharia híbrida, RAG corporativo, n8n/Python determinístico, IA local em Linux (Ollama) e conformidade LGPD.

4. REFERÊNCIAS COM LINKS REAIS:
- Finalize com a seção '## 📚 Referências e Leituras Complementares' contendo links Markdown válidos e clicáveis para os papers/fontes citados.
- Assinatura final: '*Revisado e adaptado por {AUTHOR_NAME} — Arquitetura de Dados & IA.*'

CONTEXTO DE NOTÍCIAS E PESQUISAS DA SEMANA:
{context_news if context_news else "Utilize o seu conhecimento técnico para fundamentar a análise."}"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agente autônomo de geração de artigos para o Blog Jekyll/Chirpy",
    )
    parser.add_argument("--title", "-t", help="Título do artigo.")
    parser.add_argument("--keywords", "-k", help="Keywords separadas por vírgula.")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Modelo Gemini.")
    parser.add_argument("--dry-run", action="store_true", help="Visualiza os prompts.")
    parser.add_argument(
        "--max-tokens", type=int, default=12000, help="Máximo de tokens."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key and not args.dry_run:
        raise SystemExit("❌ Defina GEMINI_API_KEY ou GOOGLE_API_KEY no terminal.")

    client = None if args.dry_run else genai.Client(api_key=api_key)

    keywords = (
        [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
        if args.keywords
        else TOPIC_KEYWORDS
    )

    context_news, used_urls = collect_news(RSS_URLS, keywords)
    title = (
        args.title
        or FIXED_TITLE
        or "A Ilusão da Inteligência: O Que Realmente Separa os LLMs da AGI Real?"
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

    log.info("🧠 Gerando artigo no blog em PT-BR com %s...", args.model)
    blog_raw = call_gemini(
        client, args.model, blog_prompt, max_output_tokens=args.max_tokens
    )
    blog_content = sanitize_markdown(blog_raw)

    post_filename = f"{date_filename}-{slug}-{time_suffix}.md"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, post_filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(blog_content.strip() + "\n")

    log.info("✅ Artigo gerado e salvo com sucesso em: %s", filepath)


if __name__ == "__main__":
    main()
