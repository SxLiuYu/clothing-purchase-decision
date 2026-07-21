import paramiko

password = 'YuJin#Ze$12'
HOST = '123.57.107.21'
USER = 'root'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=password, timeout=15)

# 修复 run.py
print('Fixing run.py...')
sftp = client.open_sftp()
run_py_content = '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.main import app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=False)
'''
with open('/tmp/run.py', 'w') as f:
    f.write(run_py_content)
sftp.put('/tmp/run.py', '/opt/clothing-decision/run.py')
sftp.close()

# 重启服务
print('Restarting service...')
stdin, stdout, stderr = client.exec_command('systemctl restart clothing-decision')
stdout.channel.recv_exit_status()

import time
time.sleep(3)

# 检查状态
stdin, stdout, stderr = client.exec_command('systemctl status clothing-decision')
print(stdout.read().decode())

# 测试 API
import subprocess
result = subprocess.run(['curl', '-s', 'http://localhost:8000/health'], capture_output=True, text=True)
print('Health check:', result.stdout)

client.close()
print('Done!')
