"""
Unit tests for RPC, service dispatch, and BadLogon behavior.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import json
import socket
from unittest.mock import Mock, call

import pytest

from bdsh.service import ServiceUnavailableError
from bdsh.service import badlogon
from bdsh.service import dispatch as dispatch_module
from bdsh.service.rpc import (
    RPCError,
    RPCSocketClient,
    RPCSocketService,
    servicemethod,
)
import bdsh.service.rpc as rpc_module


class ExampleRPCService(RPCSocketService, name=None):
    """Provide deterministic service methods for RPC dispatch tests."""

    name = "example.sys"

    @servicemethod
    def add(self, left, right):
        return left + right

    def private_operation(self):
        return "not exposed"

    @servicemethod
    def fail(self):
        raise ValueError("operation failed")


def test_rpc_dispatch_invokes_only_exposed_service_methods():
    """Invoke a decorated method and reject a non-exposed method."""
    service = ExampleRPCService.__new__(ExampleRPCService)

    assert service.dispatch("add", {"left": 2, "right": 3}) == 5
    with pytest.raises(ValueError, match="service method does not exist: 'private_operation'"):
        service.dispatch("private_operation", {})


def test_rpc_request_handler_returns_method_result():
    """Preserve the request ID and return a successful service response."""
    service = ExampleRPCService.__new__(ExampleRPCService)

    response = service._handle_request({
        "id": 7,
        "method": "add",
        "params": {"left": 4, "right": 6},
    })

    assert response == {"id": 7, "msg": 10}


def test_rpc_request_handler_serializes_service_exception():
    """Convert an operation exception into an RPC error response."""
    service = ExampleRPCService.__new__(ExampleRPCService)

    response = service._handle_request({"id": 8, "method": "fail", "params": {}})

    assert response == {
        "id": 8,
        "error": {"type": "ValueError", "message": "operation failed"},
    }


def test_rpc_client_sends_request_and_returns_message(monkeypatch):
    """Send a JSON request over the socket and return the response message."""
    sock = Mock()
    sock.recv.return_value = b'{"id": 1, "msg": {"ok": true}}'
    socket_factory = Mock(return_value=sock)
    monkeypatch.setattr("bdsh.service.rpc.socket.socket", socket_factory)
    client = RPCSocketClient("example.sys")

    result = client.request("status", {"verbose": True})

    assert result == {"ok": True}
    assert socket_factory.call_args_list[0].args == (
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )
    assert sock.connect.call_args_list == [call("/tmp/example.sys.sock")]
    assert json.loads(sock.sendall.call_args.args[0]) == {
        "id": 1,
        "method": "status",
        "params": {"verbose": True},
    }
    assert sock.close.call_args_list == [call()]
    assert client._request_id == 1


def test_rpc_client_raises_rpc_error_for_service_error(monkeypatch):
    """Expose the upstream exception type and message to RPC callers."""
    sock = Mock()
    sock.recv.return_value = (
        b'{"id": 1, "error": {"type": "ValueError", "message": "bad input"}}'
    )
    monkeypatch.setattr("bdsh.service.rpc.socket.socket", Mock(return_value=sock))
    client = RPCSocketClient("example.sys")

    with pytest.raises(RPCError, match="ValueError: bad input"):
        client.request("status")

    assert sock.close.call_args_list == [call()]


def test_rpc_client_maps_missing_socket_to_service_unavailable(monkeypatch):
    """Translate a missing UNIX socket into the service-specific exception."""
    sock = Mock()
    sock.connect.side_effect = FileNotFoundError(2, "missing socket")
    monkeypatch.setattr("bdsh.service.rpc.socket.socket", Mock(return_value=sock))
    client = RPCSocketClient("missing.sys")

    with pytest.raises(ServiceUnavailableError, match="service unavailable"):
        client.request("status")

    assert sock.close.call_args_list == [call()]


def test_user_login_verifies_matching_and_rejects_wrong_password(monkeypatch):
    """Accept a password matching its Argon2 hash and reject a mismatch."""
    user = badlogon.User("alice", badlogon.hasher.hash("correct"))

    assert user.try_login("correct")
    assert not user.try_login("incorrect")


def test_badlogon_service_validates_and_persists_users(monkeypatch, tmp_path):
    """Reject invalid account input, save valid users, and reload them from disk."""
    monkeypatch.setattr("bdsh.service.signal.signal", Mock())
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    monkeypatch.setattr(badlogon.OSPaths, "PROFILES", profiles)
    user_file = tmp_path / "users"
    service = badlogon.BadLogonService(user_file)

    with pytest.raises(ValueError, match="username contains illegal characters"):
        service.add("bad:name", "password")
    with pytest.raises(ValueError, match="cannot be empty"):
        service.add("alice", " ")

    service.add("alice", "secret")
    with pytest.raises(ValueError, match="username already in use"):
        service.add("alice", "another")
    service.save()

    reloaded = badlogon.BadLogonService(user_file)
    authenticated = reloaded.get_user_by_credentials("alice", "secret")

    assert authenticated is not None
    assert authenticated["username"] == "alice"
    assert reloaded.get_user_by_credentials("alice", "wrong") is None
    assert user_file.read_text(encoding="utf-8").startswith("alice:")
    assert (profiles / "alice").is_dir()


def test_dispatch_system_services_starts_each_service_in_daemon_thread(monkeypatch):
    """Start each configured system service using a named daemon thread."""
    first_service = Mock(name="network_service")
    first_service.name = "network.sys"
    second_service = Mock(name="badlogon_service")
    second_service.name = "badlogon.sys"
    first_class = Mock(return_value=first_service)
    second_class = Mock(return_value=second_service)
    first_thread = Mock()
    second_thread = Mock()
    thread_factory = Mock(side_effect=[first_thread, second_thread])
    monkeypatch.setattr(dispatch_module, "_SYSTEM_SERVICES", [first_class, second_class])
    monkeypatch.setattr(dispatch_module, "Thread", thread_factory)

    dispatch_module.dispatch_system_services()

    assert thread_factory.call_args_list == [
        call(target=first_service.start, daemon=True, name="network.sys"),
        call(target=second_service.start, daemon=True, name="badlogon.sys"),
    ]
    assert first_thread.start.call_args_list == [call()]
    assert second_thread.start.call_args_list == [call()]


def test_rpc_service_accepts_client_and_cleans_up(monkeypatch, tmp_path):
    """Serve an accepted client and close/unlink the socket on shutdown."""
    monkeypatch.setattr("bdsh.service.signal.signal", Mock())
    server = Mock()
    client = Mock()
    server.accept.return_value = (client, None)
    monkeypatch.setattr(rpc_module.socket, "socket", Mock(return_value=server))
    service = ExampleRPCService()
    service.socket_path = tmp_path / "example.sock"
    service._handle_client = Mock(side_effect=lambda _: setattr(service, "running", False))

    service.start()

    assert server.bind.call_args_list == [call(str(service.socket_path))]
    assert server.listen.call_args_list == [call(10)]
    assert service._handle_client.call_args_list == [call(client)]
    assert client.close.call_args_list == [call()]
    assert server.close.call_args_list == [call()]
    assert service.server is None
    assert not service.running
    assert not service.socket_path.exists()
