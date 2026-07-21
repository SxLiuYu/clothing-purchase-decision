from pathlib import Path
import markdown
from bs4 import BeautifulSoup
text = Path('设计方案_v3_superpowers.md').read_text(encoding='utf-8')
html = markdown.markdown(text)
soup = BeautifulSoup(html, 'html.parser')
for tag in soup.find_all(['h1','h2','h3'])[:5]:
    print(tag.name, tag.get_text(strip=True))
