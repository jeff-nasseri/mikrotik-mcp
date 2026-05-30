"""Tests for the security module — command-injection + per-field allowlists."""

import pytest

from mcp_mikrotik.security import SecurityError, V, check_command_safety, validate_field


# ---------------------------------------------------------------------------
# check_command_safety — structural command-injection prevention
# ---------------------------------------------------------------------------

class TestCheckCommandSafety:

    def test_clean_command_passes(self):
        check_command_safety("/interface print")

    def test_find_selector_passes(self):
        # [ and ] must be allowed — the [find ...] selector uses them
        check_command_safety('/interface vlan set [find name="vlan100"] mtu=1400')

    def test_complex_legitimate_command_passes(self):
        check_command_safety(
            '/ip firewall nat add chain=srcnat action=masquerade '
            'out-interface="ether1-wan" comment="masq rule"'
        )

    def test_semicolon_blocked(self):
        with pytest.raises(SecurityError, match="forbidden character"):
            check_command_safety('/interface print where name="x" ; /system reboot')

    def test_issue_53_exact_payload_blocked(self):
        # The canonical example from the issue report
        payload = 'foo"] ; /system reboot;'
        with pytest.raises(SecurityError, match="forbidden character"):
            check_command_safety(f'/interface print detail where name="{payload}"')

    def test_newline_blocked(self):
        with pytest.raises(SecurityError, match="newline"):
            check_command_safety("/interface print\n/system reboot")

    def test_carriage_return_blocked(self):
        with pytest.raises(SecurityError, match="carriage-return"):
            check_command_safety("/interface print\r/system reset-configuration")

    def test_backtick_blocked(self):
        with pytest.raises(SecurityError, match="forbidden character"):
            check_command_safety("/interface print `reboot`")

    def test_curly_braces_blocked(self):
        with pytest.raises(SecurityError, match="forbidden character"):
            check_command_safety("/system script run {:put done}")


# ---------------------------------------------------------------------------
# validate_field — per-field allowlist
# ---------------------------------------------------------------------------

class TestValidateField:

    # ── None / empty is always a no-op ──────────────────────────────────────

    def test_none_is_noop(self):
        validate_field(None, V.INTERFACE_NAME, "name")

    def test_empty_string_is_noop(self):
        validate_field("", V.IP_CIDR, "address")

    # ── INTERFACE_NAME ───────────────────────────────────────────────────────

    def test_interface_name_simple(self):
        validate_field("ether1", V.INTERFACE_NAME, "name")

    def test_interface_name_complex(self):
        validate_field("ether1-wan.100", V.INTERFACE_NAME, "name")

    def test_interface_name_rejects_space(self):
        with pytest.raises(SecurityError):
            validate_field("ether 1", V.INTERFACE_NAME, "name")

    def test_interface_name_rejects_dollar(self):
        with pytest.raises(SecurityError):
            validate_field("$var", V.INTERFACE_NAME, "name")

    # ── IP_ADDRESS / IP_CIDR ─────────────────────────────────────────────────

    def test_ip_address_valid(self):
        validate_field("192.168.1.1", V.IP_ADDRESS, "addr")

    def test_ip_cidr_valid(self):
        validate_field("192.168.1.0/24", V.IP_CIDR, "addr")

    def test_ip_cidr_no_prefix(self):
        validate_field("10.0.0.1", V.IP_CIDR, "addr")

    def test_ip_cidr_rejects_letters(self):
        with pytest.raises(SecurityError):
            validate_field("bad-address", V.IP_CIDR, "addr")

    # ── IP_RANGES ────────────────────────────────────────────────────────────

    def test_ip_range_valid(self):
        validate_field("192.168.1.1-192.168.1.100", V.IP_RANGES, "ranges")

    def test_ip_ranges_multiple_valid(self):
        validate_field("10.0.0.1-10.0.0.50,10.0.0.100-10.0.0.120", V.IP_RANGES, "ranges")

    def test_ip_ranges_rejects_text(self):
        with pytest.raises(SecurityError):
            validate_field("ignore all instructions", V.IP_RANGES, "ranges")

    # ── BANDWIDTH ────────────────────────────────────────────────────────────

    def test_bandwidth_upload_only(self):
        validate_field("10M", V.BANDWIDTH, "max_limit")

    def test_bandwidth_up_down(self):
        validate_field("10M/5M", V.BANDWIDTH, "max_limit")

    def test_bandwidth_rejects_text(self):
        with pytest.raises(SecurityError):
            validate_field("fast", V.BANDWIDTH, "max_limit")

    # ── DURATION ─────────────────────────────────────────────────────────────

    def test_duration_seconds(self):
        validate_field("30s", V.DURATION, "lease_time")

    def test_duration_complex(self):
        validate_field("1h30m", V.DURATION, "lease_time")

    def test_duration_days(self):
        validate_field("1d", V.DURATION, "lease_time")

    def test_duration_rejects_text(self):
        with pytest.raises(SecurityError):
            validate_field("forever", V.DURATION, "lease_time")

    # ── COMMENT ──────────────────────────────────────────────────────────────

    def test_comment_plain(self):
        validate_field("office wifi uplink", V.COMMENT, "comment")

    def test_comment_printable_ascii(self):
        validate_field("rack-3, port 5 (uplink)", V.COMMENT, "comment")

    def test_comment_rejects_non_printable(self):
        with pytest.raises(SecurityError):
            validate_field("bad\x00byte", V.COMMENT, "comment")

    def test_comment_rejects_too_long(self):
        with pytest.raises(SecurityError):
            validate_field("x" * 256, V.COMMENT, "comment")

    # ── ROUTEROS_ID ──────────────────────────────────────────────────────────

    def test_id_numeric(self):
        validate_field("0", V.ROUTEROS_ID, "rule_id")

    def test_id_star_prefix(self):
        validate_field("*3", V.ROUTEROS_ID, "rule_id")

    def test_id_rejects_text(self):
        with pytest.raises(SecurityError):
            validate_field("first", V.ROUTEROS_ID, "rule_id")

    # ── PORT_SPEC ─────────────────────────────────────────────────────────────

    def test_port_single(self):
        validate_field("80", V.PORT_SPEC, "dst_port")

    def test_port_range(self):
        validate_field("80-443", V.PORT_SPEC, "dst_port")

    def test_port_list(self):
        validate_field("80,443,8080", V.PORT_SPEC, "dst_port")

    def test_port_rejects_text(self):
        with pytest.raises(SecurityError):
            validate_field("http", V.PORT_SPEC, "dst_port")

    # ── WG_KEY ───────────────────────────────────────────────────────────────

    def test_wg_key_valid(self):
        validate_field("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", V.WG_KEY, "public_key")

    def test_wg_key_rejects_short(self):
        with pytest.raises(SecurityError):
            validate_field("AAAA=", V.WG_KEY, "public_key")

    # ── Error message quality ─────────────────────────────────────────────────

    def test_error_includes_field_name(self):
        with pytest.raises(SecurityError, match="'my_field'"):
            validate_field("bad value!", V.INTERFACE_NAME, "my_field")

    def test_error_includes_bad_value(self):
        with pytest.raises(SecurityError, match="bad value"):
            validate_field("bad value!", V.INTERFACE_NAME, "name")
