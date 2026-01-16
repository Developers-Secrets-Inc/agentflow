"""Commit entity for summarizing completed sessions."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, Text, ForeignKey, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentflow.db.base import Base
from agentflow.db.session import DatabaseSession
from agentflow.utils.id_generator import generate_id

if TYPE_CHECKING:
    from agentflow.entities.workspace import Workspace
    from agentflow.entities.session import Session
    from agentflow.entities.action import Action


class Commit(Base):
    """Represents a commit summarizing a completed session."""

    __tablename__ = "commits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    session_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    workspace_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("commits.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship(  # type: ignore[name-defined]
        back_populates="commit",
    )
    workspace: Mapped["Workspace"] = relationship(  # type: ignore[name-defined]
        back_populates="commits",
    )
    parent: Mapped["Commit | None"] = relationship(  # type: ignore[name-defined]
        remote_side=id,
        back_populates="children",
    )
    children: Mapped[List["Commit"]] = relationship(  # type: ignore[name-defined]
        back_populates="parent",
    )

    @classmethod
    async def get_by_id(cls, db: DatabaseSession, commit_id: str) -> "Commit | None":
        """Get a commit by ID.

        Args:
            db: Database session
            commit_id: Commit ID

        Returns:
            Commit or None if not found
        """
        return await db.get(cls, commit_id)

    @classmethod
    async def list_for_workspace(
        cls,
        db: DatabaseSession,
        workspace_id: str,
        limit: int | None = None,
    ) -> list["Commit"]:
        """List commits for a workspace.

        Args:
            db: Database session
            workspace_id: Workspace ID
            limit: Maximum number of commits to return

        Returns:
            List of commits ordered by creation date (newest first)
        """
        stmt = select(cls).where(
            cls.workspace_id == workspace_id
        ).order_by(cls.created_at.desc())

        if limit:
            stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def _get_last_for_workspace(
        cls,
        db: DatabaseSession,
        workspace_id: str,
    ) -> "Commit | None":
        """Get the most recent commit for a workspace.

        Args:
            db: Database session
            workspace_id: Workspace ID

        Returns:
            Most recent commit or None if no commits exist
        """
        stmt = select(cls).where(
            cls.workspace_id == workspace_id
        ).order_by(cls.created_at.desc()).limit(1)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session(self, db: DatabaseSession) -> "Session | None":
        """Get the session that created this commit.

        Args:
            db: Database session

        Returns:
            Session or None if not found
        """
        from agentflow.entities.session import Session
        return await db.get(Session, self.session_id)

    async def get_actions(self, db: DatabaseSession) -> list["Action"]:
        """Get actions from the session that created this commit.

        Args:
            db: Database session

        Returns:
            List of actions ordered by timestamp
        """
        from agentflow.entities.action import Action

        stmt = select(Action).where(
            Action.session_id == self.session_id
        ).order_by(Action.timestamp)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @property
    def short_message(self) -> str:
        """Get a shortened version of the message.

        Returns:
            Message truncated to 50 characters
        """
        if len(self.message) <= 50:
            return self.message
        return self.message[:47] + "..."

    @property
    def has_parent(self) -> bool:
        """Check if commit has a parent.

        Returns:
            True if commit has a parent, False otherwise
        """
        return self.parent_id is not None

    @property
    def has_children(self) -> bool:
        """Check if commit has children.

        Returns:
            True if commit has children, False otherwise
        """
        return len(self.children) > 0

    def __repr__(self) -> str:
        return f"Commit(id={self.id}, message={self.short_message})"
