# Artificial Intelligence Blog 🧠⚙️

Welcome to the official repository for the Artificial Intelligence blog, hosted at [blog.dataengineer.ne.br](https://blog.dataengineer.ne.br). 

This space is dedicated to exploring, documenting, and sharing knowledge about AI, data architecture, Large Language Models (LLMs), and cutting-edge development tools.

## 🛠️ Technologies and Architecture

The blog was built with a focus on performance, accessibility, and maintainability, utilizing the following technologies:

* **Static Site Generator:** [Jekyll](https://jekyllrb.com/)
* **Theme:** [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) - A clean, responsive, and text-focused theme.
* **Hosting & CI/CD:** GitHub Pages via GitHub Actions (`pages.yml`) for automated deployment.

## ✨ Integrated Features

The repository already includes several advanced configurations and integrations:

* **SEO and Monetization:** Search engine optimization and Google AdSense review implemented (`SEO_ADSENSE_REVIEW.md`, `ads.txt`).
* **Commenting System:** Integration with Utterances, allowing readers to comment using GitHub issues.
* **Project Support:** PayPal donation button configured (`paypal_donation.html`).
* **Structured Metadata:** Schema.org configurations for articles, author, and organization, improving search engine indexing.

## 📁 Repository Structure

Here is a summary of how the repository is organized:

* `_posts/`: Contains the blog articles in Markdown format (e.g., `2024-07-24-the-history-of-artificial-intelligence.md`).
* `_data/`: Data configuration files, such as contacts and social sharing options.
* `_includes/`: Modular HTML components (header, footer, comments, SEO schemas).
* `_layouts/`: Page templates (such as the default `post` template).
* `assets/`: Static files, including images, icons, CSS, and minified scripts.
* `_config.yml`: Main Jekyll configuration file.

## 🚀 How to Run Locally

If you want to run the blog locally to test changes or write new articles before deployment, follow the steps below:

1. **Prerequisites:** Make sure you have [Ruby](https://www.ruby-lang.org/) and [Bundler](https://bundler.io/) installed in your environment.
2. **Install dependencies:**
   ```bash
   bundle install
