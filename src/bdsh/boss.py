"""
Kernel entrypoint, run as PID 1 (/init).

Author: Logan Dhillon <dev@logandhillon.com>
"""

import os
import signal
import time

from bdsh import OSPaths
from bdsh.service.system import SYSTEM_SERVICES


class BOSS:
    """BOSS is the system supervisor and boot sequence for BadOS.
    Alongside managing the BDSH shell, it can spawn and supervise
    other processes, allowing it to operate as a service supervisor.

    Raises:
        RuntimeError: if BOSS is started not as PID 1

    See Also:
        bdsh.command.boss: command interface for service mgmt.
        bdsh.shell: managed shell process that the user sees
    """

    BIN_PYTHON = "/usr/bin/python3"
    BIN_BDSH = "/usr/bin/bdsh"
    BDSH_RESTART_DELAY = 2

    def __init__(self) -> None:
        self.shutdown_requested = False
        self.children_changed = False

        self.managed_processes: dict[int, str] = {}

    def handle_shutdown(self, _signum, _frame):
        self.shutdown_requested = True

    def handle_sigchld(self, _signum, _frame):
        self.children_changed = True

    def reap_children(self):
        """Reap all terminated child processes."""
        self.children_changed = False

        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)

                if pid == 0:
                    break

                process_name = self.managed_processes.pop(pid, "unknown")

                print(
                    f"boss: process {process_name} (pid {pid}) exited with status {status}")

            except ChildProcessError:
                break

            except InterruptedError:
                continue

    def spawn(self, name: str, executable: str, args: list[str] | None = None):
        """Spawn a supervised child process."""

        if args is None:
            args = []

        pid = os.fork()

        if pid == 0:
            try:
                # reset signal handlers to default
                signal.signal(signal.SIGCHLD, signal.SIG_DFL)
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
                signal.signal(signal.SIGINT, signal.SIG_DFL)

                os.execv(executable, [executable, *args])

            except Exception:  # pylint: disable=broad-exception-caught
                os._exit(127)

        self.managed_processes[pid] = name

        return pid

    def shutdown(self):
        """Perform a controlled system shutdown."""

        print("boss: shutting down")

        # gracefullly kill every managed proc
        for pid in list(self.managed_processes):
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        # deadline for processes on deathrow to kill themselves
        deadline = time.monotonic() + 10
        while self.managed_processes and time.monotonic() < deadline:
            self.reap_children()
            time.sleep(0.1)

        # once all deadlines pass, forcefully kill all managed proc
        for pid in list(self.managed_processes):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        # reap zombie children
        while True:
            self.reap_children()

            if not self.managed_processes:
                break

            time.sleep(0.1)

    def start_os(self):
        """Initialize and supervise the operating system."""

        if os.getpid() != 1:
            print("WARN: BadOS started as child process!\nstarting emulation mode...")
            self.start_emulation_mode()

        # init filesystem
        for path in OSPaths.all():
            path.mkdir(parents=True, exist_ok=True)

        # register signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGCHLD, self.handle_sigchld)

        print("boss: system initialization complete")

        # start shell
        shell_pid = self.spawn("bdsh", BOSS.BIN_PYTHON, [BOSS.BIN_BDSH])
        for service in SYSTEM_SERVICES:
            self.spawn(service.name, BOSS.BIN_PYTHON, ["-m", "bdsh.service.executor", f"{service.__module__}:{service.__qualname__}"])

        restart_at = None

        while not self.shutdown_requested:
            self.reap_children()  # always check for zombie children

            # restart shell if shell isn't found in proc list
            if shell_pid not in self.managed_processes:
                if restart_at is None:
                    restart_at = time.monotonic() + BOSS.BDSH_RESTART_DELAY

                elif time.monotonic() >= restart_at:
                    print("boss: restarting bdsh")

                    shell_pid = self.spawn(
                        "bdsh", BOSS.BIN_PYTHON, [BOSS.BIN_BDSH])

                    restart_at = None

            time.sleep(0.1)

        self.shutdown()

    def start_emulation_mode(self):
        raise NotImplementedError("fatal: emulation mode does not exist yet")


def main():
    BOSS().start_os()


if __name__ == "__main__":
    main()
