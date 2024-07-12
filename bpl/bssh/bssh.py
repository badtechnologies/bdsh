from io import TextIOBase
import socket
import threading
import paramiko
import json
import bdsh


class ChannelTextIO(TextIOBase):
    def __init__(self, channel: paramiko.Channel):
        self._channel = channel
        self._buffer = b''

    def write(self, data):
        self._channel.sendall(data.encode())

    def read(self, size=-1):
        if size < 0:
            return self._channel.recv(size).decode()
        else:
            return self._channel.recv(size).decode()

    def readline(self, size=-1):
        if size == -1:
            size = 65536
        data = b''
        while not data.endswith(b'\n') and len(data) < size:
            data += self._channel.recv(1)
        return data.decode()

    def flush(self):
        pass


with open("bdsh/cfg/users.json", 'r') as f:
    USERS = json.load(f)

host_key = paramiko.RSAKey(filename='bdsh/cfg/badbandssh_rsa_key')


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.username = ""

    def check_auth_password(self, username, password):
        self.username = username
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


def log(s: str):
    print(f"[{threading.current_thread().name}]\t{s}")


def handle_client(client_socket):
    server = SSHServer()

    log("Incoming connection")

    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)
        if channel is None:
            return

        server.event.wait(10)
        if not server.event.is_set():
            raise Exception("No shell request")

        threading.current_thread().name = server.username + "@" + \
            threading.current_thread().name
        log("Connection succeeded")

        connio = ChannelTextIO(channel)

        instance = bdsh.Shell(connio, connio, is_ssh=True)
        instance.start()

        channel.close()
    except Exception as e:
        log(f"FATAL: {e}")
    finally:
        transport.close()
        log("Connection terminated")


def start(port=2200):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        sock.listen(100)

        log(f"Listening for connection on port {port}")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=handle_client, args=(
                client,), name=f"{addr[0]}:{addr[1]}").start()
    except KeyboardInterrupt:
        sock.close()
        exit()


if __name__ == "__main__":
    start()
