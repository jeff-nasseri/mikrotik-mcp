import io
import logging
from typing import Optional

import paramiko

logger = logging.getLogger(__name__)

class MikroTikSSHClient:
    """SSH client for MikroTik devices."""

    def __init__(self, host: str, username: str, password: str, key_filename: Optional[str], port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        self.channel = None
        self.key_filename = key_filename

    @staticmethod
    def _decode_output(data: bytes) -> str:
        """Decode raw SSH output bytes with a multi-encoding fallback chain.

        RouterOS devices may return output encoded in UTF-8, CP1252 (Windows
        Western European), or ISO 8859-1 (Latin-1) depending on the locale
        configured on the device.  Strict UTF-8 decoding raises
        UnicodeDecodeError for characters such as Swedish å/ä/ö (issue #58).

        Fallback order:
          1. UTF-8       — covers ASCII and most modern configurations
          2. CP1252      — covers Windows Western European characters (å ä ö …)
          3. Latin-1     — always succeeds; covers all single-byte code points
        """
        if not data:
            return ""
        for encoding in ("utf-8", "cp1252", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        # Unreachable in practice (latin-1 never raises), but kept as a
        # safety net: replace unrecognised bytes rather than crashing.
        return data.decode("utf-8", errors="replace")

    def connect(self):
        """Establish SSH connection to MikroTik device."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MikroTik: {e}")
            return False

    def execute_command(self, command: str) -> str:
        """Execute a command on MikroTik device using exec_command."""
        if not self.client:
            raise Exception("Not connected to MikroTik device")

        try:
            stdin, stdout, stderr = self.client.exec_command(command)

            output = self._decode_output(stdout.read())
            error = self._decode_output(stderr.read())

            if error and not output:
                return error

            return output
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise

    def download_file(self, remote_filename: str) -> bytes:
        """Download a file from the device over SFTP and return its raw bytes.

        RouterOS exposes its file store over the SSH/SFTP subsystem, so binary
        backups and text exports alike can be transferred without mangling.
        """
        if not self.client:
            raise Exception("Not connected to MikroTik device")

        sftp = self.client.open_sftp()
        try:
            buffer = io.BytesIO()
            sftp.getfo(remote_filename, buffer)
            return buffer.getvalue()
        finally:
            sftp.close()

    def upload_file(self, remote_filename: str, data: bytes) -> None:
        """Upload raw bytes to a file on the device over SFTP."""
        if not self.client:
            raise Exception("Not connected to MikroTik device")

        sftp = self.client.open_sftp()
        try:
            sftp.putfo(io.BytesIO(data), remote_filename)
        finally:
            sftp.close()

    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
