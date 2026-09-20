# Terahertz Engineering Laboratory — website

Static site for the Terahertz Engineering Laboratory (University of Adelaide), rebuilt from the previous Google Sites site. Plain HTML/CSS/JS, no build step, no framework — designed to be served as-is by GitHub Pages.

## Structure

```
index.html                 Home
research.html               Research clusters + gallery
opportunities.html
contact.html
publications/
  journal-articles.html
  conference-presentations.html
  phd-theses.html
  codes.html
people/
  researchers.html
  alumni.html
  coursework.html
  visitors.html
assets/
  css/style.css            Design system (dark, minimal, academic)
  js/main.js                Nav toggle/dropdown, active-link highlight, footer year
  img/                      All images, already resized/compressed for the web
scripts/
  fetch_images.py           Downloads + resizes images from a JSON manifest (Pillow)
  build_journal_articles.py Regenerates publications/journal-articles.html from content-raw/
  build_conference.py       Regenerates publications/conference-presentations.html
  build_coursework.py       Regenerates people/coursework.html
```

There are no server-side includes — the header/nav/footer markup is duplicated at the top/bottom of every page. If you change the nav, update it in every `.html` file (a simple find-and-replace across the project works fine).

## Local preview

Any static file server works, e.g.:

```bash
python -m http.server 8090
```

then open `http://localhost:8090/index.html`. Don't open the HTML files directly via `file://` — the site uses root-relative asset paths (`/assets/...`) which only resolve correctly from a server root.

## Deploying on GitHub Pages

1. Push this repo to GitHub.
2. In the repo's Settings → Pages, set the source to the `main` branch, root folder.
3. The `CNAME` file already points at `thz-el.org` — set your DNS (A/ALIAS or CNAME record) to GitHub Pages per [GitHub's custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site), and enable "Enforce HTTPS" once DNS has propagated.
4. `.nojekyll` disables Jekyll processing so files are served as-is.

## Updating content

Everything is hand-authored HTML — open the relevant page and edit directly. For the three data-heavy list pages (journal articles, conference presentations, coursework students) it's easier to add a row to the corresponding table in `content-raw/*.md` and re-run the matching `scripts/build_*.py` script, which regenerates the HTML from scratch.

## Adding new images

Add an entry to a manifest JSON (see `scripts/manifest_*.json` for examples: `{"url": ..., "out": "assets/img/...", "max_w": 700}`) and run:

```bash
python scripts/fetch_images.py scripts/your_manifest.json
```

This downloads the image and resizes/compresses it so nothing ships at full source resolution.
