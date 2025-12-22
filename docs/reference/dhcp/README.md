# DHCP Server Management

## `mikrotik_create_dhcp_server`
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

## `mikrotik_list_dhcp_servers`
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

## `mikrotik_get_dhcp_server`
Gets detailed information about a specific DHCP server.
- Parameters:
  - `name` (required): DHCP server name
- Example:
  ```
  mikrotik_get_dhcp_server(name="dhcp-vlan100")
  ```

## `mikrotik_create_dhcp_network`
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

## `mikrotik_create_dhcp_pool`
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

## `mikrotik_remove_dhcp_server`
Removes a DHCP server from MikroTik device.
- Parameters:
  - `name` (required): DHCP server name
- Example:
  ```
  mikrotik_remove_dhcp_server(name="dhcp-vlan100")
  ```
