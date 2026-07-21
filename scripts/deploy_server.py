import paramiko
import os

password = 'YuJin#Ze$12'
HOST = '123.57.107.21'
USER = 'root'

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=password, timeout=15)
    
    # 1. 更新系统
    print('[1] Updating system...')
    run(client, 'apt-get update && apt-get upgrade -y')
    
    # 2. 安装 Python 和依赖
    print('[2] Installing Python dependencies...')
    run(client, 'apt-get install -y python3 python3-pip python3-venv git')
    
    # 3. 创建项目目录
    print('[3] Setting up project directory...')
    run(client, 'mkdir -p /opt/clothing-decision')
    
    # 4. 上传项目文件
    print('[4] Uploading project files...')
    sftp = client.open_sftp()
    for root, dirs, files in os.walk('.'):
        # 跳过 git 和缓存
        if '.git' in root or '__pycache__' in root or 'node_modules' in root:
            continue
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = f'/opt/clothing-decision/{os.path.relpath(local_path, ".")}'
            try:
                sftp.put(local_path, remote_path)
                print(f'  Uploaded: {local_path}')
            except Exception as e:
                print(f'  Skip {local_path}: {e}')
    sftp.close()
    
    # 5. 创建虚拟环境并安装依赖
    print('[5] Setting up virtual environment...')
    run(client, 'cd /opt/clothing-decision && python3 -m venv .venv')
    run(client, 'source /opt/clothing-decision/.venv/bin/activate && pip install --upgrade pip')
    run(client, 'source /opt/clothing-decision/.venv/bin/activate && pip install fastapi uvicorn pydantic httpx python-dotenv')
    run(client, 'source /opt/clothing-decision/.venv/bin/activate && pip install pytest pytest-asyncio')
    
    # 6. 创建 systemd 服务
    print('[6] Creating systemd service...')
    service_content = '''[Unit]
Description=Clothing Purchase Decision API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/clothing-decision
ExecStart=/opt/clothing-decision/.venv/bin/python run.py
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
