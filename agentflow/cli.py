"""AgentFlow CLI - Main entry point."""

import asyncio
from pathlib import Path

import questionary
import typer

from agentflow.config import (
    config_exists,
    get_current_workspace_id,
    get_database_config,
    save_database_config,
    save_user,
    set_current_workspace,
)
from agentflow.config.database import DatabaseSettings, set_database_settings
from agentflow.db.base import init_db, close_db
from agentflow.entities import Workspace
from agentflow.db.session import DatabaseSession, get_db
from agentflow.utils.id_generator import generate_id

app = typer.Typer(help="AgentFlow - Git-like workflow management for AI agents")

config_app = typer.Typer(help="Configuration management")
app.add_typer(config_app, name="config")

workspace_app = typer.Typer(help="Workspace management")
app.add_typer(workspace_app, name="workspace")


@app.command()
def init(
    db_url: str = typer.Option(None, "--db-url", help="Direct database URL (skips prompts)"),
    create_workspace: bool = typer.Option(False, "--workspace", "-w", help="Create a workspace after init"),
) -> None:
    """Initialize AgentFlow configuration.

    Interactively configure database connection and create initial workspace.
    """
    if db_url:
        # Direct mode - use provided URL
        _init_direct(db_url, create_workspace)
    else:
        # Interactive mode
        _init_interactive()


def _init_direct(db_url: str, create_ws: bool = False) -> None:
    """Initialize with direct database URL.

    Args:
        db_url: Database connection URL
        create_ws: Whether to create a workspace
    """
    typer.echo(f"[*] Configuring AgentFlow with provided database URL...")

    # Create database settings
    db_settings = DatabaseSettings(db_url=db_url)

    # Test connection
    if not _test_connection_sync(db_settings):
        typer.echo("[!] Failed to connect to database. Please check your URL and try again.")
        raise typer.Exit(1)

    # Save configuration
    save_database_config(db_settings)

    # Generate user ID
    user_id = generate_id()
    save_user(user_id, "CLI User")

    typer.echo("[*] Configuration saved to ~/.agentflow/config.json")

    # Create workspace if requested
    if create_ws:
        workspace_name = typer.prompt("Workspace name", default="my-project")
        _create_workspace_sync(workspace_name)
    else:
        typer.echo("[*] Setup complete! Use 'agentflow --help' to see available commands.")


def _init_interactive() -> None:
    """Initialize with interactive prompts."""
    typer.echo("Welcome to AgentFlow! Let's configure your connection.\n")

    # Ask database type
    db_type = questionary.select(
        "Database type:",
        choices=["PostgreSQL", "SQLite"],
        default="PostgreSQL",
    ).ask()

    if db_type == "PostgreSQL":
        # PostgreSQL configuration
        host = questionary.text("Host", default="localhost").ask()
        port = questionary.text("Port", default="5432").ask()
        database = questionary.text("Database name", default="agentflow").ask()
        username = questionary.text("Username", default="postgres").ask()
        password = questionary.password("Password").ask()

        # Build URL
        db_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    else:
        # SQLite configuration
        db_path = questionary.text("Database file path", default="agentflow.db").ask()
        db_url = f"sqlite+aiosqlite:///{db_path}"

    typer.echo("")
    typer.echo("[*] Testing connection...")

    # Create database settings
    db_settings = DatabaseSettings(db_url=db_url)

    # Test connection
    if not _test_connection_sync(db_settings):
        typer.echo("[!] Failed to connect to database. Please check your credentials and try again.")
        raise typer.Exit(1)

    typer.echo("[*] Connection successful!\n")

    # Save configuration
    save_database_config(db_settings)

    # Get user info
    user_id = generate_id()
    user_name = questionary.text("Your name", default="Developer").ask()
    save_user(user_id, user_name)

    typer.echo("[*] Configuration saved to ~/.agentflow/config.json\n")

    # Ask about workspace
    create_workspace = questionary.confirm("Create a workspace?", default=False).ask()

    if create_workspace:
        workspace_name = questionary.text("Workspace name", default="my-project").ask()
        _create_workspace_sync(workspace_name)

    typer.echo("\n[*] You're ready! Use 'agentflow --help' to see available commands.")


def _test_connection_sync(db_settings: DatabaseSettings) -> bool:
    """Test database connection synchronously.

    Args:
        db_settings: Database settings to test

    Returns:
        True if connection successful, False otherwise
    """
    try:
        # Run async init_db in sync context
        asyncio.run(_test_connection_async(db_settings))
        return True
    except Exception as e:
        typer.echo(f"[!] Connection error: {e}")
        return False


async def _test_connection_async(db_settings: DatabaseSettings) -> None:
    """Test database connection asynchronously.

    Args:
        db_settings: Database settings to test
    """
    await init_db()
    await close_db()


def _create_workspace_sync(workspace_name: str) -> None:
    """Create workspace synchronously.

    Args:
        workspace_name: Name for the workspace
    """
    try:
        asyncio.run(_create_workspace_async(workspace_name))
    except Exception as e:
        typer.echo(f"[!] Failed to create workspace: {e}")
        raise typer.Exit(1)


async def _create_workspace_async(workspace_name: str) -> None:
    """Create workspace asynchronously.

    Args:
        workspace_name: Name for the workspace
    """
    await init_db()

    async with get_db() as db:
        db_session = DatabaseSession(db.session)
        workspace = await Workspace.create(db_session, workspace_name)
        set_current_workspace(workspace.id)

    await close_db()
    typer.echo(f"[*] Workspace '{workspace_name}' created")


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    if not config_exists():
        typer.echo("[!] No configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    config = get_database_config()
    if not config:
        typer.echo("[!] No database configuration found.")
        raise typer.Exit(1)

    typer.echo("[*] Current configuration:")
    typer.echo(f"  Database URL: {config.db_url}")
    typer.echo(f"  Schema: {config.db_schema}")
    typer.echo(f"  Pool size: {config.db_pool_size}")
    typer.echo(f"  Max overflow: {config.db_max_overflow}")


@config_app.command("test")
def config_test() -> None:
    """Test database connection."""
    db_config = get_database_config()
    if not db_config:
        typer.echo("[!] No database configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    typer.echo("[*] Testing connection...")
    if _test_connection_sync(db_config):
        typer.echo("[*] Connection successful!")
    else:
        raise typer.Exit(1)


@workspace_app.command("current")
def workspace_current() -> None:
    """Show the current workspace."""
    if not config_exists():
        typer.echo("[!] No configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    current_workspace_id = get_current_workspace_id()
    if not current_workspace_id:
        typer.echo("[!] No workspace selected. Use 'agentflow workspace switch <name>' first.")
        raise typer.Exit(1)

    _workspace_current_sync(current_workspace_id)


def _workspace_current_sync(workspace_id: str) -> None:
    """Show workspace details synchronously.

    Args:
        workspace_id: Workspace ID to display
    """
    try:
        asyncio.run(_workspace_current_async(workspace_id))
    except Exception as e:
        typer.echo(f"[!] Failed to retrieve workspace: {e}")
        raise typer.Exit(1)


async def _workspace_current_async(workspace_id: str) -> None:
    """Show workspace details asynchronously.

    Args:
        workspace_id: Workspace ID to display
    """
    db_config = get_database_config()
    if not db_config:
        typer.echo("[!] No database configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    # Set database settings from config
    set_database_settings(db_config)

    # Initialize database with config settings
    await init_db()

    async with get_db() as db:
        db_session = DatabaseSession(db.session)
        workspace = await Workspace.get_by_id(db_session, workspace_id)

        if not workspace:
            typer.echo(f"[!] Workspace with ID '{workspace_id}' not found.")
            typer.echo("[!] Use 'agentflow workspace list' to see available workspaces.")
            raise typer.Exit(1)

        typer.echo("[*] Current workspace:")
        typer.echo(f"  Name: {workspace.name}")
        typer.echo(f"  ID: {workspace.id}")
        if workspace.description:
            typer.echo(f"  Description: {workspace.description}")
        typer.echo(f"  Created at: {workspace.created_at}")

    await close_db()


@workspace_app.command("list")
def workspace_list() -> None:
    """List all workspaces."""
    if not config_exists():
        typer.echo("[!] No configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    _workspace_list_sync()


def _workspace_list_sync() -> None:
    """List workspaces synchronously."""
    try:
        asyncio.run(_workspace_list_async())
    except Exception as e:
        typer.echo(f"[!] Failed to list workspaces: {e}")
        raise typer.Exit(1)


async def _workspace_list_async() -> None:
    """List workspaces asynchronously."""
    db_config = get_database_config()
    if not db_config:
        typer.echo("[!] No database configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    # Set database settings from config
    set_database_settings(db_config)

    await init_db()

    async with get_db() as db:
        db_session = DatabaseSession(db.session)
        workspaces = await Workspace.list_all(db_session)
        current_workspace_id = get_current_workspace_id()

        if not workspaces:
            typer.echo("[*] No workspaces found. Create one with 'agentflow workspace create <name>'.")
            return

        typer.echo("[*] Workspaces:")
        for workspace in workspaces:
            current_marker = " (current)" if workspace.id == current_workspace_id else ""
            desc = f" - {workspace.description}" if workspace.description else ""
            typer.echo(f"  {workspace.name}{current_marker}")
            typer.echo(f"    ID: {workspace.id}{desc}")

    await close_db()


@workspace_app.command("create")
def workspace_create(
    name: str = typer.Argument(..., help="Workspace name"),
    description: str = typer.Option(None, "--description", "-d", help="Workspace description"),
) -> None:
    """Create a new workspace."""
    if not config_exists():
        typer.echo("[!] No configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    _workspace_create_sync(name, description)


def _workspace_create_sync(name: str, description: str | None) -> None:
    """Create workspace synchronously.

    Args:
        name: Workspace name
        description: Optional description
    """
    try:
        asyncio.run(_workspace_create_async(name, description))
    except Exception as e:
        typer.echo(f"[!] Failed to create workspace: {e}")
        raise typer.Exit(1)


async def _workspace_create_async(name: str, description: str | None) -> None:
    """Create workspace asynchronously.

    Args:
        name: Workspace name
        description: Optional description
    """
    db_config = get_database_config()
    if not db_config:
        typer.echo("[!] No database configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    # Set database settings from config
    set_database_settings(db_config)

    await init_db()

    async with get_db() as db:
        db_session = DatabaseSession(db.session)

        # Check if workspace with same name exists
        existing = await Workspace.get_by_name(db_session, name)
        if existing:
            typer.echo(f"[!] Workspace '{name}' already exists.")
            raise typer.Exit(1)

        # Create workspace
        workspace = await Workspace.create(db_session, name, description)

        # Set as current if it's the first workspace
        all_workspaces = await Workspace.list_all(db_session)
        if len(all_workspaces) == 1:
            set_current_workspace(workspace.id)
            typer.echo("[*] This is your first workspace. Set as current.")

        typer.echo(f"[*] Workspace '{name}' created (id: {workspace.id})")

    await close_db()


@workspace_app.command("switch")
def workspace_switch(
    identifier: str = typer.Argument(..., help="Workspace ID or name"),
) -> None:
    """Switch to a different workspace."""
    if not config_exists():
        typer.echo("[!] No configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    _workspace_switch_sync(identifier)


def _workspace_switch_sync(identifier: str) -> None:
    """Switch workspace synchronously.

    Args:
        identifier: Workspace ID or name
    """
    try:
        asyncio.run(_workspace_switch_async(identifier))
    except Exception as e:
        typer.echo(f"[!] Failed to switch workspace: {e}")
        raise typer.Exit(1)


async def _workspace_switch_async(identifier: str) -> None:
    """Switch workspace asynchronously.

    Args:
        identifier: Workspace ID or name
    """
    db_config = get_database_config()
    if not db_config:
        typer.echo("[!] No database configuration found. Run 'agentflow init' first.")
        raise typer.Exit(1)

    # Set database settings from config
    set_database_settings(db_config)

    await init_db()

    async with get_db() as db:
        db_session = DatabaseSession(db.session)

        # Try to find workspace by ID, then by name
        workspace = await Workspace.get_by_id(db_session, identifier)
        if not workspace:
            workspace = await Workspace.get_by_name(db_session, identifier)

        if not workspace:
            typer.echo(f"[!] Workspace '{identifier}' not found.")
            typer.echo("[!] Use 'agentflow workspace list' to see available workspaces.")
            raise typer.Exit(1)

        # Set as current workspace
        set_current_workspace(workspace.id)
        typer.echo(f"[*] Switched to workspace: {workspace.name}")

    await close_db()


if __name__ == "__main__":
    app()
