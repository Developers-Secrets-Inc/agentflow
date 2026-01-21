# Data Models (Phase 0)

## Data Models (Phase 0)

### Role Model

**Note**: Roles are stored on the API (remote), not locally. The local model is for reference only.

```python
class Role(BaseModel):
    """Role template stored on the API"""
    id: str  # UUID
    slug: str  # e.g., "python-dev"
    name: str  # e.g., "Python Developer"
    description: str  # System prompt for AI
    level: Literal["organization", "project"]
    documents: List["RoleDocument"]  # Associated documents
    version: int  # Role version for tracking updates
    created_at: datetime
    updated_at: datetime


class RoleDocument(BaseModel):
    """Document within a role"""
    id: str  # UUID
    role_id: str  # Parent role
    name: str  # e.g., "testing-guidelines"
    filename: str  # e.g., "testing-guidelines.md"
    content: str  # Markdown content
    content_type: Literal["guidelines", "concepts", "methodology", "conventions", "examples"]
    order: int  # Display order
    created_at: datetime
    updated_at: datetime
```

### Agent Model

```python
class Agent(BaseModel):
    id: str  # UUID
    workspace_id: str  # Organization UUID
    project_id: Optional[str]  # NULL for org-level agents
    agent_level: Literal["organization", "project"]
    agent_code: str  # e.g., "agent-dev-001"
    name: str  # e.g., "Jean" or "Alice"
    role_slug: str  # Reference to role (e.g., "python-dev")
    status: Literal["active", "probation", "inactive", "terminated"]
    trust_score: float  # 0-100, starts at 50
    settings: Dict[str, Any]  # Agent-specific settings
    last_pulled_at: Optional[datetime]  # Last pull time
    role_version: Optional[int]  # Last pulled role version
    skills_generated: List[str]  # List of generated skill names
    created_at: datetime
    updated_at: datetime

    # Computed properties
    @property
    def is_org_level(self) -> bool:
        return self.agent_level == "organization"

    @property
    def is_project_level(self) -> bool:
        return self.agent_level == "project"
```

### Session Model

```python
class Session(BaseModel):
    id: str  # UUID
    agent_id: str  # Agent UUID
    project_id: str  # Project UUID
    status: Literal["started", "logging", "stopped"]
    started_at: datetime
    stopped_at: Optional[datetime]
    duration_seconds: Optional[int]
    tasks_worked_on: List[str]  # Task UUIDs
    pull_summary: Optional[Dict[str, Any]]  # Summary from initial pull
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    @property
    def is_active(self) -> bool:
        return self.status in ["started", "logging"]

    @property
    def duration(self) -> Optional[timedelta]:
        if self.duration_seconds:
            return timedelta(seconds=self.duration_seconds)
        return None
```

### Task Model

```python
class Task(BaseModel):
    id: str  # UUID
    project_id: str  # Project UUID
    type: Literal["development", "bug", "review"]
    title: str
    description: Optional[str]
    assigned_agent_id: Optional[str]  # Agent UUID
    parent_task_id: Optional[str]  # For reviews (points to original task)
    status: Literal["backlog", "assigned", "in_progress", "ready_review", "completed", "blocked", "cancelled"]
    priority: Literal["P0", "P1", "P2", "P3"]
    tags: List[str]
    deadline: Optional[datetime]
    github_issue_id: Optional[int]
    metadata: Dict[str, Any]  # Custom fields
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Computed properties
    @property
    def is_review(self) -> bool:
        return self.type == "review"

    @property
    def is_active(self) -> bool:
        return self.status not in ["completed", "cancelled"]
```

### Message Model

```python
class Message(BaseModel):
    id: str  # UUID
    from_agent_id: str  # Sender agent UUID
    to_agent_id: str  # Receiver agent UUID (supervisor)
    type: Literal["question", "report", "request", "update"]
    content: str
    priority: Literal["P0", "P1", "P2", "P3"]
    related_task_id: Optional[str]  # Optional task being discussed
    status: Literal["sent", "read", "answered"]
    created_at: datetime
    answered_at: Optional[datetime]

    # Computed properties
    @property
    def is_unread(self) -> bool:
        return self.status == "sent"

    @property
    def is_pending(self) -> bool:
        return self.status in ["sent", "read"]
```

### Event Model (for Logs)

```python
class Event(BaseModel):
    id: str  # UUID
    type: Literal[
        "session_start",
        "session_log",
        "session_stop",
        "task_assigned",
        "task_completed",
        "problem_report",
        "question_asked",
        "advice_given",
        ...
    ]
    author_id: Optional[str]  # Agent UUID (NULL for system events)
    session_id: Optional[str]  # Session UUID
    project_id: Optional[str]  # Project UUID
    content: Dict[str, Any]  # Event-specific data
    mentions: List[str]  # Agent UUIDs mentioned
    metadata: Dict[str, Any]  # Additional context
    timestamp: datetime
    created_at: datetime
```

### Database Structure (Phase 0)

```json
{
  "users": [...],
  "organizations": [...],
  "projects": [...],
  "agents": [
    {
      "id": "uuid",
      "workspace_id": "org-uuid",
      "project_id": "project-uuid",
      "agent_level": "project",
      "agent_code": "agent-dev-001",
      "name": "Jean",
      "role_slug": "python-dev",
      "status": "active",
      "trust_score": 52.5,
      "settings": {},
      "last_pulled_at": "2025-01-21T10:00:00Z",
      "role_version": 3,
      "skills_generated": ["python-testing", "python-api", "python-async"],
      "created_at": "2025-01-15T09:00:00Z",
      "updated_at": "2025-01-21T10:00:00Z"
    }
  ],
  "sessions": [
    {
      "id": "uuid",
      "agent_id": "agent-uuid",
      "project_id": "project-uuid",
      "status": "logging",
      "started_at": "2025-01-21T09:00:00Z",
      "stopped_at": null,
      "duration_seconds": null,
      "tasks_worked_on": [],
      "pull_summary": {
        "tasks_new": 2,
        "messages": 1
      },
      "metadata": {},
      "created_at": "2025-01-21T09:00:00Z",
      "updated_at": "2025-01-21T09:00:00Z"
    }
  ],
  "events": [
    {
      "id": "uuid",
      "type": "session_log",
      "author_id": "agent-uuid",
      "session_id": "session-uuid",
      "project_id": "project-uuid",
      "content": {
        "message": "Implementing user authentication",
        "context": {
          "file": "src/auth.py",
          "progress": 25
        }
      },
      "mentions": [],
      "metadata": {
        "log_type": "activity"
      },
      "timestamp": "2025-01-21T09:15:00Z",
      "created_at": "2025-01-21T09:15:00Z"
    }
  ],
  "tasks": [
    {
      "id": "uuid",
      "project_id": "project-uuid",
      "type": "development",
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication to the API",
      "assigned_agent_id": "agent-uuid",
      "parent_task_id": null,
      "status": "in_progress",
      "priority": "P1",
      "tags": ["authentication", "security", "api"],
      "deadline": "2025-02-01T00:00:00Z",
      "github_issue_id": null,
      "metadata": {},
      "created_at": "2025-01-21T08:00:00Z",
      "updated_at": "2025-01-21T10:30:00Z",
      "started_at": "2025-01-21T09:00:00Z",
      "completed_at": null
    },
    {
      "id": "uuid",
      "project_id": "project-uuid",
      "type": "bug",
      "title": "Fix login error",
      "description": "Users cannot log in with valid credentials",
      "assigned_agent_id": "agent-uuid",
      "parent_task_id": null,
      "status": "backlog",
      "priority": "P0",
      "tags": ["bug", "urgent", "login"],
      "deadline": null,
      "github_issue_id": null,
      "metadata": {},
      "created_at": "2025-01-21T08:00:00Z",
      "updated_at": "2025-01-21T08:00:00Z",
      "started_at": null,
      "completed_at": null
    }
  ],
  "messages": [
    {
      "id": "uuid",
      "from_agent_id": "agent-dev-uuid",
      "to_agent_id": "agent-lead-uuid",
      "type": "question",
      "content": "Should we use bcrypt or argon2 for password hashing?",
      "priority": "P1",
      "related_task_id": "task-uuid",
      "status": "sent",
      "created_at": "2025-01-21T10:15:00Z",
      "answered_at": null
    }
  ],
  "hierarchy": {
    "organization": {
      "tree_structure": "cto→architect,cto→tech-lead,cto→pm"
    },
    "project": {
      "project-uuid": {
        "tree_structure": "tech-lead→senior-dev→dev,tech-lead→qa"
      }
    }
  }
}
```

---
