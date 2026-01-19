# AgentFlow Database Schema

## Overview

AgentFlow uses PostgreSQL as the database with Drizzle ORM for type-safe database operations. This document provides the complete schema definition for all tables, relations, indexes, and constraints.

**Technology Stack:**
- Database: PostgreSQL 15+
- ORM: Drizzle ORM
- Schema Language: TypeScript
- Validation: Zod

## Design Principles

1. **UUID Primary Keys**: All tables use UUID primary keys for distributed system compatibility
2. **Timestamps**: All tables have `created_at` and `updated_at` timestamps
3. **Soft Deletes**: Critical tables use `deleted_at` for soft deletes instead of hard deletes
4. **Audit Trail**: All mutating operations include `created_by` and `updated_by` tracking
5. **JSONB for Flexibility**: Use JSONB columns for evolving schema requirements
6. **Foreign Key Cascades**: Define clear cascade behaviors for referential integrity

## Union Type Definitions

### AgentLevel

```typescript
type AgentLevel = 'organization' | 'project'

// Values:
// - 'organization': Management agents (CTO, Tech Lead, PM)
// - 'project': Execution agents (Developer, Designer, QA)
```

**PostgreSQL Constraint**: `CHECK (agent_level IN ('organization', 'project'))`

---

### AgentStatus

```typescript
type AgentStatus = 'active' | 'probation' | 'inactive' | 'terminated'
```

**PostgreSQL Constraint**: `CHECK (status IN ('active', 'probation', 'inactive', 'terminated'))`

---

### PriorityLevel

```typescript
type PriorityLevel = 'P0' | 'P1' | 'P2' | 'P3'

// Values:
// - 'P0': Critical
// - 'P1': High
// - 'P2': Medium
// - 'P3': Low
```

**PostgreSQL Constraint**: `CHECK (priority IN ('P0', 'P1', 'P2', 'P3'))`

---

### TaskStatus

```typescript
type TaskStatus = 'backlog' | 'assigned' | 'in_progress' | 'blocked' | 'completed' | 'cancelled'
```

**PostgreSQL Constraint**: `CHECK (status IN ('backlog', 'assigned', 'in_progress', 'blocked', 'completed', 'cancelled'))`

---

### SessionStatus

```typescript
type SessionStatus = 'started' | 'logging' | 'stopped'

// Values:
// - 'started': Session initiated
// - 'logging': Active with logs being written
// - 'stopped': Session ended
```

**PostgreSQL Constraint**: `CHECK (session_status IN ('started', 'logging', 'stopped'))`

---

### EventType

```typescript
type EventType =
  // Session Management
  | 'session_start'
  | 'session_log'
  | 'session_stop'
  // Task & Work
  | 'task_assigned'
  | 'task_completed'
  | 'task_blocked'
  // Communication
  | 'problem_report'
  | 'advice_given'
  | 'question_asked'
  // Code Review
  | 'review_requested'
  | 'review_response'
  // GitHub Integration
  | 'github_pr_opened'
  | 'github_pr_merged'
  | 'github_issue_assigned'
  // System Events
  | 'kpi_updated'
  | 'trust_score_changed'
  // Knowledge
  | 'wiki_contribution'
```

**PostgreSQL Constraint**:
```sql
CHECK (type IN (
  'session_start', 'session_log', 'session_stop',
  'task_assigned', 'task_completed', 'task_blocked',
  'problem_report', 'advice_given', 'question_asked',
  'review_requested', 'review_response',
  'github_pr_opened', 'github_pr_merged', 'github_issue_assigned',
  'kpi_updated', 'trust_score_changed',
  'wiki_contribution'
))
```

---

### WikiEntryStatus

```typescript
type WikiEntryStatus = 'draft' | 'pending_approval' | 'approved' | 'rejected'
```

**PostgreSQL Constraint**: `CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected'))`

---

## Tables

### 1. users

**Purpose**: Stores CEO (human user) accounts who own and manage workspaces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique user identifier |
| email | varchar(255) | NOT NULL, UNIQUE | User email address |
| password_hash | varchar(255) | NOT NULL | Hashed password (bcrypt) |
| name | varchar(255) | NOT NULL | Display name |
| avatar_url | varchar(500) | NULL | Profile avatar URL |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Relations:**
- HasMany → workspaces (owner_id)
- HasMany → sessions (created_by)

**Indexes:**
- UNIQUE INDEX idx_users_email (email)
- INDEX idx_users_deleted_at (deleted_at) -- For soft delete queries

**Zod Schema**:
```typescript
const userSchema = z.object({
  id: z.uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(255),
  avatarUrl: z.string().url().nullable(),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})
```

---

### 2. workspaces

**Purpose**: Represents a virtual company owned by a user (CEO).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique workspace identifier |
| owner_id | uuid | NOT NULL, FK → users.id | Owner (CEO) of the workspace |
| name | varchar(255) | NOT NULL | Workspace name |
| slug | varchar(100) | NOT NULL, UNIQUE | URL-friendly identifier |
| description | text | NULL | Workspace description |
| settings | jsonb | NOT NULL, DEFAULT '{}' | Workspace settings (theme, preferences) |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Relations:**
- BelongsTo → users (owner_id)
- HasMany → projects (workspace_id)
- HasMany → agents (workspace_id)

**Indexes:**
- UNIQUE INDEX idx_workspaces_slug (slug)
- INDEX idx_workspaces_owner_id (owner_id)
- INDEX idx_workspaces_deleted_at (deleted_at)

**Zod Schema**:
```typescript
const workspaceSchema = z.object({
  id: z.uuid(),
  ownerId: z.uuid(),
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().nullable(),
  settings: z.record(z.any()),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})
```

---

### 3. projects

**Purpose**: Represents specific initiatives within a workspace.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique project identifier |
| workspace_id | uuid | NOT NULL, FK → workspaces.id | Parent workspace |
| name | varchar(255) | NOT NULL | Project name |
| slug | varchar(100) | NOT NULL | URL-friendly identifier |
| description | text | NULL | Project description |
| repository_url | varchar(500) | NULL | GitHub repository URL |
| github_installation_id | bigint | NULL | GitHub App installation ID |
| mvp_document_url | varchar(500) | NULL | Link to MVP document |
| is_active | boolean | NOT NULL, DEFAULT true | Project status flag |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Composite Unique Constraint:**
- UNIQUE (workspace_id, slug) -- Unique slug within workspace

**Relations:**
- BelongsTo → workspaces (workspace_id)
- HasMany → agents (project_id) -- Project-level agents only
- HasMany → tasks (project_id)

**Indexes:**
- INDEX idx_projects_workspace_id (workspace_id)
- INDEX idx_projects_slug (slug)
- INDEX idx_projects_is_active (is_active)
- INDEX idx_projects_deleted_at (deleted_at)
- UNIQUE INDEX idx_projects_workspace_slug (workspace_id, slug)

**Zod Schema**:
```typescript
const projectSchema = z.object({
  id: z.uuid(),
  workspaceId: z.uuid(),
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().nullable(),
  repositoryUrl: z.string().url().nullable(),
  githubInstallationId: z.number().int().nullable(),
  mvpDocumentUrl: z.string().url().nullable(),
  isActive: z.boolean(),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})
```

---

### 4. agents

**Purpose**: Represents AI agents (virtual employees) with identity, roles, and performance tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique agent identifier |
| workspace_id | uuid | NOT NULL, FK → workspaces.id | Parent workspace |
| project_id | uuid | NULL, FK → projects.id | Project assignment (NULL for org-level agents) |
| agent_level | varchar(50) | NOT NULL | Agent level: 'organization' or 'project' |
| agent_code | varchar(100) | NOT NULL | Unique agent code (e.g., 'agent-dev-001') |
| name | varchar(255) | NOT NULL | Agent display name (e.g., 'Alice - Senior Python Developer') |
| role_title | varchar(255) | NOT NULL | Role title (e.g., 'Senior Python Developer') |
| status | varchar(50) | NOT NULL, DEFAULT 'active' | Agent status: 'active', 'probation', 'inactive', 'terminated' |
| trust_score | decimal(5,2) | NOT NULL, DEFAULT 50.00 | Trust score (0-100) |
| api_key_hash | varchar(255) | NOT NULL | Hashed API key for authentication |
| public_key | text | NULL | Public key for cryptographic signatures |
| capabilities | jsonb | NOT NULL, DEFAULT '[]' | Array of capability strings |
| settings | jsonb | NOT NULL, DEFAULT '{}' | Agent-specific settings |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Composite Unique Constraints:**
- UNIQUE (workspace_id, agent_code) -- Unique code within workspace
- UNIQUE (workspace_id, project_id, name) -- Unique name within scope

**Business Rules:**
- If `agent_level = 'organization'`, then `project_id` must be NULL
- If `agent_level = 'project'`, then `project_id` must be NOT NULL
- `trust_score` must be between 0 and 100
- Agents on 'probation' status cannot be assigned critical tasks

**Relations:**
- BelongsTo → workspaces (workspace_id)
- BelongsTo → projects (project_id, optional)
- HasMany → sessions (agent_id)
- HasMany → events (author_id)
- HasMany → tasks (assigned_agent_id)

**Indexes:**
- INDEX idx_agents_workspace_id (workspace_id)
- INDEX idx_agents_project_id (project_id)
- INDEX idx_agents_agent_level (agent_level)
- INDEX idx_agents_agent_code (agent_code)
- INDEX idx_agents_status (status)
- INDEX idx_agents_trust_score (trust_score)
- INDEX idx_agents_deleted_at (deleted_at)
- UNIQUE INDEX idx_agents_workspace_code (workspace_id, agent_code)
- UNIQUE INDEX idx_agents_workspace_project_name (workspace_id, project_id, name)

**Zod Schema**:
```typescript
const agentSchema = z.object({
  id: z.uuid(),
  workspaceId: z.uuid(),
  projectId: z.uuid().nullable(),
  agentLevel: z.union([z.literal('organization'), z.literal('project')]),
  agentCode: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  name: z.string().min(1).max(255),
  roleTitle: z.string().min(1).max(255),
  status: z.union([z.literal('active'), z.literal('probation'), z.literal('inactive'), z.literal('terminated')]),
  trustScore: z.number().min(0).max(100),
  capabilities: z.array(z.string()),
  settings: z.record(z.any()),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})

// Type inference
type Agent = z.infer<typeof agentSchema>
// agentLevel: 'organization' | 'project'
// status: 'active' | 'probation' | 'inactive' | 'terminated'
```

**Notes:**
- `api_key_hash` stores bcrypt hash of agent's API key (never store plaintext)
- `public_key` is used for verifying agent signatures on events
- `capabilities` JSONB array stores strings like 'python', 'typescript', 'code-review', etc.
- `trust_score` is recalculated after significant actions (PR merged, task completed)

---

### 5. sessions

**Purpose**: Tracks agent work sessions with start/stop times and logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique session identifier |
| agent_id | uuid | NOT NULL, FK → agents.id | Agent who started the session |
| project_id | uuid | NOT NULL, FK → projects.id | Project context for the session |
| status | varchar(50) | NOT NULL, DEFAULT 'started' | Session status: 'started', 'logging', 'stopped' |
| started_at | timestamp | NOT NULL, DEFAULT NOW() | Session start time |
| stopped_at | timestamp | NULL | Session stop time (NULL if active) |
| duration_seconds | integer | NULL | Calculated duration in seconds |
| tasks_worked_on | jsonb | NOT NULL, DEFAULT '[]' | Array of task IDs worked on during session |
| metadata | jsonb | NOT NULL, DEFAULT '{}' | Additional session metadata |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Business Rules:**
- A session cannot be modified after `stopped_at` is set
- `duration_seconds` is calculated automatically on stop
- Only one active session per agent at a time

**Relations:**
- BelongsTo → agents (agent_id)
- BelongsTo → projects (project_id)
- HasMany → events (session_id)

**Indexes:**
- INDEX idx_sessions_agent_id (agent_id)
- INDEX idx_sessions_project_id (project_id)
- INDEX idx_sessions_status (status)
- INDEX idx_sessions_started_at (started_at)
- INDEX idx_sessions_stopped_at (stopped_at)
- INDEX idx_sessions_agent_status (agent_id, status) -- For finding active sessions

**Zod Schema**:
```typescript
const sessionSchema = z.object({
  id: z.uuid(),
  agentId: z.uuid(),
  projectId: z.uuid(),
  status: z.union([z.literal('started'), z.literal('logging'), z.literal('stopped')]),
  startedAt: z.datetime(),
  stoppedAt: z.datetime().nullable(),
  durationSeconds: z.number().int().nullable(),
  tasksWorkedOn: z.array(z.uuid()),
  metadata: z.record(z.any()),
  createdAt: z.datetime(),
  updatedAt: z.datetime()
})

// Type inference: status: 'started' | 'logging' | 'stopped'
```

**Notes:**
- Session automatically pulls latest updates when started
- All session_log events are linked to a session
- Session duration is calculated and cached for performance

---

### 6. events

**Purpose**: Timeline of all agent and system events in chronological order.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique event identifier |
| type | varchar(100) | NOT NULL | Event type (see EventType union type) |
| author_id | uuid | NULL, FK → agents.id | Agent who created the event (NULL for automatic events) |
| session_id | uuid | NULL, FK → sessions.id | Related session (if applicable) |
| project_id | uuid | NULL, FK → projects.id | Related project (for filtering) |
| content | jsonb | NOT NULL | Event-specific payload (varies by type) |
| mentions | uuid[] | NOT NULL, DEFAULT '{}' | Array of agent IDs mentioned/affected |
| metadata | jsonb | NOT NULL, DEFAULT '{}' | Additional context (tags, related_issue, etc.) |
| timestamp | timestamp | NOT NULL, DEFAULT NOW() | Event timestamp |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Business Rules:**
- Events are immutable (append-only timeline)
- All events must have a valid `type` from EventType union type
- `author_id` is NULL for automatic system events
- `content` structure varies by event type

**Relations:**
- BelongsTo → agents (author_id, optional)
- BelongsTo → sessions (session_id, optional)
- BelongsTo → projects (project_id, optional)

**Indexes:**
- INDEX idx_events_type (type)
- INDEX idx_events_author_id (author_id)
- INDEX idx_events_session_id (session_id)
- INDEX idx_events_project_id (project_id)
- INDEX idx_events_timestamp (timestamp)
- INDEX idx_events_mentions (mentions) -- GIN index for array searching
- INDEX idx_events_metadata (metadata) -- GIN index for JSONB queries
- INDEX idx_events_type_timestamp (type, timestamp) -- For timeline queries
- INDEX idx_events_project_timestamp (project_id, timestamp) -- For project timeline

**Zod Schema**:
```typescript
const eventSchema = z.object({
  id: z.uuid(),
  type: z.union([
    z.literal('session_start'), z.literal('session_log'), z.literal('session_stop'),
    z.literal('task_assigned'), z.literal('task_completed'), z.literal('task_blocked'),
    z.literal('problem_report'), z.literal('advice_given'), z.literal('question_asked'),
    z.literal('review_requested'), z.literal('review_response'),
    z.literal('github_pr_opened'), z.literal('github_pr_merged'), z.literal('github_issue_assigned'),
    z.literal('kpi_updated'), z.literal('trust_score_changed'),
    z.literal('wiki_contribution')
  ]),
  authorId: z.uuid().nullable(),
  sessionId: z.uuid().nullable(),
  projectId: z.uuid().nullable(),
  content: z.record(z.any()),
  mentions: z.array(z.uuid()),
  metadata: z.record(z.any()),
  timestamp: z.datetime(),
  createdAt: z.datetime()
})

// Type inference:
// type: 'session_start' | 'session_log' | 'session_stop' | ...
```

**Event Content Examples**:

```typescript
// session_start
{
  pulled_updates: {
    tasks: 5,
    messages: 3,
    role_changes: 0
  }
}

// session_log
{
  message: "Implemented authentication flow",
  context: {
    file: "src/auth.ts",
    progress: 50
  }
}

// task_assigned
{
  taskId: uuid,
  title: string,
  description: string,
  priority: "P1",
  deadline: "2025-02-01T00:00:00Z"
}

// kpi_updated (automatic event)
{
  agentId: uuid,
  previousKPIs: { ... },
  newKPIs: { ... },
  changeReason: "PR merged successfully"
}

// wiki_contribution
{
  entryId: uuid,
  title: string,
  content: string,
  status: "pending_approval"
}
```

**Notes:**
- Events form an immutable timeline (no updates, no deletes)
- Use GIN indexes on `mentions` and `metadata` for efficient querying
- Partitioning by month/year may be needed for large-scale deployments

---

### 7. kpis

**Purpose**: Stores agent Key Performance Indicators with historical tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique KPI record identifier |
| agent_id | uuid | NOT NULL, FK → agents.id | Agent this KPI belongs to |
| recorded_at | timestamp | NOT NULL, DEFAULT NOW() | When this KPI was recorded |
| metrics | jsonb | NOT NULL | KPI metrics object |
| trend_data | jsonb | NOT NULL, DEFAULT '{}' | Trend analysis data |
| calculated_at | timestamp | NOT NULL, DEFAULT NOW() | Calculation timestamp |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Composite Unique Constraint:**
- UNIQUE (agent_id, recorded_at) -- One KPI record per agent per timestamp

**Business Rules:**
- New KPI record is created after significant actions
- Historical KPIs are preserved for trend analysis
- Latest KPI for an agent can be found by ordering by `recorded_at`

**Relations:**
- BelongsTo → agents (agent_id)

**Indexes:**
- INDEX idx_kpis_agent_id (agent_id)
- INDEX idx_kpis_recorded_at (recorded_at)
- INDEX idx_kpis_agent_recorded (agent_id, recorded_at DESC) -- For fetching latest
- INDEX idx_kpis_metrics (metrics) -- GIN index for JSONB queries

**Zod Schema**:
```typescript
const kpiSchema = z.object({
  id: z.uuid(),
  agentId: z.uuid(),
  recordedAt: z.datetime(),
  metrics: z.object({
    // Maximization KPIs
    tasksCompleted: z.number().int().default(0),
    codeQualityScore: z.number().min(0).max(100).default(0),
    positiveFeedbackCount: z.number().int().default(0),
    featureCompletionRate: z.number().min(0).max(1).default(0),

    // Minimization KPIs
    bugsIntroduced: z.number().int().default(0),
    deploymentFailures: z.number().int().default(0),
    codeChurn: z.number().int().default(0),
    averageTaskDuration: z.number().int().default(0), // in minutes

    // Custom metrics per role
    customMetrics: z.record(z.number()).optional()
  }),
  trendData: z.object({
    tasksCompletedTrend: z.union([z.literal('up'), z.literal('down'), z.literal('stable')]),
    codeQualityTrend: z.union([z.literal('up'), z.literal('down'), z.literal('stable')]),
    overallTrend: z.union([z.literal('improving'), z.literal('declining'), z.literal('stable')])
  }),
  calculatedAt: z.datetime(),
  createdAt: z.datetime()
})
```

**Notes:**
- KPIs are recalculated asynchronously after significant events
- Historical KPIs enable trend analysis and trust score calculation
- `metrics` JSONB allows flexible metrics per role

---

### 8. tasks

**Purpose**: Represents work tasks linked to GitHub Issues.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique task identifier |
| project_id | uuid | NOT NULL, FK → projects.id | Project this task belongs to |
| github_issue_id | bigint | NOT NULL | GitHub Issue ID |
| github_issue_number | integer | NOT NULL | GitHub Issue number |
| assigned_agent_id | uuid | NULL, FK → agents.id | Agent assigned to this task |
| status | varchar(50) | NOT NULL, DEFAULT 'backlog' | Task status (see TaskStatus union type) |
| priority | varchar(10) | NOT NULL, DEFAULT 'P2' | Priority level (P0-P3) |
| title | varchar(500) | NOT NULL | Task title (from GitHub) |
| description | text | NULL | Task description (from GitHub) |
| deadline | timestamp | NULL | Task deadline (NULL = no deadline) |
| success_criteria | jsonb | NOT NULL, DEFAULT '[]' | Array of success criteria |
| started_at | timestamp | NULL | When agent started working |
| completed_at | timestamp | NULL | When task was completed |
| metadata | jsonb | NOT NULL, DEFAULT '{}' | Additional task metadata |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Composite Unique Constraints:**
- UNIQUE (project_id, github_issue_id) -- One task per GitHub issue
- UNIQUE (project_id, github_issue_number) -- One task per issue number

**Business Rules:**
- Task status is synchronized with GitHub issue status
- Only one agent can be assigned to a task at a time
- Tasks are prioritized by priority level, then deadline
- Agents work on highest priority tasks first

**Relations:**
- BelongsTo → projects (project_id)
- BelongsTo → agents (assigned_agent_id)
- HasMany → events (task_id in metadata)

**Indexes:**
- INDEX idx_tasks_project_id (project_id)
- INDEX idx_tasks_github_issue_id (github_issue_id)
- INDEX idx_tasks_assigned_agent_id (assigned_agent_id)
- INDEX idx_tasks_status (status)
- INDEX idx_tasks_priority (priority)
- INDEX idx_tasks_deadline (deadline)
- INDEX idx_tasks_priority_status (priority, status) -- For priority queue
- INDEX idx_tasks_agent_priority (assigned_agent_id, priority, status) -- For agent's queue
- INDEX idx_tasks_deleted_at (deleted_at)
- UNIQUE INDEX idx_tasks_project_github_id (project_id, github_issue_id)
- UNIQUE INDEX idx_tasks_project_github_number (project_id, github_issue_number)

**Zod Schema**:
```typescript
const taskSchema = z.object({
  id: z.uuid(),
  projectId: z.uuid(),
  githubIssueId: z.number().int(),
  githubIssueNumber: z.number().int(),
  assignedAgentId: z.uuid().nullable(),
  status: z.union([
    z.literal('backlog'), z.literal('assigned'), z.literal('in_progress'),
    z.literal('blocked'), z.literal('completed'), z.literal('cancelled')
  ]),
  priority: z.union([z.literal('P0'), z.literal('P1'), z.literal('P2'), z.literal('P3')]),
  title: z.string().min(1).max(500),
  description: z.string().nullable(),
  deadline: z.datetime().nullable(),
  successCriteria: z.array(z.string()),
  startedAt: z.datetime().nullable(),
  completedAt: z.datetime().nullable(),
  metadata: z.record(z.any()),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})

// Type inference:
// status: 'backlog' | 'assigned' | 'in_progress' | 'blocked' | 'completed' | 'cancelled'
// priority: 'P0' | 'P1' | 'P2' | 'P3'
```

**Notes:**
- Tasks are synchronized with GitHub Issues via webhooks
- When GitHub issue is assigned, create `github_issue_assigned` event
- When PR is merged, check if linked task is complete
- Task conflicts are prevented through proper assignment (no system-level locks)

---

### 9. wiki_entries

**Purpose**: Knowledge base for organizational knowledge with versioning.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique wiki entry identifier |
| workspace_id | uuid | NOT NULL, FK → workspaces.id | Workspace this entry belongs to |
| project_id | uuid | NULL, FK → projects.id | Project-specific entry (NULL = org-wide) |
| proposed_by_agent_id | uuid | NULL, FK → agents.id | Agent who proposed this entry (NULL if CEO) |
| status | varchar(50) | NOT NULL, DEFAULT 'draft' | Approval status (see WikiEntryStatus union type) |
| title | varchar(500) | NOT NULL | Entry title |
| slug | varchar(200) | NOT NULL | URL-friendly identifier |
| content | text | NOT NULL | Entry content (Markdown) |
| tags | varchar[] | NOT NULL, DEFAULT '{}' | Array of tags for categorization |
| version | integer | NOT NULL, DEFAULT 1 | Entry version |
| parent_entry_id | uuid | NULL, FK → wiki_entries.id | Parent entry (for version history) |
| approved_by | uuid | NULL, FK → users.id | CEO who approved this entry |
| approved_at | timestamp | NULL | Approval timestamp |
| rejection_reason | text | NULL | Reason for rejection (if rejected) |
| view_count | integer | NOT NULL, DEFAULT 0 | Number of times this entry was viewed |
| last_viewed_at | timestamp | NULL | Last viewed timestamp |
| metadata | jsonb | NOT NULL, DEFAULT '{}' | Additional metadata |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Composite Unique Constraints:**
- UNIQUE (workspace_id, project_id, slug) -- Unique slug per scope
- UNIQUE (workspace_id, project_id, title) -- Unique title per scope

**Business Rules:**
- Only organization-level agents can propose wiki entries
- CEO (user) must approve all wiki entries before they're visible
- Version history is maintained through `parent_entry_id`
- Draft entries are only visible to the proposing agent
- Approved entries are visible to all agents in workspace/project

**Relations:**
- BelongsTo → workspaces (workspace_id)
- BelongsTo → projects (project_id, optional)
- BelongsTo → agents (proposed_by_agent_id, optional)
- BelongsTo → users (approved_by, optional)
- Self-referential → wiki_entries (parent_entry_id) -- For version history

**Indexes:**
- INDEX idx_wiki_workspace_id (workspace_id)
- INDEX idx_wiki_project_id (project_id)
- INDEX idx_wiki_proposed_by_agent_id (proposed_by_agent_id)
- INDEX idx_wiki_status (status)
- INDEX idx_wiki_slug (slug)
- INDEX idx_wiki_tags (tags) -- GIN index for array searching
- INDEX idx_wiki_parent_entry_id (parent_entry_id)
- INDEX idx_wiki_approved_by (approved_by)
- INDEX idx_wiki_deleted_at (deleted_at)
- INDEX idx_wiki_fulltext (title, content) -- For full-text search
- UNIQUE INDEX idx_wiki_workspace_project_slug (workspace_id, project_id, slug)

**Zod Schema**:
```typescript
const wikiEntrySchema = z.object({
  id: z.uuid(),
  workspaceId: z.uuid(),
  projectId: z.uuid().nullable(),
  proposedByAgentId: z.uuid().nullable(),
  status: z.union([
    z.literal('draft'), z.literal('pending_approval'),
    z.literal('approved'), z.literal('rejected')
  ]),
  title: z.string().min(1).max(500),
  slug: z.string().min(1).max(200).regex(/^[a-z0-9-]+$/),
  content: z.string().min(1),
  tags: z.array(z.string()),
  version: z.number().int().positive(),
  parentEntryId: z.uuid().nullable(),
  approvedBy: z.uuid().nullable(),
  approvedAt: z.datetime().nullable(),
  rejectionReason: z.string().nullable(),
  viewCount: z.number().int().nonnegative(),
  lastViewedAt: z.datetime().nullable(),
  metadata: z.record(z.any()),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})

// Type inference: status: 'draft' | 'pending_approval' | 'approved' | 'rejected'
```

**Notes:**
- Use PostgreSQL full-text search on `title` and `content` columns
- Wiki entries support Markdown formatting
- Tags are stored as array for flexible categorization
- When CEO approves, create new version with `parent_entry_id` pointing to previous
- When CEO edits approved entry, create new version (never mutate existing versions)

---

### 10. agent_credentials (Security Table)

**Purpose**: Stores agent API credentials securely.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique credential identifier |
| agent_id | uuid | NOT NULL, FK → agents.id | Agent this credential belongs to |
| credential_type | varchar(50) | NOT NULL | Type: 'api_key', 'jwt_secret', etc. |
| credential_hash | varchar(255) | NOT NULL | Hashed credential (bcrypt) |
| salt | varchar(100) | NOT NULL | Salt for hashing |
| is_active | boolean | NOT NULL, DEFAULT true | Whether this credential is active |
| expires_at | timestamp | NULL | Expiration timestamp (NULL = never) |
| last_used_at | timestamp | NULL | Last time this credential was used |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |
| deleted_at | timestamp | NULL | Soft delete timestamp |

**Business Rules:**
- Credentials are never stored in plaintext
- Use bcrypt with salt for hashing
- Old credentials can be rotated (set `is_active = false`, create new entry)
- Credentials can have expiration dates for automatic rotation

**Relations:**
- BelongsTo → agents (agent_id)
- HasMany → credential_usage_logs (id)

**Indexes:**
- INDEX idx_agent_credentials_agent_id (agent_id)
- INDEX idx_agent_credentials_credential_type (credential_type)
- INDEX idx_agent_credentials_is_active (is_active)
- INDEX idx_agent_credentials_expires_at (expires_at)

**Zod Schema**:
```typescript
const agentCredentialSchema = z.object({
  id: z.uuid(),
  agentId: z.uuid(),
  credentialType: z.union([z.literal('api_key'), z.literal('jwt_secret')]),
  credentialHash: z.string(),
  salt: z.string(),
  isActive: z.boolean(),
  expiresAt: z.datetime().nullable(),
  lastUsedAt: z.datetime().nullable(),
  createdAt: z.datetime(),
  updatedAt: z.datetime(),
  deletedAt: z.datetime().nullable()
})

// Type inference: credentialType: 'api_key' | 'jwt_secret'
```

**Notes:**
- This table is separate from `agents` for security isolation
- Never expose credential hashes via API
- Implement rate limiting on credential validation
- Log all credential usage for audit trail

---

## Database Constraints & Triggers

### Timestamp Triggers

All tables with `updated_at` should have an automatic trigger:

```sql
CREATE OR FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Repeat for all other tables...
```

### Cascade Behaviors

**ON DELETE CASCADE:**
- events → sessions (when session deleted, events cascade)
- events → agents (soft delete preferred, but cascade on hard delete)
- kpis → agents (cascade KPIs when agent permanently deleted)

**ON DELETE SET NULL:**
- agents → projects (if project deleted, set agent.project_id to NULL)
- tasks → agents (if agent deleted, set task.assigned_agent_id to NULL)

**ON DELETE RESTRICT:**
- projects → workspaces (cannot delete workspace with projects)
- agents → workspaces (cannot delete workspace with agents)

---

## PostgreSQL Features Used

### JSONB Columns

Use JSONB for flexible schema evolution:

```sql
-- Example: Query agents with specific capability
SELECT * FROM agents
WHERE capabilities @> '"python"';

-- Example: Query events by metadata
SELECT * FROM events
WHERE metadata->>'related_issue' = 'GitHub-123';
```

### Full-Text Search

For wiki entries:

```sql
-- Create full-text search index
CREATE INDEX idx_wiki_fulltext_search ON wiki_entries
USING GIN (to_tsvector('english', title || ' ' || content));

-- Query with full-text search
SELECT * FROM wiki_entries
WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('authentication & flow');
```

### Array Operations

For tags and mentions:

```sql
-- Query events that mention specific agents
SELECT * FROM events
WHERE 'agent-uuid-123' = ANY(mentions);

-- Query wiki entries with specific tags
SELECT * FROM wiki_entries
WHERE 'architecture' = ANY(tags);
```

---

## Migration Strategy

### Drizzle Kit Commands

```bash
# Generate migration from schema changes
npx drizzle-kit generate:pg

# Apply migrations
npx drizzle-kit push:pg

# Open studio (database GUI)
npx drizzle-kit studio
```

### Seed Data

Initial seed data should include:
1. Default CEO user account
2. Example workspace structure
3. Basic organization-level agent templates
4. Default wiki categories/tags

---

## Performance Considerations

### Indexing Strategy

1. **Foreign Keys**: All foreign keys have indexes
2. **Query Patterns**: Indexes match common query patterns (agent_id, status, timestamps)
3. **Composite Indexes**: For multi-column queries (agent_id + status)
4. **GIN Indexes**: For JSONB and array columns

### Partitioning (Future)

Consider partitioning for large tables:
- `events` - Partition by month (timestamp)
- `kpis` - Partition by month (recorded_at)

### Connection Pooling

Use PgBouncer or Drizzle's built-in connection pooling:
- Default pool size: 10 connections
- Max connections: 100 (PostgreSQL default)

---

## Backup & Recovery

### Backup Strategy

1. **Daily Full Backups**: `pg_dump` at midnight
2. **WAL Archiving**: Continuous write-ahead log archiving
3. **Point-in-Time Recovery**: Enable PITR for critical data

### Backup Command

```bash
# Full backup
pg_dump -U postgres -h localhost -d agentflow > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres -h localhost -d agentflow | gzip > backup_$(date +%Y%m%d).sql.gz
```

---

## Security Considerations

### Access Control

1. **Database User Permissions**:
   - `agentflow_app`: Application user (SELECT, INSERT, UPDATE, DELETE)
   - `agentflow_admin`: Admin user (DDL, manage migrations)
   - `agentflow_read`: Read-only user (SELECT only for analytics)

2. **Row-Level Security** (Optional):
   - Enable RLS on `agents` table
   - Agents can only see their own credentials
   - Organization-level agents can see all agents in workspace

### Sensitive Data Protection

1. **API Keys**: Hash with bcrypt (never store plaintext)
2. **Passwords**: Hash with bcrypt (cost factor 12)
3. **Secrets**: Use PostgreSQL's `pgcrypto` extension for encryption

---

## Summary

**Total Tables**: 10
**Total Union Types**: 8
**Total Indexes**: 50+ (including composite and GIN indexes)

**Key Design Decisions**:
- UUID for all primary keys (distributed system compatible)
- Soft deletes on critical tables (users, workspaces, projects, agents, tasks, wiki)
- JSONB for flexible schema evolution
- Comprehensive indexing for performance
- Full audit trail with created_at/updated_at timestamps
- Separate security table for credentials (agent_credentials)

---

**Last Updated**: 2025-01-19
**Version**: 1.0
**Status**: Database Schema Definition
