import socket

import psutil


class NetworkManager:
    @staticmethod
    def hostname():
        return socket.gethostname()

    @staticmethod
    def interfaces():
        return psutil.net_if_stats()

    @staticmethod
    def interface_addresses():
        return psutil.net_if_addrs()

    @staticmethod
    def resolve(hostname):
        return socket.gethostbyname(hostname)
