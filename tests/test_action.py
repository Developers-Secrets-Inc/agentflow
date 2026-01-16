"""Tests for Action entity."""

import pytest

from agentflow.entities.action import Action


@pytest.mark.asyncio
async def test_create_action(db_session):
    """Test creating an action."""
    action = Action.create(
        session_id="test-session-1",
        description="Created a test file",
        action_type="file_create",
        metadata={"file": "test.py", "lines": 10},
    )

    db_session.add(action)
    await db_session.commit()
    await db_session.refresh(action)

    assert action.id is not None
    assert action.session_id == "test-session-1"
    assert action.description == "Created a test file"
    assert action.action_type == "file_create"
    assert action.timestamp is not None
    assert action.get_metadata() == {"file": "test.py", "lines": 10}


@pytest.mark.asyncio
async def test_create_action_without_metadata(db_session):
    """Test creating an action without metadata."""
    action = Action.create(
        session_id="test-session-2",
        description="Analyzed code",
        action_type="analysis",
    )

    db_session.add(action)
    await db_session.commit()
    await db_session.refresh(action)

    assert action.id is not None
    assert action.meta_data is None
    assert action.get_metadata() is None


@pytest.mark.asyncio
async def test_action_repr(db_session):
    """Test action string representation."""
    action = Action.create(
        session_id="test-session-3",
        description="This is a very long description that should be truncated",
        action_type="test",
    )

    repr_str = repr(action)
    assert "Action(id=" in repr_str
    assert "type=test" in repr_str
    assert "..." in repr_str  # Truncated description
