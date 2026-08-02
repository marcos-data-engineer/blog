# Blog de Inteligência Artificial 🧠⚙️

Bem-vindo ao repositório oficial do blog sobre Inteligência Artificial, hospedado em [blog.dataengineer.ne.br](https://blog.dataengineer.ne.br). 

Este espaço é dedicado à exploração, documentação e compartilhamento de conhecimentos sobre IA, arquitetura de dados, Large Language Models (LLMs) e ferramentas de desenvolvimento de ponta.

## 🛠️ Tecnologias e Arquitetura

O blog foi construído com foco em performance, acessibilidade e facilidade de manutenção, utilizando as seguintes tecnologias:

* **Gerador de Site Estático:** [Jekyll](https://jekyllrb.com/)[cite: 2]
* **Tema:** [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) - Um tema limpo, responsivo e focado em texto[cite: 2].
* **Hospedagem & CI/CD:** GitHub Pages via GitHub Actions (`pages.yml`) para deploy automatizado[cite: 2].

## ✨ Funcionalidades Integradas

O repositório já conta com diversas configurações e integrações avançadas:

* **SEO e Monetização:** Otimização para motores de busca e revisão do Google AdSense implementadas (`SEO_ADSENSE_REVIEW.md`, `ads.txt`)[cite: 2].
* **Sistema de Comentários:** Integração com o Utterances, permitindo que os leitores comentem usando issues do GitHub[cite: 2].
* **Apoio ao Projeto:** Botão de doação via PayPal configurado (`paypal_donation.html`)[cite: 2].
* **Metadados Estruturados:** Configurações de Schema.org para artigos, autor e organização, melhorando a indexação[cite: 2].

## 📁 Estrutura do Repositório

Aqui está um resumo de como o repositório está organizado[cite: 2]:

* `_posts/`: Contém os artigos do blog em formato Markdown (ex: `2024-07-24-the-history-of-artificial-intelligence.md`).
* `_data/`: Arquivos de configuração de dados, como contatos e opções de compartilhamento social.
* `_includes/`: Componentes modulares de HTML (cabeçalho, rodapé, comentários, esquemas de SEO).
* `_layouts/`: Templates de páginas (como o template padrão de `post`).
* `assets/`: Arquivos estáticos, incluindo imagens, ícones, CSS e scripts minificados.
* `_config.yml`: Arquivo principal de configuração do Jekyll.

## 🚀 Como Executar Localmente

Se você deseja rodar o blog localmente para testar alterações ou escrever novos artigos antes do deploy, siga os passos abaixo:

1. **Pré-requisitos:** Certifique-se de ter o [Ruby](https://www.ruby-lang.org/) e o [Bundler](https://bundler.io/) instalados no seu ambiente.
2. **Instalação das dependências:**
   ```bash
   bundle install
