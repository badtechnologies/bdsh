import json
import socket

from bdsh.daemon import DaemonUnavailableError


class NetworkClient:
    def __init__(self, socket_path="/tmp/bdsh-networkd.sock"):
        self.socket_path = socket_path
        self._request_id = 0

    def request(self, method, params=None):
        if params is None:
            params = {}

        self._request_id += 1

        request = {"id": self._request_id, "method": method, "params": params}
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            sock.connect(self.socket_path)
            sock.sendall(json.dumps(request).encode())
            data = sock.recv(65536)
        except OSError as e:
            if e.errno == 2:
                raise DaemonUnavailableError("networkd")
            else:
                raise e
        finally:
            sock.close()

        response = json.loads(data.decode())

        if "error" in response:
            raise RuntimeError(response["error"]["message"])

        return response["result"]

    def hostname(self):
        return self.request("hostname")

    def interfaces(self):
        return self.request("interfaces")

    def interface_addresses(self):
        return self.request("interface_addresses")

    def resolve(self, hostname):
        return self.request("resolve", {"hostname": hostname})
