"""
Kernel entrypoint, run as PID 1 (/init).

Author: Logan Dhillon <dev@logandhillon.com>
"""

import os
import signal
import sys
import time

import bdsh
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

    BDSH_RESTART_DELAY = 1

    def __init__(self) -> None:
        self.shutdown_requested = False
        self.children_changed = False

        self.managed_processes: dict[int, str] = {}

        self.bin_python = "/usr/bin/python3"
        self.bin_bdsh = "/usr/bin/bdsh"

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

    def spawn(self, name: str, executable: str, *args: str) -> int:
        """Spawn a supervised child process.

        Args:
            name (str): process name
            executable (str): path or name of executable
            args (*str): cli args to pass to executable

        Returns:
            int: pid of forked process
        """

        if executable is None:
            executable = self.bin_python

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

    def spawn_py(self, name: str, *args: str, module: str | None = None) -> int:
        """Spawns a supervised Python interpreter running a specified file.

        Args:
            name (str): process name
            args (*str): cli args to pass to executable, first arg should be pyfile unless module is specified
            module (str, optional): specify a module to pass to the interpreter

        See also:
            BOSS#spawn
        """
        return self.spawn(name, self.bin_python, *(["-m", module] if module is not None else []), *args)

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

        if os.getpid() == 1:
            # init filesystem
            for path in bdsh.OSPaths.all():
                path.mkdir(parents=True, exist_ok=True)
        else:
            print("boss: warn: BadOS started as child process!\nskipping fs init...")
            self.bin_python = sys.executable
            self.bin_bdsh = bdsh.__path__[0]
            print(f"boss: set {self.bin_python=}, {self.bin_bdsh=}")

        # register signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGCHLD, self.handle_sigchld)

        # start shell
        shell_pid = self.spawn_py("bdsh", self.bin_bdsh)
        for service in SYSTEM_SERVICES:
            self.spawn_py(service.name,
                          f"{service.__module__}:{service.__qualname__}",
                          module="bdsh.service.executor")

        print("boss: system initialization complete")

        restart_at = None

        while not self.shutdown_requested:
            self.reap_children()  # always check for zombie children

            # restart shell if shell isn't found in proc list
            if shell_pid not in self.managed_processes:
                if restart_at is None:
                    restart_at = time.monotonic() + BOSS.BDSH_RESTART_DELAY

                elif time.monotonic() >= restart_at:
                    print("boss: restarting bdsh")

                    shell_pid = self.spawn_py("bdsh", self.bin_bdsh)

                    restart_at = None

            time.sleep(0.1)

        self.shutdown()

    def start_emulation_mode(self):
        raise NotImplementedError("fatal: emulation mode does not exist yet")


def main():
    BOSS().start_os()


if __name__ == "__main__":
    main()
