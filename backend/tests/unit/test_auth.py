"""Tests for authentication utilities."""

from app.auth import decode_token, create_token

class TestDecodeToken:
    def test_decode_token_success(self):
        token = create_token({"sub": "test_user"})
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test_user"

    def test_decode_token_expired(self):
        token = create_token({"sub": "test_user"}, expires_minutes=-1)
        decoded = decode_token(token)
        assert decoded is None

    def test_decode_token_invalid_signature(self):
        token = create_token({"sub": "test_user"})
        # Modify the signature to make it invalid (since token is base64 encoded parts split by .)
        parts = token.split(".")
        invalid_token = f"{parts[0]}.{parts[1]}.invalid_signature"

        decoded = decode_token(invalid_token)
        assert decoded is None

    def test_decode_token_malformed(self):
        invalid_token = "not.a.valid.jwt.token"
        decoded = decode_token(invalid_token)
        assert decoded is None
