#!/bin/bash
# 服务器初始化脚本 - 在服务器上执行一次
# 用法: ssh root@SERVER 'bash -s' < scripts/server_setup.sh
set -e

PROJECT_DIR="/opt/clothing-decision"
REPO_URL="https://github.com/SxLiuYu/clothing-purchase-decision.git"

echo "=== [1/6] 安装系统依赖 ==="
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git

echo "=== [2/6] 克隆项目 ==="
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "项目已存在，拉取最新代码..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo "=== [3/6] 创建数据目录 ==="
mkdir -p "$PROJECT_DIR/data"

echo "=== [4/6] 创建虚拟环境并安装依赖 ==="
python3 -m venv "$PROJECT_DIR/.venv"
source "$PROJECT_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [5/6] 配置 systemd 服务 ==="
cp "$PROJECT_DIR/deploy/clothing-decision.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable clothing-decision
systemctl restart clothing-decision

echo "=== [6/6] 配置防火墙 ==="
ufw allow 8000/tcp || true

echo ""
echo "=== 部署完成 ==="
sleep 3
systemctl status clothing-decision --no-pager || true
echo ""
echo "API 地址: http://$(hostname -I | awk '{print $1}'):8000/health"
