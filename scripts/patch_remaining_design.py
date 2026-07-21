from pathlib import Path
import re

def insert_after(text, anchor, addition):
    pos = text.find(anchor)
    if pos == -1:
        return text
    insert = text[pos:pos+len(anchor)] + addition
    return text[:pos] + insert + text[pos+len(anchor):]

def replace_text(text, old, new):
    if old in text:
        text = text.replace(old, new)
    return text

path = Path('设计方案_v3_superpowers.md')
text = path.read_text(encoding='utf-8')

text = insert_after(text, '决策反馈学习', '；支持连续拒绝/修正反馈，降低同类风格权重，更新体态/偏好档案')
text = insert_after(text, '更新体态/偏好档案', '；记录用户接受率并持续反哺模型')
text = replace_text(text, '降低该类风格权重', '连续拒绝某类搭配/风格时，降低该类风格权重')

path.write_text(text, encoding='utf-8')

hybrid = Path('设计方案_v3_hybrid.md').read_text(encoding='utf-8')
if '决策服务域' not in hybrid and 'Decision Domain' not in hybrid:
    for anchor in ['+-- [购物服务域]', '-- [购物服务域]']:
        if anchor in hybrid:
            repl = anchor.replace('购物服务域', '决策服务域 / Decision Domain')
            hybrid = hybrid.replace(anchor, repl, 1)
            break
Path('设计方案_v3_hybrid.md').write_text(hybrid, encoding='utf-8')