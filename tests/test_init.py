import io
import os
import unittest
from pathlib import Path
from unittest.mock import call, patch

from bdsh.init import BootShell, reap_children


class BootShellTests(unittest.TestCase):
    def make_shell(self, commands: str = "") -> tuple[BootShell, io.StringIO]:
        output = io.StringIO()
        shell = BootShell(stdin=io.StringIO(commands), stdout=output)
        shell.use_rawinput = False
        return shell, output

    def test_exit_does_not_stop_command_loop(self) -> None:
        shell, output = self.make_shell("exit\npwd\n")

        shell.cmdloop()

        self.assertIn("exit is disabled", output.getvalue())
        self.assertIn("/", output.getvalue())

    def test_shell_starts_at_absolute_root(self) -> None:
        shell, _ = self.make_shell()

        self.assertEqual(shell.cwd, Path("/"))

    def test_checkpid_prints_current_process_id(self) -> None:
        shell, output = self.make_shell()

        with patch("bdsh.init.os.getpid", return_value=1):
            shell.do_checkpid("")

        self.assertEqual(output.getvalue(), "1\n")

    def test_reaper_waits_until_no_children_are_ready(self) -> None:
        with patch("bdsh.init.os.waitpid", side_effect=[(123, 0), (0, 0)]) as waitpid:
            reap_children(0, None)

        self.assertEqual(waitpid.call_args_list, [call(-1, os.WNOHANG), call(-1, os.WNOHANG)])


if __name__ == "__main__":
    unittest.main()
