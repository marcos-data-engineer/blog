# ✅ Checklist de Implementação SEO & AdSense

Imprima este documento e marque conforme avança!

---

## 🎯 FASE 1: INICIO (HOJE) ⏱️ 30 minutos

### Infraestrutura de Rastreamento
- [ ] **Verificar robots.txt criado**
  ```bash
  cat robots.txt | grep "Sitemap"
  ```
  ✓ Deve mostrar: `Sitemap: https://blog.dataengineer.net.br/sitemap.xml`

- [ ] **Verificar ads.txt criado**
  ```bash
  cat ads.txt
  ```
  ✓ Deve existir (vazio ou com comentários)

- [ ] **Confirmar schema files criados**
  ```bash
  ls -la _includes/schema-*.html
  ```
  ✓ Deve listar 3 arquivos:
  - schema-article.html
  - schema-author.html  
  - schema-organization.html

### Configuração Jekyll
- [ ] **_config.yml atualizado com social image padrão**
  ```bash
  grep "social_preview_image" _config.yml
  ```
  ✓ Deve mostrar: `social_preview_image: "/assets/img/avatar2.jpg"`

- [ ] **head.html tem schemas inclusos**
  ```bash
  grep "schema-" _includes/head.html
  ```
  ✓ Deve encontrar 3 includes

- [ ] **post.html tem lazy loading**
  ```bash
  grep "loading=\"lazy\"" _layouts/post.html
  ```
  ✓ Deve encontrar pelo menos 1 match

### Build & Test
- [ ] **Build em produção sem erros**
  ```bash
  JEKYLL_ENV=production bundle exec jekyll build
  ```
  ✓ Deve terminar com "done in X seconds"

- [ ] **_site/robots.txt existe**
  ```bash
  ls -la _site/robots.txt
  ```
  ✓ Deve listar arquivo

- [ ] **_site/ads.txt existe**
  ```bash
  ls -la _site/ads.txt
  ```
  ✓ Deve listar arquivo

- [ ] **_site contém schema markup**
  ```bash
  grep -r "application/ld+json" _site/ | head -1
  ```
  ✓ Deve encontrar schema

### Version Control
- [ ] **Git add das mudanças**
  ```bash
  git add -A
  ```

- [ ] **Git commit com mensagem clara**
  ```bash
  git commit -m "🚀 SEO: Schema JSON-LD, robots.txt, ads.txt"
  ```

- [ ] **Git push para main**
  ```bash
  git push origin main
  ```
  ✓ GitHub Pages publica automaticamente

**SCORE FASE 1:** ___ / 15 ✓

---

## 📊 FASE 2: GOOGLE SEARCH CONSOLE (⏱️ 20 minutos)

### Registro & Verificação
- [ ] **Abrir Google Search Console**
  - Link: https://search.google.com/search-console
  - [ ] Conectado com Google Account (não precisa criar)

- [ ] **Adicionar Propriedade**
  - [ ] Clicou "+ Create property"
  - [ ] Colou URL exata: `https://blog.dataengineer.net.br`
  - [ ] Próximo passo

- [ ] **Escolher métodos de verificação**
  - [ ] Selecionou "HTML tag"
  - [ ] Copiou tag meta: `<meta name="google-site-verification"...>`
  - [ ] Extraiu o `content="xxxx-xxxx"`

- [ ] **Adicionar código em _config.yml**
  - [ ] Abriu _config.yml
  - [ ] Localizou: `webmaster_verifications: google:`
  - [ ] Colou string aqui (apenas o valor, sem aspas adicionais)
  - [ ] Exemplo: `google: "abc123def456"`

- [ ] **Build e push com verificação**
  ```bash
  JEKYLL_ENV=production bundle exec jekyll build
  git add _config.yml
  git commit -m "GSC: Adicionar verificação Google"
  git push origin main
  ```
  - [ ] Aguardou 5-10 min para GitHub Pages processar

- [ ] **Voltar ao GSC e Verificar**
  - [ ] Voltou para aba GSC
  - [ ] Clicou "Verify"
  - [ ] ✓ Página mostrou "Verification successful"

### Submissão de Sitemap
- [ ] **Abrir menu Sitemaps**
  - Link: https://search.google.com/search-console/sitemaps

- [ ] **Submeter sitemap**
  - [ ] Clicou "+ New sitemap"
  - [ ] Digitou: `sitemap.xml`
  - [ ] Clicou "Submit"
  - [ ] ✓ Status surgiu como "Success" (pode levar 1 dia)

### Verificação de Coverage
- [ ] **Acessar Coverage report**
  - Link: https://search.google.com/search-console/coverage

- [ ] **Anotar status**
  - [ ] Quantas URLs válidas? ___
  - [ ] Alguma com erro? ___
  - [ ] Alguma excluída? ___
  - ✓ Esperado: Válidas = ~10-50 (home, posts, páginas)

**SCORE FASE 2:** ___ / 12 ✓

---

## 🔍 FASE 3: VALIDAÇÃO DE SCHEMA (⏱️ 15 minutos)

### Teste de Schema
- [ ] **Acessar seu post em produção**
  - URL: https://blog.dataengineer.net.br/posts/the-history-of-artificial-intelligence/

- [ ] **Ver source code (F12 ou Ctrl+U)**
  - [ ] Abriu DevTools
  - [ ] Procuro por: `<script type="application/ld+json">`
  - ✓ Deve encontrar 3 blocos (BlogPosting, Author, Organization)

- [ ] **Copiar schema BlogPosting**
  - [ ] Selecionou o primeiro `<script>...</script>` inteiro
  - [ ] Ctrl+C para copiar

- [ ] **Validar em Schema Validator**
  - Link: https://validator.schema.org
  - [ ] Clicou "Validate" com a aba "Fetch URL" ou "Code Snippet"
  - [ ] Colou código: Ctrl+V
  - [ ] Clicou "Validate"
  - ✓ Resultado: "Valid"

- [ ] **Repetir para Author Schema**
  - [ ] Copiar segundo `<script>...</script>`
  - [ ] Colar no validator
  - [ ] Validar
  - ✓ Resultado: "Valid"

- [ ] **Repetir para Organization Schema (se production)**
  - [ ] Procura pelo terceiro `<script>...</script>`
  - [ ] Se encontrou: Copiar e validar (✓ Valid)
  - [ ] Se não encontrou (development): OK, é normal

### Google Rich Results Test
- [ ] **Testar em Rich Results Test**
  - Link: https://search.google.com/test/rich-results
  - [ ] Clicou "URL" tab
  - [ ] Colou: https://blog.dataengineer.net.br/posts/the-history-of-artificial-intelligence/
  - [ ] Clicou "Test"
  - ✓ Resultado: "Page qualifies for rich results"
  - [ ] Mostra "BlogPosting" como resultado

**SCORE FASE 3:** ___ / 10 ✓

---

## 💰 FASE 4: ADSENSE (⏱️ 10 minutos aplicação)

### Preparação
- [ ] **Revisar ads.txt local**
  ```bash
  cat ads.txt
  ```
  ✓ Deve estar vazio ou com comentários (será preenchido após aprovação)

- [ ] **Revisar privacy policy do blog**
  - Link: https://blog.dataengineer.net.br/privacy-policy/
  - [ ] Menciona AdSense? ✓ Sim (bom!)
  - [ ] Se não, adicione esta seção:
    ```
    ### Google AdSense
    Este site pode exibir anúncios fornecidos pelo Google AdSense.
    ```

### Aplicação AdSense
- [ ] **Acessar AdSense**
  - Link: https://AdSense.google.com
  - [ ] Conectado com Google Account

- [ ] **Clicar "Sign Up Now"**
  - [ ] Viu opções de conta
  - [ ] Selecionou "Publisher"

- [ ] **Preencher Formulário**
  - [ ] Website URL: `https://blog.dataengineer.net.br`
  - [ ] Country: Brazil / Brasil
  - [ ] Nome: Marcos Vasconcellos (ou nome preferido)
  - [ ] Email: seu@email.com
  - [ ] Aceitar Termos
  - [ ] Submeter

- [ ] **Aguardar Responsabilidade**
  - [ ] Email recebido de: `adsense-noreply@google.com`
  - ⏳ Aguardar 24-48h para revisão

- [ ] **Check Status**
  - [ ] Voltar a https://AdSense.google.com após 24h
  - [ ] Status da aplicação: _________
  - [ ] Se ✓ Aprovado: ir para seção "Publisher ID"
  - [ ] Se ❌ Rejeitado: revisar feedback, tentar novamente em 2 semanas

### Após Aprovação (QUANDO CHEGAR)
- [ ] **Ir para Accounts**
  - Link: https://AdSense.google.com/u/0/integration

- [ ] **Encontrar Publisher ID**
  - [ ] Procure por: `ca-pub-XXXXXXXXXXXXXXXX`
  - [ ] Copie este valor

- [ ] **Atualizar ads.txt**
  - [ ] Abra arquivo `ads.txt` no repo
  - [ ] Substitua comentário por:
    ```plaintext
    google.com, ca-pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
    ```
  - [ ] Salve o arquivo

- [ ] **Commit e Push**
  ```bash
  git add ads.txt
  git commit -m "AdSense: Adicionar Publisher ID"
  git push origin main
  ```

**SCORE FASE 4:** ___ / 10 ✓

---

## 📈 FASE 5: MONITORAMENTO (⏱️ 5 minutos/dia)

### Diário (Primeiros 30 dias)
- [ ] **Google Search Console**
  - [ ] Coverage: Algum novo erro? ___
  - [ ] Performance: Impressões: ___ CTR: ___%
  - [ ] Notações: Alguma mensagem vermelha? ___

- [ ] **Google Analytics**
  - [ ] Tráfego today: ___ sessões
  - [ ] Source: (organic / direct / referral)
  - [ ] Bounce rate: ___%

- [ ] **Seu Blog**
  - [ ] visitou https://blog.dataengineer.net.br/robots.txt
  - [ ] visitou https://blog.dataengineer.net.br/ads.txt
  - [ ] Sem erro? ✓ Sim

### Semanal (Semanas 2-4)
- [ ] **Search Console Weekly**
  - [ ] Total Impressions this week: ___
  - [ ] Total Clicks: ___
  - [ ] New keywords appearing? List: _________________
  - [ ] Any crawl errors? ___

- [ ] **Analytics Weekly**
  - [ ] Total sessions this week: ___
  - [ ] Avg. session duration: ___ segundos
  - [ ] Pages per session: ___
  - [ ] Top page: _________________

- [ ] **AdSense** (após ativação)
  - [ ] Impressions: ___
  - [ ] Clicks: ___
  - [ ] Earnings (USD): $___
  - [ ] CTR: ___%

### Mensal (Fim de cada mês)
- [ ] **Revisar Progress Geral**
  - [ ] Tráfego orgânico total mês: ___ vs mês anterior
  - [ ] Novos keywords ranking: ___
  - [ ] Ranking mejority: ___ posição melhorou
  - [ ] AdSense total earning: $___

- [ ] **Planejar Conteúdo**
  - [ ] Próximos 2-3 posts planejados? ___
  - [ ] Atualizar posts antigos? ___

**SCORE FASE 5:** ___ / 15 ✓

---

## 🎓 FASE 6: OTIMIZAÇÕES (⏱️ 30-60 minutos)

### On-Page SEO
- [ ] **Revisar Title Tags**
  - [ ] Post title tem número ou power word?
  - [ ] Menos de 60 caracteres? ✓ Yes
  - [ ] Antes: "A História da Inteligência Artificial"
  - [ ] Depois: "A História da IA: 70 Anos (1950-2025)" [sugestão]

- [ ] **Revisar Meta Descriptions**
  - [ ] Menos de 160 caracteres? ✓ Yes
  - [ ] Call-to-action claro? ✓ Yes
  - [ ] Inclui keyword principal? ✓ Yes

- [ ] **Revisar Heading Structure**
  - [ ] Um H1 por página? ✓ Yes
  - [ ] H2s em ordem lógica? ✓ Yes
  - [ ] Não pula níveis? ✓ Yes

- [ ] **Revisar Internal Links**
  - [ ] Links para sidebar (categories/tags)? ✓ Yes
  - [ ] Links internos no texto? ✗ Não (OK para primeiro post)
  - [ ] Próximo post: adicione 2-3 internos

### Technical SEO
- [ ] **Revisar Page Speed (Lighthouse)**
  - Ferramenta: Abra DevTools (F12) > Lighthouse
  - [ ] Performance: ___ / 100
  - [ ] Accessibility: ___ / 100
  - [ ] Best Practices: ___ / 100
  - [ ] SEO: ___ / 100
  - ✓ Alvo: Todos >80

- [ ] **Revisar Mobile Responsiveness**
  - Link: https://search.google.com/test/mobile-friendly
  - [ ] Resultado: "Page is mobile-friendly"

- [ ] **Revisar Core Web Vitals**
  - Link: https://search.google.com/test/core-web-vitals
  - [ ] LCP (Largest Contentful Paint): ___ ms (good: <2.5s)
  - [ ] FID (First Input Delay): ___ ms (good: <100ms)
  - [ ] CLS (Cumulative Layout Shift): ___ (good: <0.1)

### Content Quality
- [ ] **Revisar por duplicação**
  - Copiar 2-3 sentenças da seu post
  - Link: https://www.copyscape.com
  - [ ] Resultado: "No duplicate content detected" ✓

- [ ] **Revisar por Plagiarism**
  - Link: https://www.grammarly.com
  - [ ] Rodou spellcheck? ✓ Yes e 0 errors
  - [ ] Conteúdo é original? ✓ Yes

- [ ] **Revisar por Readability**
  - [ ] Frases < 20 palavras? Geralmente sim ✓
  - [ ] Parágrafos < 5 linhas? Sim ✓
  - [ ] Usando subheadings? Sim ✓
  - [ ] Usando lists/bullets? Sim ✓

**SCORE FASE 6:** ___ / 20 ✓

---

## 📋 RESUME FINAL

```
FASE 1 (Infraestrutura):    ___ / 15 ✓
FASE 2 (GSC):               ___ / 12 ✓
FASE 3 (Schema):            ___ / 10 ✓
FASE 4 (AdSense):           ___ / 10 ✓
FASE 5 (Monitoramento):     ___ / 15 ✓
FASE 6 (Otimizações):       ___ / 20 ✓
                           ───────────────
TOTAL:                      ___ / 82 ✓
```

**Score Esperado:**
- 60-70: ⭐ Bom começo
- 70-80: ⭐⭐ Muito bom  
- 80+:   ⭐⭐⭐ Excelente!

---

## 🎉 Checklist Concluído!

Parabéns! Sua implementação de SEO & AdSense está:
- ✅ Estruturada
- ✅ Otimizada
- ✅ Pronta para crescimento
- ✅ Configurada para monetização

**Próximas semanas:** Monitorar dados e criar novo conteúdo!

---

**Data Início:** Fevereiro 2026  
**Data Conclusão:** ___________  
**Assinado:** ___________

*Imprima e coloque na parede! 🚀*
