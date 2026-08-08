from bdsh.service.badlogon import BadLogonAPI
from bdsh.service.rpc import RPCSocketClient


class BadLogonClient(RPCSocketClient, BadLogonAPI):
    def __init__(self): ...
