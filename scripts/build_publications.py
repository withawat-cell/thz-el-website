import re
import os
import json
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "content-raw", "journal-notes-links.json"), encoding="utf-8") as f:
    KNOWN_LINKS = json.load(f)

def linkify_known(notes):
    """Turn 'Label (url)' / 'Label: url' pairs the live site renders as a
    hyperlink into markdown links, using the exact (text, href) pairs
    scraped from the live page."""
    for item in KNOWN_LINKS:
        text, href = item["text"], item["href"]
        href_re = re.escape(href)
        notes = re.sub(rf"{re.escape(text)}\s*\({href_re}\)", f"[{text}]({href})", notes)
        notes = re.sub(rf"{re.escape(text)}\s*:\s*{href_re}", f"[{text}]({href})", notes)
    return notes

def md_inline(s):
    s = s.strip()
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s

TRIM_PREFIXES = ["One of the ", "Among the ", "Among top ", "Among "]
MAX_PILL_LEN = 46

def shorten(original):
    p = original
    for pre in TRIM_PREFIXES:
        if p.startswith(pre):
            p = p[len(pre):]
            break
    if len(p) <= MAX_PILL_LEN:
        return p
    return p[:MAX_PILL_LEN].rsplit(" ", 1)[0] + "…"

LINK_RE = re.compile(r'<a href="([^"]+)">([^<]+)</a>')

def split_notes(notes):
    """Split a Notes cell into (pills, remainder_html).
    Each pill is a dict: {short, full (title tooltip or None), href (or None)}."""
    if not notes or not notes.strip():
        return [], ""
    notes = linkify_known(notes)
    parts = [p.strip() for p in notes.split(";") if p.strip()]
    pills, rest = [], []
    for p in parts:
        p_html = md_inline(p)
        links = LINK_RE.findall(p_html)
        plain_len = len(re.sub(r"<[^>]+>", "", p_html))
        anchor_len = sum(len(t) for _, t in links)
        if not links:
            short = shorten(p_html)
            pills.append({"short": short, "full": p_html if short != p_html else None, "href": None})
        elif len(links) == 1 and anchor_len >= plain_len * 0.7:
            href, text = links[0]
            short = shorten(text)
            pills.append({"short": short, "full": text if short != text else None, "href": href})
        else:
            rest.append(p_html)
    return pills, " &middot; ".join(rest)

def pills_html(pills):
    if not pills:
        return ""
    spans = []
    for pill in pills:
        title_attr = f' title="{html.escape(pill["full"])}"' if pill["full"] else ""
        label = html.escape(pill["short"])
        if pill["href"]:
            inner = f'<a href="{html.escape(pill["href"])}">{label}</a>'
        else:
            inner = label
        spans.append(f'<span class="tag tag-award"{title_attr}>{inner}</span>')
    return '<span class="tag-row" style="margin-top:6px;">' + "".join(spans) + "</span>"

# ---------- Journal articles ----------

def load_journal_images():
    path = os.path.join(ROOT, "content-raw", "journal-article-images.txt")
    imgs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idx, url = line.split("|", 1)
            if url != "MISSING":
                imgs[int(idx)] = f"/assets/img/publications/j{idx}.jpg"
    return imgs

TITLE_RE = re.compile(r'"([^"]+)"')

def build_journal():
    src = os.path.join(ROOT, "content-raw", "publications-journal-articles.md")
    with open(src, encoding="utf-8") as f:
        text = f.read()
    year_blocks = re.findall(r"^## (\d{4})\n\n(.*?)(?=\n## |\n---)", text, re.S | re.M)
    images = load_journal_images()

    sections = []
    global_idx = 0
    for year, block in year_blocks:
        rows = [l for l in block.strip().split("\n") if l.startswith("|")][2:]
        entries = []
        for row in rows:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) < 4:
                continue
            _, citation, doi, notes = cells
            doi = doi.strip()
            primary_doi = doi.split(" ")[0] if doi.startswith("http") else ""
            citation_html = md_inline(citation)
            m = TITLE_RE.search(citation_html)
            if m and primary_doi:
                title_linked = f'<a href="{html.escape(primary_doi)}">{m.group(1)}</a>'
                citation_html = citation_html[:m.start()] + '"' + title_linked + '"' + citation_html[m.end():]
            pills, rest = split_notes(notes)
            if any(p["short"] == "Accepted" for p in pills):
                pills = [p for p in pills if p["short"] != "Accepted"]
                citation_html += " (Accepted)"
            img = images.get(global_idx)
            thumb = f'<img class="pub-thumb" src="{img}" alt="" loading="lazy">' if img else '<span class="pub-thumb-empty" aria-hidden="true"></span>'
            meta_bits = []
            if rest:
                meta_bits.append(rest)
            meta_html = f'<p class="entry-meta">{" &middot; ".join(meta_bits)}</p>' if meta_bits else ""
            entries.append(f'''      <li class="pub-entry">
        {thumb}
        <div class="entry-body">
          <p class="entry-title">{citation_html}</p>
          {meta_html}
          {pills_html(pills)}
        </div>
      </li>''')
            global_idx += 1
        sections.append(f'    <h3 class="year-heading">{year}</h3>\n    <ul class="pub-list">\n' + "\n".join(entries) + "\n    </ul>")
    return "\n\n".join(sections)

# ---------- Conference presentations ----------

def build_conference():
    src = os.path.join(ROOT, "content-raw", "publications-conference-presentations.md")
    with open(src, encoding="utf-8") as f:
        text = f.read()
    year_blocks = re.findall(r"^## (\d{4})\n((?:\d+\..*\n?)+)", text, re.M)
    sections = []
    for year, block in year_blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        entries = []
        for line in lines:
            m = re.match(r"^\d+\.\s+(.*)$", line)
            if not m:
                continue
            raw = m.group(1)
            # pull trailing "(...)" status annotation off the end, e.g. "(Invited)" or "(Keynote; online)"
            status_m = re.search(r"\(([^()]*)\)\s*$", raw)
            pills, rest_note = [], ""
            if status_m:
                inner = status_m.group(1)
                raw_wo = raw[:status_m.start()].rstrip()
                sub_pills, sub_rest = split_notes(inner)
                pills = sub_pills
                rest_note = sub_rest
            else:
                raw_wo = raw
            citation_html = md_inline(raw_wo)
            meta_html = f'<p class="entry-meta">{rest_note}</p>' if rest_note else ""
            entries.append(f'''      <li class="pub-entry">
        <div class="entry-body">
          <p class="entry-title">{citation_html}</p>
          {meta_html}
          {pills_html(pills)}
        </div>
      </li>''')
        sections.append(f'    <h3 class="year-heading">{year}</h3>\n    <ul class="pub-list">\n' + "\n".join(entries) + "\n    </ul>")
    return "\n\n".join(sections)

journal_html = build_journal()
conference_html = build_conference()

theses_html = '''      <table class="data">
        <thead>
          <tr><th>Year</th><th>Author</th><th>Thesis title</th></tr>
        </thead>
        <tbody>
          <tr><td>2026</td><td>Sakib Quader</td><td><a href="https://drive.google.com/file/d/1W8QM0EWFt0FOjtZ4Us-JBglzDmPG6kci/view?usp=sharing">Terahertz Metasurfaces for Wave Manipulation, Detection, and Spectral Analysis</a></td></tr>
          <tr><td>2026</td><td>Linxi Chen</td><td><a href="https://drive.google.com/file/d/1Aznq9yxst9Jcf6AgWgh_3x2C86msNjcw/view?usp=sharing">Enabling Polarisation and Frequency Control in Silicon-based Terahertz Integration</a></td></tr>
          <tr><td>2025</td><td>Harrison Lees</td><td><a href="https://drive.google.com/file/d/1LmGbV1kmSq7bIvSqBfMJ_h_AlrtEY6vU/view?usp=drive_link">All-dielectric Terahertz Waveguides, Devices, and Techniques</a></td></tr>
          <tr><td>2024</td><td>Mingxiang Li</td><td><a href="https://drive.google.com/file/d/15CJXWQRQiDyEu1E8wug1PTNDyc1sNbJk/view?usp=sharing">Planar Antennas and Lenses for Terahertz Source Integration</a></td></tr>
          <tr><td>2024</td><td>Panisa Dechwechprasit</td><td><a href="https://drive.google.com/file/d/1pT2D7iBJQhsEdHyM6LIFcZNmyZOp6THf/view?usp=sharing">Tunable Terahertz Components on Substrateless Silicon Platform</a></td></tr>
          <tr><td>2023</td><td>Mohamed Shehata</td><td><a href="https://drive.google.com/file/d/1lp1QtiLngMfPHv83MPc6nqQ4CIPOEyV5/view?usp=sharing">Pulse Shaping for Terahertz Communications</a></td></tr>
          <tr><td>2022</td><td>Weijie Gao</td><td><a href="https://drive.google.com/file/d/1aCrscCKxx-WVFCWqplah432e6Z5hvZDz/view?usp=sharing">Effective-Medium-Clad Dielectric Components Towards Terahertz Integrated Platform</a></td></tr>
          <tr><td>2021</td><td>Xiaolong You</td><td><a href="https://drive.google.com/file/d/1hjK8BNyG74linQ7OxC4tJaNmTvtaB-J5/view?usp=sharing">Broadband Terahertz Metasurfaces</a></td></tr>
          <tr><td>2018</td><td>Wendy S.-L. Lee</td><td><a href="https://drive.google.com/file/d/1o7AS-8NutjgowlgLGchyK0E7LAh0HWSk/view?usp=sharing">Terahertz Metasurfaces for Wideband Polarisation Control</a></td></tr>
          <tr><td>2017</td><td>Daniel Headland</td><td><a href="https://drive.google.com/file/d/1jVAc4gv89OScGtsN1ecLfv6c04hSH_Qa/view?usp=sharing">Efficient Terahertz-Range Beam Control Using Flat Optics</a></td></tr>
        </tbody>
      </table>'''

codes_html = '''      <div class="card-grid">
        <div class="card">
          <img src="/assets/img/research/code-comm-chain.jpg" alt="End-to-end wireless communication chain simulator interface" loading="lazy">
          <h3>End-to-End Wireless Communication Chain Simulator</h3>
          <p>A MATLAB application for modelling, testing, and demonstrating complete wireless communication chains, built to align with the laboratory's transmission hardware. It supports sinusoidal and complex waveform transmission, with built-in digital compensation modules &mdash; including IQ-imbalance correction and coarse time-synchronisation &mdash; for evaluating system robustness and isolating hardware-induced impairments. Designed as a standalone interface for rapid experimentation, algorithm development, and hardware-in-the-loop testing.</p>
          <p class="small">Developed by <a href="https://www.linkedin.com/in/marlon-kha-208141293/">Marlon Kha</a></p>
          <div class="entry-links"><a href="https://github.com/withawat-cell/comm_chain.git">Repository &rarr;</a></div>
        </div>
        <div class="card">
          <img src="/assets/img/research/code-cst-sim.jpg" alt="CST simulation of a substrateless terahertz waveguide" loading="lazy">
          <h3>CST Simulation of Substrateless Terahertz Waveguide</h3>
          <p>A Python automation script for CST Studio Suite (Python 3.12, CST Microwave Studio 2025) that builds, configures, and runs full-wave transient simulations for substrateless (effective-medium-clad) dielectric terahertz waveguides, based on the design principles below.</p>
          <p class="small">W. Gao et al., "Effective-medium-cladded dielectric waveguides for terahertz waves," <em>Optics Express</em>, vol. 27, no. 26, pp. 38721&ndash;38734, 2019. <a href="https://doi.org/10.1364/OE.382181">doi.org/10.1364/OE.382181</a><br>
          W. Gao et al., "Characteristics of effective-medium-clad dielectric waveguides," <em>IEEE Transactions on Terahertz Science and Technology</em>, vol. 11, no. 1, pp. 28&ndash;41, 2021. <a href="https://ieeexplore.ieee.org/document/9195766">ieeexplore.ieee.org/document/9195766</a></p>
          <div class="entry-links"><a href="https://gist.github.com/withawat-cell/5f3192e66faae0e291e63ef4a68d6c75">Gist &rarr;</a></div>
        </div>
      </div>'''

template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Publications — Terahertz Engineering Laboratory</title>
<meta name="description" content="Journal articles, conference presentations, PhD theses, and research software from the Terahertz Engineering Laboratory, Adelaide University.">
<link rel="icon" href="/assets/img/brand/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>

<header class="site-header">
  <div class="site-header-inner">
    <a class="brand plain" href="/index.html">
      <img class="brand-mark" src="/assets/img/brand/mark-white.png" alt="THz">
      <span class="brand-name">Terahertz Engineering Laboratory</span>
    </a>
    <nav class="primary-nav" aria-label="Primary">
      <ul>
        <li><a href="/index.html">Home</a></li>
        <li><a href="/research.html">Research</a></li>
        <li><a href="/publications.html" aria-current="page">Publications</a></li>
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
      <h1>Publications</h1>
      <p class="lead">Journal articles, conference presentations, PhD theses, and research software from the Terahertz Engineering Laboratory.</p>
      <div class="filter-tabs" role="tablist" aria-label="Filter publications by type">
        <button class="filter-tab" data-filter="all" aria-pressed="true">All</button>
        <button class="filter-tab" data-filter="journal" aria-pressed="false">Journal Articles</button>
        <button class="filter-tab" data-filter="conference" aria-pressed="false">Conference Presentations</button>
        <button class="filter-tab" data-filter="theses" aria-pressed="false">PhD Theses</button>
        <button class="filter-tab" data-filter="codes" aria-pressed="false">Codes</button>
      </div>
    </div>
  </section>

  <section class="block pub-section" data-type="journal">
    <div class="wrap-wide">
      <h2>Journal articles</h2>
      <p class="prose small" style="margin-bottom:24px;">Most recent first. Excludes journal publications prior to the lab's establishment and those in the microwave and optics domains outside terahertz.</p>
{journal}
    </div>
  </section>

  <section class="block pub-section" data-type="conference">
    <div class="wrap-wide">
      <h2>Selected conference presentations</h2>
      <p class="prose small" style="margin-bottom:24px;">Invited talks, keynotes, and presentations at international conferences and workshops.</p>
{conference}
    </div>
  </section>

  <section class="block pub-section" data-type="theses">
    <div class="wrap-wide">
      <h2>PhD theses</h2>
{theses}
    </div>
  </section>

  <section class="block pub-section" data-type="codes">
    <div class="wrap-wide">
      <h2>Codes</h2>
{codes}
    </div>
  </section>

</main>

<footer class="site-footer">
  <div class="wrap-wide" style="display:block;">
    <p class="acknowledgement">We acknowledge and pay our respects to the Kaurna people, the traditional custodians whose ancestral lands we gather on. We acknowledge the deep feelings of attachment and relationship of the Kaurna people to country and we respect and value their past, present and ongoing connection to the land and cultural beliefs.</p>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px;">
      <span>&copy; <span data-year>2026</span> Terahertz Engineering Laboratory, Adelaide University</span>
      <span><a href="/contact.html">Contact</a> &middot; <a href="https://www.linkedin.com/company/thz-el">LinkedIn</a></span>
    </div>
  </div>
</footer>

<script src="/assets/js/main.js"></script>
<script src="/assets/js/publications-filter.js"></script>
</body>
</html>
"""

out = (template
       .replace("{journal}", journal_html)
       .replace("{conference}", conference_html)
       .replace("{theses}", theses_html)
       .replace("{codes}", codes_html))

with open(os.path.join(ROOT, "publications.html"), "w", encoding="utf-8") as f:
    f.write(out)

print("Wrote publications.html")
