# 穿衣购衣决策

智能衣橱 + AI 搭配师原型，当前可基于 FastAPI 体验核心接口。

## 快速开始

\\ash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python run.py
\
## 默认测试

\\ash
python -m pytest tests/test_api.py
python -m pytest
\
## 原型接口

- \POST /api/v3/wardrobe/items- \GET /api/v3/wardrobe/users/{user_id}/items- \POST /api/v3/decisions/outfit- \POST /api/v3/shop/roi-analysis- \POST /api/v3/body/feedback- \POST /api/v3/inspiration/similar-outfits
## 目标功能

- A01+A03 基础衣橱录入与记忆补全入口
- B01+B02+B05 决策输入、天气接入与决策链
- C01+C08 买前 ROI 计算
- B09/D01 动态体态反馈入口

## 项目结构

\├── docs/                    # 文档目录
│   ├── design/              # 设计方案（v1-v3）
│   ├── evaluations/         # 评估报告与测试用例
│   └── records/             # 会话记录与内容
├── scripts/                 # 工具脚本（检查、补丁、部署）
├── src/app/                 # FastAPI 应用源码
│   ├── main.py              # 应用入口
│   ├── models/schemas.py    # 数据模型
│   ├── routes/              # API 路由
│   └── services/            # 业务服务
├── tests/                   # 测试用例
├── run.py                   # 启动脚本
├── requirements.txt         # Python 依赖
└── pyproject.toml           # 项目配置
\