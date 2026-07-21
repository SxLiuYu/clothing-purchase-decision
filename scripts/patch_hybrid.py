from pathlib import Path
import re

path = Path('设计方案_v3_hybrid.md')
text = path.read_text(encoding='utf-8')

anchor = '### 附录 C：下一步建议'
pos = text.find(anchor)
left = text.index('### 附录 C：下一步建议')
if left != -1:
    insertion = (
        '\n### 商业与成本说明\n'
        '- 商业链路：CPS 分佣 + 高级订阅 + 品牌合作 + 穿搭师服务\n'
        '- 成本重点：AI 推理成本、云服务成本、获客成本\n'
        '- 金额口径：订阅金额、单用户 LTV、ROI 目标\n'
        '- 性价比校验：以 Wardrobe ROI 和复用率为核心依据，减少高价低效推荐\n'
        '- 定价边界：避免低价高频推荐占用算力，优先高价值转化场景\n'
    )
    text = text[:left] + insertion + text[left:]

path.write_text(text, encoding='utf-8')
