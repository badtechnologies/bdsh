import argparse
import socket
from typing import List

from icmplib import ping

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

            self.session.io.println(msg)

    def help(self) -> str:
        return "displays network interface info, specify an interface with a second argument"


class HostnameCommand(Command):
    def execute(self, args: List[str]):
        self.session.io.println(NetworkManager.hostname())

    def help(self) -> str:
        return "displays the current system hostname"


class PingCommand(Command):
    parser = argparse.ArgumentParser(color=False, add_help=False)
    parser.add_argument('host', type=str, help='host to ping')
    parser.add_argument('-c', '--count', type=int, default=4, help='amount of packets to send')
    parser.add_argument('-t', '--timeout', type=int, default=2, help='seconds to timeout')
    parser.add_argument('-s', '--size', type=int, default=56, help='bytes to send')

    def execute(self, args: List[str]):
        try:
            args = self.parser.parse_args(args[1:])
        except SystemExit:
            return

        try:
            host = NetworkManager.resolve(args.host)
        except socket.gaierror:
            raise ValueError(f"failed to resolve host: \"{args.host}\"")

        self.session.io.println(f"pinging {args.host} ({host}) with {args.size} bytes")
        received = 0
        for i in range(args.count):
            self.session.io.print(f"icmp_seq {i}... ")
            ok = ping(args.host, count=1, timeout=args.timeout, payload_size=args.size, privileged=False)
            self.session.io.println("OK" if ok else "TIMEOUT")
            if ok: received += 1

        self.session.io.println(
            f"{args.count} packets sent, {received} packets received, {round((1 - received / args.count) * 100, 1)}% packet loss")

    def help(self) -> str:
        return self.parser.format_help()
