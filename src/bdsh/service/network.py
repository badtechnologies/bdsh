"""
The network service controls on-device network drivers, provides information
about device interfaces, and allows mangement of said interfaces.

Author: Logan Dhillon <dev@logandhillon.com>
"""


import socket
from abc import ABC, abstractmethod

import psutil

from bdsh.service.rpc import RPCSocketClient, RPCSocketService, servicemethod


class NetworkAPI(ABC):
    """The API which this service's accessors (e.g. clients and servers) must implement."""
    @abstractmethod
    def hostname(self) -> str: ...

    @abstractmethod
    def interfaces(self) -> dict: ...

    @abstractmethod
    def interface_addresses(self) -> dict: ...

    @abstractmethod
    def resolve(self, hostname: str) -> str: ...


class NetworkClient(RPCSocketClient, NetworkAPI):
    """The network service controls on-device network drivers.

    This class allows usage of/communication with the service.
    """

    def __init__(self):
        super().__init__("network.sys")

    def hostname(self) -> str:
        return self.request("hostname")

    def interfaces(self) -> dict:
        return self.request("interfaces")

    def interface_addresses(self) -> dict:
        return self.request("interface_addresses")

    def resolve(self, hostname: str) -> str:
        return self.request("resolve", {hostname: hostname})


class NetworkService(RPCSocketService, NetworkAPI, name="network.sys"):
    """The network service controls on-device network drivers."""
    @servicemethod
    def hostname(self):
        return socket.gethostname()

    @servicemethod
    def resolve(self, hostname: str) -> str:
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
