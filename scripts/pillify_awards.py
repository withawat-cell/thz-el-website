import re
import sys

AWARD_KEYWORDS = ["Scholarship", "Fellowship", "Award", "Medal", "Prize", "Commendation",
                   "Grant", "Finalist", "Honorary Mention", "Hackathon"]

def is_award_line(text):
    return any(k in text for k in AWARD_KEYWORDS)

def split_pills(inner_html):
    # split on the middot separator, respecting existing <a> tags (no nested middots inside hrefs)
    parts = re.split(r"\s*&middot;\s*", inner_html)
    return [p.strip() for p in parts if p.strip()]

def process(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'<p class="person-meta">(.*?)</p>', re.S)

    def repl(m):
        inner = m.group(1)
        plain_text = re.sub(r"<[^>]+>", "", inner)
        if not is_award_line(plain_text):
            return m.group(0)
        pills = split_pills(inner)
        spans = "".join(f'<span class="tag tag-award">{p}</span>' for p in pills)
        return f'<div class="tag-row" style="margin:2px 0 8px;">{spans}</div>'

    new_content = pattern.sub(repl, content)
    n = len(pattern.findall(content))
    changed = sum(1 for m in pattern.finditer(content) if is_award_line(re.sub(r"<[^>]+>", "", m.group(1))))
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(path, "- award lines converted:", changed, "/ total person-meta:", n)

for p in sys.argv[1:]:
    process(p)
