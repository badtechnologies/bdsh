"""
Unit tests for built-in shell commands.

Author: Logan Dhillon <dev@logandhillon.com>
"""

from pathlib import Path
from unittest.mock import Mock, call

import pytest

from bdsh.command import AnonymousCommand, Command
from bdsh.command.commands import (DefineCommand, GoCommand, HelpCommand,
                                   ListDirectoryCommand, PeekCommand)
from bdsh.service.badlogon import User
from bdsh.session import Session


def make_session(cwd: Path, userhome: Path | None = None):
    """Create a small session-shaped object for command unit tests."""
    session = Session(io=Mock(), user=User("test", ""))

    setattr(session, "chdir", Mock(
        side_effect=lambda path: setattr(session, "cwd", path)))
    setattr(session, "cwd", cwd)
    setattr(session, "userhome", userhome)

    return session


def test_define_command_rejects_missing_definition(tmp_path):
    """Require both an alias name and a command body."""
    session = make_session(tmp_path)

    with pytest.raises(ValueError, match="missing params"):
        DefineCommand(session).execute(["def", "ll"])


def test_define_command_stores_definition_and_reports_it(tmp_path):
    """Store a multi-token command definition and confirm it to the user."""
    session = make_session(tmp_path)
    command = DefineCommand(session)

    command.execute(["def", "ll", "ld", "-a"])

    assert ("ll", "ld -a") in session.definitions.items()
    assert session.io.println.call_args_list == [
        call("defined 'll' to run 'ld -a'")
    ]


def test_define_command_rejects_alias_that_defines_itself(tmp_path):
    """Reject an alias whose complete definition is identical to its name."""
    session = make_session(tmp_path)

    with pytest.raises(ValueError, match="keyword cannot be the same"):
        DefineCommand(session).execute(["def", "ll", "ll"])


def test_go_command_changes_to_child_directory(tmp_path):
    """Resolve a child directory relative to the session's current directory."""
    child = tmp_path / "child"
    child.mkdir()
    session = make_session(tmp_path)

    GoCommand(session).execute(["go", "child"])

    assert session.chdir.call_args_list == [call(child)]


def test_go_command_uses_home_for_tilde(tmp_path):
    """Treat '~' as the user's home rather than a literal child path."""
    home = tmp_path / "home"
    home.mkdir()
    session = make_session(tmp_path, userhome=home)

    GoCommand(session).execute(["go", "~"])

    assert session.chdir.call_args_list == [call(home)]


def test_go_command_rejects_non_directory(tmp_path):
    """Raise a path-specific error when the requested folder is absent."""
    session = make_session(tmp_path)

    with pytest.raises(FileNotFoundError, match="absent: no such folder"):
        GoCommand(session).execute(["go", "absent"])


def test_list_directory_lists_entries_and_marks_subdirectories(tmp_path):
    """Include each immediate entry and distinguish directories with a slash."""
    (tmp_path / "folder").mkdir()
    (tmp_path / "file.txt").write_text("content", encoding="utf-8")
    session = make_session(tmp_path)

    ListDirectoryCommand(session).execute(["ld"])

    entries = set(session.io.println.call_args.args[0].split("\t"))
    assert entries == {"folder/", "file.txt"}


def test_list_directory_reports_missing_directory(tmp_path):
    """Translate an absent listing target into the command's path-specific error."""
    session = make_session(tmp_path)

    with pytest.raises(FileNotFoundError, match="missing: does not exist"):
        ListDirectoryCommand(session).execute(["ld", "missing"])


def test_peek_command_prints_file_contents(tmp_path):
    """Read and print the requested file without altering its contents."""
    source = tmp_path / "notes.txt"
    source.write_text("first line\nsecond line", encoding="utf-8")
    session = make_session(tmp_path)

    PeekCommand(session).execute(["peek", "notes.txt"])

    assert session.io.println.call_args_list == [
        call("first line\nsecond line")]


def test_peek_command_rejects_missing_file(tmp_path):
    """Raise a specific error when the requested file cannot be read."""
    session = make_session(tmp_path)

    with pytest.raises(FileNotFoundError, match="missing: no such file"):
        PeekCommand(session).execute(["peek", "missing"])


def test_help_command_displays_selected_command_help(tmp_path):
    """Show the help text belonging to the requested command."""
    session = make_session(tmp_path)
    command = AnonymousCommand(session, lambda _: None, "prints a value")
    session.commands = {"echo": command}

    HelpCommand(session).execute(["help", "echo"])

    assert session.io.println.call_args_list == [
        call("help: echo: prints a value")
    ]


def test_help_command_rejects_unknown_command(tmp_path):
    """Avoid silently displaying help for an unregistered command."""
    session = make_session(tmp_path)

    with pytest.raises(TypeError, match="unknown is not a valid command"):
        HelpCommand(session).execute(["help", "unknown"])


def test_anonymous_command_runs_callback_and_returns_help_text(tmp_path):
    """Adapt a callback into the standard command interface."""
    callback = Mock()
    command = AnonymousCommand(make_session(
        tmp_path), callback, "callback help")
    args = ["custom", "value"]

    command.execute(args)

    assert callback.call_args_list == [call(args)]
    assert command.help() == "callback help"


def test_command_base_cannot_be_instantiated_without_implementations(tmp_path):
    """Enforce implementation of the command execution/help interface."""
    with pytest.raises(TypeError):
        Command(make_session(tmp_path))
