"""
Unit tests for package metadata and package-manager command behavior.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

import bdsh.command.bpm as bpm


def make_package(**overrides):
    """Create a valid package record with optional field overrides."""
    values = {
        "internal_repo": "owner/repo/main",
        "internal_package": "sample",
        "name": "Sample package",
        "id": "sample",
        "version": "1.2.3",
        "author": "Test author",
        "shellVersion": ">=1.0.0",
    }
    values.update(overrides)
    return bpm.Package(**values)


def test_dependency_map_accepts_valid_names_and_constraints():
    """Store dependency names with constraints accepted by the manager."""
    dependencies = bpm.DependencyMap({
        "core-lib": "^1.2.3",
        "compat-lib": ">=2.0.0",
        "optional-lib": "*",
    })

    assert dependencies == {
        "core-lib": "^1.2.3",
        "compat-lib": ">=2.0.0",
        "optional-lib": "*",
    }


@pytest.mark.parametrize(
    ("dependency", "constraint", "message"),
    [
        ("Bad_Name", "1.2.3", "Invalid dependency name"),
        ("good-name", "1.2", "Invalid dependency version constraint"),
    ],
)
def test_dependency_map_rejects_invalid_entries(dependency, constraint, message):
    """Reject invalid dependency identifiers and malformed version constraints."""
    with pytest.raises(ValueError, match=message):
        bpm.DependencyMap({dependency: constraint})


def test_package_rejects_invalid_id_version_and_homepage():
    """Validate package identifiers, semantic versions, and homepage URLs."""
    with pytest.raises(ValueError, match="Invalid id"):
        make_package(id="Sample")
    with pytest.raises(ValueError, match="Invalid version"):
        make_package(version="1.2")
    with pytest.raises(ValueError, match="Invalid homepage URI"):
        make_package(homepage="relative/path")


def test_package_load_json_sets_repository_fields_and_nested_values():
    """Load the supported package fields and attach source repository metadata."""
    data = {
        "name": "Sample package",
        "id": "sample",
        "version": "1.2.3",
        "author": "Test author",
        "shellVersion": ">=1.0.0",
        "binaries": {"sample": "bin/sample"},
        "dependencies": {"core-lib": "^1.2.3"},
    }

    package = bpm.Package.load_json("sample", data, "owner/repo/main")

    assert package.internal_repo == "owner/repo/main"
    assert package.internal_package == "sample"
    assert package.binaries == {"sample": "bin/sample"}
    assert package.dependencies == {"core-lib": "^1.2.3"}


def test_package_fetch_parses_successful_response(monkeypatch):
    """Fetch package metadata and parse its JSON body into a Package."""
    response = Mock(status_code=200)
    response.content = json.dumps({
        "name": "Sample",
        "id": "sample",
        "version": "1.0.0",
        "author": "Author",
        "shellVersion": "*",
    }).encode()
    get = Mock(return_value=response)
    monkeypatch.setattr(bpm.requests, "get", get)

    package = bpm.Package.fetch("sample", "owner/repo/main")

    assert package.id == "sample"
    assert package.internal_repo == "owner/repo/main"
    assert get.call_args_list == [
        call("https://raw.githubusercontent.com/owner/repo/main/lib/sample/bpl.json")
    ]


def test_package_fetch_distinguishes_missing_package(monkeypatch):
    """Report a package-specific exception for an HTTP 404 response."""
    monkeypatch.setattr(bpm.requests, "get", Mock(return_value=Mock(status_code=404)))

    with pytest.raises(bpm.PackageException, match="sample: does not exist"):
        bpm.Package.fetch("sample", "owner/repo/main")


def test_store_metadata_round_trips_paths(tmp_path):
    """Persist and restore package-owned binaries and executable links."""
    file = tmp_path / "package.bpmstore"
    metadata = bpm.StoreMetadata(
        name="Sample",
        author="Author",
        binaries=[tmp_path / "app" / "sample"],
        symlinks=[tmp_path / "exec" / "sample"],
    )

    metadata.dump(file)
    restored = bpm.StoreMetadata.load(file)

    assert restored == metadata


def test_store_metadata_uses_defaults_for_missing_optional_fields(tmp_path):
    """Load older or minimal metadata files using documented fallback values."""
    file = tmp_path / "minimal.bpmstore"
    file.write_text("{}", encoding="utf-8")

    metadata = bpm.StoreMetadata.load(file)

    assert metadata == bpm.StoreMetadata(
        name="Unnamed package",
        author="Unknown author",
        binaries=[],
        symlinks=[],
    )


def test_package_manager_execute_parses_arguments_and_dispatches_action(tmp_path):
    """Route parsed CLI arguments to the matching package action handler."""
    command = bpm.BadOSPackageManagerCommand(SimpleNamespace(io=Mock()))
    handler = Mock()
    command.handlers["install"] = handler

    command.execute(["bpm", "install", "sample", "-y", "-r", "owner/repo/main"])

    args = handler.call_args.args[0]
    assert args.action == "install"
    assert args.packages == ["sample"]
    assert args.yes
    assert args.repo == "owner/repo/main"


def test_package_manager_install_reports_when_no_packages_are_found(monkeypatch, tmp_path):
    """Stop before installation when dependency discovery yields no packages."""
    io = Mock()
    command = bpm.BadOSPackageManagerCommand(SimpleNamespace(io=io))
    discovery = Mock(return_value=[])
    monkeypatch.setattr(command, "_BadOSPackageManagerCommand__discover_package_dependencies", discovery)

    command.execute(["bpm", "install", "missing", "-y"])

    assert discovery.call_args_list[0].args == ("missing", bpm.BPL_REPO)
    assert io.println.call_args_list[-1] == call("No packages to install!")


def test_package_manager_remove_deletes_binaries_links_and_store(monkeypatch, tmp_path):
    """Remove files and links referenced by package-store metadata."""
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setattr(bpm, "BPM_STORE_DIR", store_dir)
    binary = tmp_path / "apps" / "sample"
    binary.parent.mkdir()
    binary.write_text("executable", encoding="utf-8")
    executable = tmp_path / "exec" / "sample"
    executable.parent.mkdir()
    executable.symlink_to(binary)
    store_file = store_dir / "sample@1.0.0.bpmstore"
    bpm.StoreMetadata(
        name="Sample",
        author="Author",
        binaries=[binary],
        symlinks=[executable],
    ).dump(store_file)
    io = Mock()
    command = bpm.BadOSPackageManagerCommand(SimpleNamespace(io=io))

    command._BadOSPackageManagerCommand__remove(
        SimpleNamespace(packages=["sample"], yes=True)
    )

    assert not binary.exists()
    assert not executable.is_symlink()
    assert not store_file.exists()
    assert io.println.call_args_list[-1] == call("\tCompleted package deletion")
