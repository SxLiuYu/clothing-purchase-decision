# 模块 D：社媒推荐 Design Spec v1.0

> 文档版本：v1.0 | 更新时间：2026-07-21
> 状态：设计方案
> 关联：设计方案_v3_superpowers.md 第六章

---

## 一、设计原则

1. **可闭环**：所有功能在当前后端项目内可测试、可验证
2. **可插拔**：外部依赖（社媒爬取、AI 视觉、电商）定义接口契约，用 mock 实现
3. **依赖已有资产**：复用 Superpower 2 体态档案、Superpower 3 衣橱图谱
4. **YAGNI**：只实现核心推荐链路，不做 P2 功能（D-07 穿搭组合预览、D-08 一键跳转）

## 二、范围

### 本次实现（P1 核心链路）

| 功能 ID | 功能名称 | 说明 |
|---------|----------|------|
| D-01 | 脸型录入 | 用户选择脸型类型（扩展 body/profile 接口） |
| D-02 | 动态体态细化 | 扩展肤色、脸型字段到体态档案 |
| D-04 | 同特征筛选 | 基于脸型+体型+肤色匹配推荐内容 |
| D-06 | 推荐展示 | 结构化输出：单品 + 推荐理由 + 匹配度 |

### 接口预留（mock 实现，可替换）

| 功能 ID | 功能名称 | 接口契约 |
|---------|----------|---------|
| D-03 | 社媒爬取 | `SocialMediaFetcher` 接口，返回 `List[Post]` |
| D-05 | AI 单品分析 | `ItemAnalyzer` 接口，从图片提取单品属性 |

### 本次不实现（P2）

| 功能 ID | 原因 |
|---------|------|
| D-07 穿搭组合预览 | 前端功能，需前端实现 |
| D-08 一键跳转 | 需电商联盟合作 |

## 三、架构

```
POST /api/v3/social/profile          PUT /api/v3/social/preferences
     |                                       |
     v                                       v
[体态档案扩展]                          [风格偏好]
     |                                       |
     +-----------+-----------+---------------+
                 |           |
                 v           v
     [SocialMediaFetcher]  [ItemAnalyzer]
          (mock)              (mock)
                 |           |
                 +-----+-----+
                       |
                       v
     [同特征筛选引擎] - 脸型 + 体型 + 肤色 匹配
                       |
                       v
     [RecommendationEngine] - 排序 + 推荐理由
                       |
                       v
     POST /api/v3/social/recommend
```

## 四、数据模型

### 4.1 体态档案扩展

在 `BodyProfileRequest` 中新增字段：

```python
# 现有字段
height: Optional[float]
weight: Optional[float]
shoulder_width: Optional[float]
waistline: Optional[float]
leg_type: Optional[str]       # 'straight', 'o-shape', 'x-shape'
body_shape: Optional[str]     # 'hourglass', 'pear', 'apple', 'rectangle', 'inverted-triangle'
fit_preference: Optional[str] # 'slim', 'loose', 'regular'

# 新增字段（D-01 / D-02）
face_shape: Optional[str]     # 'oval', 'round', 'square', 'heart', 'diamond', 'oblong'
skin_tone: Optional[str]      # 'warm', 'cool', 'neutral', 'olive'
```

### 4.2 推荐数据结构

```python
class SocialPost(BaseModel):
    post_id: str
    title: str
    source: str               # 'mock', 'xiaohongshu', 'weibo'
    author: str
    image_url: Optional[str] = None

class SocialItem(BaseModel):
    item_id: str
    category: str
    name: str
    brand: Optional[str] = None
    price: Optional[float] = None
    purchase_url: Optional[str] = None
    image_url: Optional[str] = None

class SocialRecommendation(BaseModel):
    rank: int
    score: float               # 综合推荐分 0-100
    match_score: float         # 特征匹配度 0-1
    reproducibility: float     # 可复现度 0-1
    sentiment: float           # 正向情感分 0-1
    post: SocialPost
    items: List[SocialItem]
    rationale: str             # 推荐理由

class SocialRecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[SocialRecommendation]
    total_count: int
```

## 五、接口设计

### 5.1 更新体态档案（扩展已有接口）

```
PUT /api/v3/body/profile
```

在现有 `POST /api/v3/body/profile` 基础上，新增 `face_shape` 和 `skin_tone` 字段。

### 5.2 社媒推荐

```
POST /api/v3/social/recommend
Request:
{
    "user_id": "string",
    "occasion": "string",          # 穿搭需求：formal/casual/sport/...
    "limit": 5                     # 返回数量
}

Response:
{
    "user_id": "string",
    "recommendations": [
        {
            "rank": 1,
            "score": 85.0,
            "match_score": 0.92,
            "reproducibility": 0.78,
            "sentiment": 0.95,
            "post": {
                "post_id": "mock-001",
                "title": "正式通勤穿搭推荐",
                "source": "mock",
                "author": "穿搭达人"
            },
            "items": [
                {
                    "item_id": "mock-item-001",
                    "category": "outwear",
                    "name": "白色修身衬衫",
                    "brand": "示例品牌",
                    "price": 299.0
                }
            ],
            "rationale": "同脸型（oval）+ 同体型（rectangle）+ 同为暖色调肤色"
        }
    ],
    "total_count": 1
}
```

## 六、核心组件

### 6.1 SocialMediaFetcher（可插拔）

```python
class SocialMediaFetcher(ABC):
    """社媒数据获取接口"""

    @abstractmethod
    def fetch_posts(
        self,
        face_shape: str,
        body_shape: str,
        skin_tone: str,
        occasion: str,
        limit: int = 10,
    ) -> List[Dict]:
        ...

class MockSocialMediaFetcher(SocialMediaFetcher):
    """Mock 实现：返回预置示例数据"""

class XiaoHongShuFetcher(SocialMediaFetcher):
    """小红书爬取实现（预留）"""

class WeiBoFetcher(SocialMediaFetcher):
    """微博爬取实现（预留）"""
```

### 6.2 ItemAnalyzer（可插拔）

```python
class ItemAnalyzer(ABC):
    """从图片/文本中提取单品信息"""

    @abstractmethod
    def analyze_items(self, post: Dict) -> List[Dict]:
        ...

class MockItemAnalyzer(ItemAnalyzer):
    """Mock 实现：返回预置示例单品"""

class VisionItemAnalyzer(ItemAnalyzer):
    """基于多模态模型的单品分析（预留）"""
```

### 6.3 推荐引擎

```python
class SocialRecommendationEngine:
    """
    社媒推荐引擎

    排序：综合分 = 可复现度 × 匹配度 × 正向情感分
    """

    def __init__(self, fetcher: SocialMediaFetcher, analyzer: ItemAnalyzer):
        self.fetcher = fetcher
        self.analyzer = analyzer

    def recommend(
        self,
        user_id: str,
        body_profile: Dict,
        occasion: str,
        limit: int = 5,
    ) -> Dict:
        ...
```

## 七、文件结构

```
src/app/
├── routes/
│   └── social.py              # 新增：社媒推荐路由
├── models/
│   └── schemas.py             # 修改：扩展 BodyProfileRequest + 新增推荐模型
├── services/
│   ├── social_recommendation.py  # 新增：推荐引擎
│   ├── social_fetcher.py         # 新增：社媒数据获取器（含 mock）
│   └── item_analyzer.py          # 新增：单品分析器（含 mock）
tests/
└── test_social_recommendation.py # 新增：社媒推荐测试
```

## 八、测试策略

| 测试类型 | 数量 | 说明 |
|---------|------|------|
| 体态档案扩展 | 1 | 验证 face_shape / skin_tone 存储 |
| Mock 社媒获取 | 1 | 验证 fetcher 返回格式正确 |
| 推荐引擎单元 | 2 | 匹配度计算 + 排序逻辑 |
| 完整推荐链路 | 1 | 从体态→获取→分析→推荐 全链路 |
| 冷启动 | 1 | 无体态档案时默认推荐 |

## 九、不实现的内容

- D-03 真实社媒爬取：仅 mock，接口预留
- D-05 AI 单品分析：仅 mock，接口预留
- D-07 穿搭组合预览：前端功能
- D-08 一键跳转：需电商联盟合作
- 真实图片上传/存储：仅 URL 字段
- 用户点赞/收藏反馈：未来版本