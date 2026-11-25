# Site tools

- `posts.json` / `meta.json`: LinkedIn posts (exact text) and their LinkedIn activity IDs.
- `build.py <site_dir>`: rebuilds `posts/*.html`, `writing.html` and the Home page's latest-posts sections.
- `seo.py <site_dir> [base_url]`: adds link-preview tags, preview images (`images/og/`), `sitemap.xml` and `robots.txt`. Run after `build.py`, and again with the new base URL if the domain changes.

## Daily post workflow

1. Add the post text to `posts.json` (next number as key; first line = title) and `{"id": "", "date": "YYYY-MM-DD"}` to `meta.json`.
2. Write a carousel spec (see the top of `carousel.py`) and run `python3 tools/carousel.py spec.json` → `tools/slides/<slug>.pdf` (the file to upload to LinkedIn).
3. `python3 tools/build.py .` → `python3 tools/slides.py .` → `python3 tools/build.py .` → `python3 tools/seo.py .`
4. After it is live on LinkedIn, put the activity ID in `meta.json` and rebuild (build.py, seo.py).

## Sending LinkedIn readers to the website

- Every post has a short link: `kumarashwani-law.github.io/p/<post number>` (built by `build.py` into `p/`). It redirects to the post with `utm_source=linkedin`, so GoatCounter shows these visits as coming from LinkedIn.
- Carousels: put `"key": "<post number>"` in the carousel spec; the last slide then shows the short link in a lime box, and every slide after the cover shows the site address in its footer.
- Post text: end the body (before the hashtags) with a line pointing to the website, e.g. "Full article, sources and the case timeline on my website: link in the first comment."
- After publishing on LinkedIn, add the first comment: "Full article with sources: https://kumarashwani-law.github.io/p/<post number>".
