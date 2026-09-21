from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, ip_address, ip_network
from typing import Awaitable, Callable, Iterable

from starlette.responses import PlainTextResponse
from starlette.types import Receive, Scope, Send

IPNetwork = IPv4Network | IPv6Network
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


def parse_allowed_ips(value: str) -> tuple[IPNetwork, ...]:
    """Parse comma-separated IP addresses and networks."""
    return tuple(ip_network(item.strip()) for item in value.split(",") if item.strip())


class IPAllowListMiddleware:
    def __init__(self, app: ASGIApp, allowed_ips: Iterable[IPNetwork]) -> None:
        self.app = app
        self.allowed_ips = tuple(allowed_ips)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.allowed_ips:
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        try:
            address = ip_address(client[0]) if client else None
        except ValueError:
            address = None

        candidates: tuple[IPv4Address | IPv6Address, ...] = () if address is None else (address,)
        if isinstance(address, IPv6Address) and address.ipv4_mapped:
            candidates += (address.ipv4_mapped,)

        if any(candidate in network for candidate in candidates for network in self.allowed_ips):
            await self.app(scope, receive, send)
            return

        await PlainTextResponse("Forbidden", status_code=403)(scope, receive, send)
