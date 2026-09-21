import pytest

from mcp_mikrotik.sensitive import REDACTED, redact_sensitive_data, redact_sensitive_text


@pytest.mark.parametrize(("value", "expected"), [
    ('password="hunter2"', 'password="***"'),
    ("security.passphrase='correct horse'", "security.passphrase='***'"),
    ("private-key=base64value==", "private-key=***"),
    ("PrivateKey = base64value==", "PrivateKey = ***"),
    ('{"token": "abc123"}', '{"token": "***"}'),
    ("community: monitoring", "community: ***"),
    ("wpa2-pre-shared-key=wifi-secret", "wpa2-pre-shared-key=***"),
    ("authentication-password=radius-secret", "authentication-password=***"),
    ("public-key=visible", "public-key=visible"),
    ("password-file=no", "password-file=no"),
    ("include_password=false", "include_password=false"),
])
def test_redact_sensitive_text(value, expected):
    assert redact_sensitive_text(value) == expected


def test_redact_private_key_block():
    value = "before\n-----BEGIN OPENSSH PRIVATE KEY-----\nsecret\n-----END OPENSSH PRIVATE KEY-----\nafter"
    assert redact_sensitive_text(value) == f"before\n{REDACTED}\nafter"


def test_redact_sensitive_text_replaces_supplied_secret():
    assert redact_sensitive_text("RouterOS echoed hunter2", ["hunter2"]) == "RouterOS echoed ***"
    assert redact_sensitive_text("RouterOS echoed p", ["p"]) == "RouterOS echoed ***"
    assert redact_sensitive_text("Operation completed", ["p"]) == "Operation completed"


def test_redact_sensitive_data_handles_notification_structures():
    value = {"messages": ["password=one", "public-key=two"], "private_key": "three"}
    assert redact_sensitive_data(value) == {
        "messages": ["password=***", "public-key=two"],
        "private_key": "***",
    }
