import os
import datetime
import feedparser
from google import genai

# Inicialização automática (lê a variável GEMINI_API_KEY do ambiente)
client = genai.Client()

# RSS Feeds de IA
rss_urls = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://rss.arxiv.org/rss/cs.AI"
]

content_buffer = ""
for url in rss_urls:
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]:
        summary = entry.get("summary", entry.get("description", ""))
        content_buffer += f"Title: {entry.title}\nSummary: {summary}\n\n"

# Formatação de data (UTC-3)
now = datetime.datetime.now()
date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S -0300")
date_filename = now.strftime("%Y-%m-%d")

# Prompt em Inglês para saída em Inglês Internacional
prompt = f"""
You are a Data Engineer specialized in Artificial Intelligence and author of the blog 'Beyond AI Code'.

Synthesize the news below into a weekly technical blog post in International English.

FORMATTING RULES (JEKYLL / CHIRPY):
1. The output MUST start strictly with YAML Front Matter delimited by '---':
---
title: "INSERT_AN_ENGAGING_TITLE"
date: {date_front_matter}
categories: [Artificial Intelligence, Weekly Digest]
tags: [ai, llm, data-engineering, trends]
description: >-
  INSERT_A_CONCISE_SUMMARY_UP_TO_160_CHARACTERS
author: marcos
math: false
mermaid: false
---

2. The post body must immediately follow the closing Front Matter delimiter ('---').
3. DO NOT include H1 (#) headers in the body. Start subsections with H2 (##) headers.
4. Maintain a technical, objective, and analytical tone focused on engineering applications and AI developments.

Collected news:
{content_buffer}
"""

# Execução da requisição
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
post_content = response.text.strip()

# Sanitização de delimitadores markdown da resposta
if post_content.startswith("```markdown"):
    post_content = post_content[11:].strip()
elif post_content.startswith("```"):
    post_content = post_content[3:].strip()

if post_content.endswith("```"):
    post_content = post_content[:-3].strip()

# Gravação do arquivo final no diretório do Jekyll
output_dir = "_posts"
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, f"{date_filename}-weekly-ai-digest.md")

with open(filename, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"Draft generated successfully: {filename}")