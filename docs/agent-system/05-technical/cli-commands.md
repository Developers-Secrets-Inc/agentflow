# CLI Commands Design

## CLI Commands Design

### Role Management Commands

```bash
# List available roles
agentflow role list
agentflow role list --level project
agentflow role list --level organization

# Create a new role
agentflow role create \
  --name "Python Developer" \
  --slug "python-dev" \
  --description "Senior Python developer with FastAPI expertise" \
  --level project

# View role details
agentflow role view python-dev

# Add documents to a role
agentflow role add-document python-dev \
  --name "testing-guidelines" \
  --file "./docs/testing.md"

agentflow role add-document python-dev \
  --name "api-conventions" \
  --file "./docs/api-conventions.md"

# List role documents
agentflow role list-documents python-dev

# Update a role
agentflow role update python-dev \
  --description "Updated description..."

# Delete a role
agentflow role delete python-dev
```

### Agent Management Commands

```bash
# List agents
agentflow agent list
agentflow agent list --level organization
agentflow agent list --level project
agentflow agent list --status active
agentflow agent list --project my-project

# Create an agent (assigning a role)
agentflow agent create \
  --name "Jean" \
  --code "agent-dev-001" \
  --role "python-dev" \
  --level project \
  --project my-project

# View agent details
agentflow agent view agent-dev-001

# Pull agent role (generates Claude Code skills)
agentflow agent pull agent-dev-001

# Update agent (change role assignment)
agentflow agent update agent-dev-001 \
  --role "senior-python-dev"

# Deactivate/reactivate agent
agentflow agent deactivate agent-dev-001
agentflow agent activate agent-dev-001

# Delete agent
agentflow agent delete agent-dev-001
```

### Agent Lifecycle & Deletion

**Agent Status States**:
```
active → probation → inactive → terminated
   ↑          ↓            ↓
   └──────────┴────────────┘
      (can recover)
```

**Status Changes**:
```bash
# Deactivate agent (temporary)
agentflow agent deactivate agent-dev-001
# Status: active → inactive
# Agent cannot start new sessions
# Data preserved

# Reactivate agent
agentflow agent activate agent-dev-001
# Status: inactive → active
# Agent can work again

# Terminate agent (permanent)
agentflow agent terminate agent-dev-001
# Status: any → terminated
# Agent permanently disabled
# All data preserved (see below)
```

**Data Retention on Termination**:

**IMPORTANT: ALL data from terminated agents is preserved**

| Data Type | Fate | Reason |
|-----------|------|--------|
| **Tasks** | Kept with assignment | Audit trail, who did what |
| **Sessions** | Kept | Historical record, analytics |
| **Logs** | Kept | Debugging, performance analysis |
| **Messages** | Kept (both sent and received) | Communication history |
| **Trust Score History** | Kept | Long-term performance tracking |
| **Skills Generated** | **Kept in ~/.claude/skills/** | Other agents may use same role |
| **Timeline** | Kept | Complete agent history |

**What happens when agent is terminated**:

```bash
agentflow agent terminate agent-dev-001

# Output:
# ⚠️  Terminating agent: agent-dev-001 (Jean)
#
# The following will be PRESERVED:
#   • Tasks: 23 tasks completed by this agent
#   • Sessions: 45 sessions with 120h of work logged
#   • Logs: 847 event entries
#   • Messages: 156 sent, 89 received
#   • Trust history: [50, 52, 55, ..., 67]
#   • Generated skills: python-testing, python-api, python-async
#
# Agent will be marked as 'terminated' and cannot be reactivated.
# All data remains accessible for audit and analytics.
#
# Confirm termination? [y/N]:
```

**After Termination**:

```bash
# Cannot start sessions (error)
agentflow session start --agent agent-dev-001
# Error: Agent agent-dev-001 is terminated and cannot work

# Cannot assign tasks (error)
agentflow task create --title "Fix bug" --assign-to agent-dev-001
# Error: Cannot assign task to terminated agent

# Can still view history
agentflow agent timeline agent-dev-001
# Shows complete timeline of all work

# Can view terminated agents
agentflow agent list --include-terminated
# Shows all agents including terminated ones
```

**Viewing Terminated Agent Data**:

```bash
# View agent details
agentflow agent view agent-dev-001
# Shows: Status: terminated, Trust: 67, Tasks: 23 completed, etc.

# View all sessions
agentflow session list --agent agent-dev-001
# Shows all 45 sessions

# View complete timeline
agentflow agent timeline agent-dev-001 --full
# Shows entire work history

# Export agent data (for archive/audit)
agentflow agent export agent-dev-001 --output agent-dev-001-archive.json
# Exports all agent data to JSON file
```

**Task Reassignment**:

When an agent is terminated, their tasks are NOT automatically reassigned:

```bash
# Manually reassign tasks from terminated agent
agentflow task list --assigned-to agent-dev-001 --status in_progress,backlog
agentflow task reassign --task 123 --to agent-dev-002
agentflow task reassign --task 124 --to agent-dev-002
# ...or batch reassign:
agentflow task reassign --from agent-dev-001 --to agent-dev-002 --all
```

**Why Keep All Data?**

1. **Audit Trail**: Know exactly who did what, when
2. **Analytics**: Long-term performance analysis
3. **Debugging**: Investigate issues by looking at past work
4. **Compliance**: Legal/regulatory requirements
5. **Learning**: Analyze what went well/poorly

**Deleting Agent Data** (Full System - Optional):

For full system, may add data retention policies:

```bash
# Archive old terminated agents (compress data)
agentflow agent archive --older-than 365days
# Compresses data, removes from active database

# Purge very old data (configurable retention policy)
agentflow agent purge --older-than 7years --confirm
# Permanently deletes data per retention policy
```

**Phase 0**: No deletion/archiving, all data kept indefinitely
**Full System**: Optional retention policies per organization requirements

### Session Commands

```bash
# Start a work session
agentflow session start \
  --agent agent-dev-001 \
  --project my-project

# View active session
agentflow session status

# Log an activity
agentflow session log \
  --message "Implemented user authentication" \
  --type activity \
  --task 123

# Log with context
agentflow session log \
  --message "Refactored database queries" \
  --context '{"files": ["src/db.py"], "improvement": "2.3x faster"}' \
  --tags "performance,refactoring"

# Stop work session
agentflow session stop

# View session history
agentflow session list --agent agent-dev-001
agentflow session view <session-id>
```

### Query/Filter Commands

```bash
# View agent timeline
agentflow agent timeline agent-dev-001

# View recent logs
agentflow logs recent --agent agent-dev-001 --limit 20

# Search logs
agentflow logs search "authentication" --agent agent-dev-001

# View session summary
agentflow session summary <session-id>
```

### Task Management Commands

```bash
# Create a task
agentflow task create \
  --title "Implement user authentication" \
  --type development \
  --priority P1 \
  --project website-redesign \
  --assign-to agent-dev-001

# List tasks
agentflow task list
agentflow task list --project website-redesign
agentflow task list --agent agent-dev-001
agentflow task list --status in_progress
agentflow task list --priority P0

# View task details
agentflow task view 123

# Assign task
agentflow task assign --task 123 --to agent-dev-002

# Reassign task
agentflow task reassign --task 123 --to agent-dev-003

# Update task status
agentflow task update --task 123 --status in_progress
agentflow task update --task 123 --status ready_review

# Approve task (manager only)
agentflow task approve --task 123

# Reject task (manager only)
agentflow task reject --task 123 --reason "Code quality issues"

# View review queue (manager)
agentflow task review-queue --agent agent-lead-001

# Cancel task
agentflow task cancel --task 123
```

### Hierarchy Management Commands

```bash
# Set organization hierarchy
agentflow org set-hierarchy --tree "
CTO
├── Architect
├── Tech Lead
└── PM
"

# View organization hierarchy
agentflow org hierarchy show

# Set project hierarchy
agentflow project set-hierarchy --project my-project --tree "
Tech Lead
├── Senior Dev
│   └── Dev
└── QA
"

# View project hierarchy
agentflow project hierarchy show --project my-project

# Visualize hierarchy (ASCII tree)
agentflow project hierarchy visualize --project my-project

# Export hierarchy to file
agentflow project hierarchy export --project my-project --output tree.yaml

# Import hierarchy from file
agentflow project hierarchy import --project my-project --input tree.yaml

# Validate hierarchy
agentflow project hierarchy validate --project my-project
```

### Agent Communication Commands

```bash
# Send message to supervisor
agentflow agent send-message \
  --from agent-dev-001 \
  --to supervisor \
  --type question \
  --message "Need clarification on authentication flow"

# Send to specific agent
agentflow agent send-message \
  --from agent-lead-001 \
  --to agent-dev-001 \
  --type request \
  --message "Please prioritize task #123"

# View inbox
agentflow agent inbox --agent agent-lead-001

# View sent messages
agentflow agent sent --agent agent-dev-001

# Reply to message
agentflow agent reply \
  --message-id 456 \
  --message "Here's the answer..."

# Mark message as read
agentflow agent mark-read --message-id 456
```

### Hierarchy Query Commands

```bash
# Who is my boss?
agentflow agent who-is-my-boss --agent agent-dev-001

# View subordinates
agentflow agent subordinates --agent agent-lead-001

# View agent's position in hierarchy
agentflow agent position --agent agent-dev-001
```

### Trust Score Commands

```bash
# View agent trust score
agentflow agent trust-score --agent agent-dev-001

# Manually adjust trust score (Phase 0 / manual override)
agentflow agent trust-score set --agent agent-dev-001 --score 75

# View trust history
agentflow agent trust-history --agent agent-dev-001
```

---
