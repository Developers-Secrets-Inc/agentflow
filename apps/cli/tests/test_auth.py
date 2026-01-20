"""Tests for auth commands."""

import pytest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from agentflow.commands.auth import app, hash_password, generate_api_key

runner = CliRunner()


@pytest.fixture
def temp_data_dir(tmp_path: Path):
    """Create temporary data directory for testing."""

    def mock_data_dir():
        return tmp_path / ".agentflow"

    with patch("agentflow.storage.DATA_DIR", mock_data_dir()):
        with patch("agentflow.storage.DATA_FILE", mock_data_dir() / "data.json"):
            yield


@pytest.fixture
def temp_config_dir(tmp_path: Path):
    """Create temporary config directory for testing."""

    def mock_config_dir():
        return tmp_path / ".agentflow"

    with patch("agentflow.utils.config.CONFIG_DIR", mock_config_dir()):
        with patch("agentflow.utils.config.CONFIG_FILE", mock_config_dir() / "config.yaml"):
            yield


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hashes_password(self):
        """Test that hash_password returns a hash."""
        result = hash_password("password123")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 produces 64 hex characters

    def test_same_password_same_hash(self):
        """Test that same password produces same hash."""
        hash1 = hash_password("password123")
        hash2 = hash_password("password123")
        assert hash1 == hash2

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("password123")
        hash2 = hash_password("password456")
        assert hash1 != hash2


class TestGenerateAPIKey:
    """Tests for generate_api_key function."""

    def test_generates_key_with_prefix(self):
        """Test that API key starts with 'afk_'."""
        key = generate_api_key()
        assert key.startswith("afk_")

    def test_generates_unique_keys(self):
        """Test that each generated key is unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        assert key1 != key2

    def test_key_length(self):
        """Test that API key has expected length."""
        key = generate_api_key()
        # 'afk_' + 43 characters (token_urlsafe(32) produces 43 chars)
        assert len(key) == 4 + 43


class TestAuthRegister:
    """Tests for auth register command."""

    def test_registers_new_user(self, temp_data_dir, temp_config_dir):
        """Test registering a new user."""
        result = runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        assert result.exit_code == 0
        assert "User registered successfully" in result.stdout
        assert "test@example.com" in result.stdout
        assert "afk_" in result.stdout

        # Verify user was created
        from agentflow.storage import find_user_by_email

        user = find_user_by_email("test@example.com")
        assert user is not None
        assert user.name == "Test User"

    def test_rejects_duplicate_email(self, temp_data_dir, temp_config_dir):
        """Test that duplicate email is rejected."""
        # Register first user
        runner.invoke(
            app,
            [
                "register",
                "--email",
                "test@example.com",
                "--password",
                "password123",
                "--name",
                "User 1",
            ],
        )

        # Try to register with same email
        result = runner.invoke(
            app,
            [
                "register",
                "--email",
                "test@example.com",
                "--password",
                "password456",
                "--name",
                "User 2",
            ],
        )

        assert result.exit_code == 1
        assert "User already exists" in result.stdout

    def test_rejects_short_password(self, temp_data_dir, temp_config_dir):
        """Test that short password is rejected."""
        result = runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "pass", "--name", "Test User"],
        )

        assert result.exit_code == 1
        assert "8 characters" in result.stdout

    def test_rejects_long_name(self, temp_data_dir, temp_config_dir):
        """Test that name over 255 characters is rejected."""
        long_name = "A" * 256
        result = runner.invoke(
            app,
            [
                "register",
                "--email",
                "test@example.com",
                "--password",
                "password123",
                "--name",
                long_name,
            ],
        )

        assert result.exit_code == 1
        assert "255 characters" in result.stdout


class TestAuthLogin:
    """Tests for auth login command."""

    def test_login_success(self, temp_data_dir, temp_config_dir):
        """Test successful login."""
        # Register user first
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Login
        result = runner.invoke(
            app, ["login", "--email", "test@example.com", "--password", "password123"]
        )

        assert result.exit_code == 0
        assert "Logged in successfully" in result.stdout
        assert "test@example.com" in result.stdout

    def test_login_invalid_email(self, temp_data_dir, temp_config_dir):
        """Test login with non-existent email."""
        result = runner.invoke(
            app, ["login", "--email", "nonexistent@example.com", "--password", "password123"]
        )

        assert result.exit_code == 1
        assert "Invalid credentials" in result.stdout

    def test_login_invalid_password(self, temp_data_dir, temp_config_dir):
        """Test login with wrong password."""
        # Register user first
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Try login with wrong password
        result = runner.invoke(
            app, ["login", "--email", "test@example.com", "--password", "wrongpassword"]
        )

        assert result.exit_code == 1
        assert "Invalid credentials" in result.stdout


class TestAuthStatus:
    """Tests for auth status command."""

    def test_status_when_not_authenticated(self, temp_data_dir, temp_config_dir):
        """Test status command when not logged in."""
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Not authenticated" in result.stdout

    def test_status_when_authenticated(self, temp_data_dir, temp_config_dir):
        """Test status command when logged in."""
        # Register and login
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Check status
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Authenticated" in result.stdout
        assert "test@example.com" in result.stdout
        assert "Test User" in result.stdout


class TestAPIKeysList:
    """Tests for api-keys list command."""

    def test_list_keys(self, temp_data_dir, temp_config_dir):
        """Test listing API keys."""
        # Register user (creates default key)
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # List keys
        result = runner.invoke(app, ["api-keys", "list"])

        assert result.exit_code == 0
        assert "Default Key" in result.stdout
        assert "NAME" in result.stdout  # Table header

    def test_list_keys_when_not_authenticated(self, temp_data_dir, temp_config_dir):
        """Test listing keys when not authenticated."""
        result = runner.invoke(app, ["api-keys", "list"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.stdout


class TestAPIKeysCreate:
    """Tests for api-keys create command."""

    def test_create_new_key(self, temp_data_dir, temp_config_dir):
        """Test creating a new API key."""
        # Register user first
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Create new key
        result = runner.invoke(app, ["api-keys", "create", "--name", "Test Key"])

        assert result.exit_code == 0
        assert "API key created" in result.stdout
        assert "Test Key" in result.stdout
        assert "afk_" in result.stdout

    def test_create_key_without_name(self, temp_data_dir, temp_config_dir):
        """Test creating key without name parameter."""
        # Register user first
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Try create without name
        result = runner.invoke(app, ["api-keys", "create"])

        assert result.exit_code == 1
        assert "required" in result.stdout.lower()

    def test_create_key_when_not_authenticated(self, temp_data_dir, temp_config_dir):
        """Test creating key when not authenticated."""
        result = runner.invoke(app, ["api-keys", "create", "--name", "Test Key"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.stdout

    def test_create_key_with_long_name(self, temp_data_dir, temp_config_dir):
        """Test creating key with name > 255 characters."""
        # Register user first
        runner.invoke(
            app,
            ["register", "--email", "test@example.com", "--password", "password123", "--name", "Test User"],
        )

        # Try with long name
        long_name = "A" * 256
        result = runner.invoke(app, ["api-keys", "create", "--name", long_name])

        assert result.exit_code == 1
        assert "255 characters" in result.stdout
