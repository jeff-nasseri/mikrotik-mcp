from typing import List, Optional, Dict, Any

from ..connector import execute_mikrotik_command
from ..logger import app_logger
from ..app import mcp


def mikrotik_detect_wireless_interface_type() -> Optional[str]:
    """
    Detects the wireless interface type based on RouterOS version.

    Returns:
        The appropriate wireless interface command path or None if not supported
    """
    app_logger.info("Detecting wireless interface type")

    # Try different wireless interface types in order of preference
    interface_types = [
        "/interface wifi",  # RouterOS v7.x (newest)
        "/interface wifiwave2",  # RouterOS v7.x (alternative)
        "/interface wireless",  # RouterOS v6.x
        "/interface wlan"  # Older versions
    ]

    for interface_type in interface_types:
        try:
            app_logger.debug(f"Testing interface type: {interface_type}")

            # Use a simpler test command that's less likely to hang
            test_cmd = f"{interface_type} print count-only"
            result = execute_mikrotik_command(test_cmd)

            app_logger.debug(f"Result for {interface_type}: {result}")

            # Check for specific error patterns
            if result and isinstance(result, str):
                result_lower = result.lower()
                if ("bad command name" in result_lower or
                        "failure:" in result_lower or
                        "no such command prefix" in result_lower or
                        "invalid command name" in result_lower):
                    app_logger.debug(f"Interface type {interface_type} not supported")
                    continue
                else:
                    # If we get a numeric result or no error, this type is supported
                    app_logger.info(f"Detected wireless interface type: {interface_type}")
                    return interface_type

        except Exception as e:
            app_logger.debug(f"Interface type {interface_type} failed with exception: {e}")
            continue

    # If none work, return None
    app_logger.warning("No wireless interface type detected")
    return None


@mcp.tool()
def mikrotik_create_wireless_interface(
        name: str,
        ssid: Optional[str] = None,
        disabled: bool = False,
        comment: Optional[str] = None,
        radio_name: Optional[str] = None,
        mode: Optional[str] = None,
        frequency: Optional[str] = None,
        band: Optional[str] = None,
        channel_width: Optional[str] = None,
        security_profile: Optional[str] = None,
) -> str:
    """
    Creates a wireless interface on MikroTik device.

    Args:
        name: Name of the wireless interface
        ssid: Network SSID name
        disabled: Whether to disable the interface
        comment: Optional comment
        radio_name: Radio interface name (required for legacy systems)
        mode: Wireless mode (e.g., ap-bridge) for legacy systems
        frequency: Operating frequency for legacy systems
        band: Frequency band for legacy systems
        channel_width: Channel width for legacy systems
        security_profile: Security profile name for legacy systems

    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating wireless interface: name={name}, ssid={ssid}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    # Build the command based on interface type
    if interface_type == "/interface wifi":
        # RouterOS v7.x newest wifi syntax - simplified
        cmd = f"{interface_type} add name={name}"

        if ssid:
            cmd += f' ssid="{ssid}"'
        if disabled:
            cmd += " disabled=yes"
        if comment:
            cmd += f' comment="{comment}"'

    elif interface_type == "/interface wifiwave2":
        # RouterOS v7.x wifiwave2 syntax
        cmd = f"{interface_type} add name={name}"

        if ssid:
            cmd += f' ssid="{ssid}"'
        if disabled:
            cmd += " disabled=yes"
        if comment:
            cmd += f' comment="{comment}"'

    else:
        # Legacy wireless syntax (RouterOS v6.x and older)
        if not radio_name:
            return "Error: radio_name is required for legacy wireless systems. Please specify the radio interface (e.g., 'wlan1')."

        cmd = f"{interface_type} add name={name} radio-name={radio_name} mode={mode or 'ap-bridge'}"

        if ssid:
            cmd += f' ssid="{ssid}"'
        if disabled:
            cmd += " disabled=yes"
        if comment:
            cmd += f' comment="{comment}"'

        # Add other legacy parameters if provided
        for param_name, param_value in [
            ('frequency', frequency), ('band', band),
            ('channel-width', channel_width), ('security-profile', security_profile),
        ]:
            if param_value:
                cmd += f" {param_name}={param_value}"

    app_logger.info(f"Executing command: {cmd}")
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create wireless interface: {result}"

    # Get the created interface details
    details_cmd = f'{interface_type} print detail where name="{name}"'
    details = execute_mikrotik_command(details_cmd)

    return f"Wireless interface created successfully using {interface_type}:\n\n{details}"


@mcp.tool()
def mikrotik_list_wireless_interfaces(
        name_filter: Optional[str] = None,
        disabled_only: bool = False,
        running_only: bool = False
) -> str:
    """
    Lists wireless interfaces on MikroTik device.

    Args:
        name_filter: Filter by interface name
        disabled_only: Show only disabled interfaces
        running_only: Show only running interfaces

    Returns:
        List of wireless interfaces
    """
    app_logger.info(f"Listing wireless interfaces with filters: name={name_filter}")

    # Try multiple interface types to ensure we find all wireless interfaces
    interface_types_to_try = [
        "/interface wifi",
        "/interface wifiwave2",
        "/interface wireless",
        "/interface wlan"
    ]

    all_results = []
    working_types = []

    for interface_type in interface_types_to_try:
        try:
            # Build the command
            cmd = f"{interface_type} print"

            # Add filters
            filters = []
            if name_filter:
                filters.append(f'name~"{name_filter}"')
            if disabled_only:
                filters.append("disabled=yes")
            if running_only:
                filters.append("running=yes")

            if filters:
                cmd += " where " + " and ".join(filters)

            result = execute_mikrotik_command(cmd)

            # Check if command worked and has results
            if (result and
                    result.strip() != "" and
                    "bad command name" not in result.lower() and
                    "failure:" not in result.lower() and
                    "no such command prefix" not in result.lower()):
                working_types.append(interface_type)
                all_results.append(f"=== {interface_type.upper()} ===\n{result}")

        except Exception as e:
            app_logger.debug(f"Interface type {interface_type} failed: {e}")
            continue

    # If we found results, return them
    if all_results:
        return f"WIRELESS INTERFACES:\n\n" + "\n\n".join(all_results)

    # If no results found, try to show all interfaces to help debug
    try:
        all_interfaces_cmd = "/interface print"
        all_interfaces = execute_mikrotik_command(all_interfaces_cmd)
        return f"""No wireless interfaces found matching the criteria.

DEBUGGING INFO:
Working interface types: {', '.join(working_types) if working_types else 'None detected'}

ALL INTERFACES ON DEVICE:
{all_interfaces}

NOTE: If you see wireless interfaces above, they might be using a different command structure."""

    except Exception:
        return "No wireless interfaces found matching the criteria."


@mcp.tool()
def mikrotik_get_wireless_interface(name: str) -> str:
    """
    Gets detailed information about a specific wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Detailed information about the wireless interface
    """
    app_logger.info(f"Getting wireless interface details: name={name}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    cmd = f'{interface_type} print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return f"Wireless interface '{name}' not found."

    return f"WIRELESS INTERFACE DETAILS:\n\n{result}"


@mcp.tool()
def mikrotik_remove_wireless_interface(name: str) -> str:
    """
    Removes a wireless interface from MikroTik device.

    Args:
        name: Name of the wireless interface to remove

    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing wireless interface: name={name}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    # Check if interface exists
    check_cmd = f'{interface_type} print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless interface '{name}' not found."

    # Remove the interface
    cmd = f'{interface_type} remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove wireless interface: {result}"

    return f"Wireless interface '{name}' removed successfully."


@mcp.tool()
def mikrotik_enable_wireless_interface(name: str) -> str:
    """
    Enables a wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Command output or error message
    """
    app_logger.info(f"Enabling wireless interface: {name}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    cmd = f'{interface_type} enable [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable wireless interface: {result}"

    return f"Wireless interface '{name}' enabled successfully."


@mcp.tool()
def mikrotik_disable_wireless_interface(name: str) -> str:
    """
    Disables a wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Command output or error message
    """
    app_logger.info(f"Disabling wireless interface: {name}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    cmd = f'{interface_type} disable [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable wireless interface: {result}"

    return f"Wireless interface '{name}' disabled successfully."


@mcp.tool()
def mikrotik_scan_wireless_networks(
        interface: str,
        duration: int = 5
) -> str:
    """
    Scans for wireless networks using specified interface.

    Args:
        interface: Wireless interface to use for scanning
        duration: Scan duration in seconds

    Returns:
        List of discovered wireless networks
    """
    app_logger.info(f"Scanning wireless networks on interface: {interface}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    # Different scan commands for different versions
    scan_cmd = f'{interface_type} scan {interface} duration={duration}'

    result = execute_mikrotik_command(scan_cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to scan wireless networks: {result}"

    return f"WIRELESS NETWORK SCAN RESULTS:\n\n{result}"


@mcp.tool()
def mikrotik_get_wireless_registration_table(
        interface: Optional[str] = None
) -> str:
    """
    Gets the wireless registration table (connected clients).

    Args:
        interface: Filter by specific wireless interface

    Returns:
        List of registered wireless clients
    """
    app_logger.info(f"Getting wireless registration table for interface: {interface}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    # Build command
    cmd = f"{interface_type} registration-table print"

    if interface:
        cmd += f' where interface="{interface}"'

    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return "No wireless clients registered."

    return f"WIRELESS REGISTRATION TABLE:\n\n{result}"


@mcp.tool()
def mikrotik_check_wireless_support() -> str:
    """
    Checks if the device supports wireless functionality and returns detailed information.

    Returns:
        Information about wireless support and available packages
    """
    app_logger.info("Checking wireless support")

    # Check RouterOS version
    version_cmd = "/system resource print"
    version_result = execute_mikrotik_command(version_cmd)

    # Check installed packages
    package_cmd = "/system package print"
    package_result = execute_mikrotik_command(package_cmd)

    # Check available interfaces
    interface_cmd = "/interface print"
    interface_result = execute_mikrotik_command(interface_cmd)

    # Detect wireless interface type
    wireless_type = mikrotik_detect_wireless_interface_type()

    report = f"""WIRELESS SUPPORT CHECK:

RouterOS Version:
{version_result}

Installed Packages:
{package_result}

Available Interfaces:
{interface_result}

Detected Wireless Interface Type: {wireless_type if wireless_type else 'None detected'}

Compatibility Notes:
- RouterOS v7.x uses '/interface wifi' (newest system)
- RouterOS v7.x also supports '/interface wifiwave2' (alternative)
- RouterOS v6.x uses '/interface wireless' (legacy system)  
- Older versions may use '/interface wlan'

USAGE EXAMPLES:
For RouterOS v7.x:
  mikrotik_create_wireless_interface(name="wlan1", ssid="MyNetwork")

For legacy systems:
  mikrotik_create_wireless_interface(name="wlan1", radio_name="wlan1", ssid="MyNetwork")
"""

    return report


# Legacy compatibility functions (simplified versions for older RouterOS)
@mcp.tool()
def mikrotik_create_wireless_security_profile(name: str) -> str:
    """Legacy function - not supported in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Security profiles are not used in RouterOS v7.x. Configure security directly on the wireless interface."
    return "Legacy security profile creation not implemented in this version."


@mcp.tool()
def mikrotik_list_wireless_security_profiles() -> str:
    """Legacy function - not supported in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Security profiles are not used in RouterOS v7.x. Security is configured directly on wireless interfaces."
    return "Legacy security profile listing not implemented in this version."


@mcp.tool()
def mikrotik_get_wireless_security_profile(name: str) -> str:
    """Legacy function - not supported in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Security profiles are not used in RouterOS v7.x. Check security configuration on wireless interfaces directly."
    return "Legacy security profile details not implemented in this version."


@mcp.tool()
def mikrotik_remove_wireless_security_profile(name: str) -> str:
    """Legacy function - not supported in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Security profiles are not used in RouterOS v7.x. Security is configured directly on wireless interfaces."
    return "Legacy security profile removal not implemented in this version."


@mcp.tool()
def mikrotik_set_wireless_security_profile(interface_name: str, security_profile: str) -> str:
    """Legacy function - not supported in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Security profiles are not used in RouterOS v7.x. Configure security directly on the wireless interface."
    return "Legacy security profile setting not implemented in this version."


@mcp.tool()
def mikrotik_create_wireless_access_list() -> str:
    """Legacy function - different in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Access lists are configured differently in RouterOS v7.x. Use firewall rules or other access control methods."
    return "Legacy access list creation not implemented in this version."


@mcp.tool()
def mikrotik_list_wireless_access_list() -> str:
    """Legacy function - different in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Access lists are configured differently in RouterOS v7.x. Check firewall rules or other access control configurations."
    return "Legacy access list listing not implemented in this version."


@mcp.tool()
def mikrotik_remove_wireless_access_list_entry(entry_id: str) -> str:
    """Legacy function - different in RouterOS v7.x"""
    interface_type = mikrotik_detect_wireless_interface_type()
    if interface_type in ["/interface wifi", "/interface wifiwave2"]:
        return "Access lists are configured differently in RouterOS v7.x."
    return "Legacy access list removal not implemented in this version."


@mcp.tool()
def mikrotik_update_wireless_interface(
        name: str,
        new_name: Optional[str] = None,
        ssid: Optional[str] = None,
        disabled: Optional[bool] = None,
        comment: Optional[str] = None,
) -> str:
    """
    Updates an existing wireless interface.

    Args:
        name: Name of the wireless interface to update
        new_name: New name for the interface
        ssid: New SSID
        disabled: Whether to disable the interface
        comment: Optional comment

    Returns:
        Command output or error message
    """
    app_logger.info(f"Updating wireless interface: name={name}")

    # Detect wireless interface type
    interface_type = mikrotik_detect_wireless_interface_type()

    if not interface_type:
        return "Error: No wireless interface support detected on this device."

    # Check if interface exists
    check_cmd = f'{interface_type} print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless interface '{name}' not found."

    # Build update command
    updates = []

    if new_name:
        updates.append(f"name={new_name}")
    if ssid:
        updates.append(f'ssid="{ssid}"')
    if disabled is not None:
        updates.append(f"disabled={'yes' if disabled else 'no'}")
    if comment:
        updates.append(f'comment="{comment}"')

    if not updates:
        return "No updates specified."

    cmd = f'{interface_type} set [find name="{name}"] {" ".join(updates)}'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update wireless interface: {result}"

    # Get updated details
    target_name = new_name or name
    details_cmd = f'{interface_type} print detail where name="{target_name}"'
    details = execute_mikrotik_command(details_cmd)

    return f"Wireless interface updated successfully:\n\n{details}"