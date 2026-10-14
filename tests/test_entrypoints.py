"""
Unit tests for interactive shell and service entrypoints.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import sys
from unittest.mock import Mock, call

from bdsh import __main__ as shell_entrypoint
from bdsh.service import __main__ as service_entrypoint
from bdsh.service.badlogon import User


def test_shell_login_retries_invalid_credentials_then_returns_user(monkeypatch, capsys):
    """Retry rejected credentials and return the serialized user after success."""
    client = Mock()
    client.get_user_by_credentials.side_effect = [
        None,
        {"username": "alice", "password_hash": "stored-hash"},
    ]
    monkeypatch.setattr(shell_entrypoint, "BadLogonClient", Mock(return_value=client))
    username = Mock(side_effect=["alice", "alice"])
    password = Mock(side_effect=["wrong", "correct"])
    monkeypatch.setattr("builtins.input", username)
    monkeypatch.setattr(shell_entrypoint, "getpass", password)

    user = shell_entrypoint.shell_login()

    assert user == User("alice", "stored-hash")
    assert client.get_user_by_credentials.call_args_list == [
        call(username="alice", password="wrong"),
        call(username="alice", password="correct"),
    ]
    assert username.call_count == 2
    assert password.call_count == 2
    assert "Invalid login" in capsys.readouterr().out


def test_shell_entrypoint_starts_shell_and_restores_working_directory(monkeypatch):
    """Start an authenticated shell and restore the initial process directory."""
    user = User("alice", "hash")
    shell = Mock()
    monkeypatch.setattr(shell_entrypoint.os, "getcwd", Mock(return_value="/original"))
    chdir = Mock()
    monkeypatch.setattr(shell_entrypoint.os, "chdir", chdir)
    monkeypatch.setattr(shell_entrypoint.os, "getenv", Mock(return_value="false"))
    monkeypatch.setattr(shell_entrypoint, "shell_login", Mock(return_value=user))
    monkeypatch.setattr(shell_entrypoint, "ConsoleTerminal", Mock(return_value="terminal"))
    monkeypatch.setattr(shell_entrypoint, "Session", Mock(return_value="session"))
    monkeypatch.setattr(shell_entrypoint, "Shell", Mock(return_value=shell))

    shell_entrypoint.main()

    assert shell_entrypoint.Session.call_args_list == [call("terminal", user)]
    assert shell_entrypoint.Shell.call_args_list == [call("session")]
    assert shell.start.call_args_list == [call()]
    assert chdir.call_args_list == [call("/original")]


def test_service_entrypoint_executes_boss_with_process_arguments(monkeypatch):
    """Forward CLI arguments to the virtual supervisor shell."""
    shell = Mock()
    monkeypatch.setattr(sys, "argv", ["badproc", "start", "network.sys"])
    monkeypatch.setattr(service_entrypoint, "ConsoleTerminal", Mock(return_value="terminal"))
    monkeypatch.setattr(service_entrypoint, "Session", Mock(return_value="session"))
    monkeypatch.setattr(service_entrypoint, "Shell", Mock(return_value=shell))

    service_entrypoint.main()

    assert service_entrypoint.Session.call_args_list == [
        call("terminal", service_entrypoint.SERVICE_USER)
    ]
    assert service_entrypoint.Shell.call_args_list == [call("session")]
    assert shell.execute.call_args_list == [call("boss start network.sys")]
