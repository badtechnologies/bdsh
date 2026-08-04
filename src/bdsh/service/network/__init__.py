import socket

import psutil

from bdsh.service.ipc import IPCSocketService


class NetworkService(IPCSocketService, name="network.badproc"):
    def dispatch(self, method, params):
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
