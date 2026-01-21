# Future Feature: Organizational Knowledge Base

## Overview

An organizational knowledge base (wiki) system that allows agents to capture, share, and retrieve solutions, patterns, decisions, and best practices. The knowledge base serves as a persistent, searchable repository of organizational intelligence that agents can leverage to avoid reinventing solutions and accelerate problem-solving.

## Why It Matters

**Prevent Knowledge Silos**: As agents complete tasks, they accumulate valuable knowledge about the codebase, architecture patterns, debugging approaches, and domain-specific insights. Without a knowledge base, this knowledge remains trapped in individual agent sessions and chat history.

**Accelerate Onboarding**: New agents (or new instances of existing agents) can rapidly get up to speed by accessing the collective knowledge of the organization, reducing ramp-up time from days to hours.

**Improve Decision Quality**: Agents can make better decisions by understanding past decisions, their rationale, and their outcomes. The knowledge base captures the "why" behind architectural and implementation choices.

**Enable Continuous Learning**: As the organization learns and evolves, the knowledge base grows and improves, creating a virtuous cycle of increasing organizational intelligence.

**Reduce Redundancy**: Agents can quickly discover if a problem has already been solved, avoiding duplicate effort and ensuring consistency across the codebase.

## How It Works

### Knowledge Entry Lifecycle

```
┌─────────────┐
│  Create     │  Agent creates knowledge entry during/after task
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Categorize │  Assign type, tags, and metadata
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Review     │  Optional peer review for quality assurance
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Publish    │  Entry becomes searchable in knowledge base
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Evolve     │  Entries can be updated, versioned, deprecated
└─────────────┘
```

### Knowledge Types

1. **Solutions**: Complete solutions to specific problems with code examples
2. **Patterns**: Reusable architectural or design patterns
3. **Decisions**: Records of significant decisions with rationale
4. **Checklists**: Step-by-step procedures for common tasks
5. **Troubleshooting**: Debugging guides and known issues
6. **Best Practices**: Recommended approaches and conventions
7. **Glossary**: Domain-specific terminology and concepts

### Search & Discovery

Agents can search the knowledge base using:
- **Full-text search**: Find entries by content
- **Tag-based filtering**: Filter by technology, domain, task type
- **Semantic search**: Find similar entries even without exact keyword matches (Phase 2+)
- **Related entries**: Discover connected knowledge

### Integration with Agent Workflows

- **Automatic capture**: Agent can capture key insights during task execution
- **Contextual suggestions**: Agent suggests relevant knowledge entries during tasks
- **Post-task documentation**: Agent creates knowledge entries as part of task completion
- **Query during execution**: Agent can query knowledge base during task execution

## Usage Examples

### Creating Knowledge Entries

```bash
# Create a solution entry
$ agentflow knowledge create \
  --type solution \
  --title "Fixing race condition in WebSocket message handler" \
  --tags "websocket,race-condition,concurrency" \
  --task-id task_abc123

# Opens editor for content
# Agent writes detailed solution with code examples
```

**Content Template**:
```markdown
## Problem
Race condition occurring when multiple WebSocket messages arrive simultaneously for the same session.

## Root Cause
The WebSocket handler was modifying shared session state without proper locking, leading to:
- Lost message updates
- Inconsistent session state
- Intermittent test failures

## Solution
Implemented async lock using asyncio.Lock() to serialize access to session state:

\`\`\`python
class WebSocketMessageHandler:
    def __init__(self):
        self._session_locks = {}  # session_id -> Lock

    async def handle_message(self, session_id: str, message: dict):
        lock = self._session_locks.setdefault(session_id, asyncio.Lock())
        async with lock:
            await self._update_session_state(session_id, message)
\`\`\`

## Testing
Added integration test with concurrent message flooding to verify fix.

## References
- Task: task_abc123
- Commit: a1b2c3d4
```

```bash
✓ Knowledge entry created: KB-2024-001
  Title: Fixing race condition in WebSocket message handler
  Type: solution
  Tags: websocket, race-condition, concurrency
```

### Creating a Pattern Entry

```bash
$ agentflow knowledge create \
  --type pattern \
  --title "Repository Pattern with Async Caching" \
  --tags "pattern,repository,async,cache"
```

**Content**:
```markdown
## Pattern: Repository with Async Caching

### Context
Need to provide data access with caching for frequently accessed entities.

### Implementation
\`\`\`python
class CachedRepository(Generic[T]):
    def __init__(self, session: AsyncSession, ttl: int = 300):
        self._session = session
        self._cache = {}
        self._ttl = ttl

    async def get(self, id: str) -> Optional[T]:
        # Check cache
        if cached := self._cache.get(id):
            if time.time() - cached['timestamp'] < self._ttl:
                return cached['entity']

        # Query database
        entity = await self._session.get(Entity, id)

        # Update cache
        if entity:
            self._cache[id] = {
                'entity': entity,
                'timestamp': time.time()
            }

        return entity
\`\`\`

### Benefits
- Reduces database load
- Improves response time
- Simple implementation

### When to Use
- Read-heavy workloads
- Entities that change infrequently
- When eventual consistency is acceptable

### When NOT to Use
- Strong consistency requirements
- Real-time data
- Write-heavy workloads
```

### Creating a Decision Record

```bash
$ agentflow knowledge create \
  --type decision \
  --title "Choosing Pydantic for data validation" \
  --tags "decision,validation,pydantic"
```

**Content**:
```markdown
## Decision: Use Pydantic for Data Validation

Date: 2024-01-15
Status: Accepted

### Context
Need a robust data validation layer for API inputs and configuration.

### Decision
Use Pydantic as the primary validation library across the project.

### Rationale
**Pros:**
- Native Python type annotations
- Excellent performance (Rust core)
- Great error messages
- TypeScript export support
- Widely adopted in Python ecosystem
- Integrates well with FastAPI

**Cons:**
- Additional dependency
- Learning curve for team members unfamiliar
- Migration effort from existing code

**Alternatives Considered:**
1. **Marshmallow**: More mature but slower, requires separate schema definition
2. **Cerberus**: Lightweight but less feature-rich
3. **Custom validation**: Too much maintenance burden

### Impact
- All API endpoints now use Pydantic models
- Configuration files validated with Pydantic
- Reduced validation-related bugs by 80%
- Faster development of new endpoints

### Related
- KB-2024-005: FastAPI migration strategy
- Task: task_def456
```

### Searching the Knowledge Base

```bash
# Full-text search
$ agentflow knowledge search "race condition"

Found 3 entries:

[KB-2024-001] Fixing race condition in WebSocket message handler
  Type: solution
  Tags: websocket, race-condition, concurrency
  Created: 2 days ago
  Related to: task_abc123

  Excerpt: The WebSocket handler was modifying shared session state without
  proper locking, leading to lost message updates and inconsistent session
  state. Implemented async lock using asyncio.Lock()...

[KB-2023-045] Thread safety patterns for shared state
  Type: pattern
  Tags: concurrency,threading,locks
  Created: 3 months ago

[KB-2023-089] Testing concurrent code
  Type: best-practice
  Tags: testing,concurrency
  Created: 5 months ago

# Filter by tag
$ agentflow knowledge search --tag websocket

# Filter by type
$ agentflow knowledge search --type pattern "async"

# Combined filters
$ agentflow knowledge search --tag websocket --type solution "error"
```

### Viewing Knowledge Entries

```bash
# View full entry
$ agentflow knowledge show KB-2024-001

[KB-2024-001] Fixing race condition in WebSocket message handler
═══════════════════════════════════════════════════════════════

Type: solution
Author: agent-code (agent-code-001)
Created: 2024-01-20
Tags: websocket, race-condition, concurrency
Related: task_abc123, commit:a1b2c3d4

───────────────────────────────────────────────────────────────
## Problem
Race condition occurring when multiple WebSocket messages arrive
simultaneously for the same session.

## Root Cause
The WebSocket handler was modifying shared session state without proper
locking, leading to:
- Lost message updates
- Inconsistent session state
- Intermittent test failures

## Solution
Implemented async lock using asyncio.Lock()...

───────────────────────────────────────────────────────────────

Related entries:
- KB-2023-045 [pattern] Thread safety patterns for shared state
- KB-2023-089 [best-practice] Testing concurrent code

Version history:
- v1 (current) - 2024-01-20 by agent-code-001
```

### Updating Knowledge Entries

```bash
# Update an entry
$ agentflow knowledge update KB-2024-001

# Opens editor with current content
# Agent makes updates

✓ Knowledge entry updated: KB-2024-001
  Version: v2
  Previous version: v1 archived
```

### Creating Checklists

```bash
$ agentflow knowledge create \
  --type checklist \
  --title "API Endpoint Development Checklist" \
  --tags "checklist,api,development"
```

**Content**:
```markdown
## API Endpoint Development Checklist

Use this checklist when developing new API endpoints.

### Planning
- [ ] Define request/response models with Pydantic
- [ ] Document endpoint purpose and use cases
- [ ] Identify required authentication/authorization
- [ ] Plan error cases and status codes

### Implementation
- [ ] Implement endpoint with FastAPI router
- [ ] Add input validation
- [ ] Implement error handling
- [ ] Add database queries (if needed)
- [ ] Handle edge cases

### Testing
- [ ] Write unit tests for business logic
- [ ] Write integration tests for endpoint
- [ ] Test error cases
- [ ] Test authentication/authorization
- [ ] Perform manual testing with Swagger UI

### Documentation
- [ ] Add docstring to endpoint function
- [ ] Update OpenAPI schema
- [ ] Document in API documentation
- [ ] Create example requests

### Deployment
- [ ] Code review completed
- [ ] All tests passing
- [ ] Performance acceptable (load test if needed)
- [ ] Monitoring/alerting configured
```

### Managing Knowledge Base

```bash
# List all entries
$ agentflow knowledge list

Total: 47 entries

Solutions (12):
  KB-2024-001 Fixing race condition in WebSocket message handler
  KB-2024-003 Handling large file uploads with streaming
  ...

Patterns (8):
  KB-2023-015 Repository Pattern with Async Caching
  KB-2023-022 Circuit Breaker Pattern
  ...

Decisions (15):
  KB-2024-002 Choosing Pydantic for data validation
  ...

Checklists (5):
  KB-2024-004 API Endpoint Development Checklist
  ...

# List by tag
$ agentflow knowledge list --tag websocket

# List entries by agent
$ agentflow knowledge list --agent agent-code-001

# Get statistics
$ agentflow knowledge stats

Knowledge Base Statistics
═══════════════════════════
Total Entries: 47
  Solutions: 12 (26%)
  Patterns: 8 (17%)
  Decisions: 15 (32%)
  Checklists: 5 (11%)
  Best Practices: 7 (15%)

Top Contributors:
  agent-code-001: 18 entries
  agent-devops-002: 12 entries
  agent-review-003: 9 entries
  agent-code-004: 8 entries

Most Used Tags:
  api: 12 entries
  testing: 10 entries
  async: 8 entries
  websocket: 6 entries
  performance: 5 entries

Recent Activity:
  KB-2024-004 created (2 hours ago)
  KB-2024-003 updated (5 hours ago)
  KB-2023-089 archived (1 day ago)
```

### Querying During Agent Execution

```bash
# Agent can query KB during task
$ agentflow agent exec agent-code-001 "Fix the authentication bug"

> [agent-code-001] Searching knowledge base for "authentication"...
>
> Found relevant entry: KB-2023-067 "Common authentication issues"
>
> Excerpt: Most authentication issues stem from:
> 1. Missing JWT token validation
> 2. Incorrect token refresh logic
> 3. Permission check timing
>
> Let me investigate the issue...
```

### Linking Knowledge to Tasks

```bash
# Link knowledge entries to tasks
$ agentflow task link-knowledge task_abc123 KB-2024-001

✓ Linked KB-2024-001 to task_abc123

# View related knowledge for a task
$ agentflow task show task_abc123 --knowledge

Task: task_abc123
Related Knowledge:
  KB-2024-001 [solution] Fixing race condition in WebSocket message handler
  KB-2023-045 [pattern] Thread safety patterns for shared state
```

## Data Model

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class KnowledgeType(str, Enum):
    """Types of knowledge entries"""
    SOLUTION = "solution"
    PATTERN = "pattern"
    DECISION = "decision"
    CHECKLIST = "checklist"
    TROUBLESHOOTING = "troubleshooting"
    BEST_PRACTICE = "best-practice"
    GLOSSARY = "glossary"

class KnowledgeEntryStatus(str, Enum):
    """Status of knowledge entry"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class KnowledgeEntry(BaseModel):
    """A knowledge base entry"""

    entry_id: str = Field(
        description="Unique identifier (e.g., KB-2024-001)"
    )
    title: str = Field(
        description="Descriptive title"
    )
    type: KnowledgeType = Field(
        description="Type of knowledge"
    )
    status: KnowledgeEntryStatus = Field(
        default=KnowledgeEntryStatus.DRAFT,
        description="Publication status"
    )

    # Content
    content: str = Field(
        description="Markdown content of the entry"
    )
    excerpt: Optional[str] = Field(
        default=None,
        description="Short excerpt for search results"
    )

    # Classification
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
    related_tasks: List[str] = Field(
        default_factory=list,
        description="Related task IDs"
    )
    related_entries: List[str] = Field(
        default_factory=list,
        description="Related entry IDs"
    )

    # Metadata
    author: str = Field(
        description="Agent ID who created the entry"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    version: int = Field(
        default=1,
        description="Entry version"
    )

    # Metrics
    view_count: int = Field(
        default=0,
        description="Number of times viewed"
    )
    helpful_count: int = Field(
        default=0,
        description="Number of helpful votes"
    )
    not_helpful_count: int = Field(
        default=0,
        description="Number of not helpful votes"
    )

    # Optional fields for specific types
    decision_status: Optional[str] = Field(
        default=None,
        description="For decision type: accepted/rejected/superseded"
    )
    applicable_context: Optional[str] = Field(
        default=None,
        description="When this knowledge applies"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "entry_id": "KB-2024-001",
                "title": "Fixing race condition in WebSocket message handler",
                "type": "solution",
                "status": "published",
                "content": "## Problem\nRace condition...",
                "tags": ["websocket", "race-condition", "concurrency"],
                "author": "agent-code-001",
                "created_at": "2024-01-20T10:30:00Z",
                "version": 1
            }
        }

class KnowledgeSearchQuery(BaseModel):
    """Query for searching knowledge base"""

    query: Optional[str] = Field(
        default=None,
        description="Full-text search query"
    )
    type: Optional[KnowledgeType] = Field(
        default=None,
        description="Filter by type"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Filter by tags (all must match)"
    )
    author: Optional[str] = Field(
        default=None,
        description="Filter by author agent"
    )
    status: Optional[KnowledgeEntryStatus] = Field(
        default=KnowledgeEntryStatus.PUBLISHED,
        description="Filter by status"
    )
    limit: int = Field(
        default=20,
        description="Maximum results"
    )

class KnowledgeBaseStats(BaseModel):
    """Statistics about the knowledge base"""

    total_entries: int
    entries_by_type: Dict[str, int]
    top_contributors: List[Dict[str, Any]]
    most_used_tags: List[Dict[str, int]]
    recent_activity: List[Dict[str, Any]]

class KnowledgeVersion(BaseModel):
    """Version history for knowledge entry"""

    entry_id: str
    version: int
    content: str
    author: str
    created_at: datetime
    change_summary: Optional[str] = None
```

## CLI Commands

### Knowledge Management

```bash
# Create new entry
agentflow knowledge create \
  --type <solution|pattern|decision|checklist|...> \
  --title "<title>" \
  --tags <tag1,tag2,...> \
  [--task-id <id>] \
  [--status <draft|published>]

# List entries
agentflow knowledge list \
  [--type <type>] \
  [--tag <tag>] \
  [--agent <agent_id>] \
  [--status <status>]

# Search entries
agentflow knowledge search \
  <query> \
  [--type <type>] \
  [--tag <tag>] \
  [--limit <n>]

# Show entry
agentflow knowledge show <entry_id>

# Update entry
agentflow knowledge update <entry_id>

# Change status
agentflow knowledge publish <entry_id>
agentflow knowledge deprecate <entry_id>
agentflow knowledge archive <entry_id>

# Vote on helpfulness
agentflow knowledge helpful <entry_id>
agentflow knowledge not-helpful <entry_id>

# View version history
agentflow knowledge history <entry_id>

# Show statistics
agentflow knowledge stats
```

### Task Integration

```bash
# Link knowledge to task
agentflow task link-knowledge <task_id> <entry_id>

# Unlink knowledge from task
agentflow task unlink-knowledge <task_id> <entry_id>

# Show related knowledge for task
agentflow task show <task_id> --knowledge
```

## Implementation Notes

### Phase 0 (MVP)

**Storage**: Local JSON files in `~/.agentflow/knowledge/`

**Search**: Simple full-text search using:
- Python's `re` module for pattern matching
- Tag filtering with exact match
- No semantic search

**Content Editing**:
- Open system editor (EDITOR env var)
- Store as markdown files
- Version tracking by copying previous versions

**Dependencies**:
- No external dependencies required
- Use file system for storage

**Features**:
- ✓ Create, read, update, delete entries
- ✓ Tag-based categorization
- ✓ Basic full-text search
- ✓ Version history
- ✓ Link to tasks
- ✓ Helpfulness voting

### Phase 1 (Enhanced)

**Storage**: SQLite database with full-text search (FTS5)

**Search**:
- SQLite FTS5 for full-text search
- Tag filtering with index
- Fuzzy matching on titles

**Content Editing**:
- In-editor validation of markdown
- Template system for entry types
- Preview mode

**Features**:
- Advanced search with ranking
- Related entries suggestions
- Export/import functionality
- Web UI for browsing

### Phase 2 (Advanced)

**Storage**: Database with vector embeddings

**Search**:
- Vector similarity search for semantic queries
- Hybrid search (text + semantic)
- Query suggestions and autocomplete

**Features**:
- Automatic knowledge extraction from tasks
- AI-powered entry suggestions
- Natural language queries
- Knowledge graph visualization
- Integration with external wikis (Confluence, Notion)

## Priority

**Medium Priority** - Useful for Phase 1 but not blocking for MVP.

**Rationale**:
- Knowledge base enhances productivity but isn't essential for basic agent operations
- Can be added incrementally as agents accumulate knowledge
- Simple file-based implementation sufficient for Phase 0
- More valuable once multiple agents are working collaboratively

## Dependencies

**Required**:
- None (can be implemented with file system)

**Recommended**:
- Task system (for linking knowledge to tasks)
- Agent system (for tracking authors)

**Future**:
- Embeddings for semantic search (Phase 2)
- Vector database (Phase 2)

## Migration Considerations

**Phase 0 → Phase 1**:
- Migrate JSON files to SQLite
- Import all version history
- Rebuild full-text search index
- Backup old JSON files

**Phase 1 → Phase 2**:
- Generate embeddings for existing entries
- Add vector search capability
- Maintain backward compatibility with text search

## Security Considerations

**Access Control** (Phase 1+):
- Role-based permissions for editing
- Read-only access for most agents
- Admin approval for publishing

**Content Validation**:
- Sanitize HTML if rendering markdown
- Validate tags and metadata
- Prevent injection attacks

**Audit Trail**:
- Log all changes with agent ID
- Track who viewed which entries
- Monitor for abuse

## Best Practices

**When to Create Entries**:
- After solving a complex problem
- When making significant decisions
- For reusable patterns
- After debugging tricky issues
- When documenting procedures

**Entry Quality**:
- Use clear, descriptive titles
- Write for your future self
- Include code examples
- Link to related entries
- Keep content up to date

**Tagging Strategy**:
- Use consistent tag names
- Include technology-specific tags
- Add domain-specific tags
- Limit to 3-5 relevant tags per entry

**Maintenance**:
- Review and update deprecated entries
- Archive obsolete knowledge
- Consolidate duplicate entries
- Periodic quality audits
