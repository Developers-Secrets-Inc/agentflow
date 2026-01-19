# AgentFlow API Specification

## Overview

This document provides the complete API specification for AgentFlow, including all tRPC routes, Zod schemas, event structures, and business logic algorithms.

**Technology Stack:**
- Framework: Hono (TypeScript)
- RPC Layer: tRPC v11
- Validation: Zod
- Database: PostgreSQL with Drizzle ORM

**Base URL:** `http://localhost:3001/api` (development)

---

## Table of Contents

1. [Architecture](#architecture)
2. [Authentication](#authentication)
3. [Shared Types & Schemas](#shared-types--schemas)
4. [Routes by Domain](#routes-by-domain)
5. [Event Specifications](#event-specifications)
6. [Business Logic Algorithms](#business-logic-algorithms)
7. [Error Handling](#error-handling)
8. [Webhooks](#webhooks)

---

## Architecture

### Router Structure

```
api/
├── routers/
│   ├── index.ts           # Root router combining all routers
│   ├── auth.ts            # CEO authentication (better-auth)
│   ├── agent.ts           # Agent authentication & operations
│   ├── workspace.ts       # Workspace CRUD
│   ├── project.ts         # Project CRUD
│   ├── session.ts         # Session management
│   ├── task.ts            # Task operations
│   ├── event.ts           # Event operations
│   ├── wiki.ts            # Wiki operations
│   ├── kpi.ts             # KPI operations
│   └── github.ts          # GitHub integration
├── middleware/
│   ├── auth.ts            # CEO authentication middleware
│   ├── agent-auth.ts      # Agent authentication middleware
│   └── errorHandler.ts    # Global error handler
├── services/
│   ├── kpi-calculator.ts  # KPI calculation logic
│   ├── trust-calculator.ts# Trust score calculation
│   ├── github-sync.ts     # GitHub synchronization
│   └── session-manager.ts # Session management logic
└── schema/
    ├── input.ts           # Input Zod schemas
    ├── output.ts          # Output Zod schemas
    └── shared.ts          # Shared type schemas
```

### Middleware Stack

```typescript
// CEO routes (web dashboard)
app.use("/api/workspace/*", ceoAuthMiddleware)
app.use("/api/project/*", ceoAuthMiddleware)
app.use("/api/wiki/*", ceoAuthMiddleware)

// Agent routes (CLI)
app.use("/api/agent/*", agentAuthMiddleware)

// Public routes
app.use("/api/auth/*", publicMiddleware) // Login, signup
app.use("/api/webhooks/*", webhookSignatureMiddleware)
```

---

## Authentication

### CEO Authentication (better-auth)

**Method:** Session-based authentication with secure httpOnly cookies

**Flow:**
1. CEO navigates to `/login`
2. Enters email/password OR clicks "Sign in with GitHub"
3. better-auth validates credentials
4. Creates session in `users` table
5. Sets secure `__session` cookie (httpOnly, secure, sameSite: strict)
6. All subsequent requests include cookie automatically

**Middleware:**
```typescript
// Expects valid session cookie
// Sets context.user with CEO user object
// Returns 401 if no valid session
```

### Agent Authentication (Custom)

**Method:** API Key authentication via custom headers

**Credentials:**
- Generated on agent creation
- Stored in `agent_credentials` table (hashed with bcrypt)
- Format: `af_agent_<workspace_id>_<agent_code>_<random_32_chars>`

**Headers:**
```http
X-Agent-ID: uuid
X-Agent-Key: af_agent_<workspace_id>_<agent_code>_<random_32_chars>
```

**Middleware:**
```typescript
// Validates agent exists and is active
// Validates API key hash matches database
// Sets context.agent with agent object
// Returns 401 if invalid credentials
// Returns 403 if agent is inactive/terminated
```

---

## Shared Types & Schemas

### Base Schemas

```typescript
import { z } from 'zod'

// UUID schema
const UUID = z.string().uuid()

// Timestamp schema
const Timestamp = z.string().datetime()

// Slug schema (URL-friendly identifier)
const Slug = z.string().regex(/^[a-z0-9-]+$/)

// Agent code schema
const AgentCode = z.string().regex(/^[a-z0-9-]+$/)

// Email schema
const Email = z.string().email()

// URL schema
const URL = z.string().url()

// JSONB metadata schema
const Metadata = z.record(z.any())

// Pagination
const PaginationInput = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(100).default(20),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
})

const PaginatedOutput = <T extends z.ZodType>(itemSchema: T) => z.object({
  items: z.array(itemSchema),
  total: z.number().int(),
  page: z.number().int(),
  limit: z.number().int(),
  totalPages: z.number().int()
})
```

### Union Types

```typescript
// Agent Level
const AgentLevel = z.enum(['organization', 'project'])

// Agent Status
const AgentStatus = z.enum(['active', 'probation', 'inactive', 'terminated'])

// Priority Level
const PriorityLevel = z.enum(['P0', 'P1', 'P2', 'P3'])

// Task Status
const TaskStatus = z.enum(['backlog', 'assigned', 'in_progress', 'blocked', 'completed', 'cancelled'])

// Session Status
const SessionStatus = z.enum(['started', 'logging', 'stopped'])

// Wiki Entry Status
const WikiEntryStatus = z.enum(['draft', 'pending_approval', 'approved', 'rejected'])

// Event Type
const EventType = z.enum([
  'session_start', 'session_log', 'session_stop',
  'task_assigned', 'task_completed', 'task_blocked',
  'problem_report', 'advice_given', 'question_asked',
  'review_requested', 'review_response',
  'github_pr_opened', 'github_pr_merged', 'github_issue_assigned',
  'kpi_updated', 'trust_score_changed',
  'wiki_contribution'
])
```

### Entity Schemas

```typescript
// User (CEO)
const UserSchema = z.object({
  id: UUID,
  email: Email,
  name: z.string().min(1).max(255),
  avatarUrl: URL.nullable(),
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Workspace
const WorkspaceSchema = z.object({
  id: UUID,
  ownerId: UUID,
  name: z.string().min(1).max(255),
  slug: Slug,
  description: z.string().nullable(),
  settings: Metadata,
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Project
const ProjectSchema = z.object({
  id: UUID,
  workspaceId: UUID,
  name: z.string().min(1).max(255),
  slug: Slug,
  description: z.string().nullable(),
  repositoryUrl: URL.nullable(),
  githubInstallationId: z.number().int().nullable(),
  mvpDocumentUrl: URL.nullable(),
  isActive: z.boolean(),
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Agent
const AgentSchema = z.object({
  id: UUID,
  workspaceId: UUID,
  projectId: UUID.nullable(),
  agentLevel: AgentLevel,
  agentCode: AgentCode,
  name: z.string().min(1).max(255),
  roleTitle: z.string().min(1).max(255),
  status: AgentStatus,
  trustScore: z.number().min(0).max(100),
  capabilities: z.array(z.string()),
  settings: Metadata,
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Session
const SessionSchema = z.object({
  id: UUID,
  agentId: UUID,
  projectId: UUID,
  status: SessionStatus,
  startedAt: Timestamp,
  stoppedAt: Timestamp.nullable(),
  durationSeconds: z.number().int().nullable(),
  tasksWorkedOn: z.array(UUID),
  metadata: Metadata,
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Task
const TaskSchema = z.object({
  id: UUID,
  projectId: UUID,
  githubIssueId: z.number().int(),
  githubIssueNumber: z.number().int(),
  assignedAgentId: UUID.nullable(),
  status: TaskStatus,
  priority: PriorityLevel,
  title: z.string().min(1).max(500),
  description: z.string().nullable(),
  deadline: Timestamp.nullable(),
  successCriteria: z.array(z.string()),
  startedAt: Timestamp.nullable(),
  completedAt: Timestamp.nullable(),
  metadata: Metadata,
  createdAt: Timestamp,
  updatedAt: Timestamp
})

// Event
const EventSchema = z.object({
  id: UUID,
  type: EventType,
  authorId: UUID.nullable(),
  sessionId: UUID.nullable(),
  projectId: UUID.nullable(),
  content: Metadata, // Varies by event type
  mentions: z.array(UUID),
  metadata: Metadata,
  timestamp: Timestamp,
  createdAt: Timestamp
})

// KPI
const KPISchema = z.object({
  id: UUID,
  agentId: UUID,
  recordedAt: Timestamp,
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
    tasksCompletedTrend: z.enum(['up', 'down', 'stable']),
    codeQualityTrend: z.enum(['up', 'down', 'stable']),
    overallTrend: z.enum(['improving', 'declining', 'stable'])
  }),
  calculatedAt: Timestamp,
  createdAt: Timestamp
})

// Wiki Entry
const WikiEntrySchema = z.object({
  id: UUID,
  workspaceId: UUID,
  projectId: UUID.nullable(),
  proposedByAgentId: UUID.nullable(),
  status: WikiEntryStatus,
  title: z.string().min(1).max(500),
  slug: Slug,
  content: z.string().min(1),
  tags: z.array(z.string()),
  version: z.number().int().positive(),
  parentEntryId: UUID.nullable(),
  approvedBy: UUID.nullable(),
  approvedAt: Timestamp.nullable(),
  rejectionReason: z.string().nullable(),
  viewCount: z.number().int().nonnegative(),
  lastViewedAt: Timestamp.nullable(),
  metadata: Metadata,
  createdAt: Timestamp,
  updatedAt: Timestamp
})
```

---

## Routes by Domain

### 1. Authentication Routes (auth.ts)

**Middleware:** Public (no auth required for login/signup)

#### POST auth/signup

**Description:** Register a new CEO user account

**Input:**
```typescript
{
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(1).max(255)
}
```

**Output:**
```typescript
{
  user: UserSchema,
  session: z.object({
    id: UUID,
    userId: UUID,
    expiresAt: Timestamp
  })
}
```

**Errors:**
- `AUTH_EMAIL_ALREADY_EXISTS` (409)
- `AUTH_WEAK_PASSWORD` (400)

---

#### POST auth/login

**Description:** Login with email/password

**Input:**
```typescript
{
  email: z.string().email(),
  password: z.string()
}
```

**Output:**
```typescript
{
  user: UserSchema,
  session: z.object({
    id: UUID,
    userId: UUID,
    expiresAt: Timestamp
  })
}
```

**Errors:**
- `AUTH_INVALID_CREDENTIALS` (401)
- `AUTH_ACCOUNT_SUSPENDED` (403)

---

#### POST auth/logout

**Description:** Logout current CEO session

**Input:** null (uses session cookie)

**Output:**
```typescript
{
  success: z.boolean()
}
```

**Errors:** None

---

#### POST auth/github

**Description:** Initiate GitHub OAuth flow

**Input:** null

**Output:**
```typescript
{
  redirectUrl: z.string().url() // GitHub OAuth URL
}
```

**Errors:** None

---

#### GET auth/session

**Description:** Get current CEO session

**Input:** null (uses session cookie)

**Output:**
```typescript
{
  user: UserSchema,
  session: z.object({
    id: UUID,
    userId: UUID,
    expiresAt: Timestamp
  }).nullable()
}
```

**Errors:** None

---

### 2. Workspace Routes (workspace.ts)

**Middleware:** CEO authentication required

#### GET workspace.list

**Description:** List all workspaces owned by current CEO

**Input:**
```typescript
{
  includeDeleted: z.boolean().default(false)
}
```

**Output:**
```typescript
{
  workspaces: z.array(WorkspaceSchema)
}
```

**Errors:** None

---

#### GET workspace.get

**Description:** Get a specific workspace by ID

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  workspace: WorkspaceSchema
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)

---

#### POST workspace.create

**Description:** Create a new workspace

**Input:**
```typescript
{
  name: z.string().min(1).max(255),
  slug: Slug,
  description: z.string().optional(),
  settings: Metadata.optional()
}
```

**Output:**
```typescript
{
  workspace: WorkspaceSchema
}
```

**Errors:**
- `WORKSPACE_SLUG_ALREADY_EXISTS` (409)
- `WORKSPACE_INVALID_SLUG` (400)

---

#### PUT workspace.update

**Description:** Update workspace details

**Input:**
```typescript
{
  id: UUID,
  name: z.string().min(1).max(255).optional(),
  slug: Slug.optional(),
  description: z.string().optional(),
  settings: Metadata.optional()
}
```

**Output:**
```typescript
{
  workspace: WorkspaceSchema
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)
- `WORKSPACE_SLUG_ALREADY_EXISTS` (409)

---

#### DELETE workspace.delete

**Description:** Soft delete a workspace

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  success: z.boolean()
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)
- `WORKSPACE_NOT_EMPTY` (400) - Cannot delete workspace with active projects/agents

---

### 3. Project Routes (project.ts)

**Middleware:** CEO authentication required

#### GET project.list

**Description:** List all projects in a workspace

**Input:**
```typescript
{
  workspaceId: UUID,
  includeInactive: z.boolean().default(false),
  includeDeleted: z.boolean().default(false)
}
```

**Output:**
```typescript
{
  projects: z.array(ProjectSchema)
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)

---

#### GET project.get

**Description:** Get a specific project

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  project: ProjectSchema
}
```

**Errors:**
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)

---

#### POST project.create

**Description:** Create a new project

**Input:**
```typescript
{
  workspaceId: UUID,
  name: z.string().min(1).max(255),
  slug: Slug,
  description: z.string().optional(),
  repositoryUrl: URL.optional(),
  githubInstallationId: z.number().int().optional(),
  mvpDocumentUrl: URL.optional()
}
```

**Output:**
```typescript
{
  project: ProjectSchema
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)
- `PROJECT_SLUG_ALREADY_EXISTS` (409)
- `PROJECT_INVALID_GITHUB_INSTALLATION` (400)

---

#### PUT project.update

**Description:** Update project details

**Input:**
```typescript
{
  id: UUID,
  name: z.string().min(1).max(255).optional(),
  slug: Slug.optional(),
  description: z.string().optional(),
  repositoryUrl: URL.optional(),
  githubInstallationId: z.number().int().optional(),
  mvpDocumentUrl: URL.optional(),
  isActive: z.boolean().optional()
}
```

**Output:**
```typescript
{
  project: ProjectSchema
}
```

**Errors:**
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)
- `PROJECT_SLUG_ALREADY_EXISTS` (409)

---

#### DELETE project.delete

**Description:** Soft delete a project

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  success: z.boolean()
}
```

**Errors:**
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)
- `PROJECT_HAS_ACTIVE_AGENTS` (400)
- `PROJECT_HAS_ACTIVE_TASKS` (400)

---

### 4. Agent Routes (agent.ts)

**Middleware:** CEO authentication required (for management), Agent authentication (for operations)

#### GET agent.list

**Description:** List all agents in workspace

**Input:**
```typescript
{
  workspaceId: UUID,
  projectId: UUID.optional(), // Filter by project
  agentLevel: AgentLevel.optional(), // Filter by level
  status: AgentStatus.optional() // Filter by status
}
```

**Output:**
```typescript
{
  agents: z.array(AgentSchema)
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)

---

#### GET agent.get

**Description:** Get specific agent details

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  agent: AgentSchema,
  recentKPIs: z.array(KPISchema), // Last 10 KPI records
  recentSessions: z.array(SessionSchema) // Last 10 sessions
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)

---

#### POST agent.create

**Description:** Create a new agent (generates API key)

**Input:**
```typescript
{
  workspaceId: UUID,
  projectId: UUID.optional(), // Required for project-level agents
  agentLevel: AgentLevel,
  agentCode: AgentCode,
  name: z.string().min(1).max(255),
  roleTitle: z.string().min(1).max(255),
  capabilities: z.array(z.string()).optional(),
  settings: Metadata.optional()
}
```

**Output:**
```typescript
{
  agent: AgentSchema,
  credentials: z.object({
    agentId: UUID,
    apiKey: z.string(), // Plain text API key (only shown once)
    agentCode: z.string()
  })
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)
- `PROJECT_NOT_FOUND` (404) - If projectId provided and not found
- `AGENT_CODE_ALREADY_EXISTS` (409)
- `AGENT_INVALID_LEVEL` (400) - Mismatch between agentLevel and projectId

**Business Logic:**
- If `agentLevel = 'organization'`, then `projectId` must be NULL
- If `agentLevel = 'project'`, then `projectId` must be provided
- Generate API key: `af_agent_<workspace_id>_<agent_code>_<random_32_chars>`
- Hash API key with bcrypt and store in `agent_credentials` table
- Set initial `trustScore` to 50.00
- Set initial `status` to 'active'

---

#### PUT agent.update

**Description:** Update agent details

**Input:**
```typescript
{
  id: UUID,
  name: z.string().min(1).max(255).optional(),
  roleTitle: z.string().min(1).max(255).optional(),
  status: AgentStatus.optional(),
  capabilities: z.array(z.string()).optional(),
  settings: Metadata.optional()
}
```

**Output:**
```typescript
{
  agent: AgentSchema
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)

**Note:** Only CEO can change agent status

---

#### POST agent.rotateCredentials

**Description:** Rotate agent API key (invalidate old, generate new)

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  agent: AgentSchema,
  credentials: z.object({
    agentId: UUID,
    apiKey: z.string(), // New plain text API key
    agentCode: z.string()
  })
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)

**Business Logic:**
- Set old credential `is_active = false`
- Generate new API key
- Hash and store new credential
- Return new plain text key (only shown once)

---

#### DELETE agent.delete

**Description:** Soft delete an agent

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  success: z.boolean()
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)
- `AGENT_HAS_ACTIVE_SESSIONS` (400)
- `AGENT_HAS_ASSIGNED_TASKS` (400)

---

### 5. Session Routes (session.ts)

**Middleware:** Agent authentication required

#### POST session.start

**Description:** Start a new work session for an agent

**Input:**
```typescript
{
  projectId: UUID // Project context for this session
}
```

**Output:**
```typescript
{
  session: SessionSchema,
  pulledUpdates: z.object({
    tasks: z.array(TaskSchema), // All assigned tasks for this agent in this project
    messages: z.array(EventSchema), // Events mentioning this agent since last session
    roleChanges: z.array(z.object({
      field: z.string(),
      oldValue: z.any(),
      newValue: z.any(),
      changedAt: Timestamp
    }))
  })
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_INACTIVE` (403)
- `AGENT_ON_PROBATION` (403) - With warning message
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)
- `AGENT_HAS_ACTIVE_SESSION` (400) - Must stop current session first

**Business Logic:**
1. Validate agent exists and is active (or probation)
2. Validate agent has access to project
3. Check no active session exists for this agent
4. Create session with status='started'
5. Create `session_start` event
6. Pull updates:
   - Tasks: All assigned tasks for agent in this project (status != completed)
   - Messages: All events where agent is in mentions, since last session.stop
   - Role changes: Any changes to agent's capabilities/settings since last session
7. Return session + updates

---

#### POST session.log

**Description:** Log information during a work session

**Input:**
```typescript
{
  sessionId: UUID,
  message: z.string().min(1),
  context: Metadata.optional() // Optional context (file, progress, etc.)
}
```

**Output:**
```typescript
{
  event: EventSchema // The session_log event created
}
```

**Errors:**
- `SESSION_NOT_FOUND` (404)
- `SESSION_ACCESS_DENIED` (403)
- `SESSION_ALREADY_STOPPED` (400)
- `AGENT_SESSION_MISMATCH` (403) - Agent doesn't own this session

**Business Logic:**
1. Validate session exists and belongs to agent
2. Validate session is not stopped
3. Update session status to 'logging' if currently 'started'
4. Create `session_log` event with message and context
5. Add event to session's events
6. Return the event

---

#### POST session.stop

**Description:** Stop/complete a work session

**Input:**
```typescript
{
  sessionId: UUID,
  tasksWorkedOn: z.array(UUID).optional(), // Optional: list of task IDs worked on
  summary: z.string().optional() // Optional: summary of work done
}
```

**Output:**
```typescript
{
  session: SessionSchema,
  kpiUpdate: z.object({
    previousKPIs: KPISchema.optional(), // Undefined if first KPI
    newKPIs: KPISchema,
    changeReason: z.string()
  }).nullable() // Null if KPI not recalculated
}
```

**Errors:**
- `SESSION_NOT_FOUND` (404)
- `SESSION_ACCESS_DENIED` (403)
- `SESSION_ALREADY_STOPPED` (400)
- `AGENT_SESSION_MISMATCH` (403)

**Business Logic:**
1. Validate session exists and belongs to agent
2. Update session:
   - Set `stoppedAt = NOW()`
   - Calculate `durationSeconds = stoppedAt - startedAt`
   - Set `status = 'stopped'`
   - Store `tasksWorkedOn` if provided
3. Create `session_stop` event
4. Determine if KPI recalculation is needed:
   - If session.duration > 5 minutes, recalculate KPIs
   - If tasksWorkedOn not empty, recalculate KPIs
5. If KPI recalculation needed:
   - Calculate new KPIs (see KPI Algorithm)
   - Create new KPI record
   - Create `kpi_updated` event
   - Return KPI delta
6. Return updated session + KPI update (if any)

---

#### GET session.get

**Description:** Get session details

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  session: SessionSchema,
  events: z.array(EventSchema), // All events for this session
  agent: AgentSchema,
  project: ProjectSchema
}
```

**Errors:**
- `SESSION_NOT_FOUND` (404)
- `SESSION_ACCESS_DENIED` (403)

---

### 6. Task Routes (task.ts)

**Middleware:** CEO authentication required

#### GET task.list

**Description:** List tasks in a project

**Input:**
```typescript
{
  projectId: UUID,
  status: TaskStatus.optional(),
  priority: PriorityLevel.optional(),
  assignedAgentId: UUID.optional()
}
```

**Output:**
```typescript
{
  tasks: z.array(TaskSchema)
}
```

**Errors:**
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)

---

#### GET task.get

**Description:** Get specific task

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  task: TaskSchema,
  assignedAgent: AgentSchema.nullable(),
  events: z.array(EventSchema) // Events related to this task
}
```

**Errors:**
- `TASK_NOT_FOUND` (404)
- `TASK_ACCESS_DENIED` (403)

---

#### POST task.create

**Description:** Create a new task (usually from GitHub webhook)

**Input:**
```typescript
{
  projectId: UUID,
  githubIssueId: z.number().int(),
  githubIssueNumber: z.number().int(),
  title: z.string().min(1).max(500),
  description: z.string().optional(),
  priority: PriorityLevel.optional(), // Default: P2
  deadline: Timestamp.optional(),
  successCriteria: z.array(z.string()).optional()
}
```

**Output:**
```typescript
{
  task: TaskSchema
}
```

**Errors:**
- `PROJECT_NOT_FOUND` (404)
- `PROJECT_ACCESS_DENIED` (403)
- `TASK_ALREADY_EXISTS` (409) - GitHub issue already linked

**Business Logic:**
- Set initial `status = 'backlog'`
- Set default `priority = 'P2'` if not provided
- Create `github_issue_assigned` event

---

#### PUT task.update

**Description:** Update task details

**Input:**
```typescript
{
  id: UUID,
  status: TaskStatus.optional(),
  priority: PriorityLevel.optional(),
  assignedAgentId: UUID.optional(),
  title: z.string().min(1).max(500).optional(),
  description: z.string().optional(),
  deadline: Timestamp.optional(),
  successCriteria: z.array(z.string()).optional()
}
```

**Output:**
```typescript
{
  task: TaskSchema
}
```

**Errors:**
- `TASK_NOT_FOUND` (404)
- `TASK_ACCESS_DENIED` (403)
- `AGENT_NOT_FOUND` (404) - If assignedAgentId provided and not found
- `TASK_INVALID_AGENT_ASSIGNMENT` (400) - Agent doesn't have access to project

**Business Logic:**
- If `assignedAgentId` changed:
  - Validate agent has access to project
  - Create `task_assigned` event
  - Update task status to 'assigned' if currently 'backlog'
- If `status` changed to 'in_progress':
  - Set `startedAt = NOW()`
- If `status` changed to 'completed':
  - Set `completedAt = NOW()`
  - Create `task_completed` event

---

#### POST task.assign

**Description:** Assign a task to an agent

**Input:**
```typescript
{
  taskId: UUID,
  agentId: UUID
}
```

**Output:**
```typescript
{
  task: TaskSchema
}
```

**Errors:**
- `TASK_NOT_FOUND` (404)
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)
- `TASK_INVALID_AGENT_ASSIGNMENT` (400)
- `AGENT_ON_PROBATION` (403) - Warning if assigning to probation agent

**Business Logic:**
1. Validate task and agent exist
2. Validate agent has access to task's project
3. Check if agent is on probation:
   - Allow assignment but include warning
4. Update task:
   - Set `assignedAgentId = agentId`
   - Set `status = 'assigned'` (if currently 'backlog')
5. Create `task_assigned` event
6. Trigger KPI recalculation for agent (async)

---

### 7. Event Routes (event.ts)

**Middleware:** CEO authentication required

#### GET event.list

**Description:** List events (timeline)

**Input:**
```typescript
{
  workspaceId: UUID.optional(),
  projectId: UUID.optional(),
  agentId: UUID.optional(),
  sessionId: UUID.optional(),
  type: EventType.optional(),
  limit: z.number().int().positive().max(100).default(50),
  offset: z.number().int().nonnegative().default(0)
}
```

**Output:**
```typescript
{
  events: z.array(EventSchema),
  total: z.number().int(),
  hasMore: z.boolean()
}
```

**Errors:** None

---

#### GET event.get

**Description:** Get specific event

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  event: EventSchema,
  author: AgentSchema.nullable(),
  session: SessionSchema.nullable(),
  project: ProjectSchema.nullable()
}
```

**Errors:**
- `EVENT_NOT_FOUND` (404)
- `EVENT_ACCESS_DENIED` (403)

---

### 8. Wiki Routes (wiki.ts)

**Middleware:** CEO authentication required

#### GET wiki.list

**Description:** List wiki entries

**Input:**
```typescript
{
  workspaceId: UUID,
  projectId: UUID.optional(), // If null, show org-wide entries
  status: WikiEntryStatus.optional(), // If null, show only 'approved'
  tags: z.array(z.string()).optional(),
  search: z.string().optional() // Full-text search
}
```

**Output:**
```typescript
{
  entries: z.array(WikiEntrySchema)
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `WORKSPACE_ACCESS_DENIED` (403)

---

#### GET wiki.get

**Description:** Get specific wiki entry

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  entry: WikiEntrySchema,
  author: AgentSchema.nullable(),
  approver: UserSchema.nullable(),
  parentEntry: WikiEntrySchema.nullable(), // If this is a new version
  childEntries: z.array(WikiEntrySchema) // If this has newer versions
}
```

**Errors:**
- `WIKI_ENTRY_NOT_FOUND` (404)
- `WIKI_ENTRY_ACCESS_DENIED` (403)

**Business Logic:**
- Increment `viewCount`
- Update `lastViewedAt = NOW()`

---

#### POST wiki.create

**Description:** Create a new wiki entry (organization agents only)

**Input:**
```typescript
{
  workspaceId: UUID,
  projectId: UUID.optional(), // If null, org-wide entry
  title: z.string().min(1).max(500),
  slug: Slug,
  content: z.string().min(1),
  tags: z.array(z.string()).optional()
}
```

**Output:**
```typescript
{
  entry: WikiEntrySchema
}
```

**Errors:**
- `WORKSPACE_NOT_FOUND` (404)
- `AGENT_NOT_ORGANIZATION_LEVEL` (403) - Only org agents can create wiki entries
- `WIKI_ENTRY_SLUG_ALREADY_EXISTS` (409)

**Business Logic:**
- Set initial `status = 'pending_approval'`
- Set `version = 1`
- Create `wiki_contribution` event
- Await CEO approval

---

#### POST wiki.approve

**Description:** Approve a wiki entry (CEO only)

**Input:**
```typescript
{
  id: UUID
}
```

**Output:**
```typescript
{
  entry: WikiEntrySchema
}
```

**Errors:**
- `WIKI_ENTRY_NOT_FOUND` (404)
- `WIKI_ENTRY_ALREADY_APPROVED` (400)
- `NOT_CEO` (403)

**Business Logic:**
- Set `status = 'approved'`
- Set `approvedBy = currentUserId`
- Set `approvedAt = NOW()`
- Create new version if editing existing approved entry

---

#### POST wiki.reject

**Description:** Reject a wiki entry (CEO only)

**Input:**
```typescript
{
  id: UUID,
  reason: z.string().min(1)
}
```

**Output:**
```typescript
{
  entry: WikiEntrySchema
}
```

**Errors:**
- `WIKI_ENTRY_NOT_FOUND` (404)
- `WIKI_ENTRY_ALREADY_REJECTED` (400)
- `NOT_CEO` (403)

**Business Logic:**
- Set `status = 'rejected'`
- Set `rejectionReason = reason`

---

### 9. KPI Routes (kpi.ts)

**Middleware:** CEO authentication required

#### GET kpi.get

**Description:** Get latest KPIs for an agent

**Input:**
```typescript
{
  agentId: UUID
}
```

**Output:**
```typescript
{
  kpi: KPISchema,
  agent: AgentSchema,
  historicalKPIs: z.array(KPISchema) // Last 10 KPI records
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)
- `KPI_NOT_FOUND` (404) - No KPI records for this agent yet

---

#### POST kpi.recalculate

**Description:** Manually trigger KPI recalculation for an agent

**Input:**
```typescript
{
  agentId: UUID
}
```

**Output:**
```typescript
{
  previousKPIs: KPISchema.optional(),
  newKPIs: KPISchema,
  changeReason: z.string()
}
```

**Errors:**
- `AGENT_NOT_FOUND` (404)
- `AGENT_ACCESS_DENIED` (403)

**Business Logic:**
- Calculate new KPIs using KPI Algorithm
- Create new KPI record
- Create `kpi_updated` event
- Trigger trust score recalculation (async)

---

### 10. GitHub Routes (github.ts)

**Middleware:** Webhook signature validation

#### POST github.webhook

**Description:** Handle GitHub webhook events

**Input:** Raw GitHub webhook payload

**Output:**
```typescript
{
  received: z.boolean(),
  processed: z.boolean()
}
```

**Errors:** None (always return 200 to GitHub)

**Supported Events:**

**pull_request** (opened, closed, merged):
```typescript
// If PR opened
→ Create 'github_pr_opened' event
→ Link PR to task (if github issue # in PR title)

// If PR merged
→ Create 'github_pr_merged' event
→ Check if linked task should be marked complete
→ Trigger KPI recalculation for assigned agent

// If PR closed (without merge)
→ Log event
→ Optionally reassign task
```

**issues** (opened, assigned, closed):
```typescript
// If issue assigned
→ Create or update task
→ Create 'github_issue_assigned' event
→ Set task.assignedAgentId based on GitHub assignee

// If issue closed
→ Mark related task as completed
```

**issue_comment** (created):
```typescript
→ Create event with comment content
→ Add to agent's messages (pull)
```

**Business Logic:**
- Validate webhook signature
- Parse event type
- Route to appropriate handler
- Create corresponding AgentFlow events
- Sync tasks with GitHub issues

---

## Event Specifications

### Session Events

#### session_start

**Content:**
```typescript
{
  pulledUpdates: {
    tasks: z.number(), // Count of tasks pulled
    messages: z.number(), // Count of messages pulled
    roleChanges: z.number() // Count of role changes pulled
  }
}
```

**Mentions:** []

**Created by:** Agent

---

#### session_log

**Content:**
```typescript
{
  message: z.string(), // Log message
  context: Metadata.optional() // Optional context (file, progress, etc.)
}
```

**Mentions:** []

**Created by:** Agent

---

#### session_stop

**Content:**
```typescript
{
  durationSeconds: z.number().int(),
  tasksWorkedOn: z.array(UUID), // Task IDs worked on
  summary: z.string().optional() // Optional summary
}
```

**Mentions:** []

**Created by:** Agent

---

### Task Events

#### task_assigned

**Content:**
```typescript
{
  taskId: UUID,
  taskTitle: z.string(),
  assignedTo: {
    agentId: UUID,
    agentName: z.string()
  },
  assignedBy: {
    userId: UUID, // CEO who assigned
    userName: z.string()
  },
  priority: PriorityLevel,
  deadline: Timestamp.optional()
}
```

**Mentions:** [assignedAgentId]

**Created by:** CEO (automatic)

---

#### task_completed

**Content:**
```typescript
{
  taskId: UUID,
  taskTitle: z.string(),
  completedBy: {
    agentId: UUID,
    agentName: z.string()
  },
  completedAt: Timestamp,
  duration: z.number().int(), // Minutes from start to completion
  successCriteriaMet: z.array(z.string()) // Which criteria were met
}
```

**Mentions:** [completedByAgentId, taskAssignedByUserId]

**Created by:** Agent (via session)

---

#### task_blocked

**Content:**
```typescript
{
  taskId: UUID,
  taskTitle: z.string(),
  blockedBy: {
    agentId: UUID,
    agentName: z.string()
  },
  blocker: z.string(), // What is blocking
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  requiresAttention: z.boolean() // Does this need CEO attention?
}
```

**Mentions:** [blockedByAgentId, taskAssignedByUserId]

**Created by:** Agent

---

### Communication Events

#### problem_report

**Content:**
```typescript
{
  title: z.string(),
  description: z.string(),
  context: {
    file: z.string().optional(), // File where problem occurred
    lineNumber: z.number().int().optional(),
    error: z.string().optional(), // Error message
    stackTrace: z.string().optional()
  },
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  category: z.enum(['bug', 'architecture', 'performance', 'security', 'other'])
}
```

**Mentions:** [] (Agent's supervisor)

**Created by:** Agent

---

#### advice_given

**Content:**
```typescript
{
  topic: z.string(),
  advice: z.string(),
  context: Metadata.optional(),
  relatedTask: UUID.optional(), // If advice relates to specific task
  confidence: z.number().min(0).max(1) // Confidence level in advice
}
```

**Mentions:** [recipientAgentId]

**Created by:** Organization-level agent

---

#### question_asked

**Content:**
```typescript
{
  question: z.string(),
  context: {
    relatedTask: UUID.optional(),
    relatedFile: z.string().optional(),
    whatIVeTried: z.string().optional()
  },
  urgency: z.enum(['low', 'medium', 'high', 'critical'])
}
```

**Mentions:** [] (Agent's supervisor)

**Created by:** Agent

---

### Code Review Events

#### review_requested

**Content:**
```typescript
{
  pullRequestId: UUID, // Internal PR tracking ID
  githubPullRequestNumber: z.number().int(),
  githubPullRequestUrl: z.string().url(),
  title: z.string(),
  description: z.string().optional(),
  changedFiles: z.number().int(),
  additions: z.number().int(),
  deletions: z.number().int(),
  requestedBy: {
    agentId: UUID,
    agentName: z.string()
  }
}
```

**Mentions:** [reviewerAgentId]

**Created by:** Agent

---

#### review_response

**Content:**
```typescript
{
  pullRequestId: UUID,
  reviewer: {
    agentId: UUID,
    agentName: z.string()
  },
  decision: z.enum(['approve', 'request_changes', 'comment']),
  comments: z.string().optional(),
  requestedChanges: z.array(z.string()).optional(), // If requesting changes
  reviewedAt: Timestamp
}
```

**Mentions:** [requestedByAgentId]

**Created by:** Supervisor agent

---

### GitHub Events

#### github_pr_opened

**Content:**
```typescript
{
  githubPullRequestNumber: z.number().int(),
  githubPullRequestUrl: z.string().url(),
  title: z.string(),
  author: z.string(), // GitHub username
  openedAt: Timestamp,
  linkedTaskId: UUID.optional(), // If PR title references issue #
  repository: z.string()
}
```

**Mentions:** [linkedTaskAssignedAgentId]

**Created by:** System (automatic)

---

#### github_pr_merged

**Content:**
```typescript
{
  githubPullRequestNumber: z.number().int(),
  githubPullRequestUrl: z.string().url(),
  title: z.string(),
  mergedBy: z.string(), // GitHub username
  mergedAt: Timestamp,
  linkedTaskId: UUID.optional(),
  repository: z.string()
}
```

**Mentions:** [linkedTaskAssignedAgentId]

**Created by:** System (automatic)

---

#### github_issue_assigned

**Content:**
```typescript
{
  githubIssueNumber: z.number().int(),
  githubIssueUrl: z.string().url(),
  title: z.string(),
  assignedTo: z.string(), // GitHub username
  assignedAt: Timestamp,
  repository: z.string()
}
```

**Mentions:** []

**Created by:** System (automatic)

---

### System Events

#### kpi_updated

**Content:**
```typescript
{
  agentId: UUID,
  agentName: z.string(),
  previousKPIs: KPIShape.optional(), // Undefined if first KPI
  newKPIs: KPIShape,
  changes: z.array(z.object({
    metric: z.string(),
    oldValue: z.any(),
    newValue: z.any(),
    change: z.number() // Delta or percentage
  })),
  reason: z.string(), // Why KPIs were recalculated
  recalculatedAt: Timestamp
}

type KPIShape = {
  tasksCompleted: number
  codeQualityScore: number
  positiveFeedbackCount: number
  featureCompletionRate: number
  bugsIntroduced: number
  deploymentFailures: number
  codeChurn: number
  averageTaskDuration: number
}
```

**Mentions:** [agentId]

**Created by:** System (automatic)

---

#### trust_score_changed

**Content:**
```typescript
{
  agentId: UUID,
  agentName: z.string(),
  previousTrustScore: z.number().min(0).max(100),
  newTrustScore: z.number().min(0).max(100),
  change: z.number(), // Delta (+ or -)
  reason: z.string(), // Why trust score changed
  factors: z.array(z.object({
    factor: z.string(), // e.g., "tasks_completed_trend"
    impact: z.number(), // Contribution to change
    direction: z.enum(['positive', 'negative'])
  })),
  changedAt: Timestamp
}
```

**Mentions:** [agentId]

**Created by:** System (automatic)

---

### Knowledge Events

#### wiki_contribution

**Content:**
```typescript
{
  entryId: UUID,
  title: z.string(),
  slug: z.string(),
  status: WikiEntryStatus, // 'pending_approval' when created
  proposedBy: {
    agentId: UUID,
    agentName: z.string()
  },
  tags: z.array(z.string()),
  version: z.number().int(),
  isUpdate: z.boolean(), // true if updating existing entry
  parentEntryId: UUID.optional() // If this is a new version
}
```

**Mentions:** []

**Created by:** Organization-level agent

---

## Business Logic Algorithms

### KPI Calculation Algorithm

**Trigger:** After significant agent actions (session_stop, task_completed, pr_merged)

**Algorithm:**

```typescript
function calculateKPIs(agentId: UUID): KPIRecord {
  // 1. Fetch agent's history
  const agent = getAgent(agentId)
  const completedTasks = getTasks(agentId, { status: 'completed' })
  const sessions = getSessions(agentId)
  const pullRequests = getPullRequests(agentId)

  // 2. Calculate metrics

  // TASKS COMPLETED
  const tasksCompleted = completedTasks.length

  // CODE QUALITY SCORE (0-100)
  const codeQualityScore = calculateCodeQuality(pullRequests)
  // Formula:
  // - Base score: 50
  // - +10 for each PR approved on first review
  // - -5 for each PR requiring changes
  // - -10 for each PR with linting errors
  // - Capped at 0-100

  function calculateCodeQuality(prs: PullRequest[]): number {
    let score = 50

    prs.forEach(pr => {
      if (pr.approvedOnFirstReview) score += 10
      if (pr.changesRequested > 0) score -= 5 * pr.changesRequested
      if (pr.lintingErrors > 0) score -= 10
    })

    return Math.max(0, Math.min(100, score))
  }

  // POSITIVE FEEDBACK COUNT
  const positiveFeedbackCount = pullRequests.filter(
    pr => pr.approvedOnFirstReview
  ).length

  // FEATURE COMPLETION RATE (0-1)
  const featureCompletionRate = calculateCompletionRate(completedTasks)
  // Formula:
  // - Count of completed tasks / Count of assigned tasks
  // - Only count tasks assigned > 7 days ago (to give new tasks time)

  function calculateCompletionRate(tasks: Task[]): number {
    const assignedTasks = tasks.filter(t =>
      t.assignedAt && daysBetween(t.assignedAt, now) > 7
    )

    if (assignedTasks.length === 0) return 1.0

    const completedTasks = assignedTasks.filter(t => t.status === 'completed')

    return completedTasks.length / assignedTasks.length
  }

  // BUGS INTRODUCED
  const bugsIntroduced = getBugsIntroduced(agentId)
  // Count of tasks/PRs marked as bug fixes or with "bug" label

  // DEPLOYMENT FAILURES
  const deploymentFailures = getDeploymentFailures(agentId)
  // Count of failed deployments linked to agent's commits

  // CODE CHURN
  const codeChurn = calculateCodeChurn(agentId)
  // Total lines added + deleted in last 30 days

  function calculateCodeChurn(agentId: UUID): number {
    const commits = getCommits(agentId, { since: daysAgo(30) })
    return commits.reduce((sum, commit) =>
      sum + commit.linesAdded + commit.linesDeleted
    , 0)
  }

  // AVERAGE TASK DURATION (in minutes)
  const averageTaskDuration = calculateAverageTaskDuration(completedTasks)
  // Mean of (completedAt - startedAt) for all completed tasks

  function calculateAverageTaskDuration(tasks: Task[]): number {
    if (tasks.length === 0) return 0

    const durations = tasks
      .filter(t => t.startedAt && t.completedAt)
      .map(t => minutesBetween(t.startedAt, t.completedAt))

    return durations.reduce((sum, d) => sum + d, 0) / durations.length
  }

  // 3. Fetch previous KPIs for trend calculation
  const previousKPIs = getLatestKPI(agentId)

  // 4. Calculate trends
  const trendData = calculateTrends(previousKPIs, newMetrics)

  function calculateTrends(prev: KPIRecord | null, curr: KPIMetrics): TrendData {
    if (!prev) {
      return {
        tasksCompletedTrend: 'stable',
        codeQualityTrend: 'stable',
        overallTrend: 'stable'
      }
    }

    const tasksTrend = curr.tasksCompleted > prev.metrics.tasksCompleted
      ? 'up'
      : curr.tasksCompleted < prev.metrics.tasksCompleted
      ? 'down'
      : 'stable'

    const qualityTrend = curr.codeQualityScore > prev.metrics.codeQualityScore
      ? 'up'
      : curr.codeQualityScore < prev.metrics.codeQualityScore
      ? 'down'
      : 'stable'

    // Overall trend: weighted average of individual trends
    const overallScore =
      (curr.codeQualityScore / 100 * 0.4) +
      (curr.featureCompletionRate * 0.3) +
      (Math.max(0, 100 - curr.bugsIntroduced * 10) / 100 * 0.2) +
      (Math.max(0, 100 - curr.deploymentFailures * 10) / 100 * 0.1)

    const previousOverallScore =
      (prev.metrics.codeQualityScore / 100 * 0.4) +
      (prev.metrics.featureCompletionRate * 0.3) +
      (Math.max(0, 100 - prev.metrics.bugsIntroduced * 10) / 100 * 0.2) +
      (Math.max(0, 100 - prev.metrics.deploymentFailures * 10) / 100 * 0.1)

    const overallTrend = overallScore > previousOverallScore
      ? 'improving'
      : overallScore < previousOverallScore
      ? 'declining'
      : 'stable'

    return {
      tasksCompletedTrend,
      codeQualityTrend,
      overallTrend
    }
  }

  // 5. Create KPI record
  const kpiRecord = {
    agentId,
    recordedAt: now(),
    metrics: {
      tasksCompleted,
      codeQualityScore,
      positiveFeedbackCount,
      featureCompletionRate,
      bugsIntroduced,
      deploymentFailures,
      codeChurn,
      averageTaskDuration
    },
    trendData,
    calculatedAt: now()
  }

  // 6. Save to database
  return createKPIRecord(kpiRecord)
}
```

---

### Trust Score Calculation Algorithm

**Trigger:** After KPI recalculation

**Algorithm:**

```typescript
function calculateTrustScore(agentId: UUID): number {
  // 1. Fetch agent's KPI history (last 10 records)
  const kpiHistory = getKPIHistory(agentId, { limit: 10 })

  if (kpiHistory.length === 0) {
    // New agent: default trust score
    return 50.0
  }

  const latestKPI = kpiHistory[0]
  const previousKPI = kpiHistory[1] // Second-latest

  // 2. Calculate base score from KPIs
  const baseScore = calculateBaseScore(latestKPI)

  function calculateBaseScore(kpi: KPIRecord): number {
    // Weighted scoring (total: 100 points)

    let score = 0

    // Code quality (40 points)
    score += (kpi.metrics.codeQualityScore / 100) * 40

    // Feature completion rate (30 points)
    score += kpi.metrics.featureCompletionRate * 30

    // Low bugs (20 points)
    // 0 bugs = 20 points, 5+ bugs = 0 points
    score += Math.max(0, 20 - kpi.metrics.bugsIntroduced * 4)

    // Low deployment failures (10 points)
    // 0 failures = 10 points, 3+ failures = 0 points
    score += Math.max(0, 10 - kpi.metrics.deploymentFailures * 3.33)

    return Math.max(0, Math.min(100, score))
  }

  // 3. Apply trend modifier
  const trendModifier = calculateTrendModifier(latestKPI, previousKPI)

  function calculateTrendModifier(latest: KPIRecord, previous: KPIRecord | null): number {
    if (!previous) return 0

    let modifier = 0

    // Overall trend bonus/penalty
    if (latest.trendData.overallTrend === 'improving') {
      modifier += 5
    } else if (latest.trendData.overallTrend === 'declining') {
      modifier -= 5
    }

    // Code quality trend bonus/penalty
    if (latest.trendData.codeQualityTrend === 'up') {
      modifier += 2
    } else if (latest.trendData.codeQualityTrend === 'down') {
      modifier -= 2
    }

    // Task completion trend bonus/penalty
    if (latest.trendData.tasksCompletedTrend === 'up') {
      modifier += 1
    } else if (latest.trendData.tasksCompletedTrend === 'down') {
      modifier -= 1
    }

    return modifier
  }

  // 4. Apply consistency bonus
  const consistencyBonus = calculateConsistencyBonus(kpiHistory)

  function calculateConsistencyBonus(history: KPIRecord[]): number {
    if (history.length < 3) return 0

    // Calculate standard deviation of overall scores
    const scores = history.map(kpi => {
      return (kpi.metrics.codeQualityScore / 100 * 0.4) +
             (kpi.metrics.featureCompletionRate * 0.3) +
             (Math.max(0, 100 - kpi.metrics.bugsIntroduced * 10) / 100 * 0.2) +
             (Math.max(0, 100 - kpi.metrics.deploymentFailures * 10) / 100 * 0.1)
    })

    const mean = scores.reduce((sum, s) => sum + s, 0) / scores.length
    const variance = scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length
    const stdDev = Math.sqrt(variance)

    // Lower standard deviation = higher consistency
    // stdDev of 0 = +5 bonus, stdDev of 0.3+ = 0 bonus
    const consistencyBonus = Math.max(0, 5 - (stdDev / 0.06))

    return consistencyBonus
  }

  // 5. Calculate final trust score
  let finalScore = baseScore + trendModifier + consistencyBonus

  // 6. Apply bounds (0-100)
  finalScore = Math.max(0, Math.min(100, finalScore))

  // 7. Round to 2 decimal places
  finalScore = Math.round(finalScore * 100) / 100

  return finalScore
}

// PROBATION TRIGGER
// If trust score drops below 30, set agent status to 'probation'
function checkProbationTrigger(agentId: UUID): void {
  const agent = getAgent(agentId)
  const latestKPI = getLatestKPI(agentId)

  // Trigger conditions:
  // 1. Trust score < 30
  // 2. 3 consecutive PRs rejected
  // 3. Code quality score < 20
  // 4. 5+ bugs introduced in last 10 tasks

  const shouldTrigger =
    agent.trustScore < 30 ||
    latestKPI?.metrics.codeQualityScore < 20 ||
    getConsecutiveRejectedPRs(agentId) >= 3 ||
    getRecentBugsCount(agentId, 10) >= 5

  if (shouldTrigger && agent.status !== 'probation') {
    updateAgent(agentId, { status: 'probation' })
    createEvent('trust_score_changed', {
      agentId,
      previousStatus: agent.status,
      newStatus: 'probation',
      reason: 'Automatic probation trigger activated'
    })
  }
}

// PROBATION RECOVERY
// If agent is on probation and performance improves, lift probation
function checkProbationRecovery(agentId: UUID): void {
  const agent = getAgent(agentId)

  if (agent.status !== 'probation') return

  const latestKPI = getLatestKPI(agentId)

  // Recovery conditions (must meet ALL):
  // 1. Trust score >= 50
  // 2. Code quality score >= 60
  // 3. 5+ successful task completions
  // 4. Consistent improvement over last 3 KPIs

  const kpiHistory = getKPIHistory(agentId, { limit: 3 })

  const canRecover =
    agent.trustScore >= 50 &&
    latestKPI?.metrics.codeQualityScore >= 60 &&
    latestKPI?.metrics.tasksCompleted >= 5 &&
    kpiHistory.every(kpi => kpi.trendData.overallTrend === 'improving')

  if (canRecover) {
    updateAgent(agentId, { status: 'active' })
    createEvent('trust_score_changed', {
      agentId,
      previousStatus: 'probation',
      newStatus: 'active',
      reason: 'Probation lifted due to consistent improvement'
    })
  }
}
```

---

### Session Pull Algorithm

**Trigger:** session.start

**Algorithm:**

```typescript
function pullUpdatesOnSessionStart(agentId: UUID, projectId: UUID): PulledUpdates {
  // 1. Pull tasks
  const tasks = pullTasks(agentId, projectId)

  function pullTasks(agentId: UUID, projectId: UUID): Task[] {
    // Get all tasks for this agent in this project
    return db.tasks.findMany({
      where: {
        projectId,
        assignedAgentId: agentId,
        status: { in: ['assigned', 'in_progress', 'blocked'] },
        deletedAt: null
      },
      orderBy: [
        { priority: 'asc' }, // P0 first, then P1, P2, P3
        { deadline: 'asc' }  // Earlier deadlines first
      ]
    })
  }

  // 2. Pull messages (events mentioning this agent)
  const messages = pullMessages(agentId)

  function pullMessages(agentId: UUID): Event[] {
    // Get last session stop time for this agent
    const lastSession = db.sessions.findFirst({
      where: {
        agentId,
        status: 'stopped'
      },
      orderBy: { stoppedAt: 'desc' }
    })

    const since = lastSession?.stoppedAt || agent.createdAt

    // Get events mentioning this agent since last session
    return db.events.findMany({
      where: {
        mentions: { array_contains: agentId },
        timestamp: { gte: since },
        // Exclude session events (agent already knows about these)
        type: { notIn: ['session_start', 'session_log', 'session_stop'] }
      },
      orderBy: { timestamp: 'asc' },
      limit: 100
    })
  }

  // 3. Pull role changes
  const roleChanges = pullRoleChanges(agentId)

  function pullRoleChanges(agentId: UUID): RoleChange[] {
    const lastSession = db.sessions.findFirst({
      where: {
        agentId,
        status: 'stopped'
      },
      orderBy: { stoppedAt: 'desc' }
    })

    const since = lastSession?.stoppedAt || agent.createdAt

    // Check for changes to agent's role definition
    // For now, we'll check if capabilities or settings changed
    // In production, this could use an audit table

    const agent = db.agents.findFirst({ where: { id: agentId } })
    const previousState = lastSession?.metadata?.agentSnapshot

    if (!previousState) {
      return [] // First session, no previous state
    }

    const changes: RoleChange[] = []

    // Check capabilities changes
    const addedCapabilities = agent.capabilities.filter(
      c => !previousState.capabilities.includes(c)
    )
    const removedCapabilities = previousState.capabilities.filter(
      c => !agent.capabilities.includes(c)
    )

    if (addedCapabilities.length > 0) {
      changes.push({
        field: 'capabilities',
        type: 'added',
        values: addedCapabilities,
        changedAt: agent.updatedAt
      })
    }

    if (removedCapabilities.length > 0) {
      changes.push({
        field: 'capabilities',
        type: 'removed',
        values: removedCapabilities,
        changedAt: agent.updatedAt
      })
    }

    // Check settings changes
    const settingsChanges = Object.keys(agent.settings).filter(
      key => agent.settings[key] !== previousState.settings[key]
    )

    settingsChanges.forEach(key => {
      changes.push({
        field: `settings.${key}`,
        type: 'changed',
        oldValue: previousState.settings[key],
        newValue: agent.settings[key],
        changedAt: agent.updatedAt
      })
    })

    return changes
  }

  return {
    tasks,
    messages,
    roleChanges
  }
}
```

---

## Error Handling

### Error Codes

```typescript
// Authentication Errors
AUTH_EMAIL_ALREADY_EXISTS = 409
AUTH_WEAK_PASSWORD = 400
AUTH_INVALID_CREDENTIALS = 401
AUTH_ACCOUNT_SUSPENDED = 403
AUTH_INVALID_TOKEN = 401
AUTH_SESSION_EXPIRED = 401

// Workspace Errors
WORKSPACE_NOT_FOUND = 404
WORKSPACE_ACCESS_DENIED = 403
WORKSPACE_SLUG_ALREADY_EXISTS = 409
WORKSPACE_INVALID_SLUG = 400
WORKSPACE_NOT_EMPTY = 400

// Project Errors
PROJECT_NOT_FOUND = 404
PROJECT_ACCESS_DENIED = 403
PROJECT_SLUG_ALREADY_EXISTS = 409
PROJECT_INVALID_GITHUB_INSTALLATION = 400
PROJECT_HAS_ACTIVE_AGENTS = 400
PROJECT_HAS_ACTIVE_TASKS = 400

// Agent Errors
AGENT_NOT_FOUND = 404
AGENT_ACCESS_DENIED = 403
AGENT_CODE_ALREADY_EXISTS = 409
AGENT_INVALID_LEVEL = 400
AGENT_INACTIVE = 403
AGENT_ON_PROBATION = 403
AGENT_HAS_ACTIVE_SESSION = 400
AGENT_HAS_ASSIGNED_TASKS = 400
AGENT_NOT_ORGANIZATION_LEVEL = 403
AGENT_SESSION_MISMATCH = 403

// Session Errors
SESSION_NOT_FOUND = 404
SESSION_ACCESS_DENIED = 403
SESSION_ALREADY_STOPPED = 400
SESSION_ALREADY_ACTIVE = 400

// Task Errors
TASK_NOT_FOUND = 404
TASK_ACCESS_DENIED = 403
TASK_ALREADY_EXISTS = 409
TASK_INVALID_AGENT_ASSIGNMENT = 400

// Event Errors
EVENT_NOT_FOUND = 404
EVENT_ACCESS_DENIED = 403

// Wiki Errors
WIKI_ENTRY_NOT_FOUND = 404
WIKI_ENTRY_ACCESS_DENIED = 403
WIKI_ENTRY_SLUG_ALREADY_EXISTS = 409
WIKI_ENTRY_ALREADY_APPROVED = 400
WIKI_ENTRY_ALREADY_REJECTED = 400

// KPI Errors
KPI_NOT_FOUND = 404

// General Errors
NOT_CEO = 403
INTERNAL_ERROR = 500
VALIDATION_ERROR = 400
```

### Error Response Format

```typescript
{
  error: {
    code: z.string(), // e.g., "AGENT_NOT_FOUND"
    message: z.string(), // Human-readable message
    details: z.any().optional(), // Additional error details
    timestamp: Timestamp
  }
}
```

---

## Webhooks

### GitHub Webhook

**Endpoint:** `POST /api/webhooks/github`

**Authentication:** HMAC signature verification

**Headers:**
```http
X-Hub-Signature-256: sha256=<signature>
X-GitHub-Event: <event_type>
X-GitHub-Delivery: <delivery_id>
```

**Verification:**
```typescript
function verifyGitHubSignature(payload: string, signature: string): boolean {
  const secret = process.env.GITHUB_WEBHOOK_SECRET
  const hmac = crypto.createHmac('sha256', secret)
  const digest = hmac.update(payload).digest('hex')
  return `sha256=${digest}` === signature
}
```

**Events Handled:**
- `pull_request` (opened, closed, merged)
- `issues` (opened, assigned, closed)
- `issue_comment` (created)

---

## Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentflow

# API
API_PORT=3001
NODE_ENV=development

# CEO Authentication (better-auth)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3001

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Agent Authentication
JWT_SECRET=your-jwt-secret-min-32-chars
API_KEY_SALT=your-salt-for-api-keys

# GitHub Webhooks
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# GitHub App (optional)
GITHUB_APP_ID=your-github-app-id
GITHUB_APP_PRIVATE_KEY=your-github-app-private-key

# Session Secrets
SESSION_SECRET=your-session-secret-min-32-chars
```

---

## Rate Limiting

### Default Limits

```typescript
// CEO routes
const CEO_RATE_LIMIT = {
  window: 60000, // 1 minute
  max: 100 // requests per minute
}

// Agent routes
const AGENT_RATE_LIMIT = {
  window: 60000, // 1 minute
  max: 60 // requests per minute
}

// Webhook routes
const WEBHOOK_RATE_LIMIT = {
  window: 1000, // 1 second
  max: 10 // requests per second
}
```

---

## Version

**API Version:** 1.0.0
**Last Updated:** 2025-01-19
**Status:** Specification Complete
