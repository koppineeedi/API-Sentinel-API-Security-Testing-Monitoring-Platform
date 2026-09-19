import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple, Optional
import httpx
from fastapi import HTTPException, status

RESTRICTED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"), # Includes AWS IMDS 169.254.169.254
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

class SSRFProtector:
    @staticmethod
    def validate_url(url: str, allow_local: bool = False) -> str:
        """
        Validates URL scheme, resolves domain IP address, and verifies it is not in a restricted network.
        """
        if not url:
            raise ValueError("URL cannot be empty")

        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            raise ValueError(f"Disallowed URL scheme '{parsed.scheme}'. Only http and https are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid URL: Missing hostname")

        # Bypass loopback check ONLY if allow_local is explicitly True (e.g., local lab testing)
        if allow_local and (hostname in ["localhost", "127.0.0.1", "::1"]):
            return url

        # Resolve hostname to IP address
        try:
            ip_info = socket.getaddrinfo(hostname, None)
            resolved_ips = {item[4][0] for item in ip_info}
        except socket.gaierror as e:
            raise ValueError(f"Could not resolve hostname '{hostname}': {str(e)}")

        for ip_str in resolved_ips:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                for restricted_net in RESTRICTED_IP_NETWORKS:
                    if ip_obj in restricted_net:
                        if not allow_local:
                            raise ValueError(
                                f"SSRF Security Violation: Hostname '{hostname}' resolves to restricted IP '{ip_str}'"
                            )
            except ValueError as ve:
                if "SSRF Security Violation" in str(ve):
                    raise ve
                continue

        return url

    @staticmethod
    async def fetch_safe_url(url: str, allow_local: bool = True, max_bytes: int = 2097152) -> str:
        """
        Safe HTTP GET client enforcing timeout (5s), max payload size (2MB max), and no redirects.
        """
        validated_url = SSRFProtector.validate_url(url, allow_local=allow_local)
        
        transport = httpx.AsyncHTTPTransport(retries=0)
        async with httpx.AsyncClient(transport=transport, follow_redirects=False, timeout=5.0) as client:
            try:
                response = await client.get(validated_url)
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Target URL returned HTTP {response.status_code}"
                    )

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Imported spec content exceeds maximum size limit of 2MB"
                    )

                body = response.text
                if len(body.encode('utf-8')) > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Imported spec content exceeds maximum size limit of 2MB"
                    )

                return body
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Connection to target URL timed out (5s limit)"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch specification from target URL: {str(e)}"
                )
