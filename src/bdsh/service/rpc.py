"""
An RPC service is a type of BadOS service that communicates over RPC using
internal UNIX sockets. 

These should be used for any service that requires any type of communication
(e.g. anything that's more than a background process.)

Author: Logan Dhillon <dev@logandhillon.com>
"""


import json
import socket
from pathlib import Path

from bdsh.service import BadOSService, ServiceUnavailableError
from bdsh.util.serializing import validate_json_value


def _socket_path(proc):
    """Defines the UNIX socket path for a given process."""
    # TODO: this is like this so i can run it on my dev machine, change it for real OS
    return f"/tmp/{proc}.sock"


class RPCSocketService(BadOSService, name=None):
    """An RPC service is a type of BadOS service that communicates over RPC using
    internal UNIX sockets.

    The service is the "server" that responds to RPC requests.
    """

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
        """Starts running this socket, listening for incoming client connections and
        handling them via _handle_client.
        """
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

    def _handle_client(self, client: socket.socket):
        """Handles an incoming client connection, sending the data it receives on the
        connection to _handle_request

        Args:
            client (socket): the socket of the client connection
        """
        req = json.loads(client.recv(65536).decode("utf-8"))
        validate_json_value(req, "request")
        res = self._handle_request(req)

        validate_json_value(res, "response")
        client.sendall(json.dumps(res).encode("utf-8"))

    def _handle_request(self, request):
        """Handles an incomming request from an RPC client

        Args:
            request (any): JSON-formatted request data from client

        Returns:
            dict[str, object]: id and message (or error) from usptream dispatched method
        """
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

    def dispatch(self, method: str, params: dict[str, object]):
        """Given the provided method name, this finds the corresponding method, dispatches
        it, and returns the value of the given method. This will only run methods marked
        with @servicemethod.

        Args:
            method (str): name of method to dispatch
            params (dict[str, object]): parameters to pass to dispatched method

        Raises:
            ValueError: if the service method does not exist (or isn't marked with @servicemethod)

        Returns:
            unknown: return value of dispatched method
        """
        handler = getattr(self, method, None)

        if handler is None or not getattr(handler, "_is_service_method", False):
            raise ValueError(f"service method does not exist: '{method}'")

        return handler(**params)


def servicemethod(func):
    """Marks a method as a "service method," meaning it will be available for request via RPC."""
    func._is_service_method = True  # pylint: disable=protected-access
    return func


class RPCError(Exception):
    """Generic error used for upstream errors on an RPC service"""

    def __init__(self, msg: str, *, err_type: str | None = None):
        super().__init__(f"{err_type or "generic error"}: {msg}")


class RPCSocketClient:
    """An RPC service is a type of BadOS service that communicates over RPC using
    internal UNIX sockets.

    The client requests operations from the service it is created for.
    """

    def __init__(self, proc_name: str):
        self.socket_path = _socket_path(proc_name)
        self._request_id = 0

    def request(self, method: str, params: dict[str, object] | None = None):
        """Requests an operation from the service this client was created for.

        Args:
            method (str): the name of the method to request
            params (dict[str, object], optional): named dictionary of the parameters to include in the request

        Raises:
            ServiceUnavailableError: if the requested service is unavailable or does not exist
            RPCError: if an error happened upstream and was communicated back
            OSError: other I/O error that occured during socket communication

        Returns:
            any, optional: the response from the service operation
        """
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
                raise ServiceUnavailableError(self.socket_path) from e

            raise e
        finally:
            sock.close()

        response = json.loads(data.decode())
        validate_json_value(response, "response")

        if "error" in response:
            raise RPCError(response["error"]["message"],
                           err_type=response["error"]["type"])

        return response["msg"]
