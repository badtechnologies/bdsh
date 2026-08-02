import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Never

from bdsh import get_shell_path


def load_exec(path: Path) -> ModuleType | Never:
    loader = SourceFileLoader("bdsh_exec", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)

    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load executable: {path}")

    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def get_exec_path(executable: str) -> Path | None:
    for root, dirs, files in Path.walk(get_shell_path("exec")):
        if executable in files:
            return root.joinpath(executable)

    return None
