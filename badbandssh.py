import socket
import threading
import paramiko
import json
import bdsh

with open("bdsh/conf/users.json", 'r') as f:
    USERS = json.load(f)

# Load the host key
host_key = paramiko.RSAKey(filename='bdsh/conf/badbandssh_rsa_key')

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL if USERS.get(username) == password else paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

def handle_client(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    
    server = SSHServer()
    try:
        transport.start_server(server=server)
        channel = transport.accept(20)
        if channel is None:
            return
        
        server.event.wait(10)
        if not server.event.is_set():
            raise Exception("No shell request")
        
        instance = bdsh.Shell(lambda s: channel.send(s.encode()), lambda: channel.recv(1).decode(), is_ssh=True)
        instance.start()
        
        channel.close()
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        transport.close()

def start(port=2200):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        sock.listen(100)

        print(f"Listening for connection on port {port} ...")
    
        while True:
            client, addr = sock.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client,)).start()
    except KeyboardInterrupt:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

if __name__ == "__main__":
    start()
