import paramiko
import os

# 从环境变量读取部署配置
HOST = os.environ.get('DEPLOY_HOST', '')
USER = os.environ.get('DEPLOY_USER', '')
PASSWORD = os.environ.get('DEPLOY_PASSWORD', '')

# 远程路径
REMOTE_PROJECT_PATH = os.environ.get('DEPLOY_REMOTE_PATH', '/opt/clothing-decision')

def deploy():
    # 验证环境变量
    if not all([HOST, USER, PASSWORD]):
        print('❌ 错误: 请设置环境变量 DEPLOY_HOST, DEPLOY_USER, DEPLOY_PASSWORD')
        print('   示例: export DEPLOY_HOST=123.57.107.21')
        print('   或创建 .env 文件并运行: source .env && python scripts/deploy_server.py')
        return
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    
    # 1. 更新系统
    print('[1] Updating system...')
    run(client, 'apt-get update && apt-get upgrade -y')
    
    # 2. 安装 Python 和依赖
    print('[2] Installing Python dependencies...')
    run(client, 'apt-get install -y python3 python3-pip python3-venv git')
    
    # 3. 创建项目目录
    print('[3] Setting up project directory...')
    run(client, f'mkdir -p {REMOTE_PROJECT_PATH}/data')
    
    # 4. 上传项目文件
    print('[4] Uploading project files...')
    sftp = client.open_sftp()
    for root, dirs, files in os.walk('.'):
        # 跳过 git、缓存、虚拟环境、敏感文件
        if '.git' in root or '__pycache__' in root or 'node_modules' in root or '.venv' in root:
            continue
        for file in files:
            local_path = os.path.join(root, file)
            # 跳过 .env 文件（包含敏感信息）
            if file == '.env':
                continue
            remote_path = f'{REMOTE_PROJECT_PATH}/{os.path.relpath(local_path, ".")}'
            try:
                sftp.put(local_path, remote_path)
                print(f'  Uploaded: {local_path}')
            except Exception as e:
                print(f'  Skip {local_path}: {e}')
    sftp.close()
    
    # 5. 创建虚拟环境并安装依赖
    print('[5] Setting up virtual environment...')
    run(client, f'cd {REMOTE_PROJECT_PATH} && python3 -m venv .venv')
    run(client, f'source {REMOTE_PROJECT_PATH}/.venv/bin/activate && pip install --upgrade pip')
    run(client, f'source {REMOTE_PROJECT_PATH}/.venv/bin/activate && pip install -r {REMOTE_PROJECT_PATH}/requirements.txt')
    
    # 6. 创建 systemd 服务
    print('[6] Creating systemd service...')
    service_content = f'''[Unit]
Description=Clothing Purchase Decision API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_PROJECT_PATH}
Environment="STORE_DB_PATH={REMOTE_PROJECT_PATH}/data/wardrobe.db"
ExecStart={REMOTE_PROJECT_PATH}/.venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    write_file(client, '/etc/systemd/system/clothing-decision.service', service_content)
    
    run(client, 'systemctl daemon-reload')
    run(client, 'systemctl enable clothing-decision')
    run(client, 'systemctl start clothing-decision')
    
    # 7. 设置防火墙
    print('[7] Configuring firewall...')
    run(client, 'ufw allow 8000/tcp || true')
    
    # 8. 检查状态
    print('[8] Checking service status...')
    stdin, stdout, stderr = client.exec_command('systemctl status clothing-decision')
    print(stdout.read().decode())
    
    print('\\nDeployment complete!')
    client.close()

def run(client, cmd):
    print(f'  $ {cmd}')
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.close()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(f'  OUT: {out[:500]}')
    if err:
        print(f'  ERR: {err[:500]}')

def write_file(client, path, content):
    with open(f'/tmp/{os.path.basename(path)}', 'w') as f:
        f.write(content)
    sftp = client.open_sftp()
    sftp.put(f'/tmp/{os.path.basename(path)}', path)
    sftp.close()

if __name__ == '__main__':
    deploy()
