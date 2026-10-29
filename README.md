# Blog de Arquitetura de Dados e Inteligência Artificial 🧠⚙️

Repositório do blog de arquitetura de dados e inteligência artificial, publicado em [marcos-data-engineer.github.io/blog](https://marcos-data-engineer.github.io/blog).

O conteúdo aborda engenharia de dados, arquitetura, modelos de linguagem de grande porte (LLMs), inteligência artificial generativa e ferramentas modernas de desenvolvimento.

## Tecnologias

- **Gerador de sites estáticos:** [Jekyll](https://jekyllrb.com/)
- **Tema:** [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
- **Publicação e CI/CD:** GitHub Pages, automatizado por GitHub Actions.

## Recursos

- Otimização para mecanismos de busca com `jekyll-seo-tag` e `jekyll-sitemap`.
- Comentários por meio do Utterances, usando discussões do GitHub.
- Apoio ao projeto via LivePix.
- Dados estruturados Schema.org para artigos, autoria e organização.
- RSS, busca e navegação por categorias e tags.

## Estrutura do repositório

- `_posts/`: artigos em Markdown.
- `_data/`: configurações de idioma, contato e compartilhamento.
- `_includes/`: componentes HTML reutilizáveis e metadados estruturados.
- `_layouts/`: modelos de páginas e artigos.
- `_tabs/`: páginas de navegação do site.
- `assets/`: imagens, ícones, folhas de estilo e scripts.
- `_config.yml`: configuração principal do Jekyll.

## Executar localmente

Requisitos: Ruby, Bundler, Node.js e npm.

1. Instale as dependências Ruby:

   ```bash
   bundle install
   ```

2. Instale as dependências JavaScript:

   ```bash
   npm install
   ```

3. Inicie o site:

   ```bash
   bundle exec jekyll serve
   ```

4. Acesse <http://localhost:4000/blog/>.

Para compilar os recursos JavaScript, execute `npm run build` antes de iniciar o Jekyll.

## Autoria

Projeto criado e mantido por Marcos Vasconcellos de Andrade, em Brasília, Brasil. O conteúdo reflete estudos e experiências práticas em arquitetura de dados, infraestrutura, inteligência artificial generativa, agentes autônomos e ferramentas modernas de desenvolvimento.

> A URL pública e o caminho-base são definidos em `_config.yml`. Mantenha-os alinhados ao domínio configurado no GitHub Pages para evitar URLs canônicas e sitemaps apontando para endereços diferentes.
