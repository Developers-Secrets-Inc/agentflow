# AgentFlow Architecture

## Technology Stack

### Core Technologies

- **CLI**: Python 3.14 with Typer
- **API**: Hono (TypeScript) with tRPC
- **Frontend**: Next.js (TypeScript/React)
- **Database**: PostgreSQL
- **ORM**: Drizzle ORM
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Validation**: Zod
- **Language**: TypeScript (backend + frontend), Python (CLI only)

## Architecture Overview

```
┌─────────────────────┐
│  CLI (Python 3.14)  │ ◄───── Typer CLI interface
│  - Typer            │       HTTP client (httpx)
│  - httpx/requests   │       Pydantic models
└──────────┬──────────┘
           │
           │ HTTP REST API calls
           │
           ↓
┌─────────────────────┐
│  API (Hono + tRPC)  │ ◄───── Hono web framework
│  - tRPC             │       tRPC for type-safe RPC
│  - Zod validation   │       TypeScript
│  - Edge-ready       │       OpenAPI export for CLI
└──────────┬──────────┘
           │
           │ Database queries
           │
           ↓
┌─────────────────────┐
│  Database (PostgreSQL)│
│  - Users            │
│  - Workspaces       │
│  - Projects         │
│  - Agents           │
│  - Sessions         │
│  - Events           │
│  - KPIs             │
│  - Wiki             │
└─────────────────────┘
           ↑
           │ tRPC (type-safe)
           │
┌──────────┴──────────┐
│  Web (Next.js)      │ ◄───── Next.js 14+
│  - React            │       TypeScript/React
│  - tRPC client      │       Shared types
│  - Tailwind CSS     │       Server components
└─────────────────────┘
```

## Component Breakdown

### 1. API Layer (Hono + tRPC)

**Framework**: Hono (TypeScript web framework)

**Why Hono?**
- Ultra-fast and lightweight
- Edge-ready (can run on Cloudflare Workers, Deno, etc.)
- Modern TypeScript-first API
- Excellent developer experience
- Compatible with tRPC

**Communication**: tRPC
- Type-safe remote procedure calls
- End-to-end type safety between API and frontend
- Automatic type inference (no code generation)
- Zod schema validation
- No manual API schema maintenance

**For CLI consumption:**
- tRPC can export OpenAPI schema
- CLI uses OpenAPI schema or direct HTTP calls
- REST-like endpoints for Python client

### 2. Web Dashboard (Next.js)

**Framework**: Next.js (TypeScript)

**State Management**: Zustand
- Lightweight, simple state management
- No boilerplate or providers needed
- TypeScript-first with excellent type inference
- Perfect for managing UI state (modals, filters, etc.)

**Data Fetching**: TanStack Query (React Query)
- Server state management (caching, refetching, invalidation)
- Automatic background refetching
- Optimistic updates
- Type-safe integration with tRPC
- Handles loading/error states automatically

**Validation**: Zod
- Schema validation for API inputs/outputs
- Runtime type checking
- Used by tRPC for input validation
- Shared schemas between API and frontend (when needed)

**Features:**
- Server-side rendering with React Server Components
- tRPC client for type-safe API calls
- TanStack Query for data synchronization
- Real-time updates (via polling or WebSockets in future)
- Dashboard for CEO oversight
- Wiki management interface
- Agent and project management UI

**Type Safety:**
- Shares TypeScript types with API via tRPC
- Zod schemas for runtime validation
- Zero duplication of type definitions
- Compile-time error checking
- Excellent IDE autocomplete

### 3. CLI (Python)

**Framework**: Typer

**Purpose**: Agent interaction interface
- AI agents use the CLI to interact with the system
- Commands for starting sessions, logging, pulling updates
- Work session management
- Agent role pulling

**Communication with API:**
- HTTP client using `httpx` or `requests`
- Pydantic models for type safety and validation
- Calls tRPC endpoints via HTTP (tRPC acts as RPC layer)
- Can use OpenAPI schema for type generation

**Why Python for CLI?**
- AI agents typically run in Python environments
- Rich ecosystem for AI/ML tooling
- Easy integration with LLMs and agent frameworks
- CEO runs agents manually on their machine

### 4. Database (PostgreSQL)

**Why PostgreSQL?**
- Production-ready relational database
- Excellent support for complex queries and joins
- ACID compliance for data integrity
- Supports JSON/JSONB for flexible schema evolution
- Concurrent writes (multi-agent support)
- Full-text search capabilities (useful for wiki/search)
- Robust backup and replication options
- Perfect fit for TypeScript ORMs (Drizzle, Prisma)

**ORM: Drizzle ORM**

**Why Drizzle?**
- TypeScript-first with excellent type safety
- SQL-like syntax (you write actual SQL, not a custom query language)
- Lightweight and fast (no query engine overhead)
- Schema-as-code approach (define schema in TypeScript)
- Excellent migration system with Drizzle Kit
- Perfect for PostgreSQL with full feature support
- No code generation (types are inferred from schema)
- Great developer experience with autocomplete

**Features:**
- Schema defined in TypeScript files
- Type-safe queries with full autocomplete
- Automatic migrations via Drizzle Kit
- Support for relations, transactions, and complex queries
- Connection pooling built-in
- Edge-compatible (can run on Cloudflare Workers with appropriate adapter)

**Schema:**
- Users (CEO)
- Workspaces (virtual companies)
- Projects
- Agents (with identity, roles, trust scores)
- Sessions (work sessions)
- Events (timeline)
- KPIs (agent performance metrics)
- Wiki (knowledge base with versioning)
- Tasks (linked to GitHub issues)

**Connection:**
- Connection pooling for efficient resource usage
- Migration system for schema evolution
- Seed data for development

## Data Flow

### Agent Work Session Flow

```
1. CEO starts agent CLI
   ↓
2. CLI calls API: agentflow.session_start()
   ↓
3. API validates agent, creates session event in DB
   ↓
4. CLI pulls: latest tasks, messages, role updates
   ↓
5. Agent works, CLI logs progress via agentflow.session_log()
   ↓
6. CLI calls: agentflow.session_stop()
   ↓
7. API updates session, triggers KPI recalculation
   ↓
8. CEO reviews session via web dashboard
```

### CEO Dashboard Flow

```
1. CEO opens Next.js dashboard
   ↓
2. Dashboard fetches data via tRPC: api.workspace.getAgents()
   ↓
3. tRPC makes type-safe call to Hono API
   ↓
4. API queries PostgreSQL, returns data
   ↓
5. Dashboard displays with real-time updates
   ↓
6. CEO takes action: assign task, approve wiki entry, etc.
   ↓
7. Action sent via tRPC, API updates DB
```

## Type Safety Strategy

### Frontend ↔ API: tRPC + Zod
- **Zero code generation**: Types are automatically inferred
- **End-to-end type safety**: From frontend to API to database
- **Zod validation**: Runtime type checking for all API inputs/outputs
- **No schema drift**: Types are always in sync
- **Developer experience**: Like calling a local function

### State Management Strategy
- **Server State**: TanStack Query handles API data (agents, sessions, events)
- **Client State**: Zustand handles UI state (modals, filters, forms)
- **Form State**: React Hook Form + Zod for form validation
- **Clear separation**: Server vs client state to avoid sync issues

### CLI ↔ API: OpenAPI + Pydantic
- **Option 1**: CLI uses OpenAPI schema exported from tRPC
  - Generate Pydantic models from OpenAPI
  - Type-safe HTTP client

- **Option 2**: Manual Pydantic models in CLI
  - Define models matching API schemas
  - Update when API changes

- **Option 3**: Direct HTTP with minimal typing
  - Simple requests/responses
  - Validation happens on API side

## Monorepo Structure

```
agentflow/
├── apps/
│   ├── api/              # Hono + tRPC backend
│   │   ├── src/
│   │   │   ├── routers/  # tRPC routers
│   │   │   ├── models/   # Database models (Drizzle)
│   │   │   ├── services/ # Business logic
│   │   │   ├── schema/   # Zod schemas
│   │   │   └── db/       # Database connection
│   │   ├── drizzle/      # Drizzle migrations
│   │   └── package.json
│   │
│   ├── web/              # Next.js dashboard
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components
│   │   ├── lib/          # tRPC client, TanStack Query setup
│   │   ├── stores/       # Zustand stores
│   │   └── package.json
│   │
│   └── cli/              # Python CLI (separate repo or subdirectory)
│       ├── agentflow/
│       │   ├── __init__.py
│       │   ├── cli.py    # Typer CLI
│       │   ├── client.py # HTTP client (httpx)
│       │   ├── models/   # Pydantic models
│       │   └── commands/ # CLI commands
│       └── pyproject.toml
│
├── packages/
│   ├── types/            # Shared TypeScript types (if needed)
│   ├── schema/           # Shared Zod schemas
│   └── config/           # Shared configuration
│
├── db/
│   └── migrations/       # Database migrations
│
├── turbo.json            # Turborepo config (optional)
└── package.json          # Root package.json
```

## Deployment Strategy

### Development
- API: Hono dev server with hot reload
- Web: Next.js dev server
- CLI: Local Python installation
- Database: PostgreSQL (Docker or local installation)
- Migrations: Drizzle Kit for schema changes

### Production
- **API**: Deploy to Node.js (Vercel, Railway, Fly.io) or Edge (Cloudflare Workers with adapter)
- **Web**: Vercel (native Next.js support)
- **CLI**: Installed via pip from private PyPI or git
- **Database**: PostgreSQL (Supabase, Neon, Railway, or self-hosted)
- **Migrations**: Run via Drizzle Kit as part of deployment

## Security Considerations

### Authentication
- CLI: API tokens (stored in config)
- Web: Session-based auth (cookies)
- API: Token validation on every request

### Authorization
- Role-based access control (CEO, org-level agents, project-level agents)
- Agent identity verification (cryptographic signatures)
- CEO has ultimate authority

### Data Protection
- SQLite file permissions
- API rate limiting (future)
- HTTPS in production

## Advantages of This Architecture

### For CEO (User)
- **Full TypeScript stack**: Familiar, productive development
- **Type safety everywhere**: Catch errors at compile time
- **Excellent DX**: Like using PayloadCMS + Next.js
- **Modern tooling**: Hot reload, great IDE support
- **Production-ready**: PostgreSQL from day one

### For Web Dashboard
- **TanStack Query**: Automatic caching, refetching, optimistic updates
- **Zustand**: Simple, lightweight state management
- **Zod**: Runtime validation everywhere, type-safe inputs
- **tRPC**: End-to-end type safety, zero code generation
- **Next.js 14**: Server components, great performance

### For Agents (CLI)
- **Simple interface**: Just HTTP calls to API
- **Python ecosystem**: Easy AI/ML integration
- **Manual execution**: CEO has full control
- **Session-based**: Clear boundaries and logging

### For System
- **Production-ready**: PostgreSQL, not a "toy" database
- **Scalable**: Built to handle concurrent operations
- **Edge-ready**: API can run on edge infrastructure
- **Maintainable**: Shared types, single source of truth
- **Testable**: Clear separation of concerns

## Trade-offs

### CLI Python ↔ API TypeScript
- **Con**: CLI doesn't benefit from tRPC type safety
- **Pro**: CLI is simple consumer, doesn't need complex types
- **Solution**: Use Pydantic models or OpenAPI schema

### Business Logic in TypeScript
- **Con**: Not in Python (might need Python-specific logic)
- **Pro**: CEO is TS expert, full stack consistency
- **Solution**: Keep business logic simple, or use Python microservice if needed

### PostgreSQL for Single-User App
- **Con**: Heavier than SQLite, requires separate process
- **Pro**: Production-ready from day one, no migration needed later
- **Solution**: Use Docker in development for easy setup

### Multiple State Management Solutions
- **Con**: TanStack Query (server state) + Zustand (client state) + React Hook Form (form state)
- **Pro**: Each tool is best-in-class for its purpose
- **Solution**: Clear guidelines on when to use each (server vs client state)
