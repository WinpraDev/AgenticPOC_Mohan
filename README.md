# 🤖 Meta-Agent Script Executor

> Transform natural language into production-ready Python scripts with automatic validation, Docker containerization, and database integration using local LLMs.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Qwen2.5%20Coder-green.svg)](https://lmstudio.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Architecture](#%EF%B8%8F-architecture)
- [Usage Examples](#-usage-examples)
- [Technology Stack](#-technology-stack)
- [Configuration](#%EF%B8%8F-configuration)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🎯 Overview

**Meta-Agent Script Executor** is an AI-powered system that converts natural language requests into executable, production-ready Python scripts. It automatically handles task analysis, execution planning, code generation, validation, and containerized deployment—all in seconds.

### **Why Meta-Agent?**

Traditional approaches require manual scripting, testing, and deployment. Meta-Agent automates this entire workflow:

```
Natural Language Request → AI Analysis → Code Generation → Validation → Docker Deploy → Results
```

**Time Savings:** ~97% faster than manual development
**Reliability:** Built-in validation, security checks, and error handling
**Flexibility:** Supports database operations, web interfaces, calculations, and more

---

## ✨ Key Features

### 🚀 **Automated End-to-End Workflow**
- Natural language to executable Python in **8 seconds**
- Automatic task analysis and execution planning
- LLM-powered code generation (local Qwen2.5-Coder via LM Studio)
- Multi-layer validation (syntax, security, best practices)

### 🐳 **Containerized Execution**
- Automatic Docker containerization
- Isolated execution environments
- Resource limits and security controls
- One-command deployment

### 🗄️ **Smart Database Integration**
- Automatic schema discovery
- Dynamic query generation
- PostgreSQL support with RealDictCursor pattern
- Connection pooling and error handling

### 🌐 **Web Interface Generation**
- Auto-generated Flask applications
- Interactive dashboards
- Real-time results display
- Built-in simulation capabilities

### 🔒 **Security First**
- No hardcoded credentials (environment variables only)
- Container isolation
- Code validation and security scanning
- Dangerous pattern detection

### 📊 **Results Display**
- Terminal output with formatted results
- Web-based dashboards (when requested)
- Exportable reports (PDF, Excel)
- Real-time execution logs

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Docker** (with Docker Compose)
- **LM Studio** with `qwen2.5-coder-7b-instruct-mlx` model loaded
- **PostgreSQL** (optional, for database tasks)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AgenticPOC_Meta.git
cd AgenticPOC_Meta

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
bash setup_env.sh

# Edit .env file with your configuration
nano .env
```

### Configuration

Create a `.env` file in the project root:

```bash
# LM Studio Configuration
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
LLM_CONTEXT_LENGTH=8192

# Database Configuration (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/your_db

# Meta-Agent Configuration
META_AGENT_STRICT_MODE=true
```

### Run Your First Script

```bash
# Make sure LM Studio is running with the model loaded
# Start the Meta-Agent Script Executor
python script_executor.py
```

**Example Request (edit in `script_executor.py`):**
```python
user_request = """
Calculate the debt service coverage ratio (DSCR) for all properties in my portfolio.
Show me the property name, NOI, annual debt service, and DSCR for each property.
"""
```

**Output:**
```
📊 RESULTS
============================================================
   Orlando Fashion Square: NOI = 1681699.59, Annual Debt Service = 866855.46, DSCR = 1.94
   1893 Rouse Lake Rd: NOI = 2024147.93, Annual Debt Service = 1219366.22, DSCR = 1.66
   Orlando Vineland Premium Outlets: NOI = 813169.89, Annual Debt Service = 672041.23, DSCR = 1.21
   ...
============================================================
✨  COMPLETED SUCCESSFULLY
```

---

## 🏗️ Architecture

### Workflow Overview

```mermaid
graph LR
    A[Natural Language Request] --> B[Task Analyzer]
    B --> C[Execution Planner]
    C --> D[Script Generator LLM]
    D --> E[Script Validator]
    E --> F[Container Executor]
    F --> G[Results Display]
```

### 7-Step Process

1. **🔍 Task Analysis** - Understand request intent, complexity, and requirements
2. **📋 Execution Planning** - Design step-by-step execution plan with dependencies
3. **🗄️ Schema Discovery** - Inspect database structure (if needed)
4. **⚡ Script Generation** - LLM generates Python code with best practices
5. **🔒 Validation** - Syntax, security, and best practice checks
6. **📦 Containerization** - Package with Docker, dependencies, and environment
7. **🚀 Execution & Results** - Run in isolated container, display results

### Key Components

```
meta_agent/
├── analyzers/          # Task understanding
├── planners/           # Execution strategy
├── generators/         # Code & Docker generation
├── validators/         # Multi-layer validation
├── executors/          # Container management
└── utils/              # LLM client, DB inspector
```

---

## 💡 Usage Examples

### Example 1: Financial Calculations (Console Output)

```python
user_request = """
Calculate the debt service coverage ratio (DSCR) for all properties in my portfolio.
"""
```

**Result:**
- Generated Python script with database queries
- Automatic calculation logic
- Terminal output with formatted results
- Execution time: ~5 seconds

---

### Example 2: Interactive Web Dashboard

```python
user_request = """
Calculate cap rates for all properties and create a website to display results 
with simulation capabilities for different scenarios.
"""
```

**Result:**
- Generated Flask web application
- Interactive dashboard at `http://localhost:8080`
- Pre-calculated results displayed
- Simulation form for what-if analysis
- Execution time: ~8 seconds

---

### Example 3: Financial Analysis with Ranking

```python
user_request = """
Rank all properties by their cap rate from highest to lowest. 
Show me the top performers and identify any properties below 5% cap rate.
"""
```

**Result:**
- Database query with JOIN operations
- Sorting and filtering logic
- Formatted output with rankings
- Highlighted underperformers

---

### Example 4: Complex Multi-Metric Analysis

```python
user_request = """
Analyze property performance by calculating DSCR, Cap Rate, and Cash-on-Cash return. 
Create a comprehensive dashboard showing all metrics with drill-down capabilities.
"""
```

**Result:**
- Multi-table database queries
- Multiple calculation engines
- Interactive web dashboard
- Exportable reports

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Core scripting language |
| **LLM** | Qwen2.5-Coder-7B (via LM Studio) | Code generation |
| **Containerization** | Docker + Docker Compose | Isolated execution |
| **Database** | PostgreSQL + psycopg2 | Data persistence |
| **Web Framework** | Flask | Generated web interfaces |
| **Validation** | Pydantic + AST | Data & code validation |
| **Logging** | Loguru | Structured logging |

### Python Libraries

```
pydantic>=2.0.0          # Data validation
loguru>=0.7.0            # Logging
psycopg2-binary>=2.9.0   # PostgreSQL
langchain-openai         # LLM client adapter
httpx                    # HTTP client
flask>=3.0.0            # Web framework (generated)
```

---

## ⚙️ Configuration

### Environment Variables

#### LM Studio Configuration
```bash
LLM_BASE_URL=http://localhost:1234/v1       # LM Studio API endpoint
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx  # Model identifier
LLM_API_KEY=lm-studio                       # Placeholder key
LLM_TEMPERATURE=0.1                         # Generation temperature (0.0-1.0)
LLM_MAX_TOKENS=4096                         # Max tokens per response
LLM_CONTEXT_LENGTH=8192                     # Context window size
```

#### Database Configuration
```bash
DATABASE_URL=postgresql://user:password@host:port/database
# Format: postgresql://[user]:[password]@[host]:[port]/[database]
```

#### Meta-Agent Settings
```bash
META_AGENT_STRICT_MODE=true                 # Enable strict validation
DOCKER_TIMEOUT=30                           # Container timeout (seconds)
SANDBOX_MEMORY_LIMIT=512m                   # Memory limit per container
SANDBOX_CPU_LIMIT=1.0                       # CPU limit per container
```

---

## 📁 Project Structure

```
AgenticPOC_Meta/
├── script_executor.py              # Main entry point
├── config.py                       # Configuration management
├── setup_env.sh                    # Environment setup script
├── requirements.txt                # Python dependencies
│
├── meta_agent/                     # Core Meta-Agent modules
│   ├── analyzers/
│   │   └── task_analyzer.py       # Task understanding & analysis
│   ├── planners/
│   │   └── execution_planner.py   # Execution strategy design
│   ├── generators/
│   │   ├── script_generator.py    # Python code generation
│   │   └── dockerfile_generator.py # Docker file generation
│   ├── validators/
│   │   └── script_validator.py    # Multi-layer validation
│   ├── executors/
│   │   └── container_executor.py  # Docker container management
│   └── utils/
│       ├── llm_client.py          # LLM communication
│       ├── database_inspector.py  # Schema discovery
│       └── archive_manager.py     # Cleanup utilities
│
├── generated_scripts/              # Generated script outputs (gitignored)
│   └── script_YYYYMMDD_HHMMSS/
│       ├── script.py              # Generated Python script
│       ├── requirements.txt       # Script dependencies
│       ├── Dockerfile             # Container definition
│       ├── docker-compose.yml     # Container orchestration
│       ├── deploy.sh              # Deployment script
│       ├── .env                   # Environment config
│       ├── README.md              # Usage instructions
│       ├── results/               # Execution outputs
│       ├── logs/                  # Application logs
│       └── exports/               # Reports & data
│
├── Docs/                          # Documentation
│   ├── TECHNICAL_DOCUMENTATION.md
│   ├── BACKEND_WORKFLOW_TECHNICAL.md
│   └── COMPLETE_WORKFLOW_EXAMPLE.md
│
└── logs/                          # System logs (gitignored)
```

---

## 📊 Performance

### Benchmarks

| Task Type | Execution Time | Lines of Code | Memory Usage |
|-----------|---------------|---------------|--------------|
| Simple calculation | 2-5 sec | 50-100 | 128 MB |
| Database query + calculation | 5-8 sec | 100-150 | 256 MB |
| Web interface generation | 8-12 sec | 150-250 | 512 MB |
| Complex multi-metric analysis | 15-30 sec | 250-400 | 512 MB |

### Comparison: Agent Factory vs. Script Executor

| Metric | Agent Factory | Script Executor | Improvement |
|--------|--------------|-----------------|-------------|
| **Time to Results** | 13 minutes | 8 seconds | **97% faster** |
| **Steps** | 10 | 7 | 30% fewer |
| **Output** | Persistent agents | Task results | Task-optimized |
| **Web UI** | Manual setup | Auto-generated | Automated |
| **Cleanup** | Manual | Automatic | Simplified |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. LM Studio Connection Error

**Symptom:**
```
ConnectionError: Cannot connect to LM Studio at http://localhost:1234
```

**Solution:**
- Ensure LM Studio is running
- Verify model `qwen2.5-coder-7b-instruct-mlx` is loaded
- Check Local Server is started (port 1234)
- Verify `LLM_BASE_URL` in `.env`

---

#### 2. Database Connection Failed

**Symptom:**
```
ERROR: connection to server at "localhost", port 5432 failed
```

**Solution:**
- Check PostgreSQL is running: `pg_isready`
- Verify `DATABASE_URL` in `.env`
- For Docker containers, use `host.docker.internal` instead of `localhost`
- Check database credentials and permissions

---

#### 3. Docker Container Failed

**Symptom:**
```
Container deployment failed: Exited (1)
```

**Solution:**
```bash
# Check container logs
docker logs <container_name>

# Verify Docker is running
docker info

# Check port availability
lsof -i :8080

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop
```

---

#### 4. Generated Script Syntax Error

**Symptom:**
```
SyntaxError: invalid syntax in generated script
```

**Solution:**
- Auto-retry mechanism will attempt to fix (up to 3 attempts)
- Check LLM temperature (lower = more conservative)
- Review `script.py` in generated directory
- Increase `LLM_MAX_TOKENS` if code is truncated

---

#### 5. Empty Results Display

**Symptom:**
```
📊 RESULTS
============================================================
============================================================
```

**Solution:**
- Check container logs: `docker logs <container_name>`
- Verify `DATABASE_URL` is correctly set in generated `.env`
- Wait a few seconds for container to process
- Check script execution succeeded: `docker ps -a`

---

### Debug Commands

```bash
# Check LM Studio connectivity
curl http://localhost:1234/v1/models

# View container logs
docker logs <container_name>

# Check container status
docker ps -a --filter "name=script_"

# Inspect generated script
cat generated_scripts/script_<timestamp>/script.py

# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# View execution results
cat generated_scripts/script_<timestamp>/logs/app.log
```

---

## 📚 Documentation

### Comprehensive Guides

- **[Technical Documentation](Docs/TECHNICAL_DOCUMENTATION.md)** - Architecture, components, and design decisions
- **[Backend Workflow](Docs/BACKEND_WORKFLOW_TECHNICAL.md)** - Step-by-step backend process with examples
- **[Complete Workflow Example](Docs/COMPLETE_WORKFLOW_EXAMPLE.md)** - Real-world example from start to finish

### Quick References

- **[Script Validation](meta_agent/validators/script_validator.py)** - How validation works
- **[Database Inspector](meta_agent/utils/database_inspector.py)** - Schema discovery logic
- **[LLM Client](meta_agent/utils/llm_client.py)** - LM Studio integration

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/AgenticPOC_Meta.git
cd AgenticPOC_Meta

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python script_executor.py

# Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name

# Create Pull Request
```

### Areas for Contribution

- **🔌 New Integrations:** MySQL, MongoDB, Redis support
- **📊 Visualization:** Chart generation, advanced dashboards
- **🧪 Testing:** Unit tests, integration tests
- **📝 Documentation:** Tutorials, examples, translations
- **🐛 Bug Fixes:** Report and fix issues
- **⚡ Performance:** Optimization and caching

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include comments for complex logic
- Write descriptive commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LM Studio** for local LLM infrastructure
- **Qwen2.5-Coder** for code generation capabilities
- **Docker** for containerization
- **PostgreSQL** for reliable data storage

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/your-username/AgenticPOC_Meta/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/AgenticPOC_Meta/discussions)
- **Documentation:** [Docs](Docs/)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Transform natural language into executable scripts in seconds!** 🚀

[Get Started](#-quick-start) · [View Documentation](Docs/) · [Report Bug](https://github.com/your-username/AgenticPOC_Meta/issues)

</div>
