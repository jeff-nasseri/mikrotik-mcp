import logging
import re
import threading
import time
from typing import Optional

from . import config
from .mikrotik_ssh_client import MikroTikSSHClient

logger = logging.getLogger(__name__)

# Matches MikroTik prompts in both normal and safe-mode:
#   [admin@MikroTik] >
#   [admin@MikroTik] <SAFE> >
_PROMPT_RE = re.compile(r'\[.+?@.+?\] (?:<SAFE> )?> ?$', re.MULTILINE)

# Strip ANSI/VT escape sequences that MikroTik emits on interactive shells
_ANSI_RE = re.compile(
    r'\x1b(?:'
    r'\[[0-9;]*[mABCDEFGHJKLMSTfhilmnprsu]'
    r'|[()][0-9A-Za-z]'
    r'|\[?\?[0-9]+[hl]'
    r'|\[\d*[ABCDEFGHJKLMST]'
    r')'
)


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub('', text)


class SafeModeManager:
    """
    Manages a persistent interactive SSH session for MikroTik Safe Mode.

    Safe Mode is activated by sending Ctrl+X (0x18) to the interactive shell.
    While active, any change is held in memory only — a reboot or session drop
    reverts all changes.  Sending Ctrl+X a second time commits the changes and
    exits Safe Mode.
    """

    def __init__(self) -> None:
        self._ssh: Optional[MikroTikSSHClient] = None
        self._channel = None
        self._active = False
        self._lock = threading.Lock()

    @property
    def is_active(self) -> bool:
        return self._active

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enable(self) -> str:
        """Open a persistent SSH shell and activate MikroTik Safe Mode."""
        with self._lock:
            if self._active:
                return "Safe mode is already active."

            ssh = MikroTikSSHClient(
                host=config.mikrotik_config.host,
                username=config.mikrotik_config.username,
                password=config.mikrotik_config.password,
                key_filename=config.mikrotik_config.key_filename,
                port=config.mikrotik_config.port,
            )
            if not ssh.connect():
                return "Error: Failed to connect to MikroTik device for safe mode session."

            channel = ssh.client.invoke_shell(term='dumb', width=220, height=50)
            channel.settimeout(1.0)
            self._ssh = ssh
            self._channel = channel

            # Wait for the initial shell prompt
            initial = self._read_until_prompt(timeout=20)
            if not _PROMPT_RE.search(initial):
                self._cleanup()
                return (
                    f"Error: Timed out waiting for MikroTik shell prompt. "
                    f"Got: {repr(initial[:300])}"
                )

            # Ctrl+X activates safe mode
            channel.send('\x18')
            response = self._read_until_prompt(timeout=10)

            if '<SAFE>' not in response:
                self._cleanup()
                return (
                    f"Error: Safe mode did not activate. "
                    f"Response: {repr(response[:300])}"
                )

            self._active = True
            return (
                "Safe mode ENABLED. All changes are temporary — they will be "
                "reverted automatically if the connection drops or you call "
                "rollback_safe_mode. Call commit_safe_mode to make changes permanent."
            )

    def execute(self, command: str) -> str:
        """Execute a command through the safe-mode persistent shell session."""
        if not self._active or not self._channel:
            raise RuntimeError("Safe mode session is not active.")

        with self._lock:
            self._channel.send(command + '\n')
            raw = self._read_until_prompt()
            return self._extract_output(raw, command)

    def commit(self) -> str:
        """Send Ctrl+X again to exit Safe Mode and persist all changes."""
        with self._lock:
            if not self._active:
                return "Safe mode is not active. Nothing to commit."

            self._channel.send('\x18')
            response = self._read_until_prompt(timeout=15)
            self._cleanup()

            # After exiting safe mode the prompt should no longer contain <SAFE>
            if '<SAFE>' not in response:
                return "Changes committed successfully. Safe mode DISABLED."
            return f"Commit attempted. Response: {response[:200]}"

    def rollback(self) -> str:
        """Close the session to trigger MikroTik's automatic safe-mode revert."""
        with self._lock:
            if not self._active:
                return "Safe mode is not active. Nothing to roll back."

            self._cleanup()
            return (
                "Safe mode session closed. MikroTik has reverted all "
                "uncommitted changes automatically."
            )

    def status(self) -> str:
        if self._active:
            return (
                "Safe mode is ACTIVE. Changes are pending — they are NOT yet "
                "persisted. Call commit_safe_mode to persist or "
                "rollback_safe_mode to revert."
            )
        return (
            "Safe mode is NOT active. Changes take effect and persist immediately."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_until_prompt(self, timeout: float = 15.0) -> str:
        """Read from the channel until a RouterOS prompt is detected."""
        buf = ""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if self._channel.recv_ready():
                    chunk = self._channel.recv(4096).decode('utf-8', errors='replace')
                    buf += chunk
                    cleaned = _strip_ansi(buf)
                    if _PROMPT_RE.search(cleaned):
                        return cleaned
            except Exception:
                break
            time.sleep(0.05)
        return _strip_ansi(buf)

    def _extract_output(self, raw: str, command: str) -> str:
        """Strip the echoed command and trailing prompt from shell output."""
        # Normalise line endings
        text = raw.replace('\r\n', '\n').replace('\r', '\n')
        lines = text.split('\n')

        result_lines: list[str] = []
        past_echo = False
        for line in lines:
            stripped = line.strip()
            if not past_echo:
                # The interactive shell echoes the command we sent
                if command.strip() in stripped:
                    past_echo = True
                continue
            # Stop at the next prompt
            if _PROMPT_RE.match(stripped):
                break
            result_lines.append(line)

        return '\n'.join(result_lines).strip()

    def _cleanup(self) -> None:
        self._active = False
        if self._channel:
            try:
                self._channel.close()
            except Exception:
                pass
            self._channel = None
        if self._ssh:
            try:
                self._ssh.disconnect()
            except Exception:
                pass
            self._ssh = None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_manager: Optional[SafeModeManager] = None
_manager_lock = threading.Lock()


def get_safe_mode_manager() -> SafeModeManager:
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = SafeModeManager()
    return _manager
