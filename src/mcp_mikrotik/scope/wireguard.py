from typing import Optional

from mcp.server.fastmcp import Context

from ..connector import execute_mikrotik_command
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE


# ---------------------------------------------------------------------------
# WireGuard Interface Management
# ---------------------------------------------------------------------------

@mcp.tool(name="create_wireguard_interface", annotations=WRITE)
async def mikrotik_create_wireguard_interface(
    ctx: Context,
    name: str,
    listen_port: Optional[int] = None,
    private_key: Optional[str] = None,
    mtu: Optional[int] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
) -> str:
    """
    Creates a WireGuard interface on MikroTik device.

    Args:
        name: Interface name (e.g. "wg0")
        listen_port: UDP port to listen on (default: 13231)
        private_key: Base64-encoded private key. If omitted RouterOS generates one automatically.
        mtu: MTU size (default: 1420)
        comment: Optional comment
        disabled: Whether to disable the interface after creation
    """
    await ctx.info(f"Creating WireGuard interface: name={name}")

    cmd = f"/interface wireguard add name={name}"

    if listen_port is not None:
        cmd += f" listen-port={listen_port}"
    if private_key:
        cmd += f' private-key="{private_key}"'
    if mtu is not None:
        cmd += f" mtu={mtu}"
    if comment:
        cmd += f' comment="{comment}"'
    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create WireGuard interface: {result}"

    details_cmd = f'/interface wireguard print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)

    if details.strip():
        return f"WireGuard interface created successfully:\n\n{details}"
    return "WireGuard interface created successfully."


@mcp.tool(name="list_wireguard_interfaces", annotations=READ)
async def mikrotik_list_wireguard_interfaces(
    ctx: Context,
    name_filter: Optional[str] = None,
    disabled_only: bool = False,
    running_only: bool = False,
) -> str:
    """
    Lists WireGuard interfaces on MikroTik device.

    Args:
        name_filter: Filter by interface name (partial match)
        disabled_only: Show only disabled interfaces
        running_only: Show only running interfaces
    """
    await ctx.info("Listing WireGuard interfaces")

    cmd = "/interface wireguard print"

    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if running_only:
        filters.append("running=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No WireGuard interfaces found."

    return f"WIREGUARD INTERFACES:\n\n{result}"


@mcp.tool(name="get_wireguard_interface", annotations=READ)
async def mikrotik_get_wireguard_interface(ctx: Context, name: str) -> str:
    """
    Gets detailed information about a specific WireGuard interface.

    Args:
        name: Interface name
    """
    await ctx.info(f"Getting WireGuard interface details: name={name}")

    cmd = f'/interface wireguard print detail where name="{name}"'
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"WireGuard interface '{name}' not found."

    return f"WIREGUARD INTERFACE DETAILS:\n\n{result}"


@mcp.tool(name="update_wireguard_interface", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_wireguard_interface(
    ctx: Context,
    name: str,
    new_name: Optional[str] = None,
    listen_port: Optional[int] = None,
    private_key: Optional[str] = None,
    mtu: Optional[int] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> str:
    """
    Updates an existing WireGuard interface on MikroTik device.

    Args:
        name: Current interface name
        new_name: New name for the interface
        listen_port: New UDP listen port
        private_key: New Base64-encoded private key
        mtu: New MTU size
        comment: New comment
        disabled: Enable (False) or disable (True) the interface
    """
    await ctx.info(f"Updating WireGuard interface: name={name}")

    updates = []
    if new_name:
        updates.append(f"name={new_name}")
    if listen_port is not None:
        updates.append(f"listen-port={listen_port}")
    if private_key:
        updates.append(f'private-key="{private_key}"')
    if mtu is not None:
        updates.append(f"mtu={mtu}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')

    if not updates:
        return "No updates specified."

    cmd = f'/interface wireguard set [find name="{name}"] ' + " ".join(updates)
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update WireGuard interface: {result}"

    lookup_name = new_name if new_name else name
    details_cmd = f'/interface wireguard print detail where name="{lookup_name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"WireGuard interface updated successfully:\n\n{details}"


@mcp.tool(name="remove_wireguard_interface", annotations=DESTRUCTIVE)
async def mikrotik_remove_wireguard_interface(ctx: Context, name: str) -> str:
    """
    Removes a WireGuard interface from MikroTik device.

    Args:
        name: Interface name to remove
    """
    await ctx.info(f"Removing WireGuard interface: name={name}")

    check_cmd = f'/interface wireguard print count-only where name="{name}"'
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"WireGuard interface '{name}' not found."

    cmd = f'/interface wireguard remove [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove WireGuard interface: {result}"

    return f"WireGuard interface '{name}' removed successfully."


@mcp.tool(name="enable_wireguard_interface", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_wireguard_interface(ctx: Context, name: str) -> str:
    """
    Enables a WireGuard interface.

    Args:
        name: Interface name
    """
    await ctx.info(f"Enabling WireGuard interface: name={name}")

    cmd = f'/interface wireguard enable [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable WireGuard interface: {result}"

    return f"WireGuard interface '{name}' enabled successfully."


@mcp.tool(name="disable_wireguard_interface", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_wireguard_interface(ctx: Context, name: str) -> str:
    """
    Disables a WireGuard interface.

    Args:
        name: Interface name
    """
    await ctx.info(f"Disabling WireGuard interface: name={name}")

    cmd = f'/interface wireguard disable [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable WireGuard interface: {result}"

    return f"WireGuard interface '{name}' disabled successfully."


# ---------------------------------------------------------------------------
# WireGuard Peer Management
# ---------------------------------------------------------------------------

@mcp.tool(name="add_wireguard_peer", annotations=WRITE)
async def mikrotik_add_wireguard_peer(
    ctx: Context,
    interface: str,
    public_key: str,
    allowed_address: str,
    endpoint_address: Optional[str] = None,
    endpoint_port: Optional[int] = None,
    preshared_key: Optional[str] = None,
    persistent_keepalive: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
) -> str:
    """
    Adds a WireGuard peer to an interface on MikroTik device.

    Args:
        interface: WireGuard interface name the peer belongs to
        public_key: Base64-encoded public key of the remote peer
        allowed_address: Comma-separated list of allowed IP addresses/subnets (e.g. "10.0.0.2/32")
        endpoint_address: Remote peer IP address or hostname
        endpoint_port: Remote peer UDP port
        preshared_key: Optional Base64-encoded preshared key for extra security
        persistent_keepalive: Keepalive interval (e.g. "25s")
        comment: Optional comment
        disabled: Whether to disable the peer after creation
    """
    await ctx.info(f"Adding WireGuard peer: interface={interface}, public_key={public_key[:12]}...")

    cmd = (
        f'/interface wireguard peers add interface="{interface}"'
        f' public-key="{public_key}"'
        f' allowed-address="{allowed_address}"'
    )

    if endpoint_address:
        cmd += f' endpoint-address="{endpoint_address}"'
    if endpoint_port is not None:
        cmd += f" endpoint-port={endpoint_port}"
    if preshared_key:
        cmd += f' preshared-key="{preshared_key}"'
    if persistent_keepalive:
        cmd += f' persistent-keepalive={persistent_keepalive}'
    if comment:
        cmd += f' comment="{comment}"'
    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to add WireGuard peer: {result}"

    details_cmd = (
        f'/interface wireguard peers print detail where'
        f' interface="{interface}" public-key="{public_key}"'
    )
    details = await execute_mikrotik_command(details_cmd, ctx)

    if details.strip():
        return f"WireGuard peer added successfully:\n\n{details}"
    return "WireGuard peer added successfully."


@mcp.tool(name="list_wireguard_peers", annotations=READ)
async def mikrotik_list_wireguard_peers(
    ctx: Context,
    interface_filter: Optional[str] = None,
    disabled_only: bool = False,
) -> str:
    """
    Lists WireGuard peers on MikroTik device.

    Args:
        interface_filter: Filter by WireGuard interface name
        disabled_only: Show only disabled peers
    """
    await ctx.info("Listing WireGuard peers")

    cmd = "/interface wireguard peers print"

    filters = []
    if interface_filter:
        filters.append(f'interface="{interface_filter}"')
    if disabled_only:
        filters.append("disabled=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No WireGuard peers found."

    return f"WIREGUARD PEERS:\n\n{result}"


@mcp.tool(name="get_wireguard_peer", annotations=READ)
async def mikrotik_get_wireguard_peer(ctx: Context, peer_id: str) -> str:
    """
    Gets detailed information about a specific WireGuard peer.

    Args:
        peer_id: Peer ID (e.g. "*1" or the numeric ID from list output)
    """
    await ctx.info(f"Getting WireGuard peer details: peer_id={peer_id}")

    cmd = f"/interface wireguard peers print detail where .id={peer_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"WireGuard peer with ID '{peer_id}' not found."

    return f"WIREGUARD PEER DETAILS:\n\n{result}"


@mcp.tool(name="update_wireguard_peer", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_wireguard_peer(
    ctx: Context,
    peer_id: str,
    allowed_address: Optional[str] = None,
    endpoint_address: Optional[str] = None,
    endpoint_port: Optional[int] = None,
    preshared_key: Optional[str] = None,
    persistent_keepalive: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> str:
    """
    Updates an existing WireGuard peer on MikroTik device.

    Args:
        peer_id: Peer ID (e.g. "*1")
        allowed_address: New comma-separated allowed IP addresses/subnets
        endpoint_address: New remote peer address
        endpoint_port: New remote peer UDP port
        preshared_key: New preshared key (pass empty string "" to remove)
        persistent_keepalive: New keepalive interval (e.g. "25s", "0s" to disable)
        comment: New comment
        disabled: Enable (False) or disable (True) the peer
    """
    await ctx.info(f"Updating WireGuard peer: peer_id={peer_id}")

    updates = []
    if allowed_address is not None:
        updates.append(f'allowed-address="{allowed_address}"')
    if endpoint_address is not None:
        if endpoint_address == "":
            updates.append("!endpoint-address")
        else:
            updates.append(f'endpoint-address="{endpoint_address}"')
    if endpoint_port is not None:
        updates.append(f"endpoint-port={endpoint_port}")
    if preshared_key is not None:
        if preshared_key == "":
            updates.append("!preshared-key")
        else:
            updates.append(f'preshared-key="{preshared_key}"')
    if persistent_keepalive is not None:
        updates.append(f"persistent-keepalive={persistent_keepalive}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')

    if not updates:
        return "No updates specified."

    cmd = f"/interface wireguard peers set {peer_id} " + " ".join(updates)
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update WireGuard peer: {result}"

    details_cmd = f"/interface wireguard peers print detail where .id={peer_id}"
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"WireGuard peer updated successfully:\n\n{details}"


@mcp.tool(name="remove_wireguard_peer", annotations=DESTRUCTIVE)
async def mikrotik_remove_wireguard_peer(ctx: Context, peer_id: str) -> str:
    """
    Removes a WireGuard peer from MikroTik device.

    Args:
        peer_id: Peer ID (e.g. "*1")
    """
    await ctx.info(f"Removing WireGuard peer: peer_id={peer_id}")

    check_cmd = f"/interface wireguard peers print count-only where .id={peer_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"WireGuard peer with ID '{peer_id}' not found."

    cmd = f"/interface wireguard peers remove {peer_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove WireGuard peer: {result}"

    return f"WireGuard peer '{peer_id}' removed successfully."


@mcp.tool(name="enable_wireguard_peer", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_wireguard_peer(ctx: Context, peer_id: str) -> str:
    """
    Enables a WireGuard peer.

    Args:
        peer_id: Peer ID (e.g. "*1")
    """
    await ctx.info(f"Enabling WireGuard peer: peer_id={peer_id}")

    cmd = f"/interface wireguard peers enable {peer_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable WireGuard peer: {result}"

    return f"WireGuard peer '{peer_id}' enabled successfully."


@mcp.tool(name="disable_wireguard_peer", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_wireguard_peer(ctx: Context, peer_id: str) -> str:
    """
    Disables a WireGuard peer.

    Args:
        peer_id: Peer ID (e.g. "*1")
    """
    await ctx.info(f"Disabling WireGuard peer: peer_id={peer_id}")

    cmd = f"/interface wireguard peers disable {peer_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable WireGuard peer: {result}"

    return f"WireGuard peer '{peer_id}' disabled successfully."
