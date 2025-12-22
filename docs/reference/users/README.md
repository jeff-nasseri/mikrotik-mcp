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

