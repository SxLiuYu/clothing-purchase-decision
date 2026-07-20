# Superpowers 修复方案实施计划

> 文档版本：v1.0 | 更新日期：2026-07-20
> 目标：基于评估报告实现所有 Superpower 能力修复

---

## 修复范围

根据 superpowers评估报告_v3.md，需要修复以下差距：

### SP1：穿搭决策中枢
- ❌ 多目标优化（美学/复用/场景）→ 当前仅示例数据
- ❌ 真实衣橱候选生成 → 硬编码 items 列表

### SP2：动态体态档案
- ❌ 连续 3 次拒绝 → 全局权重下降
- ❌ 体重变化 > 5% → 档案重新校准

### SP3：Wardrobe ROI
- ❌ 真实组合缺口图计算 → 简化公式
- ❌ 场景覆盖真实变化 → 公式估算

---

## 实施步骤

### Phase 1: Superpower 2 修复（P0）
1. 实现 ContinuousFeedbackAnalyzer 类
2. 添加全局偏好权重动态调整
3. 实现体重变化检测

### Phase 2: Superpower 3 修复（P0）
1. 实现真实衣橱图谱组合计算
2. 添加场景覆盖度计算
3. 优化 ROI 评分公式

### Phase 3: Superpower 1 修复（P1）
1. 实现多目标优化算法
2. 替换硬编码候选为真实衣橱查询
3. 添加可解释性生成

### Phase 4: 测试验证（P1）
1. 添加功能测试用例
2. 验证所有修复点

---

## 技术方案

### 1. 连续反馈模式识别

`python
class ContinuousFeedbackAnalyzer:
    - 检测连续拒绝模式（默认阈值：3次）
    - 动态调整全局偏好权重
    - 触发体态档案重新校准
`

### 2. 真实组合缺口计算

`python
class CombinationGapCalculator:
    - 基于衣橱图谱计算新衣激活组合
    - 评估场景覆盖度变化
    - 生成替代方案建议
`

### 3. 多目标优化

`python
class MultiObjectiveOptimizer:
    - 美学评分优化
    - 衣橱复用率优化
    - 场景覆盖率优化
    - Pareto 前沿求解
`

---

## 预期成果

| Superpower | 修复后达标率 |
|------------|------------|
| SP1 | 75% → 85% |
| SP2 | 60% → 80% |
| SP3 | 70% → 85% |

---
