import ipaddress
import socket
from urllib.parse import urlsplit, urljoin
import requests


ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443,}
BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata.amazonaws.com",
}
REDIRECT_STATUSES = {
    301,
    302,
    303,
    307,
    308,
}
MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class UnsafeURLError(ValueError):
    pass


def validate_url_structure(url: str):
    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise UnsafeURLError("Invalid URL.") from error
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise UnsafeURLError ("Only HTTP and HTTPS URLs are allowed.")
    if not parsed.hostname:
        raise UnsafeURLError("URL must contain a hostname.")
    if parsed.username and parsed.password:
        raise UnsafeURLError("URLs containing usernames or passwords are not allowed.")
    if parsed.port and parsed.port not in ALLOWED_PORTS:
        raise UnsafeURLError("Only ports 80 and 443 are allowed.")
    return parsed


def validate_hostname(hostname: str):
    hostname = hostname.rstrip(".").lower()
    if hostname in BLOCKED_HOSTNAMES:
        raise UnsafeURLError("This hostname is not allowed.")
    if hostname.endswith(".localhost"):
        raise UnsafeURLError("Localhost addresses are not allowed.")
    

def resolve_hostname(hostname: str, port: int):
    try:
        results = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise UnsafeURLError("Hostname could not be resolved.") from error
    addresses = {result[4][0] for result in results}
    if not addresses:
        raise UnsafeURLError("Hostname did not resolve to an IP address.")
    return addresses


def is_public_ip(address: str) -> bool:
    ip = ipaddress.ip_address(address)

    if ip.is_private:
        return False

    if ip.is_loopback:
        return False

    if ip.is_link_local:
        return False

    if ip.is_multicast:
        return False

    if ip.is_reserved:
        return False

    if ip.is_unspecified:
        return False

    if not ip.is_global:
        return False

    return True


def validate_resolved_addresses(hostname: str, port: int):
    addresses = resolve_hostname(hostname, port)
    for address in addresses:
        if not is_public_ip(address):
            raise UnsafeURLError("Hostname resolves to a non-public address.")


def validate_external_url(url: str):
    parsed = validate_url_structure(url)
    hostname = parsed.hostname.rstrip(".").lower()
    validate_hostname(hostname)
    if parsed.port:
        port = parsed.port
    elif parsed.scheme.lower() == "https":
        port = 443
    else:
        port = 80
    validate_resolved_addresses(hostname, port)


def safe_get(url: str, headers=None,timeout=(5, 10)):
    current_url = url

    for _ in range(MAX_REDIRECTS + 1):

        validate_external_url(current_url)

        response = requests.get(
            current_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=False,
            stream=True,
        )

        if response.status_code in REDIRECT_STATUSES:
            location = response.headers.get("Location")
            if not location:
                response.close()
                raise UnsafeURLError("Redirect has no destination.")
            next_url = urljoin(current_url,location)
            response.close()
            current_url = next_url
            continue
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
            except ValueError:
                size = None
            if (size is not None and size > MAX_RESPONSE_BYTES):
                response.close()
                raise UnsafeURLError("Webpage is too large.")
        content = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            content.extend(chunk)
            if len(content) > MAX_RESPONSE_BYTES:
                response.close()
                raise UnsafeURLError("Webpage is too large.")
        response._content = bytes(content)
        response._content_consumed = True
        return response
    raise UnsafeURLError("Too many redirects.")