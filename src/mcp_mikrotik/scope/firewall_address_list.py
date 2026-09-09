import ipaddress
from typing import Literal, Optional

from ..connector import execute_mikrotik_command
from mcp.server.mcpserver import Context
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE, annotate

Family = Literal["ipv4", "ipv6"]


def _tree(family: str) -> str:
    return "/ipv6 firewall address-list" if family == "ipv6" else "/ip firewall address-list"


def _canonical(family: str, address: str) -> str:
    """Return the address as RouterOS stores it.

    The IPv6 list keeps host entries with an explicit /128 and lowercases the
    address, so "2001:DB8::5" has to become "2001:db8::5/128" or an exact
    `where address=` comparison finds nothing. IPv4 is stored verbatim.
    Unparseable input is returned unchanged.
    """
    if family != "ipv6":
        return address
    try:
        if "/" in address:
            return str(ipaddress.ip_interface(address))
        return f"{ipaddress.ip_address(address)}/128"
    except ValueError:
        return address


def _selector(family: str, list_name: str, address: str) -> str:
    return f'list="{list_name}" address="{_canonical(family, address)}"'


async def _count(family: str, where: str, ctx: Context, device: Optional[str]) -> str:
    out = await execute_mikrotik_command(
        f"{_tree(family)} print count-only where {where}", ctx, device=device
    )
    return out.strip()


@mcp.tool(name="create_address_list_entry", annotations=annotate(WRITE, "Create Address List Entry"))
async def mikrotik_create_address_list_entry(
    ctx: Context,
    family: Family,
    list_name: str,
    address: str,
    comment: Optional[str] = None,
    timeout: Optional[str] = None,
    disabled: bool = False,
    device: Optional[str] = None,
) -> str:
    """Adds an entry to an IPv4 or IPv6 firewall address list.

    Notes:
        address: an address or prefix; a hostname is also accepted and RouterOS
            adds a dynamic child entry per resolved address.
        timeout: RouterOS duration e.g. "1h". An entry with a timeout is
            dynamic, so it does not survive a reboot.
        list_name is matched exactly, including any leading or trailing spaces.
    """
    await ctx.info(f"Creating {family} address list entry: list={list_name}, address={address}")

    cmd = f'{_tree(family)} add list="{list_name}" address={address}'
    if comment:
        cmd += f' comment="{comment}"'
    if timeout:
        cmd += f" timeout={timeout}"
    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    # A successful add prints nothing or the new id; anything else is RouterOS
    # refusing, and not every refusal says "failure:" or "error".
    if result.strip() and "*" not in result and not result.strip().isdigit():
        return f"Failed to create address list entry: {result}"

    details = await execute_mikrotik_command(
        f'{_tree(family)} print detail where {_selector(family, list_name, address)}',
        ctx, device=device,
    )
    if "address=" in details:
        return f"Address list entry created successfully:\n\n{details}"
    return f"Address list entry '{address}' added to '{list_name}'."


@mcp.tool(name="list_address_list_entries", annotations=annotate(READ, "List Address List Entries"))
async def mikrotik_list_address_list_entries(
    ctx: Context,
    family: Family,
    list_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    comment_filter: Optional[str] = None,
    disabled_only: bool = False,
    dynamic_only: bool = False,
    static_only: bool = False,
    device: Optional[str] = None,
) -> str:
    """Lists IPv4 or IPv6 firewall address list entries.

    Notes:
        list_filter: exact list name, including any trailing space.
        address_filter/comment_filter: partial match.
        static_only excludes the dynamic children a hostname entry creates.
    """
    await ctx.info(f"Listing {family} address list entries: list={list_filter}")

    filters = []
    if list_filter:
        filters.append(f'list="{list_filter}"')
    if address_filter:
        filters.append(f'address~"{address_filter}"')
    if comment_filter:
        filters.append(f'comment~"{comment_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if dynamic_only:
        filters.append("dynamic")
    if static_only:
        filters.append("!dynamic")

    cmd = f"{_tree(family)} print"
    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx, device=device)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No address list entries found matching the criteria."

    return f"{family.upper()} ADDRESS LIST ENTRIES:\n\n{result}"


@mcp.tool(name="get_address_list_entry", annotations=annotate(READ, "Get Address List Entry"))
async def mikrotik_get_address_list_entry(
    ctx: Context, family: Family, list_name: str, address: str, device: Optional[str] = None
) -> str:
    """Gets one address list entry by list name and address."""
    await ctx.info(f"Getting {family} address list entry: list={list_name}, address={address}")

    result = await execute_mikrotik_command(
        f'{_tree(family)} print detail where {_selector(family, list_name, address)}',
        ctx, device=device,
    )

    # `print detail` emits the Flags legend even when nothing matches.
    if not result or "address=" not in result:
        return f"Address list entry '{address}' not found in '{list_name}'."

    return f"{family.upper()} ADDRESS LIST ENTRY:\n\n{result}"


@mcp.tool(name="update_address_list_entry", annotations=annotate(WRITE_IDEMPOTENT, "Update Address List Entry"))
async def mikrotik_update_address_list_entry(
    ctx: Context,
    family: Family,
    list_name: str,
    address: str,
    new_list_name: Optional[str] = None,
    comment: Optional[str] = None,
    timeout: Optional[str] = None,
    disabled: Optional[bool] = None,
    device: Optional[str] = None,
) -> str:
    """Updates an address list entry, located by its current list name and address.

    Notes:
        Pass "" to clear comment or timeout.
    """
    await ctx.info(f"Updating {family} address list entry: list={list_name}, address={address}")

    updates = []
    if new_list_name:
        updates.append(f'list="{new_list_name}"')
    if comment is not None:
        updates.append("!comment" if comment == "" else f'comment="{comment}"')
    if timeout is not None:
        updates.append("!timeout" if timeout == "" else f"timeout={timeout}")
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')

    if not updates:
        return "No updates specified."

    where = _selector(family, list_name, address)
    if await _count(family, where, ctx, device) == "0":
        return f"Address list entry '{address}' not found in '{list_name}'."

    result = await execute_mikrotik_command(
        f"{_tree(family)} set [find {where}] " + " ".join(updates), ctx, device=device
    )
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update address list entry: {result}"

    lookup = _selector(family, new_list_name or list_name, address)
    details = await execute_mikrotik_command(
        f"{_tree(family)} print detail where {lookup}", ctx, device=device
    )
    if "address=" not in details:
        return f"Failed to update address list entry: {result or details}"

    return f"Address list entry updated successfully:\n\n{details}"


@mcp.tool(name="remove_address_list_entry", annotations=annotate(DESTRUCTIVE, "Remove Address List Entry"))
async def mikrotik_remove_address_list_entry(
    ctx: Context, family: Family, list_name: str, address: str, device: Optional[str] = None
) -> str:
    """Removes an address list entry by list name and address.

    Notes:
        Removes every entry matching the pair, dynamic ones included.
    """
    await ctx.info(f"Removing {family} address list entry: list={list_name}, address={address}")

    where = _selector(family, list_name, address)
    if await _count(family, where, ctx, device) == "0":
        return f"Address list entry '{address}' not found in '{list_name}'."

    result = await execute_mikrotik_command(
        f"{_tree(family)} remove [find {where}]", ctx, device=device
    )
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove address list entry: {result}"

    return f"Address list entry '{address}' removed from '{list_name}'."


@mcp.tool(name="enable_address_list_entry", annotations=annotate(WRITE_IDEMPOTENT, "Enable Address List Entry"))
async def mikrotik_enable_address_list_entry(
    ctx: Context, family: Family, list_name: str, address: str, device: Optional[str] = None
) -> str:
    """Enables an address list entry."""
    return await mikrotik_update_address_list_entry(
        ctx, family, list_name, address, disabled=False, device=device
    )


@mcp.tool(name="disable_address_list_entry", annotations=annotate(WRITE_IDEMPOTENT, "Disable Address List Entry"))
async def mikrotik_disable_address_list_entry(
    ctx: Context, family: Family, list_name: str, address: str, device: Optional[str] = None
) -> str:
    """Disables an address list entry."""
    return await mikrotik_update_address_list_entry(
        ctx, family, list_name, address, disabled=True, device=device
    )
