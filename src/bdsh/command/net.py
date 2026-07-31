from typing import List

from bdsh.command import Command
from bdsh.network import NetworkManager


class NetCommand(Command):
    def execute(self, args: List[str]):
        interfaces = NetworkManager.interfaces()
        addrs = NetworkManager.interface_addresses()

        if len(args) > 1:
            if_name = args[1]
            if not interfaces.get(if_name):
                raise ValueError(f"interface {if_name} does not exist")

            interfaces = {if_name: interfaces[if_name]}
            addrs = {if_name: addrs[if_name]}


        for interface, stats in interfaces.items():
            msg = f"{interface}: flags={stats.flags} mtu {stats.mtu}"

            ifaddrs = addrs.get(interface)
            if ifaddrs:
                for addr in ifaddrs:
                    msg += f"\n\t{addr.family.name} {addr.address}"
                    if addr.netmask:
                        msg += f" netmask {addr.netmask}"
                    if addr.broadcast:
                        msg += f" broadcast {addr.broadcast}"
                    elif addr.ptp:
                        msg += f" ptp {addr.ptp}"

            print(msg)

    def help(self) -> str:
        return "displays network interface info, specify an interface with a second argument"
