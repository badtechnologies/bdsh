import socket

import psutil

from bdsh.service.rpc import RPCSocketService, RPCSocketClient, servicemethod


class NetworkService(RPCSocketService, name="network.badproc"):
    @servicemethod
    def hostname(self):
        return socket.gethostname()

    @servicemethod
    def resolve(self, hostname: str):
        return socket.gethostbyname(hostname)

    @servicemethod
    def interfaces(self):
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

    @servicemethod
    def interface_addresses(self):
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


class NetworkClient(RPCSocketClient):
    def __init__(self):
        super().__init__("network.badproc")
