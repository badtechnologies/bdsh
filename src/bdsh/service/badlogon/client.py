from bdsh.service.rpc import RPCSocketClient


class BadLogonClient(RPCSocketClient):
    def __init__(self):
        super().__init__("badlogon.sys")
