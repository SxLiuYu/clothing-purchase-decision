from pathlib import Path
import re
text = Path('设计方案_v3_superpowers.md').read_text(encoding='utf-8')
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
sections = [m.group(2).strip() for m in re.finditer(r'^(#+)\s+(.*?)\s*$', text, re.M)]
missing = [item for item in required if item not in sections]
print('missing_sections=', missing)
for func_name in ['连续拒绝', '明日评分']:
    match = next((line for line in text.splitlines() if func_name in line), None)
    print(func_name, '->', match)
print('0.7', '0.7' in text)
print('同体型', '同体型' in text)
hybrid = Path('设计方案_v3_hybrid.md').read_text(encoding='utf-8')
print('hybrid_decision_domain', '决策服务域' in hybrid or 'Decision Domain' in hybrid)
