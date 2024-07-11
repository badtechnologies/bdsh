import socket
import threading
import paramiko
import json
import bdsh

with open("users.json", 'r') as f:
    USERS = json.load(f)

# Load the host key
host_key = paramiko.RSAKey(filename="server_rsa_key")

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
        
        buffer = []

        channel.send(bdsh.get_header())
        channel.send(bdsh.get_prompt())

        while True:
            char = channel.recv(1024)
            channel.send(char)
            
            if char == b'\x03':
                break
            elif char == b'\r':
                channel.send(b'\n'+bdsh.run_line(b''.join(buffer)))
                buffer.clear()
                channel.send(bdsh.get_prompt())
            else:
                buffer.append(char)
        
        channel.close()
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        transport.close()

def start_server(port=2200):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(100)
    
    print(f"Listening for connection on port {port} ...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
