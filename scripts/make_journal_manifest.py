import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content-raw", "journal-article-images.txt")
OUT = os.path.join(ROOT, "scripts", "manifest_journal.json")

entries = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        idx, url = line.split("|", 1)
        if url == "MISSING":
            continue
        entries.append({"url": url, "out": f"assets/img/publications/j{idx}.jpg", "max_w": 320})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=1)
print(len(entries), "entries written to", OUT)
