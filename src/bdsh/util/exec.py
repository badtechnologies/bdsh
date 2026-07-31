import importlib.util
import os
from importlib.machinery import SourceFileLoader

from bdsh import get_shell_path


def load_exec(path: str):
    loader = SourceFileLoader("bdsh_exec", path)
    spec = importlib.util.spec_from_loader(loader.name, loader)

    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load executable: {path}")

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def get_exec_path(executable: str) -> str | None:
    base = get_shell_path("exec")

    for root, dirs, files in os.walk(base):
        if executable in files:
            return os.path.join(root, executable)

    return None
