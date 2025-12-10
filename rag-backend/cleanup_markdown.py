import os
from pathlib import Path
import re

# Path to Docusaurus docs folder
ROOT = Path("../docs/AI_USAGE_IN_DAILY_LIFE")

for md_file in ROOT.rglob("*.md*"):
    with open(md_file, "r+", encoding="utf-8") as f:
        content = f.read()
        # Remove leading '('\n' and trailing '\n) > ...'
        cleaned_content = re.sub(r'^\(\n', '', content)
        cleaned_content = re.sub(r'\n\) > .*?$', '', cleaned_content)
        # Remove 'echo ' from the beginning of each line
        cleaned_content = re.sub(r'^echo\.', '', cleaned_content, flags=re.MULTILINE)
        f.seek(0)
        f.write(cleaned_content)
        f.truncate()

print("Markdown files cleaned up!")
