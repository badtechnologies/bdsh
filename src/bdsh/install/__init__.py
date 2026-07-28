from enum import Enum


class InstallType(Enum):
    STANDARD = "std"  # standard bdsh installation
    SYSTEM = "sys"  # system-wide bdsh installation; made for BadOS Shell System

    @staticmethod
    def display():
        for t in InstallType:
            print(f"\t> {t.value} ({t.name})")
