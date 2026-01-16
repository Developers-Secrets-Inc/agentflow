"""Local configuration management for AgentFlow."""

import json
from pathlib import Path
from typing import Any

from agentflow.config.database import DatabaseSettings


def get_config_dir() -> Path:
    """Get the AgentFlow configuration directory.

    Returns:
        Path to ~/.agentflow
    """
    return Path.home() / ".agentflow"


def get_config_path() -> Path:
    """Get the configuration file path.

    Returns:
        Path to ~/.agentflow/config.json
    """
    return get_config_dir() / "config.json"


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    get_config_dir().mkdir(exist_ok=True)


def config_exists() -> bool:
    """Check if configuration file exists.

    Returns:
        True if config exists, False otherwise
    """
    return get_config_path().exists()


def load_config() -> dict[str, Any]:
    """Load configuration from file.

    Returns:
        Configuration dictionary, or empty dict if no config exists
    """
    if not config_exists():
        return {}

    with get_config_path().open("r") as f:
        return json.load(f)


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file.

    Args:
        config: Configuration dictionary to save
    """
    ensure_config_dir()

    with get_config_path().open("w") as f:
        json.dump(config, f, indent=2)


def get_database_config() -> DatabaseSettings | None:
    """Get database configuration from settings.

    Returns:
        DatabaseSettings if configured, None otherwise
    """
    config = load_config()
    db_config = config.get("database", {})

    if not db_config.get("db_url"):
        return None

    return DatabaseSettings(**db_config)


def save_database_config(db_settings: DatabaseSettings) -> None:
    """Save database configuration.

    Args:
        db_settings: Database settings to save
    """
    config = load_config()
    config["database"] = {
        "db_url": db_settings.db_url,
        "db_schema": db_settings.db_schema,
        "db_pool_size": db_settings.db_pool_size,
        "db_max_overflow": db_settings.db_max_overflow,
    }
    save_config(config)


def get_current_workspace_id() -> str | None:
    """Get the current workspace ID from config.

    Returns:
        Workspace ID or None if not set
    """
    config = load_config()
    return config.get("current_workspace")


def set_current_workspace(workspace_id: str) -> None:
    """Set the current workspace.

    Args:
        workspace_id: Workspace ID to set as current
    """
    config = load_config()
    config["current_workspace"] = workspace_id
    save_config(config)


def get_user_id() -> str | None:
    """Get the user ID from config.

    Returns:
        User ID or None if not set
    """
    config = load_config()
    return config.get("user", {}).get("id")


def get_user_name() -> str | None:
    """Get the user name from config.

    Returns:
        User name or None if not set
    """
    config = load_config()
    return config.get("user", {}).get("name")


def save_user(user_id: str, user_name: str) -> None:
    """Save user information.

    Args:
        user_id: User ID
        user_name: User name
    """
    config = load_config()
    config["user"] = {
        "id": user_id,
        "name": user_name,
    }
    save_config(config)
