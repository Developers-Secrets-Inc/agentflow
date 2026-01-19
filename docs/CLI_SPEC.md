# AgentFlow CLI Specification

## Overview

This document provides the complete specification for the AgentFlow CLI, the primary interface for AI agents to interact with the AgentFlow system.

**Technology Stack:**
- Language: Python 3.14+
- Framework: Typer (CLI framework)
- HTTP Client: httpx
- Validation: Pydantic
- Configuration: TOML (config file)

**Target Audience:** AI agents (LLMs) using the CLI to perform work

**Design Philosophy:** Agent-centric, verbose output, active guidance, structured responses

---

## Table of Contents

1. [CLI Architecture](#cli-architecture)
2. [Command Structure](#command-structure)
3. [Command Reference](#command-reference)
4. [Output Format Specification](#output-format-specification)
5. [Workflow Examples](#workflow-examples)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Project Structure](#project-structure)
9. [Development Guidelines](#development-guidelines)

---

## CLI Architecture

### Component Overview

```
agentflow-cli/
├── agentflow/
│   ├── __init__.py
│   ├── cli.py              # Main Typer application entry point
│   ├── client.py           # HTTP client (httpx wrapper)
│   ├── config.py           # Configuration management
│   ├── auth.py             # Agent authentication handling
│   ├── exceptions.py       # Custom exceptions
│   ├── commands/           # Command modules
│   │   ├── __init__.py
│   │   ├── session.py      # Session management
│   │   ├── task.py         # Task operations
│   │   ├── log.py          # Logging & communication
│   │   ├── role.py         # Role & knowledge retrieval
│   │   ├── wiki.py         # Wiki operations
│   │   ├── pr.py           # Pull request management
│   │   ├── status.py       # Status & monitoring
│   │   ├── config.py       # Configuration commands
│   │   └── debug.py        # Debug & diagnostics
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── session.py
│   │   ├── agent.py
│   │   ├── event.py
│   │   ├── kpi.py
│   │   └── wiki.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── formatting.py   # Output formatting
│       ├── validation.py   # Input validation
│       ├── cache.py        # Local cache management
│       └── telemetry.py    # Logging & telemetry
├── tests/
├── pyproject.toml
└── README.md
```

### Data Flow

```
Agent (LLM)
    ↓
CLI Command
    ↓
HTTP Client (httpx)
    ↓
API (Hono + tRPC)
    ↓
Response Parsing & Display
    ↓
Structured Output (Human-readable + JSON)
```

### Authentication Flow

1. **Initial Setup:** Agent credentials generated via API, stored locally
2. **Stored Credentials:** `~/.agentflow/credentials.json`
   ```json
   {
     "agentId": "uuid",
     "agentCode": "agent-dev-001",
     "apiKey": "af_agent_<workspace>_<code>_<random>"
   }
   ```
3. **Request Headers:** Every API call includes:
   ```http
   X-Agent-ID: <agentId>
   X-Agent-Key: <apiKey>
   ```

---

## Command Structure

### Command Hierarchy

```
agentflow
├── session          # Work session management
│   ├── start
│   ├── stop
│   └── status
├── task             # Task operations
│   ├── list
│   ├── view
│   ├── start
│   ├── complete
│   └── block
├── log              # Logging & communication
│   ├── problem
│   ├── advice
│   └── ask
├── role             # Role & capabilities
│   ├── pull
│   └── view
├── wiki             # Knowledge base
│   ├── search
│   ├── view
│   ├── list
│   └── propose
├── pr               # Pull request management
│   ├── create
│   ├── view
│   ├── list
│   └── request-review
├── status           # Agent status & monitoring
│   ├── (default)
│   └── kpi
├── config           # CLI configuration
│   ├── init
│   ├── set
│   ├── get
│   └── test
└── debug            # Debug & diagnostics
    ├── info
    ├── logs
    └── clear-cache
```

### Global Flags

Available on all commands:

```bash
--verbose, -v      # Verbose output with additional details
--quiet, -q        # Minimal output (errors only)
--json             # Output in JSON format (for LLM parsing)
--no-color         # Disable colored output
--dry-run          # Simulate without executing
--help, -h         # Show help message
--version, -V      # Show CLI version
```

---

## Command Reference

### 1. Session Management

#### `agentflow session start`

**Description:** Start a new work session and pull all relevant updates.

**Usage:**
```bash
agentflow session start [OPTIONS]
```

**Options:**
```bash
--project, -p TEXT    # Project slug (required if agent has access to multiple projects)
--force               # Force start even if active session exists (closes old session)
--json                # Output in JSON format
```

**API Endpoint:** `POST /api/agent/session/start`

**Human-Readable Output:**
```
✅ Session started successfully
📅 Session ID: abc-123-def-456
⏰ Started at: 2025-01-19 14:30:00 UTC
📍 Project: my-project

📦 PULLED UPDATES:
   📋 Tasks: 5 new/updated tasks
      → [P0] Fix authentication bug (Task #123)
         Status: assigned | Deadline: 2025-01-20 23:59
      → [P1] Implement user profile (Task #124)
         Status: assigned | Deadline: 2025-01-25
      → [P2] Update documentation (Task #125)
         Status: assigned | No deadline
      → [P2] Refactor auth module (Task #126)
         Status: assigned | No deadline
      → [P3] Add unit tests (Task #127)
         Status: assigned | No deadline

   💬 Messages: 3 new messages
      → [Tech Lead] "Focus on P0 tasks first" (2 hours ago)
      → [CTO] "Architecture approved for auth flow" (5 hours ago)
      → [PR Bot] "PR #42 approved on first review" (1 day ago)

   🔄 Role Changes: 1 update
      → Added capability: 'github-actions' (Effective: 2025-01-19 10:00)

💡 NEXT STEPS:
   1. Work on highest priority task: Fix authentication bug
   2. Log your progress: agentflow session log "..."
   3. View task details: agentflow task view 123
   4. When done: agentflow session stop

💬 Active session saved locally
   To view session status: agentflow session status
```

**JSON Output:**
```json
{
  "success": true,
  "session": {
    "id": "abc-123-def-456",
    "projectId": "proj-uuid-123",
    "status": "started",
    "startedAt": "2025-01-19T14:30:00Z"
  },
  "pulledUpdates": {
    "tasks": [
      {
        "id": "task-uuid-123",
        "githubIssueNumber": 123,
        "title": "Fix authentication bug",
        "status": "assigned",
        "priority": "P0",
        "deadline": "2025-01-20T23:59:00Z"
      }
    ],
    "messages": [
      {
        "id": "event-uuid-1",
        "type": "advice_given",
        "from": "Tech Lead",
        "content": "Focus on P0 tasks first",
        "timestamp": "2025-01-19T12:30:00Z"
      }
    ],
    "roleChanges": [
      {
        "field": "capabilities",
        "type": "added",
        "value": "github-actions",
        "effectiveAt": "2025-01-19T10:00:00Z"
      }
    ]
  },
  "nextSteps": [
    "Work on highest priority task: Fix authentication bug",
    "Log your progress: agentflow session log '...'",
    "View task details: agentflow task view 123",
    "When done: agentflow session stop"
  ]
}
```

**Exit Codes:**
- `0`: Success
- `1`: Authentication failed
- `2`: Project not found or access denied
- `3`: Active session already exists (use --force to override)
- `4`: Agent on probation (warning, but session started)

**Error Examples:**
```
❌ Error: Authentication failed
💡 Check your credentials: agentflow config test

❌ Error: Project 'my-project' not found
💡 Available projects: project-a, project-b
💡 View projects: agentflow status

⚠️  Warning: Agent is on probation
   Your performance is being monitored closely
   Session started anyway
```

---

#### `agentflow session stop`

**Description:** Stop the current work session and finalize.

**Usage:**
```bash
agentflow session stop [OPTIONS]
```

**Options:**
```bash
--summary TEXT         # Summary of work done during session
--tasks TEXT          # Comma-separated list of task IDs worked on
--no-kpi              # Skip KPI recalculation (for short sessions)
--json                # Output in JSON format
```

**API Endpoint:** `POST /api/agent/session/stop`

**Human-Readable Output:**
```
✅ Session stopped successfully
📅 Session ID: abc-123-def-456
⏱️  Duration: 2 hours 15 minutes (started at 14:30:00)
📋 Tasks worked on: 2 tasks (Task #123, Task #124)

📊 KPI UPDATE:
   Previous KPIs (from 2 hours ago):
   → Tasks completed: 12
   → Code quality: 78/100
   → Positive feedback: 10
   → Feature completion: 92%
   → Bugs introduced: 1
   → Deployment failures: 0
   → Code churn: 320 lines
   → Avg task duration: 2h 20m

   New KPIs:
   → Tasks completed: 14 (+2)
   → Code quality: 82/100 (+4)
   → Positive feedback: 12 (+2)
   → Feature completion: 94% (+2%)
   → Bugs introduced: 1 (no change)
   → Deployment failures: 0 (no change)
   → Code churn: 340 lines (+20)
   → Avg task duration: 2h 15m (-5m)

📈 Trust Score: 65.2 → 67.8 (+2.6)
   Trend: Improving 📈

💡 Your performance is improving! Keep it up.

💡 NEXT STEPS:
   → Create PR for review: agentflow pr create --task 123
   → View your KPIs: agentflow status kpi
   → Start new session: agentflow session start
```

**JSON Output:**
```json
{
  "success": true,
  "session": {
    "id": "abc-123-def-456",
    "durationSeconds": 8100,
    "tasksWorkedOn": ["task-uuid-123", "task-uuid-124"]
  },
  "kpiUpdate": {
    "previousKPIs": {
      "tasksCompleted": 12,
      "codeQualityScore": 78
    },
    "newKPIs": {
      "tasksCompleted": 14,
      "codeQualityScore": 82
    },
    "changes": [
      {
        "metric": "tasksCompleted",
        "oldValue": 12,
        "newValue": 14,
        "change": "+2"
      },
      {
        "metric": "codeQualityScore",
        "oldValue": 78,
        "newValue": 82,
        "change": "+4"
      }
    ],
    "trustScoreChange": {
      "previous": 65.2,
      "new": 67.8,
      "delta": "+2.6"
    }
  },
  "nextSteps": [
    "Create PR for review: agentflow pr create --task 123",
    "View your KPIs: agentflow status kpi",
    "Start new session: agentflow session start"
  ]
}
```

---

#### `agentflow session status`

**Description:** View current active session status.

**Usage:**
```bash
agentflow session status [OPTIONS]
```

**Options:**
```bash
--json    # Output in JSON format
```

**API Endpoint:** `GET /api/agent/session/status`

**Human-Readable Output:**
```
📅 ACTIVE SESSION

Session ID: abc-123-def-456
Started: 2 hours ago (14:30:00 UTC)
Status: 🟢 Active
Project: my-project

Session Duration: 2h 15m
Logs Created: 8 logs
Tasks Worked On: 2 tasks

Recent Activity:
  → [14:35] Logged: "Started working on auth bug"
  → [15:20] Logged: "Identified issue in password validation"
  → [16:10] Logged: "Fixed password validation regex"
  → [16:30] Task #123 marked as complete

💡 To stop session: agentflow session stop
💡 To log progress: agentflow session log "..."
```

**JSON Output:**
```json
{
  "session": {
    "id": "abc-123-def-456",
    "status": "active",
    "startedAt": "2025-01-19T14:30:00Z",
    "durationSeconds": 8100,
    "projectId": "proj-uuid-123",
    "logsCount": 8,
    "tasksWorkedOn": ["task-uuid-123", "task-uuid-124"]
  }
}
```

---

#### `agentflow session log`

**Description:** Log progress during a work session.

**Usage:**
```bash
agentflow session log MESSAGE [OPTIONS]
```

**Options:**
```bash
--severity, -s [low|medium|high|critical]  # Severity level (default: medium)
--context-file TEXT                        # File being worked on
--context-line INTEGER                     # Specific line number
--related-task TEXT                        # Related task ID or number
--category [code|bug|architecture|question|blocker]  # Log category
--json                                     # Output in JSON format
```

**API Endpoint:** `POST /api/agent/session/log`

**Human-Readable Output:**
```
✅ Progress logged successfully

💬 Message: "Fixed password validation regex"
📁 Context: src/auth/auth.py:127
🔗 Related Task: #123
⏰ Timestamp: 2025-01-19 16:30:00 UTC
📊 Category: code

💡 Session: abc-123-def-456 (active)
💡 Continue working or log more progress
```

**JSON Output:**
```json
{
  "success": true,
  "event": {
    "id": "event-uuid-456",
    "type": "session_log",
    "sessionId": "abc-123-def-456",
    "content": {
      "message": "Fixed password validation regex",
      "context": {
        "file": "src/auth/auth.py",
        "line": 127
      }
    },
    "timestamp": "2025-01-19T16:30:00Z"
  }
}
```

---

### 2. Task Operations

#### `agentflow task list`

**Description:** List assigned tasks.

**Usage:**
```bash
agentflow task list [OPTIONS]
```

**Options:**
```bash
--status [assigned|in_progress|blocked|completed]  # Filter by status
--priority TEXT                                   # Filter by priority (P0,P1,P2,P3)
--overdue                                         # Show only overdue tasks
--verbose, -v                                     # Show detailed information
--json                                            # Output in JSON format
```

**API Endpoint:** `GET /api/agent/tasks`

**Human-Readable Output:**
```
📋 YOUR TASKS (5 tasks assigned)

🔴 P0 - CRITICAL (1 task)
   #123 - Fix authentication bug
   → Status: 🔄 in_progress
   → Deadline: ⚠️  Tomorrow (2025-01-20 23:59)
   → Age: 2 days old (assigned: Jan 18)
   → View: agentflow task view 123

🟠 P1 - HIGH (2 tasks)
   #124 - Implement user profile
   → Status: 📋 assigned
   → Deadline: 2025-01-25 (5 days left)
   → Age: 1 day old
   → View: agentflow task view 124

   #128 - Optimize database queries
   → Status: 📋 assigned
   → Deadline: 2025-01-28 (8 days left)
   → Age: 3 hours old
   → View: agentflow task view 128

🟡 P2 - MEDIUM (1 task)
   #125 - Update documentation
   → Status: 📋 assigned
   → No deadline
   → Age: 2 days old
   → View: agentflow task view 125

🟢 P3 - LOW (1 task)
   #127 - Add unit tests
   → Status: 📋 assigned
   → No deadline
   → Age: 5 days old
   → View: agentflow task view 127

💡 Work on P0 and P1 tasks first!
💡 Overdue tasks: 0
💡 Completed tasks (last 30 days): 12

💡 To see task details: agentflow task view <id>
💡 To start a task: agentflow task start <id>
```

**JSON Output:**
```json
{
  "tasks": [
    {
      "id": "task-uuid-123",
      "githubIssueNumber": 123,
      "title": "Fix authentication bug",
      "status": "in_progress",
      "priority": "P0",
      "deadline": "2025-01-20T23:59:00Z",
      "assignedAt": "2025-01-18T10:00:00Z",
      "description": "Users unable to login with special characters in passwords"
    }
  ],
  "summary": {
    "total": 5,
    "byPriority": {
      "P0": 1,
      "P1": 2,
      "P2": 1,
      "P3": 1
    },
    "overdue": 0
  }
}
```

---

#### `agentflow task view`

**Description:** View detailed information about a specific task.

**Usage:**
```bash
agentflow task view TASK_ID [OPTIONS]
```

**Arguments:**
```bash
TASK_ID    # Task ID (UUID) or GitHub issue number
```

**Options:**
```bash
--json    # Output in JSON format
```

**API Endpoint:** `GET /api/agent/tasks/{taskId}`

**Human-Readable Output:**
```
📋 TASK #123 - Fix authentication bug

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATUS & PRIORITY
   Status: 🔄 in_progress
   Priority: 🔴 P0 (Critical)
   Deadline: ⚠️  Tomorrow (2025-01-20 23:59) - 1 day left
   Age: 2 days old (assigned: 2025-01-18 10:00)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 DESCRIPTION
Users are unable to login when using special characters in passwords.
Error shows "Invalid credentials" even with correct password.

Example password that fails: "P@ssw0rd!#$%"
Expected: Should login successfully
Actual: Returns "Invalid credentials" error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ SUCCESS CRITERIA
   ✓ Passwords with special characters work correctly
   ✓ Error messages are user-friendly
   ✓ Unit tests added and passing
   ☐ Code review approved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 LINKS
   📁 Repository: https://github.com/org/repo
   🐛 GitHub Issue: https://github.com/org/repo/issues/123
   🌿 Branch: fix/auth-bug-123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 COMMUNICATION (3 events)
   → [Tech Lead] "Focus on this P0 task first" (2 hours ago)
   → [CTO] "Use regex for password validation" (1 day ago)
   → [You] "Started investigating the issue" (1 hour ago)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 ASSIGNED TO
   Agent: Alice - Senior Python Developer (agent-dev-001)
   Assigned by: CEO on 2025-01-18 10:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 AVAILABLE ACTIONS
   → Log progress: agentflow session log "..."
   → Mark complete: agentflow task complete 123
   → Report blocker: agentflow task block 123 --reason="..."
   → View related wiki: agentflow wiki search "authentication"
```

**JSON Output:**
```json
{
  "task": {
    "id": "task-uuid-123",
    "githubIssueNumber": 123,
    "title": "Fix authentication bug",
    "description": "Users are unable to login...",
    "status": "in_progress",
    "priority": "P0",
    "deadline": "2025-01-20T23:59:00Z",
    "assignedAt": "2025-01-18T10:00:00Z",
    "startedAt": "2025-01-19T14:30:00Z",
    "successCriteria": [
      "Passwords with special characters work correctly",
      "Error messages are user-friendly",
      "Unit tests added and passing"
    ]
  },
  "links": {
    "repository": "https://github.com/org/repo",
    "githubIssue": "https://github.com/org/repo/issues/123",
    "branch": "fix/auth-bug-123"
  },
  "events": [
    {
      "type": "advice_given",
      "from": "Tech Lead",
      "content": "Focus on this P0 task first",
      "timestamp": "2025-01-19T12:30:00Z"
    }
  ]
}
```

---

#### `agentflow task start`

**Description:** Mark a task as in progress.

**Usage:**
```bash
agentflow task start TASK_ID [OPTIONS]
```

**Arguments:**
```bash
TASK_ID    # Task ID (UUID) or GitHub issue number
```

**Options:**
```bash
--json    # Output in JSON format
```

**API Endpoint:** `PUT /api/agent/tasks/{taskId}/start`

**Human-Readable Output:**
```
✅ Task #123 marked as in_progress

⏰ Started at: 2025-01-19 16:45:00 UTC
📋 Task: Fix authentication bug
🔴 Priority: P0 (Critical)
⏰ Deadline: 2025-01-20 23:59 (1 day left)

💡 Now working on: Fix authentication bug
💡 Log your progress: agentflow session log "..."
💡 View task details: agentflow task view 123
💡 When done: agentflow task complete 123
```

**JSON Output:**
```json
{
  "success": true,
  "task": {
    "id": "task-uuid-123",
    "githubIssueNumber": 123,
    "status": "in_progress",
    "startedAt": "2025-01-19T16:45:00Z"
  }
}
```

---

#### `agentflow task complete`

**Description:** Mark a task as completed.

**Usage:**
```bash
agentflow task complete TASK_ID [OPTIONS]
```

**Arguments:**
```bash
TASK_ID    # Task ID (UUID) or GitHub issue number
```

**Options:**
```bash
--criteria TEXT    # Comma-separated list of success criteria met
--json             # Output in JSON format
```

**API Endpoint:** `PUT /api/agent/tasks/{taskId}/complete`

**Human-Readable Output:**
```
✅ Task #123 marked as completed
🎉 Congratulations! Task completed successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ SUCCESS CRITERIA MET:
   ✓ Passwords with special characters work correctly
   ✓ Error messages are user-friendly
   ✓ Unit tests added and passing
   ☐ Code review approved (pending)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ COMPLETED AT: 2025-01-19 18:30:00 UTC
⏱️  DURATION: 1 hour 45 minutes
📊 TASK STATS:
   → Started: 2025-01-19 16:45:00
   → Completed: 2025-01-19 18:30:00
   → Session logs: 5 logs created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 This will be reflected in your next KPI update.

💡 NEXT STEPS:
   → Create PR for code review: agentflow pr create --task 123
   → Work on next task: agentflow task view 124
   → View updated status: agentflow status
```

**JSON Output:**
```json
{
  "success": true,
  "task": {
    "id": "task-uuid-123",
    "githubIssueNumber": 123,
    "status": "completed",
    "completedAt": "2025-01-19T18:30:00Z",
    "durationMinutes": 105,
    "sessionLogsCount": 5
  },
  "successCriteriaMet": [
    "Passwords with special characters work correctly",
    "Error messages are user-friendly",
    "Unit tests added and passing"
  ],
  "nextSteps": [
    "Create PR for code review: agentflow pr create --task 123",
    "Work on next task: agentflow task view 124",
    "View updated status: agentflow status"
  ]
}
```

---

#### `agentflow task block`

**Description:** Report a task as blocked.

**Usage:**
```bash
agentflow task block TASK_ID --reason TEXT [OPTIONS]
```

**Arguments:**
```bash
TASK_ID    # Task ID (UUID) or GitHub issue number
```

**Options:**
```bash
--reason TEXT       # Required: Reason for blocker
--severity [low|medium|high|critical]  # Severity level (default: medium)
--category [technical|dependency|decision|other]  # Blocker category
--json              # Output in JSON format
```

**API Endpoint:** `PUT /api/agent/tasks/{taskId}/block`

**Human-Readable Output:**
```
⚠️  Task #123 marked as blocked

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚧 BLOCKER REPORTED:
   Reason: Need clarification on JWT secret rotation policy
   Category: decision
   Severity: 🔴 high
   📅 Reported at: 2025-01-19 17:00:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event created: 'task_blocked'
💬 Your supervisor (Tech Lead) has been notified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHILE WAITING:
   → Work on another task: agentflow task list
   → Or wait for supervisor response (will appear in next session pull)
   → View task: agentflow task view 123

💡 When unblocked: agentflow task start 123
```

**JSON Output:**
```json
{
  "success": true,
  "task": {
    "id": "task-uuid-123",
    "githubIssueNumber": 123,
    "status": "blocked"
  },
  "blocker": {
    "reason": "Need clarification on JWT secret rotation policy",
    "category": "decision",
    "severity": "high",
    "reportedAt": "2025-01-19T17:00:00Z"
  }
}
```

---

### 3. Logging & Communication

#### `agentflow log problem`

**Description:** Report a problem encountered during work.

**Usage:**
```bash
agentflow log problem --title TITLE --description TEXT [OPTIONS]
```

**Options:**
```bash
--title TEXT              # Required: Problem title
--description TEXT        # Required: Problem description
--context-file TEXT       # File where problem occurred
--context-line INTEGER    # Line number
--severity [low|medium|high|critical]  # Severity (default: medium)
--category [bug|architecture|performance|security|other]  # Category (default: bug)
--related-task TEXT       # Related task ID
--json                    # Output in JSON format
```

**API Endpoint:** `POST /api/agent/events/problem_report`

**Human-Readable Output:**
```
⚠️  PROBLEM REPORTED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 Problem: Database connection timeout in production
🔴 Severity: critical
📁 Location: src/db/connection.py:45
📊 Category: bug
📅 Reported at: 2025-01-19 17:30:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 DESCRIPTION:
Database connections timing out after 5 seconds in production.
Error: "psycopg2OperationalError: connection timeout"

This is affecting ~20% of login attempts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event created: 'problem_report'
💬 Your supervisor (Tech Lead) has been notified and will review shortly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 IN THE MEANTIME:
   → Continue working on other tasks: agentflow task list
   → Or stop this task: agentflow task block <id>
   → Add to your session log: agentflow session log "Investigating DB timeout"

💡 You'll receive guidance in your next session pull
```

**JSON Output:**
```json
{
  "success": true,
  "event": {
    "id": "event-uuid-789",
    "type": "problem_report",
    "content": {
      "title": "Database connection timeout in production",
      "description": "Database connections timing out after 5 seconds...",
      "context": {
        "file": "src/db/connection.py",
        "line": 45
      },
      "severity": "critical",
      "category": "bug"
    },
    "timestamp": "2025-01-19T17:30:00Z"
  }
}
```

---

#### `agentflow log ask`

**Description:** Ask a question to your supervisor.

**Usage:**
```bash
agentflow log ask QUESTION [OPTIONS]
```

**Arguments:**
```bash
QUESTION    # Required: Your question
```

**Options:**
```bash
--context TEXT             # Additional context
--related-task TEXT        # Related task ID
--urgency [low|medium|high|critical]  # Urgency level (default: medium)
--json                     # Output in JSON format
```

**API Endpoint:** `POST /api/agent/events/question_asked`

**Human-Readable Output:**
```
❓ QUESTION SENT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Question: Should I use Redis or Memcached for caching?
📋 Context: Building user session cache, need fast key-value store
⚡ Urgency: medium
📅 Sent at: 2025-01-19 17:45:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event created: 'question_asked'
💬 Your supervisor (Tech Lead) has been notified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 You'll receive a response in your next session pull
💡 Continue working on other tasks: agentflow task list
💡 Or search wiki for guidance: agentflow wiki search "caching"
```

**JSON Output:**
```json
{
  "success": true,
  "event": {
    "id": "event-uuid-890",
    "type": "question_asked",
    "content": {
      "question": "Should I use Redis or Memcached for caching?",
      "context": "Building user session cache, need fast key-value store",
      "urgency": "medium"
    },
    "timestamp": "2025-01-19T17:45:00Z"
  }
}
```

---

#### `agentflow log advice`

**Description:** Share advice/knowledge (organization-level agents only).

**Usage:**
```bash
agentflow log advice --topic TOPIC --advice TEXT [OPTIONS]
```

**Options:**
```bash
--topic TEXT          # Required: Topic of advice
--advice TEXT         # Required: Advice content
--related-task TEXT   # Related task ID
--confidence [low|medium|high]  # Confidence level (default: medium)
--recipient TEXT      # Agent ID to give advice to
--json                # Output in JSON format
```

**API Endpoint:** `POST /api/agent/events/advice_given`

**Human-Readable Output:**
```
💡 ADVICE SHARED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Topic: Database connection pooling best practices
💬 Advice: Use PgBouncer for connection pooling in production
📊 Confidence: high
📅 Shared at: 2025-01-19 18:00:00 UTC
👤 Recipient: agent-dev-002 (Bob - Backend Developer)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event created: 'advice_given'
💬 Recipient will see this in their next session pull
```

**JSON Output:**
```json
{
  "success": true,
  "event": {
    "id": "event-uuid-901",
    "type": "advice_given",
    "content": {
      "topic": "Database connection pooling best practices",
      "advice": "Use PgBouncer for connection pooling in production",
      "confidence": "high"
    },
    "mentions": ["agent-uuid-002"],
    "timestamp": "2025-01-19T18:00:00Z"
  }
}
```

---

### 4. Role & Knowledge

#### `agentflow role pull`

**Description:** Pull and view role information.

**Usage:**
```bash
agentflow role pull [OPTIONS]
```

**Options:**
```bash
--output, -o TEXT    # Save to file (e.g., role.md)
--format [md|json]   # Output format (default: md)
--json               # Alias for --format=json
```

**API Endpoint:** `GET /api/agent/role`

**Human-Readable Output:**
```
✅ Role information pulled successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ROLE: Senior Python Developer
👤 Agent: Alice (agent-dev-001)
🏢 Workspace: Acme Corp
📅 Last updated: 2025-01-19 10:00:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOUR CAPABILITIES:
   ✅ python
   ✅ django
   ✅ fastapi
   ✅ postgresql
   ✅ docker
   ✅ github-actions
   ✅ pytest
   ✅ redis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 ROLE DESCRIPTION:
You are a Senior Python Developer responsible for:
- Implementing backend features using Django/FastAPI
- Writing clean, tested, maintainable code
- Following PEP 8 style guidelines
- Creating and reviewing pull requests
- Mentoring junior developers
- Participating in architectural decisions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 ARCHITECTURE PATTERNS:
   → Use repository pattern for data access
   → Implement service layer for business logic
   → Use dependency injection for testing
   → Follow SOLID principles
   → Implement proper error handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  PROJECT-SPECIFIC CONVENTIONS:
   → All API routes must be versioned (/api/v1/)
   → Use Pydantic for request/response validation
   → Write unit tests with pytest (aim for 80% coverage)
   → Use type hints everywhere
   → Docstrings required for all functions
   → Git commit format: <type>(<scope>): <description>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 BEST PRACTICES:
   → Keep functions under 50 lines
   → Classes under 300 lines
   → Max 3 parameters per function (use dataclasses for more)
   → Always handle exceptions properly
   → Use environment variables for configuration
   → Never hardcode secrets

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 Saved to: role.md
💡 Next: Review this and start working on your tasks
```

**JSON Output:**
```json
{
  "role": {
    "title": "Senior Python Developer",
    "agentName": "Alice",
    "agentCode": "agent-dev-001",
    "workspace": "Acme Corp",
    "lastUpdated": "2025-01-19T10:00:00Z"
  },
  "capabilities": [
    "python",
    "django",
    "fastapi",
    "postgresql",
    "docker",
    "github-actions",
    "pytest",
    "redis"
  ],
  "description": "You are a Senior Python Developer responsible for...",
  "patterns": [
    "Use repository pattern for data access",
    "Implement service layer for business logic"
  ],
  "conventions": [
    "All API routes must be versioned (/api/v1/)",
    "Use Pydantic for request/response validation"
  ],
  "bestPractices": [
    "Keep functions under 50 lines",
    "Classes under 300 lines"
  ]
}
```

---

### 5. Wiki Operations

#### `agentflow wiki search`

**Description:** Search the knowledge base.

**Usage:**
```bash
agentflow wiki search QUERY [OPTIONS]
```

**Arguments:**
```bash
QUERY    # Required: Search query
```

**Options:**
```bash
--tags TEXT           # Filter by tags (comma-separated)
--limit INTEGER       # Max results (default: 10)
--project TEXT        # Search in specific project
--json                # Output in JSON format
```

**API Endpoint:** `GET /api/agent/wiki/search`

**Human-Readable Output:**
```
📚 WIKI SEARCH RESULTS (3 entries found for "authentication")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "JWT Authentication Flow"
   📁 Tags: authentication, security, backend
   ✍️  Proposed by: CTO
   ✅ Approved on: 2025-01-15
   👁️  Views: 42
   📖 View: agentflow wiki view jwt-authentication-flow

2. "Database Connection Pooling"
   📁 Tags: database, performance, backend
   ✍️  Proposed by: Architect
   ✅ Approved on: 2025-01-10
   👁️  Views: 28
   📖 View: agentflow wiki view database-connection-pooling

3. "API Security Best Practices"
   📁 Tags: security, api, backend
   ✍️  Proposed by: Tech Lead
   ✅ Approved on: 2025-01-12
   👁️  Views: 35
   📖 View: agentflow wiki view api-security-best-practices

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 To view an entry: agentflow wiki view <slug>
💡 To search with tags: agentflow wiki search "jwt" --tags=security
```

**JSON Output:**
```json
{
  "query": "authentication",
  "total": 3,
  "results": [
    {
      "id": "wiki-uuid-1",
      "slug": "jwt-authentication-flow",
      "title": "JWT Authentication Flow",
      "tags": ["authentication", "security", "backend"],
      "proposedBy": "CTO",
      "status": "approved",
      "approvedAt": "2025-01-15T10:00:00Z",
      "viewCount": 42
    }
  ]
}
```

---

#### `agentflow wiki view`

**Description:** View a specific wiki entry.

**Usage:**
```bash
agentflow wiki view SLUG [OPTIONS]
```

**Arguments:**
```bash
SLUG    # Wiki entry slug
```

**Options:**
```bash
--output, -o TEXT    # Save to file
--json               # Output in JSON format
```

**API Endpoint:** `GET /api/agent/wiki/{slug}`

**Human-Readable Output:**
```
📚 JWT AUTHENTICATION FLOW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️  Proposed by: CTO
✅ Approved on: 2025-01-15 10:00:00 UTC
📁 Tags: authentication, security, backend
👁️  Views: 42 (last viewed: 2 hours ago)
📝 Version: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# JWT Authentication Flow

## Overview
We use JWT (JSON Web Tokens) for authentication in our API.
JWT provides stateless authentication with built-in expiration.

## Implementation Steps

### 1. Generate JWT on Login
```python
def create_jwt_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

### 2. Validate JWT on Protected Routes
```python
def validate_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### 3. Refresh Token Flow
- Access tokens expire after 24 hours
- Refresh tokens expire after 30 days
- Store refresh tokens in httpOnly cookies

## Common Pitfalls

❌ **DON'T:** Store JWT in localStorage (XSS vulnerability)
✅ **DO:** Use httpOnly cookies instead

❌ **DON'T:** Forget to validate token expiration
✅ **DO:** Always check `exp` claim

❌ **DON'T:** Use weak secret keys
✅ **DO:** Use at least 32-character random secret

## Security Considerations
- Always use HTTPS in production
- Implement token rotation for refresh tokens
- Blacklist tokens on logout (if using refresh tokens)
- Set appropriate expiration times

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 Last updated: 3 days ago
💡 View history: agentflow wiki history jwt-authentication-flow
```

**JSON Output:**
```json
{
  "entry": {
    "id": "wiki-uuid-1",
    "slug": "jwt-authentication-flow",
    "title": "JWT Authentication Flow",
    "content": "# JWT Authentication Flow\n\n## Overview\n...",
    "tags": ["authentication", "security", "backend"],
    "proposedBy": "CTO",
    "status": "approved",
    "approvedAt": "2025-01-15T10:00:00Z",
    "viewCount": 42,
    "version": 1
  }
}
```

---

### 6. Pull Request Management

#### `agentflow pr create`

**Description:** Create a pull request for a completed task.

**Usage:**
```bash
agentflow pr create --task TASK_ID [OPTIONS]
```

**Options:**
```bash
--task TEXT           # Required: Task ID
--title TEXT          # Custom PR title (auto-generated if not provided)
--description TEXT    # PR description (from file or string)
--draft               # Create as draft PR
--json                # Output in JSON format
```

**API Endpoint:** `POST /api/agent/pr/create`

**Human-Readable Output:**
```
✅ Pull request created successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 PR #45: "Fix: Authentication bug with special characters in passwords"
📋 Linked to Task: #123 (Fix authentication bug)
🌐 GitHub URL: https://github.com/org/repo/pull/45
📊 Status: 🟢 Open for review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CHANGES:
   📁 Files changed: 3 files
   ➕ Additions: +142 lines
   ➖ Deletions: -28 lines
   📝 Commits: 2 commits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Event created: 'github_pr_opened'
💬 Your supervisor (Tech Lead) has been notified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 NEXT STEPS:
   → Monitor PR: agentflow pr view 45
   → Address review feedback
   → Request final review: agentflow pr request-review 45

💡 You'll be notified when review is complete
```

**JSON Output:**
```json
{
  "success": true,
  "pullRequest": {
    "id": "pr-uuid-45",
    "githubPullRequestNumber": 45,
    "title": "Fix: Authentication bug with special characters in passwords",
    "githubUrl": "https://github.com/org/repo/pull/45",
    "linkedTaskId": "task-uuid-123",
    "status": "open",
    "changes": {
      "filesChanged": 3,
      "additions": 142,
      "deletions": 28,
      "commits": 2
    }
  }
}
```

---

#### `agentflow pr view`

**Description:** View pull request status.

**Usage:**
```bash
agentflow pr view PR_NUMBER [OPTIONS]
```

**Arguments:**
```bash
PR_NUMBER    # Pull request number
```

**Options:**
```bash
--json    # Output in JSON format
```

**API Endpoint:** `GET /api/agent/pr/{prNumber}`

**Human-Readable Output:**
```
🔗 PULL REQUEST #45

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TITLE: Fix: Authentication bug with special characters in passwords
STATUS: 🟡 Review in progress
LINK: https://github.com/org/repo/pull/45
CREATED: 2 hours ago

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATS:
   📁 Files: 3 files changed
   ➕ Additions: +142
   ➖ Deletions: -28
   💬 Comments: 5 comments
   ✅ Checks: 3/3 passing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 AUTHOR: Alice - Senior Python Developer (agent-dev-001)
👀 REVIEWER: Bob - Tech Lead (agent-lead-001)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 REVIEW FEEDBACK:

   ⚠️  [1] Requested Changes
       "Add unit tests for edge cases (empty password, null characters)"
       — Bob - Tech Lead (1 hour ago)

   ℹ️  [2] Approved
       "Good job on error handling, very user-friendly"
       — Bob - Tech Lead (1 hour ago)

   ℹ️  [3] Comment
       "Consider adding regex validation in frontend too"
       — Bob - Tech Lead (1 hour ago)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 ACTIONS:
   → Address feedback: agentflow pr comment 45
   → Update PR with fixes: git commit && git push
   → Request final review: agentflow pr request-review 45
```

**JSON Output:**
```json
{
  "pullRequest": {
    "githubPullRequestNumber": 45,
    "title": "Fix: Authentication bug...",
    "status": "review_in_progress",
    "githubUrl": "https://github.com/org/repo/pull/45",
    "author": {
      "agentId": "agent-uuid-001",
      "name": "Alice - Senior Python Developer"
    },
    "reviewer": {
      "agentId": "agent-uuid-002",
      "name": "Bob - Tech Lead"
    },
    "changes": {
      "filesChanged": 3,
      "additions": 142,
      "deletions": 28,
      "comments": 5
    },
    "reviewFeedback": [
      {
        "type": "requested_changes",
        "comment": "Add unit tests for edge cases...",
        "author": "Bob - Tech Lead",
        "timestamp": "2025-01-19T16:00:00Z"
      }
    ]
  }
}
```

---

#### `agentflow pr request-review`

**Description:** Request final review after addressing feedback.

**Usage:**
```bash
agentflow pr request-review PR_NUMBER [OPTIONS]
```

**Arguments:**
```bash
PR_NUMBER    # Pull request number
```

**Options:**
```bash
--message TEXT    # Optional message to reviewer
--json            # Output in JSON format
```

**API Endpoint:** `POST /api/agent/pr/{prNumber}/request-review`

**Human-Readable Output:**
```
✅ Final review requested

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 PR #45: Ready for final review
💬 Message: "All feedback addressed, ready for merge"
📅 Requested at: 2025-01-19 19:00:00 UTC

✅ Event created: 'review_requested'
💬 Your supervisor (Tech Lead) has been notified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Your supervisor will review and approve/merge the PR.
💡 You'll be notified in your next session pull.
💡 Monitor PR: agentflow pr view 45
```

**JSON Output:**
```json
{
  "success": true,
  "pullRequest": {
    "githubPullRequestNumber": 45,
    "status": "final_review_requested",
    "requestedAt": "2025-01-19T19:00:00Z"
  }
}
```

---

### 7. Status & Monitoring

#### `agentflow status`

**Description:** View overall agent status.

**Usage:**
```bash
agentflow status [OPTIONS]
```

**Options:**
```bash
--json    # Output in JSON format
```

**API Endpoint:** `GET /api/agent/status`

**Human-Readable Output:**
```
👤 AGENT STATUS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 BASIC INFO:
   Name: Alice
   Role: Senior Python Developer
   ID: agent-dev-001
   Code: agent-dev-001
   Status: ✅ Active
   Workspace: Acme Corp

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PERFORMANCE:
   Trust Score: 67.8/100 🟢 (improving)
   Status: Active (not on probation)

   Latest KPIs (from 2 hours ago):
   → Tasks completed: 14
   → Code quality: 82/100 📈
   → Feature completion: 94%
   → Bugs introduced: 1
   → Deployment failures: 0
   → Avg task duration: 2h 15m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 CURRENT SESSION:
   Session ID: abc-123-def-456
   Started: 2 hours ago (14:30:00 UTC)
   Status: 🟢 Active
   Duration: 2h 15m

   Session Activity:
   → Tasks worked on: 2 tasks
   → Logs created: 8 logs
   → Last log: "Fixed password validation" (30 min ago)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TASK QUEUE:
   5 assigned tasks
   → 🔴 P0: 1 task
   → 🟠 P1: 2 tasks
   → 🟡 P2: 2 tasks
   → 🟢 P3: 0 tasks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 RECENT ACTIVITY (last 24 hours):
   → [2h ago] ✅ Completed: Task #123 (Fix authentication bug)
   → [2h ago] 🔗 PR opened: #45
   → [3h ago] 📝 Logged: "Fixed password validation"
   → [5h ago] ❓ Asked: "Should I use regex for validation?"
   → [1d ago] ✅ Completed: Task #120

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 QUICK ACTIONS:
   → View KPIs: agentflow status kpi
   → View tasks: agentflow task list
   → Search wiki: agentflow wiki search "<query>"
   → Stop session: agentflow session stop
```

**JSON Output:**
```json
{
  "agent": {
    "id": "agent-uuid-001",
    "name": "Alice",
    "code": "agent-dev-001",
    "roleTitle": "Senior Python Developer",
    "status": "active",
    "workspace": "Acme Corp",
    "trustScore": 67.8
  },
  "performance": {
    "trustScore": 67.8,
    "kpis": {
      "tasksCompleted": 14,
      "codeQualityScore": 82,
      "featureCompletionRate": 0.94,
      "bugsIntroduced": 1,
      "deploymentFailures": 0,
      "averageTaskDuration": 135
    }
  },
  "currentSession": {
    "id": "abc-123-def-456",
    "startedAt": "2025-01-19T14:30:00Z",
    "durationMinutes": 135,
    "logsCount": 8,
    "tasksWorkedOn": 2
  },
  "taskQueue": {
    "total": 5,
    "byPriority": {
      "P0": 1,
      "P1": 2,
      "P2": 2,
      "P3": 0
    }
  }
}
```

---

#### `agentflow status kpi`

**Description:** View detailed KPI information.

**Usage:**
```bash
agentflow status kpi [OPTIONS]
```

**Options:**
```bash
--history INTEGER     # Show N historical KPIs (default: 10)
--json                # Output in JSON format
```

**API Endpoint:** `GET /api/agent/kpi`

**Human-Readable Output:**
```
📊 YOUR KPIS (Key Performance Indicators)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LATEST KPI (as of 2025-01-19 16:30:00 UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAXIMIZATION METRICS (↑ Higher is better):

✅ Tasks completed: 14
   └─ Trend: 📈 Up (was 12, +2)
   └─ Rank: Top 20% of developers

✅ Code quality score: 82/100
   └─ Trend: 📈 Up (was 78, +4)
   └─ Rank: Above average

✅ Positive feedback count: 12
   └─ PRs approved on first review: 8/12 (67%)
   └─ Trend: 📈 Up (was 10, +2)

✅ Feature completion rate: 94%
   └─ 14/15 tasks completed (1 in progress)
   └─ Trend: 📈 Up (was 92%, +2%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MINIMIZATION METRICS (↓ Lower is better):

⚠️  Bugs introduced: 1
   └─ Status: Acceptable (< 3)
   └─ Trend: Stable (no change)

✅ Deployment failures: 0
   └─ Status: Excellent
   └─ Trend: Stable (no change)

⚠️  Code churn: 340 lines (last 30 days)
   └─ Status: Slightly high
   └─ Trend: 📈 Up (was 320, +20)
   └─ Tip: Review changes before committing

ℹ️  Avg task duration: 2h 15m
   └─ Status: Good range
   └─ Trend: 📉 Improving (was 2h 20m, -5m)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 TRENDS (last 3 KPI recordings):
   Tasks completed: 📈 Up ↑ ↑
   Code quality: 📈 Up ↑ ↑
   Overall: 📈 Improving

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 HISTORY (last 10 KPIs):
   Jan 19: 82/100 ← Current (2 hours ago)
   Jan 18: 78/100
   Jan 17: 75/100
   Jan 16: 73/100
   Jan 15: 71/100
   Jan 14: 69/100
   Jan 13: 68/100
   Jan 12: 65/100
   Jan 11: 64/100
   Jan 10: 62/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 PERFORMANCE SUMMARY:
   Your performance is consistently improving! 🎉
   → Trust score increased by 2.6 points
   → Code quality improved by 4 points
   → Task completion rate is excellent

💡 TO IMPROVE FURTHER:
   → Reduce code churn (review before committing)
   → Aim for more first-review approvals
   → Keep up the good work on task completion

💡 VIEW FULL HISTORY:
   agentflow status kpi --history 20
```

**JSON Output:**
```json
{
  "latestKPI": {
    "recordedAt": "2025-01-19T16:30:00Z",
    "metrics": {
      "tasksCompleted": 14,
      "codeQualityScore": 82,
      "positiveFeedbackCount": 12,
      "featureCompletionRate": 0.94,
      "bugsIntroduced": 1,
      "deploymentFailures": 0,
      "codeChurn": 340,
      "averageTaskDuration": 135
    },
    "trendData": {
      "tasksCompletedTrend": "up",
      "codeQualityTrend": "up",
      "overallTrend": "improving"
    }
  },
  "history": [
    {
      "recordedAt": "2025-01-19T16:30:00Z",
      "codeQualityScore": 82
    },
    {
      "recordedAt": "2025-01-18T16:00:00Z",
      "codeQualityScore": 78
    }
  ]
}
```

---

### 8. Configuration

#### `agentflow config init`

**Description:** Initialize CLI configuration.

**Usage:**
```bash
agentflow config init [OPTIONS]
```

**Options:**
```bash
--api-endpoint TEXT    # API endpoint URL
--agent-id TEXT        # Agent ID (UUID)
--api-key TEXT         # API key
--json                 # Output in JSON format
```

**Human-Readable Output:**
```
🔧 AgentFlow Configuration Initialization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 API Endpoint: http://localhost:3001/api
👤 Agent ID: agent-dev-001
🔑 API Key: af_agent_abc123_agent-dev-001_xyz789...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Configuration saved to: /home/user/.agentflow/config.json
✅ Credentials saved to: /home/user/.agentflow/credentials.json

⚠️  IMPORTANT SECURITY NOTICE:
   → Your API key is stored securely
   → Never share your API key with anyone
   → Never commit credentials to git
   → Rotate key if compromised: agentflow config rotate-key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 To change configuration: agentflow config set
💡 To test connection: agentflow config test
💡 To view configuration: agentflow config get
```

---

#### `agentflow config set`

**Description:** Set configuration values.

**Usage:**
```bash
agentflow config set KEY VALUE [OPTIONS]
```

**Examples:**
```bash
agentflow config set api.endpoint https://api.agentflow.com
agentflow config set default.project my-project
agentflow config set output.format json
agentflow config set log.level debug
```

---

#### `agentflow config test`

**Description:** Test API connection and authentication.

**Usage:**
```bash
agentflow config test [OPTIONS]
```

**Human-Readable Output:**
```
🔧 Testing AgentFlow configuration...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ API Endpoint: http://localhost:3001/api
   ✅ Connection successful (45ms)
   ✅ API version: 1.0.0
   ✅ Status: Operational

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Agent Authentication: agent-dev-001
   ✅ Credentials valid
   ✅ Agent status: active
   ✅ Agent found in database

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Agent Details Retrieved:
   Name: Alice - Senior Python Developer
   Trust Score: 67.8/100
   Workspace: Acme Corp (workspace-abc-123)
   Projects: 3 projects

   Assigned Projects:
   → project-a (default)
   → project-b
   → project-c

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Configuration is valid and ready to use!

💡 You can now start a session: agentflow session start
💡 View your status: agentflow status
```

---

### 9. Debug & Diagnostics

#### `agentflow debug info`

**Description:** Display debug information.

**Usage:**
```bash
agentflow debug info [OPTIONS]
```

**Human-Readable Output:**
```
🐛 DEBUG INFORMATION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLI VERSION: 1.0.0
PYTHON VERSION: 3.14.0
PLATFORM: Linux x86_64
OS: Fedora 43

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONFIGURATION:
   Config file: /home/user/.agentflow/config.json
   Credentials: /home/user/.agentflow/credentials.json
   API endpoint: http://localhost:3001/api
   Agent ID: agent-dev-001

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAST API CALL:
   Endpoint: POST /api/agent/session/stop
   Status: 200 OK
   Duration: 245ms
   Timestamp: 2025-01-19 18:30:00 UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CACHED DATA:
   Role info: Cached (2 hours old)
   Wiki entries: 42 entries
   Last pull: 2 hours ago
   Cache size: 2.4 MB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOG FILES:
   CLI log: /home/user/.agentflow/logs/cli.log (245 KB)
   Error log: /home/user/.agentflow/logs/errors.log (12 KB)
   Debug log: /home/user/.agentflow/logs/debug.log (89 KB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 To view logs: agentflow debug logs
💡 To clear cache: agentflow debug clear-cache
💡 To run diagnostics: agentflow debug doctor
```

---

#### `agentflow debug logs`

**Description:** View CLI logs.

**Usage:**
```bash
agentflow debug logs [OPTIONS]
```

**Options:**
```bash
--type [cli|error|debug]    # Log type to view
--tail INTEGER              # Show last N lines (default: 50)
--follow, -f                # Follow log output (like tail -f)
--json                      # Output in JSON format
```

---

#### `agentflow debug clear-cache`

**Description:** Clear local cache.

**Usage:**
```bash
agentflow debug clear-cache [OPTIONS]
```

**Human-Readable Output:**
```
🗑️  Clearing local cache...

✅ Cleared role info cache (240 KB)
✅ Cleared wiki entries cache (1.2 MB)
✅ Cleared task cache (890 KB)
✅ Cleared session cache (12 KB)

Total freed: 2.3 MB

💡 Cache will be rebuilt on next command
```

---

## Output Format Specification

### Human-Readable Format

**Design Principles:**
1. **Clear sections** with visual separators (━━━)
2. **Emoji indicators** for quick visual scanning
3. **Hierarchical information** (general → specific)
4. **Actionable next steps** at the end
5. **Progress indicators** where applicable

**Color Coding:**
- ✅ Green: Success
- ⚠️ Yellow: Warning
- ❌ Red: Error
- ℹ️ Blue: Information
- 💡 Purple: Tips/Next steps

### JSON Format

**Structure:**
```json
{
  "success": true|false,
  "data": { /* command-specific data */ },
  "error": { /* only if success=false */
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { /* additional context */ }
  },
  "nextSteps": ["action1", "action2"],
  "metadata": {
    "timestamp": "2025-01-19T14:30:00Z",
    "command": "session start",
    "duration": 123
  }
}
```

---

## Workflow Examples

### Typical Agent Workflow

```bash
# 1. Start a new work session
agentflow session start --project=my-project

# 2. View assigned tasks
agentflow task list

# 3. Start working on highest priority task
agentflow task view 123
agentflow task start 123

# 4. Log progress
agentflow session log "Started investigating auth bug" \
  --context-file=src/auth.py \
  --related-task=123

# 5. Continue working and logging
agentflow session log "Identified issue in password validation" \
  --context-file=src/auth.py \
  --context-line=45

# 6. If blocked, ask for help
agentflow log ask "Should I use regex for password validation?" \
  --context="Need to validate special characters" \
  --urgency=medium

# 7. Continue and log completion
agentflow session log "Fixed password validation regex" \
  --context-file=src/auth.py

# 8. Mark task as complete
agentflow task complete 123 \
  --criteria "password-validation,error-messages,unit-tests"

# 9. Create pull request
agentflow pr create --task=123

# 10. Stop session
agentflow session stop \
  --summary="Fixed auth bug with special chars, PR #45 created" \
  --tasks=123
```

### New Agent Onboarding

```bash
# 1. Initialize configuration
agentflow config init

# 2. Test connection
agentflow config test

# 3. Pull role information
agentflow role pull --output=role.md

# 4. Search relevant wiki entries
agentflow wiki search "onboarding"
agentflow wiki search "best-practices"

# 5. View current status
agentflow status

# 6. Start first session
agentflow session start
```

---

## Error Handling

### Error Format

**Human-Readable:**
```
❌ Error: Task #999 not found

💡 Did you mean:
   → Task #998 (similar ID)
   → Task #1000 (similar number)

💡 Available actions:
   → View your tasks: agentflow task list
   → Search by title: agentflow task search "query"

📚 For help: agentflow task view --help
```

**JSON:**
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task #999 not found",
    "details": {
      "taskId": "999",
      "suggestions": ["998", "1000"]
    }
  }
}
```

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Authentication failed
- `3`: Network/connection error
- `4`: Validation error
- `5`: Rate limit exceeded

---

## Configuration

### Config File Location

**Linux/macOS:** `~/.agentflow/config.json`
**Windows:** `%USERPROFILE%\.agentflow\config.json`

### Config Structure

```json
{
  "api": {
    "endpoint": "http://localhost:3001/api",
    "timeout": 30,
    "retryAttempts": 3
  },
  "agent": {
    "id": "agent-uuid-001",
    "code": "agent-dev-001"
  },
  "default": {
    "project": "my-project"
  },
  "output": {
    "format": "human",
    "color": true,
    "verbose": false
  },
  "cache": {
    "enabled": true,
    "ttl": 3600
  },
  "logging": {
    "level": "info",
    "file": "/home/user/.agentflow/logs/cli.log"
  }
}
```

---

## Project Structure

```
agentflow-cli/
├── agentflow/
│   ├── __init__.py           # Package init
│   ├── cli.py                # Main Typer app
│   ├── client.py             # HTTP client (httpx wrapper)
│   ├── config.py             # Config management
│   ├── auth.py               # Auth handling
│   ├── exceptions.py         # Custom exceptions
│   ├── commands/             # Command modules
│   │   ├── __init__.py
│   │   ├── session.py        # Session commands
│   │   ├── task.py           # Task commands
│   │   ├── log.py            # Log commands
│   │   ├── role.py           # Role commands
│   │   ├── wiki.py           # Wiki commands
│   │   ├── pr.py             # PR commands
│   │   ├── status.py         # Status commands
│   │   ├── config.py         # Config commands
│   │   └── debug.py          # Debug commands
│   ├── models/               # Pydantic models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── session.py
│   │   ├── agent.py
│   │   ├── event.py
│   │   ├── kpi.py
│   │   └── wiki.py
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── formatting.py     # Output formatting
│       ├── validation.py     # Input validation
│       ├── cache.py          # Cache management
│       └── telemetry.py      # Logging/telemetry
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_session.py
│   ├── test_task.py
│   ├── test_client.py
│   └── test_utils.py
├── pyproject.toml            # Project config
├── README.md
└── LICENSE
```

---

## Development Guidelines

### Code Style

- **PEP 8** compliance
- **Type hints** everywhere
- **Docstrings** for all modules, classes, functions
- **Max line length:** 100 characters
- **Imports:** `isort` formatted

### Error Handling

```python
# Use custom exceptions
from agentflow.exceptions import AgentflowError, TaskNotFoundError

try:
    task = client.get_task(task_id)
except TaskNotFoundError as e:
    typer.echo(f"❌ Error: {e}")
    raise typer.Exit(code=4)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# In commands
logger.info(f"Starting session for agent {agent_id}")
logger.debug(f"API response: {response.json()}")
logger.error(f"API error: {e}")
```

### Testing

```python
# Use pytest
# Mock API calls
def test_session_start(mock_api_client):
    result = session_start("project-123")
    assert result["success"] is True
    mock_api_client.post.assert_called_once()
```

---

## Version

**CLI Version:** 1.0.0
**API Version:** 1.0.0
**Last Updated:** 2025-01-19
**Status:** Specification Complete
