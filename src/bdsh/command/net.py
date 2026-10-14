import argparse
import socket

from bdsh.command import Command
from bdsh.service.network import NetworkClient


class NetCommand(Command):
    def execute(self, args: list[str]):
        client = NetworkClient()
        interfaces = client.interfaces()
        addrs = client.interface_addresses()

        if len(args) > 1:
            if_name = args[1]
            if not interfaces.get(if_name):
                raise ValueError(f"interface {if_name} does not exist")

            interfaces = {if_name: interfaces[if_name]}
            addrs = {if_name: addrs[if_name]}

        for interface, stats in interfaces.items():
            if not isinstance(stats, dict):
                raise TypeError("cannot lookup interface stats")

            msg = f"{interface}: flags={stats["flags"]} mtu {stats["mtu"]}"

            raw_addrs = addrs.get(interface)
            if not isinstance(raw_addrs, list):
                raise TypeError("cannot index ifaddrs")
            ifaddrs: list[dict[str, str]] = raw_addrs  # pyright: ignore

            if ifaddrs:
                for addr in ifaddrs:
                    msg += f"\n\t{addr["family"]} {addr["address"]}"

                    if addr.get("netmask"):
                        msg += f" netmask {addr["netmask"]}"

                    if addr.get("broadcast"):
                        msg += f" broadcast {addr["broadcast"]}"
                    elif addr.get("ptp"):
                        msg += f" ptp {addr["ptp"]}"

            self.session.io.println(msg)

    def help(self) -> str:
        return "displays network interface info, specify an interface with a second argument"


class HostnameCommand(Command):
    def execute(self, args: list[str]):
        self.session.io.println(NetworkClient().hostname())

    def help(self) -> str:
        return "displays the current system hostname"


class PingCommand(Command):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('host', type=str, help='host to ping')
    parser.add_argument('-c', '--count', type=int, default=4,
                        help='amount of packets to send')
    parser.add_argument('-t', '--timeout', type=int,
                        default=2, help='seconds to timeout')
    parser.add_argument('-s', '--size', type=int,
                        default=56, help='bytes to send')

    def execute(self, args: list[str]):
        try:
            cfg = self.parser.parse_args(args[1:])
        except SystemExit:
            return

        # TODO: install this into kernel or something so i can just import it :P
        from icmplib import ping

        try:
            host = NetworkClient().resolve(hostname=cfg.host)
        except socket.gaierror as e:
            raise ValueError(f"failed to resolve host: \"{cfg.host}\"") from e

        self.session.io.println(
            f"pinging {cfg.host} ({host}) with {cfg.size} bytes")
        received = 0
        for i in range(cfg.count):
            self.session.io.print(f"icmp_seq {i}... ")
            ok = ping(cfg.host, count=1, timeout=cfg.timeout,
                      payload_size=cfg.size, privileged=False)
            self.session.io.println("OK" if ok else "TIMEOUT")
            if ok:
                received += 1

        self.session.io.println(
            f"{cfg.count} packets sent, {received} packets received, {round((1 - received / cfg.count) * 100, 1)}% packet loss")

    def help(self) -> str:
        return self.parser.format_help()
