from threading import Thread

from bdsh.service.network.service import NetworkService

_SYSTEM_SERVICES = [
    NetworkService
]


def dispatch_system_services():
    for cls in _SYSTEM_SERVICES:
        srv = cls()
        Thread(target=srv.start, daemon=True, name=srv.name).start()
