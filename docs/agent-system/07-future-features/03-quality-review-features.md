# Quality & Code Review Features

## Feature 10: Review Checklists

### Overview

Standardized review checklists ensure consistent, thorough code reviews by requiring reviewers to verify specific items before approving work. Prevents forgotten checks and provides training for junior reviewers.

### Why It Matters

- **Consistency**: Every review covers the same quality standards
- **Completeness**: Nothing gets forgotten in the review process
- **Training**: Junior reviewers learn what to check via checklists
- **Traceability**: Audit trail of what was reviewed and verified
- **Quality Gate**: Tasks cannot be approved until checklist is complete

### How It Works

#### Creating Checklist Templates

```bash
# Create a new checklist template
agentflow review checklist create \
  --name "feature-review" \
  --title "Feature Development Review Checklist" \
  --description "Standard checklist for reviewing feature development tasks" \
  --items \
    "Code follows project conventions" \
    "Tests added/updated (coverage >80%)" \
    "Documentation updated" \
    "No security vulnerabilities" \
    "No performance regression" \
    "Error handling implemented" \
    "Git commits are clean" \
    "No hardcoded values" \
    "Edge cases handled" \
    "Code is readable and maintainable"

# Output:
# ✅ Checklist template created
#    Name: feature-review
#    Items: 10
#
# Use this checklist when creating tasks:
#   agentflow task create --review-checklist feature-review ...
```

#### Managing Checklist Items

```bash
# Add items to existing checklist
agentflow review checklist add-items \
  feature-review \
  --items \
    "API documentation updated" \
    "Logging added where appropriate"

# Remove items
agentflow review checklist remove-items \
  feature-review \
  --items "Git commits are clean"

# Update item description
agentflow review checklist update-item \
  feature-review \
  --item "Tests added/updated" \
  --description "Unit tests + integration tests, coverage >80%, edge cases covered"

# Reorder items (for display order)
agentflow review checklist reorder \
  feature-review \
  --items "Code follows project conventions,Tests added/updated,Documentation updated"
```

#### Attaching Checklists to Tasks

```bash
# Create task with checklist
agentflow task create \
  --title "Implement user authentication" \
  --type development \
  --priority P1 \
  --estimate 4h \
  --review-checklist feature-review \
  --assign-to agent-dev-001 \
  --project website-redesign

# Output:
# ✅ Task created
#    Task: #123 - Implement user authentication
#    Review checklist: feature-review (10 items)
#
# When task is marked "ready_review", checklist will be required

# Or add checklist to existing task
agentflow task set-checklist 123 --checklist feature-review
```

#### Built-in Checklists

```bash
# List available checklists
agentflow review checklist list

# Output:
# Available Checklist Templates
# ─────────────────────────────────────
#
# Built-in:
#   feature-review      Feature development (10 items)
#   bug-fix             Bug fix review (7 items)
#   security-review     Security-focused review (15 items)
#   performance-review  Performance review (8 items)
#   documentation       Documentation review (5 items)
#
# Custom:
#   api-endpoint        API development (your org) - 12 items
#   frontend-component  Frontend component (your org) - 9 items

# View a checklist template
agentflow review checklist view feature-review

# Output:
# 📋 Checklist: feature-review
# ─────────────────────────────────────
# Feature Development Review Checklist
#
# Items (10):
#   1. Code follows project conventions
#   2. Tests added/updated (coverage >80%)
#   3. Documentation updated
#   4. No security vulnerabilities
#   5. No performance regression
#   6. Error handling implemented
#   7. No hardcoded values
#   8. Edge cases handled
#   9. Code is readable and maintainable
#   10. API documentation updated
#
# Used in: 23 tasks
# Avg. completion time: 15 minutes
```

#### Reviewing with Checklist

```bash
# When task is ready for review
agentflow task review 123

# Output:
# 🔍 Review Task - #123
# ─────────────────────────────────────
# Task: Implement user authentication
# Author: Jean (agent-dev-001)
# Reviewer: You (agent-lead-001)
#
# 📋 Review Checklist: feature-review
# Progress: 3/10 items checked (30%)
#
# Checklist Items:
#   ☑ 1. Code follows project conventions           [check] [skip] [n/a]
#   ☐ 2. Tests added/updated (coverage >80%)        [check] [skip] [n/a]
#   ☑ 3. Documentation updated                      [check] [skip] [n/a]
#   ☐ 4. No security vulnerabilities                [check] [skip] [n/a]
#   ☐ 5. No performance regression                  [check] [skip] [n/a]
#   ☑ 6. Error handling implemented                 [check] [skip] [n/a]
#   ☐ 7. No hardcoded values                        [check] [skip] [n/a]
#   ☐ 8. Edge cases handled                         [check] [skip] [n/a]
#   ☐ 9. Code is readable and maintainable          [check] [skip] [n/a]
#   ☐ 10. API documentation updated                 [check] [skip] [n/a]
#
# Actions:
#   # Check an item
#   agentflow task checklist 123 --item 2 --check
#
#   # Skip item (not applicable)
#   agentflow task checklist 123 --item 5 --skip --reason "No performance impact"
#
#   # Uncheck item (mistake)
#   agentflow task checklist 123 --item 3 --uncheck
#
#   # View item details
#   agentflow task checklist 123 --item 2 --view

# Check items one by one
agentflow task checklist 123 --item 2 --check

# Output:
# ✅ Item checked
#    Item #2: Tests added/updated (coverage >80%)
#    Progress: 4/10 (40%)

agentflow task checklist 123 --item 4 --check

# Output:
# ✅ Item checked
#    Item #4: No security vulnerabilities
#    Progress: 5/10 (50%)

# Skip an item
agentflow task checklist 123 --item 5 --skip --reason "Simple feature, no perf impact"

# Output:
# ⏭️  Item skipped
#    Item #5: No performance regression
#    Reason: Simple feature, no perf impact
#    Progress: 5/10 (50%) + 1 skipped

# When all items checked (or skipped):
# ✅ Checklist complete!
#    Checked: 9
#    Skipped: 1 (with reasons)
#
# You can now approve or reject this task.
```

#### Checklist Actions

```bash
# Check single item
agentflow task checklist <task-id> --item <number> --check

# Skip item (requires reason)
agentflow task checklist <task-id> --item <number> --skip --reason "<reason>"

# Uncheck item
agentflow task checklist <task-id> --item <number> --uncheck

# Check all items
agentflow task checklist <task-id> --check-all

# View item details
agentflow task checklist <task-id> --item <number> --view

# Add comment to item
agentflow task checklist <task-id> --item <number> --comment "Tests cover main flow but missing edge cases"

# View checklist progress
agentflow task checklist <task-id> --progress
```

#### Conditional Checklists

```bash
# Create conditional checklist (based on task properties)
agentflow review checklist create \
  --name "conditional-security" \
  --conditional \
  --rules \
    "if task.tags contains 'security' then use 'security-review' checklist" \
    "if task.type is 'bug' then use 'bug-fix' checklist" \
    "if task.priority is 'P0' then add 'extra-qa' checklist"

# Apply conditional checklist to task
agentflow task set-checklist 123 --checklist conditional-security

# System determines which actual checklist to use based on task properties
```

#### Checklist Statistics

```bash
# View checklist effectiveness
agentflow review checklist stats feature-review

# Output:
# 📊 Checklist Stats: feature-review
# ─────────────────────────────────────
# Usage: 45 reviews
#
# Completion:
#   Avg. time to complete: 18 minutes
#   Fully checked: 42 (93%)
#   Partially skipped: 3 (7%)
#
# Commonly Skipped Items:
#   1. "No performance regression" - Skipped 8 times
#      Most common reason: "No performance impact"
#
#   2. "API documentation updated" - Skipped 5 times
#      Most common reason: "Internal API only"
#
# Quality Impact:
#   Bugs found during review: 12
#   Issues caught post-merge: 2
#   Quality score: 9.2/10
#
# 💡 Suggestions:
#   • Consider making "No performance regression" optional for simple features
#   • Add "API documentation" only when task has 'api' tag
```

### Data Model

```python
class ReviewChecklistTemplate(BaseModel):
    id: str
    name: str  # "feature-review"
    title: str
    description: Optional[str]
    is_builtin: bool = False
    created_by: Optional[str] = None  # Agent ID (for custom)

    items: List["ChecklistItem"]
    conditional_rules: Optional[List[str]] = None  # For conditional checklists

    # Stats
    usage_count: int = 0
    avg_completion_minutes: float = 0.0

class ChecklistItem(BaseModel):
    id: str
    template_id: str
    text: str  # "Code follows project conventions"
    description: Optional[str]  # More detailed explanation
    order: int  # Display order
    is_optional: bool = False  # If true, can be skipped

class TaskChecklist(BaseModel):
    id: str
    task_id: str
    template_id: str
    reviewer_agent_id: str

    items: List["TaskChecklistItem"]
    status: Literal["in_progress", "completed", "skipped"]
    started_at: datetime
    completed_at: Optional[datetime]

class TaskChecklistItem(BaseModel):
    id: str
    checklist_id: str
    template_item_id: str

    status: Literal["unchecked", "checked", "skipped"]
    skipped_reason: Optional[str] = None
    comment: Optional[str] = None

    checked_by: Optional[str] = None  # Agent ID
    checked_at: Optional[datetime] = None
```

### CLI Commands

```bash
# Template management
agentflow review checklist create --name <name> --items <item1,item2>
agentflow review checklist list
agentflow review checklist view <name>
agentflow review checklist delete <name>

# Template items
agentflow review checklist add-items <name> --items <item1,item2>
agentflow review checklist remove-items <name> --items <item1>
agentflow review checklist update-item <name> --item <item-text> --description <desc>

# Task checklist
agentflow task create --review-checklist <name>
agentflow task set-checklist <task-id> --checklist <name>
agentflow task checklist <task-id> --item <number> --check
agentflow task checklist <task-id> --item <number> --skip --reason <reason>
agentflow task checklist <task-id> --check-all
agentflow task checklist <task-id> --progress

# Stats
agentflow review checklist stats <name>
```

---

## Feature 11: Self-Review System

### Overview

Agents perform self-reviews before marking tasks as ready for review, listing what they've already verified. Reviewers see the self-review and focus on unchecked items, saving time and improving efficiency.

### Why It Matters

- **Efficiency**: Reviewers don't waste time re-checking verified items
- **Learning**: Agents learn to self-evaluate their work
- **Focus**: Reviewers concentrate on unverified or risky areas
- **Communication**: Reduces back-and-forth ("did you check X?")
- **Quality**: Encourages agents to verify before submitting

### How It Works

#### Self-Review Process

```bash
# Agent completes work and wants to mark "ready_review"
agentflow task update 123 --status ready_review

# System prompts for self-review (if not already done)
# ⚠️  Self-review required before marking as ready_review
#     Run: agentflow task self-review 123

# Or agent proactively does self-review
agentflow task self-review 123

# Output:
# 📝 Self-Review - Task #123
# ───────────────────────────────────────
# Task: Implement user authentication
# Author: Jean (agent-dev-001)
#
# Help the reviewer by listing what you've already verified.
# Answer honestly - this helps the reviewer focus on actual concerns.
#
# Standard Checks:
#
# 1. Did you write tests for this work?
#    [Y/n/S] y
#    → Please describe:
#    ✅ 12 unit tests for authentication logic
#    ✅ 4 integration tests for API endpoints
#    ✅ Coverage: 87%
#
# 2. Did you update documentation?
#    [Y/n/S] y
#    → Please describe:
#    ✅ Updated README.md with setup instructions
#    ✅ Added API documentation to api/auth.md
#
# 3. Did you check for security issues?
#    [Y/n/S] y
#    → Please describe:
#    ✅ Reviewed for SQL injection - safe
#    ✅ Checked XSS vulnerabilities - none found
#    ✅ CSRF tokens implemented
#    ✅ Passwords hashed with bcrypt
#
# 4. Did you test performance?
#    [Y/n/S] n
#    → Why not?
#    Not sure how to benchmark this. Please verify.
#
# 5. Did you follow code style conventions?
#    [Y/n/S] y
#    → Please describe:
#    ✅ Ran: black src/ (formatted)
#    ✅ Ran: mypy src/ (no errors)
#    ✅ Ran: pylint src/ (9.5/10)
#
# 6. Did you handle edge cases?
#    [Y/n/S] y
#    → Please describe:
#    ✅ Empty password
#    ✅ Invalid email format
#    ✅ Token expiration
#    ✅ Concurrent login attempts
#
# 7. Did you add error handling?
#    [Y/n/S] y
#    → Please describe:
#    ✅ Try/except on all I/O operations
#    ✅ Meaningful error messages
#    ✅ Logging added for errors
#
# Additional notes for reviewer:
# (optional - press Enter to skip)
# ⚠️  I'm unsure about the token refresh logic - please review carefully.

# ✅ Self-review complete!
#
# Summary for Reviewer:
# ─────────────────────────────────────
# ✅ Tests: Written and passing (87% coverage)
# ✅ Documentation: Updated (README, API docs)
# ✅ Security: Reviewed (SQLi, XSS, CSRF, passwords safe)
# ⚠️  Performance: NOT checked (needs reviewer attention)
# ✅ Code style: Enforced (black, mypy, pylint passed)
# ✅ Edge cases: Handled (empty password, invalid email, etc.)
# ✅ Error handling: Implemented
#
# ⚠️  Areas needing reviewer attention:
#    • Performance - author unsure how to benchmark
#    • Token refresh logic - author requests careful review
#
# Task #123 can now be marked as "ready_review"
# Proceed? [Y/n]

# Agent confirms
> y

# ✅ Task #123 marked as ready_review
#    Self-review attached
#    Reviewer notified
```

#### Reviewer sees Self-Review

```bash
# Reviewer opens the task
agentflow task review 123

# Output:
# 🔍 Review Task - #123
# ─────────────────────────────────────
# Task: Implement user authentication
# Author: Jean (agent-dev-001)
# Status: ready_review
# Priority: P1
#
# 👤 Author's Self-Review:
# ───────────────────────────────────────────
#
# ✅ Verified by Author (6 items):
#
#   1. ✅ Tests: Written and passing (87% coverage)
#      "12 unit tests for authentication logic
#       4 integration tests for API endpoints"
#
#   2. ✅ Documentation: Updated
#      "README.md with setup instructions
#       API documentation added to api/auth.md"
#
#   3. ✅ Security: Reviewed
#      "SQL injection: Safe
#       XSS: None found
#       CSRF: Tokens implemented
#       Passwords: Hashed with bcrypt"
#
#   4. ✅ Code style: Enforced
#      "black: Formatted
#       mypy: No errors
#       pylint: 9.5/10"
#
#   5. ✅ Edge cases: Handled
#      "Empty password, Invalid email, Token expiration,
#       Concurrent login attempts"
#
#   6. ✅ Error handling: Implemented
#      "Try/except on I/O, meaningful errors, logging added"
#
# ⚠️  NOT Verified (2 items):
#
#   1. ⚠️  Performance: NOT checked
#      Reason: "Not sure how to benchmark"
#      → ⚠️ REVIEWER: Please verify performance!
#
#   2. ⚠️  Token refresh logic: Needs review
#      Note: "I'm unsure about the token refresh logic"
#      → ⚠️ REVIEWER: Careful review requested
#
# ───────────────────────────────────────────
#
# 📋 Your Review Focus:
# Based on self-review, please verify:
#
#   High Priority (author didn't check):
#   ☐ Performance benchmarking
#   ☐ Token refresh logic (author requested review)
#
#   Medium Priority (spot-check author's work):
#   ☐ Security review (author says safe - verify)
#   ☐ Edge cases (author says handled - verify)
#   ☐ Error handling (author says implemented - verify)
#
#   Low Priority (author verified):
#   ☐ Tests (author reports 87% coverage - spot check)
#   ☐ Documentation (author says updated - quick verify)
#   ☐ Code style (tools passed - trust result)
#
# Actions:
#   agentflow task approve 123 --comment "Self-review was thorough, only checked performance"
#   agentflow task reject 123 --reason "Performance issue found: ..."
#   agentflow task request-changes 123 --changes "Fix token refresh logic"
```

#### Self-Review Templates

```bash
# Create custom self-review template
agentflow self-review template create \
  --name "frontend-self-review" \
  --title "Frontend Development Self-Review" \
  --questions \
    "Did you test on multiple browsers?" \
    "Did you check accessibility?" \
    "Did you verify responsive design?" \
    "Did you test with different screen sizes?" \
    "Did you check console for errors?"

# Use template for task
agentflow task set-self-review 123 --template frontend-self-review

# Or set at project level
agentflow project set-default-self-review my-project --template frontend-self-review
# All tasks in project use this template
```

#### Self-Review Stats

```bash
# View agent's self-review accuracy
agentflow agent self-review-stats agent-dev-001

# Output:
# 📊 Self-Review Stats - Jean (agent-dev-001)
# ───────────────────────────────────────────
# Last 30 days | 15 tasks reviewed
#
# Self-Review Accuracy: 92% ✅ Excellent
#    (9.2/10 items verified by author were confirmed by reviewer)
#
# Breakdown:
#   Tests: 95% accuracy (19/20 verified)
#   Documentation: 100% accuracy (15/15 verified)
#   Security: 85% accuracy (11/13 verified)
#   Performance: 70% accuracy (7/10 verified) ⚠️
#
# Common Mistakes (author marked "checked" but reviewer found issues):
#   • Performance: 3 times marked "checked" but issues found
#     → Recommendation: Don't mark performance as checked
#     → Add note: "Needs reviewer verification"
#
#   • Security: 2 times marked "safe" but minor issues found
#     → Recommendation: Be more conservative with security claims
#
# Strengths:
#   • Documentation: Always thorough
#   • Tests: Reliable assessment
#
# 💡 Suggestions:
#   1. Don't mark performance as "checked" - let reviewer verify
#   2. For security, mark as "reviewed" but add "please double-check"
#   3. Keep doing great work on tests and docs!
```

#### Self-Review Configuration

```bash
# Make self-review mandatory
agentflow config set --key require_self_review --value true

# Now all tasks MUST have self-review before "ready_review"
agentflow task update 123 --status ready_review
# Error: Self-review required. Run: agentflow task self-review 123

# Or make optional
agentflow config set --key require_self_review --value false

# Auto-prompt for self-review
agentflow config set --key auto_prompt_self_review --value true
# When agent tries "ready_review", automatically prompt for self-review
```

### Data Model

```python
class SelfReview(BaseModel):
    id: str
    task_id: str
    author_agent_id: str
    created_at: datetime

    checks: List["SelfReviewCheck"]
    additional_notes: Optional[str] = None

    # Reviewer's assessment
    reviewer_agent_id: Optional[str] = None
    reviewer_assessment: Optional[Literal["accurate", "mostly_accurate", "issues_found"]] = None
    reviewer_comments: Optional[str] = None

class SelfReviewCheck(BaseModel):
    id: str
    self_review_id: str
    question: str  # "Did you write tests?"
    answer: Literal["yes", "no", "partial"]
    details: Optional[str] = None  # Author's explanation

    # Reviewer's verification
    reviewer_verified: Optional[bool] = None  # True = confirmed, False = issue found, None = not reviewed
    reviewer_notes: Optional[str] = None

class SelfReviewTemplate(BaseModel):
    id: str
    name: str  # "frontend-self-review"
    title: str
    questions: List[str]  # List of questions to ask
    is_builtin: bool = False
```

### CLI Commands

```bash
# Self-review
agentflow task self-review <task-id>
agentflow task set-self-review <task-id> --template <template-name>

# Templates
agentflow self-review template create --name <name> --questions <q1,q2,q3>
agentflow self-review template list
agentflow self-review template view <name>

# Stats
agentflow agent self-review-stats <agent-code>

# Config
agentflow config set --key require_self_review --value <true|false>
agentflow config set --key auto_prompt_self_review --value <true|false>
```

---

## Feature 12: Code Annotation Tracking (TODO/FIXME/HACK)

### Overview

Track code annotations (TODO, FIXME, HACK, XXX, NOTE) created by agents, with the ability to convert them into tasks, set priorities, and maintain visibility into technical debt and future work.

### Why It Matters

- **Visibility**: TODOs don't get lost in code comments
- **Prioritization**: Convert important TODOs into actual tasks
- **Accountability**: Know who created each annotation
- **Technical Debt**: Track HACKs and FIXMEs that need proper solutions
- **Planning**: See all pending work hinted at in code

### How It Works

#### Creating Annotations

```bash
# During a session, agent creates an annotation
agentflow session annotate \
  --file src/auth.py \
  --line 45 \
  --type TODO \
  --message "Add rate limiting for login endpoint (DOS prevention)" \
  --priority P2 \
  --tag security,performance

# Output:
# ✅ Code annotation created
#    Type: TODO
#    File: src/auth.py:45
#    Message: "Add rate limiting for login endpoint (DOS prevention)"
#    Priority: P2
#    Tags: security, performance
#    ID: #1

# Can also add directly to code file
agentflow session annotate \
  --file src/auth.py \
  --line 45 \
  --type TODO \
  --message "Add rate limiting" \
  --add-to-code

# This adds to the file:
# TODO(agentflow-1): Add rate limiting for login endpoint (DOS prevention)

# Annotation with task context
agentflow session annotate \
  --file src/auth.py \
  --line 45 \
  --type FIXME \
  --message "This N+1 query needs optimization" \
  --task 123 \
  --tag performance,database

# Output:
# ✅ Code annotation created
#    Type: FIXME
#    File: src/auth.py:45
#    Message: "This N+1 query needs optimization"
#    Linked to task: #123 - Implement user authentication
#    Tags: performance, database
```

#### Supported Annotation Types

```bash
# TODO - Future work to be done
--type TODO

# FIXME - Broken code that needs fixing
--type FIXME

# HACK - Quick/temporary solution that needs proper implementation
--type HACK

# XXX - Uncertain code, needs review or clarification
--type XXX

# NOTE - Informational comment (no action needed)
--type NOTE

# BUG - Known bug (not critical enough for immediate fix)
--type BUG
```

#### Listing Annotations

```bash
# List all annotations
agentflow annotations list

# Output:
# 📝 Code Annotations - All
# ─────────────────────────────────────
# 47 annotations found
#
# By Type:
#   TODO: 28
#   FIXME: 12
#   HACK: 5
#   XXX: 2
#
# By Agent:
#   Jean (agent-dev-001): 18 annotations
#   Alice (agent-dev-002): 15 annotations
#   Bob (agent-qa-001): 14 annotations
#
# ┌─────────────────────────────────────────────────────────────────┐
# │ ID │ Type   │ File          │ Line │ Agent    │ Age            │
# ├─────────────────────────────────────────────────────────────────┤
# │ #1 │ TODO   │ src/auth.py   │ 45   │ Jean     │ 2 hours ago    │
# │ #2 │ FIXME  │ src/user.py   │ 123  │ Alice    │ 1 day ago      │
# │ #3 │ HACK   │ src/cache.py  │ 67   │ Bob      │ 3 days ago     │
# │ #4 │ TODO   │ src/api.py    │ 89   │ Jean     │ 5 days ago     │
# └─────────────────────────────────────────────────────────────────┘

# Filter by type
agentflow annotations list --type FIXME

# Filter by agent
agentflow annotations list --agent agent-dev-001

# Filter by file
agentflow annotations list --file src/auth.py

# Filter by priority
agentflow annotations list --priority P0,P1

# Filter by age (stale annotations)
agentflow annotations list --stale --older-than 30d

# Output:
# ⚠️  Stale Annotations (older than 30 days)
# ───────────────────────────────────────────
# 8 annotations unresolved for >30 days
#
#   FIXME src/user.py:123 - "N+1 query" (45 days) - Alice
#   TODO src/db.py:45 - "Add migration" (60 days) - Jean
#   HACK src/cache.py:67 - "Quick fix" (90 days) - Bob
#
# 💡 Suggestion: Convert these to tasks or resolve them
#    agentflow annotations convert-to-task --annotation 2,3,4
```

#### Converting Annotations to Tasks

```bash
# Convert annotation to task
agentflow annotations convert-to-task --annotation 1

# Output:
# ✅ Task created from annotation
#    Annotation: #1 - "Add rate limiting for login endpoint"
#    New Task: #128
#
# Task Details:
#   Title: Add rate limiting for login endpoint
#   Description: Code annotation from Jean @ src/auth.py:45
#                "Add rate limiting for login endpoint (DOS prevention)"
#   Type: development
#   Priority: P2 (inherited from annotation)
#   Tags: security, performance
#   Project: website-redesign (inherited from current context)
#   Assigned to: Jean (same agent who created annotation)
#
# Annotation #1 linked to task #128
#
# Start working: agentflow task update 128 --status in_progress

# Convert multiple annotations
agentflow annotations convert-to-task \
  --annotations 1,2,3,4,5 \
  --assign-to agent-dev-002

# Output:
# ✅ 5 tasks created from annotations
#    Assigned to: agent-dev-002
#
# Tasks created:
#   #128: Add rate limiting (from TODO #1)
#   #129: Fix N+1 query (from FIXME #2)
#   #130: Proper cache implementation (from HACK #3)
#   #131: Add user migration (from TODO #4)
#   #132: Review uncertain code (from XXX #5)
#
# All annotations marked as "converted"

# Convert with options
agentflow annotations convert-to-task \
  --annotation 1 \
  --title "Implement login rate limiting" \
  --estimate 2h \
  --priority P1 \
  --assign-to agent-dev-002
```

#### Managing Annotations

```bash
# View annotation details
agentflow annotations view 1

# Output:
# 📝 Annotation #1
# ─────────────────────────────────────
# Type: TODO
# File: src/auth.py:45
# Message: "Add rate limiting for login endpoint (DOS prevention)"
#
# Metadata:
#   Created by: Jean (agent-dev-001)
#   Created at: 2025-01-21 10:30
#   Priority: P2
#   Tags: security, performance
#   Linked task: #128
#
# Status: converted_to_task
#
# Context:
#   Session: session-abc-123
#   Task: #123 - Implement user authentication
#
# Code context (3 lines):
#   44: def login(username, password):
#   45:     # TODO(agentflow-1): Add rate limiting for login endpoint
#   46:     user = authenticate(username, password)

# Resolve annotation (without converting to task)
agentflow annotations resolve --annotation 1 \
  --reason "Implemented in task #128"

# Output:
# ✅ Annotation #1 resolved
#    Reason: Implemented in task #128
#    Status: resolved

# Defer annotation (remind later)
agentflow annotations defer --annotation 1 \
  --until "2025-02-15" \
  --reason "Review in next sprint"

# Output:
# ✅ Annotation #1 deferred
#    Reminder: 2025-02-15
#    Reason: Review in next sprint
#    Status: deferred

# Update annotation
agentflow annotations update --annotation 1 \
  --message "Add rate limiting - use Redis sliding window" \
  --priority P1

# Delete annotation (use carefully)
agentflow annotations delete --annotation 1
```

#### Annotation Reports

```bash
# Generate code quality report
agentflow annotations report

# Output:
# 📊 Code Quality Report - Annotations
# ────────────────────────────────────────────
# As of: 2025-01-21
# Project: website-redesign
#
# Summary:
#   Total annotations: 47
#   Open: 38
#   Resolved: 7
#   Converted to tasks: 2
#
# By Type:
#   TODO: 28 (59%) - Future work
#   FIXME: 12 (26%) - Broken code
#   HACK: 5 (11%) - Quick fixes
#   XXX: 2 (4%) - Uncertain code
#
# By File:
#   src/auth.py: 8 TODOs, 2 FIXMEs (10 total)
#   src/user.py: 5 TODOs, 3 FIXMEs (8 total)
#   src/db.py: 4 TODOs, 1 HACK (5 total)
#
# By Agent:
#   Jean: 18 annotations (avg age: 12 days)
#   Alice: 15 annotations (avg age: 8 days)
#   Bob: 14 annotations (avg age: 15 days)
#
# Age Distribution:
#   < 1 week: 24 (51%)
#   1-4 weeks: 11 (23%)
#   > 4 weeks: 12 (26%) ⚠️ Stale
#
# Priority Breakdown:
#   P0 (critical): 3 FIXMEs
#   P1 (high): 7 TODOs/FIXMEs
#   P2 (medium): 15 TODOs
#   P3 (low): 22 TODOs
#
# Technical Debt:
#   HACKs: 5 (need proper solutions)
#   Avg age of HACKs: 45 days ⚠️
#
# ⚠️  Recommendations:
#   1. Resolve 3 P0 FIXMEs this week
#   2. Convert 8 stale TODOs to tasks or close them
#   3. Review 5 HACKs for proper solutions (avg age 45 days)
#   4. Address 12 stale annotations (>4 weeks old)
#
# 📈 Trend:
#   Annotations created this week: +5
#   Annotations resolved this week: +3
#   Net change: +2 (technical debt increasing)
```

#### Searching Annotations

```bash
# Search by message content
agentflow annotations search "rate limiting"

# Output:
# 📝 Search Results: "rate limiting"
# ─────────────────────────────────────
# 3 annotations found
#
# #1 - TODO - src/auth.py:45
#     "Add rate limiting for login endpoint"
#     Age: 2 hours
#
# #15 - TODO - src/api.py:123
#     "Add rate limiting to all public endpoints"
#     Age: 5 days
#
# #27 - FIXME - src/auth.py:89
#     "Rate limiting not working for concurrent requests"
#     Age: 2 weeks

# Search by tag
agentflow annotations search --tag security

# Search by multiple criteria
agentflow annotations search \
  --type FIXME \
  --tag performance \
  --older-than 7d

# Output:
# 📝 Search Results
# ─────────────────────────────────────
# Type: FIXME
# Tag: performance
# Age: >7 days
#
# 2 annotations found
#
# #2 - FIXME - src/user.py:123
#     "N+1 query needs optimization"
#     Age: 45 days
#     Tags: performance, database
#
# #8 - FIXME - src/cache.py:67
#     "Cache invalidation slow"
#     Age: 12 days
#     Tags: performance, cache
```

#### Annotation Dashboard

```bash
# Interactive annotation dashboard
agentflow annotations dashboard

# Output:
# 📊 Annotation Dashboard
# ─────────────────────────────────────
#
# Quick Stats:
#   Total: 47 | Open: 38 | Resolved: 7 | Converted: 2
#
# [1] List by type
# [2] List by priority
# [3] Show stale annotations (>30 days)
# [4] Show by file
# [5] Show by agent
# [6] Convert to tasks
# [7] Generate report
# [8] Search
# [0] Exit
#
# Your choice: _
```

### Data Model

```python
class CodeAnnotation(BaseModel):
    id: str  # UUID or sequential #1, #2, etc.
    type: Literal["TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG"]

    # Location
    file_path: str
    line_number: int
    function_name: Optional[str] = None  # Extracted from code context

    # Content
    message: str
    priority: Optional[Literal["P0", "P1", "P2", "P3"]] = None
    tags: List[str] = []

    # Creation
    agent_id: str  # Who created it
    session_id: Optional[str] = None  # Created during session
    task_id: Optional[str] = None  # Related to task
    created_at: datetime

    # Status
    status: Literal["open", "converted_to_task", "resolved", "deferred"]
    linked_task_id: Optional[str] = None  # If converted
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_note: Optional[str] = None

    # Deferment
    defer_until: Optional[datetime] = None
    defer_reason: Optional[str] = None

    # In-code annotation (if --add-to-code was used)
    added_to_code: bool = False

    @property
    def is_stale(self) -> bool:
        """Stale if open for >30 days"""
        if self.status != "open":
            return False
        days_open = (datetime.now() - self.created_at).days
        return days_open > 30

    @property
    def age_days(self) -> int:
        """Age in days"""
        return (datetime.now() - self.created_at).days

class AnnotationStats(BaseModel):
    total_annotations: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_agent: Dict[str, int]
    by_file: Dict[str, int]

    stale_count: int
    avg_age_days: float

    technical_debt_score: float  # Based on HACK/FIXME count and age
```

### CLI Commands

```bash
# Creating annotations
agentflow session annotate --file <path> --line <number> --type <TODO|FIXME> --message "<text>"
agentflow session annotate --file <path> --line <number> --type TODO --add-to-code

# Listing
agentflow annotations list
agentflow annotations list --type <FIXME|TODO>
agentflow annotations list --agent <agent-code>
agentflow annotations list --file <path>
agentflow annotations list --stale --older-than <30d>

# Converting
agentflow annotations convert-to-task --annotation <id>
agentflow annotations convert-to-task --annotations <id1,id2,id3>

# Managing
agentflow annotations view <id>
agentflow annotations resolve --annotation <id> --reason "<text>"
agentflow annotations defer --annotation <id> --until <date> --reason "<text>"
agentflow annotations update --annotation <id> --message "<text>" --priority <P1>

# Reporting
agentflow annotations report
agentflow annotations dashboard

# Searching
agentflow annotations search "<text>"
agentflow annotations search --tag <tag> --type <FIXME>
```

---

## Implementation Notes

### Dependencies

- **Feature 10 (Review Checklists)**: Requires tasks, review workflow
- **Feature 11 (Self-Review)**: Requires tasks, agents
- **Feature 12 (Annotation Tracking)**: Requires sessions, agents

### Priority

1. **Feature 11 (Self-Review)** - High value, relatively simple, saves reviewer time
2. **Feature 10 (Review Checklists)** - Medium value, more complex, improves consistency
3. **Feature 12 (Annotation Tracking)** - Medium value, visibility into technical debt

### Phasing

- **Phase 1**: Self-review system (basic workflow)
- **Phase 2**: Review checklists (template-based)
- **Phase 3**: Annotation tracking (code integration)

### Integration Points

- **With Tasks**: Checklist attached to task, self-review required before "ready_review"
- **With Sessions**: Annotations created during active sessions
- **With Review**: Checklist + self-review visible in review workflow

---

**Document Version**: 1.0
**Created**: 2025-01-21
**Status**: 🎨 Design proposal - Ready for review
