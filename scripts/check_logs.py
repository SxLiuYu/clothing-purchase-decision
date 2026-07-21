import paramiko

password = 'YuJin#Ze$12'
HOST = '123.57.107.21'
USER = 'root'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=password, timeout=15)

# 查看日志
stdin, stdout, stderr = client.exec_command('journalctl -u clothing-decision --no-pager -n 20')
print(stdout.read().decode())

# 手动运行看错误
print('\\n--- Manual run test ---')
stdin, stdout, stderr = client.exec_command('cd /opt/clothing-decision && source .venv/bin/activate && python run.py 2>&1 &')
import time
time.sleep(5)

stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health')
print('Health:', stdout.read().decode())

client.close()
