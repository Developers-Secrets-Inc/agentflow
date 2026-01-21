# Summary

## Summary

### Key Concepts

1. **Agent** (Complete Worker): Autonomous AI worker with multiple components
   - **Identity**: Unique name, code, status (active/probation/inactive/terminated)
   - **Role**: Template that defines behaviors and capabilities
   - **Tasks**: Assigned work with priorities and types
   - **Tools**: CLI utilities available for use
   - **Objective**: Self-improvement (maximize trust score)
   - **Hierarchy**: Position in organization/project tree structure

2. **Role** (Template): Stored on API, contains system prompt + Markdown documents
   - Defines job function, behaviors, and knowledge
   - Includes tool definitions (CLI tools agents can use)
   - Reusable across multiple agents
   - Documents generate Claude Code skills when pulled

3. **Hierarchy** (Tree Structure): Two-level organization
   - **Organization tree**: CTO, Architect, Tech Lead, PM
   - **Project tree**: Tech Lead → Senior Dev → Dev → QA
   - Manual definition via CLI commands
   - Supervisor identification for review workflow

4. **Tasks** (Work Units): What agents complete
   - **Types**: development, bug, review (Phase 0)
   - **Priorities**: P0 (critical) → P1 → P2 → P3 (low)
   - **Status**: backlog → assigned → in_progress → ready_review → completed
   - **Permissions**: Workers cannot mark `completed` (only managers)
   - **Auto-review**: Creates review task for supervisor when ready

5. **Permissions** (Role-Based):
   - **Manager roles** (org-level): Full permissions (create, assign, approve, cancel)
   - **Worker roles** (project-level): Limited permissions (update own status, log)
   - **Probation restrictions**: Additional limits for low trust scores

6. **Communication** (Upward Only):
   - **IMPORTANT**: Agents communicate ONLY with supervisors (no peer communication)
   - **Direct messages**: To supervisor when clarification/intervention needed
   - **Session logs**: Informational updates, progress, decisions, ideas
   - **Distinction**: Messages require response, logs are informational
   - **Rationale**: Agents with same role have same skills, supervisor coordinates

7. **Trust Score** (Self-Improvement):
   - Range: 0-100 (starts at 50)
   - Increases: Completing tasks (+1 to +5 based on priority)
   - Decreases: Rejections, bugs, delays (-2 to -10)
   - Status implications: 80+ excellent, 60-79 good, 30-49 warning, <30 probation

8. **Pull**: Fetch role from API, generate Claude Code skills
   - Downloads role documents + tool definitions
   - Creates `~/.claude/skills/<skill-name>/SKILL.md`
   - Generates both role skills (guidelines) and tool skills (CLI usage)

9. **Claude Code Skills**: Extension of Claude's capabilities
   - **Role skills**: Guidelines, conventions, methodologies
   - **Tool skills**: How to use specific CLI tools (pytest, black, etc.)
   - Format: YAML frontmatter (metadata) + Markdown (instructions)
   - Invoked via `/skill-name` or auto-loaded by Claude

10. **Session**: Temporal block of work with start/stop and duration tracking
    - Requires active pull before starting
    - Logs activities and progress
    - Immutable after stop

11. **Logging**: Record activities, progress, problems, ideas, decisions
    - Types: activity, progress, problem, decision, question, idea
    - Structured with message, context, tags
    - Linked to sessions and agents

### Architecture Diagram

```
┌─────────────────────────┐
│   AgentFlow API            │
│                             │
│  Roles (Templates)         │
│  ┌────────────────────┐   │
│  │ python-dev           │   │
│  │ ├─ desc (prompt)     │   │
│  │ ├─ docs (MD)          │   │
│  │ └─ tools (CLI)       │   │
│  └────────────────────┘   │
│                             │
│  Tasks                      │
│  ┌────────────────────┐   │
│  │ #123: development   │   │
│  │ #124: bug           │   │
│  │ #125: review        │   │
│  └────────────────────┘   │
└─────────────┬───────────────┘
              │
              │ Pull (agentflow agent pull)
              │
              ▼
┌─────────────────────────────────────────────┐
│         Local AgentFlow Database                │
│  ┌──────────────────────────────────────┐  │
│  │ Agents                                   │  │
│  │ ┌────────────────────────────────┐   │  │
│  │ │ Jean (agent-dev-001)            │   │  │
│  │ │ - role: python-dev               │   │  │
│  │ │ - trust_score: 52.5               │   │  │
│  │ │ - status: active                  │   │  │
│  │ │ - skills: [python-testing, ...]   │   │  │
│  │ └────────────────────────────────┘   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌────────────────────────────────────┐  │
│  │ Tasks                                   │  │
│  │ #123: Implement authentication       │  │
│  │ #124: Fix login bug                   │  │
│  │ #125: Review task #123               │  │
│  └────────────────────────────────────┘  │
│                                            │
│  ┌────────────────────────────────────┐  │
│  │ Messages                               │  │
│  │ From: agent-dev-001                  │  │
│  │ To:   agent-lead-001                  │  │
│  │ Type: question                        │  │
│  └────────────────────────────────────┘  │
│                                            │
│  ┌────────────────────────────────────┐  │
│  │ Hierarchy (Project Tree)               │  │
│ │ Tech Lead                               │  │
│  ├── Senior Dev                            │  │
│  │   └── Dev (Jean)                      │  │
│  └── QA                                    │  │
│  └────────────────────────────────────┘  │
└────────────┬───────────────────────────────┘
             │
             │ Generate Skills (Role Docs + Tools)
             ▼
┌─────────────────────────────────────────────┐
│           Claude Code Skills                  │
│  ~/.claude/skills/                           │
│  ┌────────────────────────────────────┐ │
│  │ Role Skills                             │ │
│  │ ├── python-testing/SKILL.md          │ │
│  │ ├── python-api/SKILL.md               │ │
│  │ └── python-async/SKILL.md             │ │
│  │                                         │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ Tool Skills                             │ │
│  │ ├── python-pytest/SKILL.md           │ │
│  │ ├── python-black/SKILL.md            │ │
│  │ └── python-mypy/SKILL.md            │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Complete Agent Lifecycle

```
1. CREATE AGENT
   agentflow agent create --name "Jean" --role "python-dev"
   → Agent created with trust_score: 50

2. PULL ROLE
   agentflow agent pull agent-dev-001
   → Downloads role definition + tools
   → Generates Claude Code skills

3. ASSIGN TASKS
   agentflow task create --title "Fix login" --assign-to agent-dev-001
   → Task appears in agent's queue

4. START SESSION
   agentflow session start --agent agent-dev-001
   → Agent begins working

5. LOG PROGRESS
   agentflow session log --type activity --message "Implementing JWT auth"
   → Progress recorded in timeline

6. ASK FOR HELP
   agentflow agent send-message --to supervisor --type question
   → Message sent to Tech Lead

7. COMPLETE TASK
   agentflow task update --task 123 --status ready_review
   → Creates review task for Tech Lead

8. TECH LEAD REVIEWS
   agentflow task approve --task 123
   → Task marked completed
   → Agent trust_score +3

9. STOP SESSION
   agentflow session stop
   → Duration calculated
```

### Review Workflow

```
Worker Agent (Jean) completes task
        ↓
Marks task "ready_review"
        ↓
System checks hierarchy tree
        ↓
Finds supervisor: Tech Lead
        ↓
Creates review task for Tech Lead
        ↓
Tech Lead reviews work
        ↓
Tech Lead approves task
        ↓
┌─────────────────────────────┐
│ Trust Score Updates           │
│                                │
│ Jean: +3 (task completed)     │
│                                │
│ Tech Lead: +1 (review done)    │
└─────────────────────────────┘
```

### Phase 0 Approach

- **Local storage** (JSON files for agents, sessions, events)
- **Role templates** (predefined in code for Phase 0, API in full system)
- **Manual operations** (user-triggered pull, session start/stop)
- **Skill generation** (automatic from role documents)
- **Basic sessions** (start/log/stop)
- **Structured logs** (message + optional context)

### Next Steps

1. ✅ Define role templates (system prompts + documents)
2. ✅ Implement role management CLI commands
3. ✅ Implement agent management with role assignment
4. ✅ Implement pull mechanism with skill generation
5. ✅ Implement session management (start/log/stop)
6. ✅ Add validation and error handling
7. ✅ Write tests for core functionality
8. ✅ Document CLI usage examples

---

**Document Version**: 4.3
**Last Updated**: 2025-01-21
**Status**: ✅ Updated with hierarchy structure (one-to-many) and log categorization (domain-specific) - Ready for DX testing (Phase 0)

### Key Changes in v4.3:
- **Hierarchy Structure**: One-to-many only (no many-to-many, no dotted line relationships)
- **Hierarchy Rules**: Clear constraints on allowed/forbidden organizational structures
- **Multiple Supervisors**: NOT supported - each agent has exactly one supervisor
- **Log Categories**: Domain-specific names (status, decision, issue) not DEBUG/INFO/ERROR
- **Log Filtering**: Filter by semantic category, not system log level
- **Rationale**: Simplicity, clarity, unambiguous chain of command for agents

### Key Changes in v4.2:
- **Tool Documentation**: Each tool has Markdown documentation stored in database (like roles)
- **Tool Management**: CLI commands for creating/updating tools with documentation
- **Internal vs External Tools**: Distinction between pre-defined (pytest) and custom (excel-analyzer)
- **Agent Termination**: ALL data preserved (tasks, sessions, logs, messages, skills)
- **Agent Lifecycle**: Added terminate/deactivate/activate commands with data retention policies
- **Task Reassignment**: Manual reassignment (not automatic) when agent terminated

### Key Changes in v4.1:
- **Trust Score Bounds**: Floor at 0, ceiling at 100, no glass ceiling
- **Recovery Mechanism**: Phase 0 (manual by manager) vs Full System (automatic via task completion)
- **Training Tasks**: Removed - agents learn by doing actual work, not artificial exercises
- **Sessions**: One session active at a time (even across multiple projects)
- **Session Mutability**: Immutable after stop, but can append additional logs
- **Logs**: Append-only modification (can add info, cannot modify existing data)
- **Status Thresholds**: Updated ranges (90-100 Excellent, 70-89 Very Good, 50-69 Neutral, etc.)

### Key Changes in v4.0:
- **Communication**: Clarified that agents communicate ONLY with supervisors (no peer communication)
- **Message vs Log**: Clear distinction - messages require response, logs are informational
- **Role Version Management**: Added notification system for outdated roles, skill overwrite behavior
- **Task Assignment**: Clarified project-level assignment (not global)
- **Message Priority**: Added implicit priority for hierarchical messages
- **Removed**: "Help another agent" from trust score increases (no peer interaction)
