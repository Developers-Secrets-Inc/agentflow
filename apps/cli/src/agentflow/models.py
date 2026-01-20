"""Data models for AgentFlow CLI."""

from datetime import datetime, UTC
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
import uuid


def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def now_utc() -> datetime:
    """Get current datetime in UTC."""
    return datetime.now(UTC)


class APIKey(BaseModel):
    """API key model."""

    id: str = Field(default_factory=generate_uuid)
    key: str  # API key (plaintext for Phase 0 local storage)
    name: str
    created_at: datetime = Field(default_factory=now_utc)
    last_used_at: Optional[datetime] = None
    is_active: bool = True


class User(BaseModel):
    """User model."""

    id: str = Field(default_factory=generate_uuid)
    email: EmailStr
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=now_utc)
    api_keys: List[APIKey] = []


class Organization(BaseModel):
    """Organization model."""

    id: str = Field(default_factory=generate_uuid)
    owner_id: str
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=now_utc)


class Project(BaseModel):
    """Project model."""

    id: str = Field(default_factory=generate_uuid)
    organization_id: str
    name: str
    slug: str
    description: Optional[str] = None
    github_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=now_utc)


class Database(BaseModel):
    """Database model containing all data."""

    users: List[User] = []
    organizations: List[Organization] = []
    projects: List[Project] = []
