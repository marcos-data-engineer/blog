# 📋 Revisão de SEO e AdSense - Beyond AI Code Blog

**Data:** Fevereiro de 2026  
**Versão:** 1.0  
**Revisor:** GitHub Copilot

---

## 📊 Sumário Executivo

Seu blog Jekyll com tema Chirpy está bem estruturado para SEO básico, mas há **oportunidades significativas de melhoria** para alcançar posições melhores no Google e implementar AdSense efetivamente.

### Pontuação Geral:
- **SEO:** 6.5/10 (Bom Fundamento, Melhorias Necessárias)
- **AdSense Readiness:** 3/10 (Não Implementado)
- **Mobile/UX:** 8/10 (Bom)

---

## ✅ Pontos Fortes Atuais

### 1. **Configuração de SEO Básica** ✓
- ✓ `jekyll-seo-tag` propriamente configurado
- ✓ Google Analytics (GA4) ativo
- ✓ Descrições de página bem estruturadas
- ✓ Tags e categorias implementadas
- ✓ Open Graph e Twitter Card tags presentes
- ✓ Meta tags essenciais (viewport, charset, theme-color)

### 2. **Conteúdo Bem Estruturado** ✓
- ✓ Post principal com >900 palavras (bom para SEO)
- ✓ Hierarquia de headings apropriada (H1, H2, H3)
- ✓ Imagens com atribuição de créditos
- ✓ Linguagem natural e readability
- ✓ Tempo de leitura incluído (bom sinal para users)
- ✓ Comments enabled (sinal de engajamento)

### 3. **Estrutura Técnica** ✓
- ✓ Sitemap.xml gerado automaticamente
- ✓ PWA habilitado (melhora user experience)
- ✓ Compressão HTML ativa
- ✓ Cache de includes em produção
- ✓ Padrão de permalink limpo: `/posts/:title/`

### 4. **Experiência Mobile** ✓
- ✓ Viewport correto configurado
- ✓ Theme responsivo (Chirpy)
- ✓ Touch-friendly com Apple meta tags

---

## ❌ Problemas Detectados e Oportunidades

### 🔴 CRÍTICOS (Implementar IMEDIATAMENTE)

#### 1. **Verificação do Google Search Console**
**Status:** ❌ Não Configurado  
**Por quê:** Você tem `webmaster_verifications` em _config.yml mas está vazia!

**Ações Necessárias:**
```yaml
# Em _config.yml
webmaster_verifications:
  google: "ADICIONE_AQUI_SEU_CODE_DE_VERIFICACAO"
  bing: "OPCIONAL_MAS_RECOMENDADO"
```

1. Acesse: https://search.google.com/search-console
2. Adicione a propriedade `https://blog.dataengineer.net.br`
3. Copie o código de verificação e adicione em _config.yml

#### 2. **URLs com Localhost em Produção**
**Status:** ❌ CRÍTICO  
**Local:** `_site/robots.txt` e `_site/sitemap.xml` contêm `http://localhost:4000`

**robots.txt Atual (ERRADO):**
```plaintext
Sitemap: http://localhost:4000/sitemap.xml
```

**Ação:** Você precisa garantir que em **produção** a URL seja:
```plaintext
Sitemap: https://blog.dataengineer.net.br/sitemap.xml
```

> **Nota:** Isso pode estar relacionado ao seu processo de build. Verifique se está usando `JEKYLL_ENV=production` ao fazer build.

#### 3. **Sem Implementação de Schema.org (JSON-LD)**
**Status:** ❌ Ausente  
**Impacto:** Sem rich snippets no Google, perda de potencial de destaque

**O que falta:**
- [ ] Schema para ArticleSchema (para posts)
- [ ] Schema para Organization (seu blog)
- [ ] Schema para Author (Marcos)
- [ ] Schema para BreadcrumbList
- [ ] Schema para FAQPage (em posts com Q&A)
- [ ] Schema para NewsArticle (se aplicável)

**Benefício:** 
- 📈 Rich snippets no SERP (aparência melhorada)
- 📈 Featured snippets (posição zero)
- 📈 Visual stars/ratings possíveis

---

### 🟠 ALTOS PRIORIDADE

#### 4. **Sem Implementação de AdSense**
**Status:** ❌ Não Integrado  
**Por quê:** Privacy policy menciona AdSense mas nenhuma implementação existe

**O que Falta:**
- [ ] Google AdSense approval/account
- [ ] Ad unit placement planning
- [ ] Ad code no template
- [ ] Responsive ad units não implementados
- [ ] No ads.txt file
- [ ] Sem app-ads.txt (se mobile apps)

**Recomendação de Placement:**
```
┌─────────────────────────────────────┐
│         Header Display Ad           │  (728x90 ou Responsive)
├─────────────────────────────────────┤
│ [SIDEBAR]     │  Post Content       │
│ (300x600      │  - In-article ads   │  (300x250)
│  Skyscraper)  │  - After paragraph  │
│               │  - Before comments  │
│               │                     │
│               │  [Bottom - 728x90]  │
└─────────────────────────────────────┘
```

#### 5. **Ausência de robots.txt na Raiz**
**Status:** ❌ Falta  
**Impacto:** Pode causar warnings no GSC

Na raiz do projeto, você deve ter um arquivo `robots.txt`:

```plaintext
User-agent: *
Allow: /

Disallow: /_*
Disallow: /assets/
Disallow: /admin/

Sitemap: https://blog.dataengineer.net.br/sitemap.xml
```

#### 6. **Falta ads.txt**
**Status:** ❌ Ausente  
**Obrigatório para:** AdSense/Monetização

Você precisa de um arquivo `ads.txt` na raiz:
```plaintext
google.com, ca-pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
# Obtenha esse código ao aprovar AdSense
```

#### 7. **Sem Otimização de Imagens**
**Status:** ⚠️ Parcial  
**Problema:** Imagens externas (Wikimedia, Flickr) sem atributos otimizados

Melhorias necessárias:
- [ ] Adicionar `loading="lazy"` em imagens
- [ ] Adicionar `width` e `height` explícitos (melhora CLS)
- [ ] Usar WebP com fallback (opcional mas recomendado)
- [ ] Otimizar imagens locais em `/assets/img/`
- [ ] Adicionar `srcset` para responsividade

---

### 🟡 PRIORIDADE MÉDIA

#### 8. **Sem Internal Linking Strategy**
**Status:** ⚠️ Fraco  
**Impacto:** Reduz autoridade de página e crawl efficiency

**Recomendação:**
Você tem apenas 1 post. Ao adicionar mais posts, implemente:
- Links internos para posts relacionados (use tags comuns)
- Links para categoria no texto (não apenas sidebar)
- Links entre posts em seção de "Related Posts" (*já existe na template*)
- Breadcrumb schema com links

#### 9. **Meta Descriptions Passivas em Alguns Lugares**
**Status:** ⚠️ Poderia Melhorar

Suas descriptions estão bem, mas:
- [ ] Algumas poderiam ser mais action-oriented
- [ ] Adicionar numbers/estatísticas (ex: "A História da IA: Uma Jornada de 20+ Anos")
- [ ] CTAs explícitos ("Aprenda como..." em vez de "Uma exploração...")

**Exemplo Melhorado:**
```markdown
---
description: "A História da IA: Uma jornada de 70 anos desde Alan Turing até ChatGPT. Descubra os marcos que transformaram a tecnologia"
---
```

#### 10. **Falta Canonical URL Explícita**
**Status:** ⚠️ Jekyll-seo-tag cuida disso, mas...

O plugin gera automático, mas se usar CDN ou mirror, adicione em front matter:
```yaml
canonical_url: "https://blog.dataengineer.net.br/posts/the-history-of-artificial-intelligence/"
```

#### 11. **Sem Open Graph Image Padrão**
**Status:** ⚠️ Falta fallback  

Em _config.yml está vazio:
```yaml
social_preview_image: "" # ← Adicione uma imagem padrão aqui
```

Isso garante que compartilhamentos em redes sociais tenham imagem mesmo que a página use `/favicon.webp` ou sinta falta de og:image.

#### 12. **Sem Hreflang Tags (se multi-idioma)**
**Status:** ℹ️ Não aplicável agora  
**Recomendação:** Se expandir para EN/ES no futuro, implemente hreflang

---

### 🟢 PRIORIDADE BAIXA (Nice to Have)

#### 13. **Sem FAQ Schema**
**Seu Post teria benefício!** Considere adicionar:
```markdown
---
faq:
  - question: "O que é Teste de Turing?"
    answer: "..."
  - question: "Quando começou a IA?"
    answer: "..."
---
```

#### 14. **Sem Author Schema Estruturado**
**Recomendação:** Crie schema JSON-LD para Marcos no arquivo:

`_includes/author-schema.html` (novo):
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Marcos Vasconcellos de Andrade",
  "url": "https://blog.dataengineer.net.br/about",
  "image": "https://blog.dataengineer.net.br/assets/img/avatar2.jpg",
  "jobTitle": "Data Engineer & AI Researcher",
  "sameAs": [
    "https://linkedin.com/in/marcos-data-engineer",
    "https://github.com/marcos-data-engineer",
    "https://youtube.com/@ai-insights-marcos"
  ]
}
</script>
```

#### 15. **Sem Organization Schema**
Similar ao acima, defina:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Beyond AI Code",
  "url": "https://blog.dataengineer.net.br",
  "logo": "https://blog.dataengineer.net.br/assets/img/avatar2.jpg"
}
```

---

## 🎯 Plano de Ação Recomendado

### **Semana 1 - CRÍTICO**
- [ ] Registrar e verificar Blog no Google Search Console
- [ ] Submeter Sitemap ao GSC
- [ ] Corrigir URLs localhost em produção
- [ ] Criar/Implementar robots.txt na raiz
- [ ] Submeter ao Bing Webmaster Tools

### **Semana 2 - IMPLEMENTAÇÃO CORE SEO**
- [ ] Implementar Article Schema JSON-LD
- [ ] Implementar Organization Schema
- [ ] Implementar Author Schema
- [ ] Adicionar Breadcrumb Schema
- [ ] Testar em Schema.org validator

### **Semana 3 - ADENSE**
- [ ] Criar conta Google AdSense
- [ ] Gerar ads.txt
- [ ] Planejar placement de ads
- [ ] Implementar ad code em post layout
- [ ] Configurar auto ads vs manual units

### **Semana 4 - OTIMIZAÇÕES**
- [ ] Melhorar meta descriptions
- [ ] Adicionar loading="lazy" em imagens
- [ ] Implementar internal linking strategy
- [ ] Criar social preview image padrão
- [ ] Monitorar GSC por erros

---

## 📄 Implementações Recomendadas

### **A. Arquivo de Configuração Google Search Console**

Adicione a `_config.yml`:
```yaml
webmaster_verifications:
  google: "YOUR_VERIFICATION_CODE"
  bing: "YOUR_BING_CODE"
```

### **B. Novo Arquivo: `robots.txt` (raiz do projeto)**

```plaintext
# _robots.txt (ou /robots.txt na raiz)

User-agent: *
Allow: /

# Diretórios para não indexar
Disallow: /_drafts/
Disallow: /_includes/
Disallow: /_layouts/
Disallow: /_sass/
Disallow: /_site/
Disallow: /assets/

# Sitemap
Sitemap: https://blog.dataengineer.net.br/sitemap.xml

# Crawl delay (opcional, 1-5 segundo)
Crawl-delay: 1
```

### **C. Novo Arquivo: `ads.txt` (raiz do projeto)**

```plaintext
# ads.txt - Após aprovação do AdSense

google.com, ca-pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
```

### **D. Novo Include: Schema JSON-LD para Artigos**

Criar arquivo: `_includes/schema-article.html`

```liquid
{% if page.layout == 'post' %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ page.title | escape }}",
  "description": "{{ page.description | escape }}",
  "image": "{{ page.image | default: site.social_preview_image | prepend: site.url }}",
  "datePublished": "{{ page.date | date_to_xmlschema }}",
  "dateModified": "{{ page.last_modified_at | default: page.date | date_to_xmlschema }}",
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
}
</script>
{% endif %}
```

Adicione ao `_includes/head.html` antes de `</head>`:
```liquid
{% include schema-article.html %}
```

### **E. Otimizar Imagens no Post Layout**

Em `_layouts/post.html`, modificar tag `<img>`:
```html
<!-- Antes -->
<img {{ src }} {{ class }} {{ alt }} w="1200" h="630" {{ lqip }}>

<!-- Depois -->
<img {{ src }} {{ class }} {{ alt }} width="1200" height="630" {{ lqip }} loading="lazy">
```

### **F. Melhorar Open Graph Padrão**

Em `_config.yml`:
```yaml
# Adicione uma imagem padrão para compartilhamentos
social_preview_image: /assets/img/avatar2.jpg

# Ou uma imagem maior e melhor
social_preview_image: /assets/img/og-default.jpg
```

---

## 💰 AdSense Implementation Guide

### **Passo 1: Aplicação AdSense**
1. Acesse: https://AdSense.google.com
2. Clique "Sign up now"
3. Conecte com Google Account
4. Forneça:
   - URL do blog: `https://blog.dataengineer.net.br`
   - Tipo de conta: Publisher
   - Localização: Brasil
   - Categoria: Technology/AI Blog

### **Passo 2: Aprovação**
- Leva 24-48h (às vezes mais)
- Google verifica conteúdo original e de qualidade ✓ (seu blog tem!)
- Sem AdSense de rivais já colocados ✗ (você não tem)

### **Passo 3: Implementação**

#### **Opção A: Auto Ads (Recomendado para Começar)**
Adicione **uma vez** no `<head>`:
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXX"
     crossorigin="anonymous"></script>
```

Google automaticamente encontra melhor posição. Simples!

#### **Opção B: Placement Manual (Mais Controle)**
Coloque em `_includes/post-ads.html`:

**Antes do Conteúdo:**
```html
<div class="ad-wrapper mb-4">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXX"
       crossorigin="anonymous"></script>
  <!-- Display Ad -->
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXX"
       data-ad-slot="1234567890"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
```

**Dentro do Content (Mid-Article):**
```html
<!-- No meio do post, em _layouts/post.html após 3-4 parágrafos -->
<div class="ad-wrapper my-4">
  <ins class="adsbygoogle"
       style="display:block; text-align:center;"
       data-ad-layout="in-article"
       data-ad-format="fluid"
       data-ad-client="ca-pub-XXXXXXXX"
       data-ad-slot="2468101213"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
```

**Sidebar (300x600):**
```html
<!-- Em _includes/sidebar.html -->
<div class="ad-wrapper">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXX"
       data-ad-slot="9876543210"
       data-ad-format="vertical"
       data-full-width-responsive="true"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
```

### **Passo 4: Otimizar Rendimento**
- 📊 Monitore no AdSense Console
- 🎯 Teste placements diferentes
- 🚫 Remova underperforming units
- 📈 Aumente tráfego (SEO melhorado = $ mais)

---

## 📈 Métricas a Monitorar

Após implementar as melhorias, acompanhe:

### **Google Search Console**
- [ ] Impressões (target: +50% em 3 meses)
- [ ] CTR médio (target: >3%)
- [ ] Posição média (target: <10 para keywords principais)
- [ ] Erros de cobertura (target: 0)

### **Google Analytics 4**
- [ ] Organic traffic (target: +30% em 2 meses)
- [ ] Bounce rate (target: <60%)
- [ ] Avg. session duration (target: >2min)
- [ ] Pages/session (target: >2)

### **AdSense** (após implementação)
- [ ] RPM (Revenue Per Mille): Varia 10-50 BRL no Brasil
- [ ] CTR (Click-Through Rate): Target 2-5%
- [ ] Impressions: Aumentar com tráfego SEO
- [ ] Est. earnings: Acompanhar rendimento

---

## 🔍 Ferramentas Recomendadas (Livres)

1. **Google Search Console** - https://search.google.com/search-console
2. **Schema.org Validator** - https://validator.schema.org
3. **Google Mobile-Friendly Test** - https://search.google.com/test/mobile-friendly
4. **Lighthouse** - Integrado no Chrome DevTools
5. **SEMrush Free Tier** - Análise de keywords
6. **Ubersuggest Free** - Keyword research
7. **Screaming Frog SEO Spider** (Free version) - Crawl site

---

## ✨ Melhorias Adicionais (Bonus)

### **1. Implementar Breadcrumb Navigation**
```liquid
<!-- Em _layouts/post.html -->
<nav aria-label="breadcrumb">
  <ol>
    <li><a href="{{ site.url }}">Home</a></li>
    <li><a href="{{ site.url }}/categories/{{ page.categories[0] | downcase | replace: ' ', '-' }}">{{ page.categories[0] }}</a></li>
    <li><span>{{ page.title }}</span></li>
  </ol>
</nav>
```

### **2. Adicionar Last Updated Badge**
```liquid
{% if page.last_modified_at and page.last_modified_at != page.date %}
<p class="update-notice">⚠️ Última atualização: {{ page.last_modified_at | date: "%d de %B de %Y" }}</p>
{% endif %}
```

### **3. Implementar Table of Contents Melhorado**
JS para sticky TOC na lateral (Chirpy já tem, mas pode melhorar).

### **4. Keywords & SEO Metadata**
Adicione em front matter de posts:
```yaml
---
keywords: "artificial intelligence, AI history, machine learning"
---
```

### **5. Share Buttons**
Adicione botões para LinkedIn, HN, Reddit
```html
<div class="share-buttons">
  <a href="https://www.linkedin.com/sharing/share-offsite/?url=...">LinkedIn</a>
  <a href="https://news.ycombinator.com/submitlink?u=...">Hacker News</a>
  <a href="https://reddit.com/submit?url=...">Reddit</a>
</div>
```

---

## 🎓 Recursos de Aprendizagem

- **Google Search Central:** https://developers.google.com/search
- **Jekyll SEO Guide:** https://jekyllrb.com/tutorials/convert-site-to-jekyll/
- **JSON-LD Documentation:** https://json-ld.org
- **AdSense Help Center:** https://support.google.com/adsense
- **Core Web Vitals Guide:** https://web.dev/vitals/

---

## 📋 Checklist Final

### **Antes de Ir ao Vivo com Melhorias**
- [ ] Todas URLs em config.yml apontam para produção
- [ ] Cache cleared (_site/ deletado e gerado novo)
- [ ] robots.txt criado na raiz
- [ ] Schema JSON-LD testado em validator.schema.org
- [ ] Imagens otimizadas e com alt text completo
- [ ] Links internos entre posts (se >1 post)
- [ ] Privacy policy atualizada com AdSense details
- [ ] Google Search Console verificado
- [ ] Mobile test passando no Lighthouse

---

## 💬 Próximos Passos

1. **Imediatamente:** Registre no Google Search Console
2. **Esta Semana:** Implemente Schema JSON-LD
3. **Próxima Semana:** Solicite Aprovação AdSense
4. **Continuidade:** Acompanhe métricas semanalmente
5. **Escalabilidade:** Crie roadmap de novos posts (1-2/mês ajuda SEO)

---

**Nota**, você tem um blog com **potencial MUITO BOM**! O conteúdo é original, bem estruturado e em um nicho com pouca concorrência (Portuguese + AI + Data Engineering). Com essas melhorias, espero que veja:

- 📈 50-100% aumento em tráfego orgânico em 3 meses
- 💰 $50-500/mês com AdSense (dependendo do tráfego)
- 🎯 Top 5 posições para suas keywords principais

Sucesso! 🚀

---

*Última atualização deste documento: Fevereiro 2026*
