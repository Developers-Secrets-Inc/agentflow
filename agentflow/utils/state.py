"""Local state management for AgentFlow."""

import json
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """Get the AgentFlow configuration directory.

    Returns:
        Path to ~/.agentflow
    """
    return Path.home() / ".agentflow"


def get_state_path() -> Path:
    """Get the state file path.

    Returns:
        Path to ~/.agentflow/state.json
    """
    return get_config_dir() / "state.json"


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    get_config_dir().mkdir(exist_ok=True)


def state_exists() -> bool:
    """Check if state file exists.

    Returns:
        True if state exists, False otherwise
    """
    return get_state_path().exists()


def load_state() -> dict[str, Any]:
    """Load state from file.

    Returns:
        State dictionary, or empty dict if no state exists
    """
    if not state_exists():
        return {}

    with get_state_path().open("r") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    """Save state to file.

    Args:
        state: State dictionary to save
    """
    ensure_config_dir()

    with get_state_path().open("w") as f:
        json.dump(state, f, indent=2)


def get_current_session_id() -> str | None:
    """Get the current active session ID.

    Returns:
        Session ID or None if no active session
    """
    state = load_state()
    return state.get("current_session_id")


def set_current_session(session_id: str) -> None:
    """Set the current active session.

    Args:
        session_id: Session ID to set as active
    """
    state = load_state()
    state["current_session_id"] = session_id
    save_state(state)


def clear_current_session() -> None:
    """Clear the current active session."""
    state = load_state()
    state.pop("current_session_id", None)
    save_state(state)


def get_current_workspace_id() -> str | None:
    """Get the current workspace ID from state.

    Returns:
        Workspace ID or None if not set
    """
    state = load_state()
    return state.get("current_workspace_id")


def set_current_workspace(workspace_id: str) -> None:
    """Set the current workspace in state.

    Args:
        workspace_id: Workspace ID to set as current
    """
    state = load_state()
    state["current_workspace_id"] = workspace_id
    save_state(state)
