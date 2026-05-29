import pytest
from app.models.user import User

class TestUserModel:
    """Tests for the User model password hashing and verification."""

    def test_set_password_and_check_correct(self):
        """Happy path: password can be set and verified correctly."""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("SecureP@ssw0rd")
        assert user.check_password("SecureP@ssw0rd") is True

    def test_check_password_incorrect(self):
        """Edge case: incorrect password returns False."""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("SecureP@ssw0rd")
        assert user.check_password("WrongPassword") is False

    def test_password_is_hashed_not_plaintext(self):
        """Security: password_hash must not store the raw password."""
        user = User(username="testuser", email="test@example.com", role="employee")
        raw = "Secret123"
        user.set_password(raw)
        assert user.password_hash != raw
        # Basic hash format check (Werkzeug uses method$salt$hash)
        assert "pbkdf2" in user.password_hash or "scrypt" in user.password_hash

    def test_set_password_empty_string(self):
        """Edge case: setting an empty password should still work (hash is generated)."""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("")
        assert user.password_hash != ""
        # Even with empty string, check_password should return True
        assert user.check_password("") is True

    def test_check_password_with_none_raises(self):
        """Error path: passing None to check_password should raise TypeError."""
        user = User(username="testuser", email="test@example.com", role="employee")
        user.set_password("SomePass")
        with pytest.raises(TypeError):
            user.check_password(None)