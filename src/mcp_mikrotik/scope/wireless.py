from typing import List, Optional, Dict, Any

from ..connector import execute_mikrotik_command
from ..logger import app_logger


def mikrotik_create_wireless_interface(
        name: str,
        radio_name: str,
        mode: str = "ap-bridge",
        ssid: Optional[str] = None,
        frequency: Optional[str] = None,
        band: Optional[str] = None,
        channel_width: Optional[str] = None,
        disabled: bool = False,
        comment: Optional[str] = None
) -> str:
    """
    Creates a wireless interface on MikroTik device.

    Args:
        name: Name of the wireless interface
        radio_name: Name of the radio interface (e.g., "wlan1")
        mode: Wireless mode (ap-bridge, station, bridge, etc.)
        ssid: Network SSID name
        frequency: Operating frequency
        band: Frequency band (2ghz-b/g/n, 5ghz-a/n/ac, etc.)
        channel_width: Channel width (20mhz, 40mhz, 80mhz, etc.)
        disabled: Whether to disable the interface
        comment: Optional comment

    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating wireless interface: name={name}, radio={radio_name}, mode={mode}")

    # Build the command
    cmd = f"/interface wireless add name={name} radio-name={radio_name} mode={mode}"

    # Add optional parameters
    if ssid:
        cmd += f' ssid="{ssid}"'

    if frequency:
        cmd += f" frequency={frequency}"

    if band:
        cmd += f" band={band}"

    if channel_width:
        cmd += f" channel-width={channel_width}"

    if disabled:
        cmd += " disabled=yes"

    if comment:
        cmd += f' comment="{comment}"'

    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create wireless interface: {result}"

    # Get the created interface details
    details_cmd = f'/interface wireless print detail where name="{name}"'
    details = execute_mikrotik_command(details_cmd)

    return f"Wireless interface created successfully:\n\n{details}"


def mikrotik_list_wireless_interfaces(
        name_filter: Optional[str] = None,
        mode_filter: Optional[str] = None,
        disabled_only: bool = False,
        running_only: bool = False
) -> str:
    """
    Lists wireless interfaces on MikroTik device.

    Args:
        name_filter: Filter by interface name
        mode_filter: Filter by wireless mode
        disabled_only: Show only disabled interfaces
        running_only: Show only running interfaces

    Returns:
        List of wireless interfaces
    """
    app_logger.info(f"Listing wireless interfaces with filters: name={name_filter}, mode={mode_filter}")

    # Build the command
    cmd = "/interface wireless print"

    # Add filters
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if mode_filter:
        filters.append(f'mode="{mode_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if running_only:
        filters.append("running=yes")

    if filters:
        cmd += " where " + " and ".join(filters)

    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return "No wireless interfaces found matching the criteria."

    return f"WIRELESS INTERFACES:\n\n{result}"


def mikrotik_get_wireless_interface(name: str) -> str:
    """
    Gets detailed information about a specific wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Detailed information about the wireless interface
    """
    app_logger.info(f"Getting wireless interface details: name={name}")

    cmd = f'/interface wireless print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return f"Wireless interface '{name}' not found."

    return f"WIRELESS INTERFACE DETAILS:\n\n{result}"


def mikrotik_update_wireless_interface(
        name: str,
        new_name: Optional[str] = None,
        ssid: Optional[str] = None,
        frequency: Optional[str] = None,
        band: Optional[str] = None,
        channel_width: Optional[str] = None,
        mode: Optional[str] = None,
        disabled: Optional[bool] = None,
        comment: Optional[str] = None
) -> str:
    """
    Updates an existing wireless interface.

    Args:
        name: Current name of the wireless interface
        new_name: New name for the interface
        ssid: New SSID name
        frequency: New operating frequency
        band: New frequency band
        channel_width: New channel width
        mode: New wireless mode
        disabled: Enable/disable interface
        comment: New comment

    Returns:
        Command output or error message
    """
    app_logger.info(f"Updating wireless interface: name={name}")

    # Check if interface exists
    check_cmd = f'/interface wireless print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless interface '{name}' not found."

    # Build update command
    updates = []

    if new_name:
        updates.append(f"name={new_name}")
    if ssid:
        updates.append(f'ssid="{ssid}"')
    if frequency:
        updates.append(f"frequency={frequency}")
    if band:
        updates.append(f"band={band}")
    if channel_width:
        updates.append(f"channel-width={channel_width}")
    if mode:
        updates.append(f"mode={mode}")
    if disabled is not None:
        updates.append(f"disabled={'yes' if disabled else 'no'}")
    if comment:
        updates.append(f'comment="{comment}"')

    if not updates:
        return "No updates specified."

    cmd = f'/interface wireless set [find name="{name}"] {" ".join(updates)}'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update wireless interface: {result}"

    # Get updated details
    target_name = new_name if new_name else name
    details_cmd = f'/interface wireless print detail where name="{target_name}"'
    details = execute_mikrotik_command(details_cmd)

    return f"Wireless interface updated successfully:\n\n{details}"


def mikrotik_remove_wireless_interface(name: str) -> str:
    """
    Removes a wireless interface from MikroTik device.

    Args:
        name: Name of the wireless interface to remove

    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing wireless interface: name={name}")

    # Check if interface exists
    check_cmd = f'/interface wireless print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless interface '{name}' not found."

    # Remove the interface
    cmd = f'/interface wireless remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove wireless interface: {result}"

    return f"Wireless interface '{name}' removed successfully."


def mikrotik_create_wireless_security_profile(
        name: str,
        mode: str = "dynamic-keys",
        authentication_types: Optional[List[str]] = None,
        unicast_ciphers: Optional[List[str]] = None,
        group_ciphers: Optional[List[str]] = None,
        wpa_pre_shared_key: Optional[str] = None,
        wpa2_pre_shared_key: Optional[str] = None,
        supplicant_identity: Optional[str] = None,
        eap_methods: Optional[str] = None,
        tls_mode: Optional[str] = None,
        tls_certificate: Optional[str] = None,
        comment: Optional[str] = None
) -> str:
    """
    Creates a wireless security profile on MikroTik device.

    Args:
        name: Name of the security profile
        mode: Security mode (none, static-keys-required, dynamic-keys, etc.)
        authentication_types: List of authentication types (wpa-psk, wpa2-psk, wpa-eap, wpa2-eap)
        unicast_ciphers: List of unicast ciphers (tkip, aes-ccm)
        group_ciphers: List of group ciphers (tkip, aes-ccm)
        wpa_pre_shared_key: WPA pre-shared key
        wpa2_pre_shared_key: WPA2 pre-shared key
        supplicant_identity: Supplicant identity for EAP
        eap_methods: EAP methods
        tls_mode: TLS mode
        tls_certificate: TLS certificate
        comment: Optional comment

    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating wireless security profile: name={name}, mode={mode}")

    # Build the command
    cmd = f'/interface wireless security-profiles add name={name} mode={mode}'

    # Add optional parameters
    if authentication_types:
        cmd += f" authentication-types={','.join(authentication_types)}"

    if unicast_ciphers:
        cmd += f" unicast-ciphers={','.join(unicast_ciphers)}"

    if group_ciphers:
        cmd += f" group-ciphers={','.join(group_ciphers)}"

    if wpa_pre_shared_key:
        cmd += f' wpa-pre-shared-key="{wpa_pre_shared_key}"'

    if wpa2_pre_shared_key:
        cmd += f' wpa2-pre-shared-key="{wpa2_pre_shared_key}"'

    if supplicant_identity:
        cmd += f' supplicant-identity="{supplicant_identity}"'

    if eap_methods:
        cmd += f" eap-methods={eap_methods}"

    if tls_mode:
        cmd += f" tls-mode={tls_mode}"

    if tls_certificate:
        cmd += f" tls-certificate={tls_certificate}"

    if comment:
        cmd += f' comment="{comment}"'

    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create wireless security profile: {result}"

    # Get the created profile details
    details_cmd = f'/interface wireless security-profiles print detail where name="{name}"'
    details = execute_mikrotik_command(details_cmd)

    return f"Wireless security profile created successfully:\n\n{details}"


def mikrotik_list_wireless_security_profiles(
        name_filter: Optional[str] = None,
        mode_filter: Optional[str] = None
) -> str:
    """
    Lists wireless security profiles on MikroTik device.

    Args:
        name_filter: Filter by profile name
        mode_filter: Filter by security mode

    Returns:
        List of wireless security profiles
    """
    app_logger.info(f"Listing wireless security profiles with filters: name={name_filter}, mode={mode_filter}")

    # Build the command
    cmd = "/interface wireless security-profiles print"

    # Add filters
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if mode_filter:
        filters.append(f'mode="{mode_filter}"')

    if filters:
        cmd += " where " + " and ".join(filters)

    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return "No wireless security profiles found matching the criteria."

    return f"WIRELESS SECURITY PROFILES:\n\n{result}"


def mikrotik_get_wireless_security_profile(name: str) -> str:
    """
    Gets detailed information about a specific wireless security profile.

    Args:
        name: Name of the security profile

    Returns:
        Detailed information about the security profile
    """
    app_logger.info(f"Getting wireless security profile details: name={name}")

    cmd = f'/interface wireless security-profiles print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return f"Wireless security profile '{name}' not found."

    return f"WIRELESS SECURITY PROFILE DETAILS:\n\n{result}"


def mikrotik_remove_wireless_security_profile(name: str) -> str:
    """
    Removes a wireless security profile from MikroTik device.

    Args:
        name: Name of the security profile to remove

    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing wireless security profile: name={name}")

    # Check if profile exists
    check_cmd = f'/interface wireless security-profiles print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless security profile '{name}' not found."

    # Remove the profile
    cmd = f'/interface wireless security-profiles remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove wireless security profile: {result}"

    return f"Wireless security profile '{name}' removed successfully."


def mikrotik_set_wireless_security_profile(
        interface_name: str,
        security_profile: str
) -> str:
    """
    Sets the security profile for a wireless interface.

    Args:
        interface_name: Name of the wireless interface
        security_profile: Name of the security profile to apply

    Returns:
        Command output or error message
    """
    app_logger.info(f"Setting security profile for interface: {interface_name} -> {security_profile}")

    # Check if interface exists
    check_cmd = f'/interface wireless print count-only where name="{interface_name}"'
    count = execute_mikrotik_command(check_cmd)

    if count.strip() == "0":
        return f"Wireless interface '{interface_name}' not found."

    # Set the security profile
    cmd = f'/interface wireless set [find name="{interface_name}"] security-profile={security_profile}'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to set security profile: {result}"

    return f"Security profile '{security_profile}' applied to interface '{interface_name}' successfully."


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

    # Start scan
    scan_cmd = f'/interface wireless scan {interface} duration={duration}'
    result = execute_mikrotik_command(scan_cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to scan wireless networks: {result}"

    return f"WIRELESS NETWORK SCAN RESULTS:\n\n{result}"


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

    # Build command
    cmd = "/interface wireless registration-table print"

    if interface:
        cmd += f' where interface="{interface}"'

    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return "No wireless clients registered."

    return f"WIRELESS REGISTRATION TABLE:\n\n{result}"


def mikrotik_create_wireless_access_list(
        interface: str,
        mac_address: str,
        action: str = "accept",
        signal_range: Optional[str] = None,
        time: Optional[str] = None,
        comment: Optional[str] = None
) -> str:
    """
    Creates a wireless access list entry.

    Args:
        interface: Wireless interface
        mac_address: MAC address to control
        action: Action (accept, reject, query)
        signal_range: Signal strength range
        time: Time schedule
        comment: Optional comment

    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating wireless access list entry: {mac_address} -> {action}")

    # Build command
    cmd = f'/interface wireless access-list add interface={interface} mac-address={mac_address} action={action}'

    # Add optional parameters
    if signal_range:
        cmd += f" signal-range={signal_range}"

    if time:
        cmd += f" time={time}"

    if comment:
        cmd += f' comment="{comment}"'

    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create wireless access list entry: {result}"

    return f"Wireless access list entry created successfully."


def mikrotik_list_wireless_access_list(
        interface_filter: Optional[str] = None,
        action_filter: Optional[str] = None
) -> str:
    """
    Lists wireless access list entries.

    Args:
        interface_filter: Filter by interface
        action_filter: Filter by action

    Returns:
        List of wireless access list entries
    """
    app_logger.info(f"Listing wireless access list entries")

    # Build command
    cmd = "/interface wireless access-list print"

    # Add filters
    filters = []
    if interface_filter:
        filters.append(f'interface="{interface_filter}"')
    if action_filter:
        filters.append(f'action="{action_filter}"')

    if filters:
        cmd += " where " + " and ".join(filters)

    result = execute_mikrotik_command(cmd)

    if not result or result.strip() == "":
        return "No wireless access list entries found."

    return f"WIRELESS ACCESS LIST:\n\n{result}"


def mikrotik_remove_wireless_access_list_entry(
        entry_id: str
) -> str:
    """
    Removes a wireless access list entry.

    Args:
        entry_id: ID of the access list entry to remove

    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing wireless access list entry: {entry_id}")

    cmd = f'/interface wireless access-list remove {entry_id}'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove wireless access list entry: {result}"

    return f"Wireless access list entry '{entry_id}' removed successfully."


def mikrotik_enable_wireless_interface(name: str) -> str:
    """
    Enables a wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Command output or error message
    """
    app_logger.info(f"Enabling wireless interface: {name}")

    cmd = f'/interface wireless enable [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to enable wireless interface: {result}"

    return f"Wireless interface '{name}' enabled successfully."


def mikrotik_disable_wireless_interface(name: str) -> str:
    """
    Disables a wireless interface.

    Args:
        name: Name of the wireless interface

    Returns:
        Command output or error message
    """
    app_logger.info(f"Disabling wireless interface: {name}")

    cmd = f'/interface wireless disable [find name="{name}"]'
    result = execute_mikrotik_command(cmd)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to disable wireless interface: {result}"

    return f"Wireless interface '{name}' disabled successfully."