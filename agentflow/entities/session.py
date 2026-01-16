"""Session entity for tracking agent work sessions."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentflow.db.base import Base
from agentflow.db.session import DatabaseSession
from agentflow.utils.id_generator import generate_id

if TYPE_CHECKING:
    from agentflow.entities.workspace import Workspace
    from agentflow.entities.commit import Commit
    from agentflow.entities.action import Action


class SessionStatus:
    """Session status constants."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"


class Session(Base):
    """Represents a work session for tracking agent activity."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String,
        default=SessionStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(  # type: ignore[name-defined]
        back_populates="sessions",
    )
    commit: Mapped["Commit | None"] = relationship(  # type: ignore[name-defined]
        back_populates="session",
        uselist=False,
    )

    @classmethod
    async def create(cls, db: DatabaseSession, workspace_id: str, task: str) -> "Session":
        """Create a new session.

        Args:
            db: Database session
            workspace_id: Workspace ID
            task: Task description

        Returns:
            The created Session instance
        """
        session = cls(
            id=generate_id(),
            workspace_id=workspace_id,
            task=task,
            status=SessionStatus.ACTIVE,
            started_at=datetime.utcnow(),
        )
        return await db.add(session)

    @classmethod
    async def get_active(cls, db: DatabaseSession, workspace_id: str) -> "Session | None":
        """Get the active session for a workspace.

        Args:
            db: Database session
            workspace_id: Workspace ID

        Returns:
            Active session or None if no active session exists
        """
        stmt = select(cls).where(
            cls.workspace_id == workspace_id,
            cls.status == SessionStatus.ACTIVE,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, db: DatabaseSession, session_id: str) -> "Session | None":
        """Get a session by ID.

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            Session or None if not found
        """
        return await db.get(cls, session_id)

    async def log_action(
        self,
        db: DatabaseSession,
        description: str,
        action_type: str,
        metadata: dict | None = None,
    ) -> "Action":
        """Log an action during this session.

        Args:
            db: Database session
            description: Action description
            action_type: Type of action
            metadata: Optional metadata

        Returns:
            The created Action instance
        """
        from agentflow.entities.action import Action

        action = Action.create(
            session_id=self.id,
            description=description,
            action_type=action_type,
            metadata=metadata,
        )
        return await db.add(action)

    async def get_actions(self, db: DatabaseSession) -> list["Action"]:
        """Get all actions for this session.

        Args:
            db: Database session

        Returns:
            List of actions ordered by timestamp
        """
        from agentflow.entities.action import Action

        stmt = select(Action).where(
            Action.session_id == self.id
        ).order_by(Action.timestamp)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def complete(
        self,
        db: DatabaseSession,
        message: str,
        description: str | None = None,
    ) -> "Commit":
        """Complete the session and create a commit.

        Args:
            db: Database session
            message: Commit message
            description: Optional detailed description

        Returns:
            The created Commit instance
        """
        from agentflow.entities.commit import Commit

        # Update session
        self.completed_at = datetime.utcnow()
        self.status = SessionStatus.COMPLETED
        await db.commit()

        # Get previous commit for parent reference
        parent = await Commit._get_last_for_workspace(db, self.workspace_id)

        # Calculate duration
        duration = self.duration_seconds

        # Create commit
        commit = Commit(
            id=generate_id(),
            session_id=self.id,
            workspace_id=self.workspace_id,
            message=message,
            description=description,
            parent_id=parent.id if parent else None,
            duration_seconds=duration,
            created_at=datetime.utcnow(),
        )
        return await db.add(commit)

    async def abort(self, db: DatabaseSession) -> None:
        """Abort the current session.

        Args:
            db: Database session
        """
        self.completed_at = datetime.utcnow()
        self.status = SessionStatus.ABORTED
        await db.commit()

    @property
    def duration_seconds(self) -> int | None:
        """Get session duration in seconds.

        Returns:
            Duration in seconds or None if session is not completed
        """
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds())
        return None

    @property
    def is_active(self) -> bool:
        """Check if session is active.

        Returns:
            True if session is active, False otherwise
        """
        return self.status == SessionStatus.ACTIVE

    def __repr__(self) -> str:
        return f"Session(id={self.id}, task={self.task[:30]}..., status={self.status})"
