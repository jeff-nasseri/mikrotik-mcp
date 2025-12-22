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

