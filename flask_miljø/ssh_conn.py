import paramiko

def create_ssh_client(host_addr, user, password):
    host = host_addr
    port = 22
    user = user
    password = password
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password)
    
    return client

def find_pid_by_name(process_name, ssh_client):
    command = f"pgrep -f {process_name}"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    pid = stdout.read().decode().strip().split()
    return pid

def get_database_status(ssh_client):
    command = 'ps aux | grep mysql'
    stdin, stdout, stderr = ssh_client.exec_command(command)
    process_list = stdout.read().decode()
    ssh_client.close()

    if 'mariadbd' in process_list:
        return 'On'
    else:
        return 'Off'

def get_mqtt_sub_status(ssh_client):
    command = 'ps aux | grep mqtt_sub.py'
    stdin, stdout, stderr = ssh_client.exec_command(command)
    process_list = stdout.read().decode()
    ssh_client.close()

    if 'python3 mqtt_sub.py' in process_list:
        return "On"
    else:
        return "Off"

def get_mqtt_broker_status(ssh_client):
    command = 'ps aux | grep mosquitto'
    stdin, stdout, stderr = ssh_client.exec_command(command)
    process_list = stdout.read().decode()
    ssh_client.close()

    if '/mosquitto/mosquitto.conf' in process_list:
        return 'On'
    else:
        return 'Off'
    
def start_mqtt_sub(ssh_client):
    cmd = 'python3 mqtt_sub.py'
    ssh_client.exec_command(cmd)

def stop_mqtt_sub(ssh_client):
    pid_list = find_pid_by_name('mqtt_sub.py', ssh_client)
    for i in pid_list:
        ssh_client.exec_command(f"kill {i}")
    print('mqtt stopped')

def exec_cmd_on_vm(cmd):
    host_list = {'Mqtt_Sub'      : ['192.168.2.20', 'test', 'test'],
                 'start_Mqtt_Sub': ['192.168.2.20', 'test', 'test'],
                 'stop_Mqtt_Sub' : ['192.168.2.20', 'test', 'test'],
                 'Mqtt_Broker'   : ['192.168.2.18', 'test', 'test'],
                 'Database'      : ['192.168.2.21', 'test', 'test']
                 }

    client = create_ssh_client(host_list[cmd][0], host_list[cmd][1], host_list[cmd][2])
    if cmd == 'start_Mqtt_Sub':
        start_mqtt_sub(client)
    elif cmd == 'stop_Mqtt_Sub':
        stop_mqtt_sub(client)
    elif cmd == 'Database':
        return get_database_status(client)
    elif cmd == 'Mqtt_Sub':
        return get_mqtt_sub_status(client)
    elif cmd == 'Mqtt_Broker':
        return get_mqtt_broker_status(client)
    client.close()
    
    


