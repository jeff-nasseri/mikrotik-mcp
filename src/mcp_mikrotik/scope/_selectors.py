import re


_ID_RE = re.compile(r"\*[0-9A-Fa-f]+")


async def resolve_item_id(menu, item_id, ctx, device, execute):
    """Accept internal IDs or resolve a print position without RouterOS number maps."""
    item_id = item_id.strip()
    if _ID_RE.fullmatch(item_id):
        return item_id
    if not item_id.isascii() or not item_id.isdecimal():
        return None
    result = await execute(f":put [:pick [{menu} find] {int(item_id)}]", ctx, device=device)
    resolved = result.strip()
    return resolved if _ID_RE.fullmatch(resolved) else None


async def item_count(menu, item_id, ctx, device, execute):
    return (await execute(f"{menu} print count-only where .id={item_id}", ctx, device=device)).strip()


async def item_at_position(menu, position, ctx, device, execute):
    return (await execute(f":put [:pick [{menu} find] {position}]", ctx, device=device)).strip()
