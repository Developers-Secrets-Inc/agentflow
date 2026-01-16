# AgentFlow

Git-like workflow management for AI agents.

## Overview

AgentFlow is a workflow management system designed to help AI agents track and manage their work sessions in a structured, version-controlled manner similar to how Git manages code.

## Features

- **Workspace Management** - Organize work into isolated workspaces for different projects
- **Session Tracking** - Track work sessions with start/end times and status
- **Action Logging** - Log detailed actions during active sessions
- **Commit System** - Create commits to summarize completed work with parent-child relationships
- **Multiple Databases** - Support for PostgreSQL and SQLite

## Installation

```bash
pip install agentflow-cli
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install agentflow-cli
```

## Quick Start

### 1. Initialize

Interactive setup:
```bash
agentflow init
```

Or with a direct database URL:
```bash
agentflow init --db-url "postgresql://user:pass@localhost/agentflow"
```

For SQLite:
```bash
agentflow init --db-url "sqlite:///agentflow.db"
```

### 2. Create a Workspace

```bash
agentflow workspace create my-project
agentflow workspace switch my-project
```

### 3. Start a Session

```bash
agentflow session start "Implement user authentication"
```

### 4. Log Actions

```bash
agentflow session log "Created User model"
agentflow session log "Added login endpoint"
```

### 5. Check Status

```bash
agentflow session status
```

## Commands

### Configuration
- `agentflow init` - Initialize configuration
- `agentflow config show` - Show current configuration
- `agentflow config test` - Test database connection

### Workspace
- `agentflow workspace create <name>` - Create a new workspace
- `agentflow workspace list` - List all workspaces
- `agentflow workspace switch <name>` - Switch to a workspace
- `agentflow workspace current` - Show current workspace

### Session
- `agentflow session start <task>` - Start a new session
- `agentflow session status` - Show current session status
- `agentflow session abort` - Abort the current session
- `agentflow session log <action>` - Log an action to the current session

## Requirements

- Python >= 3.14
- PostgreSQL or SQLite

## Development

Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

Run tests:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check
```

Type check:

```bash
uv run mypy
```

## License

MIT
