# DevSquad — Multi-Agent Software Development Team

<p align="center">
  <strong>Assemble an AI-powered software development squad on demand.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green" />
  <img alt="Tests" src="https://img.shields.io/badge/Tests-825%2B%20passing-brightgreen" />
  <img alt="Version" src="https://img.shields.io/badge/V3.3-2026--04--17-orange" />
</p>

---

## What is DevSquad?

DevSquad transforms a **single AI coding assistant into a specialized multi-role development team**. Instead of one AI handling your entire task, it automatically dispatches to the right combination of expert roles — architect, product manager, coder, tester, security reviewer, and more — then orchestrates their parallel collaboration through a shared workspace, resolves conflicts via consensus voting, and delivers a unified structured report.

**Think of it as assembling a virtual dev team on demand, powered by AI agents that collaborate like real engineers.**

```
You: "Design a microservices e-commerce backend"
         │
         ▼
┌─────────────────┐
│  Intent Analysis  ──→ Auto-match: architect + devops + security
└────────┬────────┘
         ▼
┌──────────┬──────────┬──────────┐
│ Architect │  DevOps   │ Security │
│(Design)   │(Infra)   │(Threat)  │
└────┬──────┴────┬─────┴────┬────┘
     └────────────┼───────────┘
                  ▼
      ┌──────────────────┐
      │    Scratchpad     │ ← Shared blackboard
      │ (Real-time sync) │
      └────────┬─────────┘
               ▼
      ┌──────────────────┐
      │ Consensus Engine  │ ← Weighted vote + veto
      └────────┬─────────┘
               ▼
      ┌──────────────────┐
      │ Structured Report │ ← Findings + Action Items (H/M/L)
      └──────────────────┘
```

## 📚 Documentation

**New to DevSquad?** Start here: [Documentation Index](docs/INDEX.md)

- 📖 [Installation Guide](INSTALL.md) - Setup and configuration
- 💡 [Usage Examples](EXAMPLES.md) - Real-world scenarios
- 🏗️ [Architecture](docs/architecture/ARCHITECTURE.md) - System design
- 📊 [Project Status](docs/PROJECT_STATUS.md) - Current state and roadmap
- 🎯 [Optimization Plan](docs/OPTIMIZATION_PLAN_KARPATHY.md) - Improvement roadmap

## Quick Start

### Prerequisites

- **Python 3.9+** (pure Python, no compiled dependencies)
- **OS**: macOS / Linux / **Windows 10+**
- No external dependencies required (all integrations use graceful degradation)

See [**INSTALL.md**](INSTALL.md) for detailed setup instructions including Windows.

### 3 Ways to Use

**Method 1: CLI (Recommended)**

```bash
git clone https://github.com/lulin70/DevSquad.git
cd DevSquad

# Mock mode (default) — no API key needed
python3 scripts/cli.py dispatch -t "Design user authentication system"

# Real AI output — set environment variables first
export OPENAI_API_KEY="sk-..."
python3 scripts/cli.py dispatch -t "Design user authentication system" --backend openai

# Specify roles (short IDs: arch/pm/test/coder/ui/infra/sec)
python3 scripts/cli.py dispatch -t "Design auth system" -r arch sec --backend openai

python3 scripts/cli.py status
python3 scripts/cli.py roles
```

**Method 2: Python API**

```python
import sys
sys.path.insert(0, '/path/to/DevSquad')
from scripts.collaboration.dispatcher import MultiAgentDispatcher

disp = MultiAgentDispatcher()
result = disp.dispatch("Design REST API for user management")
print(result.to_markdown())
disp.shutdown()
```

**Method 3: Quick Dispatch (3 output formats)**

```python
from scripts.collaboration.dispatcher import MultiAgentDispatcher

disp = MultiAgentDispatcher()

# Structured report (default table format)
result = disp.quick_dispatch(task, output_format="structured")

# Compact (one-line per role)
result = disp.quick_dispatch(task, output_format="compact")

# Detailed (full findings + action items)
result = disp.quick_dispatch(task, output_format="detailed",
                              include_action_items=True)

disp.shutdown()
```

## 7 Core Roles

| Role | ID | Aliases | Best For |
|------|----|---------|----------|
| Architect | `architect` | `arch` | System design, tech stack, performance/security/data architecture |
| Product Manager | `product-manager` | `pm` | Requirements, user stories, acceptance criteria |
| Security Expert | `security` | `sec` | Threat modeling, vulnerability audit, compliance |
| Tester | `tester` | `test`, `qa` | Test strategy, quality assurance, edge cases |
| Coder | `solo-coder` | `coder`, `dev` | Implementation, code review, performance optimization |
| DevOps | `devops` | `infra` | CI/CD, containerization, monitoring, infrastructure |
| UI Designer | `ui-designer` | `ui` | UX flow, interaction design, accessibility |

**Auto-match**: If no roles specified, the dispatcher automatically matches based on task intent.

## 19 Core Modules

| Module | Purpose |
|--------|---------|
| **MultiAgentDispatcher** | Unified entry point — one call does everything |
| **Coordinator** | Global orchestration: decompose → assign → collect → resolve |
| **Scratchpad** | Shared blackboard for inter-worker real-time communication |
| **Worker** | Role executor — independent instance per role |
| **ConsensusEngine** | Weighted voting + veto power + human escalation |
| **BatchScheduler** | Parallel/sequential hybrid with auto safety detection |
| **ContextCompressor** | 4-level compression prevents context overflow |
| **PermissionGuard** | 4-level safety gate (PLAN → DEFAULT → AUTO → BYPASS) |
| **Skillifier** | Learns from successful patterns, auto-generates new skills |
| **WarmupManager** | 3-layer startup preloading (cold-start < 300ms) |
| **MemoryBridge** | Cross-session memory (7 types, TF-IDF, forgetting curve) |
| **MCEAdapter** | Memory Classification Engine integration (v0.4, tenant-aware) |
| **WorkBuddyClawSource** | External knowledge bridge (INDEX search, AI news feed) |
| **PromptAssembler** | Dynamic prompt construction (3 variants × 5 styles) |
| **PromptVariantGenerator** | Closed-loop A/B testing for prompt optimization |
| **TestQualityGuard** | Automated test quality audit (API validation, coverage) |
| **LLMCache** ⭐ NEW | Intelligent caching (60-80% cost reduction, 90% faster on hits) |
| **LLMRetryManager** ⭐ NEW | Exponential backoff retry + circuit breaker + multi-backend fallback |
| **PerformanceMonitor** ⭐ NEW | Real-time performance tracking with P95/P99 metrics |

## Cross-Platform Compatibility

DevSquad works natively across multiple AI coding environments:

| Platform | Integration Method | Status |
|----------|-------------------|--------|
| **Trae IDE** | `skill-manifest.yaml` native skill | ✅ Primary |
| **Claude Code** | `CLAUDE.md` + `.claude/skills/` custom skill | ✅ Supported |
| **OpenClaw** | MCP Server (`scripts/mcp_server.py`, 6 tools) | ✅ Supported |
| **Terminal / Any IDE** | CLI (`scripts/cli.py`) or Python import | ✅ Universal |

### MCP Server (for OpenClaw / Cursor / any MCP client)

```bash
pip install mcp          # optional
python3 scripts/mcp_server.py              # stdio mode
python3 scripts/mcp_server.py --port 8080  # SSE mode
```

Exposes 6 tools: `multiagent_dispatch`, `multiagent_quick`, `multiagent_roles`,
`multiagent_status`, `multiagent_analyze`, `multiagent_shutdown`.

## Performance Optimization Modules ⭐ NEW

DevSquad now includes three powerful optimization modules to enhance LLM-based applications:

### 1. LLM Cache (`scripts/collaboration/llm_cache.py`)

Intelligent two-tier caching system that dramatically reduces API costs and improves response times.

**Features:**
- Memory + Disk dual-layer caching
- TTL-based expiration (default: 24 hours)
- LRU eviction policy
- Hit rate statistics and reporting

**Benefits:**
- 60-80% reduction in API costs
- 90% faster response on cache hits
- Offline testing support

**Quick Start:**
```python
from scripts.collaboration import get_llm_cache

cache = get_llm_cache()
response = cache.get(prompt, backend="openai", model="gpt-4")
if not response:
    response = your_api_call(prompt)
    cache.set(prompt, response, backend="openai", model="gpt-4")
```

### 2. LLM Retry Manager (`scripts/collaboration/llm_retry.py`)

Robust error handling with exponential backoff, circuit breaker, and multi-backend fallback.

**Features:**
- Exponential backoff retry (configurable delays)
- Circuit breaker pattern (prevents cascade failures)
- Multi-backend fallback (OpenAI → Anthropic → Zhipu)
- Rate limit detection and handling

**Benefits:**
- 99%+ success rate (with retries)
- Automatic fault tolerance
- Graceful degradation

**Quick Start:**
```python
from scripts.collaboration import retry_with_fallback

@retry_with_fallback(max_retries=3, fallback_backends=["openai", "anthropic"])
def call_llm(prompt: str, backend: str = "openai"):
    return your_api_call(prompt, backend)
```

### 3. Performance Monitor (`scripts/collaboration/performance_monitor.py`)

Real-time performance tracking with detailed metrics and bottleneck detection.

**Features:**
- Automatic execution time tracking
- CPU and memory usage monitoring
- P95/P99 latency percentiles
- Bottleneck detection and reporting

**Benefits:**
- Real-time performance visibility
- Data-driven optimization
- Historical trend analysis

**Quick Start:**
```python
from scripts.collaboration import monitor_performance, get_monitor

@monitor_performance("my_function")
def my_function():
    # Your code here
    pass

# Get statistics
monitor = get_monitor()
stats = monitor.get_stats("my_function")
print(f"Avg: {stats['avg_duration_ms']:.1f}ms, P95: {stats['p95_duration_ms']:.1f}ms")
```

### Integration Example

Use all three modules together for maximum benefit:

```python
from scripts.collaboration import (
    get_llm_cache,
    retry_with_fallback,
    monitor_performance
)

@monitor_performance("optimized_llm_call")
@retry_with_fallback(max_retries=3, fallback_backends=["openai", "anthropic"])
def optimized_llm_call(prompt: str, backend: str = "openai"):
    cache = get_llm_cache()
    
    # Try cache first
    cached = cache.get(prompt, backend, "gpt-4")
    if cached:
        return cached
    
    # Call API with retry/fallback
    response = your_api_call(prompt, backend)
    
    # Save to cache
    cache.set(prompt, response, backend, "gpt-4")
    return response
```

**Documentation:**
- 📖 [Optimization Guide](docs/OPTIMIZATION_GUIDE.md) - Complete usage guide
- 📊 [Review & Scoring](docs/OPTIMIZATION_REVIEW_SCORE.md) - Performance evaluation (85/100)
- 💡 [Integration Example](scripts/collaboration/integration_example.py) - Full demo

## External Integrations

| Component | Status | Fallback |
|-----------|--------|----------|
| **MCE v0.4** (Memory Classification Engine) | Optional tenant/permission support | Graceful degrade if unavailable |
| **WorkBuddy Claw** | Read-only bridge to external knowledge base | Skip if path not found |

All integrations are optional — DevSquad works fully standalone.

## Running Tests

```bash
cd /path/to/DevSquad

# Core collaboration tests
python3 -m pytest scripts/collaboration/ -v
# Expected: ~825+ test cases, all passing

# Quick status check
python3 scripts/cli.py status
# Expected: {"name": "DevSquad", "status": "ready", ...}

# Dry-run verification
python3 scripts/cli.py dispatch -t "test" --dry-run
```

## Project Structure

```
DevSquad/
├── scripts/
│   ├── cli.py                    # Primary CLI entry point
│   ├── mcp_server.py             # MCP server (OpenClaw/Cursor)
│   ├── trae_agent.py             # Legacy wrapper (/dss command)
│   ├── trae_agent_dispatch_v2.py # Core dispatcher (legacy)
│   └── collaboration/            # ★ 16 core modules
│       ├── dispatcher.py         # MultiAgentDispatcher
│       ├── coordinator.py        # Global orchestrator
│       ├── scratchpad.py         # Shared blackboard
│       ├── worker.py             # Role executor
│       ├── consensus.py          # Weighted voting + veto
│       ├── memory_bridge.py      # Cross-session memory
│       ├── mce_adapter.py        # MCE v0.4 adapter
│       └── *_test.py             # Test suites (~825+ cases)
├── SKILL.md                      # English skill manual
├── SKILL-CN.md                   # Chinese skill manual
├── SKILL-JP.md                   # Japanese skill manual
├── CLAUDE.md                     # Claude Code project instructions
├── INSTALL.md                    # Installation guide (Unix + Windows)
├── CHANGELOG.md                  # Complete version history
└── docs/                         # Architecture specs, plans
```

## Philosophy

> **"One AI is a tool. Ten AI collaborators are a team."**

Software development is inherently multi-disciplinary. No single perspective can match the quality of a well-coordinated team with diverse expertise. DevSquad makes that team available on demand, in seconds, for any software task.

## Version History

| Date | Version | Highlights |
|------|---------|-----------|
| 2026-04-24 | **V3.3.0** | Real LLM backend (OpenAI/Anthropic), env-var-only API keys, 7 core roles (security+devops promoted), TaskDefinition.role_prompt fix, verified real AI output |
| 2026-04-17 | V3.2 | E2E Demo, MCE Adapter, Dispatcher UX, Delivery Workflow Iron Rule |
| 2026-04-16 | V3.1 | Prompt Optimization System (A/B variant testing) |
| 2026-04-16 | V3.0 | Complete redesign — Coordinator/Worker/Scratchpad architecture |
| Mar 2026 | V2.x | Dual-layer context, Vibe Coding, MCE integration, code map visualization |

## License

MIT License — see [LICENSE](LICENSE) for details.

## Links

| Link | URL |
|------|-----|
| **GitHub (This Repo)** | https://github.com/lulin70/DevSquad |
| **Original / Upstream** | https://github.com/weiransoft/TraeMultiAgentSkill |
| **Installation** | See [INSTALL.md](INSTALL.md) |
| **Skill Manual** | [SKILL.md](SKILL.md) / [SKILL-CN.md](SKILL-CN.md) / [SKILL-JP.md](SKILL-JP.md) |
| **Examples** | [EXAMPLES.md](EXAMPLES.md) |
| **Chinese Readme** | [README-CN.md](README-CN.md) |
| **Japanese Readme** | [README-JP.md](README-JP.md) |
