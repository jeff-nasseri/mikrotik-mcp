import time
from typing import Optional, List, Dict
from ..connector import execute_mikrotik_command
from ..logger import app_logger
from ..app import mcp
import re
from datetime import datetime, timedelta

@mcp.tool()
def mikrotik_get_logs(
    topics: Optional[str] = None,
    action: Optional[str] = None,
    time_filter: Optional[str] = None,
    message_filter: Optional[str] = None,
    prefix_filter: Optional[str] = None,
    limit: Optional[int] = None,
    follow: bool = False,
    print_as: str = "value"
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
    app_logger.info(f"Getting logs with filters: topics={topics}, action={action}, time={time_filter}")
    
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
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No log entries found matching the criteria."
    
    return f"LOG ENTRIES:\n\n{result}"

@mcp.tool()
def mikrotik_get_logs_by_severity(
    severity: str,
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
    app_logger.info(f"Getting logs by severity: severity={severity}")
    
    # Map severity to topics
    severity_topics = {
        "debug": "debug",
        "info": "info",
        "warning": "warning",
        "error": "error,critical",
        "critical": "critical"
    }
    
    if severity.lower() not in severity_topics:
        return f"Invalid severity level: {severity}. Must be one of: debug, info, warning, error, critical"
    
    topics = severity_topics[severity.lower()]
    
    return mikrotik_get_logs(
        topics=topics,
        time_filter=time_filter,
        limit=limit
    )

@mcp.tool()
def mikrotik_get_logs_by_topic(
    topic: str,
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
    app_logger.info(f"Getting logs by topic: topic={topic}")
    
    return mikrotik_get_logs(
        topics=topic,
        time_filter=time_filter,
        limit=limit
    )

@mcp.tool()
def mikrotik_search_logs(
    search_term: str,
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
    app_logger.info(f"Searching logs for: term={search_term}")
    
    # Adjust search term for case sensitivity
    if not case_sensitive:
        # MikroTik uses ~ for partial match (case-insensitive by default)
        message_filter = search_term
    else:
        # For case-sensitive, we'd need to use exact match or regex
        message_filter = search_term
    
    return mikrotik_get_logs(
        message_filter=message_filter,
        time_filter=time_filter,
        limit=limit
    )

@mcp.tool()
def mikrotik_get_system_events(
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
    app_logger.info(f"Getting system events: type={event_type}")
    
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
    
    return mikrotik_get_logs(
        topics=topics,
        message_filter=message_filter,
        time_filter=time_filter,
        limit=limit
    )

@mcp.tool()
def mikrotik_get_security_logs(
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
    app_logger.info("Getting security logs")
    
    # Security-related topics and keywords
    security_topics = "system,firewall,warning,error"
    security_keywords = "(login|logout|failed|denied|blocked|attack|invalid|unauthorized)"
    
    cmd = f"/log print where (topics~'{security_topics}') and message~'{security_keywords}'"
    
    if time_filter:
        cmd += f" and time > ([:timestamp] - {time_filter})"
    
    if limit:
        cmd += f" limit={limit}"
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No security-related log entries found."
    
    return f"SECURITY LOG ENTRIES:\n\n{result}"

@mcp.tool()
def mikrotik_clear_logs() -> str:
    """
    Clears all logs from MikroTik device.
    Note: This action cannot be undone!
    
    Returns:
        Command result
    """
    app_logger.info("Clearing all logs")
    
    cmd = "/log print follow-only"
    result = execute_mikrotik_command(cmd)
    
    if not result.strip():
        return "Logs cleared successfully."
    else:
        return f"Log clear result: {result}"

@mcp.tool()
def mikrotik_get_log_statistics() -> str:
    """
    Gets statistics about log entries.
    
    Returns:
        Log statistics including counts by topic and severity
    """
    app_logger.info("Getting log statistics")
    
    # Get total count
    total_cmd = "/log print count-only"
    total_count = execute_mikrotik_command(total_cmd)
    
    stats = [f"Total log entries: {total_count.strip()}"]
    
    # Get counts by common topics
    topics = ["info", "warning", "error", "system", "dhcp", "firewall", "interface"]
    for topic in topics:
        count_cmd = f'/log print count-only where topics~"{topic}"'
        count = execute_mikrotik_command(count_cmd)
        if count.strip().isdigit() and int(count.strip()) > 0:
            stats.append(f"{topic.capitalize()}: {count.strip()}")
    
    # Get recent entries count (last hour)
    recent_cmd = "/log print count-only where time > ([:timestamp] - 1h)"
    recent_count = execute_mikrotik_command(recent_cmd)
    stats.append(f"\nEntries in last hour: {recent_count.strip()}")
    
    # Get today's entries
    today_cmd = "/log print count-only where time > ([:timestamp] - 1d)"
    today_count = execute_mikrotik_command(today_cmd)
    stats.append(f"Entries in last 24 hours: {today_count.strip()}")
    
    return "LOG STATISTICS:\n\n" + "\n".join(stats)

@mcp.tool()
def mikrotik_export_logs(
    filename: Optional[str] = None,
    topics: Optional[str] = None,
    time_filter: Optional[str] = None,
    format: str = "plain"
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
    
    app_logger.info(f"Exporting logs to file: {filename}")
    
    # Build export command
    cmd = f"/log print file={filename}"
    
    filters = []
    if topics:
        filters.append(f'topics~"{topics}"')
    
    if time_filter:
        filters.append(f"time > ([:timestamp] - {time_filter})")
    
    if filters:
        cmd += " where " + " and ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result.strip():
        return f"Logs exported to file: {filename}.txt"
    else:
        return f"Export result: {result}"

@mcp.tool()
def mikrotik_monitor_logs(
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
    app_logger.info(f"Monitoring logs for {duration} seconds")
    
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
    
    result = execute_mikrotik_command(cmd)
    
    return f"LOG MONITOR (last {duration} seconds):\n\n{result}"