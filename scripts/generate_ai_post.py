#!/usr/bin/env python3
"""
generate_ai_post.py
--------------------
Agente de geração de conteúdo para blog Jekyll/Chirpy + LinkedIn.

Modos de operação:
  - Guiado:   TOPIC_KEYWORDS preenchido → filtra feeds RSS por tema
  - Autônomo: TOPIC_KEYWORDS vazio → descobre trending topics nos feeds

Saídas:
  - .md   → Artigo completo para Jekyll/Chirpy
  - .txt  → Post LinkedIn (Post Principal + 1º Comentário)
  - .txt  → Carrossel LinkedIn (7-9 slides) [opcional: --carousel]

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
LINKEDIN_URL = "https://linkedin.com/in/marcos-data-engineer"
OUTPUT_DIR = "_posts"
TIMEZONE = ZoneInfo("America/Sao_Paulo")

# ---------------------------------------------------------------------------
# Configuração do Modelo e Resiliência
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 5

# ---------------------------------------------------------------------------
# Título Fixo (opcional)
# Defina um título aqui para forçar o uso, ou deixe None para geração dinâmica.
# Pode ser sobrescrito via CLI: --title "Meu Título"
# ---------------------------------------------------------------------------
FIXED_TITLE = None

# ---------------------------------------------------------------------------
# Palavras-Chave de Filtragem
# Preencha para filtrar feeds RSS por tema específico.
# Deixe vazio [] para modo autônomo (descobre trending topics).
# Pode ser sobrescrito via CLI: --keywords "rag,llm,automacao"
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS = [
    "agi",
    "llm",
    "scaling",
    "world model",
    "jepa",
    "reasoning",
    "intelligence",
]

# ---------------------------------------------------------------------------
# Feeds RSS
# ---------------------------------------------------------------------------
RSS_URLS = [
    # Labs & Research
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    # Industry & Media
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    # Open Source & MLOps
    "https://huggingface.co/blog/feed.xml",
]

FEEDPARSER_USER_AGENT = (
    "Mozilla/5.0 (compatible; DataArchitectureAIInsightsBot/1.0; "
    "+https://marcos-data-engineer.github.io/blog/)"
)


# ═══════════════════════════════════════════════════════════════════════════
# Utilidades
# ═══════════════════════════════════════════════════════════════════════════


def generate_slug(title: str, max_length: int = 70) -> str:
    """Gera slug URL-friendly a partir do título."""
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    slug = text.strip("-")
    # Cortar no limite sem quebrar palavras
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug


def clean_html(raw_html: str) -> str:
    """Remove tags HTML de uma string."""
    return re.sub(r"<[^>]+>", " ", raw_html).strip()


# ═══════════════════════════════════════════════════════════════════════════
# Coleta de Notícias (RSS)
# ═══════════════════════════════════════════════════════════════════════════


def collect_news(
    rss_urls: list[str],
    keywords: list[str],
    pool_per_feed: int = 5,
    max_items: int = 15,
) -> tuple[str, list[str]]:
    """
    Coleta notícias de feeds RSS, filtrando por keywords.
    Se keywords estiver vazio, aceita todas as entradas.
    """
    feedparser.USER_AGENT = FEEDPARSER_USER_AGENT
    collected_items: list[str] = []
    used_urls: set[str] = set()

    log.info("📡 Varrendo %d canais de notícias e pesquisas...", len(rss_urls))

    for url in rss_urls:
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                log.warning("Feed malformado sem entradas: %s (%s)", url, feed.bozo_exception)
                continue

            for entry in feed.entries[:pool_per_feed]:
                title = entry.get("title", "Sem título")
                link = entry.get("link", "")
                summary = clean_html(
                    entry.get("summary", entry.get("description", ""))
                )

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


# ═══════════════════════════════════════════════════════════════════════════
# Chamada à API Gemini (com retry e backoff)
# ═══════════════════════════════════════════════════════════════════════════


def call_gemini(
    client,
    model: str,
    prompt: str,
    max_output_tokens: int = 12000,
    temperature: float = 0.7,
) -> str:
    """Chama a API do Gemini com retry exponencial + jitter."""
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


# ═══════════════════════════════════════════════════════════════════════════
# Sanitizadores e Validadores
# ═══════════════════════════════════════════════════════════════════════════


def sanitize_markdown(raw_output: str) -> str:
    """Remove code fences e localiza o início do front matter YAML."""
    text = raw_output.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    idx = text.find("---")
    return text[idx:].strip() if idx != -1 else text


def sanitize_linkedin(raw_output: str) -> str:
    """Remove preâmbulos e localiza o bloco [1. Post Principal]."""
    text = raw_output.strip()
    idx = text.find("[1. Post Principal]")
    return text[idx:].strip() if idx != -1 else text


def sanitize_carousel(raw_output: str) -> str:
    """Remove code fences do output do carrossel."""
    text = raw_output.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def validate_blog_output(content: str) -> list[str]:
    """Valida o output do blog e retorna lista de avisos."""
    warnings = []
    if not content.startswith("---"):
        warnings.append("Front matter YAML não encontrado no início")
    if content.count("---") < 2:
        warnings.append("Front matter YAML incompleto (faltam delimitadores)")
    if "```mermaid" not in content:
        warnings.append("Diagrama Mermaid não encontrado no artigo")
    if "## 📚" not in content and "Referências" not in content:
        warnings.append("Seção de referências não encontrada")
    # Verificar se há links reais na seção de referências
    ref_section = content.split("Referências")[-1] if "Referências" in content else ""
    if ref_section and "http" not in ref_section:
        warnings.append("Referências parecem não conter links reais (URLs)")
    return warnings


def validate_linkedin_output(content: str) -> list[str]:
    """Valida o output do LinkedIn e retorna lista de avisos."""
    warnings = []
    if "[1. Post Principal]" not in content:
        warnings.append("Bloco [1. Post Principal] não encontrado")
    if "[2. Primeiro Comentário]" not in content:
        warnings.append("Bloco [2. Primeiro Comentário] não encontrado")
    # Verificar se há links no Post Principal (não deveria haver)
    parts = content.split("[2. Primeiro Comentário]")
    if len(parts) >= 1 and "http" in parts[0]:
        warnings.append("Post Principal contém links (devem ficar no 1º Comentário)")
    return warnings


# ═══════════════════════════════════════════════════════════════════════════
# Prompts
# ═══════════════════════════════════════════════════════════════════════════


def build_topic_discovery_prompt(context_news: str) -> str:
    """Prompt para descobrir o melhor tema quando keywords estão vazios."""
    return f"""Você é um estrategista de conteúdo especializado em IA, Engenharia de Dados e Automação.

Analise as notícias abaixo e escolha O MELHOR tema para um artigo de blog em PT-BR que:
1. Esteja em alta e gere alto engajamento
2. Seja relevante para profissionais de TI, CTOs e engenheiros de dados
3. Permita conexão prática com automação B2B, infraestrutura Linux e IA aplicada
4. Tenha potencial de se tornar um artigo de referência no tema

Retorne APENAS um JSON válido (sem code fences, sem texto antes ou depois):
{{"titulo": "Título provocativo em PT-BR", "keywords": ["keyword1", "keyword2", "keyword3"], "justificativa": "Por que este tema é relevante agora e gera engajamento"}}

--- NOTÍCIAS E TENDÊNCIAS RECENTES ---
{context_news}"""


def build_title_prompt(keywords: list[str], context_news: str) -> str:
    """Prompt para gerar um título quando keywords existem mas título não foi definido."""
    kw_str = ", ".join(keywords)
    return f"""Você é um copywriter especializado em conteúdo técnico B2B.

Crie UM título de artigo em Português do Brasil sobre os temas: [{kw_str}].
O título deve ser:
- Provocativo e que gere curiosidade
- Máximo 15 palavras
- Que funcione bem no LinkedIn E no Google (SEO)
- Tom: profissional mas intrigante

Contexto das notícias atuais:
{context_news[:1000]}

Retorne APENAS o título, sem aspas, sem explicação."""


def build_blog_prompt(title: str, context_news: str, date_front_matter: str) -> str:
    """Prompt principal para geração do artigo do blog."""
    slug = generate_slug(title)
    return f"""Você é {AUTHOR_NAME}, Especialista em Infraestrutura Linux, Automação de Processos e Engenharia de Dados.
Você escreve com autoridade, mas de forma acessível — como se estivesse explicando para um colega inteligente num café.
Você tem opiniões fortes, baseadas em experiência real, e não tem medo de discordar do hype do mercado.

Sua tarefa: escrever um artigo ENVOLVENTE e PROVOCATIVO em PT-BR para o blog '{BLOG_NAME}'.

TÍTULO: "{title}"

═══════════════════════════════════════════════════
REGRAS DE SAÍDA (OBRIGATÓRIAS):
═══════════════════════════════════════════════════
- Retorne APENAS o Markdown bruto, começando direto com '---' (front matter).
- Sem preâmbulos como "Aqui está o artigo" ou "Claro, vou escrever".
- Sem code fences (```) envolvendo todo o conteúdo.

FRONT MATTER (copie EXATAMENTE, adapte apenas description e tags ao tema):
---
layout: post
title: "{title}"
date: {date_front_matter}
categories: [Inteligencia Artificial, Engenharia de Dados]
tags: [adapte-ao-tema, maximo-8-tags, separadas-por-virgula]
description: "Descrição provocativa e otimizada para SEO em até 160 caracteres"
lang: pt-BR
author: {AUTHOR_NAME}
image:
  path: /assets/img/posts/{slug}/cover.jpg
  alt: "{title}"
published: false
---

═══════════════════════════════════════════════════
ESTILO E TOM DE ESCRITA:
═══════════════════════════════════════════════════

ABERTURA (primeiros 3 parágrafos — DECISIVOS para prender o leitor):
- Comece com um GANCHO irresistível: dado surpreendente, analogia inesperada ou pergunta provocativa.
- NÃO use citações genéricas de filósofos ou frases motivacionais. Seja concreto.
- Exemplo de bom gancho: "Uma criança de 4 anos entende que uma bola vai cair se soltar. Um LLM treinado com 400.000 anos de texto... não faz ideia."
- Nos 3 primeiros parágrafos o leitor decide se continua ou fecha a aba. Seja magnético.

CORPO DO ARTIGO:
- Parágrafos CURTOS: máximo 3 linhas. Se ficou longo, QUEBRE em dois.
- Subtítulos (### ou ##) a cada 2-3 parágrafos para manter ritmo e escaneabilidade.
- Tom CONVERSACIONAL e PESSOAL:
  • Use primeira pessoa: "Na minha experiência...", "O que eu vejo no mercado...", "Já implementei isso em..."
  • Inclua pelo menos 1-2 opiniões pessoais fortes do autor.
  • Inclua pelo menos UM exemplo prático ou caso de uso real.
- Use ANALOGIAS do mundo real para explicar conceitos técnicos.
- Inclua pelo menos UM diagrama Mermaid (```mermaid ... ```).
  IMPORTANTE: Nomes de subgraph com espaços devem estar entre aspas: subgraph "Nome Com Espaço"
- Inclua pelo menos UMA tabela comparativa Markdown.
- O artigo deve ter entre 1200-2000 palavras.

SEÇÃO B2B PRÁTICA (obrigatória):
- Mostre por que empresas NÃO devem esperar pela "AGI mágica".
- Mencione soluções concretas: RAG, n8n, Python, IA Local (Ollama), conformidade LGPD.
- Dê valor IMEDIATO e aplicável, não teoria abstrata.

REFERÊNCIAS (OBRIGATÓRIAS — com links REAIS):
- Seção: '## 📚 Referências e Leituras Complementares'
- TODAS as referências DEVEM conter URLs reais. Exemplos:
  * LeCun, Y. (2022). *A Path Towards Autonomous Machine Intelligence*. [OpenReview](https://openreview.net/pdf?id=BZ5a1r-kVsf)
  * Chollet, F. (2019). *On the Measure of Intelligence*. [arXiv:1911.01547](https://arxiv.org/abs/1911.01547)
- NÃO inclua referências genéricas sem URL. Cada referência precisa de link clicável.
- Mínimo 3 referências, máximo 6.

ASSINATURA (última linha do artigo):
*Artigo desenvolvido por {AUTHOR_NAME} — Especialista em Infraestrutura Linux, Automação & Engenharia de Dados.*

═══════════════════════════════════════════════════
CONTEXTO E NOTÍCIAS PARA FUNDAMENTAÇÃO:
═══════════════════════════════════════════════════
{context_news if context_news else "Nenhuma notícia recente coletada. Use seu conhecimento para fundamentar o artigo."}"""


def build_linkedin_prompt(blog_markdown: str, title: str) -> str:
    """Prompt para geração do post LinkedIn (texto + 1º comentário)."""
    return f"""Você é {AUTHOR_NAME}, Especialista em Infraestrutura Linux e Automação B2B.
Crie uma publicação LinkedIn otimizada para MÁXIMO ENGAJAMENTO em PT-BR.

REGRAS:
- Inicie a saída DIRETO em '[1. Post Principal]' sem nenhuma frase introdutória.

═══════════════════════════════════════════════════
[1. Post Principal] — REGRAS:
═══════════════════════════════════════════════════
- ZERO links no corpo do post (links ficam no 1º comentário).
- GANCHO MATADOR nas primeiras 2 linhas (antes do "ver mais" do LinkedIn ≈ 210 caracteres).
  Use: pergunta provocativa, dado surpreendente ou afirmação ousada com emoji.
- Parágrafos curtos (2-3 linhas) com espaçamento entre eles.
- Emojis estratégicos (máximo 1 por parágrafo, não exagere).
- Tom: profissional mas HUMANO, como uma conversa entre colegas.
- Soft sell de 2 linhas com prova de resultado:
  ❌ Evite: "Ofereço consultoria especializada"
  ✅ Prefira: "Tenho ajudado empresas a reduzir custos com IA em até 70% usando modelos locais"
- CTA final: pergunta ABERTA que qualquer profissional tech possa responder.
  ❌ Evite: "CTOs, gestores e líderes..." (exclui a maioria do público)
  ✅ Prefira: "E você, como está usando IA no dia a dia? Conta aqui 👇"
- Hashtags (8-10): #IA #AGI #LLM #Automacao #EngenhariaDeDados #B2B #LGPD #Linux #InteligenciaArtificial #DataEngineering

═══════════════════════════════════════════════════
[2. Primeiro Comentário]:
═══════════════════════════════════════════════════
Para aprofundar neste tema, confira o artigo completo e minhas outras publicações:

🔗 Links e Detalhes:
• 🌐 Blog: {BLOG_URL}
• 💻 GitHub: {GITHUB_URL}
• 🔗 LinkedIn: {LINKEDIN_URL}

💼 Consultoria & Serviços de TI (B2B / PJ):
🛠️ Infraestrutura Linux: Servidores, VPS, Docker, Hardening e Segurança.
⚙️ Automação de Processos: Workflows no n8n, Python, Bash e RAG sem custos de nuvem.
🧠 IA Privada & Local: Chatbots offline, Agentes de IA e modelos locais (Ollama) com 100% de conformidade à LGPD.

📩 Para orçamentos, parcerias e projetos corporativos, envie uma mensagem direta (DM)!

--- ARTIGO BASE ---
{blog_markdown}"""


def build_carousel_prompt(blog_markdown: str, title: str) -> str:
    """Prompt para geração do texto do carrossel LinkedIn (PDF slides)."""
    return f"""Você é um designer de conteúdo especializado em carousels de LinkedIn (documentos PDF deslizáveis).
Com base no artigo abaixo, crie o TEXTO completo para um carrossel de 7-9 slides.

═══════════════════════════════════════════════════
REGRAS DO CARROSSEL:
═══════════════════════════════════════════════════

[SLIDE 1 - CAPA]
- Título chamativo (pode ser uma versão curta do título do artigo)
- Subtítulo de 1 linha
- "Deslize para entender →"

[SLIDES 2 a 7 - CONTEÚDO]
- UM insight-chave por slide
- Máximo 40 palavras por slide
- Use bullet points, números ou frases de impacto
- Cada slide deve fazer sentido sozinho (sem depender dos outros)
- Alterne entre: dado surpreendente, analogia, dica prática, comparação

[SLIDE 8 - CTA]
- "Gostou? Salve este post 🔖"
- "Comente '🧠' e eu envio o artigo completo"
- Menção ao blog/perfil

[SLIDE 9 - SOBRE O AUTOR]
- Nome: {AUTHOR_NAME}
- Especialidade: Infraestrutura Linux, Automação & Engenharia de Dados
- 3 bullet points com serviços B2B
- "📩 DM para projetos e parcerias"

═══════════════════════════════════════════════════
FORMATO DE SAÍDA:
═══════════════════════════════════════════════════
Retorne cada slide em um bloco separado:

[SLIDE 1 - CAPA]
Título: ...
Subtítulo: ...

[SLIDE 2]
Título do slide: ...
• Ponto 1
• Ponto 2

(continuar até o último slide)

--- ARTIGO BASE ---
{blog_markdown}"""


# ═══════════════════════════════════════════════════════════════════════════
# Execução Principal
# ═══════════════════════════════════════════════════════════════════════════


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agente de geração de conteúdo para Blog + LinkedIn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Modo padrão (usa TOPIC_KEYWORDS do script)
  python generate_ai_post.py

  # Título específico
  python generate_ai_post.py --title "O Futuro do RAG em 2026"

  # Keywords via CLI (sobrescreve TOPIC_KEYWORDS)
  python generate_ai_post.py --keywords "rag,automacao,llm"

  # Modo autônomo (descobre trending topics)
  python generate_ai_post.py --keywords ""

  # Gerar com carrossel LinkedIn
  python generate_ai_post.py --carousel

  # Apenas blog, sem LinkedIn
  python generate_ai_post.py --blog-only

  # Visualizar prompts sem gastar tokens
  python generate_ai_post.py --dry-run

  # Usar modelo mais potente
  python generate_ai_post.py --model gemini-2.5-pro
        """,
    )
    parser.add_argument(
        "--title", "-t",
        help="Título do artigo. Se omitido, usa FIXED_TITLE ou gera automaticamente.",
    )
    parser.add_argument(
        "--keywords", "-k",
        help='Keywords separadas por vírgula (sobrescreve TOPIC_KEYWORDS). Use "" para modo autônomo.',
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Modelo Gemini a usar (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--blog-only",
        action="store_true",
        help="Gera apenas o artigo do blog (.md)",
    )
    parser.add_argument(
        "--linkedin-only",
        action="store_true",
        help="Gera apenas o post LinkedIn (.txt). Requer artigo existente como base.",
    )
    parser.add_argument(
        "--carousel",
        action="store_true",
        help="Gera também o texto do carrossel LinkedIn",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exibe os prompts gerados sem chamar a API (não gasta tokens)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=12000,
        help="Máximo de tokens na resposta do blog (default: 12000)",
    )
    return parser.parse_args()


def resolve_title(client, model: str, keywords: list[str], context_news: str, dry_run: bool) -> str:
    """Resolve o título do artigo: FIXED_TITLE > geração dinâmica."""
    if FIXED_TITLE:
        log.info("📌 Usando título fixo: %s", FIXED_TITLE)
        return FIXED_TITLE

    log.info("🎯 Gerando título baseado nos keywords e contexto...")
    prompt = build_title_prompt(keywords, context_news)

    if dry_run:
        print("\n--- PROMPT DE GERAÇÃO DE TÍTULO ---")
        print(prompt)
        return "Título Placeholder (dry-run)"

    title = call_gemini(client, model, prompt, max_output_tokens=100, temperature=0.9)
    title = title.strip('"').strip("'").strip()
    log.info("💡 Título gerado: %s", title)
    return title


def discover_topic(client, model: str, context_news: str, dry_run: bool) -> tuple[str, list[str]]:
    """Modo autônomo: descobre o melhor tema nos trending topics."""
    log.info("🔍 Modo autônomo: descobrindo melhor tema nos feeds...")
    prompt = build_topic_discovery_prompt(context_news)

    if dry_run:
        print("\n--- PROMPT DE DESCOBERTA DE TEMA ---")
        print(prompt)
        return "Tema Placeholder (dry-run)", []

    raw = call_gemini(client, model, prompt, max_output_tokens=500, temperature=0.8)

    # Limpar possíveis code fences
    clean = re.sub(r"^```json?\n?", "", raw.strip())
    clean = re.sub(r"\n?```$", "", clean)

    try:
        topic = json.loads(clean)
        title = topic["titulo"]
        keywords = topic.get("keywords", [])
        log.info("💡 Tema escolhido: %s", title)
        log.info("   Keywords: %s", ", ".join(keywords))
        log.info("   Justificativa: %s", topic.get("justificativa", "N/A"))
        return title, keywords
    except (json.JSONDecodeError, KeyError) as e:
        log.error("Falha ao parsear tema descoberto: %s\nResposta: %s", e, raw)
        raise SystemExit(1)


def save_file(directory: str, filename: str, content: str) -> str:
    """Salva conteúdo em arquivo e retorna o caminho."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    return filepath


def main():
    args = parse_args()

    # --- Validar API Key ---
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key and not args.dry_run:
        raise SystemExit("❌ Defina GEMINI_API_KEY ou GOOGLE_API_KEY no terminal.")

    client = None if args.dry_run else genai.Client(api_key=api_key)

    # --- Resolver Keywords ---
    if args.keywords is not None:
        if args.keywords.strip() == "":
            keywords = []  # Modo autônomo forçado via CLI
        else:
            keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
    else:
        keywords = TOPIC_KEYWORDS

    # --- Coleta inicial de notícias ---
    context_news, used_urls = collect_news(RSS_URLS, keywords)

    # --- Resolver Título ---
    title = args.title

    if not title:
        if not keywords:
            # Modo totalmente autônomo
            title, discovered_keywords = discover_topic(
                client, args.model, context_news, args.dry_run
            )
            if discovered_keywords:
                keywords = discovered_keywords
                # Re-coletar com novas keywords para contexto mais focado
                context_news, used_urls = collect_news(RSS_URLS, keywords)
        else:
            # Keywords existem, resolver título
            title = resolve_title(client, args.model, keywords, context_news, args.dry_run)

    if args.dry_run and not title:
        title = "Título Placeholder (dry-run)"

    # --- Timestamps ---
    now = datetime.datetime.now(TIMEZONE)
    date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S %z")
    date_filename = now.strftime("%Y-%m-%d")
    time_suffix = now.strftime("%H%M")
    slug = generate_slug(title)

    log.info("📝 Título: %s", title)
    log.info("📎 Slug: %s", slug)
    log.info("📅 Data: %s", date_front_matter)

    # --- Gerar Blog ---
    blog_content = None

    if not args.linkedin_only:
        blog_prompt = build_blog_prompt(title, context_news, date_front_matter)

        if args.dry_run:
            print("\n" + "=" * 60)
            print("PROMPT DO BLOG")
            print("=" * 60)
            print(blog_prompt)
        else:
            log.info("🧠 Gerando artigo com %s...", args.model)
            blog_raw = call_gemini(
                client, args.model, blog_prompt, max_output_tokens=args.max_tokens
            )
            blog_content = sanitize_markdown(blog_raw)

            # Validar
            for w in validate_blog_output(blog_content):
                log.warning("⚠️ Blog: %s", w)

            # Salvar artigo
            post_filename = f"{date_filename}-{slug}-{time_suffix}.md"
            filepath = save_file(OUTPUT_DIR, post_filename, blog_content)
            log.info("✅ Artigo salvo: %s", filepath)

            # Salvar prompt para rastreabilidade
            prompt_filename = f".prompt-{date_filename}-{time_suffix}.log"
            save_file(OUTPUT_DIR, prompt_filename, blog_prompt)
            log.info("📋 Prompt salvo: %s/%s", OUTPUT_DIR, prompt_filename)

    # --- Gerar LinkedIn ---
    if not args.blog_only:
        # Garantir que temos o blog como base
        if blog_content is None:
            existing = sorted(
                [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md") and not f.startswith(".")],
                reverse=True,
            )
            if existing:
                with open(os.path.join(OUTPUT_DIR, existing[0]), "r", encoding="utf-8") as f:
                    blog_content = f.read()
                log.info("📄 Usando artigo existente: %s", existing[0])
            else:
                log.error("❌ Nenhum artigo encontrado. Gere o blog primeiro (sem --linkedin-only).")
                raise SystemExit(1)

        # Post LinkedIn
        linkedin_prompt = build_linkedin_prompt(blog_content, title)

        if args.dry_run:
            print("\n" + "=" * 60)
            print("PROMPT DO LINKEDIN")
            print("=" * 60)
            print(linkedin_prompt)
        else:
            log.info("💼 Gerando post LinkedIn com %s...", args.model)
            linkedin_raw = call_gemini(
                client, args.model, linkedin_prompt,
                max_output_tokens=2500, temperature=0.8,
            )
            linkedin_content = sanitize_linkedin(linkedin_raw)

            for w in validate_linkedin_output(linkedin_content):
                log.warning("⚠️ LinkedIn: %s", w)

            caption_filename = f"{date_filename}-linkedin-{slug[:40]}-{time_suffix}.txt"
            filepath = save_file(OUTPUT_DIR, caption_filename, linkedin_content)
            log.info("✅ LinkedIn salvo: %s", filepath)

        # Carrossel LinkedIn
        if args.carousel:
            carousel_prompt = build_carousel_prompt(blog_content, title)

            if args.dry_run:
                print("\n" + "=" * 60)
                print("PROMPT DO CARROSSEL")
                print("=" * 60)
                print(carousel_prompt)
            else:
                log.info("🎠 Gerando carrossel com %s...", args.model)
                carousel_raw = call_gemini(
                    client, args.model, carousel_prompt,
                    max_output_tokens=3000, temperature=0.7,
                )
                carousel_content = sanitize_carousel(carousel_raw)

                carousel_filename = f"{date_filename}-carousel-{slug[:40]}-{time_suffix}.txt"
                filepath = save_file(OUTPUT_DIR, carousel_filename, carousel_content)
                log.info("✅ Carrossel salvo: %s", filepath)

    log.info("🏁 Processo concluído com sucesso!")


if __name__ == "__main__":
    main()
