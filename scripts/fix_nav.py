import re
import os
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_BLOCK_RE = re.compile(
    r'        <li class="has-children[^"]*">\n'
    r'          <button class="nav-parent" aria-expanded="false">Publications</button>\n'
    r'          <div class="submenu">\n'
    r'(?:.*\n)*?'
    r'          </div>\n'
    r'        </li>\n',
)

NEW_BLOCK = '        <li><a href="/publications.html">Publications</a></li>\n'

files = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "people", "*.html"))
changed = []
for fp in files:
    if os.path.basename(fp) == "publications.html":
        continue
    with open(fp, encoding="utf-8") as f:
        content = f.read()
    new_content, n = OLD_BLOCK_RE.subn(NEW_BLOCK, content)
    if n:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_content)
        changed.append((fp, n))

for fp, n in changed:
    print(f"{fp}: {n} replacement(s)")
print(f"{len(changed)} files changed")
