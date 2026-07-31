import os

from .__version__ import __version__

NL = '\r\n'
ROOT_DIR = os.path.abspath('bdsh')
SHELL_COPYRIGHT = f"BadOS Dynamic Shell (v{__version__}){NL}(c) Bad Technologies. All rights reserved.{NL}"


def get_shell_path(*paths: str):
    path = os.path.abspath(os.path.join(ROOT_DIR, *paths))
    return path if path.startswith(ROOT_DIR) else ROOT_DIR
