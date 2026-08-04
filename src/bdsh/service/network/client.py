from bdsh.service.ipc import IPCSocketClient


class NetworkClient(IPCSocketClient):
    def __init__(self):
        super().__init__("network.badproc")

    def hostname(self):
        return self.request("hostname")

    def interfaces(self):
        return self.request("interfaces")

    def interface_addresses(self):
        return self.request("interface_addresses")

    def resolve(self, hostname):
        return self.request("resolve", {"hostname": hostname})
