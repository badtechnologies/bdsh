"""
Unit tests for terminal abstractions and console forwarding.

Author: Logan Dhillon <dev@logandhillon.com>
"""

from unittest.mock import Mock, call

import bdsh
import bdsh.io.console as console_module
from bdsh.io import TerminalIO
from bdsh.io.console import ConsoleTerminal


class MemoryTerminal(TerminalIO):
    """Capture writes made through the shared terminal convenience methods."""

    def __init__(self, interactive=False):
        self.output = []
        self.flush_count = 0
        self.interactive = interactive

    def read(self, size=-1):
        return ""

    def readline(self):
        return "input"

    def write(self, text):
        self.output.append(text)

    def flush(self):
        self.flush_count += 1

    def close(self):
        pass

    def get_size(self):
        return (24, 80)

    def is_interactive(self):
        return self.interactive


def test_terminal_print_methods_write_and_flush():
    """Flush both plain output and newline-terminated output immediately."""
    terminal = MemoryTerminal()

    terminal.print("value")
    terminal.println("line")

    assert terminal.output == ["value", f"line{bdsh.NL}"]
    assert terminal.flush_count == 2


def test_terminal_input_writes_prompt_before_reading():
    """Display an input prompt and return the terminal's next line."""
    terminal = MemoryTerminal()

    result = terminal.input("Name: ")

    assert terminal.output == ["Name: "]
    assert result == "input"
    assert terminal.flush_count == 1


def test_terminal_bell_writes_bell_character():
    """Send the terminal bell control character and flush it."""
    terminal = MemoryTerminal()

    terminal.bell()

    assert terminal.output == ["\a"]
    assert terminal.flush_count == 1


def test_terminal_clear_and_title_are_noops_when_not_interactive():
    """Avoid emitting terminal escape sequences to redirected output."""
    terminal = MemoryTerminal(interactive=False)

    terminal.clear()
    terminal.set_title("bdsh")

    assert terminal.output == []
    assert terminal.flush_count == 0


def test_terminal_clear_and_title_emit_sequences_when_interactive():
    """Emit expected terminal control sequences only for an interactive terminal."""
    terminal = MemoryTerminal(interactive=True)

    terminal.clear()
    terminal.set_title("bdsh")

    assert terminal.output == ["\033[H\033[2J", "\033]0;bdsh\007"]
    assert terminal.flush_count == 2


def test_console_terminal_forwards_stream_operations(monkeypatch):
    """Forward reads, writes, flushes, and interactivity checks to standard streams."""
    stdin = Mock()
    stdin.read.return_value = "x"
    stdin.isatty.return_value = True
    stdout = Mock()
    stdout.isatty.return_value = True
    monkeypatch.setattr(console_module.sys, "stdin", stdin)
    monkeypatch.setattr(console_module.sys, "stdout", stdout)
    terminal = ConsoleTerminal()

    assert terminal.read(1) == "x"
    terminal.write("hello")
    terminal.flush()
    assert terminal.is_interactive()

    assert stdin.read.call_args_list == [call(1)]
    assert stdout.write.call_args_list == [call("hello")]
    assert stdout.flush.call_args_list == [call()]


def test_console_terminal_readline_uses_builtin_input(monkeypatch):
    """Read a line from the console using Python's input function."""
    input_fn = Mock(return_value="typed")
    monkeypatch.setattr("builtins.input", input_fn)

    assert ConsoleTerminal().readline() == "typed"
    assert input_fn.call_args_list == [call()]
