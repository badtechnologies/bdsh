import json
import signal
import socket
from abc import ABC, abstractmethod
from pathlib import Path
from types import FrameType
from typing import Type

SERVICES: dict[str, Type["Service"]] = {}


class Service(ABC):
    def __init__(self):
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def __init_subclass__(cls, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)

        if name is not None:
            cls.name = name
            if name in SERVICES:
                raise ValueError(f"service already registered: '{name}'")
            SERVICES[name] = cls

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def _handle_shutdown(self, signum: int, frame: FrameType | None):
        ...


class IPCSocketService(Service, name=None):
    def __init__(self):
        super().__init__()
        self.socket_path = Path(f"/tmp/{self.name}.sock").resolve()
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



class ServiceUnavailableError(OSError):
    def __init__(self, name: str):
        super().__init__(f"service unavailable: {name}")
