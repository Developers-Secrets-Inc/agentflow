# Open Questions & Decisions Needed

## Open Questions & Decisions Needed

### ✅ All Questions Resolved

All design decisions have been finalized. Here's the complete summary:

| Category | Question | Decision | Rationale |
|----------|----------|----------|-----------|
| **Architecture** | Roles vs Agents | Separated into template (role) and instance (agent) | Reusability, scalability, individualization |
| **Architecture** | Role Storage | Roles stored on API, agents stored locally | API provides source of truth, local cache for agents |
| **Architecture** | Pull Mechanism | Pull fetches role from API, generates Claude Code skills | Integration with Claude Code, standardized skill format |
| **Authentication** | Agent API Keys | Single API key for CLI, no per-agent keys | Simplified auth, agents identified by pull |
| **Skills** | Skill Generation | Role documents → Claude Code skills automatically | Leverages existing skill format, works with Claude Code |
| **Skills** | Skill Storage | `~/.claude/skills/` for Phase 0 | Global availability, follows Claude Code conventions |
| **Skills** | Document Mapping | 1 document = 1 skill (Option A) | Simple, predictable mapping |
| **Skills** | Naming Convention | Combined: `python-testing`, `python-api` (Option C) | Clear, avoids conflicts, memorable |
| **Skills** | Regeneration | Notify user to pull manually (Option B) | Explicit control, no surprises |
| **Skills** | Content Types | Markdown only (Phase 0) | Start simple, add complexity later if needed |
| **Sessions** | Requirement | Required - must start session before logging (Option B) | Explicit sessions = better tracking |
| **Skills** | Scope | Global in `~/.claude/skills/` (Option A) | Simplest for Phase 0, flexibility later |
| **Version** | Role conflict detection | Notification when role is outdated, `--force` to bypass | Team consistency while allowing flexibility |
| **Version** | Skill overwrite | Complete overwrite (no merge), skills are build artifacts | Simplicity, predictability, source of truth = role docs |
| **Tasks** | Assignment scope | Project-level assignment, not global | Clarity, context, isolation between projects |
| **Communication** | Peer communication | NO - only upward communication (agent → supervisor) | Agents have same skills, supervisor coordinates |
| **Communication** | Message priority | Implicit auto-P1 for hierarchical messages, explicit P0 always P0 | Ensure supervisor messages seen |
| **Message vs Log** | When to use which | Message = needs response, Log = informational | Clear distinction in purpose |
| **Sessions** | Multi-project sessions | One session active at a time, even across multiple projects | Agent works on one task/project at a time |
| **Sessions** | Session mutability | Immutable after stop, but can append additional logs | Preserve integrity while allowing corrections |
| **Logs** | Modification | Append-only - can add info, cannot modify existing data | Audit trail integrity |
| **Trust** | Training tasks | NO - agents recover by doing normal work | Simplicity, on-the-job learning |
| **Trust** | Recovery mechanism | Phase 0: Manual by manager; Full: Auto by completing tasks | Manual for DX testing, auto for production |
| **Trust** | Score bounds | Floor at 0, ceiling at 100, no glass ceiling | Simple, predictable, achievable perfection |
| **Tools** | Documentation storage | Each tool has Markdown documentation in database | Consistent with roles, enables skill generation |
| **Tools** | Internal vs External | Pre-defined (pytest) vs custom (excel-analyzer) | Flexibility for organization-specific tools |
| **Agents** | Termination data handling | ALL data preserved (tasks, sessions, logs, messages, skills) | Audit trail, analytics, compliance, debugging |
| **Agents** | Task reassignment | Manual, not automatic on termination | Manager control over reassignment |
| **Hierarchy** | Structure | One-to-many only (no many-to-many, no dotted lines) | Simplicity, clear chain of command, unambiguous reviews |
| **Logs** | Categories | Domain-specific (status, decision, issue) not DEBUG/INFO/ERROR | Semantic meaning vs system levels |

### 🎯 Implementation Decisions Summary

**Role-to-Skill Mapping**:
```
Role Document → Claude Code Skill
───────────────   ─────────────────
testing-guidelines.md  →  python-testing/SKILL.md
api-conventions.md     →  python-api/SKILL.md
async-patterns.md      →  python-async/SKILL.md
```

**Skill Naming Convention**:
- Format: `{role_prefix}-{document_name}`
- Example: `python-testing`, `python-api`
- Stored in: `~/.claude/skills/{skill_name}/SKILL.md`

**Regeneration Workflow**:
```
Role updated on API
        ↓
Notify user: "Role 'python-dev' has been updated (v3 → v4)"
        ↓
User runs: agentflow agent pull agent-dev-001
        ↓
Skills regenerated with new content
```

**Content Types (Phase 0)**:
- Guidelines (rules, standards)
- Concepts (domain knowledge)
- Methodologies (processes)
- Conventions (code style)
- Examples (reference implementations)

All as Markdown files.

---
