"""Tests for data models."""

import pytest
from datetime import datetime, UTC
from agentflow.models import (
    APIKey,
    User,
    Organization,
    Project,
    Database,
    generate_uuid,
    now_utc,
)


class TestGenerateUUID:
    """Tests for generate_uuid function."""

    def test_generate_uuid_returns_string(self):
        """Test that generate_uuid returns a string."""
        result = generate_uuid()
        assert isinstance(result, str)

    def test_generate_uuid_returns_unique_values(self):
        """Test that generate_uuid returns unique values."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generate_uuid_returns_valid_uuid_format(self):
        """Test that generate_uuid returns valid UUID format."""
        result = generate_uuid()
        # UUID format: 8-4-4-4-12 hexadecimal digits
        import re

        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(result) is not None


class TestNowUTC:
    """Tests for now_utc function."""

    def test_now_utc_returns_datetime(self):
        """Test that now_utc returns a datetime object."""
        result = now_utc()
        assert isinstance(result, datetime)

    def test_now_utc_returns_recent_time(self):
        """Test that now_utc returns a recent datetime."""
        from datetime import timedelta

        result = now_utc()
        assert (datetime.now(UTC) - result) < timedelta(seconds=1)


class TestAPIKey:
    """Tests for APIKey model."""

    def test_create_api_key_with_defaults(self):
        """Test creating APIKey with default values."""
        api_key = APIKey(key="test_key", name="Test Key")

        assert api_key.id is not None
        assert len(api_key.id) > 0
        assert api_key.key == "test_key"
        assert api_key.name == "Test Key"
        assert api_key.is_active is True
        assert api_key.last_used_at is None
        assert isinstance(api_key.created_at, datetime)

    def test_create_api_key_with_all_fields(self):
        """Test creating APIKey with all fields specified."""
        test_time = now_utc()
        api_key = APIKey(
            id="custom-id",
            key="test_key",
            name="Test Key",
            created_at=test_time,
            last_used_at=test_time,
            is_active=False,
        )

        assert api_key.id == "custom-id"
        assert api_key.key == "test_key"
        assert api_key.name == "Test Key"
        assert api_key.created_at == test_time
        assert api_key.last_used_at == test_time
        assert api_key.is_active is False


class TestUser:
    """Tests for User model."""

    def test_create_user_with_defaults(self):
        """Test creating User with default values."""
        user = User(email="test@example.com", password_hash="hash", name="Test User")

        assert user.id is not None
        assert len(user.id) > 0
        assert user.email == "test@example.com"
        assert user.password_hash == "hash"
        assert user.name == "Test User"
        assert user.api_keys == []
        assert isinstance(user.created_at, datetime)

    def test_create_user_with_api_keys(self):
        """Test creating User with API keys."""
        api_key = APIKey(key="test_key", name="Test Key")
        user = User(
            email="test@example.com",
            password_hash="hash",
            name="Test User",
            api_keys=[api_key],
        )

        assert len(user.api_keys) == 1
        assert user.api_keys[0].key == "test_key"

    def test_user_email_validation(self):
        """Test that User model validates email format."""
        with pytest.raises(ValueError):
            User(email="invalid-email", password_hash="hash", name="Test")


class TestOrganization:
    """Tests for Organization model."""

    def test_create_organization_with_defaults(self):
        """Test creating Organization with default values."""
        org = Organization(owner_id="user-1", name="Test Org", slug="test-org")

        assert org.id is not None
        assert org.owner_id == "user-1"
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.description is None
        assert isinstance(org.created_at, datetime)

    def test_create_organization_with_description(self):
        """Test creating Organization with description."""
        org = Organization(
            owner_id="user-1",
            name="Test Org",
            slug="test-org",
            description="A test organization",
        )

        assert org.description == "A test organization"


class TestProject:
    """Tests for Project model."""

    def test_create_project_with_defaults(self):
        """Test creating Project with default values."""
        project = Project(
            organization_id="org-1", name="Test Project", slug="test-project"
        )

        assert project.id is not None
        assert project.organization_id == "org-1"
        assert project.name == "Test Project"
        assert project.slug == "test-project"
        assert project.description is None
        assert project.github_url is None
        assert project.is_active is True
        assert isinstance(project.created_at, datetime)

    def test_create_project_with_all_fields(self):
        """Test creating Project with all fields specified."""
        project = Project(
            organization_id="org-1",
            name="Test Project",
            slug="test-project",
            description="A test project",
            github_url="https://github.com/test/repo",
            is_active=False,
        )

        assert project.description == "A test project"
        assert project.github_url == "https://github.com/test/repo"
        assert project.is_active is False

    def test_project_github_url_accepts_any_string(self):
        """Test that Project model accepts any string for github_url."""
        # Pydantic HttpUrl accepts valid URLs
        project = Project(
            organization_id="org-1",
            name="Test Project",
            slug="test-project",
            github_url="https://github.com/test/repo",
        )
        assert project.github_url == "https://github.com/test/repo"


class TestDatabase:
    """Tests for Database model."""

    def test_create_empty_database(self):
        """Test creating empty Database."""
        db = Database()

        assert db.users == []
        assert db.organizations == []
        assert db.projects == []

    def test_create_database_with_data(self):
        """Test creating Database with initial data."""
        user = User(email="test@example.com", password_hash="hash", name="Test")
        org = Organization(owner_id="user-1", name="Org", slug="org")
        project = Project(organization_id="org-1", name="Project", slug="project")

        db = Database(users=[user], organizations=[org], projects=[project])

        assert len(db.users) == 1
        assert len(db.organizations) == 1
        assert len(db.projects) == 1
        assert db.users[0].email == "test@example.com"
        assert db.organizations[0].name == "Org"
        assert db.projects[0].name == "Project"

    def test_database_serialization(self):
        """Test that Database can be serialized to JSON."""
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db = Database(users=[user])

        # Should not raise an exception
        json_data = db.model_dump_json()
        assert isinstance(json_data, str)

        # Should be able to deserialize
        db_restored = Database.model_validate_json(json_data)
        assert len(db_restored.users) == 1
        assert db_restored.users[0].email == "test@example.com"
