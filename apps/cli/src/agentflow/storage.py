"""Storage layer for AgentFlow CLI data."""

import json
from pathlib import Path
from typing import Optional

from agentflow.models import Database, User, Organization, Project

# File paths
DATA_DIR = Path.home() / ".agentflow"
DATA_FILE = DATA_DIR / "data.json"


def ensure_data_dir() -> None:
    """Create .agentflow directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)


def load_database() -> Database:
    """Load database from JSON file.

    Returns an empty Database if the file doesn't exist.
    """
    if not DATA_FILE.exists():
        return Database()

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    return Database(**data)


def save_database(db: Database) -> None:
    """Save database to JSON file."""
    ensure_data_dir()

    with open(DATA_FILE, "w") as f:
        f.write(db.model_dump_json(indent=2))


def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email.

    Args:
        email: User email address

    Returns:
        User if found, None otherwise
    """
    db = load_database()
    for user in db.users:
        if user.email == email:
            return user
    return None


def find_organization_by_slug(slug: str) -> Optional[Organization]:
    """Find organization by slug.

    Args:
        slug: Organization slug

    Returns:
        Organization if found, None otherwise
    """
    db = load_database()
    for org in db.organizations:
        if org.slug == slug:
            return org
    return None


def find_project_by_slug(organization_id: str, slug: str) -> Optional[Project]:
    """Find project by slug within organization.

    Args:
        organization_id: Organization ID
        slug: Project slug

    Returns:
        Project if found, None otherwise
    """
    db = load_database()
    for project in db.projects:
        if project.organization_id == organization_id and project.slug == slug:
            return project
    return None


def find_projects_by_organization(organization_id: str) -> list[Project]:
    """Find all projects within organization.

    Args:
        organization_id: Organization ID

    Returns:
        List of projects
    """
    db = load_database()
    return [p for p in db.projects if p.organization_id == organization_id]


def find_organizations_by_owner(owner_id: str) -> list[Organization]:
    """Find all organizations owned by user.

    Args:
        owner_id: User ID

    Returns:
        List of organizations
    """
    db = load_database()
    return [org for org in db.organizations if org.owner_id == owner_id]


def slug_exists_in_organizations(slug: str) -> bool:
    """Check if organization slug exists.

    Args:
        slug: Organization slug

    Returns:
        True if slug exists, False otherwise
    """
    db = load_database()
    return any(org.slug == slug for org in db.organizations)


def slug_exists_in_projects(organization_id: str, slug: str) -> bool:
    """Check if project slug exists within organization.

    Args:
        organization_id: Organization ID
        slug: Project slug

    Returns:
        True if slug exists, False otherwise
    """
    db = load_database()
    return any(
        p.organization_id == organization_id and p.slug == slug for p in db.projects
    )
