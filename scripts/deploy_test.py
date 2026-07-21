import paramiko

password = 'YuJin#Ze$12'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('123.57.107.21', username='root', password=password, timeout=15)
    stdin, stdout, stderr = client.exec_command('echo connected && uname -a')
    print(stdout.read().decode())
    client.close()
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
