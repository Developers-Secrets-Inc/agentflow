# Claude Code Skills Format

## Claude Code Skills Format

### What is a Claude Code Skill?

A **skill** extends Claude's capabilities in Claude Code by providing:
- Custom instructions for specific tasks
- Reference knowledge and conventions
- Step-by-step workflows
- Specialized behaviors

Skills follow the **Agent Skills open standard** and use:
- YAML frontmatter (metadata)
- Markdown content (instructions)

### Skill File Structure

Each skill is a directory with at least a `SKILL.md` file:

```
~/.claude/skills/python-testing/
├── SKILL.md              # Required: Main instructions
├── template.md           # Optional: Template for Claude to fill
├── examples/
│   └── test-example.md   # Optional: Example outputs
└── scripts/
    └── run-tests.sh      # Optional: Executable scripts
```

### SKILL.md Format

The core of a skill is `SKILL.md` with two parts:

#### 1. YAML Frontmatter (Metadata)

```yaml
---
name: python-testing
description: Testing guidelines and best practices for Python projects. Use when writing tests, ensuring coverage, or following TDD.

argument-hint: [test-file]
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Bash(python:*)
---
```

**Frontmatter Fields**:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Skill name (becomes `/skill-name`). Defaults to directory name. Max 64 chars, lowercase letters, numbers, hyphens only. |
| `description` | Recommended | What the skill does and when to use it. Claude uses this to auto-invoke. |
| `argument-hint` | No | Hint shown during autocomplete (e.g., `[issue-number]`) |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from auto-loading. Only user can invoke. |
| `user-invocable` | No | Set to `false` to hide from `/` menu. Background knowledge only. |
| `allowed-tools` | No | Tools Claude can use without permission when skill is active. |
| `context` | No | Set to `fork` to run in a subagent. |
| `agent` | No | Which subagent type when `context: fork` is set. |

#### 2. Markdown Content (Instructions)

The markdown content provides instructions Claude follows when the skill is invoked:

```markdown
# Python Testing Guidelines

When writing tests for Python projects, follow these principles:
