# Step 6: 衣橱搜索 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 实现衣橱搜索功能，支持按类别、颜色、风格、季节、场合等多维度过滤

**Architecture:** 新增 `GET /api/v3/wardrobe/search` 端点，基于 store 中已有衣物属性过滤

**Tech Stack:** Python 3.14, FastAPI, Pydantic v2

## Global Constraints

- 所有原有测试必须保持通过
- 遵循现有代码风格
- 搜索返回格式与现有 `list_items` 一致

---

### Task 1: 衣橱搜索 API

**Files:**
- Modify: `src/app/routes/wardrobe.py`（新增 search 端点）
- Modify: `src/app/models/schemas.py`（新增搜索请求/响应模型）
- Test: 新增 `tests/test_wardrobe_search.py`

- [ ] **Step 1: 新增搜索模型**

```python
class WardrobeSearchRequest(BaseModel):
    user_id: str
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    keyword: Optional[str] = None  # 模糊搜索 item_id / name
    limit: int = Field(default=50, ge=1, le=200)
```

- [ ] **Step 2: 实现搜索端点**

在 `wardrobe.py` 中新增：

```python
@router.post('/search')
def search_wardrobe(payload: WardrobeSearchRequest):
    user = store.get_or_create_user(payload.user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])
    
    results = []
    for node in nodes:
        # 精确匹配
        if payload.category and node.get('category') != payload.category:
            continue
        if payload.color and node.get('color') != payload.color:
            continue
        if payload.style and node.get('style') != payload.style:
            continue
        if payload.season and node.get('season') != payload.season:
            continue
        if payload.occasion and node.get('occasion') != payload.occasion:
            continue
        # 模糊搜索
        if payload.keyword:
            kw = payload.keyword.lower()
            searchable = f"{node.get('item_id', '')} {node.get('category', '')} {node.get('color', '')} {node.get('style', '')}".lower()
            if kw not in searchable:
                continue
        results.append(node)
    
    return {
        'user_id': payload.user_id,
        'count': len(results),
        'items': results[:payload.limit],
    }
```

- [ ] **Step 3: 编写测试**

```python
def test_search_by_category():
    # 录入多件衣物
    # 按 category 搜索，验证返回数量和内容

def test_search_by_color():
    # 按 color 搜索

def test_search_combined():
    # 多条件组合搜索

def test_search_keyword():
    # 关键词模糊搜索

def test_search_empty():
    # 无匹配结果
```

- [ ] **Step 4: 运行测试**

Run: `python -m pytest -q`
Expected: `117 passed`

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: 新增衣橱搜索功能，支持多维度过滤和关键词搜索"
```

---

### Task 2: CLIP 相似度计算（预留接口）

**Files:**
- Create: `src/app/services/similarity.py`（含 MockSimilarityEngine + CLIP 预留）
- Modify: `src/app/routes/roi.py`（集成相似度引擎）
- Test: 新增 `tests/test_similarity.py`

- [ ] **Step 1: 创建相似度引擎**

```python
class SimilarityEngine(ABC):
    @abstractmethod
    def calculate_similarity(self, item_a: Dict, item_b: Dict) -> float:
        ...

class MockSimilarityEngine(SimilarityEngine):
    """基于属性重叠的简化相似度"""
    def calculate_similarity(self, item_a, item_b):
        # 类别相同 +0.4，颜色相同 +0.3，风格相同 +0.2，材质相同 +0.1
        score = 0.0
        if item_a.get('category') == item_b.get('category'):
            score += 0.4
        if item_a.get('color') == item_b.get('color'):
            score += 0.3
        if item_a.get('style') == item_b.get('style'):
            score += 0.2
        if item_a.get('material') == item_b.get('material'):
            score += 0.1
        return min(1.0, score)

class CLIPSimilarityEngine(SimilarityEngine):
    """基于 CLIP 模型的视觉相似度（预留）"""
    def calculate_similarity(self, item_a, item_b):
        raise NotImplementedError("CLIPSimilarityEngine not yet implemented")
```

- [ ] **Step 2: 集成到 ROI 分析**

修改 `roi.py`，用相似度引擎替换硬编码的 `candidate_score`

- [ ] **Step 3: 编写测试**

- [ ] **Step 4: 运行测试**

Run: `python -m pytest -q`
Expected: `122 passed`

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: 新增相似度计算引擎（属性匹配 mock + CLIP 预留）"
```

---

### Task 3: 图片上传（预留接口）

**Files:**
- Create: `src/app/services/image_storage.py`（含 MockImageStorage + S3 预留）
- Modify: `src/app/routes/wardrobe.py`（新增图片上传端点）
- Test: 新增 `tests/test_image_upload.py`

- [ ] **Step 1: 创建图片存储接口**

```python
class ImageStorage(ABC):
    @abstractmethod
    def upload(self, file_bytes: bytes, filename: str) -> str:
        """返回图片 URL"""
        ...

class MockImageStorage(ImageStorage):
    def upload(self, file_bytes, filename):
        return f"https://mock-storage.example.com/images/{filename}"

class S3ImageStorage(ImageStorage):
    """S3/MinIO 存储（预留）"""
    def upload(self, file_bytes, filename):
        raise NotImplementedError("S3ImageStorage not yet implemented")
```

- [ ] **Step 2: 新增上传端点**

```python
@router.post('/users/{user_id}/upload')
def upload_image(user_id: str, file: UploadFile):
    ...
```

- [ ] **Step 3: 编写测试**

- [ ] **Step 4: 运行测试**

Run: `python -m pytest -q`
Expected: `127 passed`

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: 新增图片上传功能（mock 存储 + S3 预留）"
```
