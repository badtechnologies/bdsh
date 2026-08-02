from pathlib import Path
from typing import Final

from .__version__ import __version__

NL = '\r\n'
SHELL_COPYRIGHT = f"BadOS Dynamic Shell (v{__version__}){NL}(c) Bad Technologies. All rights reserved.{NL}"


def get_shell_path(*paths: str):
    return OSPaths.ROOT.joinpath(*paths)


class OSPaths:
    ROOT: Final[Path] = Path("bdsh").resolve()

    APPLICATIONS: Final[Path] = get_shell_path("app")
    CONFIGS: Final[Path] = get_shell_path("cfg")
    EXECUTABLES: Final[Path] = get_shell_path("exec")
    PROFILES: Final[Path] = get_shell_path("prf")

    @classmethod
    def all(cls) -> list[Path]:
        return [value for value in vars(cls).values()]
