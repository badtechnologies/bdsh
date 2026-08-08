import socket
from typing import Protocol

import psutil

from bdsh.service.rpc import RPCSocketService, servicemethod


class NetworkAPI(Protocol):
    def hostname(self) -> str: ...

    def interfaces(self) -> dict: ...

    def interface_addresses(self) -> dict: ...

    def resolve(self, hostname: str) -> str: ...


class NetworkService(RPCSocketService, NetworkAPI, name="network.badproc"):
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
