# Collaboration & Communication Features

## Feature 1: Enhanced CLI Commands (Slash-like)

### Overview

Quick-access commands for common agent workflows. These are specialized CLI commands that reduce boilerplate and standardize repetitive tasks across agents.

### Why It Matters

- **Time Savings**: Eliminate repetitive CLI patterns for common actions
- **Standardization**: All agents perform the same workflows consistently
- **Reduced Friction**: Less typing, fewer flags, faster execution

### Commands

#### Standup Command

Generate automatic daily standup summaries based on recent activity.

```bash
agentflow agent standup agent-dev-001

# Output:
# 📊 Daily Standup - Jean (agent-dev-001)
# ────────────────────────────────────────
# Date: 2025-01-21
#
# Yesterday:
#   ✓ Worked on task #123 (JWT authentication) - 80% complete
#   ✓ Fixed bug #127 (login timeout issue)
#   ✓ Implemented token refresh logic
#
# Today:
#   → Finish task #123 (remaining 20%)
#   → Start task #124 (user profile endpoints)
#   → Code review for task #125
#
# Blockers:
#   ⚠️  Waiting for API documentation (logged 2h ago)
#
# Session Stats:
#   • 2 sessions, 4h 30m total
#   • 12 events logged
#   • Trust score: 52.5 (no change)
```

**How it works:**
- Queries logs from the last 24 hours
- Identifies tasks worked on (from `task_id` in log context)
- Groups by "yesterday" vs "today" based on timestamps
- Checks for unanswered messages (blockers)
- Calculates session statistics

#### Handoff Command

Transfer work in progress to another agent with full context.

```bash
agentflow agent handoff \
  --from agent-dev-001 \
  --to agent-dev-002 \
  --task 123 \
  --message "JWT implementation done, needs testing and edge case handling"

# Output:
# ✅ Handoff created
#   From: agent-dev-001 (Jean)
#   To: agent-dev-002 (Alice)
#   Task: #123 - JWT authentication
#
# Context transferred:
#   • Session logs: 23 entries
#   • Current progress: 80% complete
#   • Files modified: src/auth/jwt.py, src/models/user.py
#   • Pending decisions: Token storage method
#
# Message sent to agent-dev-002:
#   "You've been assigned task #123 via handoff from Jean.
#    Context: JWT implementation done, needs testing and edge case handling
#    Review logs: agentflow logs show --task 123"
```

**How it works:**
- Reassigns the task to the new agent
- Creates a summary message to the receiver
- Links to relevant session logs
- Preserves context (progress, files, decisions)

#### Review Request Command

Request a code review from a supervisor or peer.

```bash
agentflow agent request-review \
  --from agent-dev-001 \
  --task 123 \
  --to agent-lead-001 \
  --message "Ready for review: JWT auth implementation"

# Output:
# ✅ Review requested
#   Task: #123 - JWT authentication
#   From: agent-dev-001 (Jean)
#   Reviewer: agent-lead-001 (Tech Lead)
#
# Task status updated: ready_review
# Review task created: #124
#
# Message sent to agent-lead-001:
#   "Review requested for task #123
#    Description: Ready for review: JWT auth implementation
#    Files: src/auth/jwt.py, src/models/user.py
#    Accept this task to begin review"
```

**How it works:**
- Updates task status to `ready_review`
- Creates a new review task linked to the original
- Sends notification message to the reviewer
- Links relevant files and context

### Data Model Additions

```python
class StandupSummary(BaseModel):
    agent_id: str
    date: datetime
    yesterday_tasks: List[Dict]  # Tasks worked on yesterday
    today_tasks: List[Dict]      # Tasks planned for today
    blockers: List[str]          # Unanswered messages, issues
    session_stats: Dict          # Session count, duration, log count

class Handoff(BaseModel):
    id: str
    from_agent_id: str
    to_agent_id: str
    task_id: str
    context_summary: str
    logs_transferred: int
    created_at: datetime
```

---

## Feature 2: Mentions in Logs

### Overview

Allow agents to tag other agents in their logs using `@agent-code` syntax. Mentions create a lightweight notification system without the formality of direct messages.

### Why It Matters

- **FYI Notifications**: Inform others without requiring action/response
- **Inbox Pollution Reduction**: Not everything needs to be a formal message
- **Context Preservation**: Mentions are part of the permanent log record
- **Discoverability**: Easy to see who's talking about what

### How It Works

#### Creating a Mention

```bash
agentflow session log \
  --agent agent-dev-001 \
  --message "Chose Redis for session storage for performance reasons. @agent-architect-001 might want to review this architectural decision." \
  --type decision \
  --context '{"alternative": "PostgreSQL", "reason": "2.3x faster reads"}'
```

**System behavior:**
1. Parses the log message for `@agent-code` patterns
2. Creates the log entry as normal
3. Creates mention records for each tagged agent
4. Notifies mentioned agents (they can query their mentions)

#### Viewing Mentions

```bash
# Check your mentions
agentflow agent mentions agent-architect-001

# Output:
# 📭 Mentions for agent-architect-001
# ─────────────────────────────────────
#
# 2 mentions unread
#
# 2 hours ago - Jean (agent-dev-001)
#   "Chose Redis for session storage for performance reasons. @agent-architect-001 might want to review this..."
#   Type: decision
#   Task: #123 - JWT authentication
#   Session: session-abc-123
#   Context: {"alternative": "PostgreSQL", "reason": "2.3x faster reads"}
#
# 5 hours ago - Alice (agent-dev-002)
#   "Implemented JWT tokens but @agent-architect-001 said we should use opaque tokens. Need clarification."
#   Type: question
#   Task: #124 - User profile
#
# ---

# Filter by unread only
agentflow agent mentions agent-architect-001 --unread

# Filter by date range
agentflow agent mentions agent-architect-001 --since "2025-01-20"

# Mark all as read
agentflow agent mentions-read agent-architect-001 --all
```

#### Mention vs Message

| Aspect | Mention | Message |
|--------|---------|---------|
| **Purpose** | FYI, awareness, FYI only | Request action/response |
| **Response Expected** | Optional (depends) | Yes |
| **Location** | Appears in "mentions" queue | Appears in inbox |
| **Formality** | Informal, contextual | Formal, direct |
| **Priority** | Always P3 (informational) | P0-P3 (explicit) |
| **Example** | "@lead FYI: using Redis here" | "@lead approve this deployment?" |

#### Auto-Linking

When an agent is mentioned:
- Their agent code becomes a clickable reference (in UI)
- Link to their profile: `agentflow agent view agent-architect-001`
- Link to relevant context (task, session, log)

### Data Model

```python
class Mention(BaseModel):
    id: str  # UUID
    mentioned_agent_id: str  # Who was tagged
    author_agent_id: str     # Who created the mention
    log_id: str              # Reference to the log event
    context: Dict[str, Any]  # Task, session, etc.
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime

class Event(BaseModel):
    # ... existing fields ...
    content: Dict[str, Any] = {
        "message": "... @agent-architect-001 ...",
        "mentions": ["agent-architect-001"],  # Extracted mentions
        # ... other fields ...
    }
```

### CLI Commands

```bash
# View mentions
agentflow agent mentions <agent-code>
agentflow agent mentions <agent-code> --unread
agentflow agent mentions <agent-code> --since <date>
agentflow agent mentions <agent-code> --limit 10

# Mark as read
agentflow agent mentions-read <agent-code> --mention-id <uuid>
agentflow agent mentions-read <agent-code> --all

# Search mentions across all agents (admin/manager)
agentflow admin search-mentions "@agent-architect-001"
```

---

## Feature 3: Session Draft & Resume

### Overview

Auto-save mechanism for active sessions with crash recovery and "draft mode" for experimentation. Prevents data loss from crashes and allows testing without committing logs.

### Why It Matters

- **Crash Recovery**: Power loss, bugs, or crashes don't lose work in progress
- **Experimentation**: Test approaches without polluting the official log record
- **Peace of Mind**: Long sessions are safe, work is preserved
- **Flexible Workflow**: Draft → Finalize → Commit to permanent record

### How It Works

#### Auto-Save During Active Session

```bash
# Start session normally
agentflow session start --agent agent-dev-001 --project my-project

# ✅ Session started
#    Auto-save enabled: every 5 minutes

# ... agent works, logs events ...

# ⚠️  CRASH! Power loss, system crash, etc.

# ... system restarts ...

# Attempt to start new session
agentflow session start --agent agent-dev-001 --project my-project

# ⚠️  Warning: Unsaved draft session detected
#     Draft created: 2025-01-21 14:32:15 UTC
#     Logs since last save: 7
#     Unsaved work: "Implementing JWT token validation..."
#
# Options:
#   • Resume draft: agentflow session resume
#   • Discard draft: agentflow session discard-draft
#   • Start new (draft will be preserved): agentflow session start --force
```

#### Resuming a Draft

```bash
agentflow session resume

# ✅ Session resumed from draft
#    Agent: agent-dev-001 (Jean)
#    Project: my-project
#    Started: 2025-01-21 14:30:00 UTC
#    Crashed: 2025-01-21 16:45:00 UTC (2h 15m ago)
#
# Recovered data:
#   • Logs: 7 events
#   • Last activity: "Fixing edge case in token refresh"
#   • Tasks worked on: #123
#
# Session status: logging (active)
# You can continue working normally.
```

#### Draft Mode (Experimental Work)

```bash
# Start in draft mode (for testing/experimentation)
agentflow session start --agent agent-dev-001 --project my-project --draft

# ✅ Draft session started
#    Session ID: session-draft-xyz
#    Mode: DRAFT (logs will not be committed until finalized)
#    Auto-save: enabled every 5 minutes

# ... agent experiments, logs things ...

# Decide to finalize the draft
agentflow session finalize

# ✅ Session finalized
#    Draft session promoted to official session
#    12 logs committed to permanent record
#    Session duration: 1h 30m
#    Tasks worked on: #123

# OR discard the draft
agentflow session discard

# ⚠️  Draft session discarded
#    12 logs deleted (not committed)
#    No permanent record created
```

#### Auto-Save Intervals

Configurable auto-save frequency:

```bash
# In config file or CLI
auto_save_interval: 5  # minutes

# Or disable auto-save
agentflow session start --no-auto-save
```

#### Draft Storage Location

```
~/.agentflow/
├── drafts/
│   ├── session-draft-agent-dev-001-20250121-143201.json
│   └── session-draft-agent-dev-002-20250121-150045.json
└── data.json
```

### Data Model

```python
class SessionDraft(BaseModel):
    id: str  # UUID (different from final session ID)
    agent_id: str
    project_id: str
    status: Literal["draft", "resumed", "discarded"]
    created_at: datetime
    last_saved_at: datetime
    crashed: bool = False  # True if session ended abnormally

    # Draft data (not yet committed)
    logs: List[Dict]  # Log events in draft
    tasks_worked_on: List[str]  # Task IDs
    metadata: Dict[str, Any]

    # Recoverable session
    def to_session(self) -> Session:
        """Convert draft to official session"""
        return Session(
            id=str(uuid.uuid4()),  # New official ID
            agent_id=self.agent_id,
            project_id=self.project_id,
            status="logging",
            started_at=self.created_at,
            logs=self.logs,
            tasks_worked_on=self.tasks_worked_on,
            metadata=self.metadata
        )

class Session(BaseModel):
    # ... existing fields ...
    draft_id: Optional[str] = None  # Link to draft if resumed from crash
    is_draft: bool = False  # True for draft sessions
```

### CLI Commands

```bash
# Normal session start
agentflow session start --agent <agent> --project <project>

# Start in draft mode
agentflow session start --agent <agent> --project <project> --draft
agentflow session start --agent <agent> --project <project> --draft --no-auto-save

# Resume after crash
agentflow session resume
agentflow session resume --draft-id <draft-uuid>

# Finalize draft (commit to permanent record)
agentflow session finalize
agentflow session finalize --keep-draft  # Keep draft copy after finalizing

# Discard draft
agentflow session discard
agentflow session discard --draft-id <draft-uuid>

# List drafts
agentflow session list-drafts
agentflow session list-drafts --agent <agent-code>

# View draft details
agentflow session view-draft <draft-uuid>

# Clean old drafts (older than N days)
agentflow session clean-drafts --older-than 7
```

### Crash Detection

How does the system know a session crashed?

1. **Heartbeat File**: `.agentflow/session-active` file with timestamp
   - Updated every minute during active session
   - If file exists but timestamp > 2 minutes ago → likely crashed

2. **Session Status Check**:
   - Active session exists but agentflow wasn't shut down cleanly
   - On next `session start`, detect active session in "logging" state

3. **User Confirmation**:
   - Prompt user: "Found unsaved session from 2 hours ago. Resume? [y/N]"

### Draft vs Official Session

| Aspect | Draft Session | Official Session |
|--------|--------------|------------------|
| **Logs** | Temporary, not counted | Permanent, counted in stats |
| **Visibility** | Agent only, hidden from reports | Visible in timelines, reports |
| **Purpose** | Experimentation, testing | Official work record |
| **Duration** | Until finalized/discarded | Until stopped |
| **Crash Recovery** | Auto-saved more frequently | Auto-saved normally |
| **Trust Score Impact** | None | Counts toward metrics |

### Edge Cases

**What if draft and official both exist for same agent?**
- Prompt user to choose: resume draft OR start new (draft preserved)

**What if multiple drafts exist?**
- Show list: "3 drafts found. Which one to resume?"
- Sort by recency (most recent first)

**What if finalize fails?**
- Draft remains intact, can retry finalization
- Error message explains what went wrong

**What if system crashes during finalize?**
- Draft marked as "finalizing" to prevent double-finalize
- Recovery: "Incomplete finalization detected. Retry or discard?"

---

## Implementation Notes (Phase 1+)

### Dependencies

- **Feature 1 (Commands)**: Requires existing logs, tasks, sessions
- **Feature 2 (Mentions)**: Requires existing log system, messages
- **Feature 3 (Drafts)**: Requires existing session system

### Priority

1. **Feature 2 (Mentions)** - High value, relatively simple
2. **Feature 3 (Drafts)** - High value, prevents data loss
3. **Feature 1 (Commands)** - Medium value, convenience feature

### Backwards Compatibility

All features are additive:
- Existing CLI commands continue to work
- New commands are optional
- Data model extensions are backwards compatible
- Draft system is opt-in (default sessions work as before)

---

**Document Version**: 1.0
**Created**: 2025-01-21
**Status**: 🎨 Design proposal - Ready for review
