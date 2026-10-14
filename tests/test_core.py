"""
Unit tests for bdsh paths, sessions, and shell behavior.

Author: Logan Dhillon <dev@logandhillon.com>
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

import bdsh
from bdsh import session as session_module
from bdsh.shell import Shell
from bdsh.service.badlogon import User


def test_get_shell_path_joins_paths_to_shell_root(monkeypatch, tmp_path):
    """Resolve supplied path segments beneath the configured shell root."""
    monkeypatch.setattr(bdsh, "_ROOT_DIR", tmp_path)

    assert bdsh.get_shell_path("prf", "alice") == tmp_path / "prf" / "alice"


def test_os_paths_all_returns_configured_path_constants():
    """Expose each configured filesystem location as a Path."""
    paths = bdsh.OSPaths.all()

    assert paths == [
        bdsh.OSPaths.ROOT,
        bdsh.OSPaths.APPLICATIONS,
        bdsh.OSPaths.CONFIGS,
        bdsh.OSPaths.EXECUTABLES,
        bdsh.OSPaths.PROFILES,
    ]
    assert all(isinstance(path, Path) for path in paths)


def test_session_rejects_missing_user():
    """Prevent constructing a session without an authenticated user."""
    with pytest.raises(ValueError, match="cannot create userless session"):
        session_module.Session(Mock(), None)


def test_session_initializes_user_paths_environment_and_running_state(monkeypatch, tmp_path):
    """Initialize session state and derive the user's home from the shell root."""
    user = User("alice", "hash")
    io = Mock()
    monkeypatch.setattr(session_module, "get_shell_path", lambda *parts: tmp_path.joinpath(*parts))
    monkeypatch.setattr(session_module, "register_commands", lambda session: {"test": session})
    monkeypatch.setenv("PYTHONPATH", "previous-path")

    session = session_module.Session(io, user)

    assert session.io is io
    assert session.get_user() is user
    assert session.is_logged_in()
    assert session.userhome == tmp_path / "prf" / "alice"
    assert session.cwd == tmp_path
    assert session.env["PYTHONPATH"] == str(Path(session_module.__file__).resolve().parent)
    assert session.commands == {"test": session}
    assert session.definitions == {"ls": "ld", "dir": "ld", "cd": "go"}
    assert not session.is_running


def test_session_chdir_resolves_path_and_running_flag_can_be_changed(tmp_path):
    """Update the current directory and shell-running flag."""
    session = SimpleNamespace(cwd=None, is_running=False)
    path = tmp_path / "nested"
    path.mkdir()

    session_module.Session.chdir(session, path)
    session_module.Session.set_is_running(session, True)

    assert session.cwd == path.resolve()
    assert session.is_running


def test_shell_execute_dispatches_alias_with_original_arguments():
    """Expand a command alias before dispatching the resulting command."""
    command = Mock()
    shell = Shell(SimpleNamespace(
        definitions={"ll": "ld"},
        commands={"ld": command},
        io=Mock(),
    ))

    shell.execute("ll /tmp")

    assert command.execute.call_args_list == [call(["ld", "/tmp"])]


def test_shell_execute_reports_unknown_command():
    """Display a useful message for commands with no registered executable."""
    io = Mock()
    shell = Shell(SimpleNamespace(definitions={}, commands={}, io=io))

    shell.execute("missing")

    assert io.println.call_args_list == [call("invalid command: missing")]


def test_shell_execute_reports_command_exceptions_without_raising():
    """Keep command failures in the shell's user-facing output."""
    command = Mock()
    command.execute.side_effect = RuntimeError("bad argument")
    io = Mock()
    shell = Shell(SimpleNamespace(
        definitions={},
        commands={"run": command},
        io=io,
    ))

    shell.execute("run value")

    assert io.print.call_args_list == [call("run: bad argument")]


def test_shell_prompt_uses_tilde_for_user_home():
    """Render the user's home as '~' and preserve the shell prompt format."""
    user = User("alice", "hash")
    home = Path("/shell/prf/alice")
    shell = Shell(SimpleNamespace(
        cwd=home,
        userhome=home,
        get_user=lambda: user,
    ))

    assert shell.get_prompt() == f"{bdsh.NL}alice:~$ "


def test_shell_process_input_executes_line_and_clears_buffer():
    """Submit a buffered command on carriage return and reset the buffer."""
    io = Mock()
    io.read.return_value = "\r"
    shell = Shell(SimpleNamespace(io=io))
    shell.execute = Mock()
    buffer = ["e", "c", "h", "o", " ", "hi"]

    shell._process_input(buffer)

    assert shell.execute.call_args_list == [call("echo hi")]
    assert buffer == []
    assert io.print.call_args_list == [call("\n")]


def test_shell_process_input_backspace_removes_last_character():
    """Erase one buffered character and emit the terminal erase sequence."""
    io = Mock()
    io.read.return_value = "\x7f"
    shell = Shell(SimpleNamespace(io=io))
    buffer = ["a", "b"]

    shell._process_input(buffer)

    assert buffer == ["a"]
    assert io.print.call_args_list == [call("\x08 \x08")]
