import os
import re
import time
import datetime
import feedparser
from google import genai

# Inicialização da SDK (utiliza GEMINI_API_KEY do ambiente)
client = genai.Client()

# RSS Feeds de notícias
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
        link = entry.get("link", "")
        title = entry.title
        content_buffer += f"Title: {title}\nURL: {link}\nSummary: {summary}\n\n"

# Formatação de data (UTC-3)
now = datetime.datetime.now()
date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S -0300")
date_filename = now.strftime("%Y-%m-%d")

# Prompt estruturado para o tema Chirpy
prompt = f"""
You are a Data Engineer specialized in Artificial Intelligence and author of the blog 'Beyond AI Code'.

Synthesize the news below into a weekly technical blog post in International English.

STEP 1: Identify the single most prominent technical topic among the collected news (e.g., 'robotics', 'neural-network', 'data-center', 'quantum-computing', 'microchip', 'autonomous-agents').
Use this topic as a single-word-slug inside the image path URL below.

FORMATTING RULES (JEKYLL / CHIRPY):
1. The output MUST start strictly with YAML Front Matter delimited by '---':
---
title: "INSERT_AN_ENGAGING_TITLE"
date: {date_front_matter}
published: false
categories: [Artificial Intelligence, Weekly Digest]
tags: [ai, llm, data-engineering, trends]
description: >-
  INSERT_A_CONCISE_SUMMARY_UP_TO_160_CHARACTERS
author: marcos
image:
  path: https://picsum.photos/seed/TOPIC_SLUG_HERE/1200/630
  alt: Technical illustration related to weekly AI developments
math: false
mermaid: false
---

2. TITLE INSTRUCTIONS:
- DO NOT use prefixes like 'Beyond the Code:' or 'Beyond AI Code:' in the title field.
- Make the title direct, concise, and focused on the key technical subjects of the week.

3. VISUAL ENGAGEMENT & STYLE:
- Use relevant emojis in all H2 section headers (e.g., '## 🤖 AI Agents', '## ⚡ Performance Improvements', '## 🚀 Strategic Moves').
- Maintain a highly professional, technical, and analytical tone for Data Engineers and AI Practitioners.

4. SOURCES & CITATIONS (VERY IMPORTANT FOR COPYRIGHT COMPLIANCE):
- Interweave direct markdown hyperlinks to the original articles when discussing specific news items.
- At the end of the post, ALWAYS include a dedicated section titled '## 🔗 Sources & References' listing the original source links provided in the prompt.

Collected news & source links:
{content_buffer}
"""

# Execução da requisição com mecanismo de tentativas (retry)
max_retries = 3
response = None

for attempt in range(max_retries):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"API temporariamente indisponível ({e}). Tentando novamente em 10 segundos... ({attempt + 1}/{max_retries})")
            time.sleep(10)
        else:
            raise e

post_content = response.text.strip()

# Sanitização rigorosa: garante que o arquivo comece estritamente no primeiro '---'
post_content = re.sub(r'^```[a-zA-Z]*\n', '', post_content)
if "---" in post_content:
    first_dash_idx = post_content.find("---")
    post_content = post_content[first_dash_idx:]

if post_content.endswith("```"):
    post_content = post_content[:-3].strip()

# Gravação do rascunho
output_dir = "_posts"
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, f"{date_filename}-weekly-ai-digest.md")

with open(filename, "w", encoding="utf-8") as f:
    f.write(post_content)

print(f"Draft generated successfully: {filename}")