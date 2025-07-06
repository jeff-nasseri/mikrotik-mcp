[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/jeff-nasseri-mikrotik-mcp-badge.png)](https://mseep.ai/app/jeff-nasseri-mikrotik-mcp)

## Overview

MikroTik MCP provides a bridge between AI assistants and MikroTik RouterOS devices. It allows AI assistants to interact with MikroTik routers through natural language requests, executing commands like managing VLANs, configuring firewall rules, handling DNS settings, and more.

## Claude Desktop

https://github.com/user-attachments/assets/24fadcdc-c6a8-48ed-90ac-74baf8f94b59


## Inspector


https://github.com/user-attachments/assets/e0301ff2-8144-4503-83d0-48589d95027d


## Installation

### Prerequisites
- Python 3.8+
- MikroTik RouterOS device with API access enabled
- Python dependencies (routeros-api or similar)

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/jeff-nasseri/mikrotik-mcp/tree/master
cd mcp-mikrotik

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the server
mcp-server-mikrotik
```

## Tools

Here are the available tools in the MikroTik MCP server:

### VLAN Interface Management

#### `mikrotik_create_vlan_interface`
Creates a VLAN interface on MikroTik device.
- Parameters:
  - `name` (required): VLAN interface name
  - `vlan_id` (required): VLAN ID (1-4094)
  - `interface` (required): Parent interface
  - `comment` (optional): Description
  - `disabled` (optional): Disable interface
  - `mtu` (optional): MTU size
  - `use_service_tag` (optional): Use service tag
  - `arp` (optional): ARP mode
  - `arp_timeout` (optional): ARP timeout
- Example:
  ```
  mikrotik_create_vlan_interface(name="vlan100", vlan_id=100, interface="ether1")
  ```

#### `mikrotik_list_vlan_interfaces`
Lists VLAN interfaces on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `vlan_id_filter` (optional): Filter by VLAN ID
  - `interface_filter` (optional): Filter by parent interface
  - `disabled_only` (optional): Show only disabled interfaces
- Example:
  ```
  mikrotik_list_vlan_interfaces(vlan_id_filter=100)
  ```

#### `mikrotik_get_vlan_interface`
Gets detailed information about a specific VLAN interface.
- Parameters:
  - `name` (required): VLAN interface name
- Example:
  ```
  mikrotik_get_vlan_interface(name="vlan100")
  ```

#### `mikrotik_update_vlan_interface`
Updates an existing VLAN interface.
- Parameters:
  - `name` (required): Current VLAN interface name
  - `new_name` (optional): New name
  - `vlan_id` (optional): New VLAN ID
  - `interface` (optional): New parent interface
  - `comment` (optional): New description
  - `disabled` (optional): Enable/disable interface
  - `mtu` (optional): New MTU size
  - `use_service_tag` (optional): Use service tag
  - `arp` (optional): ARP mode
  - `arp_timeout` (optional): ARP timeout
- Example:
  ```
  mikrotik_update_vlan_interface(name="vlan100", comment="Production VLAN")
  ```

#### `mikrotik_remove_vlan_interface`
Removes a VLAN interface from MikroTik device.
- Parameters:
  - `name` (required): VLAN interface name
- Example:
  ```
  mikrotik_remove_vlan_interface(name="vlan100")
  ```

### IP Address Management

#### `mikrotik_add_ip_address`
Adds an IP address to an interface.
- Parameters:
  - `address` (required): IP address with CIDR notation
  - `interface` (required): Interface name
  - `network` (optional): Network address
  - `broadcast` (optional): Broadcast address
  - `comment` (optional): Description
  - `disabled` (optional): Disable address
- Example:
  ```
  mikrotik_add_ip_address(address="192.168.1.1/24", interface="vlan100")
  ```

#### `mikrotik_list_ip_addresses`
Lists IP addresses on MikroTik device.
- Parameters:
  - `interface_filter` (optional): Filter by interface
  - `address_filter` (optional): Filter by address
  - `network_filter` (optional): Filter by network
  - `disabled_only` (optional): Show only disabled addresses
  - `dynamic_only` (optional): Show only dynamic addresses
- Example:
  ```
  mikrotik_list_ip_addresses(interface_filter="vlan100")
  ```

#### `mikrotik_get_ip_address`
Gets detailed information about a specific IP address.
- Parameters:
  - `address_id` (required): Address ID
- Example:
  ```
  mikrotik_get_ip_address(address_id="*1")
  ```

#### `mikrotik_remove_ip_address`
Removes an IP address from MikroTik device.
- Parameters:
  - `address_id` (required): Address ID
- Example:
  ```
  mikrotik_remove_ip_address(address_id="*1")
  ```

### DHCP Server Management

#### `mikrotik_create_dhcp_server`
Creates a DHCP server on MikroTik device.
- Parameters:
  - `name` (required): DHCP server name
  - `interface` (required): Interface to bind to
  - `lease_time` (optional): Lease time (default: "1d")
  - `address_pool` (optional): IP pool name
  - `disabled` (optional): Disable server
  - `authoritative` (optional): Authoritative mode
  - `delay_threshold` (optional): Delay threshold
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_dhcp_server(name="dhcp-vlan100", interface="vlan100", address_pool="pool-vlan100")
  ```

#### `mikrotik_list_dhcp_servers`
Lists DHCP servers on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `interface_filter` (optional): Filter by interface
  - `disabled_only` (optional): Show only disabled servers
  - `invalid_only` (optional): Show only invalid servers
- Example:
  ```
  mikrotik_list_dhcp_servers()
  ```

#### `mikrotik_get_dhcp_server`
Gets detailed information about a specific DHCP server.
- Parameters:
  - `name` (required): DHCP server name
- Example:
  ```
  mikrotik_get_dhcp_server(name="dhcp-vlan100")
  ```

#### `mikrotik_create_dhcp_network`
Creates a DHCP network configuration.
- Parameters:
  - `network` (required): Network address
  - `gateway` (required): Gateway address
  - `netmask` (optional): Network mask
  - `dns_servers` (optional): DNS server list
  - `domain` (optional): Domain name
  - `wins_servers` (optional): WINS server list
  - `ntp_servers` (optional): NTP server list
  - `dhcp_option` (optional): DHCP options
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_dhcp_network(network="192.168.1.0/24", gateway="192.168.1.1", dns_servers=["8.8.8.8", "8.8.4.4"])
  ```

#### `mikrotik_create_dhcp_pool`
Creates a DHCP address pool.
- Parameters:
  - `name` (required): Pool name
  - `ranges` (required): IP ranges
  - `next_pool` (optional): Next pool name
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_dhcp_pool(name="pool-vlan100", ranges="192.168.1.10-192.168.1.250")
  ```

#### `mikrotik_remove_dhcp_server`
Removes a DHCP server from MikroTik device.
- Parameters:
  - `name` (required): DHCP server name
- Example:
  ```
  mikrotik_remove_dhcp_server(name="dhcp-vlan100")
  ```

### NAT Rules Management

#### `mikrotik_create_nat_rule`
Creates a NAT rule on MikroTik device.
- Parameters:
  - `chain` (required): Chain type ("srcnat" or "dstnat")
  - `action` (required): Action type
  - `src_address` (optional): Source address
  - `dst_address` (optional): Destination address
  - `src_port` (optional): Source port
  - `dst_port` (optional): Destination port
  - `protocol` (optional): Protocol
  - `in_interface` (optional): Input interface
  - `out_interface` (optional): Output interface
  - `to_addresses` (optional): Translation addresses
  - `to_ports` (optional): Translation ports
  - `comment` (optional): Description
  - `disabled` (optional): Disable rule
  - `log` (optional): Enable logging
  - `log_prefix` (optional): Log prefix
  - `place_before` (optional): Rule placement
- Example:
  ```
  mikrotik_create_nat_rule(chain="srcnat", action="masquerade", out_interface="ether1")
  ```

#### `mikrotik_list_nat_rules`
Lists NAT rules on MikroTik device.
- Parameters:
  - `chain_filter` (optional): Filter by chain
  - `action_filter` (optional): Filter by action
  - `src_address_filter` (optional): Filter by source address
  - `dst_address_filter` (optional): Filter by destination address
  - `protocol_filter` (optional): Filter by protocol
  - `interface_filter` (optional): Filter by interface
  - `disabled_only` (optional): Show only disabled rules
  - `invalid_only` (optional): Show only invalid rules
- Example:
  ```
  mikrotik_list_nat_rules(chain_filter="srcnat")
  ```

#### `mikrotik_get_nat_rule`
Gets detailed information about a specific NAT rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_get_nat_rule(rule_id="*1")
  ```

#### `mikrotik_update_nat_rule`
Updates an existing NAT rule.
- Parameters:
  - `rule_id` (required): Rule ID
  - All parameters from `create_nat_rule` (optional)
- Example:
  ```
  mikrotik_update_nat_rule(rule_id="*1", comment="Updated NAT rule")
  ```

#### `mikrotik_remove_nat_rule`
Removes a NAT rule from MikroTik device.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_remove_nat_rule(rule_id="*1")
  ```

#### `mikrotik_move_nat_rule`
Moves a NAT rule to a different position.
- Parameters:
  - `rule_id` (required): Rule ID
  - `destination` (required): New position
- Example:
  ```
  mikrotik_move_nat_rule(rule_id="*1", destination=0)
  ```

#### `mikrotik_enable_nat_rule`
Enables a NAT rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_enable_nat_rule(rule_id="*1")
  ```

#### `mikrotik_disable_nat_rule`
Disables a NAT rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_disable_nat_rule(rule_id="*1")
  ```

### IP Pool Management

#### `mikrotik_create_ip_pool`
Creates an IP pool on MikroTik device.
- Parameters:
  - `name` (required): Pool name
  - `ranges` (required): IP ranges
  - `next_pool` (optional): Next pool name
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_ip_pool(name="pool1", ranges="192.168.1.100-192.168.1.200")
  ```

#### `mikrotik_list_ip_pools`
Lists IP pools on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `ranges_filter` (optional): Filter by ranges
  - `include_used` (optional): Include used addresses
- Example:
  ```
  mikrotik_list_ip_pools()
  ```

#### `mikrotik_get_ip_pool`
Gets detailed information about a specific IP pool.
- Parameters:
  - `name` (required): Pool name
- Example:
  ```
  mikrotik_get_ip_pool(name="pool1")
  ```

#### `mikrotik_update_ip_pool`
Updates an existing IP pool.
- Parameters:
  - `name` (required): Current pool name
  - `new_name` (optional): New name
  - `ranges` (optional): New ranges
  - `next_pool` (optional): New next pool
  - `comment` (optional): New description
- Example:
  ```
  mikrotik_update_ip_pool(name="pool1", ranges="192.168.1.100-192.168.1.250")
  ```

#### `mikrotik_remove_ip_pool`
Removes an IP pool from MikroTik device.
- Parameters:
  - `name` (required): Pool name
- Example:
  ```
  mikrotik_remove_ip_pool(name="pool1")
  ```

#### `mikrotik_list_ip_pool_used`
Lists used addresses from IP pools.
- Parameters:
  - `pool_name` (optional): Filter by pool name
  - `address_filter` (optional): Filter by address
  - `mac_filter` (optional): Filter by MAC address
  - `info_filter` (optional): Filter by info
- Example:
  ```
  mikrotik_list_ip_pool_used(pool_name="pool1")
  ```

#### `mikrotik_expand_ip_pool`
Expands an existing IP pool by adding more ranges.
- Parameters:
  - `name` (required): Pool name
  - `additional_ranges` (required): Additional IP ranges
- Example:
  ```
  mikrotik_expand_ip_pool(name="pool1", additional_ranges="192.168.1.251-192.168.1.254")
  ```

### Backup and Export Management

#### `mikrotik_create_backup`
Creates a system backup on MikroTik device.
- Parameters:
  - `name` (optional): Backup filename
  - `dont_encrypt` (optional): Don't encrypt backup
  - `include_password` (optional): Include passwords
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_backup(name="backup-2024-01-01")
  ```

#### `mikrotik_list_backups`
Lists backup files on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `include_exports` (optional): Include export files
- Example:
  ```
  mikrotik_list_backups()
  ```

#### `mikrotik_create_export`
Creates a configuration export on MikroTik device.
- Parameters:
  - `name` (optional): Export filename
  - `file_format` (optional): Format ("rsc", "json", "xml")
  - `export_type` (optional): Type ("full", "compact", "verbose")
  - `hide_sensitive` (optional): Hide sensitive data
  - `verbose` (optional): Verbose output
  - `compact` (optional): Compact output
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_create_export(name="config-export", file_format="rsc")
  ```

#### `mikrotik_export_section`
Exports a specific configuration section.
- Parameters:
  - `section` (required): Section to export
  - `name` (optional): Export filename
  - `hide_sensitive` (optional): Hide sensitive data
  - `compact` (optional): Compact output
- Example:
  ```
  mikrotik_export_section(section="/ip/firewall", name="firewall-config")
  ```

#### `mikrotik_download_file`
Downloads a file from MikroTik device.
- Parameters:
  - `filename` (required): Filename to download
  - `file_type` (optional): File type ("backup" or "export")
- Example:
  ```
  mikrotik_download_file(filename="backup-2024-01-01.backup")
  ```

#### `mikrotik_upload_file`
Uploads a file to MikroTik device.
- Parameters:
  - `filename` (required): Filename
  - `content_base64` (required): Base64 encoded content
- Example:
  ```
  mikrotik_upload_file(filename="config.rsc", content_base64="...")
  ```

#### `mikrotik_restore_backup`
Restores a system backup on MikroTik device.
- Parameters:
  - `filename` (required): Backup filename
  - `password` (optional): Backup password
- Example:
  ```
  mikrotik_restore_backup(filename="backup-2024-01-01.backup")
  ```

#### `mikrotik_import_configuration`
Imports a configuration script file.
- Parameters:
  - `filename` (required): Script filename
  - `run_after_reset` (optional): Run after reset
  - `verbose` (optional): Verbose output
- Example:
  ```
  mikrotik_import_configuration(filename="config.rsc")
  ```

#### `mikrotik_remove_file`
Removes a file from MikroTik device.
- Parameters:
  - `filename` (required): Filename to remove
- Example:
  ```
  mikrotik_remove_file(filename="old-backup.backup")
  ```

#### `mikrotik_backup_info`
Gets detailed information about a backup file.
- Parameters:
  - `filename` (required): Backup filename
- Example:
  ```
  mikrotik_backup_info(filename="backup-2024-01-01.backup")
  ```

### Log Management

#### `mikrotik_get_logs`
Gets logs from MikroTik device with filtering options.
- Parameters:
  - `topics` (optional): Log topics
  - `action` (optional): Log action
  - `time_filter` (optional): Time filter
  - `message_filter` (optional): Message filter
  - `prefix_filter` (optional): Prefix filter
  - `limit` (optional): Result limit
  - `follow` (optional): Follow logs
  - `print_as` (optional): Output format
- Example:
  ```
  mikrotik_get_logs(topics="firewall", limit=100)
  ```

#### `mikrotik_get_logs_by_severity`
Gets logs filtered by severity level.
- Parameters:
  - `severity` (required): Severity level ("debug", "info", "warning", "error", "critical")
  - `time_filter` (optional): Time filter
  - `limit` (optional): Result limit
- Example:
  ```
  mikrotik_get_logs_by_severity(severity="error", limit=50)
  ```

#### `mikrotik_get_logs_by_topic`
Gets logs for a specific topic/facility.
- Parameters:
  - `topic` (required): Log topic
  - `time_filter` (optional): Time filter
  - `limit` (optional): Result limit
- Example:
  ```
  mikrotik_get_logs_by_topic(topic="system")
  ```

#### `mikrotik_search_logs`
Searches logs for a specific term.
- Parameters:
  - `search_term` (required): Search term
  - `time_filter` (optional): Time filter
  - `case_sensitive` (optional): Case sensitive search
  - `limit` (optional): Result limit
- Example:
  ```
  mikrotik_search_logs(search_term="login failed")
  ```

#### `mikrotik_get_system_events`
Gets system-related log events.
- Parameters:
  - `event_type` (optional): Event type
  - `time_filter` (optional): Time filter
  - `limit` (optional): Result limit
- Example:
  ```
  mikrotik_get_system_events(event_type="reboot")
  ```

#### `mikrotik_get_security_logs`
Gets security-related log entries.
- Parameters:
  - `time_filter` (optional): Time filter
  - `limit` (optional): Result limit
- Example:
  ```
  mikrotik_get_security_logs(limit=100)
  ```

#### `mikrotik_clear_logs`
Clears all logs from MikroTik device.
- Parameters: None
- Example:
  ```
  mikrotik_clear_logs()
  ```

#### `mikrotik_get_log_statistics`
Gets statistics about log entries.
- Parameters: None
- Example:
  ```
  mikrotik_get_log_statistics()
  ```

#### `mikrotik_export_logs`
Exports logs to a file on the MikroTik device.
- Parameters:
  - `filename` (optional): Export filename
  - `topics` (optional): Log topics
  - `time_filter` (optional): Time filter
  - `format` (optional): Export format ("plain" or "csv")
- Example:
  ```
  mikrotik_export_logs(filename="security-logs.txt", topics="firewall")
  ```

#### `mikrotik_monitor_logs`
Monitors logs in real-time for a specified duration.
- Parameters:
  - `topics` (optional): Log topics
  - `action` (optional): Log action
  - `duration` (optional): Monitor duration in seconds
- Example:
  ```
  mikrotik_monitor_logs(topics="firewall", duration=30)
  ```

### Firewall Filter Rules Management

#### `mikrotik_create_filter_rule`
Creates a firewall filter rule on MikroTik device.
- Parameters:
  - `chain` (required): Chain type ("input", "forward", "output")
  - `action` (required): Action type
  - `src_address` (optional): Source address
  - `dst_address` (optional): Destination address
  - `src_port` (optional): Source port
  - `dst_port` (optional): Destination port
  - `protocol` (optional): Protocol
  - `in_interface` (optional): Input interface
  - `out_interface` (optional): Output interface
  - `connection_state` (optional): Connection state
  - `connection_nat_state` (optional): Connection NAT state
  - `src_address_list` (optional): Source address list
  - `dst_address_list` (optional): Destination address list
  - `limit` (optional): Rate limit
  - `tcp_flags` (optional): TCP flags
  - `comment` (optional): Description
  - `disabled` (optional): Disable rule
  - `log` (optional): Enable logging
  - `log_prefix` (optional): Log prefix
  - `place_before` (optional): Rule placement
- Example:
  ```
  mikrotik_create_filter_rule(chain="input", action="accept", protocol="tcp", dst_port="22", src_address="192.168.1.0/24")
  ```

#### `mikrotik_list_filter_rules`
Lists firewall filter rules on MikroTik device.
- Parameters:
  - `chain_filter` (optional): Filter by chain
  - `action_filter` (optional): Filter by action
  - `src_address_filter` (optional): Filter by source address
  - `dst_address_filter` (optional): Filter by destination address
  - `protocol_filter` (optional): Filter by protocol
  - `interface_filter` (optional): Filter by interface
  - `disabled_only` (optional): Show only disabled rules
  - `invalid_only` (optional): Show only invalid rules
  - `dynamic_only` (optional): Show only dynamic rules
- Example:
  ```
  mikrotik_list_filter_rules(chain_filter="input")
  ```

#### `mikrotik_get_filter_rule`
Gets detailed information about a specific firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_get_filter_rule(rule_id="*1")
  ```

#### `mikrotik_update_filter_rule`
Updates an existing firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
  - All parameters from `create_filter_rule` (optional)
- Example:
  ```
  mikrotik_update_filter_rule(rule_id="*1", comment="Updated rule")
  ```

#### `mikrotik_remove_filter_rule`
Removes a firewall filter rule from MikroTik device.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_remove_filter_rule(rule_id="*1")
  ```

#### `mikrotik_move_filter_rule`
Moves a firewall filter rule to a different position.
- Parameters:
  - `rule_id` (required): Rule ID
  - `destination` (required): New position
- Example:
  ```
  mikrotik_move_filter_rule(rule_id="*1", destination=0)
  ```

#### `mikrotik_enable_filter_rule`
Enables a firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_enable_filter_rule(rule_id="*1")
  ```

#### `mikrotik_disable_filter_rule`
Disables a firewall filter rule.
- Parameters:
  - `rule_id` (required): Rule ID
- Example:
  ```
  mikrotik_disable_filter_rule(rule_id="*1")
  ```

#### `mikrotik_create_basic_firewall_setup`
Creates a basic firewall setup with common security rules.
- Parameters: None
- Example:
  ```
  mikrotik_create_basic_firewall_setup()
  ```

### Route Management

#### `mikrotik_add_route`
Adds a route to MikroTik routing table.
- Parameters:
  - `dst_address` (required): Destination address
  - `gateway` (required): Gateway address
  - `distance` (optional): Administrative distance
  - `scope` (optional): Route scope
  - `target_scope` (optional): Target scope
  - `routing_mark` (optional): Routing mark
  - `comment` (optional): Description
  - `disabled` (optional): Disable route
  - `vrf_interface` (optional): VRF interface
  - `pref_src` (optional): Preferred source
  - `check_gateway` (optional): Gateway check method
- Example:
  ```
  mikrotik_add_route(dst_address="10.0.0.0/8", gateway="192.168.1.1")
  ```

#### `mikrotik_list_routes`
Lists routes in MikroTik routing table.
- Parameters:
  - `dst_filter` (optional): Filter by destination
  - `gateway_filter` (optional): Filter by gateway
  - `routing_mark_filter` (optional): Filter by routing mark
  - `distance_filter` (optional): Filter by distance
  - `active_only` (optional): Show only active routes
  - `disabled_only` (optional): Show only disabled routes
  - `dynamic_only` (optional): Show only dynamic routes
  - `static_only` (optional): Show only static routes
- Example:
  ```
  mikrotik_list_routes(active_only=true)
  ```

#### `mikrotik_get_route`
Gets detailed information about a specific route.
- Parameters:
  - `route_id` (required): Route ID
- Example:
  ```
  mikrotik_get_route(route_id="*1")
  ```

#### `mikrotik_update_route`
Updates an existing route in MikroTik routing table.
- Parameters:
  - `route_id` (required): Route ID
  - All parameters from `add_route` (optional)
- Example:
  ```
  mikrotik_update_route(route_id="*1", comment="Updated route")
  ```

#### `mikrotik_remove_route`
Removes a route from MikroTik routing table.
- Parameters:
  - `route_id` (required): Route ID
- Example:
  ```
  mikrotik_remove_route(route_id="*1")
  ```

#### `mikrotik_enable_route`
Enables a route.
- Parameters:
  - `route_id` (required): Route ID
- Example:
  ```
  mikrotik_enable_route(route_id="*1")
  ```

#### `mikrotik_disable_route`
Disables a route.
- Parameters:
  - `route_id` (required): Route ID
- Example:
  ```
  mikrotik_disable_route(route_id="*1")
  ```

#### `mikrotik_get_routing_table`
Gets a specific routing table.
- Parameters:
  - `table_name` (optional): Table name (default: "main")
  - `protocol_filter` (optional): Filter by protocol
  - `active_only` (optional): Show only active routes
- Example:
  ```
  mikrotik_get_routing_table(table_name="main")
  ```

#### `mikrotik_check_route_path`
Checks the route path to a destination.
- Parameters:
  - `destination` (required): Destination address
  - `source` (optional): Source address
  - `routing_mark` (optional): Routing mark
- Example:
  ```
  mikrotik_check_route_path(destination="8.8.8.8")
  ```

#### `mikrotik_get_route_cache`
Gets the route cache.
- Parameters: None
- Example:
  ```
  mikrotik_get_route_cache()
  ```

#### `mikrotik_flush_route_cache`
Flushes the route cache.
- Parameters: None
- Example:
  ```
  mikrotik_flush_route_cache()
  ```

#### `mikrotik_add_default_route`
Adds a default route (0.0.0.0/0).
- Parameters:
  - `gateway` (required): Gateway address
  - `distance` (optional): Administrative distance
  - `comment` (optional): Description
  - `check_gateway` (optional): Gateway check method
- Example:
  ```
  mikrotik_add_default_route(gateway="192.168.1.1")
  ```

#### `mikrotik_add_blackhole_route`
Adds a blackhole route.
- Parameters:
  - `dst_address` (required): Destination address
  - `distance` (optional): Administrative distance
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_add_blackhole_route(dst_address="10.0.0.0/8")
  ```

#### `mikrotik_get_route_statistics`
Gets routing table statistics.
- Parameters: None
- Example:
  ```
  mikrotik_get_route_statistics()
  ```

### DNS Management

#### `mikrotik_set_dns_servers`
Sets DNS server configuration on MikroTik device.
- Parameters:
  - `servers` (required): DNS server list
  - `allow_remote_requests` (optional): Allow remote requests
  - `max_udp_packet_size` (optional): Max UDP packet size
  - `max_concurrent_queries` (optional): Max concurrent queries
  - `cache_size` (optional): Cache size
  - `cache_max_ttl` (optional): Max cache TTL
  - `use_doh` (optional): Use DNS over HTTPS
  - `doh_server` (optional): DoH server URL
  - `verify_doh_cert` (optional): Verify DoH certificate
- Example:
  ```
  mikrotik_set_dns_servers(servers=["8.8.8.8", "8.8.4.4"], allow_remote_requests=true)
  ```

#### `mikrotik_get_dns_settings`
Gets current DNS configuration.
- Parameters: None
- Example:
  ```
  mikrotik_get_dns_settings()
  ```

#### `mikrotik_add_dns_static`
Adds a static DNS entry.
- Parameters:
  - `name` (required): DNS name
  - `address` (optional): IP address
  - `cname` (optional): CNAME record
  - `mx_preference` (optional): MX preference
  - `mx_exchange` (optional): MX exchange
  - `text` (optional): TXT record
  - `srv_priority` (optional): SRV priority
  - `srv_weight` (optional): SRV weight
  - `srv_port` (optional): SRV port
  - `srv_target` (optional): SRV target
  - `ttl` (optional): Time to live
  - `comment` (optional): Description
  - `disabled` (optional): Disable entry
  - `regexp` (optional): Regular expression
- Example:
  ```
  mikrotik_add_dns_static(name="router.local", address="192.168.1.1")
  ```

#### `mikrotik_list_dns_static`
Lists static DNS entries.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `address_filter` (optional): Filter by address
  - `type_filter` (optional): Filter by type
  - `disabled_only` (optional): Show only disabled entries
  - `regexp_only` (optional): Show only regexp entries
- Example:
  ```
  mikrotik_list_dns_static()
  ```

#### `mikrotik_get_dns_static`
Gets details of a specific static DNS entry.
- Parameters:
  - `entry_id` (required): Entry ID
- Example:
  ```
  mikrotik_get_dns_static(entry_id="*1")
  ```

#### `mikrotik_update_dns_static`
Updates an existing static DNS entry.
- Parameters:
  - `entry_id` (required): Entry ID
  - All parameters from `add_dns_static` (optional)
- Example:
  ```
  mikrotik_update_dns_static(entry_id="*1", address="192.168.1.2")
  ```

#### `mikrotik_remove_dns_static`
Removes a static DNS entry.
- Parameters:
  - `entry_id` (required): Entry ID
- Example:
  ```
  mikrotik_remove_dns_static(entry_id="*1")
  ```

#### `mikrotik_enable_dns_static`
Enables a static DNS entry.
- Parameters:
  - `entry_id` (required): Entry ID
- Example:
  ```
  mikrotik_enable_dns_static(entry_id="*1")
  ```

#### `mikrotik_disable_dns_static`
Disables a static DNS entry.
- Parameters:
  - `entry_id` (required): Entry ID
- Example:
  ```
  mikrotik_disable_dns_static(entry_id="*1")
  ```

#### `mikrotik_get_dns_cache`
Gets the current DNS cache.
- Parameters: None
- Example:
  ```
  mikrotik_get_dns_cache()
  ```

#### `mikrotik_flush_dns_cache`
Flushes the DNS cache.
- Parameters: None
- Example:
  ```
  mikrotik_flush_dns_cache()
  ```

#### `mikrotik_get_dns_cache_statistics`
Gets DNS cache statistics.
- Parameters: None
- Example:
  ```
  mikrotik_get_dns_cache_statistics()
  ```

#### `mikrotik_add_dns_regexp`
Adds a DNS regexp entry for pattern matching.
- Parameters:
  - `regexp` (required): Regular expression
  - `address` (required): IP address
  - `ttl` (optional): Time to live
  - `comment` (optional): Description
  - `disabled` (optional): Disable entry
- Example:
  ```
  mikrotik_add_dns_regexp(regexp="^ad[0-9]*\\.doubleclick\\.net$", address="127.0.0.1")
  ```

#### `mikrotik_test_dns_query`
Tests a DNS query.
- Parameters:
  - `name` (required): DNS name to query
  - `server` (optional): DNS server to use
  - `type` (optional): Query type
- Example:
  ```
  mikrotik_test_dns_query(name="google.com")
  ```

#### `mikrotik_export_dns_config`
Exports DNS configuration to a file.
- Parameters:
  - `filename` (optional): Export filename
- Example:
  ```
  mikrotik_export_dns_config(filename="dns-config.rsc")
  ```

### User Management

#### `mikrotik_add_user`
Adds a new user to MikroTik device.
- Parameters:
  - `name` (required): Username
  - `password` (required): Password
  - `group` (optional): User group
  - `address` (optional): Allowed address
  - `comment` (optional): Description
  - `disabled` (optional): Disable user
- Example:
  ```
  mikrotik_add_user(name="john", password="secure123", group="full")
  ```

#### `mikrotik_list_users`
Lists users on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `group_filter` (optional): Filter by group
  - `disabled_only` (optional): Show only disabled users
  - `active_only` (optional): Show only active users
- Example:
  ```
  mikrotik_list_users(group_filter="full")
  ```

#### `mikrotik_get_user`
Gets detailed information about a specific user.
- Parameters:
  - `name` (required): Username
- Example:
  ```
  mikrotik_get_user(name="john")
  ```

#### `mikrotik_update_user`
Updates an existing user on MikroTik device.
- Parameters:
  - `name` (required): Current username
  - `new_name` (optional): New username
  - `password` (optional): New password
  - `group` (optional): New group
  - `address` (optional): New allowed address
  - `comment` (optional): New description
  - `disabled` (optional): Enable/disable user
- Example:
  ```
  mikrotik_update_user(name="john", group="read")
  ```

#### `mikrotik_remove_user`
Removes a user from MikroTik device.
- Parameters:
  - `name` (required): Username
- Example:
  ```
  mikrotik_remove_user(name="john")
  ```

#### `mikrotik_disable_user`
Disables a user account.
- Parameters:
  - `name` (required): Username
- Example:
  ```
  mikrotik_disable_user(name="john")
  ```

#### `mikrotik_enable_user`
Enables a user account.
- Parameters:
  - `name` (required): Username
- Example:
  ```
  mikrotik_enable_user(name="john")
  ```

#### `mikrotik_add_user_group`
Adds a new user group to MikroTik device.
- Parameters:
  - `name` (required): Group name
  - `policy` (required): Policy list
  - `skin` (optional): UI skin
  - `comment` (optional): Description
- Example:
  ```
  mikrotik_add_user_group(name="operators", policy=["read", "write", "reboot"])
  ```

#### `mikrotik_list_user_groups`
Lists user groups on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by name
  - `policy_filter` (optional): Filter by policy
- Example:
  ```
  mikrotik_list_user_groups()
  ```

#### `mikrotik_get_user_group`
Gets detailed information about a specific user group.
- Parameters:
  - `name` (required): Group name
- Example:
  ```
  mikrotik_get_user_group(name="operators")
  ```

#### `mikrotik_update_user_group`
Updates an existing user group on MikroTik device.
- Parameters:
  - `name` (required): Current group name
  - `new_name` (optional): New name
  - `policy` (optional): New policy list
  - `skin` (optional): New UI skin
  - `comment` (optional): New description
- Example:
  ```
  mikrotik_update_user_group(name="operators", policy=["read", "write"])
  ```

#### `mikrotik_remove_user_group`
Removes a user group from MikroTik device.
- Parameters:
  - `name` (required): Group name
- Example:
  ```
  mikrotik_remove_user_group(name="operators")
  ```

#### `mikrotik_get_active_users`
Gets currently active/logged-in users.
- Parameters: None
- Example:
  ```
  mikrotik_get_active_users()
  ```

#### `mikrotik_disconnect_user`
Disconnects an active user session.
- Parameters:
  - `user_id` (required): User session ID
- Example:
  ```
  mikrotik_disconnect_user(user_id="*1")
  ```

#### `mikrotik_export_user_config`
Exports user configuration to a file.
- Parameters:
  - `filename` (optional): Export filename
- Example:
  ```
  mikrotik_export_user_config(filename="users.rsc")
  ```

#### `mikrotik_set_user_ssh_keys`
Sets SSH public keys for a user.
- Parameters:
  - `username` (required): Username
  - `key_file` (required): SSH key filename
- Example:
  ```
  mikrotik_set_user_ssh_keys(username="john", key_file="id_rsa.pub")
  ```

#### `mikrotik_list_user_ssh_keys`
Lists SSH keys for a specific user.
- Parameters:
  - `username` (required): Username
- Example:
  ```
  mikrotik_list_user_ssh_keys(username="john")
  ```

#### `mikrotik_remove_user_ssh_key`
Removes an SSH key.
- Parameters:
  - `key_id` (required): SSH key ID
- Example:
  ```
  mikrotik_remove_user_ssh_key(key_id="*1")
  ```

## Configuration

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "uvx",
      "args": ["mcp-server-mikrotik", "--host", "<HOST>", "--username", "<USERNAME>", "--password", "<PASSWORD>", "--port", "22"]
    }
  }
}
```

## Inspector

```shell
# Run the inspector against the mcp-server-mikrotik
npx @modelcontextprotocol/inspector uvx mcp-server-mikrotik --host <HOST> --username <USERNAME> --password <PASSWORD> --port 22

# Run the inspector against the mcp-config.json
npm install -g @modelcontextprotocol/inspector
cp mcp-config.json.example mcp-config.json
nano mcp-config.json # Edit the values
mcp-inspector --config mcp-config.json --server my-python-server
```

## UV
Here's the new markdown content that you should add **after the Inspector section and before the License section**:

## Usage Examples with mcp-cli

### VLAN Interface Operations
```bash
# Create a VLAN interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_vlan_interface --tool-args '{"name": "vlan100", "vlan_id": 100, "interface": "ether1", "comment": "Production VLAN"}'

# List all VLANs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_vlan_interfaces --tool-args '{}'

# Get specific VLAN details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_vlan_interface --tool-args '{"name": "vlan100"}'

# Update VLAN interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_update_vlan_interface --tool-args '{"name": "vlan100", "comment": "Updated Production VLAN"}'

# Remove VLAN interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_vlan_interface --tool-args '{"name": "vlan100"}'
```

### IP Address Management
```bash
# Add IP address to interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_ip_address --tool-args '{"address": "192.168.100.1/24", "interface": "vlan100", "comment": "Gateway address"}'

# List IP addresses
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_ip_addresses --tool-args '{"interface_filter": "vlan100"}'

# Get specific IP address
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_ip_address --tool-args '{"address_id": "*1"}'

# Remove IP address
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_ip_address --tool-args '{"address_id": "*1"}'
```

### DHCP Server Configuration
```bash
# Create DHCP pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_pool --tool-args '{"name": "pool-vlan100", "ranges": "192.168.100.10-192.168.100.200"}'

# Create DHCP network
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_network --tool-args '{"network": "192.168.100.0/24", "gateway": "192.168.100.1", "dns_servers": ["8.8.8.8", "8.8.4.4"]}'

# Create DHCP server
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_server --tool-args '{"name": "dhcp-vlan100", "interface": "vlan100", "address_pool": "pool-vlan100"}'

# List DHCP servers
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_dhcp_servers --tool-args '{}'

# Get DHCP server details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_dhcp_server --tool-args '{"name": "dhcp-vlan100"}'

# Remove DHCP server
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_dhcp_server --tool-args '{"name": "dhcp-vlan100"}'
```

### NAT Rule Management
```bash
# Create masquerade rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "srcnat", "action": "masquerade", "out_interface": "ether1", "comment": "Internet access"}'

# Create port forwarding rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "dstnat", "action": "dst-nat", "dst_port": "80", "protocol": "tcp", "to_addresses": "192.168.100.10", "to_ports": "80", "comment": "Web server"}'

# List NAT rules
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_nat_rules --tool-args '{"chain_filter": "srcnat"}'

# Get NAT rule details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_nat_rule --tool-args '{"rule_id": "*1"}'

# Move NAT rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_move_nat_rule --tool-args '{"rule_id": "*1", "destination": 0}'

# Enable/Disable NAT rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_nat_rule --tool-args '{"rule_id": "*1"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_nat_rule --tool-args '{"rule_id": "*1"}'

# Remove NAT rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_nat_rule --tool-args '{"rule_id": "*1"}'
```

### IP Pool Management
```bash
# Create IP pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_ip_pool --tool-args '{"name": "main-pool", "ranges": "192.168.1.100-192.168.1.200"}'

# List IP pools
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_ip_pools --tool-args '{"include_used": true}'

# Get IP pool details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_ip_pool --tool-args '{"name": "main-pool"}'

# List used addresses in pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_ip_pool_used --tool-args '{"pool_name": "main-pool"}'

# Expand IP pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_expand_ip_pool --tool-args '{"name": "main-pool", "additional_ranges": "192.168.1.201-192.168.1.250"}'

# Remove IP pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_ip_pool --tool-args '{"name": "main-pool"}'
```

### Backup and Export
```bash
# Create system backup
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_backup --tool-args '{"name": "full_backup", "include_password": true}'

# Create configuration export
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_export --tool-args '{"name": "config_export", "file_format": "rsc", "export_type": "full"}'

# Export specific section
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_section --tool-args '{"section": "/ip/firewall", "name": "firewall_export"}'

# List backups
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_backups --tool-args '{"include_exports": true}'

# Download file
uv run mcp-cli cmd --server mikrotik --tool mikrotik_download_file --tool-args '{"filename": "full_backup.backup"}'

# Upload file
uv run mcp-cli cmd --server mikrotik --tool mikrotik_upload_file --tool-args '{"filename": "config.rsc", "content_base64": "base64_encoded_content"}'

# Restore backup
uv run mcp-cli cmd --server mikrotik --tool mikrotik_restore_backup --tool-args '{"filename": "full_backup.backup"}'

# Import configuration
uv run mcp-cli cmd --server mikrotik --tool mikrotik_import_configuration --tool-args '{"filename": "config.rsc"}'

# Remove file
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_file --tool-args '{"filename": "old_backup.backup"}'
```

### Log Management
```bash
# Get logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_logs --tool-args '{"topics": "firewall", "limit": 100}'

# Get logs by severity
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_logs_by_severity --tool-args '{"severity": "error", "limit": 50}'

# Search logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_search_logs --tool-args '{"search_term": "login failed", "case_sensitive": false}'

# Get security logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_security_logs --tool-args '{"limit": 100}'

# Get log statistics
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_log_statistics --tool-args '{}'

# Export logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_logs --tool-args '{"filename": "firewall_logs", "topics": "firewall", "format": "csv"}'

# Monitor logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_monitor_logs --tool-args '{"topics": "firewall", "duration": 30}'

# Clear logs
uv run mcp-cli cmd --server mikrotik --tool mikrotik_clear_logs --tool-args '{}'
```

### Firewall Filter Rules
```bash
# Create basic firewall rules
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_filter_rule --tool-args '{"chain": "input", "action": "accept", "connection_state": "established,related", "comment": "Accept established"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_filter_rule --tool-args '{"chain": "input", "action": "drop", "connection_state": "invalid", "comment": "Drop invalid"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_filter_rule --tool-args '{"chain": "input", "action": "accept", "protocol": "icmp", "comment": "Accept ICMP"}'

# List firewall rules
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_filter_rules --tool-args '{"chain_filter": "input"}'

# Get firewall rule details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_filter_rule --tool-args '{"rule_id": "*1"}'

# Move firewall rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_move_filter_rule --tool-args '{"rule_id": "*1", "destination": 0}'

# Enable/Disable firewall rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_filter_rule --tool-args '{"rule_id": "*1"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_filter_rule --tool-args '{"rule_id": "*1"}'

# Create basic firewall setup
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_basic_firewall_setup --tool-args '{}'

# Remove firewall rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_filter_rule --tool-args '{"rule_id": "*1"}'
```

### Route Management
```bash
# Add route
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_route --tool-args '{"dst_address": "10.0.0.0/8", "gateway": "192.168.1.1", "comment": "Corporate network"}'

# Add default route
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_default_route --tool-args '{"gateway": "192.168.1.1", "distance": 1}'

# Add blackhole route
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_blackhole_route --tool-args '{"dst_address": "192.168.99.0/24", "comment": "Block subnet"}'

# List routes
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_routes --tool-args '{"active_only": true}'

# Get route details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_route --tool-args '{"route_id": "*1"}'

# Check route path
uv run mcp-cli cmd --server mikrotik --tool mikrotik_check_route_path --tool-args '{"destination": "8.8.8.8"}'

# Get routing table
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_routing_table --tool-args '{"table_name": "main"}'

# Get route statistics
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_route_statistics --tool-args '{}'

# Enable/Disable route
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_route --tool-args '{"route_id": "*1"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_route --tool-args '{"route_id": "*1"}'

# Remove route
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_route --tool-args '{"route_id": "*1"}'
```

### DNS Configuration
```bash
# Set DNS servers
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_dns_servers --tool-args '{"servers": ["8.8.8.8", "8.8.4.4"], "allow_remote_requests": true}'

# Get DNS settings
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_dns_settings --tool-args '{}'

# Add static DNS entry
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_dns_static --tool-args '{"name": "router.local", "address": "192.168.1.1", "comment": "Local router"}'

# Add CNAME record
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_dns_static --tool-args '{"name": "www.example.com", "cname": "example.com"}'

# List static DNS entries
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_dns_static --tool-args '{"name_filter": "local"}'

# Update DNS entry
uv run mcp-cli cmd --server mikrotik --tool mikrotik_update_dns_static --tool-args '{"entry_id": "*1", "address": "192.168.1.2"}'

# Add DNS regexp
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_dns_regexp --tool-args '{"regexp": ".*\\.ads\\..*", "address": "0.0.0.0", "comment": "Block ads"}'

# Test DNS query
uv run mcp-cli cmd --server mikrotik --tool mikrotik_test_dns_query --tool-args '{"name": "google.com"}'

# Get DNS cache
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_dns_cache --tool-args '{}'

# Flush DNS cache
uv run mcp-cli cmd --server mikrotik --tool mikrotik_flush_dns_cache --tool-args '{}'

# Export DNS config
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_dns_config --tool-args '{"filename": "dns_config"}'

# Remove DNS entry
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_dns_static --tool-args '{"entry_id": "*1"}'
```

### User Management
```bash
# Add user
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_user --tool-args '{"name": "newuser", "password": "SecurePass123", "group": "write", "comment": "New operator"}'

# List users
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_users --tool-args '{"group_filter": "write"}'

# Get user details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_user --tool-args '{"name": "newuser"}'

# Update user
uv run mcp-cli cmd --server mikrotik --tool mikrotik_update_user --tool-args '{"name": "newuser", "password": "NewSecurePass456"}'

# Enable/Disable user
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_user --tool-args '{"name": "newuser"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_user --tool-args '{"name": "newuser"}'

# Add user group
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_user_group --tool-args '{"name": "operators", "policy": ["read", "write", "test"], "comment": "Operator group"}'

# List user groups
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_user_groups --tool-args '{}'

# Get active users
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_active_users --tool-args '{}'

# Export user config
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_user_config --tool-args '{"filename": "user_config"}'

# Remove user
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_user --tool-args '{"name": "newuser"}'
```

#### Setting Up a New Network Segment
```bash
# Create VLAN
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_vlan_interface --tool-args '{"name": "vlan200", "vlan_id": 200, "interface": "ether1", "comment": "Guest Network"}'

# Add IP address
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_ip_address --tool-args '{"address": "192.168.200.1/24", "interface": "vlan200"}'

# Create DHCP pool
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_pool --tool-args '{"name": "pool-200", "ranges": "192.168.200.10-192.168.200.100"}'

# Create DHCP network
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_network --tool-args '{"network": "192.168.200.0/24", "gateway": "192.168.200.1", "dns_servers": ["8.8.8.8", "8.8.4.4"]}'

# Create DHCP server
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_dhcp_server --tool-args '{"name": "dhcp-200", "interface": "vlan200", "address_pool": "pool-200"}'

# Create NAT rule
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "srcnat", "action": "masquerade", "out_interface": "ether1", "comment": "Internet access for VLAN 200"}'
```

#### Port Forwarding Setup
```bash
# Forward HTTP traffic
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "dstnat", "action": "dst-nat", "dst_address": "203.0.113.1", "dst_port": "80", "protocol": "tcp", "to_addresses": "192.168.100.10", "to_ports": "80", "comment": "Web server"}'

# Forward HTTPS traffic
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "dstnat", "action": "dst-nat", "dst_address": "203.0.113.1", "dst_port": "443", "protocol": "tcp", "to_addresses": "192.168.100.10", "to_ports": "443", "comment": "HTTPS server"}'

# Forward custom SSH port
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_nat_rule --tool-args '{"chain": "dstnat", "action": "dst-nat", "dst_address": "203.0.113.1", "dst_port": "2222", "protocol": "tcp", "to_addresses": "192.168.100.10", "to_ports": "22", "comment": "SSH server"}'
```

#### Backup and Restore Process
```bash
# Create backup user
uv run mcp-cli cmd --server mikrotik --tool mikrotik_add_user --tool-args '{"name": "backup_user", "password": "BackupPass123", "group": "read", "comment": "Backup account"}'

# Create full backup
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_backup --tool-args '{"name": "daily_backup", "include_password": true}'

# Export configuration
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_export --tool-args '{"name": "config_export", "file_format": "rsc", "export_type": "full"}'

# Export firewall rules
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_section --tool-args '{"section": "/ip/firewall/filter", "name": "firewall_backup"}'

# Export NAT rules
uv run mcp-cli cmd --server mikrotik --tool mikrotik_export_section --tool-args '{"section": "/ip/firewall/nat", "name": "nat_backup"}'
```

### Create Wireless Interface
```bash
# Create basic AP interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "wlan1", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "MyNetwork", "comment": "Main WiFi Network"}'

# Create station interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "wlan-sta", "radio_name": "wlan2", "mode": "station", "ssid": "UpstreamWiFi"}'

# Create with specific frequency and band
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "wlan-5g", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "MyNetwork-5G", "frequency": "5180", "band": "5ghz-a/n/ac", "channel_width": "80mhz"}'
```

### List and Manage Wireless Interfaces
```bash
# List all wireless interfaces
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_interfaces --tool-args '{}'

# List only AP interfaces
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_interfaces --tool-args '{"mode_filter": "ap-bridge"}'

# List only running interfaces
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_interfaces --tool-args '{"running_only": true}'

# Get specific interface details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_interface --tool-args '{"name": "wlan1"}'

# Update wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_update_wireless_interface --tool-args '{"name": "wlan1", "ssid": "UpdatedNetworkName", "comment": "Updated main network"}'

# Enable/Disable wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_wireless_interface --tool-args '{"name": "wlan1"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "wlan1"}'

# Remove wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_wireless_interface --tool-args '{"name": "wlan-guest"}'
```

## Wireless Security Profile Management

### Create Security Profiles
```bash
# Create WPA2-PSK security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "wpa2-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-psk"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "wpa2_pre_shared_key": "SecurePassword123"}'

# Create mixed WPA/WPA2 profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "mixed-security", "mode": "dynamic-keys", "authentication_types": ["wpa-psk", "wpa2-psk"], "unicast_ciphers": ["tkip", "aes-ccm"], "group_ciphers": ["tkip"], "wpa_pre_shared_key": "Password123", "wpa2_pre_shared_key": "Password123"}'

# Create WPA2-Enterprise profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "enterprise-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-eap"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "eap_methods": "peap,tls"}'

# Create open network profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "open-network", "mode": "none", "comment": "Guest network - no security"}'
```

### Manage Security Profiles
```bash
# List all security profiles
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_security_profiles --tool-args '{}'

# List WPA2 profiles only
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_security_profiles --tool-args '{"mode_filter": "dynamic-keys"}'

# Get specific profile details
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_security_profile --tool-args '{"name": "wpa2-security"}'

# Apply security profile to interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "wlan1", "security_profile": "wpa2-security"}'

# Remove security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_wireless_security_profile --tool-args '{"name": "old-profile"}'
```

## Wireless Network Operations

### Network Scanning and Monitoring
```bash
# Scan for available networks
uv run mcp-cli cmd --server mikrotik --tool mikrotik_scan_wireless_networks --tool-args '{"interface": "wlan1", "duration": 10}'

# Quick scan (5 seconds)
uv run mcp-cli cmd --server mikrotik --tool mikrotik_scan_wireless_networks --tool-args '{"interface": "wlan2"}'

# Get connected clients (all interfaces)
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_registration_table --tool-args '{}'

# Get clients for specific interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_registration_table --tool-args '{"interface": "wlan1"}'
```

## Wireless Access List Management

### Create Access List Entries
```bash
# Allow specific MAC address
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_access_list --tool-args '{"interface": "wlan1", "mac_address": "AA:BB:CC:DD:EE:FF", "action": "accept", "comment": "Trusted device"}'

# Block specific MAC address
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_access_list --tool-args '{"interface": "wlan1", "mac_address": "11:22:33:44:55:66", "action": "reject", "comment": "Blocked device"}'

# Allow with signal strength requirement
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_access_list --tool-args '{"interface": "wlan1", "mac_address": "AA:BB:CC:DD:EE:FF", "action": "accept", "signal_range": "-80..-50", "comment": "Strong signal only"}'

# Time-based access control
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_access_list --tool-args '{"interface": "wlan1", "mac_address": "AA:BB:CC:DD:EE:FF", "action": "accept", "time": "8h-18h,mon,tue,wed,thu,fri", "comment": "Work hours only"}'
```

### Manage Access Lists
```bash
# List all access list entries
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_access_list --tool-args '{}'

# List entries for specific interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_access_list --tool-args '{"interface_filter": "wlan1"}'

# List only blocked entries
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_access_list --tool-args '{"action_filter": "reject"}'

# Remove access list entry
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_wireless_access_list_entry --tool-args '{"entry_id": "*1"}'
```

## Complete WiFi Network Setup Examples

### Basic Home Network Setup
```bash
# 1. Create security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "home-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-psk"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "wpa2_pre_shared_key": "MyHomePassword123"}'

# 2. Create wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "home-wifi", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "HomeNetwork", "band": "2ghz-b/g/n", "comment": "Main home network"}'

# 3. Apply security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "home-wifi", "security_profile": "home-security"}'

# 4. Enable the interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "home-wifi"}'
```

### Guest Network Setup
```bash
# 1. Create open security profile for guests
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "guest-open", "mode": "none", "comment": "Open guest network"}'

# 2. Create guest wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "guest-wifi", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "GuestNetwork", "comment": "Guest access network"}'

# 3. Apply open security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "guest-wifi", "security_profile": "guest-open"}'

# 4. Enable guest network
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "guest-wifi"}'
```

### Enterprise Network Setup
```bash
# 1. Create WPA2-Enterprise security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "corp-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-eap"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "eap_methods": "peap", "comment": "Corporate WPA2-Enterprise"}'

# 2. Create corporate wireless interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "corp-wifi", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "CorpNetwork", "band": "5ghz-a/n/ac", "channel_width": "80mhz", "comment": "Corporate network"}'

# 3. Apply enterprise security
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "corp-wifi", "security_profile": "corp-security"}'

# 4. Create access control for specific devices
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_access_list --tool-args '{"interface": "corp-wifi", "mac_address": "00:11:22:33:44:55", "action": "accept", "comment": "Corporate laptop"}'
```

### Dual-Band Setup (2.4GHz + 5GHz)
```bash
# 1. Create security profile
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "dual-band-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-psk"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "wpa2_pre_shared_key": "DualBandPassword123"}'

# 2. Create 2.4GHz interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "wifi-2g", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "MyNetwork", "band": "2ghz-b/g/n", "channel_width": "20mhz", "comment": "2.4GHz network"}'

# 3. Create 5GHz interface  
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "wifi-5g", "radio_name": "wlan2", "mode": "ap-bridge", "ssid": "MyNetwork-5G", "band": "5ghz-a/n/ac", "channel_width": "80mhz", "comment": "5GHz network"}'

# 4. Apply security to both interfaces
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "wifi-2g", "security_profile": "dual-band-security"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "wifi-5g", "security_profile": "dual-band-security"}'

# 5. Enable both interfaces
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "wifi-2g"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "wifi-5g"}'
```

### Point-to-Point Wireless Link
```bash
# On first device (Station)
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "p2p-station", "radio_name": "wlan1", "mode": "station", "ssid": "P2P-Link", "frequency": "5180", "band": "5ghz-a/n"}'

# On second device (AP)  
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_interface --tool-args '{"name": "p2p-ap", "radio_name": "wlan1", "mode": "ap-bridge", "ssid": "P2P-Link", "frequency": "5180", "band": "5ghz-a/n"}'

# Create security for P2P link
uv run mcp-cli cmd --server mikrotik --tool mikrotik_create_wireless_security_profile --tool-args '{"name": "p2p-security", "mode": "dynamic-keys", "authentication_types": ["wpa2-psk"], "unicast_ciphers": ["aes-ccm"], "group_ciphers": ["aes-ccm"], "wpa2_pre_shared_key": "P2PLinkPassword123"}'

# Apply security to both ends
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "p2p-station", "security_profile": "p2p-security"}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_set_wireless_security_profile --tool-args '{"interface_name": "p2p-ap", "security_profile": "p2p-security"}'
```

## Monitoring and Troubleshooting

### Network Analysis
```bash
# Scan for interference and available channels
uv run mcp-cli cmd --server mikrotik --tool mikrotik_scan_wireless_networks --tool-args '{"interface": "wlan1", "duration": 30}'

# Monitor connected clients
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_registration_table --tool-args '{"interface": "wlan1"}'

# Check interface status
uv run mcp-cli cmd --server mikrotik --tool mikrotik_get_wireless_interface --tool-args '{"name": "wlan1"}'

# List all wireless configurations
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_interfaces --tool-args '{}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_security_profiles --tool-args '{}'
uv run mcp-cli cmd --server mikrotik --tool mikrotik_list_wireless_access_list --tool-args '{}'
```

### Maintenance Operations
```bash
# Disable interface for maintenance
uv run mcp-cli cmd --server mikrotik --tool mikrotik_disable_wireless_interface --tool-args '{"name": "wlan1"}'

# Update configuration
uv run mcp-cli cmd --server mikrotik --tool mikrotik_update_wireless_interface --tool-args '{"name": "wlan1", "channel_width": "40mhz", "comment": "Updated for better performance"}'

# Re-enable interface
uv run mcp-cli cmd --server mikrotik --tool mikrotik_enable_wireless_interface --tool-args '{"name": "wlan1"}'

# Clean up unused profiles
uv run mcp-cli cmd --server mikrotik --tool mikrotik_remove_wireless_security_profile --tool-args '{"name": "old-profile"}'
```

# Using MCPO with MikroTik MCP Server

This guide shows how to expose your MikroTik MCP server as a RESTful API using MCPO (MCP-to-OpenAPI proxy).

## Prerequisites

- Python 3.8+
- MikroTik MCP server already set up
- `uv` package manager (recommended) or `pip`

## Installation

Install MCPO using one of these methods:

```bash
# Option 1: Using uvx (recommended - no installation needed)
uvx mcpo --help

# Option 2: Using pip
pip install mcpo
```

## Configuration

Create a `mcp-config.json` file in your project directory:

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "python",
      "args": [
        "src/mcp_mikrotik/server.py",
        "--password", "admin",
        "--host", "192.168.1.1",
        "--port", "22",
        "--username", "admin"
      ],
      "env": {}
    }
  }
}
```

**Note:** Adjust the MikroTik connection parameters (`host`, `username`, `password`, `port`) according to your setup.

## Starting the MCPO Server

```bash
# Start MCPO with API key authentication
uvx mcpo --port 8000 --api-key "your-secret-key" --config ./mcp-config.json

# Or without authentication (not recommended for production)
uvx mcpo --port 8000 --config ./mcp-config.json
```

The server will start and display:
- Server running on `http://0.0.0.0:8000`
- Interactive API docs available at `http://localhost:8000/docs`

### cURL Examples

**List IP Addresses:**
```bash
curl -X POST http://localhost:8000/my-python-server/mikrotik_list_ip_addresses \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.