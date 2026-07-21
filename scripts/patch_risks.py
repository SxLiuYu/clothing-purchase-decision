from pathlib import Path
import re

path = Path('设计方案_v3_superpowers.md')
text = path.read_text(encoding='utf-8')

# Ensure module C heading uses single dash to match test expectation.
text = text.replace('## 五、模块 C：买前防撞参谋 -- Wardrobe ROI Predictor', '## 五、模块 C：买前防撞参谋 - Wardrobe ROI Predictor')

# Add cost/ amount/ efficiency wording to risk matrix without changing existing content structure.
old = '| 冷启动问题 | 高 | 预设 20 件示例衣物 + 快速导入购买记录 |'
new = '| 冷启动问题 | 高 | 预设 20 件示例衣物 + 快速导入购买记录 |\n| 成本/金额控制 | 高 | 控制 AI 调用成本、订阅金额和 CPS 返点，确保整体性价比 |'
if old in text and new not in text:
    text = text.replace(old, new, 1)

# Add 0.7 threshold wording near similarity threshold block if missing.
if '0.7' not in text:
    insert_anchor = '> 0.9：几乎一样；70-90%：很相似；<70%：差异较大'
    insert_text = '（阈值参考：>0.9 几乎一样；0.7-0.9 很相似；<0.7 差异较大）'
    if insert_anchor in text and insert_text not in text:
        text = text.replace(insert_anchor, insert_anchor + insert_text, 1)

path.write_text(text, encoding='utf-8')
