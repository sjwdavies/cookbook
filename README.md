# Taylor-Davies Family Cookbook

This repository powers the Cookbook site (MkDocs + GitHub Pages) and uses GitHub Actions to:
- Convert **JSON recipes** in `data/recipes/` into **Markdown** under `recipes/<category>/`
- Auto-build tag pages, category indexes, and an "All recipes" listing
- Lint Markdown
- Build and deploy the site to GitHub Pages

## Quick Start
1. Commit a JSON recipe to `data/recipes/` (see `data/recipes/example.json`).
2. GitHub Actions will generate Markdown in `recipes/`.
3. The Pages workflow will build and deploy the site.

## Local preview
```bash
pip install -r requirements.txt
mkdocs serve
```
Then open http://127.0.0.1:8000
