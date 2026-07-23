import pytest

from ghost_browser.security.vault_logic import VaultSecurity


def test_current_key_round_trip() -> None:
    key_hex = VaultSecurity.derive_key(
        "Correct Horse Battery Staple!9",
        b"0123456789abcdef0123456789abcdef",
    ).hex()

    token = VaultSecurity.encrypt_data("sensitive payload", key_hex)

    assert VaultSecurity.decrypt_data(token, key_hex) == "sensitive payload"


def test_wrong_key_is_rejected() -> None:
    salt = b"0123456789abcdef0123456789abcdef"
    key_one = VaultSecurity.derive_key("Correct Horse Battery Staple!9", salt).hex()
    key_two = VaultSecurity.derive_key("Different Password Value!8", salt).hex()
    token = VaultSecurity.encrypt_data("sensitive payload", key_one)

    with pytest.raises(ValueError, match="authentication failed"):
        VaultSecurity.decrypt_data(token, key_two)


def test_legacy_key_is_distinct_from_current_key() -> None:
    password = "Correct Horse Battery Staple!9"
    current_key = VaultSecurity.derive_key(
        password,
        b"0123456789abcdef0123456789abcdef",
    )
    legacy_key = VaultSecurity.derive_legacy_key(password)

    assert current_key != legacy_key


def test_malformed_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="malformed"):
        VaultSecurity.encrypt_data("payload", "not-hex")
