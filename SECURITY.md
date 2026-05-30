# Security Policy

## Overview

MikroTik MCP provides programmatic access to MikroTik RouterOS devices through SSH connections. Given the sensitive nature of network infrastructure management, security is a critical concern. This document outlines our security policy and provides guidance on reporting security vulnerabilities.


## Reporting a Vulnerability

If you discover a security vulnerability in MikroTik MCP, please report it by:

**Creating a security issue at:** https://github.com/jeff-nasseri/mikrotik-mcp/issues

When reporting a security issue, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: Potential impact if exploited
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Suggested Fix**: If you have suggestions for fixing the issue (optional)
- **Environment Details**: OS, Python version, and relevant configuration details

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the severity and impact of the reported vulnerability
- **Resolution**: We will work on a fix and release it as soon as possible
- **Credit**: We will credit you in the release notes (unless you prefer to remain anonymous)

## Security Considerations

### 1. SSH Connection Security

MikroTik MCP uses SSH to connect to RouterOS devices. Be aware of the following:

- **Host Key Verification**: The current implementation uses `AutoAddPolicy()` which automatically accepts unknown host keys. This may expose you to man-in-the-middle attacks. Consider implementing stricter host key verification for production environments.

- **Credential Storage**: SSH credentials (passwords and private keys) must be properly secured:
  - Avoid storing passwords in plain text configuration files
  - Use environment variables for sensitive credentials
  - Restrict file permissions on configuration files containing credentials
  - Consider using SSH key-based authentication instead of passwords
  - Use SSH keys with passphrases for additional security

### 2. Command Injection Risks

- The server executes SSH commands on MikroTik devices based on tool inputs
- Always validate and sanitize inputs before passing them to MikroTik commands
- Avoid constructing commands using unsanitized user input
- Be cautious when using this server in environments where untrusted users have access

### 3. Access Control

- **MCP Server Access**: Ensure that access to the MCP server is restricted to authorized users only
- **Network Segmentation**: Run the MCP server in a secure network segment
- **Authentication**: When exposing the MCP server via MCPO or other REST APIs, always use strong authentication (API keys, OAuth, etc.)
- **Firewall Rules**: Implement appropriate firewall rules to restrict access to both the MCP server and MikroTik devices

### 4. Logging and Auditing

- Commands executed on MikroTik devices are logged
- Be aware that logs may contain sensitive information
- Secure log files with appropriate permissions
- Regularly review logs for suspicious activity
- Consider implementing log rotation and secure log storage

### 5. Router Configuration Changes

- This tool provides direct access to router configuration
- Changes can impact network availability and security
- Always test configuration changes in a non-production environment first
- Maintain regular backups before making significant changes
- Implement change management procedures for production environments

### 6. Backup File Security

- Backup files may contain sensitive information including:
  - Network configurations
  - Firewall rules
  - User credentials (if included)
  - VPN configurations
- Store backup files securely with encryption
- Restrict access to backup files
- Use secure channels for backup file transfers

### 7. Wireless Security

- When managing wireless configurations:
  - Use strong encryption (WPA2 or WPA3)
  - Avoid using weak pre-shared keys
  - Regularly rotate wireless passwords
  - Implement proper access control lists
  - Disable WPS if not needed

### 8. Docker Security

> ⚠️ **Environment variables are exposed by `docker inspect`.** Any value passed
> to a container as an environment variable — whether via `-e VAR=value`,
> `-e VAR` (inherited from the host shell), or `--env-file` — is stored in the
> container's configuration and shown in full by `docker inspect`. Reading a
> file into a variable (`export VAR=$(cat secret.txt)`) does **not** help: the
> resolved value still ends up in the container's environment.

To keep credentials out of `docker inspect`, prefer (in order):

1. **SSH key-based authentication** (`MIKROTIK_KEY_FILENAME` / `--key-filename`) —
   no password is stored in the environment at all. This is the recommended
   approach and is natively supported.
2. **Docker / Swarm secrets** — mounted as files under `/run/secrets/`, never
   placed in the environment. (Requires an entrypoint that reads the file into
   the process environment at startup, which keeps it out of `docker inspect`.)
3. **Runtime fetch from a secrets manager** (HashiCorp Vault, AWS Secrets
   Manager, etc.) performed inside the container, rather than injecting the
   secret at `docker run` time.

Additional hardening:

- Don't pass credentials as literal command-line arguments (also visible in
  `docker ps` and shell history)
- Run containers with minimal privileges
- Keep Docker images updated and use specific version tags instead of `latest`
- Scan images for vulnerabilities regularly

### 9. API Exposure

When exposing MikroTik MCP via REST API (using MCPO):

- Always enable API key authentication
- Use HTTPS/TLS for API endpoints
- Implement rate limiting to prevent abuse
- Monitor API usage for suspicious patterns
- Use strong, randomly generated API keys
- Rotate API keys regularly

## Security Best Practices

### For Developers

1. **Input Validation**: Always validate and sanitize inputs
2. **Error Handling**: Don't expose sensitive information in error messages
3. **Dependencies**: Keep all dependencies updated
4. **Code Review**: Review security-critical code changes carefully
5. **Testing**: Include security testing in your test suite

### For Users

1. **Principle of Least Privilege**: Create MikroTik users with minimum required permissions
2. **Network Security**:
   - Use VPNs or secure channels for remote access
   - Implement network segmentation
   - Enable firewall rules on MikroTik devices
3. **Monitoring**:
   - Monitor MikroTik logs for unauthorized access
   - Set up alerts for configuration changes
   - Review audit logs regularly
4. **Updates**:
   - Keep MikroTik MCP updated
   - Keep MikroTik RouterOS updated
   - Update Python and system packages regularly
5. **Backup Strategy**:
   - Maintain regular encrypted backups
   - Test backup restoration procedures
   - Store backups in secure, off-site locations

## Known Security Considerations

### Current Implementation Notes

1. **SSH Host Key Verification**: Uses `AutoAddPolicy()` which automatically accepts unknown host keys. This is convenient but less secure than strict host key checking.

2. **Password Logging**: Passwords are not logged, but be cautious with debug logging that might expose sensitive command parameters.

3. **Command Execution**: Direct command execution on RouterOS requires careful input validation at the application level.

## Secure Configuration Example

Passing the password as an environment variable — in **any** form — leaves it
visible in `docker inspect`. The configuration below instead uses **SSH
key-based authentication**, so no secret is stored in the container's
environment:

```json
{
  "mcpServers": {
    "mikrotik-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "MIKROTIK_HOST=192.168.88.1",
        "-e", "MIKROTIK_USERNAME=mcp_user",
        "-e", "MIKROTIK_KEY_FILENAME=/keys/id_ed25519",
        "-v", "/secure/path/keys:/keys:ro",
        "mikrotik-mcp"
      ]
    }
  }
}
```

> ❌ **Not safe from `docker inspect`:** the example below is a common but
> mistaken pattern. `export MIKROTIK_PASSWORD=$(cat ...)` followed by
> `docker run -e MIKROTIK_PASSWORD` still copies the resolved password into the
> container's environment, where `docker inspect` reveals it:
>
> ```bash
> # DON'T rely on this for secrecy — the value still shows in `docker inspect`:
> export MIKROTIK_PASSWORD=$(cat /secure/path/password.txt)
> docker run -e MIKROTIK_PASSWORD ... mikrotik-mcp
> ```

If you must use a password instead of an SSH key, supply it via Docker secrets
(mounted as a file under `/run/secrets/`) with an entrypoint that loads it into
the process environment at startup — that keeps it out of `docker inspect`.

## Compliance and Standards

This project aims to align with:

- **OWASP Top 10**: Addressing common web application security risks
- **CIS Controls**: Following Center for Internet Security best practices
- **Principle of Least Privilege**: Encouraging minimal permission configurations

## Additional Resources

- [MikroTik Security Practices](https://wiki.mikrotik.com/wiki/Manual:Securing_Your_Router)
- [SSH Key-Based Authentication](https://help.mikrotik.com/docs/display/ROS/SSH)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

## Contact

For security-related questions or concerns, please open an issue at:
https://github.com/jeff-nasseri/mikrotik-mcp/issues

---

**Remember**: Security is a shared responsibility. While we work to make MikroTik MCP as secure as possible, proper deployment, configuration, and usage are equally important.
