# 🛠️ Guia de Implementação - Mudanças Concretas

Este arquivo contém o código exato que você deve adicionar/modificar para implementar as recomendações de SEO e AdSense.

---

## 1️⃣ **Arquivo 1: robots.txt (NOVA RAIZ)**

**Localização:** `robots.txt` (na raiz do projeto, ao lado de _config.yml)

```plaintext
User-agent: *
Allow: /

# Diretórios internos para não indexar
Disallow: /_drafts/
Disallow: /_includes/
Disallow: /_layouts/
Disallow: /_sass/
Disallow: /_site/
Disallow: /assets/

# Sitemap
Sitemap: https://blog.dataengineer.net.br/sitemap.xml

# Crawl delay para economizar bandwidth do servidor
Crawl-delay: 1
```

**Por quê:** Google precisa saber quais URLs indexar e onde está seu sitemap. Isso também protege diretórios internos.

---

## 2️⃣ **Arquivo 2: ads.txt (NOVA RAIZ)**

**Localização:** `ads.txt` (na raiz, ao lado de robots.txt)

⚠️ **ANTES:** Aguarde aprovação do Google AdSense para obter o `ca-pub-XXXXXXXX`

```plaintext
# ads.txt - Arquivo de Transparência de Ads
# Gerado após aprovação do AdSense

# Seu Publisher ID (obtenha após aprovação do AdSense)
google.com, ca-pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0

# Se usar outras networks no futuro:
# openx.com, 537100188, DIRECT, 6a698e4a7bd74cad
# rubicon.com, YOUR-ACCOUNT-ID, DIRECT, 0bab2154d89a1a01
```

**Como obter seu código:**
1. Após aprovação no AdSense: https://AdSense.google.com
2. Vá em: Contas > Acesso à conta e segurança > ads.txt verificado por Google
3. Copie seu Publisher ID

---

## 3️⃣ **Arquivo 3: Schema JSON-LD para Artigos**

**Localização:** `_includes/schema-article.html` (NOVO ARQUIVO)

```liquid
{% if page.layout == 'post' %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ page.title | escape }}",
  "description": "{{ page.description | escape }}",
  "image": {% if page.image %}
    "{{ page.image | default: site.social_preview_image | prepend: site.url }}"
  {% else %}
    "{{ site.social_preview_image | prepend: site.url }}"
  {% endif %},
  "datePublished": "{{ page.date | date_to_xmlschema }}",
  {% if page.last_modified_at %}
  "dateModified": "{{ page.last_modified_at | date_to_xmlschema }}",
  {% endif %}
  "author": {
    "@type": "Person",
    "name": "{{ site.social.name }}",
    "url": "{{ site.url }}/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{{ site.title }}",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ site.avatar | prepend: site.url }}"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ page.url | absolute_url }}"
  }
  {% if page.categories %}
  ,"keywords": "{{ page.categories | join: ', ' }}"
  {% endif %}
  {% if page.tags %}
  ,"about": {{ page.tags | jsonify }}
  {% endif %}
}
</script>
{% endif %}
```

**Onde adicionar:**
1. Crie o arquivo em `_includes/schema-article.html`
2. Abra `_includes/head.html`
3. **Antes da linha `</head>`** (perto do fim), adicione:
   ```liquid
   {% include schema-article.html %}
   ```

**Por quê:** Isso permite que Google entenda melhor seu artigo e mostre rich snippets (data, autor, categoria).

---

## 4️⃣ **Arquivo 4: Schema para Author**

**Localização:** `_includes/schema-author.html` (NOVO ARQUIVO)

```liquid
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Marcos Vasconcellos de Andrade",
  "url": "{{ site.url }}/about",
  "image": "{{ site.avatar | prepend: site.url }}",
  "jobTitle": "Data Engineer & AI Researcher",
  "worksFor": {
    "@type": "Organization",
    "name": "{{ site.title }}"
  },
  "sameAs": [
    "https://linkedin.com/in/marcos-data-engineer",
    "https://github.com/marcos-data-engineer",
    "https://www.youtube.com/@ai-insights-marcos"
  ],
  "email": "{{ site.social.email }}"
}
</script>
```

**Onde adicionar:**
- Em `_includes/head.html`, logo após a inclusion de `schema-article.html`:
```liquid
{% include schema-author.html %}
```

**Por quê:** Conecta você como autoridade no tema, melhora YMYL signals.

---

## 5️⃣ **Arquivo 5: Schema para Organization**

**Localização:** `_includes/schema-organization.html` (NOVO ARQUIVO)

```liquid
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{{ site.title }}",
  "url": "{{ site.url }}",
  "logo": "{{ site.avatar | prepend: site.url }}",
  "description": "{{ site.description }}",
  "sameAs": [
    "https://linkedin.com/in/marcos-data-engineer",
    "https://github.com/marcos-data-engineer",
    "https://www.youtube.com/@ai-insights-marcos"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "{{ site.social.email }}",
    "contactType": "Customer Support"
  }
}
</script>
```

**Onde adicionar:**
- Em `_includes/head.html`, adicionado uma única vez (antes do </head>, em ambiente de produção):
```liquid
{% if jekyll.environment == 'production' %}
  {% include schema-organization.html %}
{% endif %}
```

---

## 6️⃣ **Modifique: _config.yml - Adicione Verificação Google**

**Localização:** `_config.yml` (Linha onde está `webmaster_verifications`)

```yaml
# Antes:
webmaster_verifications:
  google: "" # fill in your verification string
  bing: ""   # fill in your verification string

# Depois:
webmaster_verifications:
  google: "YOUR-GOOGLE-VERIFICATION-CODE" # 🔑 Você receberá do GSC
  bing: "YOUR-BING-VERIFICATION-CODE"     # 🔑 Opcional mas recomendado
```

**Como obter o código:**
1. Acesse https://search.google.com/search-console
2. Clique "Add property"
3. Insira: `https://blog.dataengineer.net.br`
4. Escolha "HTML tag" no método de verificação
5. Copie o código dentro de `content="..."`

---

## 7️⃣ **Modifique: _config.yml - Adicione Social Preview Image**

**Localização:** `_config.yml` (Linha onde está `social_preview_image`)

```yaml
# Antes:
social_preview_image: "" # string, local or CORS resources

# Depois:
social_preview_image: "/assets/img/avatar2.jpg" # ou outra imagem maior
```

**Recomendado:** Se tiver uma imagem maior (1200x630px) para representar o blog:
```yaml
social_preview_image: "/assets/img/og-default-image.jpg"
```

---

## 8️⃣ **Modifique: _layouts/post.html - Adicione Loading Lazy**

**Localização:** `_layouts/post.html` (Linha com `<img {{ src }}...`)

```html
<!-- ANTES: Linha ~45 -->
<img {{ src }} {{ class }} {{ alt }} w="1200" h="630" {{ lqip }}>

<!-- DEPOIS: -->
<img {{ src }} {{ class }} {{ alt }} w="1200" h="630" {{ lqip }} loading="lazy" decoding="async">
```

**Por quê:** `loading="lazy"` melhora Core Web Vitals. `decoding="async"` não bloqueia render.

---

## 9️⃣ **OPCIONAL: Módulo AdSense (Auto Ads - Recomendado para Começar)**

**Localização:** `_includes/adSense-auto.html` (NOVO ARQUIVO)

```html
<!-- Google AdSense Auto Ads -->
<!-- ⚠️ SÓ ADICIONAR APÓS APROVAÇÃO DO ADSENSE -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
     crossorigin="anonymous"></script>
```

**Onde adicionar:**
Em `_includes/head.html`, **apenas em produção**:
```liquid
{% if jekyll.environment == 'production' %}
  {% include adSense-auto.html %}
{% endif %}
```

**Simplificado:** Com Auto Ads, Google coloca anúncios automaticamente nos melhores locais. Comece com isso!

---

## 🔟 **OPCIONAL: Ad Units Manuais (Mais Controle)**

### A. **Ad no Topo do Post**

**Localização:** `_layouts/post.html` (Antes de `<article>`)

```html
{% if jekyll.environment == 'production' %}
<div class="ad-container mb-4">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="1234567890"
       data-ad-format="horizontal"
       data-full-width-responsive="true"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
{% endif %}
```

### B. **Ad no Meio do Post**

**Localização:** `_layouts/post.html` (Após ~50% do content)

```html
{% if jekyll.environment == 'production' %}
<div class="ad-container my-4" style="text-align: center;">
  <ins class="adsbygoogle"
       style="display:block; max-width:728px; margin: 0 auto;"
       data-ad-layout="in-article"
       data-ad-format="fluid"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="2234567891"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
{% endif %}
```

### C. **Ad na Sidebar**

**Localização:** `_includes/sidebar.html` (Dentro da sidebar)

```html
{% if jekyll.environment == 'production' %}
<div class="ad-container mb-4">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="3234567892"
       data-ad-format="vertical"
       data-full-width-responsive="true"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
{% endif %}
```

---

## 📋 Padrão de Implementação

### **PASSO 1: Seus slots variam, obtenha DO ADSENSE:**

```
ca-pub-XXXXXXXXXXXXXXXX    ← Publisher ID (use em todos os data-ad-client)
1234567890                 ← Ad Unit Slot 1 (atribua para cada local)
2234567891                 ← Ad Unit Slot 2
3234567892                 ← Ad Unit Slot 3
```

### **PASSO 2: Order de Implementação**

1. ✅ Antes de TUDO: Crie robots.txt + ads.txt
2. ✅ Registre no Google Search Console
3. ✅ Implemente Schema JSON-LD
4. ✅ Aplique ao _config.yml (verificação + social image)
5. ✅ Modifique post.html (lazy loading)
6. ✅ Solicite aprovação AdSense
7. ✅ Após aprovação: Adicione código AdSense (Auto Ads primeiro!)

---

## ✅ Quality Checklist Antes de Deploy

```bash
# 1. Teste Schema em:
# https://validator.schema.org

# 2. Valide JSON-LD syntax:
# - Copie o código gerado
# - Cole no validator

# 3. Teste Mobile:
# https://search.google.com/test/mobile-friendly

# 4. Build local:
JEKYLL_ENV=production bundle exec jekyll build

# 5. Verifique _site/ tem robots.txt e ads.txt:
ls -la _site/robots.txt
ls -la _site/ads.txt

# 6. Check no navegador que localhost:4000/robots.txt existe:
curl http://localhost:4000/robots.txt
```

---

## 🚀 Deploy Steps

```bash
# 1. Commit changes
git add -A
git commit -m "SEO: Adicionar Schema JSON-LD, robots.txt, ads.txt"

# 2. Build production
JEKYLL_ENV=production bundle exec jekyll build

# 3. Push para GitHub
git push origin main

# 4. GitHub Pages publica automaticamente

# 5. Aguarde 5-10 min, verifique:
# https://blog.dataengineer.net.br/robots.txt
# https://blog.dataengineer.net.br/ads.txt
```

---

## 🐛 Troubleshooting Comum

### **Problema:** Schema não aparece no validator
**Solução:** 
- Verifique se `jekyll.environment` é "production"
- Local testes: `JEKYLL_ENV=production jekyll serve`

### **Problema:** robots.txt retorna 404
**Solução:**
- Arquivo deve estar na **raiz** (mesma pasta de _config.yml)
- Certifique que não está em .gitignore
- Jekyll copia arquivos raiz para _site/

### **Problema:** AdSense não aprova
**Solução:**
- Blog precisa ter conteúdo original (✓ você tem)
- Requer tempo de espera (24-48h mínimo)
- Pode rejeitar se houver:
  - Conteúdo duplicado
  - Pop-ups excessivos
  - Clicks artificiais
  - Links suspeitos

### **Problema:** GSC mostra "não verificado"
**Solução:**
- Verifique código copiado corretamente do GSC
- Pode usar outros métodos: DNS, Google Analytics, etc.
- Aguarde reload do GSC (até 24h)

---

## 📊 Monitoramento Pós-Implementação

### **Semana 1-2:**
- [ ] Search Console: Visualizar "Coverage" (erros?)
- [ ] Verificar indexação: `site:blog.dataengineer.net.br`
- [ ] Lighthouse score no DevTools
- [ ] Mobile-friendly test passando

### **Semana 2-4:**
- [ ] Analytics: Quanto traffic orgânico?
- [ ] GSC: Qual keyword está rankando?
- [ ] Bounce rate mudou?
- [ ] CTR nos SERP

### **Contínuo:**
- [ ] AdSense: Impressions e rendimento diário
- [ ] Novos posts? Aplicar Schema em cada um
- [ ] Erros de rastreamento no GSC?
- [ ] Segurança: Examinação de malware

---

## 🎓 Recursos Complementares

**Para aprender mais:**
- [Google Search Console Training](https://support.google.com/webmasters/answer/9128668)
- [Google AdSense Help](https://support.google.com/adsense)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Web.dev Learning](https://web.dev/learn/)

---

**Versão:** 1.0  
**Criado:** Fevereiro 2026  
**Status:** Pronto para Implementação ✅
