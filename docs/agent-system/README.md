# Agent System Design - Phase 0

**Version**: 4.3
**Last Updated**: 2025-01-21
**Status**: ✅ Complete system design - Ready for DX testing (Phase 0)

## Document Purpose

This documentation explores the design and reasoning for an **agent management system** in AgentFlow. It defines what an agent is, how roles work, and how agents interact with the system through work sessions and logging.

**Status**: Design & Reasoning Phase
**Implementation**: Phase 0 (Dummy/Local Storage)
**Target**: Full system with API backend

## Quick Start

1. **[Summary](06-implementation/summary.md)** - Executive summary with key concepts
2. **[Agents](01-concepts/agents.md)** - What is an agent? Structure and lifecycle
3. **[Roles](01-concepts/roles.md)** - Role templates vs agent instances
4. **[Decisions](06-implementation/decisions.md)** - All design decisions made

## Document Structure

### 1. Concepts - Fundamentals
- **[Agents](01-concepts/agents.md)** - Core definition, structure, identity, lifecycle
- **[Roles](01-concepts/roles.md)** - Role templates, documents, vs agents
- **[Tools](01-concepts/tools.md)** - Tools integration with skills

### 2. Organization - Structure & Power
- **[Hierarchy](02-organization/hierarchy.md)** - Organizational tree (one-to-many)
- **[Permissions](02-organization/permissions.md)** - Role-based access control
- **[Trust Score](02-organization/trust-score.md)** - Rewards & punishments system

### 3. Communication - Interaction & Tracking
- **[Messages](03-communication/messages.md)** - Upward communication (agent → supervisor)
- **[Sessions](03-communication/sessions.md)** - Work sessions (start/log/stop)
- **[Logging](03-communication/logging.md)** - Activity logging and tracking

### 4. Workflow - Daily Operations
- **[Tasks](04-workflow/tasks.md)** - Task system (types, status, assignment)
- **[Pull & Generation](04-workflow/pull-generation.md)** - Role pulling and skill generation
- **[Workflows](04-workflow/workflows.md)** - Real-world workflow examples

### 5. Technical - Implementation Details
- **[Skills Format](05-technical/skills-format.md)** - Claude Code skills specification
- **[Data Models](05-technical/data-models.md)** - Data models (Phase 0)
- **[CLI Commands](05-technical/cli-commands.md)** - Complete CLI command reference

### 6. Implementation - Project Metadata
- **[Decisions](06-implementation/decisions.md)** - All Q&A decisions (12 questions resolved)
- **[Priority](06-implementation/priority.md)** - Implementation priority for Phase 0
- **[Summary](06-implementation/summary.md)** - Architecture overview, key concepts

## Key Design Principles

1. **One-to-Many Hierarchy**: Each agent has exactly one supervisor (no dotted lines)
2. **Upward Communication Only**: Agents communicate with supervisors, not peers
3. **Template vs Instance**: Roles are templates (API), agents are instances (local)
4. **Project-Scoped Tasks**: Tasks belong to projects, not globally
5. **Append-Only Logs**: Can add information, cannot modify existing data
6. **Data Preservation**: All agent data preserved on termination (audit trail)

## Version History

### v4.3 (Current)
- Hierarchy structure (one-to-many, no many-to-many)
- Log categorization (domain-specific, not DEBUG/INFO/ERROR)

### v4.2
- Tool documentation storage (in database, like roles)
- Agent termination data handling (ALL data preserved)
- Agent lifecycle commands (terminate/deactivate/activate)

### v4.1
- Trust score bounds (0-100, no glass ceiling)
- Recovery mechanism (manual Phase 0, auto Full System)
- Sessions (one active at a time, append-only logs)

### v4.0
- Communication refinement (upward only, no peer communication)
- Message vs Log distinction
- Role version management (notification, overwrite)
- Task assignment scope (project-level)

## Implementation Status

**Phase 0**: Dummy/Local Storage
- ✅ Design complete
- ✅ All decisions finalized (12 questions resolved)
- ⏳ CLI implementation (DX testing)
- ⏳ Validation and error handling

**Next**: See [Implementation Priority](06-implementation/priority.md) for MVP scope.
