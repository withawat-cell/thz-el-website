import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content-raw", "publications-conference-presentations.md")
OUT = os.path.join(ROOT, "publications", "conference-presentations.html")

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

year_blocks = re.findall(r"^## (\d{4})\n((?:\d+\..*\n?)+)", text, re.M)

def md_inline(s):
    s = s.strip()
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s

sections_html = []
for year, block in year_blocks:
    lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
    entries = []
    for line in lines:
        m = re.match(r"^\d+\.\s+(.*)$", line)
        if not m:
            continue
        citation = md_inline(m.group(1))
        entries.append(f'      <li class="pub-entry">\n        <p class="entry-title">{citation}</p>\n      </li>')
    sections_html.append(f'    <h3 class="year-heading">{year}</h3>\n    <ul class="pub-list">\n' + "\n".join(entries) + "\n    </ul>")

body = "\n\n".join(sections_html)

template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conference Presentations — Terahertz Engineering Laboratory</title>
<meta name="description" content="Selected conference presentations from the Terahertz Engineering Laboratory, University of Adelaide.">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>

<header class="site-header">
  <div class="site-header-inner">
    <a class="brand plain" href="/index.html">
      <span class="brand-mark">THz</span>
      <span class="brand-name">Terahertz Engineering Laboratory</span>
    </a>
    <nav class="primary-nav" aria-label="Primary">
      <ul>
        <li><a href="/index.html">Home</a></li>
        <li><a href="/research.html">Research</a></li>
        <li class="has-children open">
          <button class="nav-parent" aria-expanded="false">Publications</button>
          <div class="submenu">
            <a href="/publications/journal-articles.html">Journal Articles</a>
            <a href="/publications/conference-presentations.html" aria-current="page">Conference Presentations</a>
            <a href="/publications/phd-theses.html">PhD Theses</a>
            <a href="/publications/codes.html">Codes</a>
          </div>
        </li>
        <li class="has-children">
          <button class="nav-parent" aria-expanded="false">People</button>
          <div class="submenu">
            <a href="/people/researchers.html">Researchers</a>
            <a href="/people/alumni.html">Alumni</a>
            <a href="/people/coursework.html">Coursework Students</a>
            <a href="/people/visitors.html">Visitors</a>
          </div>
        </li>
        <li><a href="/opportunities.html">Opportunities</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false"><span></span></button>
  </div>
</header>

<main>

  <section class="page-hero">
    <div class="wrap-wide">
      <p class="hero-eyebrow">Publications</p>
      <h1>Selected conference presentations</h1>
      <p class="lead">Invited talks, keynotes, and presentations at international conferences and workshops.</p>
    </div>
  </section>

  <section class="block">
    <div class="wrap-wide">
{body}
    </div>
  </section>

</main>

<footer class="site-footer">
  <div class="wrap-wide" style="display:block;">
    <p class="acknowledgement">We acknowledge and pay our respects to the Kaurna people, the traditional custodians whose ancestral lands we gather on. We acknowledge the deep feelings of attachment and relationship of the Kaurna people to country and we respect and value their past, present and ongoing connection to the land and cultural beliefs.</p>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px;">
      <span>&copy; <span data-year>2026</span> Terahertz Engineering Laboratory, University of Adelaide</span>
      <span><a href="/contact.html">Contact</a> &middot; <a href="https://www.linkedin.com/company/thz-el">LinkedIn</a></span>
    </div>
  </div>
</footer>

<script src="/assets/js/main.js"></script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(template.replace("{body}", body))

print("Wrote", OUT, "-", len(year_blocks), "year sections")
