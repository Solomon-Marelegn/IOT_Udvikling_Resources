import socket
import net

def ping():
    
    default_gateway = "192.168.2.1"
    port = 53

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((default_gateway, port))
        return True

    except Exception as e:
        return False

    finally:
        sock.close()

