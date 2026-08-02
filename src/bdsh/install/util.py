import subprocess
import sys
from typing import Callable


def install_python_package(package_name: str, printfn = print):
    package_name = package_name.strip()
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        printfn("OK")
    except subprocess.CalledProcessError:
        printfn("FAILED")
        exit(0x81)


def prompt(query: str, on_cancel: Callable[[], None], **default: str):
    response = input((query + " [y/n] ") or default).lower()
    while response not in {'y', 'n'}:
        pass
    if response == 'n':
        on_cancel()


def print_header(header: str, printfn = print):
    printfn('\n' + f" {header} ".center(50, '='))


def print_task(task: str):
    print(task + '...', end=" ", flush=True)
