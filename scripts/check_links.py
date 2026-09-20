import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "http://localhost:8090"

html_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath or "content-raw" in dirpath:
        continue
    for fn in filenames:
        if fn.endswith(".html"):
            html_files.append(os.path.join(dirpath, fn))

internal_paths = set()
external_urls = set()

for fp in html_files:
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    for m in re.finditer(r'(?:href|src)="([^"]+)"', content):
        url = m.group(1)
        if url.startswith("/"):
            internal_paths.add(url)
        elif url.startswith("http"):
            external_urls.add(url)

print(f"{len(html_files)} html files, {len(internal_paths)} unique internal paths, {len(external_urls)} unique external urls\n")

print("=== Checking internal paths (local server) ===")
bad = 0
for path in sorted(internal_paths):
    try:
        req = urllib.request.Request(BASE + path, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        status = f"ERROR {e}"
    if status != 200:
        bad += 1
        print(f"  {status}  {path}")
print(f"{bad} broken internal paths out of {len(internal_paths)}")
