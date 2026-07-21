from pathlib import Path
import re
text = Path('设计方案_v3_superpowers.md').read_text(encoding='utf-8')
pattern = re.compile(r'^\s*#+\s+(.*?)\s*$', re.M)
sections = [m.group(1).strip() for m in pattern.finditer(text)]
print('count', len(sections))
for sec in sections[:25]:
    print(sec)
required = [
    '产品定位与超级能力',
    '产品架构总览',
    '模块 A：数字衣橱 - Auto Closet Cognition',
    '模块 B：穿搭决策中枢 -- Style Decision Copilot',
    '模块 C：买前防撞参谋 -- Wardrobe ROI Predictor',
    '模块 D：脸型体型 + 社媒推荐',
    '数据流与状态机设计',
    'API 接口设计',
    '数据模型设计',
    '技术实现方案',
    '实施路线图',
    '风险矩阵与应对策略',
    '附录',
]
missing = [item for item in required if item not in sections]
print('missing', missing)
