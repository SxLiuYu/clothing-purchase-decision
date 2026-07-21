from pathlib import Path
import markdown
from bs4 import BeautifulSoup
text = Path('设计方案_v3_superpowers.md').read_text(encoding='utf-8')
html = markdown.markdown(text)
soup = BeautifulSoup(html, 'html.parser')
headings = [tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
for h in headings:
    if '模块 C' in h or '买前防撞' in h:
        print(repr(h))
print('count', len(headings))
