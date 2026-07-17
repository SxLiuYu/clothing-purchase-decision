# 穿衣购衣决策

本地可运行原型已加入仓库，当前可直接基于 FastAPI 体验核心接口。

## 快速开始

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn src.app.main:app --reload
```

## 默认测试

```bash
python -m pytest tests/test_api.py
python -m pytest
```

## 原型接口

- `POST /api/v3/wardrobe/items`
- `GET /api/v3/wardrobe/users/{user_id}/items`
- `POST /api/v3/decisions/outfit`
- `POST /api/v3/shop/roi-analysis`
- `POST /api/v3/body/feedback`

## 目标功能

- A01+A03 基础衣橱录入与记忆补全入口
- B01+B02+B05 决策输入、天气接入与决策链
- C01+C08 买前 ROI 计算
- B09/D01 动态体态反馈入口
