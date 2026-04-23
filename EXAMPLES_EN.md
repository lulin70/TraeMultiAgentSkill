# DevSquad Usage Examples

> Last verified: 2026-04-18 with DevSquad V3.3

## Quick Start

```bash
# Auto-match roles based on task description
python3 scripts/cli.py dispatch -t "Design a user authentication system"

# Specify roles explicitly
python3 scripts/cli.py dispatch -t "Design a user authentication system" -r architect pm tester

# Dry-run (simulate without execution)
python3 scripts/cli.py dispatch -t "Design a user authentication system" --dry-run
```

## Basic Examples

### Example 1: Architecture Design

```bash
python3 scripts/cli.py dispatch \
    -t "Design a microservices e-commerce backend" \
    -r architect
```

The dispatcher creates an architect Worker that analyzes the task and produces a structured architecture report covering system design, tech stack, API definitions, and deployment strategy.

### Example 2: Multi-Role Collaboration

```bash
python3 scripts/cli.py dispatch \
    -t "Build a real-time chat feature" \
    -r architect pm coder tester
```

Four roles work in parallel via the Coordinator:
- **Architect**: designs the WebSocket architecture
- **PM**: defines user stories and acceptance criteria
- **Coder**: outlines implementation approach
- **Tester**: identifies edge cases and test strategy

Results are collected on the Scratchpad, conflicts resolved via ConsensusEngine, and a unified report is returned.

### Example 3: Consensus Mode

```bash
python3 scripts/cli.py dispatch \
    -t "Choose database for analytics platform" \
    -r architect data \
    --mode consensus
```

Consensus mode forces a vote when roles disagree. Each role casts a weighted vote, veto power is respected, and human escalation is available for deadlocks.

### Example 4: Quick Dispatch (Structured Output)

```bash
python3 scripts/cli.py dispatch \
    -t "Analyze API security" \
    --quick \
    --format structured \
    --action-items
```

Quick dispatch produces a concise structured report with prioritized action items (High/Medium/Low).

### Example 5: JSON Output for Automation

```bash
python3 scripts/cli.py dispatch \
    -t "Review codebase for performance issues" \
    -r optimizer reviewer \
    --format json
```

JSON output is machine-readable, suitable for CI/CD pipelines or further processing.

## System Commands

```bash
# List all available roles
python3 scripts/cli.py roles

# Show system status
python3 scripts/cli.py status

# List roles in JSON format
python3 scripts/cli.py roles --format json
```

## Python API Examples

### Basic Dispatch

```python
from scripts.collaboration.dispatcher import MultiAgentDispatcher

disp = MultiAgentDispatcher()
result = disp.dispatch(
    "Design a user authentication system",
    roles=["architect", "pm", "tester"],
    mode="auto",
)

print(result.summary)
print(result.to_markdown())
disp.shutdown()
```

### Quick Dispatch

```python
from scripts.collaboration.dispatcher import MultiAgentDispatcher

disp = MultiAgentDispatcher()
result = disp.quick_dispatch(
    "Analyze API security",
    output_format="detailed",
    include_action_items=True,
)

print(result.summary)
disp.shutdown()
```

## Role Reference

| Role | ID | Aliases | Status |
|------|----|---------|--------|
| Architect | `architect` | `arch` | ✅ Core |
| Product Manager | `product-manager` | `pm` | ✅ Core |
| Coder | `solo-coder` | `coder`, `dev` | ✅ Core |
| Tester | `tester` | `test`, `qa` | ✅ Core |
| UI Designer | `ui-designer` | `ui` | ✅ Core |
| DevOps | `devops` | — | 🔜 Planned |
| Security | `security` | — | 🔜 Planned |
| Data Engineer | `data` | — | 🔜 Planned |
| Reviewer | `reviewer` | — | 🔜 Planned |
| Optimizer | `optimizer` | — | 🔜 Planned |

## CLI Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--task`, `-t` | string | required | Task description |
| `--roles`, `-r` | list | auto | Roles to involve |
| `--mode`, `-m` | enum | auto | Execution mode: auto/parallel/sequential/consensus |
| `--format`, `-f` | enum | markdown | Output: markdown/json/compact/structured/detailed |
| `--dry-run` | flag | false | Simulate without execution |
| `--quick`, `-q` | flag | false | Use quick_dispatch (3 formats) |
| `--action-items` | flag | false | Include H/M/L action items |
| `--timing` | flag | false | Include timing info |
| `--persist-dir` | string | auto | Custom scratchpad directory |
| `--no-warmup` | flag | false | Disable startup warmup |
| `--no-compression` | flag | false | Disable context compression |
| `--skip-permission` | flag | false | Skip permission checks |
| `--no-memory` | flag | false | Disable memory bridge |
| `--no-skillify` | flag | false | Disable skill learning |
| `--permission-level` | enum | DEFAULT | PLAN/DEFAULT/AUTO/BYPASS |

## MCP Server (for OpenClaw / Cursor)

```bash
# Install MCP package (optional)
pip install mcp

# Start in stdio mode
python3 scripts/mcp_server.py

# Start in SSE mode
python3 scripts/mcp_server.py --port 8080
```

6 tools exposed: `multiagent_dispatch`, `multiagent_quick`, `multiagent_roles`, `multiagent_status`, `multiagent_analyze`, `multiagent_shutdown`.
