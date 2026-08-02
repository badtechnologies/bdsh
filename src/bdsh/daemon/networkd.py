import json
import os
import socket

from bdsh.daemon import Daemon
from bdsh.network import NetworkManager


class NetworkDaemon(Daemon, name="networkd"):
    def __init__(self):
        super().__init__()
        self.server = NetworkServer()

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def _handle_shutdown(self, signum, frame):
        self.server.shutdown()


class NetworkServer:
    def __init__(self, socket_path="/tmp/bdsh-networkd.sock"):
        self.socket_path = socket_path
        self.network = NetworkManager()
        self.server = None
        self.running = False

    def shutdown(self):
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

        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

    def _create_socket(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        self.server = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM
        )

        self.server.bind(self.socket_path)
        self.server.listen(10)

    def _handle_client(self, client):
        data = client.recv(65536)

        request = json.loads(
            data.decode("utf-8")
        )

        response = self._handle_request(request)

        client.sendall(
            json.dumps(response).encode("utf-8")
        )

    def _handle_request(self, request):
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        try:
            result = self._dispatch(
                method,
                params
            )

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
        if method == "hostname":
            return self.network.hostname()

        if method == "resolve":
            return self.network.resolve(
                params["hostname"]
            )

        if method == "interfaces":
            return {
                name: {
                    "flags": stats.flags,
                    "isup": stats.isup,
                    "duplex": stats.duplex,
                    "speed": stats.speed,
                    "mtu": stats.mtu,
                }
                for name, stats
                in self.network.interfaces().items()
            }

        if method == "interface_addresses":
            return {
                name: [
                    {
                        "family": address.family.name,
                        "address": address.address,
                        "netmask": address.netmask,
                        "broadcast": address.broadcast,
                    }
                    for address in addresses
                ]
                for name, addresses
                in self.network.interface_addresses().items()
            }

        raise ValueError(
            f"Unknown method: {method}"
        )
