import json
import socket
from pathlib import Path

import psutil

from bdsh.service import Service


class NetworkService(Service, name="network.badproc"):
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
        self._create_socket()
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

    def _create_socket(self):
        self.socket_path.unlink(missing_ok=True)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.socket_path))
        self.server.listen(10)

    def _handle_client(self, client):
        req = json.loads(client.recv(65536).decode("utf-8"))
        res = self._handle_request(req)

        client.sendall(json.dumps(res).encode("utf-8"))

    def _handle_request(self, request):
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        try:
            result = self._dispatch(method, params)

            return {
                "id": request_id,
                "result": result
            }

        except Exception as e:
            return {
                "id": request_id,
                "error": {
                    "message": str(e)
                }
            }

    def _dispatch(self, method, params):
        match method:
            case "hostname":
                return socket.gethostname()

            case "resolve":
                return socket.gethostbyname(params["hostname"])

            case "interfaces":
                return {
                    interface: {
                        "flags": stats.flags,
                        "isup": stats.isup,
                        "duplex": stats.duplex,
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                    }
                    for interface, stats
                    in psutil.net_if_stats().items()
                }

            case "interface_addresses":
                return {
                    interface: [
                        {
                            "family": address.family.name,
                            "address": address.address,
                            "netmask": address.netmask,
                            "broadcast": address.broadcast,
                        }
                        for address in addresses
                    ]
                    for interface, addresses
                    in psutil.net_if_addrs().items()
                }

        raise ValueError(f"unknown method: {method}")
