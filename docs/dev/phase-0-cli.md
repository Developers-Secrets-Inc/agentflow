# Phase 0: CLI with Local Storage

## Overview

**Phase 0** is a **prototype phase** that implements a fully functional CLI without a backend API or database. The goal is to validate user flows, command structure, and UX before building the real infrastructure.

**Key Principle:** Make it work end-to-end with fake data, then replace the fake layer with real API calls.

---

## Goals

### Primary Goals
1. ✅ **Validate CLI UX** - Test if commands feel intuitive
2. ✅ **Test user flows** - Register → Login → Create Org → Create Project
3. ✅ **Iterate quickly** - No backend setup, just JSON files
4. ✅ **Define data models** - Pydantic models that will be reused later
5. ✅ **Establish CLI patterns** - Command structure, output formatting, error handling

### Non-Goals
- ❌ Real authentication (just simulated)
- ❌ Persistent cloud data (local JSON only)
- ❌ Multi-user support (single-user local app)
- ❌ Production-ready code (this is throwaway prototype code)

---

## Technology Stack

### Package Manager: uv

**uv** is a modern, fast Python package manager and resolver:

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

**Why uv?**
- ⚡ **Fast** - 10-100x faster than pip
- 🔒 **Reliable** - Better dependency resolution
- 📦 **All-in-one** - Replaces pip, pip-tools, virtualenv
- 🎯 **Modern** - Written in Rust, actively maintained

### Dependencies (Minimal)

```bash
# Runtime
python >= 3.14

# CLI Framework
typer >= 0.12.0

# Validation & Serialization
pydantic >= 3.0.0

# Rich terminal output (optional but recommended)
rich >= 13.0.0

# UUID generation
standard library (uuid)
```

### No External Dependencies
- No httpx (no API calls)
- No database drivers (no DB)
- No SQLAlchemy/Drizzle (just JSON)

---

## Monorepo Structure

**Phase 0** implements the CLI with local JSON storage as a standalone app within the AgentFlow monorepo:

```
agentflow/                              # Root monorepo
├── apps/
│   ├── cli/                      # Phase 0: CLI with local storage (Python)
│   │   ├── src/
│   │   │   └── agentflow/
│   │   │       ├── __init__.py
│   │   │       ├── __main__.py        # Entry point for `python -m agentflow`
│   │   │       ├── cli.py             # Main Typer app
│   │   │       ├── config.py          # Config file handling
│   │   │       ├── models.py          # Pydantic models
│   │   │       ├── storage.py         # JSON storage layer
│   │   │       ├── commands/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py       # Auth commands
│   │   │       │   ├── org.py        # Organization commands
│   │   │       │   └── project.py    # Project commands
│   │   │       └── utils/
│   │   │           ├── __init__.py
│   │   │           ├── output.py     # Formatted output (tables, colors)
│   │   │           └── validators.py # Slug/email validators
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_org.py
│   │   │   └── test_project.py
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── .env.example
│   │
│   ├── api/                            # Phase 1: API (Hono + tRPC) - Future
│   └── web/                            # Phase 1: Web Dashboard (Next.js) - Future
│
├── packages/                            # Shared packages - Future
│   ├── types/                          # Shared TypeScript types
│   └── schema/                         # Shared Zod schemas
│
├── docs/
│   ├── MVP.md
│   ├── PROJECT.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── dev/
│       ├── phase-0-cli.md       # This document
│       ├── phase-1-api.md              # Future
│       └── phase-2-agents.md           # Future
│
├── turbo.json                           # Turborepo configuration (future)
├── package.json                         # Root package.json (future)
└── README.md                            # Main README
```

### Phase 0 Isolation

The `apps/cli/` directory is **completely self-contained**:

- ✅ Has its own `pyproject.toml` with Python dependencies
- ✅ Can be developed and tested independently
- ✅ No dependencies on other apps (they don't exist yet)
- ✅ Phase 0: Uses local JSON storage (no API)
- ✅ Phase 1+: Will migrate to HTTP client for API calls

### pyproject.toml Example

```toml
[project]
name = "agentflow-cli"
version = "0.0.1"
description = "AgentFlow CLI - Phase 0 (Local Storage)"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "typer>=0.12.0",
    "pydantic>=3.0.0",
    "rich>=13.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
agentflow = "agentflow:cli"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]
```

### Installation (Phase 0)

```bash
# From monorepo root
cd apps/cli

# Install with uv (recommended Python package manager)
uv sync

# Or install in development mode
uv pip install -e .

# Or run directly
uv run python -m agentflow --help
```

---

## Data Storage Design

### File Locations

```
~/.agentflow/
├── config.yaml          # Current user context (active org/project)
└── data.json            # All data (users, orgs, projects)
```

### Config File (`config.yaml`)

```yaml
current_user_email: user@example.com
current_api_key: afk_abc123...
current_organization: acme-corp
current_project: website-redesign
```

### Data File (`data.json`)

```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "password_hash": "$2b$12$...",
      "name": "John Doe",
      "created_at": "2025-01-20T10:00:00Z",
      "api_keys": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440000",
          "key": "afk_abc123def456...",
          "name": "My Laptop",
          "created_at": "2025-01-20T10:05:00Z",
          "last_used_at": null,
          "is_active": true
        }
      ]
    }
  ],
  "organizations": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "owner_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Acme Corporation",
      "slug": "acme-corp",
      "description": "A fictional company",
      "created_at": "2025-01-20T11:00:00Z"
    }
  ],
  "projects": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "organization_id": "770e8400-e29b-41d4-a716-446655440000",
      "name": "Website Redesign",
      "slug": "website-redesign",
      "description": "Complete overhaul of the main website",
      "github_url": "https://github.com/acme/website",
      "is_active": true,
      "created_at": "2025-01-20T12:00:00Z"
    }
  ]
}
```

---

## Pydantic Models

### Base Models (`models.py`)

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

def now_utc() -> datetime:
    return datetime.utcnow()

class APIKey(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    key: str  # API key (plaintext for Phase 0 local storage)
    name: str
    created_at: datetime = Field(default_factory=now_utc)
    last_used_at: Optional[datetime] = None
    is_active: bool = True

class User(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    email: EmailStr
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=now_utc)
    api_keys: List[APIKey] = []

class Organization(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    owner_id: str
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=now_utc)

class Project(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    organization_id: str
    name: str
    slug: str
    description: Optional[str] = None
    github_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=now_utc)

class Database(BaseModel):
    users: List[User] = []
    organizations: List[Organization] = []
    projects: List[Project] = []
```

---

## Command Specifications

### 1. Authentication Commands

#### `agentflow auth register`

**Description:** Register a new user account

**Arguments:**
```
--email      EMAIL     User email address (required)
--password   PASSWORD  User password (required)
--name       NAME      Display name (required)
```

**Flow:**
1. Check if email already exists in data.json
2. If exists → error "User already exists"
3. Hash password (use hashlib or passlib if available)
4. Create User object with default API key
5. Save to data.json
6. Update config.yaml with current user
7. Print success message with API key

**Success Output:**
```
✓ User registered successfully

  Email:    user@example.com
  Name:     John Doe
  API Key:  afk_abc123def456...

⚠️  Save your API key now. You won't see it again!
```

**Error Cases:**
- Email already exists
- Invalid email format
- Password too short (< 8 chars)
- Name too long (> 255 chars)

---

#### `agentflow auth login`

**Description:** Login with existing credentials

**Arguments:**
```
--email      EMAIL     User email address (required)
--password   PASSWORD  User password (required)
```

**Flow:**
1. Find user by email in data.json
2. If not found → error "Invalid credentials"
3. Verify password hash
4. If invalid → error "Invalid credentials"
5. Get first active API key for user
6. Update config.yaml with current user and API key
7. Print success message

**Success Output:**
```
✓ Logged in successfully as user@example.com

  Current Organization:  (none)
  Current Project:       (none)

Set your context:
  agentflow org list
  agentflow org use <slug>
```

**Error Cases:**
- User not found
- Invalid password
- No active API keys (shouldn't happen in Phase 0)

---

#### `agentflow auth api-keys create`

**Description:** Create a new API key

**Arguments:**
```
--name   NAME   API key name (required)
```

**Flow:**
1. Read current user from config.yaml
2. If not logged in → error "Not authenticated"
3. Generate API key: `afk_` + 32 random alphanumeric chars
4. Create APIKey object
5. Add to user's api_keys list
6. Save to data.json
7. Print success with API key

**Success Output:**
```
✓ API key created

  Name:     My Laptop
  API Key:  afk_xyz789...

⚠️  Save your API key now. You won't see it again!
```

---

#### `agentflow auth api-keys list`

**Description:** List all API keys for current user

**Arguments:** None

**Flow:**
1. Read current user from config.yaml
2. If not logged in → error
3. Load user from data.json
4. Display table of API keys (never show plaintext key)

**Output (Table):**
```
API Keys for user@example.com

NAME         LAST USED           CREATED
───────────  ──────────────────  ─────────────────────
My Laptop    2 minutes ago       2025-01-20 10:05:00
Work PC      Never               2025-01-19 15:30:00
Old Key      3 days ago          2025-01-15 09:00:00
```

---

#### `agentflow auth status`

**Description:** Show current authentication status

**Arguments:** None

**Output:**
```
AgentFlow CLI v0.0.1

Authentication: ✓ Authenticated
User:           user@example.com
Name:           John Doe

Current Organization:  acme-corp (Acme Corporation)
Current Project:       website-redesign (Website Redesign)

Config File:    /home/user/.agentflow/config.yaml
Data File:      /home/user/.agentflow/data.json
```

---

### 2. Organization Commands

#### `agentflow org list`

**Description:** List all organizations for current user

**Arguments:** None

**Flow:**
1. Read current user from config.yaml
2. Find all organizations where owner_id == user.id
3. Display table

**Output (Table):**
```
Organizations

NAME                    SLUG              DESCRIPTION              PROJECTS
──────────────────────  ────────────────  ──────────────────────  ───────
Acme Corporation        acme-corp         A fictional company      2
Startup Inc             startup-inc       Tech startup             0
Personal Projects       personal          My personal stuff        1
```

If no organizations:
```
No organizations found.

Create one:
  agentflow org create --name "My Org" --slug "my-org"
```

---

#### `agentflow org create`

**Description:** Create a new organization

**Arguments:**
```
--name         NAME     Organization name (required)
--slug         SLUG     URL-friendly slug (required)
--description  DESC     Description (optional)
```

**Flow:**
1. Read current user from config.yaml
2. If not logged in → error
3. Validate slug format (regex: `^[a-z0-9-]+$`)
4. Check if slug already exists in user's organizations
5. Create Organization object
6. Add to organizations list in data.json
7. Print success

**Success Output:**
```
✓ Organization created

  Name:     Acme Corporation
  Slug:     acme-corp
  Projects: 0

Set as active:
  agentflow org use acme-corp
```

**Error Cases:**
- Invalid slug format (must be lowercase letters, numbers, hyphens)
- Slug already exists
- Name too long (> 255 chars)

---

#### `agentflow org view <slug>`

**Description:** View organization details

**Arguments:**
```
SLAG   Organization slug (positional, required)
```

**Flow:**
1. Find organization by slug
2. If not found → error
3. Display organization details
4. List projects in organization

**Output:**
```
Organization: Acme Corporation (acme-corp)

Description:    A fictional company
Created:        2025-01-20 11:00:00 UTC
Owner:          user@example.com

Projects (2):

  NAME                   SLUG                  ACTIVE
  ────────────────────   ────────────────────  ──────
  Website Redesign       website-redesign      ✓
  Mobile App             mobile-app            ✓

Manage projects:
  agentflow project create --org acme-corp --name "New Project"
```

---

#### `agentflow org use <slug>`

**Description:** Set active organization context

**Arguments:**
```
SLAG   Organization slug (positional, required)
```

**Flow:**
1. Find organization by slug
2. If not found → error
3. Update config.yaml: current_organization = slug
4. Print success

**Success Output:**
```
✓ Now using organization: acme-corp (Acme Corporation)

Next steps:
  agentflow project list
  agentflow project create --name "My Project"
```

---

### 3. Project Commands

#### `agentflow project list`

**Description:** List all projects in current organization

**Arguments:**
```
--org   SLAG   Organization slug (optional, uses current org if not specified)
```

**Flow:**
1. Read current organization from config.yaml or --org flag
2. If no org set → error "No organization selected. Use: agentflow org use <slug>"
3. Find all projects where organization_id == org.id
4. Display table

**Output (Table):**
```
Projects in acme-corp

NAME                  SLUG                  ACTIVE    GITHUB
────────────────────  ────────────────────  ────────  ───────────────────────────
Website Redesign      website-redesign      ✓         github.com/acme/website
Mobile App            mobile-app            ✓         (none)
Internal Tools        internal-tools        ✗         (none)
```

If no projects:
```
No projects found in acme-corp.

Create one:
  agentflow project create --name "My Project" --slug "my-project"
```

---

#### `agentflow project create`

**Description:** Create a new project

**Arguments:**
```
--name         NAME     Project name (required)
--slug         SLUG     URL-friendly slug (required)
--description  DESC     Description (optional)
--github-url   URL      GitHub repository URL (optional)
```

**Flow:**
1. Read current organization from config.yaml
2. If no org set → error
3. Validate slug format
4. Check if slug already exists in organization
5. Create Project object
6. Add to projects list in data.json
7. Print success

**Success Output:**
```
✓ Project created in acme-corp

  Name:       Website Redesign
  Slug:       website-redesign
  GitHub:     github.com/acme/website
  Active:     Yes

Set as active:
  agentflow project use website-redesign
```

---

#### `agentflow project view <slug>`

**Description:** View project details

**Arguments:**
```
SLAG   Project slug (positional, required)
--org   SLAG   Organization slug (optional)
```

**Flow:**
1. Find project by slug (and org if specified)
2. If not found → error
3. Display project details

**Output:**
```
Project: Website Redesign (website-redesign)

Organization:  acme-corp (Acme Corporation)
Description:   Complete overhaul of the main website
GitHub URL:    https://github.com/acme/website
Active:        Yes
Created:       2025-01-20 12:00:00 UTC

No agents or sessions yet (coming in v2)
```

---

#### `agentflow project use <slug>`

**Description:** Set active project context

**Arguments:**
```
SLAG   Project slug (positional, required)
--org   SLAG   Organization slug (optional)
```

**Flow:**
1. Find project by slug (and org if specified)
2. If not found → error
3. Update config.yaml: current_project = slug
4. Print success

**Success Output:**
```
✓ Now using project: website-redesign (Website Redesign)

Working in: [acme-corp / website-redesign]

Coming in v2:
  - Create AI agents
  - Start work sessions
  - Track agent activities
```

---

## Prompt Context Design

The CLI prompt should show current context:

### No Context
```bash
$ agentflow
>
```

### Organization Context
```bash
$ agentflow
[acme-corp] >
```

### Full Context
```bash
$ agentflow
[acme-corp / website-redesign] >
```

This requires implementing a custom prompt or showing context in command outputs (simpler for Phase 0).

---

## Utility Functions

### Validators (`utils/validators.py`)

```python
import re
from typing import Optional

SLUG_REGEX = re.compile(r'^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$')

def validate_slug(slug: str) -> Optional[str]:
    """Validate slug format. Returns error message or None if valid."""
    if not 1 <= len(slug) <= 100:
        return "Slug must be between 1 and 100 characters"

    if not SLUG_REGEX.match(slug):
        return "Slug must contain only lowercase letters, numbers, and hyphens"

    return None

def validate_email(email: str) -> Optional[str]:
    """Validate email format. Pydantic will do most of this."""
    # Basic check, Pydantic EmailStr does full validation
    if '@' not in email:
        return "Invalid email format"
    return None
```

### Output Formatting (`utils/output.py`)

```python
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any

console = Console()

def success(message: str) -> None:
    """Print success message."""
    console.print(f"✓ {message}", style="bold green")

def error(message: str) -> None:
    """Print error message."""
    console.print(f"✗ {message}", style="bold red")

def warning(message: str) -> None:
    """Print warning message."""
    console.print(f"⚠️  {message}", style="bold yellow")

def info(message: str) -> None:
    """Print info message."""
    console.print(f"ℹ️  {message}", style="bold blue")

def print_table(columns: List[str], rows: List[List[str]]) -> None:
    """Print a rich table."""
    table = Table(show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*row)

    console.print(table)
```

---

## Storage Layer (`storage.py`)

### Functions

```python
from pathlib import Path
from typing import Optional
import json
from .models import Database, User, Organization, Project

DATA_DIR = Path.home() / ".agentflow"
DATA_FILE = DATA_DIR / "data.json"
CONFIG_FILE = DATA_DIR / "config.yaml"

def ensure_data_dir() -> None:
    """Create .agentflow directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)

def load_database() -> Database:
    """Load database from JSON file."""
    if not DATA_FILE.exists():
        return Database()

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    return Database(**data)

def save_database(db: Database) -> None:
    """Save database to JSON file."""
    ensure_data_dir()

    with open(DATA_FILE, 'w') as f:
        f.write(db.model_dump_json(indent=2))

def find_user_by_email(email: str) -> Optional[User]:
    """Find user by email."""
    db = load_database()
    for user in db.users:
        if user.email == email:
            return user
    return None

def find_organization_by_slug(slug: str) -> Optional[Organization]:
    """Find organization by slug."""
    db = load_database()
    for org in db.organizations:
        if org.slug == slug:
            return org
    return None

def find_project_by_slug(org_id: str, slug: str) -> Optional[Project]:
    """Find project by slug within organization."""
    db = load_database()
    for project in db.projects:
        if project.organization_id == org_id and project.slug == slug:
            return project
    return None
```

---

## Implementation Order

### Week 1: Foundation

**Day 1-2: Project Setup**
- [ ] Create project structure (`apps/cli/`)
- [ ] Initialize uv project: `uv init --lib`
- [ ] Set up pyproject.toml with dependencies
- [ ] Install dependencies: `uv sync`
- [ ] Implement storage.py (load/save JSON)
- [ ] Implement models.py (Pydantic models)
- [ ] Implement utils/output.py (rich output)
- [ ] Implement utils/validators.py
- [ ] Create basic cli.py with Typer app
- [ ] Test CLI entry point: `uv run python -m agentflow --help`

**Day 3-4: Auth Commands**
- [ ] Implement `agentflow auth register`
- [ ] Implement `agentflow auth login`
- [ ] Implement `agentflow auth api-keys create`
- [ ] Implement `agentflow auth api-keys list`
- [ ] Implement `agentflow auth status`

**Day 5: Org Commands**
- [ ] Implement `agentflow org list`
- [ ] Implement `agentflow org create`
- [ ] Implement `agentflow org view`
- [ ] Implement `agentflow org use`

**Day 6-7: Project Commands**
- [ ] Implement `agentflow project list`
- [ ] Implement `agentflow project create`
- [ ] Implement `agentflow project view`
- [ ] Implement `agentflow project use`

### Week 2: Polish & Testing

**Day 8-9: Error Handling**
- [ ] Add comprehensive error messages
- [ ] Handle edge cases (empty lists, missing files)
- [ ] Add validation for all inputs
- [ ] Improve output formatting

**Day 10-11: Testing**
- [ ] Manual testing of all flows
- [ ] Fix bugs
- [ ] Add basic unit tests for storage layer
- [ ] Test error paths

**Day 12-14: Documentation & Cleanup**
- [ ] Write README for CLI
- [ ] Add examples to docstrings
- [ ] Create demo scenario
- [ ] Code cleanup and refactoring

---

## Testing Scenarios

### Scenario 1: New User Flow

```bash
# 1. Register
agentflow auth register \
  --email "alice@example.com" \
  --password "secretpass" \
  --name "Alice"

# Expected: Success message with API key

# 2. Check status
agentflow auth status

# Expected: Shows logged in as alice, no org/project

# 3. Create organization
agentflow org create \
  --name "Acme Corp" \
  --slug "acme-corp" \
  --description "A company"

# Expected: Org created

# 4. List orgs
agentflow org list

# Expected: Shows acme-corp

# 5. Set active org
agentflow org use acme-corp

# Expected: Now using acme-corp

# 6. Create project
agentflow project create \
  --name "Website" \
  --slug "website" \
  --github-url "https://github.com/acme/site"

# Expected: Project created in acme-corp

# 7. List projects
agentflow project list

# Expected: Shows website project

# 8. View project
agentflow project view website

# Expected: Full project details
```

### Scenario 2: Multiple Organizations

```bash
# Create multiple orgs
agentflow org create --name "Personal" --slug "personal"
agentflow org create --name "Work" --slug "work"

# Switch between them
agentflow org use personal
agentflow project create --name "Blog" --slug "blog"

agentflow org use work
agentflow project create --name "Internal Tool" --slug "internal-tool"

# Verify context switching works
agentflow org use personal
agentflow project list  # Should show "Blog"

agentflow org use work
agentflow project list  # Should show "Internal Tool"
```

### Scenario 3: Error Handling

```bash
# Try to register with existing email
agentflow auth register --email "alice@example.com" --password "pass" --name "Alice"
# Expected: Error "User already exists"

# Try to create org with invalid slug
agentflow org create --name "Test" --slug "Test_Invalid"
# Expected: Error "Invalid slug format"

# Try to use non-existent org
agentflow org use fake-org
# Expected: Error "Organization not found"

# Try to create project without org
# (Clear config first)
# Then:
agentflow project create --name "Test" --slug "test"
# Expected: Error "No organization selected"
```

---

## Success Criteria

Phase 0 is complete when:

1. ✅ All auth commands work (register, login, api-keys)
2. ✅ All org commands work (list, create, view, use)
3. ✅ All project commands work (list, create, view, use)
4. ✅ Data persists across CLI invocations (JSON file)
5. ✅ Context switching works (org/project use)
6. ✅ Error messages are clear and helpful
7. ✅ Output is formatted and readable (tables, colors)
8. ✅ README documents all commands

---

## Known Limitations (Phase 0)

- Single-machine only (no cloud sync)
- No real authentication (just hash checking)
- No concurrent user support
- No data validation beyond Pydantic
- No migration system (JSON schema changes = break data)
- No rate limiting or security features
- No API (everything is local function calls)

**These are acceptable for Phase 0** - we're building a prototype, not production software.

---

## Next Phase (After Phase 0) - Monorepo Transition

### Phase 1: Build Real API

Create `apps/api/` with Hono + tRPC + PostgreSQL:

```
apps/api/
├── src/
│   ├── routers/          # tRPC routers
│   ├── models/           # Drizzle models
│   ├── services/         # Business logic
│   └── schema/           # Zod schemas
├── drizzle/              # Migrations
└── package.json
```

**API Implementation Order:**
1. Database schema (PostgreSQL + Drizzle)
2. Auth endpoints (register, login, api-keys)
3. Organization endpoints (CRUD)
4. Project endpoints (CRUD)

### Phase 2: Migrate CLI to API Client

Migrate `apps/cli/` from local storage to API client:

```
apps/cli/
├── src/
│   └── agentflow/
│       ├── cli.py             # Same structure
│       ├── config.py          # Same
│       ├── models.py          # Same Pydantic models
│       ├── client.py          # NEW: HTTP client (httpx) replaces storage.py
│       ├── commands/          # Same command structure
│       └── utils/             # Same utilities
└── pyproject.toml
```

**Migration Changes:**
- **Keep:** All command logic (`commands/`)
- **Keep:** All models (`models.py`)
- **Keep:** All utilities (`utils/`)
- **Replace:** `storage.py` → `client.py` (HTTP calls instead of JSON)
- **Remove:** Local `data.json` (data now in PostgreSQL via API)
- **Add:** httpx dependency for HTTP client

**Benefits of This Approach:**
- Pydantic models are identical between Phase 0 and Phase 1+
- Command logic stays 95% the same
- Only storage layer changes (JSON → HTTP)
- No need to rewrite any commands

### Phase 3: Add Agent Management

- Add `agents` table to database
- Add agent CRUD commands to CLI
- Implement agent roles and capabilities

### Phase 4: Add Sessions & Events

- Add `sessions` and `events` tables
- Add session management commands
- Implement event timeline

---

## Monorepo Benefits

### Why Structure as Monorepo?

1. **Shared Types** - Pydantic models can be shared between CLI phases
2. **Easier Migration** - Same `apps/cli/` folder, just swap storage layer
3. **Unified Testing** - Test CLI against real API in same repo
4. **Documentation** - Keep all phase docs together
5. **Tooling** - Single place for CI/CD, linting, formatting

### Future Monorepo Structure (Complete)

```
agentflow/
├── apps/
│   ├── cli/          # Phase 0→1: CLI (Phase 0: local storage → Phase 1+: API client)
│   ├── api/          # Phase 1: Real API
│   └── web/          # Phase 2+: Web dashboard
├── packages/
│   ├── shared-types/ # Shared Pydantic models
│   └── test-utils/   # Shared testing utilities
├── docs/
│   └── dev/
│       ├── phase-0-cli.md           # This document (CLI with local storage)
│       ├── phase-1-api.md           # API specification
│       ├── phase-2-cli-api-client.md # Migrate CLI to API client
│       └── phase-3-agents.md        # Agent management
└── turbo.json      # Run all apps together
```

---

## Notes

### Why Rich Terminal Output?

Using `rich` library provides:
- Beautiful tables with borders
- Syntax highlighting
- Progress bars (for later phases)
- Markdown rendering (for help text)
- Colorized output for better UX

### Why Pydantic?

- Type validation for free
- Easy serialization to/from JSON
- Will be reused in real API client
- Provides good error messages

### Why Config YAML?

- Easy to read and edit manually
- Better than JSON for config files (comments allowed)
- Simple to parse with standard libraries
- Can be extended with more settings later

---

**Document Version:** 1.1
**Last Updated:** 2025-01-20
**Status:** Phase 0 Specification (Monorepo + uv)
**Estimated Duration:** 2 weeks

### Changelog

**v1.1 (2025-01-20)**
- Updated for monorepo structure (`apps/cli/`)
- Added uv as package manager
- Added pyproject.toml example
- Added Phase 1-4 migration guide

**v1.0 (2025-01-20)**
- Initial Phase 0 specification
