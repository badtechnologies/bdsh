"""
Unit tests for the bdsh kernel entrypoint.

Author: Logan Dhillon <dev@logandhillon.com>
"""

from unittest.mock import Mock, call

from bdsh import init


def test_main_creates_all_os_paths_and_default_profile(monkeypatch):
    """Create each configured OS path and the default profile directory."""
    # Replace the path definitions with mocks so the test never writes to disk.
    os_paths = [Mock(name="root_path"), Mock(name="config_path")]
    default_profile = Mock(name="default_profile")
    profiles = Mock(name="profiles")
    profiles.joinpath.return_value = default_profile

    monkeypatch.setattr(init.OSPaths, "all", Mock(return_value=os_paths))
    monkeypatch.setattr(init.OSPaths, "PROFILES", profiles)
    monkeypatch.setattr(init, "Shell", Mock())

    init.main()

    for path in (*os_paths, default_profile):
        assert path.mkdir.call_args_list == [call(parents=True, exist_ok=True)]
    assert profiles.joinpath.call_args_list == [call("default")]


def test_main_starts_shell_with_console_default_user_and_session(monkeypatch):
    """Build the default session and start its shell."""
    # Use distinct sentinels to verify each object is passed to the next layer.
    terminal = object()
    user = object()
    session = object()
    shell = Mock()
    console_factory = Mock(return_value=terminal)
    user_factory = Mock(return_value=user)
    session_factory = Mock(return_value=session)
    shell_factory = Mock(return_value=shell)
    default_profile = Mock()
    profiles = Mock()
    profiles.joinpath.return_value = default_profile

    monkeypatch.setattr(init.OSPaths, "all", Mock(return_value=[]))
    monkeypatch.setattr(init.OSPaths, "PROFILES", profiles)
    monkeypatch.setattr(init, "ConsoleTerminal", console_factory)
    monkeypatch.setattr(init, "User", user_factory)
    monkeypatch.setattr(init, "Session", session_factory)
    monkeypatch.setattr(init, "Shell", shell_factory)

    init.main()

    # Confirm startup wiring uses a fresh console and the default account.
    assert console_factory.call_args_list == [call()]
    assert user_factory.call_args_list == [call("default", "")]
    assert session_factory.call_args_list == [call(terminal, user)]
    assert shell_factory.call_args_list == [call(session)]
    assert shell.start.call_args_list == [call()]
    # The profile directory is initialized before the shell is started.
    assert default_profile.mkdir.call_args_list == [
        call(parents=True, exist_ok=True)]
