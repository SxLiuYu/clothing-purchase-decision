# 智能衣橱 + AI 搭配师

> 你的 7×24 穿搭决策代理——不是"推荐一套衣服"，而是计算"你此刻最应该穿什么，以及这件新衣服值不值得买"。

当前为 FastAPI 后端原型，提供衣橱管理、穿搭决策、买前 ROI、体态反馈、灵感推荐五类接口。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # 启动 http://0.0.0.0:8000
```

## 运行测试

```bash
python -m pytest                 # 全部测试
python -m pytest tests/test_api.py   # 仅 API 集成测试
```

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET  | `/health` | 健康检查 |
| POST | `/api/v3/wardrobe/items` | 添加衣物 |
| GET  | `/api/v3/wardrobe/users/{user_id}/items` | 列出用户衣物 |
| POST | `/api/v3/wardrobe/relationships` | 添加衣物关系 |
| POST | `/api/v3/decisions/outfit` | 穿搭推荐决策 |
| POST | `/api/v3/shop/roi-analysis` | 买前 ROI 分析 |
| POST | `/api/v3/body/feedback` | 体态反馈 |
| POST | `/api/v3/body/profile` | 体态档案录入 |
| POST | `/api/v3/inspiration/similar-outfits` | 灵感推荐 |
| POST | `/api/v3/social/recommend` | 社媒推荐 |
| GET  | `/api/v3/wardrobe/search` | 衣橱搜索 |

## 目标功能

- A01+A03 基础衣橱录入与记忆补全入口
- B01+B02+B05 决策输入、天气接入与决策链
- C01+C08 买前 ROI 计算
- B09/D01 动态体态反馈入口

## 项目结构

```
├── src/app/                # FastAPI 应用
│   ├── main.py             # 入口
│   ├── models/schemas.py   # Pydantic 模型
│   ├── routes/             # 路由模块（wardrobe/outfits/roi/body/inspiration/social）
│   └── services/           # 存储 + 超级能力引擎
├── tests/                  # 测试用例
├── docs/                   # 设计文档与记录
│   ├── design/             # 设计方案 v1/v2/v3
│   ├── superpowers/        # 超级能力评估/优化/修复/计划
│   └── notes/              # 会话记录
├── scripts/                # 工具脚本
├── run.py                  # 启动脚本
└── pyproject.toml
```

详见 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)。

## 安全提示

- **部署凭据**：必须通过环境变量传入，禁止在脚本中硬编码密码
- **部署脚本**：`scripts/deploy_server.py` 是唯一部署入口，使用 `DEPLOY_HOST`、`DEPLOY_USER`、`DEPLOY_PASSWORD` 环境变量
- **示例配置**：参见 `.env.example` 文件
