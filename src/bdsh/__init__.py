"""
BadOS Dynamic Shell (bdsh) is a dynamic Python-based shell designed for BadOS.
It is designed around modularity and compatibility with third-party libraries.

This is the root of the bdsh package, and provides basic constants that may be
used around the codebase.

Author: Logan Dhillon <dev@logandhillon.com>
"""

from pathlib import Path
from typing import Final

from .__version__ import __version__

NL = '\r\n'
_ROOT_DIR = Path("bdsh").resolve()
SHELL_COPYRIGHT = f"BadOS Dynamic Shell (v{__version__}){NL}(c) Bad Technologies. All rights reserved.{NL}"


def get_shell_path(*paths: str):
    return _ROOT_DIR.joinpath(*paths)


class OSPaths:
    """Provides a namespace to access OS paths (e.g. /app, /cfg)"""

    ROOT: Final[Path] = _ROOT_DIR

    APPLICATIONS: Final[Path] = get_shell_path("app")
    CONFIGS: Final[Path] = get_shell_path("cfg")
    EXECUTABLES: Final[Path] = get_shell_path("exec")
    PROFILES: Final[Path] = get_shell_path("prf")

    @classmethod
    def all(cls) -> list[Path]:
        return [value for value in vars(cls).values() if isinstance(value, Path)]
