import os, json, re
from pathlib import Path

# Path to Docusaurus docs folder
ROOT = Path("../docs/AI_USAGE_IN_DAILY_LIFE")  # adjust if your docs folder is somewhere else

out = []

def read_md(file):
    text = file.read_text(encoding="utf-8")
    # Remove YAML front matter
    text = re.sub(r'^---[\s\S]*?---\n', '', text)
    return text

for md in ROOT.rglob("*.md*"):
    out.append({
        "path": str(md),
        "text": read_md(md)
    })

# Write content.json
with open("content.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("content.json created!")
