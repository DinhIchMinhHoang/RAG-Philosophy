from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


class URLValidationError(ValueError):
    pass


def validate_ingest_url(url: str) -> str:
    if not url or len(url) > MAX_URL_LENGTH:
        raise URLValidationError("URL is too long or empty")

    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise URLValidationError(f"Only http/https URLs are allowed, got: {parsed.scheme}")

    if not parsed.netloc:
        raise URLValidationError("URL must have a hostname")

    if parsed.username or parsed.password:
        raise URLValidationError("URL must not contain credentials")

    _check_ssrf_safe(parsed.hostname)

    return url


def _check_ssrf_safe(hostname: str) -> None:
    try:
        addr = ipaddress.ip_address(hostname)
        if _is_blocked_ip(addr):
            raise URLValidationError(f"Cannot access private or loopback IP: {hostname}")
        return
    except ValueError:
        pass

    try:
        addrinfo = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise URLValidationError(f"Cannot resolve hostname: {hostname}")

    seen: set[str] = set()
    for _, _, _, _, sockaddr in addrinfo:
        ip_str = sockaddr[0]
        if ip_str in seen:
            continue
        seen.add(ip_str)
        try:
            addr = ipaddress.ip_address(ip_str)
            if _is_blocked_ip(addr):
                raise URLValidationError(f"Host {hostname} resolves to blocked IP: {ip_str}")
        except ValueError:
            continue


def _is_blocked_ip(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if addr.is_private or addr.is_loopback or addr.is_link_local:
        return True
    if isinstance(addr, ipaddress.IPv6Address):
        if addr.is_site_local:
            return True
        if addr.ipv4_mapped and _is_blocked_ip(addr.ipv4_mapped):
            return True
    return False
