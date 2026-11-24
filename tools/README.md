# Site tools

- `posts.json` / `meta.json`: LinkedIn posts (exact text) and their LinkedIn activity IDs.
- `build.py <site_dir>`: rebuilds `posts/*.html`, `writing.html` and the Home page's latest-posts sections.
- `seo.py <site_dir> [base_url]`: adds link-preview tags, preview images (`images/og/`), `sitemap.xml` and `robots.txt`. Run after `build.py`, and again with the new base URL if the domain changes.

## Daily post workflow

1. Add the post text to `posts.json` (next number as key; first line = title) and `{"id": "", "date": "YYYY-MM-DD"}` to `meta.json`.
2. Write a carousel spec (see the top of `carousel.py`) and run `python3 tools/carousel.py spec.json` → `tools/slides/<slug>.pdf` (the file to upload to LinkedIn).
3. `python3 tools/build.py .` → `python3 tools/slides.py .` → `python3 tools/build.py .` → `python3 tools/seo.py .`
4. After it is live on LinkedIn, put the activity ID in `meta.json` and rebuild (build.py, seo.py).
