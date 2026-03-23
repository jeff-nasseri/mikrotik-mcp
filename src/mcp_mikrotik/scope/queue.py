from typing import Literal, Optional
from mcp.server.fastmcp import Context
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE
from ..connector import execute_mikrotik_command


# ───────────────────────────────────────────────
# Queue Types
# ───────────────────────────────────────────────

@mcp.tool(name="create_queue_type", annotations=WRITE)
async def mikrotik_create_queue_type(
    ctx: Context,
    name: str,
    kind: Literal["cake", "fq-codel", "sfq", "red", "pcq", "pfifo", "bfifo",
                   "pfifo-bpf", "mq-pfifo", "none"] = "cake",
    cake_flowmode: Optional[Literal["triple-isolate", "dual-srchost", "dual-dsthost",
                                     "host", "flow", "none"]] = None,
    cake_nat: Optional[bool] = None,
    cake_overhead: Optional[int] = None,
    cake_mpu: Optional[int] = None,
    cake_diffserv: Optional[Literal["besteffort", "diffserv3", "diffserv4", "diffserv8"]] = None,
    cake_ack_filter: Optional[Literal["filter", "aggressive", "none"]] = None,
    cake_rtt: Optional[str] = None,
    cake_wash: Optional[bool] = None,
    cake_overhead_scheme: Optional[str] = None,
    pcq_rate: Optional[str] = None,
    pcq_limit: Optional[int] = None,
    pcq_classifier: Optional[str] = None,
    pfifo_limit: Optional[int] = None,
    bfifo_limit: Optional[int] = None,
    sfq_perturb: Optional[int] = None,
    sfq_allot: Optional[int] = None,
    fq_codel_limit: Optional[int] = None,
    fq_codel_quantum: Optional[int] = None,
    fq_codel_target: Optional[str] = None,
    fq_codel_interval: Optional[str] = None,
    red_limit: Optional[int] = None,
    red_min_threshold: Optional[int] = None,
    red_max_threshold: Optional[int] = None,
    red_burst: Optional[int] = None,
    red_avg_packet: Optional[int] = None,
) -> str:
    """
    Creates a queue type on MikroTik device.

    Args:
        name: Name of the queue type
        kind: Queue discipline (cake, fq-codel, sfq, red, pcq, pfifo, bfifo, etc.)
        cake_flowmode: CAKE flow isolation mode (triple-isolate, dual-srchost, dual-dsthost, host, flow, none)
        cake_nat: CAKE NAT awareness (for correct flow identification behind NAT)
        cake_overhead: CAKE per-packet overhead in bytes (e.g., 34 for PPPoE)
        cake_mpu: CAKE minimum packet unit in bytes (e.g., 84 for PPPoE)
        cake_diffserv: CAKE DSCP priority scheme (besteffort, diffserv3, diffserv4, diffserv8)
        cake_ack_filter: CAKE ACK filter mode (filter, aggressive, none)
        cake_rtt: CAKE RTT estimate (e.g., "100ms")
        cake_wash: CAKE DSCP wash (clear DSCP on egress)
        cake_overhead_scheme: CAKE overhead scheme preset (e.g., "ethernet", "pppoe-ptm")
        pcq_rate: PCQ per-connection rate limit
        pcq_limit: PCQ queue size limit
        pcq_classifier: PCQ classifier (src-address, dst-address, both-addresses, etc.)
        pfifo_limit: PFIFO packet limit
        bfifo_limit: BFIFO byte limit
        sfq_perturb: SFQ hash perturbation interval
        sfq_allot: SFQ allotment
        fq_codel_limit: FQ-CoDel queue limit
        fq_codel_quantum: FQ-CoDel quantum
        fq_codel_target: FQ-CoDel target delay (e.g., "5ms")
        fq_codel_interval: FQ-CoDel interval (e.g., "100ms")
        red_limit: RED queue limit
        red_min_threshold: RED minimum threshold
        red_max_threshold: RED maximum threshold
        red_burst: RED burst size
        red_avg_packet: RED average packet size

    Returns:
        Command output or error message
    """
    await ctx.info(f"Creating queue type: name={name}, kind={kind}")

    cmd = f"/queue type add name={name} kind={kind}"

    # CAKE parameters
    if cake_flowmode is not None:
        cmd += f" cake-flowmode={cake_flowmode}"
    if cake_nat is not None:
        cmd += f' cake-nat={"yes" if cake_nat else "no"}'
    if cake_overhead is not None:
        cmd += f" cake-overhead={cake_overhead}"
    if cake_mpu is not None:
        cmd += f" cake-mpu={cake_mpu}"
    if cake_diffserv is not None:
        cmd += f" cake-diffserv={cake_diffserv}"
    if cake_ack_filter is not None:
        cmd += f" cake-ack-filter={cake_ack_filter}"
    if cake_rtt is not None:
        cmd += f" cake-rtt={cake_rtt}"
    if cake_wash is not None:
        cmd += f' cake-wash={"yes" if cake_wash else "no"}'
    if cake_overhead_scheme is not None:
        cmd += f" cake-overhead-scheme={cake_overhead_scheme}"

    # PCQ parameters
    if pcq_rate is not None:
        cmd += f" pcq-rate={pcq_rate}"
    if pcq_limit is not None:
        cmd += f" pcq-limit={pcq_limit}"
    if pcq_classifier is not None:
        cmd += f" pcq-classifier={pcq_classifier}"

    # PFIFO/BFIFO parameters
    if pfifo_limit is not None:
        cmd += f" pfifo-limit={pfifo_limit}"
    if bfifo_limit is not None:
        cmd += f" bfifo-limit={bfifo_limit}"

    # SFQ parameters
    if sfq_perturb is not None:
        cmd += f" sfq-perturb={sfq_perturb}"
    if sfq_allot is not None:
        cmd += f" sfq-allot={sfq_allot}"

    # FQ-CoDel parameters
    if fq_codel_limit is not None:
        cmd += f" fq-codel-limit={fq_codel_limit}"
    if fq_codel_quantum is not None:
        cmd += f" fq-codel-quantum={fq_codel_quantum}"
    if fq_codel_target is not None:
        cmd += f" fq-codel-target={fq_codel_target}"
    if fq_codel_interval is not None:
        cmd += f" fq-codel-interval={fq_codel_interval}"

    # RED parameters
    if red_limit is not None:
        cmd += f" red-limit={red_limit}"
    if red_min_threshold is not None:
        cmd += f" red-min-threshold={red_min_threshold}"
    if red_max_threshold is not None:
        cmd += f" red-max-threshold={red_max_threshold}"
    if red_burst is not None:
        cmd += f" red-burst={red_burst}"
    if red_avg_packet is not None:
        cmd += f" red-avg-packet={red_avg_packet}"

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            type_id = result.strip()
            details_cmd = f"/queue type print detail where .id={type_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)
            if details.strip():
                return f"Queue type created successfully:\n\n{details}"
            return f"Queue type created with ID: {type_id}"
        elif "failure:" in result.lower() or "error" in result.lower():
            return f"Failed to create queue type: {result}"

    # Verify by fetching by name
    details_cmd = f'/queue type print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    if details.strip():
        return f"Queue type created successfully:\n\n{details}"
    return "Queue type creation completed but unable to verify."


@mcp.tool(name="list_queue_types", annotations=READ)
async def mikrotik_list_queue_types(
    ctx: Context,
    name_filter: Optional[str] = None,
    kind_filter: Optional[str] = None,
) -> str:
    """
    Lists queue types on MikroTik device.

    Args:
        name_filter: Filter by name (partial match)
        kind_filter: Filter by kind (cake, fq-codel, sfq, etc.)

    Returns:
        List of queue types
    """
    await ctx.info("Listing queue types")

    cmd = "/queue type print"
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if kind_filter:
        filters.append(f"kind={kind_filter}")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return "No queue types found matching the criteria."
    return f"QUEUE TYPES:\n\n{result}"


@mcp.tool(name="get_queue_type", annotations=READ)
async def mikrotik_get_queue_type(ctx: Context, name: str) -> str:
    """
    Gets detailed information about a specific queue type.

    Args:
        name: Name of the queue type

    Returns:
        Detailed information about the queue type
    """
    await ctx.info(f"Getting queue type details: name={name}")

    cmd = f'/queue type print detail where name="{name}"'
    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return f"Queue type '{name}' not found."
    return f"QUEUE TYPE DETAILS:\n\n{result}"


@mcp.tool(name="update_queue_type", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_queue_type(
    ctx: Context,
    name: str,
    new_name: Optional[str] = None,
    cake_flowmode: Optional[str] = None,
    cake_nat: Optional[bool] = None,
    cake_overhead: Optional[int] = None,
    cake_mpu: Optional[int] = None,
    cake_diffserv: Optional[str] = None,
    cake_ack_filter: Optional[str] = None,
    cake_rtt: Optional[str] = None,
    cake_wash: Optional[bool] = None,
    cake_overhead_scheme: Optional[str] = None,
    pcq_rate: Optional[str] = None,
    pcq_limit: Optional[int] = None,
    pcq_classifier: Optional[str] = None,
) -> str:
    """
    Updates an existing queue type on MikroTik device.

    Args:
        name: Current name of the queue type
        new_name: New name for the queue type
        cake_flowmode: New CAKE flow mode
        cake_nat: New CAKE NAT setting
        cake_overhead: New CAKE overhead value
        cake_mpu: New CAKE MPU value
        cake_diffserv: New CAKE diffserv scheme
        cake_ack_filter: New CAKE ACK filter mode (filter, aggressive, none)
        cake_rtt: New CAKE RTT estimate
        cake_wash: New CAKE wash setting
        cake_overhead_scheme: New CAKE overhead scheme
        pcq_rate: New PCQ rate
        pcq_limit: New PCQ limit
        pcq_classifier: New PCQ classifier

    Returns:
        Command output or error message
    """
    await ctx.info(f"Updating queue type: name={name}")

    cmd = f'/queue type set [find name="{name}"]'

    updates = []
    if new_name is not None:
        updates.append(f"name={new_name}")
    if cake_flowmode is not None:
        updates.append(f"cake-flowmode={cake_flowmode}")
    if cake_nat is not None:
        updates.append(f'cake-nat={"yes" if cake_nat else "no"}')
    if cake_overhead is not None:
        updates.append(f"cake-overhead={cake_overhead}")
    if cake_mpu is not None:
        updates.append(f"cake-mpu={cake_mpu}")
    if cake_diffserv is not None:
        updates.append(f"cake-diffserv={cake_diffserv}")
    if cake_ack_filter is not None:
        updates.append(f"cake-ack-filter={cake_ack_filter}")
    if cake_rtt is not None:
        updates.append(f"cake-rtt={cake_rtt}")
    if cake_wash is not None:
        updates.append(f'cake-wash={"yes" if cake_wash else "no"}')
    if cake_overhead_scheme is not None:
        updates.append(f"cake-overhead-scheme={cake_overhead_scheme}")
    if pcq_rate is not None:
        updates.append(f"pcq-rate={pcq_rate}")
    if pcq_limit is not None:
        updates.append(f"pcq-limit={pcq_limit}")
    if pcq_classifier is not None:
        updates.append(f"pcq-classifier={pcq_classifier}")

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update queue type: {result}"

    lookup_name = new_name if new_name else name
    details_cmd = f'/queue type print detail where name="{lookup_name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Queue type updated successfully:\n\n{details}"


@mcp.tool(name="remove_queue_type", annotations=DESTRUCTIVE)
async def mikrotik_remove_queue_type(ctx: Context, name: str) -> str:
    """
    Removes a queue type from MikroTik device.

    Args:
        name: Name of the queue type to remove

    Returns:
        Command output or error message
    """
    await ctx.info(f"Removing queue type: name={name}")

    cmd = f'/queue type remove [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove queue type: {result}"
    return f"Queue type '{name}' removed successfully."


# ───────────────────────────────────────────────
# Queue Trees
# ───────────────────────────────────────────────

@mcp.tool(name="create_queue_tree", annotations=WRITE)
async def mikrotik_create_queue_tree(
    ctx: Context,
    name: str,
    parent: str,
    queue: Optional[str] = None,
    packet_mark: Optional[str] = None,
    max_limit: Optional[str] = None,
    limit_at: Optional[str] = None,
    burst_limit: Optional[str] = None,
    burst_threshold: Optional[str] = None,
    burst_time: Optional[str] = None,
    bucket_size: Optional[str] = None,
    priority: Optional[int] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
) -> str:
    """
    Creates a queue tree on MikroTik device.

    Args:
        name: Name of the queue tree
        parent: Parent interface or queue (e.g., "bridge", "pppoe-out1", "global")
        queue: Queue type name to use (e.g., "cake-upload", "default-small")
        packet_mark: Packet mark to match (e.g., "no-mark", or a mangle mark)
        max_limit: Maximum bandwidth limit (e.g., "100M", "1G")
        limit_at: Guaranteed bandwidth (CIR)
        burst_limit: Burst bandwidth limit
        burst_threshold: Burst threshold
        burst_time: Burst time
        bucket_size: Bucket size for shaping (e.g., "0.01")
        priority: Queue priority (1-8, lower = higher priority)
        comment: Optional comment
        disabled: Whether to disable after creation

    Returns:
        Command output or error message
    """
    await ctx.info(f"Creating queue tree: name={name}, parent={parent}")

    cmd = f"/queue tree add name={name} parent={parent}"

    if queue is not None:
        cmd += f" queue={queue}"
    if packet_mark is not None:
        cmd += f" packet-mark={packet_mark}"
    if max_limit is not None:
        cmd += f" max-limit={max_limit}"
    if limit_at is not None:
        cmd += f" limit-at={limit_at}"
    if burst_limit is not None:
        cmd += f" burst-limit={burst_limit}"
    if burst_threshold is not None:
        cmd += f" burst-threshold={burst_threshold}"
    if burst_time is not None:
        cmd += f" burst-time={burst_time}"
    if bucket_size is not None:
        cmd += f" bucket-size={bucket_size}"
    if priority is not None:
        cmd += f" priority={priority}"
    if comment:
        cmd += f' comment="{comment}"'
    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            tree_id = result.strip()
            details_cmd = f"/queue tree print detail where .id={tree_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)
            if details.strip():
                return f"Queue tree created successfully:\n\n{details}"
            return f"Queue tree created with ID: {tree_id}"
        elif "failure:" in result.lower() or "error" in result.lower():
            return f"Failed to create queue tree: {result}"

    details_cmd = f'/queue tree print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    if details.strip():
        return f"Queue tree created successfully:\n\n{details}"
    return "Queue tree creation completed but unable to verify."


@mcp.tool(name="list_queue_trees", annotations=READ)
async def mikrotik_list_queue_trees(
    ctx: Context,
    name_filter: Optional[str] = None,
    parent_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False,
) -> str:
    """
    Lists queue trees on MikroTik device.

    Args:
        name_filter: Filter by name (partial match)
        parent_filter: Filter by parent interface or queue
        disabled_only: Show only disabled queue trees
        invalid_only: Show only invalid queue trees

    Returns:
        List of queue trees
    """
    await ctx.info("Listing queue trees")

    cmd = "/queue tree print"
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if parent_filter:
        filters.append(f'parent="{parent_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if invalid_only:
        filters.append("invalid=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return "No queue trees found matching the criteria."
    return f"QUEUE TREES:\n\n{result}"


@mcp.tool(name="get_queue_tree", annotations=READ)
async def mikrotik_get_queue_tree(ctx: Context, name: str) -> str:
    """
    Gets detailed information about a specific queue tree.

    Args:
        name: Name of the queue tree

    Returns:
        Detailed information about the queue tree
    """
    await ctx.info(f"Getting queue tree details: name={name}")

    cmd = f'/queue tree print detail where name="{name}"'
    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return f"Queue tree '{name}' not found."
    return f"QUEUE TREE DETAILS:\n\n{result}"


@mcp.tool(name="update_queue_tree", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_queue_tree(
    ctx: Context,
    name: str,
    new_name: Optional[str] = None,
    parent: Optional[str] = None,
    queue: Optional[str] = None,
    packet_mark: Optional[str] = None,
    max_limit: Optional[str] = None,
    limit_at: Optional[str] = None,
    burst_limit: Optional[str] = None,
    burst_threshold: Optional[str] = None,
    burst_time: Optional[str] = None,
    bucket_size: Optional[str] = None,
    priority: Optional[int] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> str:
    """
    Updates an existing queue tree on MikroTik device.

    Args:
        name: Current name of the queue tree
        new_name: New name for the queue tree
        parent: New parent interface or queue
        queue: New queue type name
        packet_mark: New packet mark
        max_limit: New maximum bandwidth limit
        limit_at: New guaranteed bandwidth
        burst_limit: New burst limit
        burst_threshold: New burst threshold
        burst_time: New burst time
        bucket_size: New bucket size
        priority: New priority (1-8)
        comment: New comment
        disabled: Enable/disable the queue tree

    Returns:
        Command output or error message
    """
    await ctx.info(f"Updating queue tree: name={name}")

    cmd = f'/queue tree set [find name="{name}"]'

    updates = []
    if new_name is not None:
        updates.append(f"name={new_name}")
    if parent is not None:
        updates.append(f"parent={parent}")
    if queue is not None:
        updates.append(f"queue={queue}")
    if packet_mark is not None:
        updates.append(f"packet-mark={packet_mark}")
    if max_limit is not None:
        updates.append(f"max-limit={max_limit}")
    if limit_at is not None:
        updates.append(f"limit-at={limit_at}")
    if burst_limit is not None:
        updates.append(f"burst-limit={burst_limit}")
    if burst_threshold is not None:
        updates.append(f"burst-threshold={burst_threshold}")
    if burst_time is not None:
        updates.append(f"burst-time={burst_time}")
    if bucket_size is not None:
        updates.append(f"bucket-size={bucket_size}")
    if priority is not None:
        updates.append(f"priority={priority}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update queue tree: {result}"

    lookup_name = new_name if new_name else name
    details_cmd = f'/queue tree print detail where name="{lookup_name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Queue tree updated successfully:\n\n{details}"


@mcp.tool(name="remove_queue_tree", annotations=DESTRUCTIVE)
async def mikrotik_remove_queue_tree(ctx: Context, name: str) -> str:
    """
    Removes a queue tree from MikroTik device.

    Args:
        name: Name of the queue tree to remove

    Returns:
        Command output or error message
    """
    await ctx.info(f"Removing queue tree: name={name}")

    cmd = f'/queue tree remove [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove queue tree: {result}"
    return f"Queue tree '{name}' removed successfully."


@mcp.tool(name="enable_queue_tree", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_queue_tree(ctx: Context, name: str) -> str:
    """
    Enables a queue tree.

    Args:
        name: Name of the queue tree to enable

    Returns:
        Command output or error message
    """
    await ctx.info(f"Enabling queue tree: name={name}")

    cmd = f'/queue tree set [find name="{name}"] disabled=no'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable queue tree: {result}"

    details_cmd = f'/queue tree print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Queue tree enabled:\n\n{details}"


@mcp.tool(name="disable_queue_tree", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_queue_tree(ctx: Context, name: str) -> str:
    """
    Disables a queue tree.

    Args:
        name: Name of the queue tree to disable

    Returns:
        Command output or error message
    """
    await ctx.info(f"Disabling queue tree: name={name}")

    cmd = f'/queue tree set [find name="{name}"] disabled=yes'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable queue tree: {result}"

    details_cmd = f'/queue tree print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Queue tree disabled:\n\n{details}"


# ───────────────────────────────────────────────
# Simple Queues
# ───────────────────────────────────────────────

@mcp.tool(name="create_simple_queue", annotations=WRITE)
async def mikrotik_create_simple_queue(
    ctx: Context,
    name: str,
    target: str,
    dst: Optional[str] = None,
    max_limit: Optional[str] = None,
    limit_at: Optional[str] = None,
    burst_limit: Optional[str] = None,
    burst_threshold: Optional[str] = None,
    burst_time: Optional[str] = None,
    bucket_size: Optional[str] = None,
    queue: Optional[str] = None,
    parent: Optional[str] = None,
    priority: Optional[str] = None,
    packet_marks: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
) -> str:
    """
    Creates a simple queue on MikroTik device.

    Args:
        name: Name of the simple queue
        target: Target address or interface (e.g., "192.168.1.0/24", "ether1")
        dst: Destination address (e.g., "0.0.0.0/0")
        max_limit: Max upload/download limit (e.g., "10M/10M")
        limit_at: Guaranteed upload/download rate (e.g., "5M/5M")
        burst_limit: Burst upload/download limit
        burst_threshold: Burst threshold
        burst_time: Burst time
        bucket_size: Bucket size (e.g., "0.1/0.1")
        queue: Queue type for upload/download (e.g., "default-small/default-small")
        parent: Parent queue name
        priority: Priority for upload/download (e.g., "8/8")
        packet_marks: Packet marks to match
        comment: Optional comment
        disabled: Whether to disable after creation

    Returns:
        Command output or error message
    """
    await ctx.info(f"Creating simple queue: name={name}, target={target}")

    cmd = f"/queue simple add name={name} target={target}"

    if dst is not None:
        cmd += f" dst={dst}"
    if max_limit is not None:
        cmd += f" max-limit={max_limit}"
    if limit_at is not None:
        cmd += f" limit-at={limit_at}"
    if burst_limit is not None:
        cmd += f" burst-limit={burst_limit}"
    if burst_threshold is not None:
        cmd += f" burst-threshold={burst_threshold}"
    if burst_time is not None:
        cmd += f" burst-time={burst_time}"
    if bucket_size is not None:
        cmd += f" bucket-size={bucket_size}"
    if queue is not None:
        cmd += f" queue={queue}"
    if parent is not None:
        cmd += f" parent={parent}"
    if priority is not None:
        cmd += f" priority={priority}"
    if packet_marks is not None:
        cmd += f" packet-marks={packet_marks}"
    if comment:
        cmd += f' comment="{comment}"'
    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            queue_id = result.strip()
            details_cmd = f"/queue simple print detail where .id={queue_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)
            if details.strip():
                return f"Simple queue created successfully:\n\n{details}"
            return f"Simple queue created with ID: {queue_id}"
        elif "failure:" in result.lower() or "error" in result.lower():
            return f"Failed to create simple queue: {result}"

    details_cmd = f'/queue simple print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    if details.strip():
        return f"Simple queue created successfully:\n\n{details}"
    return "Simple queue creation completed but unable to verify."


@mcp.tool(name="list_simple_queues", annotations=READ)
async def mikrotik_list_simple_queues(
    ctx: Context,
    name_filter: Optional[str] = None,
    target_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False,
) -> str:
    """
    Lists simple queues on MikroTik device.

    Args:
        name_filter: Filter by name (partial match)
        target_filter: Filter by target address
        disabled_only: Show only disabled queues
        invalid_only: Show only invalid queues

    Returns:
        List of simple queues
    """
    await ctx.info("Listing simple queues")

    cmd = "/queue simple print"
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if target_filter:
        filters.append(f'target~"{target_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if invalid_only:
        filters.append("invalid=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return "No simple queues found matching the criteria."
    return f"SIMPLE QUEUES:\n\n{result}"


@mcp.tool(name="get_simple_queue", annotations=READ)
async def mikrotik_get_simple_queue(ctx: Context, name: str) -> str:
    """
    Gets detailed information about a specific simple queue.

    Args:
        name: Name of the simple queue

    Returns:
        Detailed information about the simple queue
    """
    await ctx.info(f"Getting simple queue details: name={name}")

    cmd = f'/queue simple print detail where name="{name}"'
    result = await execute_mikrotik_command(cmd, ctx)
    if not result or result.strip() == "":
        return f"Simple queue '{name}' not found."
    return f"SIMPLE QUEUE DETAILS:\n\n{result}"


@mcp.tool(name="update_simple_queue", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_simple_queue(
    ctx: Context,
    name: str,
    new_name: Optional[str] = None,
    target: Optional[str] = None,
    dst: Optional[str] = None,
    max_limit: Optional[str] = None,
    limit_at: Optional[str] = None,
    burst_limit: Optional[str] = None,
    burst_threshold: Optional[str] = None,
    burst_time: Optional[str] = None,
    bucket_size: Optional[str] = None,
    queue: Optional[str] = None,
    parent: Optional[str] = None,
    priority: Optional[str] = None,
    packet_marks: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> str:
    """
    Updates an existing simple queue on MikroTik device.

    Args:
        name: Current name of the simple queue
        new_name: New name
        target: New target address
        dst: New destination address
        max_limit: New max upload/download limit
        limit_at: New guaranteed rate
        burst_limit: New burst limit
        burst_threshold: New burst threshold
        burst_time: New burst time
        bucket_size: New bucket size
        queue: New queue type
        parent: New parent queue
        priority: New priority
        packet_marks: New packet marks
        comment: New comment
        disabled: Enable/disable the queue

    Returns:
        Command output or error message
    """
    await ctx.info(f"Updating simple queue: name={name}")

    cmd = f'/queue simple set [find name="{name}"]'

    updates = []
    if new_name is not None:
        updates.append(f"name={new_name}")
    if target is not None:
        updates.append(f"target={target}")
    if dst is not None:
        updates.append(f"dst={dst}")
    if max_limit is not None:
        updates.append(f"max-limit={max_limit}")
    if limit_at is not None:
        updates.append(f"limit-at={limit_at}")
    if burst_limit is not None:
        updates.append(f"burst-limit={burst_limit}")
    if burst_threshold is not None:
        updates.append(f"burst-threshold={burst_threshold}")
    if burst_time is not None:
        updates.append(f"burst-time={burst_time}")
    if bucket_size is not None:
        updates.append(f"bucket-size={bucket_size}")
    if queue is not None:
        updates.append(f"queue={queue}")
    if parent is not None:
        updates.append(f"parent={parent}")
    if priority is not None:
        updates.append(f"priority={priority}")
    if packet_marks is not None:
        updates.append(f"packet-marks={packet_marks}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update simple queue: {result}"

    lookup_name = new_name if new_name else name
    details_cmd = f'/queue simple print detail where name="{lookup_name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Simple queue updated successfully:\n\n{details}"


@mcp.tool(name="remove_simple_queue", annotations=DESTRUCTIVE)
async def mikrotik_remove_simple_queue(ctx: Context, name: str) -> str:
    """
    Removes a simple queue from MikroTik device.

    Args:
        name: Name of the simple queue to remove

    Returns:
        Command output or error message
    """
    await ctx.info(f"Removing simple queue: name={name}")

    cmd = f'/queue simple remove [find name="{name}"]'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove simple queue: {result}"
    return f"Simple queue '{name}' removed successfully."


@mcp.tool(name="enable_simple_queue", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_simple_queue(ctx: Context, name: str) -> str:
    """
    Enables a simple queue.

    Args:
        name: Name of the simple queue to enable

    Returns:
        Command output or error message
    """
    await ctx.info(f"Enabling simple queue: name={name}")

    cmd = f'/queue simple set [find name="{name}"] disabled=no'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable simple queue: {result}"

    details_cmd = f'/queue simple print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Simple queue enabled:\n\n{details}"


@mcp.tool(name="disable_simple_queue", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_simple_queue(ctx: Context, name: str) -> str:
    """
    Disables a simple queue.

    Args:
        name: Name of the simple queue to disable

    Returns:
        Command output or error message
    """
    await ctx.info(f"Disabling simple queue: name={name}")

    cmd = f'/queue simple set [find name="{name}"] disabled=yes'
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable simple queue: {result}"

    details_cmd = f'/queue simple print detail where name="{name}"'
    details = await execute_mikrotik_command(details_cmd, ctx)
    return f"Simple queue disabled:\n\n{details}"
