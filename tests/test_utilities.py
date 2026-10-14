"""
Unit tests for serialization, version selection, executable loading, and install helpers.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import sys
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from bdsh.install import InstallType
import bdsh.install.util as install_util
import bdsh.util.exec as exec_module
from bdsh.util.exec import load_exec
from bdsh.util.serializing import SerializationError, validate_json_value
from bdsh.util.version import VersionSelector


@pytest.mark.parametrize(
    ("value", "path"),
    [
        (None, "request"),
        ({"name": "package", "versions": [1, 2.5, True, None]}, "request"),
        ({"nested": [{"value": "ok"}]}, "payload"),
    ],
)
def test_validate_json_value_accepts_json_values(value, path):
    """Accept primitives and nested lists/maps containing JSON-compatible values."""
    assert validate_json_value(value, path) is None


def test_validate_json_value_reports_nested_non_string_key():
    """Include the failing nested path when a mapping key is not JSON-compatible."""
    with pytest.raises(SerializationError, match=r"request\['items'\]\[0\].*non-string"):
        validate_json_value({"items": [{1: "invalid"}]}, "request")


def test_validate_json_value_rejects_unsupported_object():
    """Reject values that JSON cannot represent and identify their location."""
    with pytest.raises(SerializationError, match=r"payload\['value'\].*unsupported type object"):
        validate_json_value({"value": object()}, "payload")


@pytest.mark.parametrize(
    ("selector", "candidate", "expected"),
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "1.2.4", False),
        (">=1.2.3", "1.2.3", True),
        (">1.2.3", "1.2.4", True),
        ("<2.0.0", "1.9.9", True),
        ("<=1.2.3", "1.2.4", False),
        ("~1.2.3", "1.2.9", True),
        ("~1.2.3", "1.3.0", False),
        ("^0.2.3", "0.2.9", True),
        ("^0.2.3", "0.3.0", False),
        ("^0.0.3", "0.0.4", False),
        ("*", "99.99.99", True),
    ],
)
def test_version_selector_matches_expected_bounds(selector, candidate, expected):
    """Match exact, open, compatible, caret, and wildcard version constraints."""
    assert VersionSelector(selector).matches(candidate) is expected


@pytest.mark.parametrize(
    ("selector", "expected"),
    [
        ("1.2.3", "==1.2.3"),
        ("~1.2.3", "~=1.2.3"),
        ("^1.2.3", ">=1.2.3,<2.0.0"),
        ("^0.2.3", ">=0.2.3,<0.3.0"),
        ("^0.0.3", ">=0.0.3,<0.0.4"),
        ("*", ""),
    ],
)
def test_version_selector_formats_pip_constraints(selector, expected):
    """Translate version selectors into equivalent pip requirement expressions."""
    assert VersionSelector(selector).to_pip() == expected


@pytest.mark.parametrize("selector", ["", "1.2", "1.2.3.4", "latest", "==1.2.3"])
def test_version_selector_rejects_malformed_selector(selector):
    """Reject incomplete versions and operators outside the selector grammar."""
    with pytest.raises(ValueError, match="Invalid version selector"):
        VersionSelector(selector)


def test_load_exec_imports_python_file(tmp_path):
    """Load an executable module from a path and expose its callable entry point."""
    executable = tmp_path / "hello.py"
    executable.write_text("def main():\n    return 'hello'\n", encoding="utf-8")

    module = load_exec(executable)

    assert module.main() == "hello"


@pytest.mark.skipif(not hasattr(Path, "walk"), reason="Path.walk requires Python 3.12+")
def test_get_exec_path_finds_executable_in_nested_directory(monkeypatch, tmp_path):
    """Search executable subdirectories and return the matching file path."""
    executable_dir = tmp_path / "exec" / "nested"
    executable_dir.mkdir(parents=True)
    executable = executable_dir / "sample"
    executable.write_text("print('sample')\n", encoding="utf-8")
    monkeypatch.setattr(exec_module, "get_shell_path", lambda *parts: tmp_path.joinpath(*parts))

    assert exec_module.get_exec_path("sample") == executable
    assert exec_module.get_exec_path("missing") is None


def test_install_type_display_lists_supported_installation_modes(capsys):
    """Show each installation type and its command-line value."""
    InstallType.display()

    assert capsys.readouterr().out.splitlines() == [
        "\t> std (STANDARD)",
        "\t> sys (SYSTEM)",
    ]


def test_install_package_invokes_pip_and_reports_success(monkeypatch):
    """Install a trimmed package name through the selected Python interpreter."""
    check_call = Mock()
    monkeypatch.setattr(install_util.subprocess, "check_call", check_call)
    output = Mock()

    install_util.install_python_package(" requests ", printfn=output)

    assert check_call.call_args_list == [
        call(
            [sys.executable, "-m", "pip", "install", "requests"],
            stdout=install_util.subprocess.DEVNULL,
            stderr=install_util.subprocess.DEVNULL,
        )
    ]
    assert output.call_args_list == [call("OK")]


def test_install_package_reports_failure_and_exits(monkeypatch):
    """Stop installation with its documented exit code when pip fails."""
    check_call = Mock(side_effect=install_util.subprocess.CalledProcessError(1, "pip"))
    monkeypatch.setattr(install_util.subprocess, "check_call", check_call)
    output = Mock()

    with pytest.raises(SystemExit) as error:
        install_util.install_python_package("missing-package", printfn=output)

    assert error.value.code == 0x81
    assert output.call_args_list == [call("FAILED")]


def test_prompt_calls_cancel_callback_for_no_response(monkeypatch):
    """Call the cancellation action only when the user explicitly declines."""
    input_fn = Mock(return_value="n")
    monkeypatch.setattr("builtins.input", input_fn)
    on_cancel = Mock()

    install_util.prompt("Continue?", on_cancel)

    assert input_fn.call_args_list == [call("Continue? [y/n] ")]
    assert on_cancel.call_args_list == [call()]
