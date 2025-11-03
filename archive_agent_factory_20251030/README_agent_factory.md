# Meta-Agent: Automated Agent Generation System

**Status**: Foundation Built ✓  
**Mode**: Strict (No Fallbacks)  
**LLM**: LM Studio with qwen2.5-coder-7b-instruct-mlx

---

## 🎯 What Has Been Built

### ✅ Completed Components

1. **Project Structure**
   - Organized directory layout
   - Python packages with proper `__init__.py`
   - Configuration management

2. **Configuration System** (`config.py`)
   - Pydantic-based settings
   - Environment variable loading from `.env`
   - **NO HARDCODED VALUES** - All config from environment
   - Strict validation - fails fast if misconfigured

3. **LLM Client** (`meta_agent/utils/llm_client.py`)
   - Connects to LM Studio
   - **NO FALLBACKS** - Fails if LM Studio not available
   - JSON and text generation
   - Health checking

4. **Core Tools** (4/15 tools built)
   - ✓ Tool #1: `analyze_requirements` - Parse natural language → structured requirements
   - ✓ Tool #2: `design_agent_architecture` - Design agent system architecture
   - ✓ Tool #3: `generate_agent_specification` - Create YAML specs for agents
   - ✓ Tool #4: `generate_agent_code` - Generate Python code from specs

5. **Validators**
   - ✓ `validate_code_syntax` - AST-based syntax validation
   - ✓ `validate_code_security` - Security checks (dangerous functions, imports, hardcoded secrets)
   - ✓ Combined validation with risk scoring

6. **File Operations**
   - ✓ `write_file` - Write with overwrite protection
   - ✓ `read_file` - Read with error handling
   - ✓ `create_directory` - Create with parents
   - ✓ `write_agent_files` - Write complete agent file set

7. **Testing Infrastructure**
   - ✓ `test_setup.py` - Verify all components are configured
   - Tests: LM Studio, PostgreSQL, Docker, Configuration

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_New"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Start the DSCR POC Database

Meta-Agent uses the database from the WinPrA Agentic POC project:

```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose up -d postgres
```

Verify it's running:
```bash
docker ps | grep dscr_poc_postgres
```

**See DATABASE_CONFIG.md for complete database setup details.**

### 4. Configure Environment

**Option A: Run setup script (recommended)**

```bash
./setup_env.sh
```

This creates `.env` file with correct database configuration.

**Option B: Create .env manually**

Create `.env` file in project root with:

```bash
# LM Studio Configuration (REQUIRED)
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
LLM_CONTEXT_LENGTH=8192

# Database Configuration (REQUIRED)
# Using WinPrA Agentic POC database (DSCR POC)
DATABASE_URL=postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db

# Meta-Agent Configuration
META_AGENT_STRICT_MODE=true
META_AGENT_MAX_RETRIES=3
```

**Important**: This uses the DSCR POC database from the WinPrA Agentic POC project. Ensure the Docker containers are running:
```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose up -d postgres
```

### 5. Start LM Studio

1. Open LM Studio
2. Load model: `qwen2.5-coder-7b-instruct-mlx`
3. Start local server (port 1234)
4. Verify it's running

### 6. Verify Setup

```bash
python test_setup.py
```

Expected output:
```
✓ Configuration loaded
✓ LM Studio connected successfully
✓ PostgreSQL connected successfully
✓ All tools imported successfully

✓ ALL REQUIRED TESTS PASSED
```

---

## 📁 Project Structure

```
AgenticPOC_New/
├── meta_agent/              # Core Meta-Agent system
│   ├── core/                # Orchestrator (to be built)
│   ├── tools/               # 15 tool functions
│   │   ├── analyze_requirements.py       ✓ Built
│   │   ├── design_agent_architecture.py  ✓ Built
│   │   ├── generate_agent_specification.py ✓ Built
│   │   ├── generate_agent_code.py        ✓ Built
│   │   └── file_operations.py            ✓ Built
│   ├── validators/          # Code validators
│   │   └── code_validator.py             ✓ Built
│   ├── utils/               # Utilities
│   │   └── llm_client.py                 ✓ Built
│   └── prompts/             # LLM prompt templates
│
├── agent_specs/             # Generated YAML specifications
├── generated_agents/        # Generated agent code
│   ├── agents/              # Agent Python files
│   └── tests/               # Generated tests
│
├── logs/                    # Execution logs
├── config.py                # Configuration management ✓
├── requirements.txt         # Dependencies ✓
├── test_setup.py            # Setup verification ✓
└── README.md                # This file ✓
```

---

## 🔧 How It Works

### Workflow (When Complete)

```
USER NATURAL LANGUAGE REQUEST
    ↓
1. analyze_requirements (Tool #1)
   - Extracts structured requirements using LLM
    ↓
2. design_agent_architecture (Tool #2)
   - Designs agent system architecture using LLM
    ↓
3. generate_agent_specification (Tool #3)
   - Creates detailed YAML spec for each agent using LLM
    ↓
4. generate_agent_code (Tool #4)
   - Generates Python code from YAML spec using LLM
    ↓
5. validate_code (Validator)
   - Syntax validation (AST parsing)
   - Security validation (dangerous patterns)
    ↓
6. write_agent_files (File Operations)
   - Writes spec, code, tests to disk
    ↓
COMPLETE AGENT SYSTEM GENERATED
```

### Example Request (When System Complete)

```python
from meta_agent.core.meta_agent import MetaAgent

agent = MetaAgent()

result = agent.generate("""
I need an agent to calculate DSCR for commercial properties.
Fetch data from PostgreSQL. Formula: annual_noi / annual_debt_service.
Validate that DSCR is above 1.25.
""")

# Result: DataAgent.py and CalcAgent.py files created
```

---

## ⚙️ Configuration Details

### LLM Configuration

- **Model**: qwen2.5-coder-7b-instruct-mlx (recommended for 16GB RAM)
- **Context**: 8192 tokens (saves memory vs 32K)
- **Temperature**: 0.1 (deterministic code generation)
- **Max Tokens**: 4096 per response

### Strict Mode

When `META_AGENT_STRICT_MODE=true`:
- ✗ No fallbacks if LLM unavailable
- ✗ No hardcoded values anywhere
- ✗ Fails fast with clear error messages
- ✓ Forces proper configuration
- ✓ Ensures all components working

This is the recommended mode for production.

---

## 🧪 Testing

### Verify Setup

```bash
python test_setup.py
```

Tests:
- ✓ Configuration loads
- ✓ LM Studio connection
- ✓ PostgreSQL connection
- ✓ Docker availability (optional)
- ✓ Tool imports

### Test Individual Tools

```python
from meta_agent.utils.llm_client import LLMClient
from meta_agent.tools.analyze_requirements import analyze_requirements

# Initialize LLM client
client = LLMClient()

# Test tool
requirements = analyze_requirements(
    "Calculate DSCR from PostgreSQL data",
    client
)

print(requirements.primary_goal)
print(requirements.required_agents)
print(requirements.complexity)
```

---

## 📊 What's Next (Remaining Work)

### Phase 1: Complete Core Tools (11 more tools)
- [ ] Tool #5: validate_specification
- [ ] Tool #6: generate_unit_tests
- [ ] Tool #7: run_tests
- [ ] Tool #8: generate_documentation
- [ ] Tools #9-15: Supporting utilities

### Phase 2: Build Meta-Agent Orchestrator
- [ ] Meta-Agent core class
- [ ] Tool orchestration logic
- [ ] Error recovery mechanism
- [ ] Logging and monitoring

### Phase 3: Integration & Testing
- [ ] End-to-end tests
- [ ] Simple DSCR example
- [ ] Complex multi-mode example
- [ ] Performance benchmarking

### Phase 4: Advanced Features
- [ ] Docker sandbox execution
- [ ] Multi-file code generation
- [ ] Component-based generation
- [ ] Self-correction on errors

---

## 🎯 Current Capabilities

### What Works Now

✅ **Requirement Analysis**
```python
from meta_agent.utils.llm_client import LLMClient
from meta_agent.tools.analyze_requirements import analyze_requirements

client = LLMClient()
requirements = analyze_requirements("Calculate DSCR...", client)
# Returns structured RequirementsAnalysis object
```

✅ **Architecture Design**
```python
from meta_agent.tools.design_agent_architecture import design_agent_architecture

architecture = design_agent_architecture(requirements, client)
# Returns ArchitectureDesign with agents, interactions, data flow
```

✅ **Specification Generation**
```python
from meta_agent.tools.generate_agent_specification import generate_agent_specification

yaml_spec = generate_agent_specification(
    agent_design=architecture.agents[0],
    architecture=architecture,
    requirements=requirements,
    llm_client=client
)
# Returns complete YAML specification
```

✅ **Code Generation**
```python
from meta_agent.tools.generate_agent_code import generate_agent_code

result = generate_agent_code(yaml_spec, client)
code = result["code"]
metadata = result["metadata"]
# Returns Python code + metadata
```

✅ **Code Validation**
```python
from meta_agent.validators.code_validator import validate_code

validation_result = validate_code(code)
print(f"Valid: {validation_result.valid}")
print(f"Risk Score: {validation_result.risk_score}")
print(f"Issues: {len(validation_result.issues)}")
```

✅ **File Writing**
```python
from meta_agent.tools.file_operations import write_agent_files

files = write_agent_files(
    agent_name="DataAgent",
    code=code,
    specification=yaml_spec
)
# Writes spec, code, optionally tests
```

### What's Missing

❌ Orchestrator to tie tools together
❌ Automated test generation
❌ Error recovery and retry logic
❌ Multi-component agent generation
❌ Sandbox execution for custom code

---

## 🔒 Security

### Built-in Security Features

1. **Code Validation**
   - AST-based syntax checking
   - Dangerous function detection (eval, exec, etc.)
   - Import whitelist/blacklist
   - Hardcoded secret detection
   - Risk scoring

2. **Strict Mode**
   - No fallback values
   - No hardcoded credentials
   - Environment-based configuration only
   - Fail-fast on errors

3. **Sandbox Execution** (when implemented)
   - Docker isolation
   - Resource limits (CPU, memory)
   - Network disabled
   - Timeout enforcement

---

## 📝 Logging

Logs are written to:
- Console (colorized, formatted)
- `logs/` directory (timestamped files)

Log levels:
- INFO: Normal operations
- DEBUG: Detailed execution
- WARNING: Issues that don't stop execution
- ERROR: Failures that stop execution

---

## 🐛 Troubleshooting

### LM Studio Connection Failed

```
Error: Cannot connect to LM Studio at http://localhost:1234/v1
```

**Solutions**:
1. Ensure LM Studio is running
2. Ensure model is loaded
3. Ensure local server is started (click "Start Server" in LM Studio)
4. Check port is 1234
5. Verify `LLM_BASE_URL` in `.env`

### PostgreSQL Connection Failed

```
Error: Database connection failed
```

**Solutions**:
1. Check PostgreSQL is running: `brew services list`
2. Start if needed: `brew services start postgresql@15`
3. Verify credentials in `.env`
4. Test connection: `psql -U your_user -d orlando_db`
5. Ensure `properties` table exists

### Configuration Error

```
Error: LLM_BASE_URL must be configured
```

**Solutions**:
1. Create `.env` file in project root
2. Copy example configuration from this README
3. Replace placeholder values with real ones
4. Restart Python to reload environment

---

## 📚 Resources

- **LM Studio**: https://lmstudio.ai/
- **qwen2.5-coder Model**: Search in LM Studio model library
- **PostgreSQL**: https://www.postgresql.org/
- **LangChain**: https://python.langchain.com/

---

## 🎯 Success Criteria

### Foundation Complete ✓

- [x] Project structure created
- [x] Configuration system (no hardcoded values)
- [x] LLM client (no fallbacks)
- [x] 4 core tools implemented
- [x] Code validators implemented
- [x] File operations implemented
- [x] Setup test created

### Next Milestone

- [ ] Remaining 11 tools built
- [ ] Meta-Agent orchestrator built
- [ ] End-to-end example working
- [ ] Can generate simple 2-agent system

---

## 💡 Key Design Principles

1. **No Fallbacks**: System fails clearly if dependencies missing
2. **No Hardcoded Values**: All configuration from environment
3. **LLM-Powered**: Uses LLM for intelligent code generation
4. **Security First**: Multiple validation layers
5. **Strict Mode**: Fails fast, clear error messages
6. **Production Ready**: Proper error handling, logging, validation

---

**Built for**: MacBook Pro M4, 16GB RAM, LM Studio
**Status**: Foundation complete, ready for next phase
**Last Updated**: 2025-01-27

