# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-16

### Added
- Configuration system with interactive setup and direct database URL support
- Workspace management (create, list, switch, current)
- Session tracking (start, status, abort)
- Action logging during active sessions
- Session commit with parent-child relationship chain
- Commit history (log, show commands)
- Support for PostgreSQL and SQLite databases
- ASCII-only output for Windows compatibility
- Complete test suite (34 tests covering all entities)

### Commands
- `agentflow init` - Initialize configuration
- `agentflow config show` - Show current configuration
- `agentflow config test` - Test database connection
- `agentflow workspace create <name>` - Create a new workspace
- `agentflow workspace list` - List all workspaces
- `agentflow workspace switch <name>` - Switch to a workspace
- `agentflow workspace current` - Show current workspace
- `agentflow session start <task>` - Start a new session
- `agentflow session status` - Show current session status
- `agentflow session abort` - Abort the current session
- `agentflow session log <action>` - Log an action to the current session
- `agentflow session commit <message>` - Complete session with commit
- `agentflow log` - Show commit history
- `agentflow show <commit-id>` - Show commit details

[0.1.0]: https://github.com/Developers-Secrets-Inc/agentflow/releases/tag/v0.1.0
