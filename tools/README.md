# Site tools

- `posts.json` / `meta.json`: LinkedIn posts (exact text) and their LinkedIn activity IDs.
- `build.py <site_dir>`: rebuilds `posts/*.html`, `writing.html` and the Home page's latest-posts sections.
- `seo.py <site_dir> [base_url]`: adds link-preview tags, preview images (`images/og/`), `sitemap.xml` and `robots.txt`. Run after `build.py`, and again with the new base URL if the domain changes.
