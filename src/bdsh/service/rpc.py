import json
import socket
from abc import abstractmethod
from pathlib import Path

from bdsh.service import Service, ServiceUnavailableError

_socket_path = lambda proc: f"/tmp/{proc}.sock"


class RPCSocketService(Service, name=None):
    def __init__(self):
        super().__init__()
        self.socket_path = Path(_socket_path(self.name)).resolve()
        self.server = None
        self.running = False

    def _handle_shutdown(self, signum, frame):
        self.running = False

        if self.server:
            self.server.close()
            self.server = None

    def start(self):
        self.socket_path.unlink(missing_ok=True)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.socket_path))
        self.server.listen(10)
        self.running = True

        try:
            while self.running:
                try:
                    client, _ = self.server.accept()
                except OSError:
                    if not self.running:
                        break
                    raise

                try:
                    self._handle_client(client)
                finally:
                    client.close()
        finally:
            self.stop()

    def stop(self):
        self.running = False

        if self.server:
            self.server.close()
            self.server = None

        self.socket_path.unlink(missing_ok=True)

    def _handle_client(self, client):
        req = json.loads(client.recv(65536).decode("utf-8"))
        res = self._handle_request(req)

        client.sendall(json.dumps(res).encode("utf-8"))

    def _handle_request(self, request):
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        try:
            result = self.dispatch(method, params)

            return {
                "id": request_id,
                "msg": result
            }

        except Exception as e:
            return {
                "id": request_id,
                "error": {
                    "message": str(e)
                }
            }

    @abstractmethod
    def dispatch(self, method, params):
        ...


class RPCSocketClient:
    def __init__(self, proc_name: str):
        self.socket_path = _socket_path(proc_name)
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
                raise ServiceUnavailableError(self.socket_path)
            else:
                raise e
        finally:
            sock.close()

        response = json.loads(data.decode())

        if "error" in response:
            raise RuntimeError(response["error"]["message"])

        return response["msg"]
