# Trae Multi-Agent Skill

🎭 Dynamically dispatches to appropriate agent roles (Architect, Product Manager, Test Expert, Solo Coder, UI Designer) based on task type. Supports multi-agent collaboration, consensus mechanism, complete project lifecycle management, specification-driven development, code map generation, project understanding, and UI design capabilities. Supports Chinese-English bilingual.

## Project Source

This project is a fork from [https://github.com/weiransoft/TraeMultiAgentSkill/](https://github.com/weiransoft/TraeMultiAgentSkill/) and optimized using the concepts from [https://github.com/2025Emma/vibe-coding-cn](https://github.com/2025Emma/vibe-coding-cn).

### Vibe Coding Optimization Concepts

- **Planning-Driven Development**: Emphasizes planning before execution
- **Context Fixation**: Ensures context consistency during development
- **AI Pair Programming**: Leverages AI capabilities to enhance development efficiency
- **Prompt Evolution System**: Self-improving generation of Alpha (generator) and Omega (optimizer) prompts
- **Memory Bank**: Centralized knowledge storage for project context management
- **Multi-Model Collaboration**: Uses multiple AI models to handle different tasks
- **Modular Design**: Breaks down projects into manageable modules with clear interfaces
- **Multimodal Support**: Integrates text, image, and voice inputs
- **Context Management**: Maintains consistent project context across interactions
- **Planning Engine**: Generates detailed implementation plans for tasks

## 🎉 March 2026 Latest Updates

- ✅ **Vibe Coding Integration (v2.4)** - Integration of planning engine, prompt evolution system, enhanced context manager, module manager, multimodal processor
- ✅ **Multi-Role Code Walkthrough (v2.3)** - Architect, PM, Solo Coder, UI Designer, Test Expert analyze code from multiple perspectives, generate aligned unified code map
- ✅ **Code Map Workspace Support (v2.3)** - Supports single workspace with multiple projects, clear project identification
- ✅ **3D Code Map Visualization (v2.3)** - Three.js interactive visualization with flowing animations and theme switching
- ✅ **Task Visualization Page (v2.3)** - Real-time display of role task status, progress, dependencies, handoffs, collaboration graph
- ✅ **Doc-Code Consistency Check (v2.3)** - New document and code consistency checklist in code review report
- ✅ **Long-Running Agent Support (v2.2)** - Based on Anthropic's "Effective Harnesses for Long-Running Agents", supports Checkpoint, Handoff, and TaskList
- ✅ **AI Semantic Role Matching (v2.1)** - Uses LLM to understand task deep semantics, provides explainable matching results and confidence scores
- ✅ **AI Assistant Deep Integration (v2.1)** - Integrated LLM capabilities, supports code review, knowledge Q&A, text analysis
- ✅ **Smart Cache and Fallback Strategy (v2.1)** - Performance optimization, auto-fallback to keyword matching when AI unavailable
- ✅ **UI Designer Role** - Creates unique, production-grade UI interfaces, avoids generic AI "slop" aesthetics
- ✅ **Agent Loop Fix** - Fixed is_all_tasks_completed method, added continuous no-progress detection
- ✅ **Specification-Driven Development** - Complete specification toolchain, unified document management, multi-agent consensus
- ✅ **Code Map Generation** - Auto-generates project code structure map, supports JSON and Markdown, identifies core components
- ✅ **Project Understanding** - Quickly reads project docs and code, generates role-specific understanding documents
- ✅ **8-Stage Standard Workflow** - Requirements → Architecture → UI Design → Test Design → Task Breakdown → Development → Test → Release
- ✅ **Cross-Role Design Review** - PRD review, architecture review, UI review, test plan review, dev plan review
- ✅ **Document-Based Task Breakdown** - All roles break down tasks based on documents, ensuring document-driven development

## 🌍 Multi-Language Support

This skill supports automatic Chinese-English language switching:

- **Auto-detection**: Automatically switches response language based on user language
- **Full Coverage**: All output content supports multiple languages
- **Smart Matching**: Code comments automatically match existing language
- **Flexible Switching**: Supports language switching during conversation

📄 Detailed documentation: [MULTILINGUAL_GUIDE.md](MULTILINGUAL_GUIDE.md)

## 📖 Table of Contents

- [Features](#-features-功能特性)
- [Quick Start](#-quick-start-快速开始)
- [Agent Roles](#-agent-roles-角色介绍)
- [Usage Methods](#-usage-methods-使用方法)
- [Installation](#-installation-安装说明)
- [Configuration](#-configuration-配置说明)
- [Example Scenarios](#-example-scenarios-示例场景)
- [Technical Architecture](#-technical-architecture-技术架构)
- [Contribution Guide](#-contribution-guide-贡献指南)
- [FAQ](#-faq-常见问题)
- [License](#-license-许可证)

## ✨ Features

### Vibe Coding Optimization (v2.4 New)

1. **Planning Engine** 📋
   - Generates detailed project implementation plans
   - Supports plan saving and management
   - Task status tracking and updates
   - **Deep Analysis Capability**: Integrates 5-Why analysis framework to identify root causes
   - **Analysis Case Library**: Stores and indexes historical analysis results
   - Core file: `scripts/vibe_coding/planning_engine.py`

2. **Prompt Evolution System** 🧠
   - Self-improving generation of Alpha (generator) and Omega (optimizer) prompts
   - Prompt effectiveness analysis and scoring
   - History and template management
   - Core file: `scripts/vibe_coding/prompt_evolution.py`

3. **Enhanced Context Manager** 🔄
   - Semantic memory and multi-model support
   - Global and task context management
   - Model coordination and allocation
   - Core file: `scripts/vibe_coding/enhanced_context_manager.py`

4. **Module Manager** 📦
   - Modular design tools
   - Module creation and management
   - Dependency analysis and interface definition
   - Core file: `scripts/vibe_coding/module_manager.py`

5. **Multimodal Processor** 🎭
   - Supports text, image, and voice inputs
   - Text-to-code conversion
   - Processing history management
   - Core file: `scripts/vibe_coding/multimodal_processor.py`

6. **Automated Verification Mechanism** 🧪
   - Rule-based test case generator
   - Automated test execution framework
   - Test coverage report generation system
   - Supports normal, boundary, and exception scenario test cases
   - Core file: `scripts/tests/automated_test_generator.py`

7. **Professional Domain Knowledge Base** 📚
   - Lightweight knowledge management system
   - Keyword-based knowledge search functionality
   - Supports knowledge addition, update, and deletion
   - Relevance ranking
   - Core file: `scripts/knowledge_base_manager.py`

8. **User Experience Optimization** 💬
   - Improved user feedback collection mechanism
   - Rule-based feedback analysis
   - Feedback classification, sentiment analysis, priority calculation
   - Interface optimization recording and management
   - Core file: `scripts/user_experience_manager.py`

9. **Integration Script** 🔗
   - Integrates all optimization modules into TraeMultiAgentSkill
   - Unified integration interface
   - Supports complete task scheduling flow
   - Core file: `scripts/integration_script.py`

### Core Capabilities

1. **Intelligent Role Dispatching** 🎯
   - Automatically identifies required roles based on task description
   - Based on keyword matching and position weight algorithm
   - Confidence evaluation and best role selection

2. **Multi-Agent Collaboration** 🤝
   - Organizes multiple agents to complete complex tasks together
   - Consensus mechanism ensures decision quality
   - Context sharing between agents

3. **Context Awareness** 🧠
   - Selects roles based on project phase
   - Intelligent inheritance of historical context
   - Automatic task chain association

4. **Complete Project Lifecycle** 📊
   - 8-stage project flow support
   - Full process from requirements to deployment
   - Quality gates and review mechanisms

5. **Specification-Driven Development** 📋
   - Complete specification toolchain (spec_tools.py)
   - Project Constitution (CONSTITUTION.md) development
   - Project Specification (SPEC.md) automatic generation
   - Specification Analysis Report (SPEC_ANALYSIS.md)
   - Specification consistency check and validation
   - Multi-agent consensus for specification development

6. **Code Map Generation** 🗺️
   - Automatically generates project code structure map (code_map_generator_v2.py)
   - Supports JSON and Markdown format output
   - Identifies core components and module dependencies
   - Visual project structure documentation
   - Technology stack analysis and statistics
   - **Multi-Project Workspace Support** (v2.3) - Auto-detects project workspace
   - **Multi-Role Code Walkthrough** (v2.3) - Architect, PM, Solo Coder, UI Designer, Test Expert analyze from multiple perspectives
   - **Document Alignment Mechanism** (v2.3) - Aligns multi-role analysis results, generates unified code map
   - **3D Code Map Visualization** (v2.3) - Three.js interactive visualization with flowing animations, theme switching
   - **Task Visualization Page** (v2.3) - Role task status, progress, dependencies, handoff process
   - Core files: `scripts/code_map_generator_v2.py`, `scripts/multi_role_code_walkthrough.py`, `docs/code-map-visualizer.html`, `docs/task-visualizer.html`

7. **Project Understanding** 📚
   - Quickly reads project documents and code (project_understanding.py)
   - Generates role-specific understanding documents
   - Provides project overview and technology stack analysis
   - Serves as work initialization context
   - Role-specific insights and recommendations

8. **8-Stage Standard Workflow** 📊
   - Stage 1: Requirements Analysis (Product Manager)
   - Stage 2: Architecture Design (Architect)
   - Stage 3: UI Design (UI Designer)
   - Stage 4: Test Design (Test Expert)
   - Stage 5: Task Breakdown (Solo Coder)
   - Stage 6: Development Implementation (Solo Coder)
   - Stage 7: Test Verification (Test Expert)
   - Stage 8: Release Review (Multi-Agent)

9. **Cross-Platform Compatibility** 🌍
   - Supports Windows, Mac, and Linux
   - Unified path handling and character encoding
   - Cross-platform script execution

### Agent Prompt System

Each role is equipped with complete work rules and quality standards:

- ✅ **Systematic Thinking Rules** - Ensures design completeness
- ✅ **Deep Thinking Rules** - 5-Why analysis to find root causes
- ✅ **Zero Tolerance Checklist** - Prohibits mock, placeholder, simplification
- ✅ **Verification-Driven Design** - Complete acceptance criteria
- ✅ **Completeness Check** - Multi-dimensional checklists
- ✅ **Self-Testing Rules** - 3-layer test validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Trae IDE
- Basic command line knowledge

### Basic Usage

Use directly in Trae without additional commands:

```
# Architecture design task
Design system architecture: including module division, technology selection, deployment plan

# Product requirements definition
Define product requirements: ad blocking functionality, clear acceptance criteria required

# Test strategy formulation
Develop test strategy: covering normal, exceptional, boundary, and performance scenarios

# Feature development
Implement ad blocking functionality: complete code with unit tests
```

The agent will automatically identify the task type and dispatch the corresponding role!

### Advanced Usage

Use the dispatch script for more fine-grained control:

```bash
# Auto-identify role
python3 scripts/trae_agent_dispatch.py \
    --task "Design system architecture"

# Specify role
python3 scripts/trae_agent_dispatch.py \
    --task "Implement functionality" \
    --agent solo_coder

# Multi-agent consensus
python3 scripts/trae_agent_dispatch.py \
    --task "Start new project: secure browser ad blocking functionality" \
    --consensus true

# Complete project lifecycle
python3 scripts/trae_agent_dispatch.py \
    --task "Secure browser ad blocking functionality" \
    --project-full-lifecycle

# Specification-driven development
python3 scripts/spec_tools.py init
python3 scripts/spec_tools.py analyze
python3 scripts/spec_tools.py update --spec-file SPEC.md

# Code map generation
python3 scripts/code_map_generator_v2.py /path/to/project --workspace /workspace

# Multi-role code walkthrough
python3 scripts/multi_role_code_walkthrough.py /path/to/project --workspace /workspace

# Project understanding
python3 scripts/project_understanding.py /path/to/project
```

## 🎭 Agent Roles

### 1. Architect

**Responsibilities**: Design systematic, forward-looking, implementable, and verifiable architecture

**Core Principles**:
- ✅ Systematic Thinking - Answer 4 key questions before designing
- ✅ 5-Why Analysis - Continuous questioning to find root causes
- ✅ Zero Tolerance Checklist - Prohibits mock, hardcoding, simplification
- ✅ Verification-Driven Design - Complete acceptance criteria

**Typical Outputs**:
- System architecture diagram (Mermaid)
- Module responsibility list
- Interface definition (input/output/exceptions)
- Data model design
- Deployment architecture description

**Trigger Keywords**: architecture, design, selection, review, performance, bottleneck, module, interface, deployment

### 2. Product Manager

**Responsibilities**: Define products with clear user value, explicit requirements, implementable and verifiable

**Core Principles**:
- ✅ Three-Layer Requirements Mining - Surface → Real → Essential
- ✅ SMART Acceptance Criteria - Specific, Measurable, Achievable
- ✅ Competitive Analysis Rules - At least 5 competitive products comparison

**Typical Outputs**:
- Product Requirements Document (PRD)
- User story map
- Acceptance criteria (SMART)
- Competitive analysis report

**Trigger Keywords**: requirements, PRD, user story, competition, market, research, acceptance, UAT, experience

### 3. Test Expert

**Responsibilities**: Ensure comprehensive, in-depth, automated, and quantifiable quality assurance

**Core Principles**:
- ✅ Test Pyramid - 70% Unit + 20% Integration + 10% E2E
- ✅ Orthogonal Analysis - 5 categories of scenarios fully covered
- ✅ Real Device Testing - Real environment verification

**Typical Outputs**:
- Test strategy document
- Test cases (normal/exception/boundary/performance/security)
- Automated test scripts
- Quality assessment report

**Trigger Keywords**: test, quality, acceptance, automation, performance test, defect, review, gate

### 4. UI Designer

**Responsibilities**: Create unique, production-grade UI interfaces with high design quality, avoiding generic AI "slop" aesthetics

**Core Principles**:
- ✅ Design Thinking Rules - Answer 4 key questions before designing
- ✅ UI Design Aesthetics Guide - Fonts, colors, animations, layout
- ✅ Zero Tolerance Checklist - Prohibits generic fonts, outdated colors, AI slop
- ✅ Verification-Driven Design - Complete acceptance criteria
- ✅ Completeness Check - Multi-dimensional checklists

**Typical Outputs**:
- Design philosophy document
- Style guide
- High-fidelity prototypes
- UI design document

**Trigger Keywords**: UI design, interface design, frontend design, visual design, UI/UX, UI prototype, interface beautification, UI optimization, UI refactoring

### 5. Solo Coder

**Responsibilities**: Write complete, high-quality, maintainable, and testable code

**Core Principles**:
- ✅ Zero Tolerance Checklist - 10 absolute prohibitions
- ✅ Completeness Check - 4-dimensional checklists
- ✅ Self-Testing Rules - 3-layer test validation

**Typical Outputs**:
- Complete feature code
- Unit tests (coverage > 80%)
- Integration tests
- Technical documentation

**Trigger Keywords**: implementation, development, code, fix, optimization, refactoring, unit test, documentation

## 💡 Usage Methods

### Scenario 1: Project Startup

```bash
# Complete project startup (multi-agent consensus)
python3 scripts/trae_agent_dispatch.py \
    --task "Start new project: secure browser ad blocking functionality" \
    --consensus true \
    --priority high

# Automatic organization:
#   1. Product Manager - Requirements definition
#   2. Architect - Architecture design
#   3. Test Expert - Test strategy
#   4. Solo Coder - Development plan
```

### Scenario 2: Feature Development

```bash
# Single role dispatch (fast development)
python3 scripts/trae_agent_dispatch.py \
    --task "Implement ad blocking core module" \
    --agent solo_coder \
    --context "Based on architecture design document v2.0"

# Automatic includes:
#   - Architecture design document as context
#   - Completeness check checklist
#   - Self-testing requirements
```

### Scenario 3: Code Review

```bash
# Multi-agent code review
python3 scripts/trae_agent_dispatch.py \
    --task "Review ad blocking core module" \
    --code-review \
    --files src/adblock/ tests/

# Participating roles:
#   - Architect (architecture compliance)
#   - Test Expert (test coverage)
#   - Solo Coder (code quality)
```

### Scenario 4: Emergency Bug Fix

```bash
# Emergency fix (fast track)
python3 scripts/trae_agent_dispatch.py \
    --task "Emergency fix: production environment crash" \
    --priority critical \
    --fast-track

# Automatic handling:
#   - Skip regular process
#   - Directly dispatch senior developer
#   - Real-time progress synchronization
```

### Scenario 5: Specification-Driven Development

```bash
# Initialize specification environment
python3 scripts/spec_tools.py init

# Analyze specifications
python3 scripts/spec_tools.py analyze

# Update specification documents
python3 scripts/spec_tools.py update --spec-file SPEC.md

# Specification-driven project startup
python3 scripts/trae_agent_dispatch.py \
    --task "Start specification-driven project: e-commerce system" \
    --spec-driven

# Automatic execution:
#   1. Initialize specification environment
#   2. Multi-agent consensus: Formulate project constitution
#   3. Product Manager: Write requirements specification
#   4. Architect: Write technical specification
#   5. Specification review (multi-agent consensus)
#   6. Task breakdown based on specifications
#   7. Each role executes tasks
#   8. Specification verification and quality review
```

### Scenario 6: Code Map & Code Walkthrough

```bash
# Generate code map (with workspace support)
python3 scripts/code_map_generator_v2.py /path/to/project --workspace /workspace

# Output:
# - Markdown format: <project>-CODE_MAP.md

# True multi-role collaborative code walkthrough (using Trae Agent dispatch)
python3 scripts/multi_role_collaborative_analyzer.py /path/to/project --workspace /workspace

# Output:
# - Unified code map: <project>-ALIGNED-CODE-MAP.md
# - Code review report: <project>-CODE-REVIEW-REPORT.md

# Simplified multi-role code walkthrough
python3 scripts/multi_role_code_walkthrough.py /path/to/project --workspace /workspace

# Generated content includes:
#   - Unified code map: project overview, architecture layers, multi-role analysis results
#   - Review report: review overview, architecture review, code quality assessment
```

### Scenario 7: Project Understanding

```bash
# Generate project understanding documents
python3 scripts/project_understanding.py /path/to/project

# Output:
# - Overall project information: project_understanding.json
# - Architect understanding: architect_understanding.md
# - Product Manager understanding: product_manager_understanding.md
# - Test Expert understanding: test_expert_understanding.md
# - Solo Coder understanding: solo_coder_understanding.md

# Document content includes:
#   - Project overview and technology stack
#   - Code structure analysis
#   - Document and dependency analysis
#   - Role-specific insights and recommendations
```

## 📦 Installation

### Method 1: Global Installation (Recommended)

```bash
# Run installation script
cd /path/to/claw/.trae/skills
./install-global.sh

# Verify installation
ls -lh ~/.trae/skills/trae-multi-agent/

# Restart Trae application
```

### Method 2: Project-Level Installation

Skill is included in project directory, Trae will automatically load:

```
project-directory/.trae/skills/trae-multi-agent/
```

### Method 3: Manual Installation

```bash
# 1. Create skill directory
mkdir -p ~/.trae/skills/trae-multi-agent

# 2. Copy skill files
cp -r /path/to/claw/.trae/skills/trae-multi-agent/* \
      ~/.trae/skills/trae-multi-agent/

# 3. Verify installation
ls -lh ~/.trae/skills/trae-multi-agent/SKILL.md

# 4. Restart Trae
```

### Verify Installation

```bash
# Check skill files
ls -lh ~/.trae/skills/trae-multi-agent/SKILL.md
# Should display: 34K SKILL.md

# Test dispatch script
python3 scripts/trae_agent_dispatch.py --task "Design system architecture"
# Should display: 🎯 Identified as: Architect
```

## ⚙️ Configuration

### Skill Configuration (skills-index.json)

```json
{
  "version": "1.0.0",
  "name": "trae-multi-agent",
  "enabled": true,
  "global": true,
  "autoInvoke": true,
  "roles": {
    "architect": { "priority": 1 },
    "product_manager": { "priority": 2 },
    "test_expert": { "priority": 3 },
    "solo_coder": { "priority": 4 }
  }
}
```

### Role Recognition Algorithm

```python
def analyze_task(task: str):
    """
    Analyze task and identify required roles
    
    Args:
        task: Task description
        
    Returns:
        (Best role, confidence, list of all matched roles)
    """
    scores = {}
    matched_roles = []
    
    # Keyword matching + position weight
    for role, config in ROLES.items():
        score = 0.0
        for keyword in config["keywords"]:
            if keyword in task:
                score += 1.0
        
        # Position weight: higher weight for earlier positions
        words = task.split()
        for i, word in enumerate(words):
            for keyword in config["keywords"]:
                if keyword in word:
                    score += 1.0 / (i + 1)
        
        scores[role] = score
    
    # Select best role
    best_role = max(scores, key=scores.get)
    confidence = min(scores[best_role] / len(keywords), 1.0)
    
    return best_role, confidence, matched_roles
```

### Consensus Trigger Conditions

```python
def _needs_consensus(task, confidence, matched_roles):
    """Determine if multi-agent consensus is needed"""
    
    # 1. Confidence below threshold
    if confidence < 0.6:
        return True
    
    # 2. Involves multiple professional domains
    if len(matched_roles) >= 2:
        return True
    
    # 3. Task description is very long
    if len(task) > 200:
        return True
    
    # 4. Contains explicit consensus request
    if any(kw in task for kw in ["consensus", "review", "discussion"]):
        return True
    
    return False
```

## 📋 New Feature / Feature Change Standard Workflow

### Core Principle: Design First, Document First, Then Develop

**Must Follow Workflow**:

```
Phase 1: Requirements Analysis (Product Manager)
    ↓ Review passed
Phase 2: Architecture Design (Architect)
    ↓ Review passed
Phase 3: Test Design (Test Expert)
    ↓ Review passed
Phase 4: Task Breakdown (Solo Coder)
    ↓
Phase 5: Development Implementation (Solo Coder)
    ↓
Phase 6: Test Verification (Test Expert)
    ↓
Phase 7: Release Review (Multi-Agent)
```

**Absolutely Prohibited**:
❌ Start coding without design phase
❌ Start development without writing or completing documentation
❌ Implement without design review

**Document Dependencies**:
```
PRD Document (Product Manager)
    ↓ [Depends on: PRD review passed]
Architecture Design Document (Architect)
    ↓ [Depends on: Architecture review passed]
Test Plan Document (Test Expert)
    ↓ [Depends on: Test plan review passed]
Development Task List (Developer)
    ↓ [Depends on: Development completed]
Test Report (Test Expert)
    ↓ [Depends on: Test passed]
Release Decision (Multi-Agent)
```

Detailed process description: [SKILL.md](SKILL.md) - New Feature / Feature Change Standard Workflow

## 📚 Example Scenarios

### Example 1: Complete Project Startup

**Input**:
```
Start new project: secure browser ad blocking functionality
- Support blocking malicious ads and phishing websites
- Performance requirement: page load delay < 100ms
- Complete test coverage required
```

**Automatic Process**:
```
🎯 Identified as: Multi-agent consensus task

📋 Phase 1: Requirements Definition (Product Manager)
   - User story map
   - Acceptance criteria (SMART)
   - Competitive analysis

📋 Phase 2: Architecture Design (Architect)
   - System architecture diagram
   - Technology selection
   - Deployment plan

📋 Phase 3: Test Strategy (Test Expert)
   - Test pyramid
   - Automation plan
   - Quality gates

📋 Phase 4: Development Plan (Solo Coder)
   - Task breakdown
   - Time estimation
   - Risk assessment
```

### Example 2: Feature Development

**Input**:
```
Implement ad blocking core module
- Based on architecture design document v2.0
- Use SQLite for rule storage
- Complete unit tests required
```

**Automatic Processing**:
```
🎯 Identified as: Solo Coder task
📊 Confidence: 0.85

✅ Context loaded: Architecture design document v2.0

📋 Development Process:
   1. Requirements understanding confirmation
   2. Technical solution design
   3. Code implementation
      - Core functionality
      - Error handling
      - Logging
   4. Unit tests
      - Coverage > 80%
      - Boundary conditions
      - Exception scenarios
   5. Self-testing verification
```

### Example 3: Architecture Review

**Input**:
```
Review current system architecture
- Evaluate performance bottlenecks
- Identify technical debt
- Propose optimization suggestions
```

**Automatic Processing**:
```
🎯 Identified as: Architect task
📊 Confidence: 0.92

📋 Review Checklist:
   ✓ System boundary clarity
   ✓ Module responsibility singularity
   ✓ Interface definition completeness
   ✓ Exception handling coverage
   ✓ Performance bottleneck analysis
   ✓ Security risk assessment
   ✓ Expansion point reservation
   ✓ Monitoring plan

📋 Output:
   - Review report
   - Issue list
   - Optimization suggestions
   - Priority sorting
```

### Example 4: Vibe Coding Optimization Process

**Input**:
```
Optimize project development process using Vibe Coding
- Generate detailed project plan
- Optimize prompts to improve AI output quality
- Manage project context and module structure
- Process multimodal inputs
```

**Automatic Process**:
```
🎯 Identified as: Vibe Coding optimization task

📋 Stage 1: Planning Generation (Planning Engine)
   - Generate detailed project implementation plan
   - Task breakdown and priority sorting
   - Progress tracking setup

📋 Stage 2: Prompt Optimization (Prompt Evolution System)
   - Alpha generator creates initial prompts
   - Omega optimizer improves prompt quality
   - Effectiveness analysis and scoring

📋 Stage 3: Context Management (Enhanced Context Manager)
   - Initialize global context
   - Assign appropriate models for tasks
   - Inject relevant knowledge and experience

📋 Stage 4: Module Design (Module Manager)
   - Create project module structure
   - Define module dependencies
   - Generate module interface specifications

📋 Stage 5: Multimodal Processing (Multimodal Processor)
   - Process text input conversion to code
   - Analyze processing history and results
   - Generate final code and documentation
```

**Usage Commands**:
```bash
# Run Vibe Coding integration test
python3 scripts/vibe_coding/integration_test.py

# Test Vibe Coding functionality
python3 scripts/vibe_coding/test_vibe_coding.py
```

## 🏗️ Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────┐
│         Trae Multi-Agent Skill          │
├─────────────────────────────────────────┤
│  User Interface Layer (Trae IDE)         │
│  - Natural language input                │
│  - Intelligent response output           │
├─────────────────────────────────────────┤
│  Dispatch Layer (Dispatcher)             │
│  - Task analysis                         │
│  - Role identification                   │
│  - Consensus organization                │
├─────────────────────────────────────────┤
│  Role Layer (Agent Roles)                │
│  - Architect                             │
│  - Product Manager                       │
│  - Test Expert                           │
│  - Solo Coder                            │
├─────────────────────────────────────────┤
│  Vibe Coding Optimization Layer          │
│  - Planning Engine                       │
│  - Prompt Evolution System               │
│  - Enhanced Context Manager              │
│  - Module Manager                        │
│  - Multimodal Processor                  │
├─────────────────────────────────────────┤
│  Execution Layer (Executor)              │
│  - Task execution                        │
│  - Context management                    │
│  - Result verification                   │
└─────────────────────────────────────────┘
```

### Data Flow

```
User Input
  ↓
Task Analysis (Keyword matching + Position weight)
  ↓
Role Identification (Confidence evaluation)
  ↓
Single role task → Direct dispatch
Multi role task → Organize consensus
  ↓
Task Execution (With complete Prompt)
  ↓
Result Verification (Checklist)
  ↓
Output Response
```

### Core Algorithms

#### 1. Role Recognition Algorithm

```python
def analyze_task(task: str) -> Tuple[str, float, List[str]]:
    """
    Analyze task and identify required roles
    
    Algorithm:
    1. Keyword matching
    2. Position weight calculation
    3. Score accumulation
    4. Confidence evaluation
    """
    scores = {}
    matched_roles = []
    
    for role, config in ROLES.items():
        score = 0.0
        matched_keywords = []
        
        # Keyword matching
        for keyword in config["keywords"]:
            if keyword in task:
                score += 1.0
                matched_keywords.append(keyword)
        
        # Position weight
        words = task.split()
        for i, word in enumerate(words):
            for keyword in config["keywords"]:
                if keyword in word:
                    score += 1.0 / (i + 1)
        
        if score > 0:
            matched_roles.append(role)
        
        scores[role] = score
    
    # Select best role
    best_role = max(scores, key=scores.get)
    max_score = scores[best_role]
    
    # Calculate confidence
    confidence = min(max_score / len(ROLES[best_role]["keywords"]), 1.0) \
                 if max_score > 0 else 0.0
    
    return best_role, confidence, matched_roles
```

#### 2. Consensus Decision Algorithm

```python
def organize_consensus(task: str, agents: List[str]) -> Dict:
    """
    Organize multi-agent consensus
    
    Process:
    1. Determine lead role
    2. Collect opinions from each role
    3. Conflict detection
    4. Reach consensus
    5. Generate resolution
    """
    # Determine lead role
    lead_role = determine_lead_role(task)
    
    # Collect opinions
    opinions = {}
    for agent in agents:
        opinion = agent.analyze(task)
        opinions[agent.role] = opinion
    
    # Conflict detection
    conflicts = detect_conflicts(opinions)
    
    # Resolve conflicts
    if conflicts:
        resolved = resolve_conflicts(conflicts, opinions)
    
    # Generate consensus
    consensus = generate_consensus(opinions)
    
    return consensus
```

## 🤝 Contribution Guide

### Development Environment Setup

```bash
# 1. Clone project
git clone https://github.com/your-org/trae-multi-agent.git
cd trae-multi-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests
pytest tests/
```

### Submission Process

1. **Fork project**
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Code Standards

- Follow PEP 8 standard
- Use type annotations
- Write unit tests
- Add comments in English

### Test Requirements

```bash
# Run all tests
pytest tests/ -v

# Test coverage
pytest tests/ --cov=src --cov-report=html

# Coverage requirements
# - Code coverage > 80%
# - Branch coverage > 70%
```

## ❓ FAQ

### Q1: Skill not working?

**A**: Check the following:
1. Skill files are in correct directory
2. File permissions are correct (readable)
3. Restart Trae application
4. Check if skill feature is enabled in Trae settings

### Q2: Role identification inaccurate?

**A**: Try:
1. Use more explicit task description
2. Use `--agent` parameter to manually specify role
3. Use `--consensus true` to organize multi-agent consensus

### Q3: Python3 not found?

**A**: Install Python3:
```bash
brew install python@3.11
```

### Q4: How to update skill?

**A**: Re-run installation script:
```bash
~/.trae/skills/install-global.sh
```

### Q5: How to customize role Prompt?

**A**: Edit role Prompt section in `SKILL.md` file, then restart Trae.

## 📄 License

MIT License

Copyright (c) 2026 Weiransoft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 📞 Contact

- **Project Homepage**: https://github.com/lulin70/TraeMultiAgentSkill
- **Issue Feedback**: https://github.com/lulin70/TraeMultiAgentSkill/issues
- **Original Project**: https://github.com/weiransoft/TraeMultiAgentSkill
- **Vibe Coding Concept**: https://github.com/2025Emma/vibe-coding-cn

## 🙏 Acknowledgments

Thank you to all contributors and users for your support!
