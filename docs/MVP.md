# AgentFlow MVP - Version 1

## Overview

This document defines the **minimum viable product (MVP)** for AgentFlow - a simplified first version that focuses on core organizational and project management functionality before introducing agents, sessions, and advanced features.

## MVP Philosophy

**Start simple, validate, then iterate.**

The MVP prioritizes:
- ✅ Proving the architecture works (CLI ↔ API ↔ Database)
- ✅ Validating authentication and API key management
- ✅ Testing core user flows (org/project navigation)
- ✅ Establishing the foundation for future features

The MVP explicitly excludes:
- ❌ AI agents and agent management
- ❌ Sessions, events, and timelines
- ❌ KPIs and trust scoring
- ❌ Wiki and knowledge base
- ❌ GitHub integration

---

## v1 Feature Scope

### Included Features

#### 1. User Authentication
- User registration and login
- API key generation and management
- Secure API key authentication for CLI

#### 2. Organization Management
- Create organizations
- List organizations
- View organization details
- Select active organization

#### 3. Project Management
- Create projects within an organization
- List projects within an organization
- View project details
- Select active project
- Link projects to GitHub repositories (optional metadata field)

#### 4. CLI Interface
- User-friendly command-line interface
- Authentication commands
- Organization navigation
- Project navigation
- Context-aware prompts (show current org/project)

---

## Technology Stack (Same as Full Version)

- **CLI**: Python 3.14 + Typer + httpx
- **API**: Hono + tRPC (TypeScript)
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod

---

## Database Schema (MVP)

### Tables Overview

Only **4 tables** are needed for the MVP:

```sql
users           -- User accounts
api_keys        -- Authentication keys
organizations   -- Organizations (workspaces)
projects        -- Projects within organizations
```

---

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique user identifier |
| email | varchar(255) | NOT NULL, UNIQUE | User email address |
| password_hash | varchar(255) | NOT NULL | Hashed password (bcrypt) |
| name | varchar(255) | NOT NULL | Display name |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- UNIQUE INDEX idx_users_email (email)

---

### Table: `api_keys`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique API key identifier |
| user_id | uuid | NOT NULL, FK → users.id | User who owns this key |
| key_hash | varchar(255) | NOT NULL, UNIQUE | Hashed API key |
| name | varchar(255) | NOT NULL | Key name (e.g., "My Laptop") |
| last_used_at | timestamp | NULL | Last usage timestamp |
| expires_at | timestamp | NULL | Expiration timestamp (NULL = never) |
| is_active | boolean | NOT NULL, DEFAULT true | Whether key is active |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- INDEX idx_api_keys_user_id (user_id)
- UNIQUE INDEX idx_api_keys_key_hash (key_hash)

**Notes:**
- Store `key_hash` (bcrypt), never plaintext
- Generate random API keys (e.g., `afk_` prefix + 32 random characters)
- Users can have multiple API keys

---

### Table: `organizations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique organization identifier |
| owner_id | uuid | NOT NULL, FK → users.id | Owner of the organization |
| name | varchar(255) | NOT NULL | Organization name |
| slug | varchar(100) | NOT NULL, UNIQUE | URL-friendly identifier |
| description | text | NULL | Organization description |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- INDEX idx_organizations_owner_id (owner_id)
- UNIQUE INDEX idx_organizations_slug (slug)

**Constraints:**
- `slug` must match regex: `^[a-z0-9-]+$` (lowercase, numbers, hyphens)

---

### Table: `projects`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, NOT NULL | Unique project identifier |
| organization_id | uuid | NOT NULL, FK → organizations.id | Parent organization |
| name | varchar(255) | NOT NULL | Project name |
| slug | varchar(100) | NOT NULL | URL-friendly identifier |
| description | text | NULL | Project description |
| github_url | varchar(500) | NULL | GitHub repository URL (optional) |
| is_active | boolean | NOT NULL, DEFAULT true | Project status flag |
| created_at | timestamp | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Composite Unique Constraint:**
- UNIQUE (organization_id, slug) -- Unique slug within organization

**Indexes:**
- INDEX idx_projects_organization_id (organization_id)
- INDEX idx_projects_slug (slug)
- UNIQUE INDEX idx_projects_org_slug (organization_id, slug)

**Constraints:**
- `slug` must match regex: `^[a-z0-9-]+$`

---

## API Endpoints (MVP)

### Authentication

```
POST   /api/v1/auth/register
       - Body: { email, password, name }
       - Response: { user_id, email, name }

POST   /api/v1/auth/login
       - Body: { email, password }
       - Response: { user_id, email, name }

POST   /api/v1/auth/api-keys
       - Auth: Bearer token (email:password)
       - Body: { name }
       - Response: { api_key (plaintext), id, name, created_at }

GET    /api/v1/auth/api-keys
       - Auth: Bearer API key
       - Response: [{ id, name, last_used_at, created_at }]

DELETE /api/v1/auth/api-keys/:id
       - Auth: Bearer API key
       - Response: { success: true }
```

### Organizations

```
GET    /api/v1/organizations
       - Auth: Bearer API key
       - Response: [{ id, name, slug, description, created_at }]

POST   /api/v1/organizations
       - Auth: Bearer API key
       - Body: { name, slug, description (optional) }
       - Response: { id, name, slug, description, created_at }

GET    /api/v1/organizations/:slug
       - Auth: Bearer API key
       - Response: { id, name, slug, description, created_at, projects: [...] }
```

### Projects

```
GET    /api/v1/organizations/:orgSlug/projects
       - Auth: Bearer API key
       - Response: [{ id, name, slug, description, github_url, is_active, created_at }]

POST   /api/v1/organizations/:orgSlug/projects
       - Auth: Bearer API key
       - Body: { name, slug, description (optional), github_url (optional) }
       - Response: { id, name, slug, description, github_url, created_at }

GET    /api/v1/organizations/:orgSlug/projects/:slug
       - Auth: Bearer API key
       - Response: { id, name, slug, description, github_url, is_active, created_at }
```

---

## CLI Commands (MVP)

### Setup & Authentication

```bash
# Initial setup
agentflow auth register
agentflow auth login
agentflow auth api-keys list
agentflow auth api-keys create "My Laptop"
agentflow auth api-keys delete <id>
agentflow auth status
```

### Organization Management

```bash
# List all organizations
agentflow org list

# Create a new organization
agentflow org create --name "Acme Corp" --slug "acme-corp"

# View organization details
agentflow org view acme-corp

# Set active organization (context)
agentflow org use acme-corp
```

### Project Management

```bash
# List projects in current organization
agentflow project list

# Create a new project (requires active org)
agentflow project create \
  --name "Website Redesign" \
  --slug "website-redesign" \
  --description "Main website overhaul" \
  --github-url "https://github.com/acme/website"

# View project details
agentflow project view website-redesign

# Set active project (context)
agentflow project use website-redesign
```

### Context Awareness

The CLI prompt shows current context:

```bash
# When no context set
$ agentflow
>

# When org is set
$ agentflow
[acme-corp] >

# When org and project are set
$ agentflow
[acme-corp / website-redesign] >
```

---

## Configuration File

The CLI stores configuration locally:

```yaml
# ~/.agentflow/config.yaml
api_key: afk_abc123...
default_organization: acme-corp
default_project: website-redesign
```

---

## Zod Schemas (MVP)

### User Schema

```typescript
const userSchema = z.object({
  id: z.uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(255),
  createdAt: z.datetime(),
  updatedAt: z.datetime()
})
```

### API Key Schema

```typescript
const apiKeySchema = z.object({
  id: z.uuid(),
  userId: z.uuid(),
  name: z.string().min(1).max(255),
  lastUsedAt: z.datetime().nullable(),
  expiresAt: z.datetime().nullable(),
  isActive: z.boolean(),
  createdAt: z.datetime()
})

const createApiKeySchema = z.object({
  name: z.string().min(1).max(255)
})

const apiKeyResponseSchema = apiKeySchema.extend({
  apiKey: z.string().startsWith('afk_') // Only shown on creation
})
```

### Organization Schema

```typescript
const organizationSchema = z.object({
  id: z.uuid(),
  ownerId: z.uuid(),
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().nullable(),
  createdAt: z.datetime(),
  updatedAt: z.datetime()
})

const createOrganizationSchema = z.object({
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().optional()
})
```

### Project Schema

```typescript
const projectSchema = z.object({
  id: z.uuid(),
  organizationId: z.uuid(),
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().nullable(),
  githubUrl: z.string().url().nullable(),
  isActive: z.boolean(),
  createdAt: z.datetime(),
  updatedAt: z.datetime()
})

const createProjectSchema = z.object({
  name: z.string().min(1).max(255),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  description: z.string().optional(),
  githubUrl: z.string().url().optional()
})
```

---

## Implementation Roadmap

### Phase 1: Database & API Foundation (Week 1)

- [ ] Set up PostgreSQL database
- [ ] Define Drizzle schema (4 tables)
- [ ] Create and run migrations
- [ ] Set up Hono + tRPC API structure
- [ ] Implement Zod validation schemas

### Phase 2: Authentication (Week 1)

- [ ] Implement user registration endpoint
- [ ] Implement user login endpoint
- [ ] Implement API key generation
- [ ] Implement API key authentication middleware
- [ ] Test auth flow with curl/Postman

### Phase 3: Organization CRUD (Week 2)

- [ ] Implement organization list endpoint
- [ ] Implement organization create endpoint
- [ ] Implement organization view endpoint
- [ ] Test with API client

### Phase 4: Project CRUD (Week 2)

- [ ] Implement project list endpoint
- [ ] Implement project create endpoint
- [ ] Implement project view endpoint
- [ ] Test org/project relationships

### Phase 5: CLI Foundation (Week 3)

- [ ] Set up Typer CLI structure
- [ ] Implement configuration file handling
- [ ] Implement HTTP client (httpx)
- [ ] Create base command structure

### Phase 6: CLI Auth Commands (Week 3)

- [ ] Implement `agentflow auth register`
- [ ] Implement `agentflow auth login`
- [ ] Implement `agentflow auth api-keys create`
- [ ] Implement `agentflow auth status`
- [ ] Store API key in config file

### Phase 7: CLI Org & Project Commands (Week 4)

- [ ] Implement `agentflow org list/create/view/use`
- [ ] Implement `agentflow project list/create/view/use`
- [ ] Implement context-aware prompts
- [ ] Test full CLI workflow

### Phase 8: Testing & Polish (Week 4)

- [ ] End-to-end testing
- [ ] Error handling improvements
- [ ] CLI UX improvements (colors, formatting)
- [ ] Documentation

---

## Success Criteria

The MVP is considered complete when:

1. ✅ A user can register and login
2. ✅ A user can generate an API key via CLI
3. ✅ A user can create an organization via CLI
4. ✅ A user can create a project within an organization via CLI
5. ✅ The CLI context shows active organization/project
6. ✅ All data is persisted in PostgreSQL
7. ✅ API authentication is secure (hashed keys, bcrypt passwords)

---

## What's Next (Post-MVP)

Once the MVP is validated, the next features to add are:

1. **Agents** - Create and manage AI agents
2. **Sessions** - Track agent work sessions
3. **Events Timeline** - Record all agent activities
4. **Roles** - Define agent roles and capabilities
5. **KPIs** - Track agent performance metrics

---

## Notes

### Security Considerations

- All passwords hashed with bcrypt (cost factor 12)
- All API keys hashed before storage
- Use HTTPS in production
- Implement rate limiting on auth endpoints
- Never expose API key plaintext after creation

### API Key Format

API keys should follow this format:
```
afk_<random 32 characters>
```

Example: `afk_k3j4h5k6j7h8g9f0d3s4a5p6o7i8u9y0`

This makes them:
- Easily identifiable as AgentFlow keys
- Long enough to be secure (256 bits)
- URL-safe (only alphanumeric characters)

### Slug Validation

Slugs must be:
- Lowercase only
- alphanumeric plus hyphens
- Cannot start or end with hyphens
- No consecutive hyphens
- Between 1-100 characters

Regex: `^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$`

---

**Document Version:** 1.0
**Last Updated:** 2025-01-20
**Status:** MVP Definition
