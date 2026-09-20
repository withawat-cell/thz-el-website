"""
Download images from the old Google Sites CDN and resize them for the new
static site, so nothing ships at the original (often huge) source resolution.

Usage: python scripts/fetch_images.py manifest.json
manifest.json: list of {"url": ..., "out": "assets/img/....", "max_w": 800, "quality": 82}
"out" is relative to the project root (parent of scripts/).
Logos (out path contains "/logos/") are kept as PNG with transparency preserved
and just downscaled; everything else is saved as JPEG/WEBP depending on extension.
"""
import json
import sys
import os
import urllib.request
from io import BytesIO
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def process(entry):
    url = entry["url"]
    out_rel = entry["out"]
    max_w = entry.get("max_w", 900)
    out_path = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    data = fetch(url)
    im = Image.open(BytesIO(data))

    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, max(1, round(im.height * ratio))), Image.LANCZOS)

    ext = os.path.splitext(out_path)[1].lower()
    if ext == ".png":
        if im.mode not in ("RGBA", "LA"):
            im = im.convert("RGBA")
        im.save(out_path, "PNG", optimize=True)
    else:
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (11, 12, 14))
            im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        im.save(out_path, "JPEG", quality=entry.get("quality", 82), optimize=True, progressive=True)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"OK  {out_rel}  {im.width}x{im.height}  {size_kb:.0f} KB")

def main():
    manifest_path = sys.argv[1]
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    for entry in manifest:
        try:
            process(entry)
        except Exception as e:
            print(f"FAIL {entry['out']}  {entry['url']}  -> {e}")

if __name__ == "__main__":
    main()
