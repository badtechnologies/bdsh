import os

from .__version__ import __version__

NL = '\r\n'
ROOT_DIR = os.path.abspath('bdsh')


def get_bdsh_path(*paths: str):
    path = os.path.abspath(os.path.join(ROOT_DIR, *paths))
    return path if path.startswith(ROOT_DIR) else ROOT_DIR
