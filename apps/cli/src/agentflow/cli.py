"""Main CLI application."""

import typer
from agentflow.commands import auth, org, project
from agentflow.utils.config import get_context_string
from agentflow.utils.output import info

app = typer.Typer(
    help="AgentFlow CLI - Phase 0 (Local Storage)\n\nManage organizations, projects, and development workflow."
)

# Register command groups
app.add_typer(auth.app, name="auth")
app.add_typer(org.app, name="org")
app.add_typer(project.app, name="project")


@app.command()
def version():
    """Show version information."""
    info("AgentFlow CLI v0.0.1")
    info("Phase 0: Local Storage (JSON)")
    print()
    info("Data locations:")
    from agentflow.storage import DATA_FILE
    from agentflow.utils.config import CONFIG_FILE

    info(f"  Config: {CONFIG_FILE}")
    info(f"  Data:   {DATA_FILE}")


def main():
    """Main entry point for the CLI."""
    # Get context for prompt prefix (if supported)
    context = get_context_string()

    # Run the app
    app()


if __name__ == "__main__":
    main()
