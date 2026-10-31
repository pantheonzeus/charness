"""Prefer IPv4 for unspecified-family lookups. This network advertises IPv6 but doesn't route it,
and httplib2 (Google's API client) never falls back, so every Google call hangs until timeout.
Loaded via PYTHONPATH by scripts/start-google-workspace-mcp.sh."""
import socket

_getaddrinfo = socket.getaddrinfo


def _v4_first(host, port, family=0, *args, **kwargs):
    if family == socket.AF_UNSPEC:
        try:
            return _getaddrinfo(host, port, socket.AF_INET, *args, **kwargs)
        except socket.gaierror:
            pass
    return _getaddrinfo(host, port, family, *args, **kwargs)


socket.getaddrinfo = _v4_first
