import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content-raw", "visitor-images.txt")
OUT = os.path.join(ROOT, "scripts", "manifest_visitors_fix.json")

slug_map = {
    "Mallika": "v-suresh", "Yiwei Xie": "v-xie", "Ngo Hoai": "v-ngo", "Jan C. Balzer": "v-balzer",
    "Ekrem": "v-yildiz", "Hibiki Shiiba": "v-shiiba", "Milan Deumer": "v-deumer", "Yixiong Zhao": "v-zhao",
    "Shamendra": "v-egodawela", "Qigejian": "v-wang", "Vladyslav": "v-cherniak", "Fedor Kovalev": "v-kovalev",
    "Rajour Tanyi Ako": "v-ako", "Orawanya": "v-orawanya", "Yossamon": "v-yossamon", "Tanatep": "v-tanatep",
    "Phojchara": "v-phojchara", "Nicolle": "v-nicolle", "Lalitsuda": "v-lalitsuda",
    "Nontiwat Amnuayphol": "v-nontiwat", "Stanley Chen": "v-stanley", "Xuan-Wei": "v-shevy",
    "Ting-Yu": "v-tiffany", "Shou-Feng": "v-robert", "Takuro": "v-takuro",
}

entries = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        name, url = line.split("|", 1)
        slug = slug_map[name]
        entries.append({"url": url, "out": f"assets/img/people/{slug}.jpg", "max_w": 300})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=1)
print(len(entries), "entries")
