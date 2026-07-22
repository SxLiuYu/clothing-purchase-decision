# 技术债务修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复代码中的 4 项技术债务：pydantic.dict() 弃用、datetime.utcnow() 弃用、fit_preference 字段名不一致、outfits.py 硬编码示例候选

**Architecture:** 直接修改现有代码，不改变核心逻辑，保持 101 项测试全部通过

**Tech Stack:** Python 3.14, Pydantic v2, FastAPI

## Global Constraints

- 所有原有测试必须保持通过
- 不改动核心业务逻辑
- 每次修改后立即运行测试验证

---

### Task 1: 修复 `item.dict()` → `model_dump()`（5 处）

**Files:**
- Modify: `src/app/services/store.py:28,34`
- Modify: `src/app/routes/outfits.py:179`
- Modify: `src/app/routes/roi.py:40`
- Modify: `src/app/routes/body.py:10,13`

**Interfaces:**
- 不变：仅替换弃用 API，函数签名和返回值不变

- [ ] **Step 1: 修复 store.py 中 2 处 `item.dict()` 和 `relationship.dict()`**

修改 `store.py:28` 和 `store.py:34`：
```python
# 第 28 行
record = item.model_dump()
# 第 34 行
record = relationship.model_dump()
```

- [ ] **Step 2: 修复 outfits.py 中 `payload.dict()`**

修改 `outfits.py:179`：
```python
"request": payload.model_dump(),
```

- [ ] **Step 3: 修复 roi.py 中 `payload.dict()`**

修改 `roi.py:40`：
```python
'request': payload.model_dump(),
```

- [ ] **Step 4: 修复 body.py 中 2 处 `payload.dict()` 和 `UpdatedProfile(**updated).dict()`**

修改 `body.py:10,13`：
```python
# 第 10 行
updated = store.apply_feedback(payload.user_id, payload.model_dump())
# 第 13 行
'updated_profile': UpdatedProfile(**updated).model_dump(),
```

- [ ] **Step 5: 运行测试验证**

Run: `python -m pytest -q`
Expected: `101 passed`，弃用警告从 16 个减少到 11 个

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "fix: 修复 pydantic.dict() 弃用警告，改为 model_dump()"
```

---

### Task 2: 修复 `datetime.utcnow()` → `datetime.now(datetime.UTC)`

**Files:**
- Modify: `src/app/services/store.py:41,50`

**Interfaces:**
- 不变：输出字符串格式不变（ISO 8601 + 'Z'）

- [ ] **Step 1: 修复 store.py 中 2 处 `datetime.utcnow()`**

修改 `store.py:41,50`：
```python
# 第 41 行
'generated_at': datetime.now(datetime.UTC).isoformat() + 'Z',
# 第 50 行
'generated_at': datetime.now(datetime.UTC).isoformat() + 'Z',
```

同时需要在文件顶部添加 import：
```python
from datetime import datetime, timezone
```
将现有的 `from datetime import datetime` 改为 `from datetime import datetime, timezone`

- [ ] **Step 2: 运行测试验证**

Run: `python -m pytest -q`
Expected: `101 passed`，弃用警告从 11 个减少到 9 个

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "fix: 修复 datetime.utcnow() 弃用警告，改为 datetime.now(datetime.UTC)"
```

---

### Task 3: 统一 `fit_preference` 字段名

**Files:**
- Modify: `src/app/services/store.py:60,67`（用 `fit_preference`）
- Modify: `src/app/services/feedback_analyzer.py:82,204,243,268,276`（用 `fit_preferences`）
- Modify: `src/app/services/multi_objective_optimizer.py:205,219`（用 `fit_preferences`）
- Modify: `tests/test_superpower_fixes.py:59`（用 `fit_preferences`）
- Modify: `tests/test_api.py:153`（用 `fit_preference`）

**决策：** 统一使用 `fit_preference`（Pydantic Schema 中定义的字段名 `schemas.py:88: fit_preference`）

- [ ] **Step 1: 修复 feedback_analyzer.py 中 5 处 `fit_preferences` → `fit_preference`**

修改 `feedback_analyzer.py`：
- 第 82 行：`.get('fit_preferences', {})` → `.get('fit_preference', {})`
- 第 204 行：`body_profile.get('fit_preferences')` → `body_profile.get('fit_preference')`
- 第 243 行：`body_profile.get('fit_preferences', {})` → `body_profile.get('fit_preference', {})`
- 第 268 行：`'fit_preferences': fit_preferences` → `'fit_preference': fit_preferences`
- 第 276 行：`'fit_preferences': fit_preferences` → `'fit_preference': fit_preferences`

- [ ] **Step 2: 修复 multi_objective_optimizer.py 中 2 处 `fit_preferences` → `fit_preference`**

修改 `multi_objective_optimizer.py`：
- 第 205 行：`fit_preferences = user_profile.get('fit_preferences', {})` → `fit_preferences = user_profile.get('fit_preference', {})`
- 第 219 行：不变（只是变量名，不影响）

- [ ] **Step 3: 修复 test_superpower_fixes.py 中 `fit_preferences` → `fit_preference`**

修改 `test_superpower_fixes.py:59`：
```python
'fit_preference': {'waist': 'slim'}
```

- [ ] **Step 4: 修复 test_api.py 中 `fit_preference` 验证（已正确，无需修改）**

确认 `test_api.py:153` 的断言正确：
```python
assert 'comfortable' in second['updated_profile']['fit_preference'].values()
```

- [ ] **Step 5: 运行测试验证**

Run: `python -m pytest -q`
Expected: `101 passed`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "fix: 统一 fit_preference 字段名（Pydantic Schema 定义为准）"
```

---

### Task 4: 将 outfits.py 从硬编码示例候选改为动态生成

**Files:**
- Modify: `src/app/routes/outfits.py`
- Modify: `tests/test_api.py`（新增测试）

**Interfaces:**
- 不变：`POST /api/v3/decisions/outfit` 输入输出格式不变
- 新增依赖：调用 `MultiObjectiveOptimizer` 排序候选

- [ ] **Step 1: 从衣橱图谱中动态生成候选方案**

修改 `_build_example_candidates()` 函数，改为从 `store` 读取用户衣橱并生成候选：

```python
def _build_candidates_from_wardrobe(active_rules, weather, constraints, top_rank, user_id):
    user = store.get_or_create_user(user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])
    
    if not nodes:
        # 冷启动：返回默认示例
        return _build_default_candidates(active_rules, weather, constraints, top_rank)
    
    candidates = []
    for node in nodes:
        attrs = node.get('attributes', {})
        category = attrs.get('category', '')
        category_score, _ = _category_hard_score(category, active_rules)
        score = min(92, 70 + category_score * 0.3)
        score = max(score, 10)
        
        candidates.append({
            "rank": 0,
            "score": round(score, 1),
            "confidence": max(round(min(0.95, score / 100 + 0.12), 2), 0.45),
            "items": [{
                "item_id": node.get('item_id'),
                "category": category,
                "name": node.get('item_id', 'unknown'),
                "rationale": f"硬约束检查通过，{category} 适配当前场景",
                "risk_flags": [],
                "score": round(score, 1),
            }],
            "rationale": "基于衣橱图谱动态生成",
            "risk_flags": [],
            "alternatives": {},
            "switch_options": [],
        })
    
    # 排序
    candidates.sort(key=lambda c: (-c['score'], -c['confidence']))
    for rank, c in enumerate(candidates, 1):
        c['rank'] = rank
    
    return candidates[:max(1, top_rank)]
```

- [ ] **Step 2: 更新 `recommend_outfit` 路由调用新函数**

```python
@router.post("/outfit", response_model=OutfitResponse)
def recommend_outfit(payload: OutfitRequest):
    active_rules = _evaluate_hard_constraints(payload)
    candidates = _build_candidates_from_wardrobe(
        active_rules, _parse_weather(payload), 
        payload.constraints or {}, top_rank=3, 
        user_id=payload.user_id
    )
    # ... 其余不变
```

- [ ] **Step 3: 运行测试验证**

Run: `python -m pytest -q`
Expected: `101 passed`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: outfits.py 从硬编码示例改为从衣橱图谱动态生成候选"
```