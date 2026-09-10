import os
import re
import datetime
import feedparser
from google import genai

client = genai.Client()

rss_urls = [
    "https://phoronix.com/phoronix-rss.php",
    "https://kubernetes.io/feed.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://pythonweekly.com/rss"
]

def clean_html(raw_html):
    """Remove tags HTML para economizar tokens no buffer."""
    return re.sub(r'<[^>]+>', '', raw_html)

content_buffer = ""
for url in rss_urls:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            summary = clean_html(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            title = entry.title
            content_buffer += f"Title: {title}\nURL: {link}\nSummary: {summary[:300]}\n\n"
    except Exception as e:
        print(f"Aviso: Falha ao ler o feed {url}: {e}")

now = datetime.datetime.now()
date_front_matter = now.strftime("%Y-%m-%d %H:%M:%S -0300")
date_filename = now.strftime("%Y-%m-%d")
time_suffix = now.strftime("%H%M")

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

OUTPUT 2: LinkedIn Announcement Post (English)
- A punchy 150-word LinkedIn post summarizing 3 key technical takeaways from the week.
- Include relevant hashtags (#Linux #DevOps #Automation #DataEngineering #AIInfra).
- Include a Call-To-Action: "Read the full technical analysis on Beyond AI Code."

Collected Technical News:
{content_buffer}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

raw_output = response.text.strip()

if "===LINKEDIN_POST===" in raw_output:
    blog_content, linkedin_content = raw_output.split("===LINKEDIN_POST===")
else:
    blog_content = raw_output
    linkedin_content = ""

blog_content = re.sub(r'^```[a-zA-Z]*\n', '', blog_content.strip())
if "---" in blog_content:
    blog_content = blog_content[blog_content.find("---"):]

output_dir = "_posts"
os.makedirs(output_dir, exist_ok=True)

# Adicionado sufixo de hora para evitar sobreposição nos deploys
post_filename = f"{date_filename}-weekly-ops-digest-{time_suffix}.md"
with open(os.path.join(output_dir, post_filename), "w", encoding="utf-8") as f:
    f.write(blog_content.strip())

if linkedin_content:
    caption_filename = f"{date_filename}-linkedin-caption-{time_suffix}.txt"
    with open(os.path.join(output_dir, caption_filename), "w", encoding="utf-8") as f:
        f.write(linkedin_content.strip())

print(f"Rascunhos criados com sucesso: {post_filename}")