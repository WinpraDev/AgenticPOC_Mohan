# 🚀 Meta-Agent Implementation Plan

**Target Environment**: MacBook Pro M4, 16GB RAM, LM Studio with MLX-optimized models

---

## 📋 Table of Contents

1. [System Requirements & Optimization](#system-requirements--optimization)
2. [LLM Model Selection](#llm-model-selection)
3. [Architecture Overview](#architecture-overview)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Setup Instructions](#detailed-setup-instructions)
6. [Resource Management](#resource-management)
7. [Testing Strategy](#testing-strategy)
8. [Timeline & Milestones](#timeline--milestones)

---

## 1. System Requirements & Optimization

### **1.1 Hardware Profile**

```
MacBook Pro M4 Specifications:
├─ CPU: Apple M4 (10-core)
├─ GPU: Apple M4 GPU (10-core)
├─ RAM: 16GB Unified Memory
├─ Neural Engine: 16-core
└─ Storage: SSD (assuming 512GB+)

Memory Allocation Strategy (16GB total):
├─ macOS System: ~3GB
├─ LM Studio + Model: ~6-8GB
├─ PostgreSQL: ~1GB
├─ Meta-Agent + Python: ~2GB
├─ Docker (for sandbox): ~2GB
└─ Available: ~2GB buffer

Critical: Close unnecessary applications during operation
```

### **1.2 Software Requirements**

```
Operating System:
├─ macOS Sonoma 14.0+ (recommended for M4)
└─ Ensure Xcode Command Line Tools installed

Core Components:
├─ Python 3.11 or 3.12 (avoid 3.13, compatibility issues)
├─ LM Studio (latest version with MLX support)
├─ PostgreSQL (already installed)
├─ Docker Desktop for Mac (Apple Silicon version)
├─ Homebrew (package manager)
└─ Git

Python Libraries:
├─ langchain (0.1.0+)
├─ langchain-openai (for LM Studio compatibility)
├─ langgraph (0.0.20+)
├─ pydantic (2.5.0+)
├─ sqlalchemy (2.0.23+)
├─ psycopg2-binary (2.9.9+)
├─ loguru (0.7.2+)
├─ pyyaml (6.0+)
├─ pytest (7.4.0+)
└─ httpx (0.25.0+)
```

### **1.3 M4 Optimization**

```
Leverage Apple Silicon:
├─ Use MLX-optimized models (faster inference)
├─ Enable Metal GPU acceleration
├─ Use unified memory efficiently
└─ Leverage Neural Engine where possible

macOS Settings:
├─ Disable automatic graphics switching (use High Performance)
├─ Increase file descriptor limits
├─ Enable Docker resource limits
└─ Configure swap space (if needed)

Terminal Commands:
  # Increase file descriptor limit
  ulimit -n 10240
  
  # Check available memory
  vm_stat
  
  # Monitor GPU usage
  sudo powermetrics --samplers gpu_power
```

---

## 2. LLM Model Selection

### **2.1 Model Comparison for Meta-Agent**

| Model | Size | RAM Usage | Tokens/sec (M4) | Code Quality | Availability |
|-------|------|-----------|-----------------|--------------|--------------|
| **qwen2.5-coder-7b-instruct-mlx** | 7B | ~6GB | ~40-50 | Excellent | ✓ |
| **deepseek-coder-6.7b-instruct-mlx** | 6.7B | ~5.5GB | ~45-55 | Excellent | ✓ |
| **codellama-7b-instruct-mlx** | 7B | ~6GB | ~35-45 | Good | ✓ |
| **mistral-7b-instruct-v0.2-mlx** | 7B | ~6GB | ~40-50 | Good | ✓ |
| **phi-3-medium-mlx** | 14B | ~10GB | ~20-25 | Very Good | ⚠️ Tight |
| **qwen2.5-coder-14b-instruct-mlx** | 14B | ~10GB | ~25-30 | Excellent | ⚠️ Tight |

### **2.2 Recommended Model: qwen2.5-coder-7b-instruct-mlx**

**Why This Model:**

✅ **Optimized for 16GB RAM**
- Base model: ~6GB
- Leaves ~10GB for other processes
- Comfortable headroom

✅ **MLX Optimization**
- 40-50 tokens/sec on M4
- Efficient memory usage
- GPU acceleration

✅ **Code Generation Excellence**
- Trained specifically for code
- Understands Python, YAML, Markdown
- Good at following specifications

✅ **Context Window**
- 32K tokens (sufficient for agent specs)
- Can handle large specifications

✅ **Instruction Following**
- Excellent at tool calling
- Follows structured output formats
- Good at reasoning

### **2.3 Alternative: deepseek-coder-6.7b-instruct-mlx**

**Consider if:**
- Need faster inference (~45-55 tokens/sec)
- Want slightly lower memory footprint (~5.5GB)
- Prioritize speed over marginal quality difference

**Trade-offs:**
- Slightly smaller context window (16K vs 32K)
- Less well-known, fewer community resources

### **2.4 NOT Recommended (for 16GB)**

❌ **qwen2.5-coder-14b-instruct-mlx**
- Too large (~10GB)
- Only ~6GB left for everything else
- Risk of memory pressure and swapping
- Slower inference (~25-30 tokens/sec)

❌ **qwen2.5-coder-32b-instruct**
- Impossible to run on 16GB
- Requires 20GB+ RAM

### **2.5 LM Studio Configuration**

```
Recommended Settings for qwen2.5-coder-7b-instruct-mlx:

Model Parameters:
├─ Context Length: 8192 (sufficient, saves memory vs 32K)
├─ Temperature: 0.1 (deterministic for code generation)
├─ Top P: 0.95
├─ Top K: 40
├─ Max Tokens: 4096 (per response)
├─ Stop Sequences: ["```\n\n", "###"]
└─ Repeat Penalty: 1.1

Server Settings:
├─ Port: 1234 (default)
├─ Enable CORS: Yes
├─ API Type: OpenAI Compatible
├─ GPU Layers: Auto (use all available)
└─ Thread Count: 8 (for M4 10-core)

Memory Settings:
├─ Model Memory: ~6GB
├─ GPU Memory: Use unified memory
└─ Batch Size: 512 (default)
```

---

## 3. Architecture Overview

### **3.1 System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    MacBook Pro M4 (16GB)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LM Studio (Port 1234)                                 │ │
│  │  Model: qwen2.5-coder-7b-instruct-mlx (~6GB)          │ │
│  │  API: OpenAI Compatible                                │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────┴───────────────────────────────────────┐ │
│  │  META-AGENT (~2GB)                                     │ │
│  │  ├─ Python 3.11                                        │ │
│  │  ├─ LangChain + LangGraph                             │ │
│  │  ├─ 15 Tool Functions                                  │ │
│  │  └─ Agent Writer Logic                                 │ │
│  └────────┬─────────────────┬─────────────────────────────┘ │
│           │                 │                                │
│  ┌────────┴─────────┐  ┌───┴────────────────────────────┐  │
│  │  PostgreSQL      │  │  Docker Desktop (~2GB)         │  │
│  │  (~1GB)          │  │  ├─ Sandbox Containers         │  │
│  │  - Properties    │  │  └─ Python 3.11-slim           │  │
│  │  - Metrics       │  └────────────────────────────────┘  │
│  │  - Formula Lib   │                                       │
│  └──────────────────┘                                       │
│                                                              │
│  OUTPUT:                                                     │
│  ├─ Generated Agents (src/agents/)                         │
│  ├─ Tests (tests/)                                          │
│  ├─ Specs (agent_specs/)                                   │
│  └─ Docs (docs/)                                            │
└─────────────────────────────────────────────────────────────┘
```

### **3.2 Data Flow**

```
USER INPUT (Natural Language)
    ↓
Meta-Agent (Python)
    ↓
    ├─→ LM Studio API (http://localhost:1234/v1)
    │   ├─ Requirements Analysis
    │   ├─ Architecture Design
    │   ├─ Specification Generation
    │   ├─ Code Generation
    │   └─ Test Generation
    │
    ├─→ PostgreSQL (localhost:5432)
    │   └─ Read existing schema (properties, financial_metrics)
    │
    └─→ Docker (localhost)
        └─ Sandbox execution (for custom mode testing)
    ↓
GENERATED AGENTS
    ↓
    ├─→ DataAgent
    │   └─→ PostgreSQL (fetch data)
    │
    └─→ CalcAgent
        ├─→ DataAgent (tool call)
        ├─→ LM Studio (analysis, decisions)
        └─→ Docker (sandbox for custom code)
```

---

## 4. Implementation Phases

### **Phase 0: Environment Setup (Day 1)**

**Duration**: 2-3 hours

**Tasks**:
1. Install/Update Software
2. Configure LM Studio
3. Download Model
4. Setup Project Structure
5. Test Connections

**Deliverables**:
- ✓ All software installed
- ✓ LM Studio running with model
- ✓ PostgreSQL accessible
- ✓ Docker running
- ✓ Python environment ready

### **Phase 1: Meta-Agent Foundation (Days 2-3)**

**Duration**: 2 days

**Tasks**:
1. Build Tool System (15 tools)
2. Implement Meta-Agent Core
3. Create Prompt Templates
4. Setup LLM Integration
5. Build Validation Framework

**Deliverables**:
- ✓ 15 tool functions implemented
- ✓ Meta-Agent base class
- ✓ LLM client wrapper
- ✓ Validation utilities

### **Phase 2: Simple Agent Generation (Days 4-5)**

**Duration**: 2 days

**Tasks**:
1. Implement Requirements Analyzer
2. Implement Architecture Designer
3. Build Spec Generator
4. Build Code Generator
5. Test with Simple DSCR Request

**Deliverables**:
- ✓ Can generate DataAgent
- ✓ Can generate simple CalcAgent
- ✓ Tests pass for generated agents
- ✓ Documentation generated

### **Phase 3: Complex Agent Generation (Days 6-8)**

**Duration**: 3 days

**Tasks**:
1. Enhance Code Generator for Multi-Mode
2. Implement Code Validator
3. Build Sandbox Executor Integration
4. Implement Error Recovery
5. Test with Complex Multi-Mode Request

**Deliverables**:
- ✓ Can generate multi-mode CalcAgent
- ✓ Code validation working
- ✓ Sandbox execution working
- ✓ Error recovery functional

### **Phase 4: Integration & Testing (Days 9-10)**

**Duration**: 2 days

**Tasks**:
1. End-to-end Testing
2. Performance Optimization
3. Documentation
4. User Interface (CLI)
5. Demo Preparation

**Deliverables**:
- ✓ Full system tested
- ✓ Performance acceptable
- ✓ Complete documentation
- ✓ CLI interface
- ✓ Demo ready

---

## 5. Detailed Setup Instructions

### **5.1 Initial Setup (Phase 0)**

#### **Step 1: Install Core Software**

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python 3.11
brew install python@3.11

# 3. Verify Python version
python3.11 --version  # Should be 3.11.x

# 4. Install PostgreSQL (if not already installed)
brew install postgresql@15

# 5. Start PostgreSQL
brew services start postgresql@15

# 6. Install Docker Desktop for Mac (Apple Silicon)
# Download from: https://www.docker.com/products/docker-desktop/
# Install and start Docker Desktop

# 7. Verify Docker
docker --version
docker ps  # Should show no errors
```

#### **Step 2: Install LM Studio**

```bash
# 1. Download LM Studio
# Visit: https://lmstudio.ai/
# Download macOS version (Apple Silicon)

# 2. Install application
# Drag to Applications folder

# 3. Launch LM Studio
# Open LM Studio from Applications

# 4. Download Model
In LM Studio:
  → Search: "qwen2.5-coder-7b-instruct-mlx"
  → Download the MLX version (optimized for Apple Silicon)
  → Wait for download (takes 5-10 minutes)

# 5. Load Model
  → Click on model in "My Models"
  → Click "Load Model"
  → Wait for model to load (~30 seconds)

# 6. Start Server
  → Click "Local Server" tab
  → Configure:
     - Port: 1234
     - Context Length: 8192
     - Temperature: 0.1
     - Max Tokens: 4096
  → Click "Start Server"
  → Server should show "Running on http://localhost:1234"

# 7. Test Server
curl http://localhost:1234/v1/models

# Expected output:
# {"object":"list","data":[{"id":"qwen2.5-coder-7b-instruct-mlx",...}]}
```

#### **Step 3: Setup Project Structure**

```bash
# 1. Navigate to project directory
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_New"

# 2. Create project structure
mkdir -p meta_agent/tools
mkdir -p meta_agent/prompts
mkdir -p meta_agent/validators
mkdir -p meta_agent/utils
mkdir -p agent_specs
mkdir -p src/agents
mkdir -p tests/agents
mkdir -p tests/meta_agent
mkdir -p docs/agents
mkdir -p logs
mkdir -p sandbox

# 3. Create Python virtual environment
python3.11 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip

# 6. Create requirements.txt
cat > requirements.txt << 'EOF'
# LLM & Agent Framework
langchain==0.1.0
langchain-openai==0.0.2
langgraph==0.0.20
langchain-core==0.1.10

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Utilities
loguru==0.7.2
python-dotenv==1.0.0
pyyaml==6.0.1
httpx==0.25.2
requests==2.31.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Code Analysis
ast-comments==1.1.2
black==23.12.0
isort==5.13.2

# Docker SDK (for sandbox)
docker==7.0.0

# Progress & CLI
tqdm==4.66.1
click==8.1.7
rich==13.7.0
EOF

# 7. Install dependencies
pip install -r requirements.txt

# 8. Create .env file
cat > .env << 'EOF'
# LM Studio Configuration
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096

# Database Configuration (use existing)
DATABASE_URL=postgresql://username:password@localhost:5432/orlando_db

# Meta-Agent Configuration
META_AGENT_LOG_LEVEL=INFO
META_AGENT_MAX_RETRIES=3
META_AGENT_TIMEOUT=300

# Sandbox Configuration
DOCKER_TIMEOUT=30
SANDBOX_MEMORY_LIMIT=512m
SANDBOX_CPU_LIMIT=1.0
EOF

# 9. Update DATABASE_URL with your actual credentials
# Edit .env and replace username, password, and database name
```

#### **Step 4: Verify Existing PostgreSQL Data**

```bash
# 1. Connect to PostgreSQL
psql -U your_username -d orlando_db

# 2. Verify tables exist
\dt

# Expected output should include:
#   properties
#   financial_metrics

# 3. Check sample data
SELECT id, property_name, location FROM properties LIMIT 5;

SELECT property_id, annual_noi, annual_debt_service 
FROM financial_metrics LIMIT 5;

# 4. Exit psql
\q
```

#### **Step 5: Test All Connections**

```bash
# Create test script
cat > test_connections.py << 'EOF'
import os
from dotenv import load_dotenv
import httpx
from sqlalchemy import create_engine, text

load_dotenv()

# Test 1: LM Studio
print("Testing LM Studio...")
try:
    response = httpx.get(f"{os.getenv('LLM_BASE_URL')}/models", timeout=5)
    if response.status_code == 200:
        print("✓ LM Studio: Connected")
    else:
        print(f"✗ LM Studio: Error {response.status_code}")
except Exception as e:
    print(f"✗ LM Studio: {e}")

# Test 2: PostgreSQL
print("\nTesting PostgreSQL...")
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM properties"))
        count = result.scalar()
        print(f"✓ PostgreSQL: Connected ({count} properties)")
except Exception as e:
    print(f"✗ PostgreSQL: {e}")

# Test 3: Docker
print("\nTesting Docker...")
try:
    import docker
    client = docker.from_env()
    client.ping()
    print("✓ Docker: Connected")
except Exception as e:
    print(f"✗ Docker: {e}")

print("\n" + "="*50)
print("Setup verification complete!")
EOF

# Run test
python test_connections.py
```

**Expected Output**:
```
Testing LM Studio...
✓ LM Studio: Connected

Testing PostgreSQL...
✓ PostgreSQL: Connected (10 properties)

Testing Docker...
✓ Docker: Connected

==================================================
Setup verification complete!
```

---

## 6. Resource Management

### **6.1 Memory Optimization**

#### **Strategy 1: Sequential Processing**

```
Avoid Parallel Operations:
  ✗ BAD: Generate multiple agents simultaneously
  ✓ GOOD: Generate one agent at a time
  
  Reason: Each LLM call uses memory for:
    - Model weights (static, ~6GB)
    - Context window (dynamic, varies)
    - Response buffer
  
  Sequential = Lower peak memory usage
```

#### **Strategy 2: Context Window Management**

```
Limit Context Size:
  - Use 8192 tokens instead of 32K
  - Saves ~1-2GB of memory
  - Still sufficient for agent specs
  
  Break Large Specs:
  - If spec > 6000 tokens:
    → Generate in components
    → Combine after generation
```

#### **Strategy 3: Model Unloading**

```
IF memory pressure detected:
  1. Complete current generation
  2. Unload model from LM Studio
  3. Free up ~6GB
  4. Continue with validation/testing
  5. Reload model when needed

Detection:
  - Monitor with: vm_stat | grep "Pages free"
  - Alert if free memory < 2GB
```

#### **Strategy 4: Docker Memory Limits**

```
Sandbox Container Limits:
  - Memory: 512MB (sufficient for code execution)
  - CPU: 1.0 core
  - Timeout: 30 seconds
  
Docker Desktop Settings:
  - Memory: 4GB max
  - CPUs: 4 cores max
  - Swap: 2GB
```

### **6.2 Performance Optimization**

#### **LLM Inference Speed**

```
Expected Performance (qwen2.5-coder-7b-instruct-mlx on M4):
├─ Tokens/sec: 40-50
├─ Average response (500 tokens): ~10-12 seconds
├─ Large code gen (2000 tokens): ~40-50 seconds
└─ Spec generation (1000 tokens): ~20-25 seconds

Total Generation Time Estimates:
├─ Simple Agent (DataAgent):
│   - Spec generation: ~25 seconds
│   - Code generation: ~45 seconds
│   - Test generation: ~30 seconds
│   - Total: ~1.5-2 minutes
│
└─ Complex Agent (Multi-mode CalcAgent):
    - Spec generation: ~35 seconds
    - Code generation (8 files): ~6-8 minutes
    - Test generation: ~2 minutes
    - Total: ~8-10 minutes

Bottlenecks:
  1. LLM inference (largest)
  2. Code validation (minimal)
  3. Test execution (varies)
  4. File I/O (negligible)
```

#### **Caching Strategy**

```
Cache Generated Components:
├─ Template code (reduce regeneration)
├─ Common patterns (imports, base classes)
├─ Validation results (skip if code unchanged)
└─ Test fixtures (reuse across tests)

Implementation:
  - Use file-based cache (disk)
  - Hash specs as cache key
  - Invalidate on spec change
  
Expected Speed Improvement:
  - 20-30% faster for similar requests
  - 50%+ faster for exact duplicates
```

### **6.3 Monitoring Commands**

```bash
# Monitor Memory Usage
watch -n 1 "ps aux | grep -E '(LM Studio|Python|postgres|docker)' | grep -v grep"

# Monitor GPU/Neural Engine
sudo powermetrics --samplers gpu_power -n 1

# Monitor Docker
docker stats

# Monitor PostgreSQL
psql -c "SELECT * FROM pg_stat_activity"

# Check LM Studio Status
curl http://localhost:1234/v1/models

# Monitor Python Process
top -pid $(pgrep -f "meta_agent")
```

---

## 7. Testing Strategy

### **7.1 Unit Tests**

```
Test Coverage:
├─ Tool Functions (15 tools)
│   ├─ analyze_requirements
│   ├─ design_agent_architecture
│   ├─ generate_agent_specification
│   └─ ... (12 more)
│
├─ Meta-Agent Core
│   ├─ Request parsing
│   ├─ Tool selection
│   ├─ Error handling
│   └─ Result aggregation
│
└─ Validators
    ├─ Spec validator
    ├─ Code syntax validator
    └─ Security validator

Target Coverage: 80%+

Test Execution:
  pytest tests/meta_agent/ -v --cov=meta_agent
```

### **7.2 Integration Tests**

```
Test Scenarios:
├─ Scenario 1: Simple DSCR Agent
│   Input: "Calculate DSCR from PostgreSQL"
│   Expected: DataAgent + CalcAgent generated
│   Time: ~4 minutes
│
├─ Scenario 2: Multi-Mode DSCR Agent
│   Input: "DSCR with 3 modes and LLM analysis"
│   Expected: DataAgent + Complex CalcAgent
│   Time: ~12 minutes
│
└─ Scenario 3: Custom Requirements
    Input: "DSCR with 15% stress test"
    Expected: Agents with custom code generation
    Time: ~15 minutes

Test Execution:
  pytest tests/integration/ -v -s --timeout=900
```

### **7.3 Generated Agent Tests**

```
After Meta-Agent generates agents:
├─ Auto-generated unit tests run automatically
├─ Verify all tests pass
└─ Check code coverage

Example:
  Generated: src/agents/data_agent.py
  Auto-generated: tests/agents/test_data_agent.py
  Run: pytest tests/agents/test_data_agent.py
  Expected: All tests pass
```

### **7.4 Performance Tests**

```
Measure:
├─ Generation time per agent type
├─ Memory usage during generation
├─ LLM token usage
└─ Docker sandbox overhead

Benchmarks:
├─ Simple agent: < 3 minutes
├─ Complex agent: < 15 minutes
├─ Memory peak: < 14GB (leaving 2GB buffer)
└─ LLM calls: < 20 per complex agent

Test Execution:
  python tests/performance/benchmark_generation.py
```

---

## 8. Timeline & Milestones

### **Detailed Implementation Schedule**

```
Week 1: Foundation
═══════════════════════════════════════════════════════════════

Day 1 (Monday): Environment Setup
─────────────────────────────────
Tasks:
  ☐ Install all software (2 hours)
  ☐ Configure LM Studio (1 hour)
  ☐ Setup project structure (30 min)
  ☐ Test all connections (30 min)

Milestone: ✓ Environment ready, all tests pass

Day 2 (Tuesday): Tool System - Part 1
──────────────────────────────────────
Tasks:
  ☐ Implement tool base class (1 hour)
  ☐ Implement 5 tools:
     - analyze_requirements (1.5 hours)
     - design_agent_architecture (1.5 hours)
     - generate_agent_specification (1.5 hours)
     - validate_specification (1 hour)
     - write_file (30 min)
  ☐ Write unit tests (1.5 hours)

Milestone: ✓ 5 tools working and tested

Day 3 (Wednesday): Tool System - Part 2
────────────────────────────────────────
Tasks:
  ☐ Implement 10 more tools:
     - generate_agent_code (2 hours)
     - validate_code_syntax (1 hour)
     - validate_code_security (1.5 hours)
     - generate_unit_tests (1.5 hours)
     - run_tests (1 hour)
     - read_file (30 min)
     - create_directory (30 min)
     - generate_documentation (1 hour)
     - deploy_agent (1 hour)
     - verify_agent_health (30 min)
  ☐ Integration testing (1 hour)

Milestone: ✓ All 15 tools implemented and tested

Day 4 (Thursday): Meta-Agent Core
──────────────────────────────────
Tasks:
  ☐ Build Meta-Agent base class (2 hours)
  ☐ Implement LLM client wrapper (1.5 hours)
  ☐ Build prompt template system (1.5 hours)
  ☐ Implement tool orchestration (2 hours)
  ☐ Add logging and monitoring (1 hour)

Milestone: ✓ Meta-Agent can make tool calls

Day 5 (Friday): Simple Agent Generation
────────────────────────────────────────
Tasks:
  ☐ Build requirements analyzer (1.5 hours)
  ☐ Build architecture designer (1.5 hours)
  ☐ Implement spec generator (2 hours)
  ☐ Implement code generator (2 hours)
  ☐ Test with simple DSCR request (1 hour)

Milestone: ✓ Can generate simple DataAgent

Week 1 Summary:
  Time: 40 hours
  Deliverables:
    ✓ 15 tools implemented
    ✓ Meta-Agent core functional
    ✓ Can generate simple agents


Week 2: Advanced Features & Testing
═══════════════════════════════════════════════════════════════

Day 6 (Monday): Complex Agent Support
──────────────────────────────────────
Tasks:
  ☐ Enhance code generator for multi-component agents (3 hours)
  ☐ Implement modular code generation (2 hours)
  ☐ Add component dependency resolution (2 hours)
  ☐ Test with multi-component CalcAgent (1 hour)

Milestone: ✓ Can generate complex multi-file agents

Day 7 (Tuesday): Validation & Security
───────────────────────────────────────
Tasks:
  ☐ Build comprehensive code validator (2 hours)
  ☐ Implement security checker (2 hours)
  ☐ Add syntax validator (1 hour)
  ☐ Build test for validation pipeline (1.5 hours)
  ☐ Test with intentionally bad code (1.5 hours)

Milestone: ✓ Validation catches all security issues

Day 8 (Wednesday): Sandbox Execution
─────────────────────────────────────
Tasks:
  ☐ Build Docker sandbox wrapper (2 hours)
  ☐ Implement code injection (1.5 hours)
  ☐ Add resource limiting (1 hour)
  ☐ Implement result extraction (1 hour)
  ☐ Test sandbox with custom code (2 hours)
  ☐ Error handling for sandbox failures (1.5 hours)

Milestone: ✓ Custom code executes safely in sandbox

Day 9 (Thursday): Error Recovery & Optimization
────────────────────────────────────────────────
Tasks:
  ☐ Implement retry logic (1.5 hours)
  ☐ Build error analysis (2 hours)
  ☐ Add self-correction (2 hours)
  ☐ Optimize LLM prompts (1.5 hours)
  ☐ Add caching layer (1.5 hours)
  ☐ Performance testing (1.5 hours)

Milestone: ✓ System recovers from errors automatically

Day 10 (Friday): Integration & Polish
──────────────────────────────────────
Tasks:
  ☐ End-to-end testing (2 hours)
  ☐ Build CLI interface (2 hours)
  ☐ Write comprehensive documentation (2 hours)
  ☐ Performance benchmarking (1.5 hours)
  ☐ Create demo examples (1.5 hours)
  ☐ Final testing and bug fixes (1 hour)

Milestone: ✓ Complete system ready for use

Week 2 Summary:
  Time: 40 hours
  Deliverables:
    ✓ Full Meta-Agent system operational
    ✓ Can generate any agent type
    ✓ Error recovery functional
    ✓ CLI interface ready
    ✓ Complete documentation


Total Implementation Time: 80 hours (2 weeks)
```

### **Critical Path**

```
Dependencies:
  Day 1 → Must complete before Day 2
  Days 2-3 → Must complete before Day 4
  Day 4 → Must complete before Day 5
  Days 5-6 → Must complete before Day 8
  Day 8 → Must complete before Day 9

Parallel Opportunities:
  - Documentation can be written alongside implementation
  - Unit tests can be written alongside tools
  - Some tools are independent and can be built in any order
```

### **Success Criteria**

```
Phase 0 Success:
  ☐ All software installed
  ☐ LM Studio running with model loaded
  ☐ PostgreSQL accessible with sample data
  ☐ Docker operational
  ☐ Test script passes all checks

Phase 1 Success:
  ☐ All 15 tools implemented
  ☐ Meta-Agent core functional
  ☐ Can make LLM calls successfully
  ☐ Logging system working

Phase 2 Success:
  ☐ Can generate simple DataAgent from NL request
  ☐ Generated agent code is valid
  ☐ Generated tests pass
  ☐ Generation time < 3 minutes

Phase 3 Success:
  ☐ Can generate complex multi-mode CalcAgent
  ☐ All components generated correctly
  ☐ Security validation works
  ☐ Sandbox execution works
  ☐ Generation time < 15 minutes

Phase 4 Success:
  ☐ End-to-end tests pass
  ☐ Error recovery works
  ☐ Performance meets benchmarks
  ☐ Documentation complete
  ☐ Demo ready
```

---

## 9. Usage Examples

### **9.1 Running Meta-Agent (After Implementation)**

```bash
# Activate environment
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_New"
source venv/bin/activate

# Ensure LM Studio is running (check in app)

# Run Meta-Agent CLI
python meta_agent_cli.py

# Interactive mode
>>> Enter your request: I need an agent to calculate DSCR for properties

Meta-Agent: Analyzing request...
Meta-Agent: Requirements extracted
Meta-Agent: Designing 2-agent architecture
Meta-Agent: Generating DataAgent...
Meta-Agent: ✓ DataAgent complete (1.8 minutes)
Meta-Agent: Generating CalcAgent...
Meta-Agent: ✓ CalcAgent complete (2.1 minutes)
Meta-Agent: Running tests...
Meta-Agent: ✓ All tests passed (4/4)
Meta-Agent: ✓ System ready!

Generated files:
  - src/agents/data_agent.py
  - src/agents/calc_agent.py
  - tests/agents/test_data_agent.py
  - tests/agents/test_calc_agent.py
  - docs/agents/data_agent.md
  - docs/agents/calc_agent.md

Total time: 3 minutes 54 seconds

# Test generated agents
python -c "
from src.agents.calc_agent import CalcAgent
agent = CalcAgent()
result = agent.calculate_dscr(property_id=5)
print(f'DSCR: {result.dscr}, Status: {result.validation_status}')
"

Output:
  DSCR: 1.35, Status: PASS
```

### **9.2 Complex Request Example**

```bash
python meta_agent_cli.py

>>> Enter your request: Build a DSCR system with 3 modes - standard, 
    conservative (10% NOI haircut), and custom (user describes stress 
    tests). Include LLM analysis and adjustment suggestions.

Meta-Agent: Analyzing complex request...
Meta-Agent: Detected: HIGH complexity
Meta-Agent: Designing 2-agent architecture (11 components)
Meta-Agent: Generating DataAgent...
Meta-Agent: ✓ DataAgent complete (1.9 minutes)
Meta-Agent: Generating CalcAgent (complex)...
  → Generating main class... (45 seconds)
  → Generating mode detector... (30 seconds)
  → Generating standard calculator... (40 seconds)
  → Generating library calculator... (50 seconds)
  → Generating custom calculator... (2.5 minutes)
  → Generating analysis engine... (1.2 minutes)
  → Generating decision engine... (1.1 minutes)
  → Generating report generator... (35 seconds)
Meta-Agent: ✓ CalcAgent complete (8.2 minutes)
Meta-Agent: Generating tests...
Meta-Agent: ✓ Tests generated (2.3 minutes)
Meta-Agent: Running tests...
  → 23/25 tests passed
  → 2 tests failed (analyzing...)
Meta-Agent: Fixing issues...
  → Regenerating custom calculator (timeout fix)
  → Regenerating decision engine (iteration fix)
Meta-Agent: Re-running tests...
Meta-Agent: ✓ All tests passed (25/25)
Meta-Agent: ✓ System ready!

Total time: 12 minutes 18 seconds
Total LLM calls: 18
Total tokens: ~45,000
```

---

## 10. Troubleshooting

### **10.1 Common Issues**

```
ISSUE: LM Studio not responding
SOLUTION:
  1. Check if server is running (green indicator)
  2. Restart LM Studio
  3. Reload model
  4. Test with: curl http://localhost:1234/v1/models

ISSUE: Out of memory errors
SOLUTION:
  1. Close unnecessary applications
  2. Reduce context length to 4096
  3. Process one agent at a time
  4. Monitor with: vm_stat

ISSUE: PostgreSQL connection refused
SOLUTION:
  1. Check if PostgreSQL is running:
     brew services list
  2. Start if needed:
     brew services start postgresql@15
  3. Verify connection:
     psql -U username -d orlando_db

ISSUE: Docker sandbox timeout
SOLUTION:
  1. Increase timeout in .env (DOCKER_TIMEOUT=60)
  2. Check Docker resource limits
  3. Restart Docker Desktop

ISSUE: Generated code has syntax errors
SOLUTION:
  1. Check LLM temperature (should be 0.1)
  2. Verify model is loaded correctly
  3. Meta-Agent should auto-fix (retry mechanism)
  4. If persists, regenerate with explicit instructions

ISSUE: Slow generation (>20 minutes)
SOLUTION:
  1. Check LM Studio GPU usage
  2. Reduce context length
  3. Close background apps
  4. Check if swapping (Activity Monitor)
```

---

## ✅ Final Recommendations

### **For 16GB M4 MacBook Pro**

**✅ DO:**
- Use qwen2.5-coder-7b-instruct-mlx (best balance)
- Keep context length at 8192 (saves memory)
- Generate agents sequentially (not parallel)
- Monitor memory usage regularly
- Close unused applications during generation
- Use Docker resource limits

**❌ DON'T:**
- Try to run 14B+ models (insufficient RAM)
- Generate multiple agents simultaneously
- Use 32K context unless necessary
- Run without monitoring memory
- Skip validation steps (causes rework)

### **Expected Performance**

```
Simple Agent Generation:
  Time: 2-4 minutes
  Memory: Peak 12GB
  Success Rate: >95%

Complex Agent Generation:
  Time: 10-15 minutes
  Memory: Peak 14GB
  Success Rate: >90% (with retry)

Resource Usage:
  CPU: 60-80% during LLM inference
  GPU: 80-95% during LLM inference
  Memory: 12-14GB peak
  Disk I/O: Minimal
```

### **Next Steps After Implementation**

```
1. Run integration tests with existing PostgreSQL data
2. Generate 2-3 different agent systems to validate
3. Benchmark performance and optimize
4. Create library of pre-generated agent specs
5. Build web UI (optional, future enhancement)
6. Integrate with CI/CD (optional)
```

---

**Ready to build! Start with Phase 0 (Day 1) and follow the timeline.** 🚀

**Estimated total implementation time: 80 hours (2 weeks at 8 hours/day)**

