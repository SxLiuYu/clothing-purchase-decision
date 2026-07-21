import paramiko

password = 'YuJin#Ze$12'
HOST = '123.57.107.21'
USER = 'root'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=password, timeout=15)

# 查看当前 run.py 内容
stdin, stdout, stderr = client.exec_command('cat /opt/clothing-decision/run.py')
print('Current run.py:')
print(stdout.read().decode())

client.close()
