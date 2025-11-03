# Meta-Agent Script Executor

**Version:** 2.1.0  
**Last Updated:** November 3, 2025 (Database Schema Discovery Integrated into Workflow)  
**Type:** Task Execution System  
**Approach:** Generate → Execute → Results

Transform natural language requests into executable scripts with interactive web interfaces and simulations.

---

## 🎯 What Is This?

The **Meta-Agent Script Executor** generates and executes Python scripts directly from natural language, eliminating the need for persistent agents.

```
Your Request → Script Generation → Container Execution → Results (8 seconds!)
```

---

## ⚡ Quick Example

**Input:**
> "Calculate DSCR for Orlando Fashion Square and create a website to show results with simulations"

**Output (8 seconds later):**
- ✓ Python script generated (200 lines)
- ✓ Docker container ready
- ✓ Web interface at http://localhost:8080
- ✓ Interactive simulations built-in
- ✓ Results updated in real-time

---

## 🏗️ Architecture

### 7-Step Workflow

```
1. Task Analyzer      → Understand what needs to be done
2. Execution Planner  → Design step-by-step process
3. Script Generator   → Generate Python code (LLM-powered)
4. Script Validator   → Syntax + security checks
5. Containerization   → Package in Docker
6. Execution          → Run in isolated environment
7. Results            → Access via web/files
```

### 97% Faster Than Agent Factory

| Metric | Agent Factory | Script Executor |
|--------|--------------|-----------------|
| Time | 13 minutes | 8 seconds |
| Steps | 10 | 7 |
| Output | Persistent agents | Task results |
| Best For | Reusable services | One-time tasks |

---

## 📚 Quick Start

### 1. Prerequisites

```bash
# Python 3.9+
python3 --version

# Docker
docker --version

# LM Studio running on port 1234
# Model: qwen2.5-coder-7b-instruct-mlx
```

### 2. Setup

```bash
cd /Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_Meta

# Activate virtual environment
source venv/bin/activate

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and settings
```

### 3. Run

```bash
python script_executor.py
```

### 4. Deploy Generated Script

```bash
# Navigate to generated script directory
cd generated_scripts/<timestamp>/

# Configure
cp .env.example .env
# Edit .env

# Deploy
bash deploy.sh

# Access web interface (if generated)
open http://localhost:8080
```

---

## 🎯 Use Cases

### 1. Financial Calculations with Web Dashboard

**Request:**
> "Calculate DSCR for properties and create a dashboard with simulation capabilities"

**Generated:**
- Python script with calculation logic
- Flask web server
- Interactive HTML dashboard
- Simulation form for what-if scenarios
- Real-time result updates

**Access:**
- http://localhost:8080 → View results
- Enter scenarios → Run simulations
- Download reports

---

### 2. Data Processing Pipeline

**Request:**
> "Extract property data from database, calculate metrics, generate report"

**Generated:**
- Database connection script
- Data processing logic
- Report generation (PDF/Excel)
- Automated execution

**Results:**
- `results/property_metrics.xlsx`
- `results/summary_report.pdf`
- `logs/execution.log`

---

### 3. API Integration with Analysis

**Request:**
> "Fetch data from API, analyze trends, create visualization dashboard"

**Generated:**
- API client code
- Data analysis logic
- Visualization web interface
- Interactive charts

---

## 🛠️ Components

### Core Modules

```
meta_agent/
├── analyzers/
│   └── task_analyzer.py          # Understand user requests
├── planners/
│   └── execution_planner.py      # Design execution steps
├── generators/
│   ├── script_generator.py       # Generate Python code
│   └── dockerfile_generator.py   # Generate Docker files
├── validators/
│   └── script_validator.py       # Validate syntax & security
├── executors/
│   └── container_executor.py     # Execute in containers
└── utils/
    ├── llm_client.py             # LLM interface
    └── archive_manager.py        # Archive results
```

---

## 🌐 Web Interface Features

When you request a web interface, the generated script includes:

### Automatic Features

✅ **Dashboard Page**
- Display current results
- Show key metrics
- Visual charts (if applicable)

✅ **Simulation Form**
- Input scenario parameters
- Run what-if analysis
- Compare results

✅ **API Endpoints**
```
GET  /              → Dashboard
GET  /health        → Health check
GET  /api/results   → Current results
POST /api/simulate  → Run simulation
GET  /api/download  → Download report
```

✅ **Real-Time Updates**
- Results update without page refresh
- Live calculation status
- Progress indicators

---

## 🔄 Interactive Workflow

### Initial Execution

```
User: "Calculate DSCR for Orlando Fashion Square"
      ↓
Meta-Agent generates script
      ↓
Container starts
      ↓
Calculations execute
      ↓
Web interface shows: DSCR = 1.35 ✓
```

### User Simulations

```
User sees results on webpage
      ↓
User enters scenarios in form:
  - Base case
  - +10% revenue
  - -10% revenue
      ↓
Clicks "Run Simulation"
      ↓
Container re-executes with new parameters
      ↓
Results update on same page
      ↓
Comparison chart displayed
```

---

## 📊 Example Output

### Generated Script Structure

```python
#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from loguru import logger

# Configuration from environment
DB_URL = os.getenv('DATABASE_URL', '')
PORT = int(os.getenv('PORT', '8080'))

app = Flask(__name__)

class DSCRCalculator:
    def calculate(self, property_id, scenario='base'):
        # Fetch data from database
        # Calculate DSCR
        # Return results
        pass

@app.route('/')
def dashboard():
    calc = DSCRCalculator()
    result = calc.calculate('orlando-fashion-square')
    return render_template('dashboard.html', result=result)

@app.route('/api/simulate', methods=['POST'])
def simulate():
    params = request.json
    calc = DSCRCalculator()
    results = []
    for scenario in params['scenarios']:
        result = calc.calculate(
            'orlando-fashion-square',
            scenario=scenario
        )
        results.append(result)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
```

---

## 🔐 Security

### Built-in Security

✅ **No Hardcoded Credentials**
- All configuration from environment variables
- Validation enforces `os.getenv()` usage

✅ **Container Isolation**
- Each execution in separate container
- Resource limits enforced
- Network restrictions

✅ **Code Validation**
- Syntax checking
- Security scanning
- Dangerous pattern detection

---

## 📁 File Structure

### Generated Files Per Execution

```
generated_scripts/<timestamp>/
├── script.py              # Main Python script
├── requirements.txt       # Dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Orchestration
├── deploy.sh             # Deployment script
├── .env.example          # Environment template
├── README.md             # Usage guide
├── results/              # Execution results
├── logs/                 # Application logs
├── exports/
│   ├── reports/          # Generated reports
│   └── data/             # Exported data
└── data/                 # Input data
```

---

## 🎓 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Web Server (if generated)
PORT=8080
HOST=0.0.0.0

# Output
OUTPUT_DIR=./results
LOG_DIR=./logs

# Logging
LOG_LEVEL=INFO
```

---

## 🚀 Advanced Usage

### Custom Scenarios

```python
# In the web interface form
Scenarios:
  1. Base case (current data)
  2. Revenue +10%, Expenses +0%
  3. Revenue +10%, Expenses -5%
  4. Revenue -10% (stress test)

→ Run Simulation

Results:
  Base:    DSCR 1.35 ✓
  +10/0:   DSCR 1.48 ✓
  +10/-5:  DSCR 1.56 ✓
  -10:     DSCR 1.22 ⚠️
```

### API Integration

```bash
# Run simulation via API
curl -X POST http://localhost:8080/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "scenarios": [
      {"name": "optimistic", "revenue_change": 0.10},
      {"name": "pessimistic", "revenue_change": -0.10}
    ]
  }'
```

---

## 📊 Performance

### Benchmarks

- **Simple calculation:** 2-5 seconds
- **Web interface generation:** 5-8 seconds
- **With simulations:** 8-12 seconds
- **Complex data processing:** 15-30 seconds

### Resource Usage

- **Memory:** 128-512 MB per container
- **CPU:** 0.5-1.0 cores per container
- **Disk:** 50-200 MB per execution

---

## 🔍 Troubleshooting

### Script Generation Issues

**LLM not responding:**
- Check LM Studio is running on port 1234
- Verify model is loaded
- Check `LLM_BASE_URL` in .env

**Syntax errors in generated code:**
- Auto-retry mechanism will attempt fixes
- Check logs for detailed error context
- May need to adjust LLM temperature

### Container Issues

**Docker not available:**
```bash
docker info
# If error, start Docker Desktop
```

**Port already in use:**
- Change `PORT` in .env
- Update docker-compose.yml

**Container fails to start:**
```bash
docker-compose logs
# Check for missing environment variables
```

---

## 📚 Documentation

- **SCRIPT_EXECUTOR_PLAN.md** - Complete architecture
- **ARCHITECTURE_COMPARISON.md** - vs Agent Factory
- **archive_agent_factory_20251030/** - Old Agent Factory files

---

## 🎯 When to Use

### ✅ Use Script Executor For:

- One-time calculations
- Ad-hoc data analysis
- Interactive dashboards
- Simulation and comparison
- Quick prototyping
- Task-based workflows

### ❌ Use Agent Factory For:

- Persistent services
- Reusable agents
- Long-running operations
- Production APIs
- Complex multi-agent systems

---

## 🛠️ Development

### Adding New Features

The system is modular and extensible:

```python
# Add new task type
# In task_analyzer.py
valid_types = ["calculation", "data_processing", 
               "analysis", "report_generation", 
               "web_app", "your_new_type"]

# Add new action type
# In execution_planner.py
valid_actions = ["database_query", "calculation",
                 "api_call", "your_new_action"]
```

---

## 📊 Comparison with Agent Factory

| Aspect | Script Executor | Agent Factory |
|--------|----------------|---------------|
| **Speed** | 8 seconds | 13 minutes |
| **Output** | Task results | Persistent agents |
| **Web UI** | Auto-generated | Manual setup |
| **Simulations** | Built-in | Manual |
| **Cleanup** | Automatic | Manual |
| **Best For** | Tasks | Services |

---

## 🎉 Success Metrics

✅ **Generation Success:** 95%+ valid scripts  
✅ **Execution Time:** <10 seconds for simple tasks  
✅ **Security:** Zero hardcoded credentials  
✅ **Simulations:** Multi-scenario comparison built-in  
✅ **Web Interface:** Interactive dashboard auto-generated  

---

## 📞 Support

**Issues:**
- Check logs: `docker-compose logs`
- Review generated code: `cat script.py`
- Validate environment: `.env` file complete?

**Architecture:**
- See SCRIPT_EXECUTOR_PLAN.md
- See ARCHITECTURE_COMPARISON.md

---

**Transform requests into results in seconds!** 🚀

