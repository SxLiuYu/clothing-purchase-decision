# 打通体态档案 → 决策链路 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 新增体态数据录入接口，体态反馈影响穿搭评分，多目标优化权重对齐设计文档

**Architecture:** 三部分并行：新增 `POST /body/profile` 接口 → 调整 `MultiObjectiveOptimizer` 权重 → 在 `outfits.py` 动态生成中集成 `fit_preference_engine` 评分调整

**Tech Stack:** Python 3.14, FastAPI, Pydantic v2

## Global Constraints

- 所有原有测试必须保持通过
- 不改动已有 API 返回格式
- 权重对齐后验证 101 项测试全部通过

---

### Task 1: 新增 `POST /body/profile` 接口

**Files:**
- Create: 无（只修改现有文件）
- Modify: `src/app/models/schemas.py`（新增 `BodyProfileRequest` schema）
- Modify: `src/app/routes/body.py`（新增 `POST /profile` 路由）
- Modify: `src/app/services/store.py`（新增 `set_body_profile` 方法）
- Test: `tests/test_api.py`（新增测试）

**Interfaces:**
- Consumes: `BodyProfileRequest` schema
- Produces: `POST /api/v3/body/profile` 返回更新后的 profile

- [ ] **Step 1: 新增 `BodyProfileRequest` schema**

```python
class BodyProfileRequest(BaseModel):
    user_id: str
    height: Optional[float] = None          # cm
    weight: Optional[float] = None          # kg
    shoulder_width: Optional[float] = None  # cm
    waistline: Optional[float] = None       # cm
    leg_type: Optional[str] = None          # 'straight', 'o-shape', 'x-shape'
    body_shape: Optional[str] = None        # 'hourglass', 'pear', 'apple', 'rectangle', 'inverted-triangle'
    fit_preference: Optional[str] = None    # 'slim', 'loose', 'regular'
```

- [ ] **Step 2: 在 `store.py` 中新增 `set_body_profile` 方法**

```python
def set_body_profile(self, user_id: str, payload: Dict) -> Dict:
    user = self.get_or_create_user(user_id)
    profile = user.setdefault('body_profile', {})
    # 更新体态字段
    for key in ['height', 'weight', 'shoulder_width', 'waistline', 'leg_type', 'body_shape', 'fit_preference']:
        if key in payload and payload[key] is not None:
            profile[key] = payload[key]
    # 记录体重变化基线
    if payload.get('weight') is not None:
        profile['recorded_weight'] = payload['weight']
        profile['weight_recorded_at'] = datetime.now(timezone.utc).isoformat()
    return profile
```

- [ ] **Step 3: 在 `body.py` 中新增路由**

```python
@router.post('/profile', response_model=dict)
def set_body_profile(payload: BodyProfileRequest):
    updated = store.set_body_profile(payload.user_id, payload.model_dump(exclude_none=True))
    return {
        'decision_id': f"profile:{payload.user_id}:{datetime.now(timezone.utc).isoformat()}",
        'updated_profile': UpdatedProfile(**updated).model_dump(),
        'note': '体态档案已更新，将在下次穿搭推荐中生效',
    }
```

- [ ] **Step 4: 新增测试**

在 `tests/test_api.py` 末尾添加：
```python
def test_set_body_profile():
    user_id = 'user-profile-1'
    response = client.post('/api/v3/body/profile', json={
        'user_id': user_id,
        'height': 175.0,
        'weight': 72.0,
        'shoulder_width': 45.0,
        'waistline': 80.0,
        'leg_type': 'straight',
        'body_shape': 'rectangle',
        'fit_preference': 'slim',
    })
    assert response.status_code == 200
    body = response.json()
    assert 'decision_id' in body
    assert 'updated_profile' in body
    assert body['updated_profile']['fit_preference'] == {'global': 'slim'}

def test_update_body_profile_partial():
    """只更新部分字段"""
    user_id = 'user-profile-2'
    # 先设置完整
    client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'height': 170.0, 'weight': 65.0,
        'body_shape': 'pear', 'fit_preference': 'loose',
    })
    # 只更新体重
    resp = client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'weight': 68.0,
    })
    assert resp.status_code == 200
```

- [ ] **Step 5: 运行测试**

Run: `python -m pytest -q`
Expected: `103 passed`（新增 2 个测试）

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: 新增 POST /body/profile 体态数据录入接口

- BodyProfileRequest: 身高/体重/肩宽/腰线/腿型/体型
- store.set_body_profile() 持久化体态数据
- 支持部分字段更新，保留已有数据"
```

---

### Task 2: 多目标优化权重对齐设计文档

**Files:**
- Modify: `src/app/services/multi_objective_optimizer.py`（调整权重和阈值）

**设计文档权重：** 身材适配 50% / 美学 20% / 衣橱复用 15% / 实用场景 10% / 用户偏好 5%

**当前 4 目标权重：** BODY_FIT 20% / AESTHETIC 30% / REUSE 25% / SCENARIO 25%

**调整方案：** 将 5% 用户偏好融入 BODY_FIT（因为反馈分析已包含偏好学习），调整后：
- BODY_FIT: 0.50
- AESTHETIC: 0.20
- REUSE: 0.15
- SCENARIO: 0.10

- [ ] **Step 1: 修改权重和阈值**

```python
DEFAULT_WEIGHTS = {
    ObjectiveType.BODY_FIT: 0.50,
    ObjectiveType.AESTHETIC: 0.20,
    ObjectiveType.REUSE: 0.15,
    ObjectiveType.SCENARIO: 0.10,
}

TARGETS = {
    ObjectiveType.BODY_FIT: 0.85,
    ObjectiveType.AESTHETIC: 80.0,
    ObjectiveType.REUSE: 0.7,
    ObjectiveType.SCENARIO: 0.8,
}
```

- [ ] **Step 2: 运行测试**

Run: `python -m pytest -q`
Expected: `103 passed`（权重调整不应破坏已有测试，因为 optimizer 未被 outfits.py 实际调用）

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "fix: 多目标优化权重对齐设计文档 50/20/15/10

- BODY_FIT: 20% → 50%（体态适配优先）
- AESTHETIC: 30% → 20%
- REUSE: 25% → 15%
- SCENARIO: 25% → 10%"
```

---

### Task 3: 在 `outfits.py` 中集成体态反馈评分调整

**Files:**
- Modify: `src/app/routes/outfits.py`（在 `_build_candidates_from_wardrobe` 中调用 `get_fit_score_adjustment`）
- Test: 修改 `tests/test_api.py` 中 `test_outfit_decision_chain` 以验证体态反馈影响

- [ ] **Step 1: 在 `_build_candidates_from_wardrobe` 中集成体态评分调整**

在函数顶部获取用户 body_profile 和 sensitive_areas：
```python
from app.services.feedback_analyzer import fit_preference_engine

def _build_candidates_from_wardrobe(...):
    user = store.get_or_create_user(user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])
    body_profile = user.get('body_profile', {})
    sensitive_areas = body_profile.get('sensitive_areas', [])
    
    # ... 循环中，计算 score 后：
    # 体态反馈评分调整
    fit_adjustment = fit_preference_engine.get_fit_score_adjustment(
        user_id, category, attrs.get('fit_feedback', 'comfortable')
    )
    score = max(score + fit_adjustment, 10.0)
    
    # 敏感区域惩罚
    if sensitive_areas:
        for area in sensitive_areas:
            if area in ['tight_waist', 'exposed_belly', 'too_tight']:
                score = max(score - 5.0, 10.0)
```

- [ ] **Step 2: 运行测试**

Run: `python -m pytest -q`
Expected: `103 passed`

- [ ] **Step 3: 新增测试验证体态反馈影响决策**

在 `tests/test_api.py` 末尾添加：
```python
def test_body_feedback_affects_outfit_score():
    """验证体态反馈后，有敏感区域的品类评分会降低"""
    user_id = 'user-body-affect'
    # 录入衣物
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'body-tight-pants', 'category': 'bottom',
        'color': 'black', 'style': 'slim', 'season': 'all', 'occasion': 'daily',
    })
    # 提交体态反馈（紧身不适）
    client.post('/api/v3/body/feedback', json={
        'user_id': user_id, 'item_id': 'body-tight-pants',
        'fit_feedback': 'tight_waist', 'visual_comfort': 'exposed_belly',
    })
    # 请求穿搭
    resp = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id, 'occasion': 'daily',
        'datetime': '2026-07-21T12:00:00+08:00',
        'weather': {'temperature_c': 25, 'condition': 'sunny'},
    })
    assert resp.status_code == 200
    # 敏感区域应出现在返回中（通过 body_profile 传递）
    profile_resp = client.get(f'/api/v3/wardrobe/users/{user_id}/items')
    assert profile_resp.status_code == 200
```

- [ ] **Step 4: 运行测试**

Run: `python -m pytest -q`
Expected: `104 passed`

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: outfits.py 集成体态反馈评分调整

- 调用 fit_preference_engine.get_fit_score_adjustment() 调整评分
- 敏感区域品类惩罚扣分（-5/次）
- 体态反馈影响穿搭决策链路闭环"
```