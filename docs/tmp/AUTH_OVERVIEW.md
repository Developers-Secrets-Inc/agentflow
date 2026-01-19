# AgentFlow Authentication System

## Overview

AgentFlow uses a **hybrid authentication system** to handle two very different use cases:

1. **CEO (Human)** - Single human user accessing the web dashboard
2. **Agents (AI)** - Multiple virtual agents accessing via CLI

```
┌─────────────────────────────────────────┐
│         AgentFlow Auth System           │
└─────────────────────────────────────────┘
           │                    │
    ┌──────┴──────┐      ┌─────┴─────┐
    │   CEO Auth  │      │ Agent Auth│
    │ (better-auth)│     │  (Custom) │
    └─────────────┘      └───────────┘
           │                    │
           ↓                    ↓
    ┌──────────┐         ┌──────────┐
    │Sessions  │         │API Tokens│
    │(Cookies) │         │(Headers) │
    └──────────┘         └──────────┘
```

## Comparison Table

| Aspect | CEO (Human) | Agents (AI) |
|--------|-------------|-------------|
| **Count** | 1 user | Multiple agents |
| **Interface** | Web Dashboard (Next.js) | CLI (Python) |
| **Auth Method** | Email/Password or GitHub OAuth | API Keys or JWT Tokens |
| **Session Storage** | HTTP Cookies (secure, httpOnly) | Headers (X-API-Key or Authorization) |
| **Implementation** | better-auth (library) | Custom implementation |
| **Frequency** | Occasional login (session persists) | Every CLI command / session start |
| **Security** | CSRF protection, session expiration | Token rotation, rate limiting |

## Authentication Flow Comparison

### CEO Authentication Flow

```
1. CEO navigates to http://localhost:3000
2. Redirected to /login
3. Enters email/password OR clicks "Sign in with GitHub"
4. better-auth validates credentials
5. Creates session in database
6. Sets secure httpOnly cookie
7. Redirects to /dashboard
8. All subsequent requests include cookie automatically
9. better-auth middleware validates session on protected routes
```

### Agent Authentication Flow

```
1. CEO runs: agentflow session start --agent=agent-dev-001
2. CLI reads agent credentials from local storage
3. CLI makes API call:
   POST /api/agent/session/start
   Headers: {
     "X-Agent-ID": "agent-dev-001",
     "X-Agent-Token": "sk_live_xxx" OR "Authorization: Bearer jwt_token_xxx"
   }
4. API validates agent credentials in database
5. API checks agent permissions (can this agent start a session?)
6. API creates agent session record
7. API returns session confirmation
8. CLI proceeds with work session
```

## Key Differences

### CEO Auth (better-auth)

**Pros:**
- Battle-tested library with active maintenance
- Handles OAuth providers (GitHub, Google, etc.)
- Built-in CSRF protection
- Session management with automatic expiration
- Email verification, password reset flows
- React hooks for easy integration
- Automatic schema generation via CLI

**Cons:**
- Designed for human users, not AI agents
- Doesn't support our agent use case out of the box

### Agent Auth (Custom)

**Pros:**
- Tailored to our specific needs
- Agents can have different permission levels
- Can integrate with trust scoring system
- Audit trail for every agent action
- Can revoke individual agent credentials

**Cons:**
- Custom implementation (more maintenance)
- Need to handle edge cases ourselves

## Security Considerations

### CEO Auth Security
- Secure httpOnly cookies (prevent XSS)
- CSRF tokens
- Session expiration
- HTTPS only in production
- Rate limiting on login attempts

### Agent Auth Security
- Credentials stored securely on CEO's machine
- Token hashing in database (never store plaintext)
- API key rotation
- Audit logging for all agent actions
- Can revoke individual agent access
- IP whitelisting (optional, for local-only access)

## Integration with Stack

### Frontend (Next.js)
```typescript
import { authClient } from "@/lib/auth-client";

// Get CEO session
const { data: session } = await authClient.getSession();

// Protect page
if (!session) {
  redirect('/login');
}
```

### API (Hono + tRPC)
```typescript
// CEO middleware
import { auth } from "@/lib/auth";

// Agent middleware
import { validateAgentCredentials } from "@/lib/agent-auth";

// Apply to routes
app.use("/api/dashboard/*", auth.middleware); // CEO only
app.use("/api/agent/*", validateAgentCredentials); // Agents only
```

### CLI (Python)
```python
# Load agent credentials
credentials = load_agent_credentials("agent-dev-001")

# Make authenticated request
response = httpx.post(
    "http://localhost:3000/api/agent/session/start",
    headers={
        "X-Agent-ID": credentials.id,
        "X-Agent-Token": credentials.token
    }
)
```

## Next Steps

Read the detailed documentation:
- [CEO Authentication (better-auth)](./AUTH_CEO.md)
- [Agent Authentication (Custom)](./AUTH_AGENT.md)
- [Database Schema](./AUTH_SCHEMA.md)
- [Authentication Flows]((./AUTH_FLOWS.md)
