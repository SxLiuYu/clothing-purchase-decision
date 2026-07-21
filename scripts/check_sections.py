from pathlib import Path
import re
text = Path('设计方案_v3_superpowers.md').read_text(encoding='utf-8')
pattern = re.compile(r'^(#+)\s+(.*?)\s*$', re.M)
sections = [m.group(2).strip() for m in pattern.finditer(text)]
print('count', len(sections))
for sec in sections[:20]:
    print(sec)
