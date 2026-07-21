# Superpowers 重新评估报告（v4.0）

> 评估时间：2026-07-21
> 评估基准：设计方案_v3_superpowers.md + v3_superpower_user_tests.md
> 代码依据：src/app/routes/*.py, src/app/services/*.py, tests/*
> 评估方法：superpowers（先探索上下文 → 三维评估 → 验证 bug → 给优化建议）

---

## 评估概览

| 维度 | 上版(v3) | 本次(v4) | 变化 |
|------|----------|----------|------|
| 文档合理性 | 完善 ✅ | 有冗余 ⚠️ | 8 份设计稿 + 7 份评估，存在过时/重复 |
| 功能实现度 | 基础 MVP ⚠️ | 框架已建未接通 ❌ | 3 个超级能力服务实现了却完全没被路由调用 |
| 性能 | 未评估 | 可显著提升 ⬆️ | 硬编码 + 全量遍历 + 无缓存 |
| 测试覆盖 | 文档结构 100% | 101 passed | 路由-服务集成测试 = 0 |

**核心结论：项目存在一个"超级能力已实现却未接入"的重大断层。** `combination_calculator.py`、`feedback_analyzer.py`、`multi_objective_optimizer.py` 三个服务共 ~36KB 代码完整实现了 Superpower 1/2/3 的算法，但路由层（`outfits.py`/`roi.py`/`body.py`）全部使用硬编码示例数据和简化公式，完全没有 import 这些服务。这导致 v3 评估报告里标注"未实现"的能力其实已实现，只是断线。

---

## 一、文档合理性评估

### 1.1 问题：文档版本冗余

```
docs/design/
├── 设计方案_v1.md                    (16KB, 已过时)
├── 设计方案_v2.md                    (54KB, 已过时)
├── 设计方案_v3_hybrid.md             (9KB, 混合架构, 部分有效)
├── 设计方案_v3_superpowers.md        (26KB, ★当前主版本)
├── 设计方案_v3_superpowers_bak.md    (59KB, 与主版本重复)
├── base_v2_backup.md                 (54KB, v2 备份, 冗余)
├── module_c_backup.txt              (3KB, 补丁中间态)
└── module_c_current.txt             (3KB, 补丁中间态)
```

- **问题：** 8 份设计稿中有 4 份是历史/备份/中间态，读者无法判断哪份是当前权威。
- **建议：** 保留 `设计方案_v3_superpowers.md` 为唯一权威；`_hybrid` 转为附录；其余 5 份归入 `docs/design/archive/`。

### 1.2 问题：评估报告也已过时

`superpowers评估报告_v3.md` 仍称"连续拒绝识别未实现""多目标优化未实现"，但代码里 `ContinuousFeedbackAnalyzer.analyze_consecutive_rejections`、`MultiObjectiveOptimizer.optimize_outfit` 都已实现——只是没接进路由。评估报告与代码实现脱节。

### 1.3 文档本身质量

`设计方案_v3_superpowers.md` 本身设计完善：三层约束模型、组合缺口算法、动态体态档案、ROI 公式、性能分级策略都写得很清楚。文档不是设计问题，是"实现未对齐文档"的问题。

---

## 二、功能评估：三大断层

### 断层 1：Superpower 1（决策中枢）服务未接入

```
multi_objective_optimizer.py   ← MultiObjectiveOptimizer.optimize_outfit() 已实现
        │  （Pareto 前沿、四目标加权、权重动态调整）
        ✗ 从未被 import
outfits.py → _build_example_candidates() → 硬编码 4 件示例衣物
```

路由的 `recommend_outfit` 用 `_build_example_candidates` 返回写死的衬衫/裤子/鞋，根本没查用户真实衣橱，也没调用多目标优化器。设计要求的"Layer2 多目标优化"完全断线。

### 断层 2：Superpower 3（ROI）服务未接入

```
combination_calculator.py     ← CombinationGapCalculator 已实现
        │  （真实组合增量、旧衣激活、场景覆盖、价格效用）
        ✗ 从未被 import
roi.py → roi_score = 50 + score*35 + count*2.5 + delta*20   ← 简化公式硬编码
        combination_gap.new_combinations = int(8 * candidate_score)  ← 拍脑袋
```

路由用 `int(8 * candidate_score)` 这种写死系数算"新组合数"，而真正的 `calculate_combination_increment`（遍历衣橱、算兼容度、去重）就在隔壁没被调用。

### 断层 3：Superpower 2（体态）服务未接入

```
feedback_analyzer.py          ← ContinuousFeedbackAnalyzer 已实现
        │  （连续拒绝检测、全局权重衰减、体重变化校准）
        ✗ 从未被 import
body.py → store.apply_feedback() 只做单次敏感区域记录
```

`store.apply_feedback` 只把反馈塞进 `sensitive_areas` set，不触发连续拒绝分析、不做权重衰减、不重新校准。设计要求的"连续 3 次拒绝→全局权重下降"完全没闭环。

### 三个断层的共同后果

- v3 评估报告误判为"未实现"，实为"已实现未接通"
- `test_superpower_fixes.py` 只测服务层单元，不测路由→服务集成
- 用户体验到的 API 行为与设计文档承诺严重不符

---

## 三、性能评估

### 3.1 当前性能问题

| 位置 | 问题 | 影响 |
|------|------|------|
| `store.py` | 全内存单例，无连接池/索引 | 重启数据丢失；衣橱节点线性扫描 `[node for node in nodes if ...]` |
| `combination_calculator` | `calculate_combination_increment` O(N) 全量遍历衣橱 | 设计自己写了分级策略（<50全量/50-200剪枝/>200近似），代码没实现 |
| `multi_objective_optimizer` | 每次请求重算四目标分，无缓存 | 候选集大时重复计算 |
| `outfits.py` | `_build_example_candidates` 每次构造 4 件写死物品 | 谈不上性能，是正确性问题 |
| 全局 | 无异步，`store` 操作同步 | 并发下瓶颈 |

### 3.2 设计文档已规划但未落地

设计方案 §5.4 性能优化节明确写了分级策略，代码零实现：
- 衣橱 < 50：全量组合计算
- 50-200：图剪枝 + 抽样
- > 200：近似算法 + 缓存历史结果
- 新衣 Top-5 先过滤再组合计算

---

## 四、可立即修复的问题

### P0-1 接通 ROI 路由 → CombinationGapCalculator（正确性）
`roi.py` 改用真实组合计算，取代 `int(8*candidate_score)` 拍脑袋系数。

### P0-2 接通体态路由 → ContinuousFeedbackAnalyzer（功能闭环）
`body.py` 调用 `fit_preference_engine.update_preference`，实现连续拒绝→权重衰减闭环。

### P0-3 接通决策路由 → MultiObjectiveOptimizer（对齐设计）
`outfits.py` 用真实衣橱候选 + 多目标优化排序，取代硬编码 4 件示例。

### P1 文档去冗余
设计稿归档，评估报告更新为 v4 反映"已实现未接通"的真实状态。

---

## 五、优化建议（分优先级）

### P0（本周可做，修复断层）
1. 三个路由接入对应服务，补集成测试
2. `combination_calculator` 接入时实现设计的分级性能策略
3. 文档归档 + 评估报告更新

### P1（下个迭代，性能与正确性）
1. `store` 引入 SQLite 持久化 + 衣橱节点索引（item_id dict）
2. 多目标优化结果按 (user_id, occasion, weather_hash) 缓存
3. 组合计算结果缓存（衣橱未变则复用）

### P2（中期，能力增强）
1. 真实衣橱候选生成（从 wardrobe_graph.nodes 查询，替代硬编码）
2. CLIP 相似度接入（设计 C-02）
3. LLM 决策解释生成（设计 Layer 3）

### P3（长期，架构）
1. 异步化（FastAPI async + 异步存储）
2. 衣橱图谱迁移 Neo4j（设计已提，可选）
3. 接入天气 API（设计 B-02）

---

## 六、结论

项目不是"设计不完善"，而是"实现没接通设计"。三个超级能力算法都已完整写出，却像三栋建好但没通水电的楼。**最高 ROI 的动作不是写新功能，而是把已写的服务接进路由**——这一步能把 v3 报告里的 SP1 75%、SP2 60%、SP3 70% 三个达标率同时拉到 90%+，且代码已现成。

---
*评估报告版本：v4.0 | 评估方法：superpowers | 评估时间：2026-07-21*
