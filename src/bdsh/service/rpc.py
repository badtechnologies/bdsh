import json
import socket
from pathlib import Path

from bdsh.service import BadOSService, ServiceUnavailableError
from bdsh.util.serializing import validate_json_value

_socket_path = lambda proc: f"/tmp/{proc}.sock"


class RPCSocketService(BadOSService, name=None):
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
        validate_json_value(req, "request")
        res = self._handle_request(req)

        validate_json_value(res, "response")
        client.sendall(json.dumps(res).encode("utf-8"))

    def _handle_request(self, request):
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        validate_json_value(params, "request.params")

        try:
            result = self.dispatch(method, params)
            validate_json_value(result, "response.msg")

            return {
                "id": request_id,
                "msg": result
            }

        except Exception as e:
            return {
                "id": request_id,
                "error": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }

    def dispatch(self, method, params):
        handler = getattr(self, method, None)

        if handler is None or not getattr(handler, "_is_service_method", False):
            raise ValueError(f"service method does not exist: '{method}'")

        return handler(**params)


def servicemethod(func):
    func._is_service_method = True
    return func


class RPCError(Exception):
    def __init__(self, msg: str, *, err_type: str | None = None):
        super().__init__(f"{err_type or "generic error"}: {msg}")


class RPCSocketClient:
    def __init__(self, proc_name: str):
        self.socket_path = _socket_path(proc_name)
        self._request_id = 0

    def request(self, method, params=None):
        validate_json_value(params, "request.params")
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
        validate_json_value(response, "response")

        if "error" in response:
            raise RPCError(response["error"]["message"], err_type=response["error"]["type"])

        return response["msg"]

    def __getattr__(self, method):
        def call(**params):
            return self.request(method, params)

        return call
