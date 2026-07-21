# 项目进展报告

> 更新时间：2026-07-21
> 项目名称：智能衣橱 + AI 搭配师（穿衣购衣决策）
> 当前版本：v3.0 Superpower Edition（原型阶段）

---

## 一、项目概述

**一句话定义：**
你的 7×24 穿搭决策代理——不是"推荐一套衣服"，而是计算"你此刻最应该穿什么，以及这件新衣服值不值得买"。

**目标用户：** 22-40 岁，关注穿搭但时间有限、决策成本高的都市人群。

**核心痛点：**
- 满柜子衣服仍觉得"没衣服穿"
- 冲动买新衣回家发现无法搭配
- 不知道旧衣服为什么该留该扔

---

## 二、三大超级能力（Superpowers）

### Superpower 1：穿搭决策中枢（Style Decision Copilot）
基于天气、行程、体型、衣橱存量、穿着历史，推演一条"可执行穿搭决策链"。
- 核心指标：约束满足率、决策置信度、衣物复用率

### Superpower 2：动态体态档案（Dynamic Body Profile）
通过多角度照片、穿着反馈、体态变化，持续更新"你对版型的真实偏好"。
- 核心指标：体态识别误差下降率、用户修正频率下降率、版型适配命中率

### Superpower 3：衣橱组合缺口计算（Wardrobe ROI Predictor）
计算"这件新衣会新增多少搭配组合、激活多少旧衣、填补哪些场景缺口"。
- 核心指标：组合增量、旧衣激活率、场景覆盖率

---

## 三、当前实现状态

### 已完成（原型可用）

| 模块 | 接口 | 状态 |
|------|------|------|
| 数字衣橱 | `POST /api/v3/wardrobe/items` | 已实现 |
| 数字衣橱 | `GET /api/v3/wardrobe/users/{user_id}/items` | 已实现 |
| 穿搭决策 | `POST /api/v3/decisions/outfit` | 已实现 |
| 买前 ROI | `POST /api/v3/shop/roi-analysis` | 已实现 |
| 体态反馈 | `POST /api/v3/body/feedback` | 已实现 |
| 灵感推荐 | `POST /api/v3/inspiration/similar-outfits` | 已实现 |

### 核心服务实现

- `src/app/services/store.py` — 内存存储（用户、衣橱图、决策记录）
- `src/app/services/combination_calculator.py` — 组合缺口计算器
- `src/app/services/feedback_analyzer.py` — 连续反馈分析器
- `src/app/services/multi_objective_optimizer.py` — 多目标优化器

### 测试覆盖

- `tests/test_api.py` — API 接口测试（7 个用例）
- `tests/test_design_spec.py` — 设计文档规范测试
- `tests/test_design_functional.py` — 设计文档功能性测试
- `tests/test_superpower_fixes.py` — 超级能力修复验证测试

**测试结果：** 101 passed, 15 warnings（Pydantic V2 弃用警告，非阻塞）

---

## 四、技术栈

- **后端框架：** FastAPI + Uvicorn
- **数据模型：** Pydantic V2
- **HTTP 客户端：** httpx
- **测试框架：** pytest + pytest-asyncio
- **Python 版本：** >=3.9

---

## 五、项目结构

```
├── docs/                         # 文档目录
│   ├── design/                   # 设计方案
│   │   ├── 设计方案_v1.md
│   │   ├── 设计方案_v2.md
│   │   ├── 设计方案_v3_hybrid.md
│   │   ├── 设计方案_v3_superpowers.md   # 当前主版本
│   │   └── 设计方案_v3_superpowers_bak.md
│   ├── evaluations/              # 评估报告
│   │   ├── superpowers_brainstorm.md
│   │   ├── superpowers评估报告.md
│   │   ├── superpowers评估报告_v2.md
│   │   ├── superpowers评估报告_v3.md
│   │   ├── superpowers优化方案.md
│   │   ├── superpowers修复方案.md
│   │   └── v3_superpower_user_tests.md
│   └── records/                  # 会话记录
│       ├── 会话内容完整记录.md
│       ├── 历史会话记录.md
│       ├── contentA.md
│       ├── contentB.md
│       └── contentC.md
├── scripts/                     # 工具脚本
│   ├── check_*.py                # 文档检查脚本
│   ├── patch_*.py                # 文档补丁脚本
│   ├── deploy_server.py          # 服务器部署脚本
│   ├── demo_user_flow.py         # 用户流程演示
│   └── test_inspiration.py       # 灵感接口测试
├── src/app/                      # 应用源码
│   ├── main.py                   # FastAPI 入口
│   ├── models/schemas.py         # Pydantic 数据模型
│   ├── routes/                   # API 路由
│   │   ├── body.py               # 体态反馈
│   │   ├── inspiration.py         # 灵感推荐
│   │   ├── outfits.py            # 穿搭决策
│   │   ├── roi.py                # 买前 ROI
│   │   └── wardrobe.py           # 数字衣橱
│   └── services/                 # 业务服务
│       ├── store.py              # 内存存储
│       ├── combination_calculator.py
│       ├── feedback_analyzer.py
│       └── multi_objective_optimizer.py
├── tests/                        # 测试用例
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_design_spec.py
│   ├── test_design_functional.py
│   └── test_superpower_fixes.py
├── run.py                        # 启动脚本
├── requirements.txt              # Python 依赖
├── pyproject.toml                # 项目配置
└── README.md
```

---

## 六、实施路线图

### 阶段 1：原型验证（当前）
- FastAPI 后端骨架
- 核心接口实现（衣橱、决策、ROI、反馈、灵感）
- 内存存储与数据模型
- 测试覆盖

### 阶段 2：数据持久化（下一步）
- 替换内存存储为数据库（PostgreSQL/SQLite）
- 用户认证与多租户隔离
- 衣橱图持久化

### 阶段 3：AI 能力接入
- 多模态体态识别模型
- 视觉相似度计算（CLIP/ResNet）
- 天气 API 接入
- 购物平台 CPS 对接

### 阶段 4：前端与小程序
- 小程序前端
- 照片录入流程
- 决策结果可视化

---

## 七、已知问题与待办

1. **Pydantic V2 弃用警告：** 多处使用 `.dict()`，应迁移至 `.model_dump()`
2. **内存存储：** 当前为单进程内存存储，重启数据丢失
3. **示例数据：** 穿搭决策与灵感推荐使用硬编码示例数据
4. **无认证：** 接口无鉴权，仅适合原型演示
5. **部署脚本含明文密码：** `scripts/deploy_*.py` 含服务器密码，需迁移至环境变量

---

## 八、快速验证

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest

# 启动服务
python run.py

# 健康检查
curl http://localhost:8000/health

# 用户流程演示（需先启动服务）
python scripts/demo_user_flow.py
```
