"""
Unit tests for network service APIs and network commands.

Author: Logan Dhillon <dev@logandhillon.com>
"""

import socket
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from bdsh.command.net import HostnameCommand, NetCommand, PingCommand
from bdsh.service import network


def test_network_client_maps_api_calls_to_rpc_methods(monkeypatch):
    """Send supported network API operations to their named RPC methods."""
    client = network.NetworkClient()
    request = Mock(side_effect=["host", {"eth0": {}}, {"eth0": []}])
    monkeypatch.setattr(client, "request", request)

    assert client.hostname() == "host"
    assert client.interfaces() == {"eth0": {}}
    assert client.interface_addresses() == {"eth0": []}

    assert request.call_args_list == [
        call("hostname"),
        call("interfaces"),
        call("interface_addresses"),
    ]


def test_network_service_returns_hostname_and_resolved_address(monkeypatch):
    """Use the operating system resolver for hostname and address operations."""
    monkeypatch.setattr(network.socket, "gethostname", Mock(return_value="node"))
    monkeypatch.setattr(network.socket, "gethostbyname", Mock(return_value="192.0.2.1"))
    service = network.NetworkService.__new__(network.NetworkService)

    assert service.hostname() == "node"
    assert service.resolve("example.test") == "192.0.2.1"
    assert network.socket.gethostbyname.call_args_list == [call("example.test")]


def test_network_service_serializes_interface_statistics(monkeypatch):
    """Expose interface status fields from psutil as a JSON-ready mapping."""
    stats = SimpleNamespace(flags="up,broadcast", isup=True, duplex=2, speed=1000, mtu=1500)
    monkeypatch.setattr(network.psutil, "net_if_stats", Mock(return_value={"eth0": stats}))
    service = network.NetworkService.__new__(network.NetworkService)

    assert service.interfaces() == {
        "eth0": {
            "flags": "up,broadcast",
            "isup": True,
            "duplex": 2,
            "speed": 1000,
            "mtu": 1500,
        }
    }


def test_network_service_serializes_interface_addresses(monkeypatch):
    """Convert address family enums and address fields into serializable values."""
    address = SimpleNamespace(
        family=socket.AddressFamily.AF_INET,
        address="192.0.2.10",
        netmask="255.255.255.0",
        broadcast="192.0.2.255",
    )
    monkeypatch.setattr(network.psutil, "net_if_addrs", Mock(return_value={"eth0": [address]}))
    service = network.NetworkService.__new__(network.NetworkService)

    assert service.interface_addresses() == {
        "eth0": [{
            "family": "AF_INET",
            "address": "192.0.2.10",
            "netmask": "255.255.255.0",
            "broadcast": "192.0.2.255",
        }]
    }


def test_net_command_formats_selected_interface_details(monkeypatch):
    """Print flags, MTU, and assigned address fields for the requested interface."""
    client = Mock()
    client.interfaces.return_value = {
        "eth0": {"flags": "up", "mtu": 1500},
        "lo": {"flags": "loopback", "mtu": 65536},
    }
    client.interface_addresses.return_value = {
        "eth0": [{
            "family": "AF_INET",
            "address": "192.0.2.10",
            "netmask": "255.255.255.0",
            "broadcast": "192.0.2.255",
        }],
        "lo": [],
    }
    monkeypatch.setattr("bdsh.command.net.NetworkClient", Mock(return_value=client))
    io = Mock()

    NetCommand(SimpleNamespace(io=io)).execute(["net", "eth0"])

    assert io.println.call_args_list == [
        call(
            "eth0: flags=up mtu 1500\n"
            "\tAF_INET 192.0.2.10 netmask 255.255.255.0 broadcast 192.0.2.255"
        )
    ]


def test_net_command_rejects_unknown_interface(monkeypatch):
    """Reject a requested interface that is not reported by the service."""
    client = Mock()
    client.interfaces.return_value = {"eth0": {"flags": "up", "mtu": 1500}}
    monkeypatch.setattr("bdsh.command.net.NetworkClient", Mock(return_value=client))

    with pytest.raises(ValueError, match="interface missing does not exist"):
        NetCommand(SimpleNamespace(io=Mock())).execute(["net", "missing"])


def test_hostname_command_prints_service_hostname(monkeypatch):
    """Print the hostname returned by the network service."""
    client = Mock()
    client.hostname.return_value = "node"
    monkeypatch.setattr("bdsh.command.net.NetworkClient", Mock(return_value=client))
    io = Mock()

    HostnameCommand(SimpleNamespace(io=io)).execute(["hostname"])

    assert io.println.call_args_list == [call("node")]


def test_ping_command_reports_packet_counts(monkeypatch):
    """Resolve the target and report each result and aggregate packet loss."""
    client = Mock()
    client.resolve.return_value = "192.0.2.20"
    monkeypatch.setattr("bdsh.command.net.NetworkClient", Mock(return_value=client))
    ping = Mock(side_effect=[True, False, True])
    monkeypatch.setitem(__import__("sys").modules, "icmplib", SimpleNamespace(ping=ping))
    io = Mock()

    PingCommand(SimpleNamespace(io=io)).execute(["ping", "example.test", "-c", "3"])

    assert client.resolve.call_args_list == [call(hostname="example.test")]
    assert ping.call_count == 3
    assert io.println.call_args_list == [
        call("pinging example.test (192.0.2.20) with 56 bytes"),
        call("OK"),
        call("TIMEOUT"),
        call("OK"),
        call("3 packets sent, 2 packets received, 33.3% packet loss"),
    ]
    assert io.print.call_args_list == [
        call("icmp_seq 0... "),
        call("icmp_seq 1... "),
        call("icmp_seq 2... "),
    ]


def test_ping_command_translates_dns_error(monkeypatch):
    """Report an invalid host as a concise command-level error."""
    client = Mock()
    client.resolve.side_effect = socket.gaierror("not found")
    monkeypatch.setattr("bdsh.command.net.NetworkClient", Mock(return_value=client))

    with pytest.raises(ValueError, match='failed to resolve host: "missing.test"'):
        PingCommand(SimpleNamespace(io=Mock())).execute(["ping", "missing.test"])
