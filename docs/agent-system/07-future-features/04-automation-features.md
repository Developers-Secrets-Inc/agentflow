# Automation & Event-Driven Features

## Feature 13: Triggers & Automation Rules

### Overview

An event-driven automation system that executes predefined actions when specific events occur (e.g., automatically create review tasks when a task is marked ready for review, send alerts when trust score drops, etc.).

### Why It Matters

- **Eliminate Repetition**: No need to manually create review tasks, send reminders, etc.
- **Prevent Errors**: Automated actions don't forget or make mistakes
- **Faster Response**: Immediate reaction to events without human intervention
- **Complex Workflows**: Chain multiple actions together for sophisticated automation

### How It Works

#### Understanding Triggers

A **trigger** consists of:
1. **Event**: What happens (task.completed, agent.trust_dropped, etc.)
2. **Condition** (optional): When to execute (if priority == P0, etc.)
3. **Action**: What to do (create_task, send_alert, etc.)

```
Event Occurs → Check Condition → Execute Action → Log Result
```

#### Creating Your First Trigger

```bash
# Auto-create review task when worker marks task "ready_review"
agentflow trigger create \
  --name "auto-create-review-task" \
  --on "task.status_changed_to:ready_review" \
  --action "create_review_task_for_supervisor"

# Output:
# ✅ Trigger created
#    Name: auto-create-review-task
#    Event: task.status_changed_to:ready_review
#    Action: create_review_task_for_supervisor
#    Status: Active
#
# This trigger will now automatically create a review task
# for the supervisor whenever a task is marked "ready_review".
#
# View trigger: agentflow trigger view auto-create-review-task
```

#### How It Works in Practice

```bash
# Worker agent completes work
agentflow task update 123 --status ready_review

# Behind the scenes:
# 1. Event fired: task.status_changed_to:ready_review
# 2. Trigger detected: auto-create-review-task
# 3. Action executed:
#    - Created task #124 (Review task #123)
#    - Assigned to: Tech Lead (supervisor of Jean)
#    - Type: review
#    - Parent task: #123
# 4. Result logged: Success

# Worker sees:
# ✅ Task #123 marked as ready_review
#    Review task #124 created for Tech Lead

# Supervisor sees:
# 📬 New review task: #124
#    Task: Review task #123
#    From: Jean (agent-dev-001)
```

#### Available Events

```bash
# Task Events
task.created                              # Task created
task.status_changed_to:<status>           # Status changed to specific value
task.status_changed                       # Any status change
task.priority_changed_to:<priority>       # Priority changed
task.assigned                             # Task assigned to agent
task.completed                            # Task marked completed
task.rejected                             # Task rejected
task.blocked                              # Task blocked

# Agent Events
agent.created                             # Agent created
agent.status_changed_to:<status>          # Agent status changed
agent.trust_dropped_below:<score>         # Trust score dropped below threshold
agent.trust_increased_above:<score>       # Trust score increased above threshold
agent.probation_started                   # Agent entered probation
agent.probation_ended                     # Agent exited probation
agent.session_started                     # Agent started session
agent.session_ended                       # Agent ended session
agent.terminated                          # Agent terminated

# Message Events
message.sent                              # Message sent
message.unread_for:<duration>             # Message unread for X time
message.from_agent_to_supervisor          # Message sent upward

# Session Events
session.started                           # Session started
session.ended                             # Session ended
session.idle_for:<duration>               # Session idle for X time
session.duration_exceeded:<duration>      # Session longer than X

# Schedule Events
schedule.every_day_at:<HH:MM>            # Every day at specific time
schedule.every_week_on:<day>              # Every week on specific day
schedule.every_month_on:<day>             # Every month on specific day
schedule.every_<duration>                 # Every X (hour, day, week)

# Organization Events
org.agent_joined                          # Agent joined organization
org.agent_left                            # Agent left organization
org.project_created                       # Project created

# Custom Events
custom.<event_name>                       # User-defined events
```

#### Available Actions

```bash
# Task Actions
create_task --template <name> --assign-to <agent>
create_review_task --for-supervisor
create_review_task --for-agent <agent-id>
reassign_task --task <id> --to <agent>
update_task --task <id> --status <status> --priority <priority>
cancel_task --task <id>

# Agent Actions
adjust_trust_score --agent <agent> --change <+5|-2>
set_trust_score --agent <agent> --score <value>
send_agent_message --to <agent> --content "<text>"

# Notification Actions
send_alert --to <agent> --message "<text>"
send_email --to <email> --subject "<subject>" --body "<body>"
send_slack --channel <#channel> --message "<text>"

# Session Actions
stop_session --session <id> --reason "<text>"
log_event --type <type> --message "<text>"

# Web Actions
call_webhook --url <url> --payload <json>
http_post --url <url> --data <json>
http_get --url <url>

# Conditional Actions
if_<condition> --then <action> --else <action>

# Multiple Actions (chain)
action1 && action2 && action3
```

#### Trigger Examples

```bash
# 1. Auto-create review tasks
agentflow trigger create \
  --name "auto-review-creation" \
  --on "task.status_changed_to:ready_review" \
  --action "
    create_review_task \
      --title 'Review task #{task.id}' \
      --parent_task {task.id} \
      --for-supervisor
  "

# 2. Alert on probation
agentflow trigger create \
  --name "probation-alert" \
  --on "agent.trust_dropped_below:30" \
  --action "
    send_alert \
      --to {agent.supervisor} \
      --message '⚠️ Agent {agent.name} trust dropped to {agent.trust_score}. Status: PROBATION'
  "

# 3. Auto-assign P0 tasks to most available agent
agentflow trigger create \
  --name "p0-auto-assign" \
  --on "task.created_with_priority:P0" \
  --action "
    reassign_task \
      --task {task.id} \
      --to {project.most_available_agent}
  "

# 4. Daily standup reminder
agentflow trigger create \
  --name "daily-standup-reminder" \
  --on "schedule.every_day_at:09:00" \
  --action "
    send_agent_message \
      --to all_agents \
      --message 'Good morning! Time for daily standup. Run: agentflow agent standup {agent.id}'
  "

# 5. Auto-stop idle sessions
agentflow trigger create \
  --name "session-timeout" \
  --on "session.idle_for:4h" \
  --action "
    stop_session \
      --session {session.id} \
      --reason 'Session idle for 4 hours, automatically stopped'
  "

# 6. Unread message reminder
agentflow trigger create \
  --name "unread-reminder" \
  --on "message.unread_for:2h" \
  --action "
    send_alert \
      --to {message.to_agent} \
      --message '⚠️ You have an unread message from {message.from_agent} for 2 hours'
  "

# 7. Auto-reward task completion
agentflow trigger create \
  --name "task-completion-reward" \
  --on "task.completed" \
  --action "
    adjust_trust_score \
      --agent {task.assigned_agent} \
      --change +{task.priority_reward}
  "
# P0 = +5, P1 = +3, P2 = +2, P3 = +1

# 8. P0 bug immediate alert
agentflow trigger create \
  --name "critical-bug-alert" \
  --on "task.created" \
  --if "task.priority == P0 AND task.type == bug" \
  --action "
    send_alert \
      --to all_managers \
      --message '🔴 CRITICAL BUG: {task.title}
                 Assigned to: {task.assigned_agent}
                 Link: agentflow task view {task.id}'
  "

# 9. Weekly summary email
agentflow trigger create \
  --name "weekly-summary" \
  --on "schedule.every_week_on:Friday at 17:00" \
  --action "
    send_email \
      --to team@company.com \
      --subject 'Weekly Summary - {project.name}' \
      --body 'Tasks completed: {project.tasks_completed_this_week}
               Agents worked: {project.active_agents}
               Trust scores: {project.agent_trust_averages}'
  "

# 10. Create follow-up task on completion
agentflow trigger create \
  --name "auto-documentation" \
  --on "task.completed" \
  --if "task.tags contains 'api'" \
  --action "
    create_task \
      --title 'Update API docs for {task.title}' \
      --type documentation \
      --priority P2 \
      --assign-to {task.assigned_agent} \
      --template 'api-documentation'
  "
```

#### Conditional Triggers

```bash
# Trigger with single condition
agentflow trigger create \
  --name "p0-only" \
  --on "task.created" \
  --if "task.priority == P0" \
  --action "send_alert --to manager --message 'P0 task created'"

# Trigger with multiple conditions
agentflow trigger create \
  --name "high-priority-bug" \
  --on "task.created" \
  --if "task.priority == P0 AND task.type == bug" \
  --action "send_alert --to all_managers"

# Trigger with OR condition
agentflow trigger create \
  --name "urgent-task" \
  --on "task.created" \
  --if "task.priority == P0 OR task.type == bug" \
  --action "assign_to_most_available_agent"

# Trigger with complex condition
agentflow trigger create \
  --name "smart-assignment" \
  --on "task.created" \
  --if "task.priority == P0" \
  --then "assign_to_most_senior_agent" \
  --else "assign_to_most_available_agent"

# Trigger with negation
agentflow trigger create \
  --name "non-trivial-task" \
  --on "task.created" \
  --if "task.estimate_hours > 1" \
  --action "create_subtask_checklist"
```

#### Managing Triggers

```bash
# List all triggers
agentflow trigger list

# Output:
# Active Triggers (8):
# ┌────────────────────────────────────────────────────────────────┐
# │ Name                    │ Event                    │ Fired   │
# ├────────────────────────────────────────────────────────────────┤
# │ auto-review-creation   │ task.status_changed_to │ 23      │
# │ probation-alert        │ agent.trust_dropped     │ 2       │
# │ p0-auto-assign         │ task.created_with_prior  │ 8       │
# │ daily-standup          │ schedule.every_day_at    │ 15      │
# │ session-timeout        │ session.idle_for         │ 5       │
# │ unread-reminder        │ message.unread_for       │ 12      │
# │ task-completion-reward │ task.completed           │ 45      │
# │ critical-bug-alert     │ task.created (if)       │ 3       │
# └────────────────────────────────────────────────────────────────┘

# View trigger details
agentflow trigger view auto-review-creation

# Output:
# 🔧 Trigger: auto-review-creation
# ─────────────────────────────────────
# Status: Active
# Created: 2025-01-15
#
# Event:
#   Type: task.status_changed_to
#   Value: ready_review
#
# Condition:
#   None (fires on all matching events)
#
# Action:
#   Type: create_review_task
#   Parameters:
#     • for-supervisor: true
#     • parent_task: {task.id}
#
# Statistics:
#   Times fired: 23
#   Success: 23 (100%)
#   Failed: 0 (0%)
#   Last fired: 2 hours ago
#
# Execution History:
#   2025-01-21 14:32 - Task #123 → Created review #124 ✅
#   2025-01-21 15:10 - Task #125 → Created review #126 ✅
#   2025-01-21 16:45 - Task #127 → Created review #128 ✅

# Disable a trigger
agentflow trigger disable auto-review-creation

# Enable a trigger
agentflow trigger enable auto-review-creation

# Delete a trigger
agentflow trigger delete auto-review-creation

# View execution history
agentflow trigger history auto-review-creation --limit 20

# Test a trigger (dry-run)
agentflow trigger test auto-review-creation --with-task 123

# Output:
# 🧪 Testing trigger: auto-review-creation
#
# Simulating event: task.status_changed_to:ready_review
# Test data: Task #123
#
# Would execute:
#   create_review_task \
#     --title 'Review task #123' \
#     --parent_task 123 \
#     --for-supervisor (agent-lead-001)
#
# Result:
#   ✅ Would create task #129
#   ✅ Would assign to agent-lead-001
#   ✅ Would link to parent task #123
#
# Dry-run complete - no changes made
```

#### Trigger Variables

In trigger actions, you can use variables from the event:

```bash
# Task variables
{task.id}              # Task ID
{task.title}           # Task title
{task.description}     # Task description
{task.type}            # Task type
{task.priority}        # Task priority
{task.status}          # Task status
{task.assigned_agent}  # Assigned agent ID
{task.assigned_agent.name}  # Agent name
{task.project}         # Project ID
{task.project.name}    # Project name
{task.created_at}      # Creation timestamp
{task.estimate_hours}  # Estimated hours
{task.actual_hours}    # Actual hours

# Agent variables
{agent.id}             # Agent ID
{agent.name}           # Agent name
{agent.code}           # Agent code
{agent.role}           # Role
{agent.trust_score}    # Trust score
{agent.status}         # Status
{agent.supervisor}     # Supervisor agent ID

# Message variables
{message.id}           # Message ID
{message.from_agent}   # Sender agent ID
{message.to_agent}     # Receiver agent ID
{message.content}      # Message content
{message.type}         # Message type
{message.priority}     # Message priority

# Session variables
{session.id}           # Session ID
{session.agent}        # Agent ID
{session.duration}     # Session duration
{session.started_at}   # Start time

# Project variables
{project.id}           # Project ID
{project.name}         # Project name
{project.most_available_agent}  # Agent with most capacity
{project.tasks_completed_this_week}
{project.active_agents}

# Timestamp variables
{timestamp}            # Current timestamp
{date}                 # Current date
{time}                 # Current time
```

### Data Model

```python
class Trigger(BaseModel):
    id: str
    name: str  # "auto-review-creation"
    description: Optional[str] = None
    status: Literal["active", "disabled", "deleted"]

    # Event
    event_type: str  # "task.status_changed_to"
    event_value: Optional[str] = None  # "ready_review"

    # Condition
    condition: Optional[str] = None  # "task.priority == P0 AND task.type == bug"
    then_action: Optional[str] = None  # For if-then-else
    else_action: Optional[str] = None

    # Action
    action_type: str  # "create_review_task"
    action_parameters: Dict[str, Any]

    # Metadata
    created_at: datetime
    created_by: str  # Agent ID or "system"
    times_fired: int = 0
    last_fired_at: Optional[datetime] = None

class TriggerExecution(BaseModel):
    id: str
    trigger_id: str
    triggered_at: datetime

    # Event data
    event_type: str
    event_data: Dict[str, Any]

    # Execution result
    status: Literal["success", "failed", "partial"]
    action_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    # Timing
    execution_duration_ms: int
```

### CLI Commands

```bash
# Creating triggers
agentflow trigger create --name <name> --on <event> --action <action>
agentflow trigger create --name <name> --on <event> --if <condition> --then <action> --else <action>

# Managing triggers
agentflow trigger list
agentflow trigger view <name>
agentflow trigger enable <name>
agentflow trigger disable <name>
agentflow trigger delete <name>

# Testing
agentflow trigger test <name> --with-task <task-id>
agentflow trigger history <name> --limit <20>

# Import/Export
agentflow trigger export --file triggers.json
agentflow trigger import --file triggers.json
```

---

## Feature 14: Scheduled Tasks (Recurring Tasks)

### Overview

Create tasks that automatically recur on a schedule (daily, weekly, monthly, cron expressions). Perfect for repetitive work like backups, maintenance, reports, and reviews.

### Why It Matters

- **Never Forget**: Recurring tasks are created automatically
- **Consistency**: Same task created at the same interval
- **Predictable**: Team knows when recurring tasks will appear
- **Flexible**: Supports simple (daily) and complex (cron) schedules

### How It Works

#### Creating a Scheduled Task

```bash
# Simple daily task
agentflow scheduled-task create \
  --name "daily-database-backup" \
  --title "Daily database backup" \
  --description "Perform full database backup and verify integrity" \
  --schedule "every day at 02:00" \
  --estimate 1h \
  --assign-to agent-ops-001 \
  --project infrastructure

# Output:
# ✅ Scheduled task created
#    Name: daily-database-backup
#    Schedule: Every day at 02:00
#    Next run: 2025-01-22 02:00 (in 6 hours)
#    Assigned to: agent-ops-001
#    Project: infrastructure
#
# Template:
#   Title: Daily database backup
#   Estimate: 1h
#
# Next occurrence: Tomorrow 2:00 AM
# Will create task: #150 (estimated)

# Weekly task
agentflow scheduled-task create \
  --name "weekly-retrospective" \
  --title "Weekly team retrospective" \
  --description "Review completed work, discuss improvements, plan next week" \
  --schedule "every Friday at 16:00" \
  --estimate 1h \
  --assign-to agent-pm-001 \
  --project website-redesign

# Monthly task
agentflow scheduled-task create \
  --name "monthly-billing-report" \
  --title "Monthly billing and cost report" \
  --schedule "every month on 1st at 09:00" \
  --estimate 2h \
  --assign-to agent-finance-001 \
  --project billing
```

#### Schedule Formats

```bash
# Every X duration
--schedule "every 5 minutes"
--schedule "every 1 hour"
--schedule "every 6 hours"
--schedule "every 1 day"
--schedule "every 1 week"
--schedule "every 1 month"

# Daily at specific time
--schedule "every day at 02:00"
--schedule "daily at 09:00"

# Weekly
--schedule "every Monday at 09:00"
--schedule "every week on Monday at 09:00"
--schedule "every Monday,Friday at 10:00"
--schedule "every weekday at 09:00"  # Monday-Friday

# Monthly
--schedule "every month on 1st at 09:00"
--schedule "every month on 15th at 10:00"
--schedule "monthly on last day at 17:00"

# Cron expressions
--schedule "0 9 * * 1-5"     # 9am Monday-Friday
--schedule "0 2 * * 1"       # 2am every Monday
--schedule "*/30 * * * *"     # Every 30 minutes
--schedule "0 0 12 * *"      # Noon on 12th of every month

# Complex schedules
--schedule "every week on Monday,Wednesday,Friday at 10:00"
--schedule "every month on 1st and 15th at 09:00"
--schedule "every day at 09:00,17:00"  # Twice daily
```

#### Listing Scheduled Tasks

```bash
# List all scheduled tasks
agentflow scheduled-task list

# Output:
# Scheduled Tasks (6):
# ┌──────────────────────────────────────────────────────────────────┐
# │ Name              │ Schedule            │ Next Run          │ Agen│
# ├──────────────────────────────────────────────────────────────────┤
# │ daily-backup      │ Every day 02:00     │ Jan 22, 02:00      │ ops │
# │ weekly-retro      │ Every Fri 16:00     │ Jan 24, 16:00      │ PM  │
# │ daily-sec-scan    │ Every day 03:00     │ Jan 22, 03:00      │ sec │
# │ monthly-billing   │ 1st of month 09:00  │ Feb 1, 09:00       │ fin │
# │ weekly-deploy     │ Every Mon 10:00     │ Jan 27, 10:00      │ dev │
# │ daily-standup     │ Every weekday 09:00 │ Jan 22, 09:00      │ all │
# └──────────────────────────────────────────────────────────────────┘

# Filter by status
agentflow scheduled-task list --status active

# Filter by project
agentflow scheduled-task list --project infrastructure

# Filter by assignee
agentflow scheduled-task list --assign-to agent-ops-001
```

#### Scheduled Task Details

```bash
# View scheduled task details
agentflow scheduled-task view daily-backup

# Output:
# 📅 Scheduled Task: daily-backup
# ─────────────────────────────────────
# Status: Active
# Created: 2025-01-15
#
# Schedule:
#   Pattern: Every day at 02:00
#   Next run: Jan 22, 2025 at 02:00
#   Time until: 6 hours
#
# Task Template:
#   Title: Daily database backup
#   Description: Perform full database backup and verify integrity
#   Type: maintenance
#   Priority: P2
#   Estimate: 1h
#   Tags: backup,database,daily
#
# Assignment:
#   Agent: agent-ops-001 (Ops Agent)
#   Project: infrastructure
#
# History:
#   Total runs: 20
#   Successful: 19 (95%)
#   Failed: 1 (5%)
#   Last run: Jan 21, 2025 at 02:00 ✅
#   Last failure: Jan 10, 2025 (DB connection timeout)
#
# Next Task:
#   Will create: Task #150
#   Estimated ID: #150
#   Due: Jan 22, 2025 at 06:00 (4h after creation)
```

#### Execution History

```bash
# View execution history
agentflow scheduled-task history daily-backup --limit 10

# Output:
# Execution History - daily-backup
# ─────────────────────────────────────────
#
# 2025-01-21 02:00 - Task #145
#   Status: ✅ Completed
#   Duration: 58 minutes
#   Assigned to: agent-ops-001
#   Actual time: 0h 58m (vs 1h estimate)
#
# 2025-01-20 02:00 - Task #138
#   Status: ✅ Completed
#   Duration: 1h 2m
#   Assigned to: agent-ops-001
#
# 2025-01-19 02:00 - Task #131
#   Status: ✅ Completed
#   Duration: 55 minutes
#   Assigned to: agent-ops-001
#
# 2025-01-18 02:00 - Task #124
#   Status: ✅ Completed
#   Duration: 1h 5m
#   Assigned to: agent-ops-001
#
# 2025-01-17 02:00 - Task #117
#   Status: ❌ Failed
#   Error: Database connection timeout
#   Assigned to: agent-ops-001
#   Retry: Created replacement task at 03:00
#
# ... (more history)

# Statistics
agentflow scheduled-task stats daily-backup

# Output:
# 📊 Statistics - daily-backup
# ─────────────────────────────────────
# Total runs: 45
# Success rate: 93% (42/45)
#
# Duration:
#   Average: 59 minutes
#   Min: 45 minutes
#   Max: 1h 15m
#
# Completion:
#   On time: 40 (89%)
#   Late: 5 (11%)
#
# Recurring issues:
#   • DB connection timeout (2 times)
#   • Insufficient disk space (1 time)
```

#### Managing Scheduled Tasks

```bash
# Pause a scheduled task (stop creating tasks)
agentflow scheduled-task pause daily-backup

# Output:
# ⏸️  Scheduled task paused
#    Name: daily-backup
#    Next run: SKIPPED (until resumed)
#    Tasks created so far: 20

# Resume a paused task
agentflow scheduled-task resume daily-backup

# Output:
# ▶️  Scheduled task resumed
#    Name: daily-backup
#    Next run: Jan 23, 2025 at 02:00 (next occurrence)

# Update schedule
agentflow scheduled-task update daily-backup \
  --schedule "every day at 03:00"

# Update assignment
agentflow scheduled-task update daily-backup \
  --assign-to agent-ops-002

# Update task template
agentflow scheduled-task update daily-backup \
  --title "Daily database backup with verification" \
  --estimate 1.5h \
  --priority P1

# Delete scheduled task
agentflow scheduled-task delete daily-backup

# Output:
# ⚠️  Delete scheduled task: daily-backup?
#    This will stop future task creation.
#    Past tasks created will remain.
#
#    Total tasks created: 20
#    Next run would have been: Jan 22, 2025
#
# Confirm? [y/N]
```

#### Advanced Features

```bash
# Scheduled task with dependencies
agentflow scheduled-task create \
  --name "weekly-deployment" \
  --title "Weekly production deployment" \
  --schedule "every Friday at 15:00" \
  --depends-on "daily-security-scan completed" \
  --assign-to agent-devops-001

# Only creates if daily-security-scan completed this week

# Scheduled task with condition
agentflow scheduled-task create \
  --name "conditional-cleanup" \
  --title "Cleanup old logs if disk > 80%" \
  --schedule "every day at 04:00" \
  --if "disk_usage > 80%" \
  --assign-to agent-ops-001

# Only creates task if condition is true

# Scheduled task with subtasks template
agentflow scheduled-task create \
  --name "weekly-security-audit" \
  --title "Weekly security audit" \
  --schedule "every Monday at 09:00" \
  --subtasks "Check access logs,Review user permissions,Scan for vulnerabilities" \
  --assign-to agent-sec-001

# Creates task with pre-defined subtasks

# Scheduled task with variable content
agentflow scheduled-task create \
  --name "weekly-sprint-report" \
  --title "Sprint {week_number} Report - Week of {monday_date}" \
  --schedule "every Friday at 17:00" \
  --assign-to agent-pm-001

# Variables automatically filled:
# {week_number} = 3, 4, 5, ...
# {monday_date} = Jan 20, Jan 27, ...
```

#### Scheduled Task Groups

```bash
# Create a group of related scheduled tasks
agentflow scheduled-task create-group \
  --name "daily-maintenance" \
  --tasks "
    daily-database-backup
    daily-log-cleanup
    daily-security-scan
    daily-health-check
  "

# Pause entire group
agentflow scheduled-task pause-group daily-maintenance

# Resume entire group
agentflow scheduled-task resume-group daily-maintenance

# View group status
agentflow scheduled-task view-group daily-maintenance
```

### Data Model

```python
class ScheduledTask(BaseModel):
    id: str
    name: str  # "daily-backup"
    status: Literal["active", "paused", "deleted"]

    # Schedule
    schedule_type: Literal["interval", "cron", "simple"]
    schedule_expression: str  # "every day at 02:00" or "0 2 * * *"
    timezone: str = "UTC"

    # Task template
    task_template: "TaskTemplate"

    # Assignment
    assign_to_agent_id: str
    project_id: str

    # Dependencies (optional)
    depends_on_scheduled_tasks: List[str] = []
    depends_on_condition: Optional[str] = None

    # Metadata
    created_at: datetime
    created_by: str
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None

    # Stats
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_runs == 0:
            return 1.0
        return self.successful_runs / self.total_runs

class ScheduledTaskExecution(BaseModel):
    id: str
    scheduled_task_id: str
    scheduled_at: datetime  # When it was supposed to run
    executed_at: datetime  # When it actually ran

    # Created task
    task_id: Optional[str] = None
    task_status: Optional[Literal["completed", "failed", "cancelled"]] = None

    # Result
    status: Literal["success", "failed", "skipped", "cancelled"]
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
```

### CLI Commands

```bash
# Creating
agentflow scheduled-task create --name <name> --schedule <expr> --assign-to <agent>
agentflow scheduled-task create-group --name <group> --tasks <task1,task2>

# Managing
agentflow scheduled-task list
agentflow scheduled-task view <name>
agentflow scheduled-task pause <name>
agentflow scheduled-task resume <name>
agentflow scheduled-task update <name> --schedule <expr>
agentflow scheduled-task delete <name>

# History
agentflow scheduled-task history <name> --limit <20>
agentflow scheduled-task stats <name>

# Groups
agentflow scheduled-task pause-group <group>
agentflow scheduled-task resume-group <group>
agentflow scheduled-task view-group <group>
```

---

## Feature 15: Webhooks & External Integrations

### Overview

Send HTTP requests to external URLs when events occur, enabling integrations with Slack, email, CI/CD systems, monitoring tools, and any service with a webhook API.

### Why It Matters

- **Notifications**: Send alerts to Slack, Discord, email, etc.
- **CI/CD Integration**: Trigger deployments when tasks complete
- **Monitoring**: Push metrics to monitoring systems
- **Custom Integrations**: Connect with any HTTP API
- **Real-time Updates**: Keep external systems in sync

### How It Works

#### Creating Your First Webhook

```bash
# Slack notification when task is completed
agentflow webhook create \
  --name "slack-task-complete" \
  --url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --event "task.completed" \
  --payload '{
    "text": "✅ Task completed: {task.title}",
    "channel": "#dev-updates",
    "username": "AgentFlow",
    "icon_emoji": ":white_check_mark:"
  }'

# Output:
# ✅ Webhook created
#    Name: slack-task-complete
#    Event: task.completed
#    URL: https://hooks.slack.com/...
#    Method: POST
#
# Test webhook: agentflow webhook test slack-task-complete

# When a task is completed, AgentFlow will POST to Slack:
# {
#   "text": "✅ Task completed: Implement user authentication",
#   "channel": "#dev-updates",
#   "username": "AgentFlow",
#   "icon_emoji": ":white_check_mark:"
# }
```

#### Webhook Components

1. **URL**: The endpoint to call
2. **Event**: When to trigger (task.completed, agent.trust_dropped, etc.)
3. **Method**: HTTP method (GET, POST, PUT, PATCH)
4. **Headers**: Custom headers (Authorization, Content-Type, etc.)
5. **Payload**: Data to send (can use variables)
6. **Conditions**: Optional filters (only fire if priority == P0, etc.)

#### Available Events

```bash
# Same events as Triggers (see Feature 13)
task.completed
task.status_changed_to:<status>
agent.trust_dropped_below:<score>
session.idle_for:<duration>
schedule.every_day_at:<HH:MM>
# ... and all other trigger events
```

#### Payload Variables

```bash
# Use curly braces for variables
{task.id}
{task.title}
{task.assigned_agent.name}
{agent.trust_score}
{timestamp}
# ... all trigger variables supported

# JSON payload example
{
  "task_id": "{task.id}",
  "title": "{task.title}",
  "agent": "{task.assigned_agent.name}",
  "completed_at": "{timestamp}"
}

# Form-encoded payload
task_id={task.id}&title={task.title}&agent={task.assigned_agent.name}
```

#### Webhook Examples

```bash
# 1. Slack notification for completed tasks
agentflow webhook create \
  --name "slack-complete" \
  --url "https://hooks.slack.com/services/XXX/YYY/ZZZ" \
  --event "task.completed" \
  --payload '{
    "text": "✅ {task.assigned_agent.name} completed: {task.title}",
    "channel": "#dev-updates",
    "attachments": [{
      "color": "good",
      "fields": [
        {"title": "Task", "value": "{task.title}", "short": true},
        {"title": "Agent", "value": "{task.assigned_agent.name}", "short": true},
        {"title": "Duration", "value": "{task.actual_hours}h", "short": true},
        {"title": "Link", "value": "https://app.agentflow.io/tasks/{task.id}", "short": false}
      ]
    }]
  }'

# 2. Email alert for P0 tasks
agentflow webhook create \
  --name "email-p0-alert" \
  --url "https://api.sendgrid.com/v3/mail/send" \
  --event "task.created" \
  --if "task.priority == P0" \
  --headers "Authorization: Bearer SENDGRID_API_KEY" \
  --payload '{
    "personalizations": [{
      "to": [{"email": "team@company.com"}],
      "subject": "🔴 P0 Task Created: {task.title}"
    }],
    "from": {"email": "agentflow@company.com"},
    "content": [{
      "type": "text/plain",
      "value": "A critical P0 task has been created:\n\nTitle: {task.title}\nType: {task.type}\nAssigned to: {task.assigned_agent.name}\nPriority: {task.priority}\n\nView: https://app.agentflow.io/tasks/{task.id}"
    }]
  }'

# 3. CI/CD trigger for deployments
agentflow webhook create \
  --name "deploy-on-complete" \
  --url "https://ci.example.com/api/trigger" \
  --event "task.completed" \
  --if "task.tags contains 'deployment'" \
  --headers "Authorization: Bearer CI_TOKEN" \
  --payload '{
    "ref": "main",
    "task_id": "{task.id}",
    "agent": "{task.assigned_agent}",
    "project": "{task.project.name}"
  }'

# 4. Metrics export to monitoring system
agentflow webhook create \
  --name "metrics-export" \
  --url "https://monitoring.example.com/api/metrics" \
  --event "task.completed" \
  --headers "X-API-Key: MONITORING_API_KEY" \
  --payload '{
    "metric": "task_completion_time",
    "value": {task.actual_hours},
    "unit": "hours",
    "tags": {
      "agent": "{task.assigned_agent.code}",
      "task_type": "{task.type}",
      "priority": "{task.priority}",
      "project": "{task.project.name}"
    },
    "timestamp": "{timestamp}"
  }'

# 5. Discord notification
agentflow webhook create \
  --name "discord-complete" \
  --url "https://discord.com/api/webhooks/XXX/YYY" \
  --event "task.completed" \
  --payload '{
    "content": "✅ Task completed by {task.assigned_agent.name}: {task.title}",
    "embeds": [{
      "title": "{task.title}",
      "description": "{task.description}",
      "color": 65280,
      "fields": [
        {"name": "Agent", "value": "{task.assigned_agent.name}", "inline": true},
        {"name": "Duration", "value": "{task.actual_hours}h", "inline": true},
        {"name": "Priority", "value": "{task.priority}", "inline": true}
      ]
    }]
  }'

# 6. GitHub issue creation
agentflow webhook create \
  --name "github-issue-on-bug" \
  --url "https://api.github.com/repos/org/repo/issues" \
  --event "task.created" \
  --if "task.type == bug" \
  --headers "Authorization: token GITHUB_TOKEN" \
  --payload '{
    "title": "{task.title}",
    "body": "{task.description}\n\nCreated by AgentFlow agent: {task.assigned_agent.name}\nPriority: {task.priority}\nLink: https://app.agentflow.io/tasks/{task.id}",
    "labels": ["bug", "agentflow"],
    "assignee": "github-username"
  }'

# 7. PagerDuty alert for critical issues
agentflow webhook create \
  --name "pagerduty-critical" \
  --url "https://events.pagerduty.com/v2/enqueue" \
  --event "task.created" \
  --if "task.priority == P0 AND task.type == bug" \
  --headers "Content-Type: application/json" \
  --payload '{
    "routing_key": "PAGERDUTY_INTEGRATION_KEY",
    "event_action": "trigger",
    "payload": {
      "summary": "Critical bug: {task.title}",
      "severity": "critical",
      "source": "agentflow",
      "custom_details": {
        "task_id": "{task.id}",
        "agent": "{task.assigned_agent.name}",
        "link": "https://app.agentflow.io/tasks/{task.id}"
      }
    }
  }'

# 8. Microsoft Teams notification
agentflow webhook create \
  --name "teams-complete" \
  --url "https://outlook.office.com/webhook/XXX" \
  --event "task.completed" \
  --payload '{
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "summary": "Task completed",
    "themeColor": "0078D7",
    "title": "✅ Task Completed",
    "sections": [{
      "activityTitle": "{task.assigned_agent.name} completed a task",
      "activitySubtitle": "{task.title}",
      "facts": [
        {"name": "Duration", "value": "{task.actual_hours}h"},
        {"name": "Priority", "value": "{task.priority}"}
      ]
    }]
  }'
```

#### Managing Webhooks

```bash
# List all webhooks
agentflow webhook list

# Output:
# Webhooks (8):
# ┌─────────────────────────────────────────────────────────────────────┐
# │ Name              │ Event           │ URL                 │ Fired  │
# ├─────────────────────────────────────────────────────────────────────┤
# │ slack-complete    │ task.completed  │ hooks.slack.com/.. │ 23     │
# │ email-p0-alert    │ task.created    │ api.sendgrid.com/  │ 8      │
# │ deploy-on-complete│ task.completed  │ ci.example.com/..  │ 3      │
# │ metrics-export    │ task.completed  │ monitoring.com/..  │ 45     │
# │ discord-complete  │ task.completed  │ discord.com/..     │ 23     │
# │ github-issue      │ task.created    │ api.github.com/..  │ 12     │
# │ pagerduty-critical│ task.created    │ pagerduty.com/..   │ 2      │
# │ teams-complete    │ task.completed  │ outlook.office.com/│ 23     │
# └─────────────────────────────────────────────────────────────────────┘

# View webhook details
agentflow webhook view slack-complete

# Output:
# 📡 Webhook: slack-complete
# ─────────────────────────────────────
# Status: Active
# Created: 2025-01-15
#
# Event:
#   Type: task.completed
#   Condition: None (fires on all task completions)
#
# Request:
#   URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
#   Method: POST
#   Headers: Content-Type: application/json
#
# Payload Template:
#   {
#     "text": "✅ {task.assigned_agent.name} completed: {task.title}",
#     "channel": "#dev-updates",
#     "attachments": [...]
#   }
#
# Statistics:
#   Times fired: 23
#   Success: 22 (96%)
#   Failed: 1 (4%)
#   Avg. response time: 245ms
#   Last fired: 2 hours ago ✅
#
# Recent executions:
#   2025-01-21 14:32 - Task #123 completed - 200 OK ✅
#   2025-01-21 13:15 - Task #122 completed - 200 OK ✅
#   2025-01-21 11:45 - Task #121 completed - 503 Service Unavailable ❌

# Test a webhook (dry run)
agentflow webhook test slack-complete --with-task 123

# Output:
# 🧪 Testing webhook: slack-complete
#
# Sending test payload to: https://hooks.slack.com/...
# Test task: #123
#
# Payload:
#   {
#     "text": "✅ Jean completed: Implement user authentication",
#     "channel": "#dev-updates",
#     "attachments": [...]
#   }
#
# Response:
#   Status: 200 OK
#   Body: ok
#
# ✅ Webhook test successful
```

#### Webhook Security

```bash
# Webhook with signature (HMAC)
agentflow webhook create \
  --name "secure-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --secret "WEBHOOK_SECRET_123" \
  --signature-method "hmac-sha256" \
  --payload '{"task_id": "{task.id}"}'

# Adds X-Signature header with HMAC hash
# Recipient can verify authenticity

# Webhook with API key in header
agentflow webhook create \
  --name "authenticated-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --headers "X-API-Key: YOUR_API_KEY,Authorization: Bearer TOKEN"

# Webhook with basic auth
agentflow webhook create \
  --name "basic-auth-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --basic-auth "username:password"
```

#### Webhook Reliability

```bash
# Retry on failure
agentflow webhook create \
  --name "reliable-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --retry 3 \
  --retry-delay 60 \
  --retry-backoff exponential

# Retry behavior:
# - First attempt: Immediate
# - Retry 1: After 60 seconds
# - Retry 2: After 120 seconds (exponential backoff)
# - Retry 3: After 240 seconds
# - After 3 failed attempts: Mark as failed

# Timeout configuration
agentflow webhook create \
  --name "timeout-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --timeout 30

# Timeout after 30 seconds

# Async webhook (don't block)
agentflow webhook create \
  --name "async-webhook" \
  --url "https://api.example.com/webhook" \
  --event "task.completed" \
  --async

# Fires asynchronously, doesn't block task completion
```

#### Managing Webhooks

```bash
# Disable webhook
agentflow webhook disable slack-complete

# Enable webhook
agentflow webhook enable slack-complete

# Update webhook
agentflow webhook update slack-complete \
  --url "https://new-url.com/webhook" \
  --payload '{"new": "payload"}'

# Delete webhook
agentflow webhook delete slack-complete

# View execution history
agentflow webhook history slack-complete --limit 20

# Export webhooks
agentflow webhook export --file webhooks.json

# Import webhooks
agentflow webhook import --file webhooks.json
```

### Data Model

```python
class Webhook(BaseModel):
    id: str
    name: str  # "slack-task-complete"
    description: Optional[str] = None
    status: Literal["active", "disabled", "deleted"]

    # Event
    event_type: str  # "task.completed"
    event_condition: Optional[str] = None  # "task.priority == P0"

    # Request
    url: str
    method: Literal["GET", "POST", "PUT", "PATCH"] = "POST"
    headers: Dict[str, str] = {}
    payload_template: str  # JSON string with variables
    content_type: str = "application/json"

    # Security
    secret: Optional[str] = None  # For HMAC signature
    signature_method: Optional[Literal["hmac-sha256", "hmac-sha1"]] = None
    basic_auth: Optional[str] = None  # "username:password"

    # Reliability
    retry_count: int = 0  # Number of retries on failure
    retry_delay_seconds: int = 60
    timeout_seconds: int = 30
    is_async: bool = False  # Fire asynchronously

    # Metadata
    created_at: datetime
    created_by: str
    times_fired: int = 0
    last_fired_at: Optional[datetime] = None

class WebhookExecution(BaseModel):
    id: str
    webhook_id: str
    triggered_at: datetime

    # Event data
    event_type: str
    event_data: Dict[str, Any]

    # Request
    url: str
    method: str
    payload_sent: str
    headers_sent: Dict[str, str]

    # Response
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    response_time_ms: Optional[int] = None

    # Result
    status: Literal["success", "failed", "timeout"]
    error_message: Optional[str] = None
    retry_attempt: int = 0  # 0 = first attempt, 1 = first retry, etc.
```

### CLI Commands

```bash
# Creating
agentflow webhook create --name <name> --url <url> --event <event> --payload <json>
agentflow webhook create --name <name> --url <url> --event <event> --if <condition> --payload <json>

# Managing
agentflow webhook list
agentflow webhook view <name>
agentflow webhook enable <name>
agentflow webhook disable <name>
agentflow webhook update <name> --url <url>
agentflow webhook delete <name>

# Testing
agentflow webhook test <name> --with-task <task-id>

# History
agentflow webhook history <name> --limit <20>

# Security
agentflow webhook set-secret <name> --secret <secret>
agentflow webhook set-auth <name> --basic-auth <user:pass>

# Import/Export
agentflow webhook export --file webhooks.json
agentflow webhook import --file webhooks.json
```

---

## Implementation Notes

### Dependencies

- **Feature 13 (Triggers)**: Requires events system (tasks, agents, sessions)
- **Feature 14 (Scheduled Tasks)**: Requires tasks, schedule parser
- **Feature 15 (Webhooks)**: Requires events system, HTTP client

### Priority

1. **Feature 13 (Triggers)** - High value, powerful automation
2. **Feature 15 (Webhooks)** - Medium value, integrations
3. **Feature 14 (Scheduled Tasks)** - Medium value, recurring work

### Phasing

- **Phase 1**: Basic triggers (task events, simple actions)
- **Phase 2**: Webhooks (HTTP POST, basic integrations)
- **Phase 3**: Scheduled tasks (cron parsing, recurrence)

### Integration Points

- **With Tasks**: Triggers on task events, auto-create review tasks
- **With Agents**: Trust score monitoring, probation alerts
- **With Sessions**: Auto-stop idle sessions, timeout warnings
- **With External Systems**: Webhooks to Slack, email, CI/CD, monitoring

---

**Document Version**: 1.0
**Created**: 2025-01-21
**Status**: 🎨 Design proposal - Ready for review
