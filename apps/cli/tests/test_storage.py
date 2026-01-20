"""Tests for storage layer."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from agentflow.storage import (
    ensure_data_dir,
    load_database,
    save_database,
    find_user_by_email,
    find_organization_by_slug,
    find_project_by_slug,
    find_projects_by_organization,
    find_organizations_by_owner,
    slug_exists_in_organizations,
    slug_exists_in_projects,
    DATA_DIR,
    DATA_FILE,
)
from agentflow.models import User, Organization, Project, Database


@pytest.fixture
def temp_data_dir(tmp_path: Path):
    """Create temporary data directory for testing."""

    def mock_data_dir():
        return tmp_path / ".agentflow"

    with patch("agentflow.storage.DATA_DIR", mock_data_dir()):
        with patch("agentflow.storage.DATA_FILE", mock_data_dir() / "data.json"):
            yield


class TestEnsureDataDir:
    """Tests for ensure_data_dir function."""

    def test_creates_directory_if_not_exists(self, temp_data_dir):
        """Test that ensure_data_dir creates directory."""
        import agentflow.storage

        # Directory should not exist initially
        assert not agentflow.storage.DATA_DIR.exists()

        # Call ensure_data_dir
        ensure_data_dir()

        # Directory should now exist
        assert agentflow.storage.DATA_DIR.exists()

    def test_does_not_fail_if_directory_exists(self, temp_data_dir):
        """Test that ensure_data_dir doesn't fail if directory exists."""
        import agentflow.storage

        # Create directory
        ensure_data_dir()

        # Call again - should not raise
        ensure_data_dir()

        assert agentflow.storage.DATA_DIR.exists()


class TestLoadDatabase:
    """Tests for load_database function."""

    def test_loads_empty_database_if_file_not_exists(self, temp_data_dir):
        """Test that load_database returns empty Database if file doesn't exist."""
        db = load_database()

        assert db.users == []
        assert db.organizations == []
        assert db.projects == []

    def test_loads_database_from_file(self, temp_data_dir):
        """Test that load_database loads data from JSON file."""
        import agentflow.storage

        # Create test data
        test_data = {
            "users": [
                {
                    "id": "user-1",
                    "email": "test@example.com",
                    "password_hash": "hash",
                    "name": "Test User",
                    "created_at": "2025-01-20T00:00:00Z",
                    "api_keys": [],
                }
            ],
            "organizations": [],
            "projects": [],
        }

        # Write to file
        ensure_data_dir()
        with open(agentflow.storage.DATA_FILE, "w") as f:
            json.dump(test_data, f)

        # Load database
        db = load_database()

        assert len(db.users) == 1
        assert db.users[0].email == "test@example.com"


class TestSaveDatabase:
    """Tests for save_database function."""

    def test_saves_database_to_file(self, temp_data_dir):
        """Test that save_database writes to JSON file."""
        import agentflow.storage

        # Create test database
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db = Database(users=[user], organizations=[], projects=[])

        # Save database
        save_database(db)

        # Verify file exists
        assert agentflow.storage.DATA_FILE.exists()

        # Load and verify content
        with open(agentflow.storage.DATA_FILE, "r") as f:
            data = json.load(f)

        assert len(data["users"]) == 1
        assert data["users"][0]["email"] == "test@example.com"


class TestFindUserByEmail:
    """Tests for find_user_by_email function."""

    def test_returns_none_if_user_not_found(self, temp_data_dir):
        """Test that find_user_by_email returns None if user doesn't exist."""
        result = find_user_by_email("nonexistent@example.com")
        assert result is None

    def test_returns_user_if_found(self, temp_data_dir):
        """Test that find_user_by_email returns User if found."""
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db = Database(users=[user], organizations=[], projects=[])
        save_database(db)

        result = find_user_by_email("test@example.com")

        assert result is not None
        assert result.email == "test@example.com"
        assert result.name == "Test"


class TestFindOrganizationBySlug:
    """Tests for find_organization_by_slug function."""

    def test_returns_none_if_org_not_found(self, temp_data_dir):
        """Test that find_organization_by_slug returns None if org doesn't exist."""
        result = find_organization_by_slug("nonexistent")
        assert result is None

    def test_returns_org_if_found(self, temp_data_dir):
        """Test that find_organization_by_slug returns Organization if found."""
        org = Organization(owner_id="user-1", name="Test Org", slug="test-org")
        db = Database(users=[], organizations=[org], projects=[])
        save_database(db)

        result = find_organization_by_slug("test-org")

        assert result is not None
        assert result.slug == "test-org"
        assert result.name == "Test Org"


class TestFindProjectBySlug:
    """Tests for find_project_by_slug function."""

    def test_returns_none_if_project_not_found(self, temp_data_dir):
        """Test that find_project_by_slug returns None if project doesn't exist."""
        result = find_project_by_slug("org-1", "nonexistent")
        assert result is None

    def test_returns_none_if_wrong_org(self, temp_data_dir):
        """Test that find_project_by_slug returns None if org doesn't match."""
        project = Project(
            organization_id="org-1", name="Test Project", slug="test-project"
        )
        db = Database(users=[], organizations=[], projects=[project])
        save_database(db)

        result = find_project_by_slug("org-2", "test-project")
        assert result is None

    def test_returns_project_if_found(self, temp_data_dir):
        """Test that find_project_by_slug returns Project if found."""
        project = Project(
            organization_id="org-1", name="Test Project", slug="test-project"
        )
        db = Database(users=[], organizations=[], projects=[project])
        save_database(db)

        result = find_project_by_slug("org-1", "test-project")

        assert result is not None
        assert result.slug == "test-project"
        assert result.organization_id == "org-1"


class TestFindProjectsByOrganization:
    """Tests for find_projects_by_organization function."""

    def test_returns_empty_list_if_no_projects(self, temp_data_dir):
        """Test that find_projects_by_organization returns empty list if no projects."""
        result = find_projects_by_organization("org-1")
        assert result == []

    def test_returns_only_org_projects(self, temp_data_dir):
        """Test that find_projects_by_organization filters by organization."""
        project1 = Project(
            id="proj-1", organization_id="org-1", name="Project 1", slug="proj-1"
        )
        project2 = Project(
            id="proj-2", organization_id="org-2", name="Project 2", slug="proj-2"
        )
        project3 = Project(
            id="proj-3", organization_id="org-1", name="Project 3", slug="proj-3"
        )
        db = Database(users=[], organizations=[], projects=[project1, project2, project3])
        save_database(db)

        result = find_projects_by_organization("org-1")

        assert len(result) == 2
        assert result[0].id == "proj-1"
        assert result[1].id == "proj-3"


class TestFindOrganizationsByOwner:
    """Tests for find_organizations_by_owner function."""

    def test_returns_empty_list_if_no_orgs(self, temp_data_dir):
        """Test that find_organizations_by_owner returns empty list if no orgs."""
        result = find_organizations_by_owner("user-1")
        assert result == []

    def test_returns_only_user_orgs(self, temp_data_dir):
        """Test that find_organizations_by_owner filters by owner."""
        org1 = Organization(id="org-1", owner_id="user-1", name="Org 1", slug="org-1")
        org2 = Organization(id="org-2", owner_id="user-2", name="Org 2", slug="org-2")
        org3 = Organization(id="org-3", owner_id="user-1", name="Org 3", slug="org-3")
        db = Database(users=[], organizations=[org1, org2, org3], projects=[])
        save_database(db)

        result = find_organizations_by_owner("user-1")

        assert len(result) == 2
        assert result[0].id == "org-1"
        assert result[1].id == "org-3"


class TestSlugExistsInOrganizations:
    """Tests for slug_exists_in_organizations function."""

    def test_returns_false_if_slug_not_exists(self, temp_data_dir):
        """Test that slug_exists_in_organizations returns False if slug doesn't exist."""
        result = slug_exists_in_organizations("nonexistent")
        assert result is False

    def test_returns_true_if_slug_exists(self, temp_data_dir):
        """Test that slug_exists_in_organizations returns True if slug exists."""
        org = Organization(owner_id="user-1", name="Test Org", slug="test-org")
        db = Database(users=[], organizations=[org], projects=[])
        save_database(db)

        result = slug_exists_in_organizations("test-org")
        assert result is True


class TestSlugExistsInProjects:
    """Tests for slug_exists_in_projects function."""

    def test_returns_false_if_slug_not_exists(self, temp_data_dir):
        """Test that slug_exists_in_projects returns False if slug doesn't exist."""
        result = slug_exists_in_projects("org-1", "nonexistent")
        assert result is False

    def test_returns_false_if_wrong_org(self, temp_data_dir):
        """Test that slug_exists_in_projects returns False if org doesn't match."""
        project = Project(
            organization_id="org-1", name="Test Project", slug="test-project"
        )
        db = Database(users=[], organizations=[], projects=[project])
        save_database(db)

        result = slug_exists_in_projects("org-2", "test-project")
        assert result is False

    def test_returns_true_if_slug_exists(self, temp_data_dir):
        """Test that slug_exists_in_projects returns True if slug exists."""
        project = Project(
            organization_id="org-1", name="Test Project", slug="test-project"
        )
        db = Database(users=[], organizations=[], projects=[project])
        save_database(db)

        result = slug_exists_in_projects("org-1", "test-project")
        assert result is True
