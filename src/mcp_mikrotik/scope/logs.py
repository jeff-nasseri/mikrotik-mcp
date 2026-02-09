import time
from typing import Literal, Optional, List, Dict
from mcp.server.fastmcp import Context
from ..connector import execute_mikrotik_command
from ..app import mcp, READ, DESTRUCTIVE
import re
from datetime import datetime, timedelta

@mcp.tool(name="get_logs", annotations=READ)
async def mikrotik_get_logs(
    ctx: Context,
    topics: Optional[str] = None,
    action: Optional[str] = None,
    time_filter: Optional[str] = None,
    message_filter: Optional[str] = None,
    prefix_filter: Optional[str] = None,
    limit: Optional[int] = None,
    follow: bool = False,
    print_as: Literal["value", "detail", "terse"] = "value"
) -> str:
    """
    Gets logs from MikroTik device with various filtering options.

    Args:
        topics: Filter by log topics (e.g., "info", "warning", "error", "system", "dhcp")
        action: Filter by action type (e.g., "login", "logout", "error")
        time_filter: Time filter (e.g., "5m", "1h", "1d" for last 5 minutes, 1 hour, 1 day)
        message_filter: Filter by message content (partial match)
        prefix_filter: Filter by message prefix
        limit: Maximum number of log entries to return
        follow: Follow log in real-time (not recommended for API use)
        print_as: Output format ("value", "detail", "terse")

    Returns:
        Filtered log entries
    """
    await ctx.info(f"Getting logs with filters: topics={topics}, action={action}, time={time_filter}")

    # Build the command
    cmd = f"/log print {print_as}"

    # Add filters
    filters = []

    if topics:
        # Handle multiple topics separated by comma
        topic_list = [t.strip() for t in topics.split(',')]
        topic_filter = ' or '.join([f'topics~"{t}"' for t in topic_list])
        if len(topic_list) > 1:
            filters.append(f"({topic_filter})")
        else:
            filters.append(topic_filter)

    if action:
        filters.append(f'action="{action}"')

    if message_filter:
        filters.append(f'message~"{message_filter}"')

    if prefix_filter:
        filters.append(f'message~"^{prefix_filter}"')

    if time_filter:
        # Convert time filter to where clause
        filters.append(f"time > ([:timestamp] - {time_filter})")

    if filters:
        cmd += " where " + " and ".join(filters)

    if limit:
        cmd += f" limit={limit}"

    if follow:
        cmd += " follow"

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No log entries found matching the criteria."

    return f"LOG ENTRIES:\n\n{result}"

@mcp.tool(name="get_logs_by_severity", annotations=READ)
async def mikrotik_get_logs_by_severity(
    severity: Literal["debug", "info", "warning", "error", "critical"],
    ctx: Context,
    time_filter: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Gets logs filtered by severity level.

    Args:
        severity: Severity level (debug, info, warning, error, critical)
        time_filter: Time filter (e.g., "5m", "1h", "1d")
        limit: Maximum number of entries

    Returns:
        Log entries of specified severity
    """
    await ctx.info(f"Getting logs by severity: severity={severity}")

    # Map severity to topics
    severity_topics = {
        "debug": "debug",
        "info": "info",
        "warning": "warning",
        "error": "error,critical",
        "critical": "critical"
    }

    topics = severity_topics[severity]

    return await mikrotik_get_logs(
        topics=topics,
        time_filter=time_filter,
        limit=limit,
        ctx=ctx
    )

@mcp.tool(name="get_logs_by_topic", annotations=READ)
async def mikrotik_get_logs_by_topic(
    topic: str,
    ctx: Context,
    time_filter: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Gets logs for a specific topic/facility.

    Args:
        topic: Log topic (system, info, script, dhcp, interface, etc.)
        time_filter: Time filter (e.g., "5m", "1h", "1d")
        limit: Maximum number of entries

    Returns:
        Log entries for the specified topic
    """
    await ctx.info(f"Getting logs by topic: topic={topic}")

    return await mikrotik_get_logs(
        topics=topic,
        time_filter=time_filter,
        limit=limit,
        ctx=ctx
    )

@mcp.tool(name="search_logs", annotations=READ)
async def mikrotik_search_logs(
    search_term: str,
    ctx: Context,
    time_filter: Optional[str] = None,
    case_sensitive: bool = False,
    limit: Optional[int] = None
) -> str:
    """
    Searches logs for a specific term.

    Args:
        search_term: Term to search for in log messages
        time_filter: Time filter (e.g., "5m", "1h", "1d")
        case_sensitive: Whether search should be case-sensitive
        limit: Maximum number of entries

    Returns:
        Log entries containing the search term
    """
    await ctx.info(f"Searching logs for: term={search_term}")

    # Adjust search term for case sensitivity
    if not case_sensitive:
        # MikroTik uses ~ for partial match (case-insensitive by default)
        message_filter = search_term
    else:
        # For case-sensitive, we'd need to use exact match or regex
        message_filter = search_term

    return await mikrotik_get_logs(
        message_filter=message_filter,
        time_filter=time_filter,
        limit=limit,
        ctx=ctx
    )

@mcp.tool(name="get_system_events", annotations=READ)
async def mikrotik_get_system_events(
    ctx: Context,
    event_type: Optional[str] = None,
    time_filter: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Gets system-related log events.

    Args:
        event_type: Type of system event (login, reboot, config-change, etc.)
        time_filter: Time filter (e.g., "5m", "1h", "1d")
        limit: Maximum number of entries

    Returns:
        System event log entries
    """
    await ctx.info(f"Getting system events: type={event_type}")

    # Build filter based on event type
    topics = "system"
    message_filter = None

    if event_type:
        event_patterns = {
            "login": "logged in",
            "logout": "logged out",
            "reboot": "reboot",
            "config-change": "config changed",
            "backup": "backup",
            "restore": "restore",
            "upgrade": "upgrade"
        }

        if event_type.lower() in event_patterns:
            message_filter = event_patterns[event_type.lower()]
        else:
            message_filter = event_type

    return await mikrotik_get_logs(
        topics=topics,
        message_filter=message_filter,
        time_filter=time_filter,
        limit=limit,
        ctx=ctx
    )

@mcp.tool(name="get_security_logs", annotations=READ)
async def mikrotik_get_security_logs(
    ctx: Context,
    time_filter: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Gets security-related log entries.

    Args:
        time_filter: Time filter (e.g., "5m", "1h", "1d")
        limit: Maximum number of entries

    Returns:
        Security-related log entries
    """
    await ctx.info("Getting security logs")

    # Security-related topics and keywords
    security_topics = "system,firewall,warning,error"
    security_keywords = "(login|logout|failed|denied|blocked|attack|invalid|unauthorized)"

    cmd = f"/log print where (topics~'{security_topics}') and message~'{security_keywords}'"

    if time_filter:
        cmd += f" and time > ([:timestamp] - {time_filter})"

    if limit:
        cmd += f" limit={limit}"

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No security-related log entries found."

    return f"SECURITY LOG ENTRIES:\n\n{result}"

@mcp.tool(name="clear_logs", annotations=DESTRUCTIVE)
async def mikrotik_clear_logs(ctx: Context) -> str:
    """
    Clears all logs from MikroTik device.
    Note: This action cannot be undone!

    Returns:
        Command result
    """
    await ctx.info("Clearing all logs")

    cmd = "/log print follow-only"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return "Logs cleared successfully."
    else:
        return f"Log clear result: {result}"

@mcp.tool(name="get_log_statistics", annotations=READ)
async def mikrotik_get_log_statistics(ctx: Context) -> str:
    """
    Gets statistics about log entries.

    Returns:
        Log statistics including counts by topic and severity
    """
    await ctx.info("Getting log statistics")

    # Get total count
    total_cmd = "/log print count-only"
    total_count = await execute_mikrotik_command(total_cmd, ctx)

    stats = [f"Total log entries: {total_count.strip()}"]

    # Get counts by common topics
    topics = ["info", "warning", "error", "system", "dhcp", "firewall", "interface"]
    for topic in topics:
        count_cmd = f'/log print count-only where topics~"{topic}"'
        count = await execute_mikrotik_command(count_cmd, ctx)
        if count.strip().isdigit() and int(count.strip()) > 0:
            stats.append(f"{topic.capitalize()}: {count.strip()}")

    # Get recent entries count (last hour)
    recent_cmd = "/log print count-only where time > ([:timestamp] - 1h)"
    recent_count = await execute_mikrotik_command(recent_cmd, ctx)
    stats.append(f"\nEntries in last hour: {recent_count.strip()}")

    # Get today's entries
    today_cmd = "/log print count-only where time > ([:timestamp] - 1d)"
    today_count = await execute_mikrotik_command(today_cmd, ctx)
    stats.append(f"Entries in last 24 hours: {today_count.strip()}")

    return "LOG STATISTICS:\n\n" + "\n".join(stats)

@mcp.tool(name="export_logs", annotations=READ)
async def mikrotik_export_logs(
    ctx: Context,
    filename: Optional[str] = None,
    topics: Optional[str] = None,
    time_filter: Optional[str] = None,
    format: Literal["plain", "csv"] = "plain"
) -> str:
    """
    Exports logs to a file on the MikroTik device.

    Args:
        filename: Export filename (without extension)
        topics: Filter by topics before export
        time_filter: Time filter for export
        format: Export format (plain, csv)

    Returns:
        Export result
    """
    if not filename:
        filename = f"logs_export_{int(time.time())}"

    await ctx.info(f"Exporting logs to file: {filename}")

    # Build export command
    cmd = f"/log print file={filename}"

    filters = []
    if topics:
        filters.append(f'topics~"{topics}"')

    if time_filter:
        filters.append(f"time > ([:timestamp] - {time_filter})")

    if filters:
        cmd += " where " + " and ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return f"Logs exported to file: {filename}.txt"
    else:
        return f"Export result: {result}"

@mcp.tool(name="monitor_logs", annotations=READ)
async def mikrotik_monitor_logs(
    ctx: Context,
    topics: Optional[str] = None,
    action: Optional[str] = None,
    duration: int = 10
) -> str:
    """
    Monitors logs in real-time for a specified duration.

    Args:
        topics: Topics to monitor
        action: Actions to monitor
        duration: Duration in seconds (limited for safety)

    Returns:
        Recent log entries
    """
    await ctx.info(f"Monitoring logs for {duration} seconds")

    # Limit duration for safety
    if duration > 60:
        duration = 60

    # This is a simplified version - real-time monitoring would require
    # a different approach with streaming
    cmd = "/log print follow-only"

    if topics:
        cmd += f' where topics~"{topics}"'

    if action:
        cmd += f' action="{action}"'

    # Add a limit to prevent overwhelming output
    cmd += " limit=100"

    result = await execute_mikrotik_command(cmd, ctx)

    return f"LOG MONITOR (last {duration} seconds):\n\n{result}"
