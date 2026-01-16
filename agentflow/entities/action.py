"""Action entity for logging session activities."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from agentflow.db.base import Base
from agentflow.utils.id_generator import generate_id


class Action(Base):
    """Represents an action logged during a session."""

    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    session_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    meta_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    @classmethod
    def create(
        cls,
        session_id: str,
        description: str,
        action_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> "Action":
        """Create a new action.

        Args:
            session_id: Session ID
            description: Action description
            action_type: Type of action
            metadata: Optional metadata dictionary

        Returns:
            The created Action instance
        """
        action = cls(
            id=generate_id(),
            session_id=session_id,
            description=description,
            action_type=action_type,
            meta_data=json.dumps(metadata) if metadata else None,
        )
        return action

    @classmethod
    async def list_for_session(cls, db, session_id: str) -> list["Action"]:
        """List all actions for a session.

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            List of actions ordered by timestamp
        """
        stmt = select(cls).where(cls.session_id == session_id).order_by(cls.timestamp)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def get_metadata(self) -> dict[str, Any] | None:
        """Get metadata as a dictionary.

        Returns:
            Metadata dict or None
        """
        if self.meta_data:
            return json.loads(self.meta_data)
        return None

    def __repr__(self) -> str:
        return f"Action(id={self.id}, type={self.action_type}, description={self.description[:50]}...)"
