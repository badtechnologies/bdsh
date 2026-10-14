"""
Unit tests for the interactive installer entrypoint.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import sys
from unittest.mock import Mock, call

import bdsh.install.__main__ as installer


def test_system_install_initializes_users_and_installs_core(monkeypatch, tmp_path):
    """Initialize the selected system installation and run core package setup."""
    monkeypatch.setattr(sys, "argv", ["bdsh-install", "type=sys"])
    root = tmp_path / "bdsh"
    monkeypatch.setattr(installer, "BDSH_ROOT", root)
    first_path = Mock()
    second_path = Mock()
    monkeypatch.setattr(installer.OSPaths, "all", Mock(return_value=[first_path, second_path]))
    install_package = Mock()
    monkeypatch.setattr(installer, "install_python_package", install_package)

    userman = Mock()
    monkeypatch.setattr(installer, "BadLogonService", Mock(return_value=userman))
    monkeypatch.setattr("builtins.input", Mock(return_value="alice"))
    monkeypatch.setattr(installer, "getpass", Mock(return_value="secret"))
    monkeypatch.setattr(installer, "prompt", Mock(side_effect=lambda _query, on_cancel: on_cancel()))

    shell = Mock()
    monkeypatch.setattr(installer, "ConsoleTerminal", Mock(return_value="terminal"))
    monkeypatch.setattr(installer, "Session", Mock(return_value="session"))
    monkeypatch.setattr(installer, "Shell", Mock(return_value=shell))

    installer.main()

    assert root.is_dir()
    assert first_path.mkdir.call_args_list == [call(exist_ok=True)]
    assert second_path.mkdir.call_args_list == [call(exist_ok=True)]
    assert install_package.call_args_list == [call("requests")]
    assert userman.add.call_args_list == [call("alice", "secret")]
    assert userman.save.call_args_list == [call()]
    assert shell.execute.call_args_list == [call("bpm install -y core")]
