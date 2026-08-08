from bdsh.service.rpc import RPCSocketClient


class NetworkClient(RPCSocketClient):
    def __init__(self):
        super().__init__("network.badproc")
