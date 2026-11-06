"""Temporary Python file containing a list of system services.
Should be moved to a BPM package and read on boot.
"""

from bdsh.service import BadOSService
from bdsh.service.badlogon import BadLogonService
from bdsh.service.network import NetworkService


SYSTEM_SERVICES: list[type[BadOSService]] = [
    NetworkService,
    BadLogonService
]
