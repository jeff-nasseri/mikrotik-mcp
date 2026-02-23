# WireGuard Management

Tools for managing WireGuard VPN interfaces and peers on MikroTik devices (RouterOS v7+).

---

## Interface Management

### `mikrotik_create_wireguard_interface`
Creates a WireGuard interface on MikroTik device.
- Parameters:
  - `name` (required): Interface name (e.g. "wg0")
  - `listen_port` (optional): UDP port to listen on (default: 13231)
  - `private_key` (optional): Base64-encoded private key. RouterOS auto-generates one if omitted.
  - `mtu` (optional): MTU size (default: 1420)
  - `comment` (optional): Description
  - `disabled` (optional): Disable after creation (default: false)
- Example:
  ```
  mikrotik_create_wireguard_interface(name="wg0", listen_port=13231)
  ```

---

### `mikrotik_list_wireguard_interfaces`
Lists WireGuard interfaces on MikroTik device.
- Parameters:
  - `name_filter` (optional): Filter by interface name (partial match)
  - `disabled_only` (optional): Show only disabled interfaces
  - `running_only` (optional): Show only running interfaces
- Example:
  ```
  mikrotik_list_wireguard_interfaces()
  ```

---

### `mikrotik_get_wireguard_interface`
Gets detailed information about a specific WireGuard interface, including the public key.
- Parameters:
  - `name` (required): Interface name
- Example:
  ```
  mikrotik_get_wireguard_interface(name="wg0")
  ```

---

### `mikrotik_update_wireguard_interface`
Updates an existing WireGuard interface on MikroTik device.
- Parameters:
  - `name` (required): Current interface name
  - `new_name` (optional): New name for the interface
  - `listen_port` (optional): New UDP listen port
  - `private_key` (optional): New Base64-encoded private key
  - `mtu` (optional): New MTU size
  - `comment` (optional): New description
  - `disabled` (optional): Enable (false) or disable (true) the interface
- Example:
  ```
  mikrotik_update_wireguard_interface(name="wg0", listen_port=51820, mtu=1280)
  ```

---

### `mikrotik_remove_wireguard_interface`
Removes a WireGuard interface from MikroTik device. All peers belonging to the interface are removed as well.
- Parameters:
  - `name` (required): Interface name to remove
- Example:
  ```
  mikrotik_remove_wireguard_interface(name="wg0")
  ```

---

### `mikrotik_enable_wireguard_interface`
Enables a disabled WireGuard interface.
- Parameters:
  - `name` (required): Interface name
- Example:
  ```
  mikrotik_enable_wireguard_interface(name="wg0")
  ```

---

### `mikrotik_disable_wireguard_interface`
Disables a WireGuard interface without removing it.
- Parameters:
  - `name` (required): Interface name
- Example:
  ```
  mikrotik_disable_wireguard_interface(name="wg0")
  ```

---

## Peer Management

### `mikrotik_add_wireguard_peer`
Adds a WireGuard peer to an interface on MikroTik device.
- Parameters:
  - `interface` (required): WireGuard interface the peer belongs to
  - `public_key` (required): Base64-encoded public key of the remote peer
  - `allowed_address` (required): Comma-separated allowed IP addresses/subnets (e.g. `"10.0.0.2/32"`)
  - `endpoint_address` (optional): Remote peer IP address or hostname
  - `endpoint_port` (optional): Remote peer UDP port
  - `preshared_key` (optional): Base64-encoded preshared key for extra security
  - `persistent_keepalive` (optional): Keepalive interval (e.g. `"25s"`)
  - `comment` (optional): Description
  - `disabled` (optional): Disable after creation (default: false)
- Example:
  ```
  mikrotik_add_wireguard_peer(
      interface="wg0",
      public_key="base64pubkey==",
      allowed_address="10.0.0.2/32",
      endpoint_address="203.0.113.10",
      endpoint_port=13231,
      persistent_keepalive="25s"
  )
  ```

---

### `mikrotik_list_wireguard_peers`
Lists WireGuard peers on MikroTik device.
- Parameters:
  - `interface_filter` (optional): Filter by WireGuard interface name
  - `disabled_only` (optional): Show only disabled peers
- Example:
  ```
  mikrotik_list_wireguard_peers(interface_filter="wg0")
  ```

---

### `mikrotik_get_wireguard_peer`
Gets detailed information about a specific WireGuard peer.
- Parameters:
  - `peer_id` (required): Peer ID (e.g. `"*1"` from list output)
- Example:
  ```
  mikrotik_get_wireguard_peer(peer_id="*1")
  ```

---

### `mikrotik_update_wireguard_peer`
Updates an existing WireGuard peer on MikroTik device.
- Parameters:
  - `peer_id` (required): Peer ID (e.g. `"*1"`)
  - `allowed_address` (optional): New comma-separated allowed IP addresses/subnets
  - `endpoint_address` (optional): New remote peer address (pass `""` to remove)
  - `endpoint_port` (optional): New remote peer UDP port
  - `preshared_key` (optional): New preshared key (pass `""` to remove)
  - `persistent_keepalive` (optional): New keepalive interval (`"0s"` to disable)
  - `comment` (optional): New description
  - `disabled` (optional): Enable (false) or disable (true) the peer
- Example:
  ```
  mikrotik_update_wireguard_peer(peer_id="*1", persistent_keepalive="25s", comment="laptop")
  ```

---

### `mikrotik_remove_wireguard_peer`
Removes a WireGuard peer from MikroTik device.
- Parameters:
  - `peer_id` (required): Peer ID (e.g. `"*1"`)
- Example:
  ```
  mikrotik_remove_wireguard_peer(peer_id="*1")
  ```

---

### `mikrotik_enable_wireguard_peer`
Enables a disabled WireGuard peer.
- Parameters:
  - `peer_id` (required): Peer ID (e.g. `"*1"`)
- Example:
  ```
  mikrotik_enable_wireguard_peer(peer_id="*1")
  ```

---

### `mikrotik_disable_wireguard_peer`
Disables a WireGuard peer without removing it.
- Parameters:
  - `peer_id` (required): Peer ID (e.g. `"*1"`)
- Example:
  ```
  mikrotik_disable_wireguard_peer(peer_id="*1")
  ```
