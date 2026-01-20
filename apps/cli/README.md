# AgentFlow CLI - Phase 0

AgentFlow CLI with local JSON storage (Phase 0 prototype).

## Installation

```bash
cd apps/cli
uv sync
```

## Usage

```bash
# Run CLI
uv run agentflow --help

# Authentication
uv run agentflow auth register --email "user@example.com" --password "pass123" --name "John Doe"
uv run agentflow auth login --email "user@example.com" --password "pass123"
uv run agentflow auth status

# Organizations
uv run agentflow org create --name "Acme Corp" --slug "acme-corp"
uv run agentflow org list
uv run agentflow org use acme-corp

# Projects
uv run agentflow project create --name "Website" --slug "website"
uv run agentflow project list
uv run agentflow project use website
```

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/agentflow --cov-report=term-missing
```

## Data Storage

- **Config**: `~/.agentflow/config.yaml`
- **Data**: `~/.agentflow/data.json`
