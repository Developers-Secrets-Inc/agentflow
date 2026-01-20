"""Authentication commands."""

import hashlib
import secrets
import typer
from typing import Optional

from agentflow.models import User, APIKey, Database
from agentflow.storage import load_database, save_database, find_user_by_email
from agentflow.utils.config import (
    set_current_user_email,
    set_current_api_key,
    get_current_user_email,
)
from agentflow.utils.validators import validate_email
from agentflow.utils.output import success, error, warning, info, print_table

app = typer.Typer(help="Authentication commands")


def hash_password(password: str) -> str:
    """Hash password using SHA-256.

    Note: In production, use bcrypt or argon2.
    For Phase 0, SHA-256 is sufficient.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a random API key."""
    return f"afk_{secrets.token_urlsafe(32)}"


@app.command()
def register(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    password: str = typer.Option(
        ..., "--password", "-p", help="User password", hide_input=True
    ),
    name: str = typer.Option(..., "--name", "-n", help="User display name"),
):
    """Register a new user account."""
    # Validate email format
    email_error = validate_email(email)
    if email_error:
        error(email_error)
        raise typer.Exit(1)

    # Check if user already exists
    existing_user = find_user_by_email(email)
    if existing_user:
        error("User already exists")
        raise typer.Exit(1)

    # Validate password length
    if len(password) < 8:
        error("Password must be at least 8 characters")
        raise typer.Exit(1)

    # Validate name length
    if len(name) > 255:
        error("Name must be 255 characters or less")
        raise typer.Exit(1)

    # Create user
    user = User(
        email=email, password_hash=hash_password(password), name=name, api_keys=[]
    )

    # Generate default API key
    api_key = APIKey(key=generate_api_key(), name="Default Key")
    user.api_keys.append(api_key)

    # Save to database
    db = load_database()
    db.users.append(user)
    save_database(db)

    # Set as current user
    set_current_user_email(email)
    set_current_api_key(api_key.key)

    # Display success
    success("User registered successfully")
    print()
    info(f"  Email:    {email}")
    info(f"  Name:     {name}")
    print()
    warning("⚠️  Save your API key now. You won't see it again!")
    print()
    info(f"  API Key:  {api_key.key}")


@app.command()
def login(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    password: str = typer.Option(
        ..., "--password", "-p", help="User password", hide_input=True
    ),
):
    """Login with existing credentials."""
    # Find user
    user = find_user_by_email(email)
    if not user:
        error("Invalid credentials")
        raise typer.Exit(1)

    # Verify password
    if user.password_hash != hash_password(password):
        error("Invalid credentials")
        raise typer.Exit(1)

    # Get first active API key
    active_key = None
    for api_key in user.api_keys:
        if api_key.is_active:
            active_key = api_key
            break

    if not active_key:
        error("No active API keys found")
        raise typer.Exit(1)

    # Set as current user
    set_current_user_email(email)
    set_current_api_key(active_key.key)

    # Display success
    success(f"Logged in successfully as {email}")
    print()
    from agentflow.utils.config import get_current_organization, get_current_project

    org = get_current_organization()
    project = get_current_project()

    if org:
        info(f"  Current Organization:  {org}")
    else:
        info("  Current Organization:  (none)")

    if project:
        info(f"  Current Project:       {project}")
    else:
        info("  Current Project:       (none)")

    print()
    info("Set your context:")
    info("  agentflow org list")
    info("  agentflow org use <slug>")


@app.command("api-keys")
def api_keys_command(
    action: str = typer.Argument(..., help="Action: 'list' or 'create'"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="API key name"),
):
    """Manage API keys."""
    if action == "list":
        api_keys_list()
    elif action == "create":
        if not name:
            error("Name is required for creating API key")
            raise typer.Exit(1)
        api_keys_create(name)
    else:
        error(f"Unknown action: {action}")
        error("Use 'list' or 'create'")
        raise typer.Exit(1)


def api_keys_list():
    """List all API keys for current user."""
    email = get_current_user_email()
    if not email:
        error("Not authenticated. Run: agentflow auth login")
        raise typer.Exit(1)

    user = find_user_by_email(email)
    if not user:
        error("User not found")
        raise typer.Exit(1)

    if not user.api_keys:
        info("No API keys found")
        return

    # Format data for table
    rows = []
    for key in user.api_keys:
        last_used = key.last_used_at.strftime("%Y-%m-%d %H:%M") if key.last_used_at else "Never"
        created = key.created_at.strftime("%Y-%m-%d %H:%M")
        status = "✓" if key.is_active else "✗"
        rows.append([key.name, last_used, created, status])

    print_table(
        ["NAME", "LAST USED", "CREATED", "ACTIVE"],
        rows,
    )


def api_keys_create(name: str):
    """Create a new API key."""
    email = get_current_user_email()
    if not email:
        error("Not authenticated. Run: agentflow auth login")
        raise typer.Exit(1)

    if len(name) > 255:
        error("Name must be 255 characters or less")
        raise typer.Exit(1)

    # Load database
    db = load_database()

    # Find user
    user_index = None
    for i, user in enumerate(db.users):
        if user.email == email:
            user_index = i
            break

    if user_index is None:
        error("User not found")
        raise typer.Exit(1)

    # Create new API key
    api_key = APIKey(key=generate_api_key(), name=name)

    # Add to user
    db.users[user_index].api_keys.append(api_key)
    save_database(db)

    # Update current API key
    set_current_api_key(api_key.key)

    # Display success
    success("API key created")
    print()
    info(f"  Name:     {name}")
    print()
    warning("⚠️  Save your API key now. You won't see it again!")
    print()
    info(f"  API Key:  {api_key.key}")


@app.command()
def status():
    """Show current authentication status."""
    from agentflow.utils.config import (
        get_current_organization,
        get_current_project,
    )

    email = get_current_user_email()

    # Print header
    print()
    info("AgentFlow CLI v0.0.1")
    print()

    # Authentication status
    if email:
        success("Authentication: ✓ Authenticated")
        user = find_user_by_email(email)
        if user:
            info(f"User:           {email}")
            info(f"Name:           {user.name}")
    else:
        error("Authentication: ✗ Not authenticated")

    print()

    # Context
    org = get_current_organization()
    project = get_current_project()

    if org:
        info(f"Current Organization:  {org}")
    else:
        info("Current Organization:  (none)")

    if project:
        info(f"Current Project:       {project}")
    else:
        info("Current Project:       (none)")

    print()

    # File locations
    from agentflow.utils.config import CONFIG_FILE
    from agentflow.storage import DATA_FILE

    info(f"Config File:    {CONFIG_FILE}")
    info(f"Data File:      {DATA_FILE}")
