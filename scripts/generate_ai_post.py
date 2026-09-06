import os
import re
import time
import datetime
import feedparser
from google import genai

client = genai.Client()

# Feeds alinhados a Linux, DevOps, MLOps e Automação de IA
rss_urls = [
    "https://phoronix.com/phoronix-rss.php",                      # Linux & Kernel News
    "https://kubernetes.io/feed.xml",                              # Cloud Native & Infrastructure
    "https://aws.amazon.com/blogs/machine-learning/feed/",       # AWS MLOps & AI Infra
    "https://pythonweekly.com/rss"                                 # Python Ecosystem & Automation
]

content_buffer = ""
for url in rss_urls:
    feed = feedparser.parse(url)
    for entry in feed.entries[:2]:
        summary = entry.get("summary", entry.get("description", ""))
        link = entry.get("link", "")
        title = entry.title
        content_buffer += f"Title: {title}\nURL: {link}\nSummary: {summary}\n\n"

now = datetime.datetime.now()
date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S -0300")
date_filename = now.strftime("%Y-%m-%d")

prompt = f"""
You are a Senior Linux Infrastructure, DevOps, and Data Engineer authoring the blog 'Beyond AI Code'.

Analyze the news below and generate TWO outputs strictly delimited by '===LINKEDIN_POST===':

OUTPUT 1: Markdown Post for Jekyll (Chirpy Theme)
- Must start strictly with YAML Front Matter:
---
title: "INSERT_DIRECT_TECHNICAL_TITLE"
date: {date_front_matter}
published: false
categories: [DevOps, AI Infrastructure]
tags: [linux, automation, devops, data-engineering]
description: >-
  INSERT_CONCISE_TECHNICAL_SUMMARY_UP_TO_160_CHARS
author: marcos
image:
  path: https://picsum.photos/seed/devops-infra/1200/630
  alt: Technical illustration of Linux and AI infrastructure
---

- Write in International English focusing on practical system administration, MLOps, automation, and infrastructure implications.
- Include section headers with technical emojis (e.g., '## 🐧 Linux & Kernel', '## ⚡ Automation & Data').
- Include markdown links to original sources and a '## 🔗 Sources & References' section.

===LINKEDIN_POST===

OUTPUT 2: LinkedIn Announcement Post (English or Portuguese)
- A punchy 150-word LinkedIn post summarizing 3 key technical takeaways from the week.
- Include relevant hashtags (#Linux #DevOps #Automation #DataEngineering #AIInfra).
- Include a Call-To-Action: "Read the full technical analysis on Beyond AI Code."

Collected Technical News:
{content_buffer}
"""

# Execução com tratamento de resposta
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

raw_output = response.text.strip()

# Separação do artigo do Blog e da legenda do LinkedIn
if "===LINKEDIN_POST===" in raw_output:
    blog_content, linkedin_content = raw_output.split("===LINKEDIN_POST===")
else:
    blog_content = raw_output
    linkedin_content = ""

# Sanitização do Markdown
blog_content = re.sub(r'^```[a-zA-Z]*\n', '', blog_content.strip())
if "---" in blog_content:
    blog_content = blog_content[blog_content.find("---"):]

# Gravação dos arquivos
output_dir = "_posts"
os.makedirs(output_dir, exist_ok=True)

# Salva o Post do Blog
with open(os.path.join(output_dir, f"{date_filename}-weekly-ops-digest.md"), "w", encoding="utf-8") as f:
    f.write(blog_content.strip())

# Salva a Legenda Pronta para o LinkedIn
if linkedin_content:
    with open(os.path.join(output_dir, f"{date_filename}-linkedin-caption.txt"), "w", encoding="utf-8") as f:
        f.write(linkedin_content.strip())

print("Drafts for Blog and LinkedIn created successfully.")