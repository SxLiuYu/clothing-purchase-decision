# 智能衣橱 + AI 搭配师 — 项目梳理

> 生成时间：2026-07-21
> 超级能力 skill 已安装完毕（obra/superpowers 系列 14 个 skill）
> GitHub: https://github.com/SxLiuYu/clothing-purchase-decision

---

## 一、项目结构

```
clothing-purchase-decision/
├── .agnes/                          # 工作区记忆（对话/偏好记录）
│   └── memories/records.jsonl
│
├── src/
│   └── app/
│       ├── __init__.py              # 新增：包初始化
│       ├── main.py                  # FastAPI 入口（4 路由组）
│       ├── models/
│       │   └── schemas.py           # Pydantic 数据模型（7 个模型）
│       ├── routes/
│       │   ├── wardrobe.py          # 衣橱 CRUD（3 个接口）
│       │   ├── outfits.py           # 穿搭决策中枢（1 个核心接口）
│       │   ├── roi.py               # 买前 ROI 分析（1 个接口）
│       │   └── body.py              # 体态反馈（1 个接口）
│       └── services/
│           ├── store.py             # 内存数据存储（MemoryStore）
│           ├── combination_calculator.py   # 新增：组合缺口计算器
│           ├── feedback_analyzer.py        # 新增：连续反馈分析器
│           └── multi_objective_optimizer.py # 新增：多目标优化器
│
├── tests/
│   ├── conftest.py                  # 路径注入
│   ├── test_api.py                  # API 集成测试（7 条链路）
│   ├── test_design_spec.py          # 设计文档规范测试（39 项）
│   ├── test_design_functional.py    # 设计文档功能完整性测试（41 项）
│   └── test_superpower_fixes.py     # 新增：Superpower 修复验证（15 项）
│
├── docs/                            # 设计文档与记录（已归类）
│   ├── design/                      # 设计方案 v1/v2/v3 + 用户测试
│   │   ├── 设计方案.md
│   │   ├── 设计方案_v2.md
│   │   ├── 设计方案_v3_superpowers.md
│   │   ├── 设计方案_v3_superpowers_bak.md
│   │   ├── 设计方案_v3_hybrid.md
│   │   └── v3_superpower_user_tests.md
│   ├── superpowers/                 # 超级能力评估/优化/修复
│   │   ├── superpowers_brainstorm.md
│   │   ├── superpowers评估报告.md / _v2 / _v3
│   │   ├── superpowers优化方案.md
│   │   └── superpowers修复方案.md
│   └── notes/                       # 会话记录
│       ├── 历史会话记录.md
│       └── 会话内容完整记录.md
├── pyproject.toml                    # 项目元数据
├── requirements.txt                  # 依赖清单
├── run.py                            # 启动脚本
└── README.md                         # 快速开始
```

---

## 二、需求全景（从设计方案提取）

### 四大模块

| 模块 | 名称 | 核心功能 | 当前实现状态 |
|------|------|---------|------------|
| **A** | 数字衣橱 (Auto Closet Cognition) | 拍照录入、AI 打标、记忆补全、衣橱浏览、关系图谱 | ✅ 基础 CRUD + 关系管理 |
| **B** | 穿搭决策中枢 (Style Decision Copilot) | 硬约束过滤、多目标优化、可解释决策、3 套方案输出 | ✅ 硬约束规则（4 条）+ 多目标优化器 |
| **C** | 买前 ROI (Wardrobe ROI Predictor) | 相似度检测、组合缺口计算、旧衣激活、场景覆盖 | ✅ ROI 计算 + 组合缺口计算器 |
| **D** | 社媒推荐 (Social Media) | 脸型体型匹配、社媒爬取、单品推荐、购买跳转 | ❌ 未实现（仅文档） |

### 三大超级能力（v3.0 核心）

| 超级能力 | 描述 | 实现状态 |
|---------|------|---------|
| **穿搭决策中枢** | 基于天气/行程/体型/衣橱存量/穿着历史，推演可执行穿搭决策链 | ✅ 硬约束规则 + 多目标优化器 + Pareto 最优 |
| **动态体态档案** | 通过穿着反馈持续更新体态偏好，检测连续拒绝模式 | ✅ 反馈接口 + 连续反馈分析器 + 体重变化检测 |
| **Wardrobe ROI** | 计算新衣的组合增量 + 旧衣激活 + 场景覆盖率 | ✅ ROI 计算 + 组合缺口计算器 + 场景覆盖分析 |

### Hybrid 架构（v3.1 扩展）

| 端 | 定位 | 实现状态 |
|---|------|---------|
| App（主阵地） | 完整超级能力、本地推理、离线缓存 | ⚠️ 仅后端 API，无前端 |
| 小程序（增长引擎） | 轻量入口、传播分享 | ❌ 未开始 |
| 穿搭师助手（专业端） | 查看衣橱、提交方案 | ❌ 未开始 |

---

## 三、功能实现详情

### 3.1 已实现接口（7 个）

| 方法 | 路径 | 功能 | 文件 |
|------|------|------|------|
| `GET` | `/health` | 健康检查 | `main.py` |
| `POST` | `/api/v3/wardrobe/items` | 添加衣物 | `wardrobe.py` |
| `GET` | `/api/v3/wardrobe/users/{user_id}/items` | 列出用户衣物 | `wardrobe.py` |
| `POST` | `/api/v3/wardrobe/relationships` | 添加衣物关系 | `wardrobe.py` |
| `POST` | `/api/v3/decisions/outfit` | 穿搭推荐决策 | `outfits.py` |
| `POST` | `/api/v3/shop/roi-analysis` | 买前 ROI 分析 | `roi.py` |
| `POST` | `/api/v3/body/feedback` | 体态反馈 | `body.py` |

### 3.2 穿搭决策规则（4 条硬约束）

| 规则 ID | 名称 | 触发条件 | 惩罚 |
|---------|------|---------|------|
| HC001 | 天冷必须穿保暖层 | 温度 < 10°C | -12 |
| HC002 | 正式场合排除运动鞋/短裤/卫衣 | 场合 = formal | -18 |
| HC003 | 雨天排除帆布鞋 | 天气 = rain/heavy rain | -15 |
| HC004 | 炎热正式场合选透气面料 | 温度 ≥ 35°C + formal | +6 |

### 3.3 多目标优化器（Multi-Objective Optimizer）

| 目标 | 权重 | 阈值 | 描述 |
|------|------|------|------|
| 美学评分 | 0.30 | ≥85 | 颜色和谐、风格一致 |
| 衣橱复用率 | 0.25 | ≥0.7 | 优先使用已有单品 |
| 场景覆盖率 | 0.25 | ≥0.8 | 满足场合需求 |
| 身体适配度 | 0.20 | ≥0.9 | 版型与体型匹配 |

**Pareto 最优**：输出不被其他方案支配的最优解

### 3.4 连续反馈分析器（Continuous Feedback Analyzer）

| 功能 | 阈值 | 动作 |
|------|------|------|
| 连续拒绝检测 | 3 次 | 触发全局权重衰减 |
| 权重衰减步长 | 0.15 | 降低对应版型偏好权重 |
| 体重变化检测 | 5% | 触发体态档案重新校准 |

### 3.5 组合缺口计算器（CombinationGapCalculator）

| 权重 | 描述 |
|------|------|
| 组合增量 | 0.40 | 新衣可搭配的组合数 |
| 旧衣激活率 | 0.25 | 激活闲置衣物的比例 |
| 场景覆盖 | 0.20 | 填补场景缺口的程度 |
| 价格效用 | 0.15 | 价格与价值的比例 |

**场景定义**：formal, casual, sport, outdoor, date, daily

### 3.6 ROI 计算逻辑

```
ROI Score = 50 + candidate_score × 35 + activation_count × 2.5 + scenario_delta × 20
→ ≥ 72 推荐购买，否则建议重新考虑
```

### 3.7 数据模型（7 个 Pydantic Schema）

- `Item` — 衣物实体
- `Relationship` — 衣物关系（搭配/同场景/同色系/替代）
- `OutfitRequest` — 穿搭请求（天气/场合/时长/约束）
- `OutfitPlan` — 单套搭配方案（含风险/替代/切换选项）
- `OutfitResponse` — 决策响应（含置信度）
- `ROIRequest` — ROI 分析请求
- `ROIResponse` — ROI 报告（含相似度/缺口/冲突/建议）
- `BodyFeedbackRequest` — 体态反馈请求
- `UpdatedProfile` — 更新后的体态档案

---

## 四、测试覆盖（101 项测试全部通过 ✅）

| 测试文件 | 测试类 | 数量 | 覆盖内容 |
|---------|-------|------|---------|
| `test_api.py` | 7 个函数 | 7 | API 集成链路（衣橱→决策→ROI→反馈→极端场景→冷启动） |
| `test_design_spec.py` | 5 个类 | 39 | 设计文档结构/关键词/完整性 |
| `test_design_functional.py` | 7 个类 | 41 | 功能模块完整性/文档结构/场景覆盖 |
| `test_superpower_fixes.py` | 5 个类 | 15 | Superpower 修复验证（连续反馈/组合计算/多目标优化/集成测试） |

### 新增测试用例（test_api.py）

| 测试 | 描述 |
|------|------|
| `test_extreme_hot_formal_meeting` | 极端炎热 + 正式会议场景 |
| `test_cold_start_wardrobe_keeps_output` | 冷启动场景：极简衣橱仍输出推荐 |
| `test_feedback_affects_body_profile_twice` | 反馈两次影响体态档案 |

### 新增测试用例（test_superpower_fixes.py）

| 测试类 | 测试内容 |
|--------|---------|
| `TestSuperpower2ContinuousFeedback` | 连续拒绝检测、全局权重衰减、体重变化检测、档案重新校准 |
| `TestSuperpower3CombinationCalculator` | 组合增量计算、场景覆盖分析、替代方案生成 |
| `TestSuperpower1MultiObjectiveOptimization` | 优化器初始化、穿搭优化、权重调整、Pareto 最优 |
| `TestIntegration` | 完整反馈闭环、Wardrobe ROI 集成 |

---

## 五、技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.14 | 运行环境 |
| FastAPI | ≥0.100 | API 框架 |
| Pydantic | ≥2.0 | 数据模型/校验 |
| Uvicorn | latest | ASGI 服务器 |
| pytest | ≥9.0 | 测试框架 |
| markdown | latest | 文档解析测试 |
| beautifulsoup4 | latest | HTML 解析测试 |

---

## 六、已知待办项

### 短期（代码层面）
1. 修复 `pydantic.dict()` → `model_dump()` 弃用警告（多处）
2. 修复 `datetime.utcnow()` → `datetime.now(datetime.UTC)` 弃用警告（多处）
3. 模块 D（社媒推荐）的功能实现
4. 内存存储 → 持久化数据库（PostgreSQL/Redis）
5. 新增接口的集成测试覆盖

### 中期（产品层面）
6. 前端 App/小程序 开发
7. 穿搭师助手端
8. 社媒数据爬取与 AI 分析
9. CPS 购买跳转集成
10. 冷启动体验优化（内置示例衣橱）

### 长期（超级能力增强）
11. 端侧 AI 推理引擎
12. 离线缓存策略
13. 多端数据同步
14. 成本控制与商业化分层

---

## 七、已安装的 Superpowers Skills

| Skill | 用途 |
|-------|------|
| `brainstorming` | 设计方案脑暴 |
| `systematic-debugging` | 系统化调试 |
| `writing-plans` | 编写实施计划 |
| `using-superpowers` | 使用超级能力方法论 |
| `test-driven-development` | TDD 开发 |
| `requesting-code-review` | 请求代码审查 |
| `receiving-code-review` | 接收代码审查 |
| `executing-plans` | 执行计划 |
| `dispatching-parallel-agents` | 并行任务分发 |
| `subagent-driven-development` | 子代理驱动开发 |
| `verification-before-completion` | 完成前验证 |
| `finishing-a-development-branch` | 完成开发分支 |
| `using-git-worktrees` | Git Worktree 操作 |
| `writing-skills` | 自定义 skill 编写 |

---

## 八、Git 状态

```
分支：SxLiuYu/main（本地） <-> origin/main（远程）
最新提交：7d09a81 feat: implement superpower fixes
本地未提交：requirements.txt 修改、PROJECT_OVERVIEW.md 新增
```

---

## 九、核心服务类说明

### 9.1 CombinationGapCalculator（组合缺口计算器）

```python
from src.app.services.combination_calculator import CombinationGapCalculator

calculator = CombinationGapCalculator()

# 计算新衣物的组合增量
result = calculator.calculate_combination_increment(
    new_item={'category': 'blazer', 'color': 'navy'},
    wardrobe_items=[...],
    existing_combinations=[...]
)

# 计算场景覆盖变化
coverage = calculator.calculate_scenario_coverage(...)
```

### 9.2 ContinuousFeedbackAnalyzer（连续反馈分析器）

```python
from src.app.services.feedback_analyzer import ContinuousFeedbackAnalyzer

analyzer = ContinuousFeedbackAnalyzer()

# 分析连续拒绝
result = analyzer.analyze_consecutive_rejections(
    user_id='user_001',
    feedback_records=[...]
)

# 检测体重变化
needs_recal, ratio = analyzer.check_weight_change(85, 80, 0.05)

# 应用全局权重衰减
result = analyzer.apply_global_weight_decay(user_id, current_weights)
```

### 9.3 MultiObjectiveOptimizer（多目标优化器）

```python
from src.app.services.multi_objective_optimizer import (
    MultiObjectiveOptimizer,
    ObjectiveType
)

optimizer = MultiObjectiveOptimizer()

# 优化穿搭方案
result = optimizer.optimize(
    candidates=[...],
    constraints={...},
    preferences={...}
)

# 调整权重
optimizer.adjust_weights(ObjectiveType.BODY_FIT, 0.30)
```

---

*文档版本：v2.0 | 更新时间：2026-07-21*