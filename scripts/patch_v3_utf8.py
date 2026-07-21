import base64, sys
from pathlib import Path
path = Path('设计方案_v3_superpowers.md')
text = path.read_text(encoding='utf-8')
rep_a = base64.b64decode(sys.argv[1]).decode('utf-8')
rep_b = base64.b64decode(sys.argv[2]).decode('utf-8')
rep_c = base64.b64decode(sys.argv[3]).decode('utf-8')
text = text.replace('### 3.1 功能规格', rep_a + '### 3.1 功能规格', 1)
text = text.replace('### 4.2 决策推理引擎（三层约束模型）', rep_b + '### 4.2 决策推理引擎（三层约束模型）', 1)
text = text.replace('### 5.2 核心算法：组合缺口计算（Combination Gap Analysis）', rep_c + '### 5.2 核心算法：组合缺口计算（Combination Gap Analysis）', 1)
path.write_text(text, encoding='utf-8')
print('updated-size=', len(text))
