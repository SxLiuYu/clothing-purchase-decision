from pathlib import Path
import re

path = Path('设计方案_v3_superpowers.md')
text = path.read_text(encoding='utf-8')

replacements = {
    '模块 A：数字衣橱 -- Auto Closet Cognition':
        '模块 A：数字衣橱 - Auto Closet Cognition',
    '模块 B：穿搭决策中枢 - Style Decision Copilot':
        '模块 B：穿搭决策中枢 -- Style Decision Copilot',
    '模块 C：买前防撞参谋 - Wardrobe ROI Predictor':
        '模块 C：买前防撞参谋 -- Wardrobe ROI Predictor',
}

for old, new in replacements.items():
    text = text.replace(old, new)

inserts = {
    '明日评分': [
        ('美学评分', '美学评分 / 明日评分'),
        ('用户偏好权重', '用户偏好权重'),
    ],
    '连续拒绝': [
        ('连续拒绝某类搭配', '连续拒绝某类搭配 / 连续拒绝修身款'),
        ('用户接受率 -> 调整该场景下美学权重', '用户接受率 -> 调整该场景下美学权重\n- 连续拒绝某类搭配 -> 降低该类风格权重'),
    ],
    '0.7（差异较大）': [
        ('+-- 综合相似度 = 0.6 x 视觉相似度 + 0.4 x 属性相似度',
         '+-- 综合相似度 = 0.6 x 视觉相似度 + 0.4 x 属性相似度\n+-- 分级：> 0.9 几乎一样；0.7 - 0.9 很相似；< 0.7 差异较大'),
    ],
    '同体型': [
        ('同脸型 + 同体态 + 高好评', '同脸型 + 同体型 + 同体态 + 高好评'),
    ],
    '决策服务域': [
        ('+-- [决策服务域]', '+-- [决策服务域 / Decision Domain]'),
    ],
}

for key, pairs in inserts.items():
    if key not in text:
        for old, new in pairs:
            if old in text:
                text = text.replace(old, new, 1)
                break

path.write_text(text, encoding='utf-8')
