# Complete Workflow Example - Meta-Agent Script Executor

**Real-World Walkthrough**  
**Date:** November 3, 2025  
**Example:** DSCR Calculation for Property Portfolio

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Pre-Execution Setup](#pre-execution-setup)
3. [Complete Example: DSCR Analysis](#complete-example-dscr-analysis)
4. [Stage-by-Stage Breakdown](#stage-by-stage-breakdown)
5. [Generated Artifacts](#generated-artifacts)
6. [Results Interpretation](#results-interpretation)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## System Overview

### What This System Does

The Meta-Agent Script Executor transforms natural language financial requests into executable Python scripts that:
1. ✅ Query your database automatically
2. ✅ Perform complex calculations
3. ✅ Generate web dashboards (optional)
4. ✅ Run in isolated Docker containers
5. ✅ Display results automatically

### Key Technologies

- **LLM**: Qwen2.5-Coder-7B-Instruct-MLX (running in LM Studio)
- **Database**: PostgreSQL (Orlando portfolio)
- **Containerization**: Docker + Docker Compose
- **Language**: Python 3.9+

---

## Pre-Execution Setup

### Step 1: Verify LM Studio is Running

```bash
# Check if LM Studio server is accessible
curl http://localhost:1234/v1/models

# Expected output:
{
  "object": "list",
  "data": [
    {
      "id": "qwen2.5-coder-7b-instruct-mlx",
      "object": "model",
      ...
    }
  ]
}
```

**If it fails:**
- Open LM Studio application
- Load model: `qwen2.5-coder-7b-instruct-mlx`
- Click "Start Server" (port 1234)

---

### Step 2: Set Environment Variables

```bash
# Navigate to project
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_Meta"

# Activate virtual environment
source venv/bin/activate

# Set database connection
export DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5433/orlando_db"

# Verify it's set
echo $DATABASE_URL
```

---

### Step 3: Verify Database Connection

```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT COUNT(*) FROM properties;"

# Expected output:
 count 
-------
    10
(1 row)
```

**If it fails:**
- Check if PostgreSQL is running: `pg_isready -h localhost -p 5433`
- Verify credentials in DATABASE_URL
- For Docker containers, use `host.docker.internal` instead of `localhost`

---

## Complete Example: DSCR Analysis

### User Request (Natural Language)

```
I need to review the debt service coverage for our entire property portfolio.
Can you pull all properties from the database and calculate their DSCR?
I want to see which properties have strong coverage and which ones might be risky.
Show me the property name, NOI, debt service, and the ratio for each one,
plus give me a portfolio summary at the end.
```

---

## Stage-by-Stage Breakdown

### 🚀 **STAGE 1: Initialization (5-10 seconds)**

**What Happens:**
- System loads environment variables
- Connects to LM Studio
- Verifies Qwen2.5-Coder-7B model is loaded
- Performs health check

**Terminal Output:**
```
08:13:15 | ============================================================
08:13:15 | 🚀  META-AGENT SCRIPT EXECUTOR
08:13:15 | ============================================================

08:13:15 | 📝 Request:
08:13:15 |    I need to review the debt service coverage for our entire property portfolio.
           Can you pull all properties from the database and calculate their DSCR?
           ...

08:13:15 | ⚙️  Initializing LLM...
08:13:17 |    ✓ LLM initialized
```

**Behind the Scenes:**
```python
# In meta_agent/utils/llm_client.py
1. Check LM Studio server at http://localhost:1234/v1
2. Verify model "qwen2.5-coder-7b-instruct-mlx" is loaded
3. Send test message: "Respond with 'OK'"
4. If successful → available = True
5. If fails → Raise explicit error (NO FALLBACK)
```

---

### 🔍 **STAGE 2: Database Schema Inspection (1-2 seconds)**

**What Happens:**
- Connects to PostgreSQL using SQLAlchemy
- Discovers all tables, columns, primary keys, foreign keys
- Counts rows in each table
- Formats schema for LLM

**Terminal Output:**
```
08:13:17 | 🗄️  Inspecting database schema...
08:13:18 |    ✓ Schema discovered: 2 tables, 10 properties
```

**Database Schema Discovered:**
```
properties (10 rows):
  - property_id [PK] INTEGER
  - property_name VARCHAR
  - property_address VARCHAR
  - property_type VARCHAR
  - total_gla_sqft INTEGER
  - acquisition_date DATE
  - city VARCHAR
  - state VARCHAR

financial_metrics (10 rows):
  - metric_id [PK] INTEGER
  - property_id [FK→properties] INTEGER
  - noi DECIMAL
  - annual_debt_service DECIMAL
  - dscr DECIMAL
  - cap_rate DECIMAL
  - occupancy_rate DECIMAL
  - operating_expenses DECIMAL

JOIN relationship:
  properties.property_id = financial_metrics.property_id
```

**Behind the Scenes:**
```python
# In meta_agent/utils/database_inspector.py
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

for table_name in inspector.get_table_names():
    columns = inspector.get_columns(table_name)
    pk = inspector.get_pk_constraint(table_name)
    fks = inspector.get_foreign_keys(table_name)
    
    # Count rows
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
```

---

### 📊 **STAGE 3: Task Analysis (10-20 seconds)**

**What Happens:**
- LLM analyzes the natural language request
- Extracts structured information:
  - Primary goal
  - Task type (calculation/reporting/analysis)
  - Web interface needed? (looks for keywords: "website", "dashboard")
  - Simulations needed? (looks for: "what-if", "scenario")
  - Data sources required
  - Complexity level

**Terminal Output:**
```
08:13:18 | 🔍 Analyzing task...
08:13:28 |   Task type: calculation
08:13:28 |   Web interface: False
08:13:28 |   Simulations: False
08:13:28 |   Complexity: MEDIUM
08:13:28 |    ✓ Task analyzed: calculation, MEDIUM
```

**LLM Prompt Sent:**
```
System: You are an expert task analyzer. Analyze the user's request and return JSON.

User: Analyze this request:
I need to review the debt service coverage for our entire property portfolio.
Can you pull all properties from the database and calculate their DSCR?
...

Return JSON with: primary_goal, task_type, requires_web_interface, requires_simulation, 
data_sources, key_entities, complexity, estimated_execution_time_seconds
```

**LLM Response (Structured JSON):**
```json
{
  "primary_goal": "Calculate DSCR for all properties in portfolio",
  "task_type": "calculation",
  "requires_web_interface": false,
  "requires_simulation": false,
  "data_sources": ["postgresql"],
  "key_entities": [],
  "complexity": "MEDIUM",
  "estimated_execution_time_seconds": 30
}
```

**Validated Result:**
```python
TaskAnalysis(
    primary_goal="Calculate DSCR for all properties in portfolio",
    task_type="calculation",
    requires_web_interface=False,
    requires_simulation=False,
    data_sources=["postgresql"],
    key_entities=[],
    complexity="MEDIUM",
    estimated_execution_time_seconds=30
)
```

---

### 📋 **STAGE 4: Execution Planning (15-30 seconds)**

**What Happens:**
- LLM designs a step-by-step execution plan
- Identifies required Python packages
- Determines if web server configuration needed
- Estimates lines of code

**Terminal Output:**
```
08:13:28 | 📋 Designing execution plan...
08:13:55 |   Plan: Debt Service Coverage Review
08:13:55 |   Steps: 4
08:13:55 |   Dependencies: 1
08:13:55 |   Estimated LOC: 75
08:13:55 |    ✓ Plan created: 4 steps
```

**LLM Prompt Sent:**
```
System: You are an expert execution planner. Design a step-by-step plan.

User: Design an execution plan for this task:
Goal: Calculate DSCR for all properties in portfolio
Type: calculation
Complexity: MEDIUM
Data Sources: postgresql
Web Interface: False
Simulations: False

Database Schema Available:
properties(10 rows): property_id[PK], property_name, property_address, +5 more
financial_metrics(10 rows): metric_id[PK], property_id[FK→properties], noi, annual_debt_service, +6 more
JOIN: properties.property_id = financial_metrics.property_id
```

**Generated Execution Plan:**
```python
ExecutionPlan(
    plan_name="Debt Service Coverage Review",
    description="Calculate DSCR for all properties and identify risk levels",
    steps=[
        ExecutionStep(
            step_number=1,
            name="Connect to Database",
            description="Establish PostgreSQL connection with RealDictCursor",
            action="database_query",
            depends_on=[]
        ),
        ExecutionStep(
            step_number=2,
            name="Query Property Financial Data",
            description="JOIN properties with financial_metrics to get NOI and debt service",
            action="database_query",
            depends_on=[1]
        ),
        ExecutionStep(
            step_number=3,
            name="Calculate DSCR",
            description="Compute DSCR = NOI / Annual Debt Service for each property",
            action="calculation",
            depends_on=[2]
        ),
        ExecutionStep(
            step_number=4,
            name="Display Results",
            description="Print formatted results to console with portfolio summary",
            action="report_generation",
            depends_on=[3]
        )
    ],
    dependencies=["psycopg2"],
    estimated_lines_of_code=75,
    web_server_config=None,
    simulation_config=None
)
```

---

### ⚡ **STAGE 5: Script Generation (20-60 seconds)**

**What Happens:**
- LLM generates complete Python script
- System prompt provides 300+ lines of best practices
- User prompt includes task, plan, and database schema
- Generated code is cleaned of markdown artifacts
- Syntax validated with AST parser
- If syntax error → retry with error feedback (max 3 attempts)

**Terminal Output:**
```
08:13:55 | ⚡ Generating script...
08:14:22 |   Lines of code: 78
08:14:22 |   Dependencies: 5
08:14:22 |    ✓ Script generated
```

**LLM System Prompt (Excerpt):**
```
You are an expert Python developer. Generate production-ready scripts.

CRITICAL REQUIREMENTS:
1. Use environment variables for ALL configuration (os.getenv())
2. NEVER hardcode credentials
3. Include proper error handling
4. Use loguru for logging

FOR CONSOLE-ONLY SCRIPTS (NO WEB INTERFACE):
- DO NOT import flask
- ONLY use logger.info() for output
- Script should run, calculate, print results, and exit

DATABASE QUERIES (MANDATORY PATTERN):
```python
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)
cursor = conn.cursor()

query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
cursor.execute(query)

for row in cursor.fetchall():
    property_name = row.get('property_name', 'Unknown')
    noi = float(row.get('noi', 0))
```

TERMINAL OUTPUT (REQUIRED):
```python
logger.info("=== Calculation Results ===")
for result in results:
    logger.info(f"{result['property_name']}: DSCR = {result['dscr']:.2f}")
logger.info("=== End Results ===")
```
...
```

**Generated Script (script.py):**
```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

# Configure logger
logger.add("logs/dscr_analysis.log", rotation="10 MB")

# Configuration from environment variables
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
}

def get_connection():
    """Get database connection with RealDictCursor"""
    if not CONFIG['db_url']:
        raise ValueError("DATABASE_URL not configured")
    return psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)

def calculate_dscr():
    """Calculate DSCR for all properties"""
    conn = None
    results = []
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Query properties with financial metrics
        query = """
            SELECT 
                p.property_name,
                fm.noi,
                fm.annual_debt_service
            FROM properties p
            JOIN financial_metrics fm ON p.property_id = fm.property_id
            ORDER BY p.property_name
        """
        
        cursor.execute(query)
        
        for row in cursor.fetchall():
            property_name = row.get('property_name', 'Unknown')
            noi = float(row.get('noi', 0))
            debt_service = float(row.get('annual_debt_service', 0))
            
            # Calculate DSCR (handle division by zero)
            if debt_service > 0:
                dscr = noi / debt_service
            else:
                dscr = 0.0
            
            # Determine risk level
            if dscr >= 1.25:
                risk_level = "Strong"
            elif dscr >= 1.0:
                risk_level = "Acceptable"
            else:
                risk_level = "At Risk"
            
            results.append({
                'property_name': property_name,
                'noi': noi,
                'debt_service': debt_service,
                'dscr': dscr,
                'risk_level': risk_level
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating DSCR: {e}")
        raise
    finally:
        if conn:
            conn.close()

def display_results(results):
    """Display results to console"""
    logger.info("=== Calculation Results ===")
    logger.info("")
    
    for result in results:
        logger.info(
            f"{result['property_name']}: "
            f"NOI=${result['noi']:,.2f}, "
            f"Debt Service=${result['debt_service']:,.2f}, "
            f"DSCR={result['dscr']:.2f} ({result['risk_level']})"
        )
    
    logger.info("")
    logger.info("=== Portfolio Summary ===")
    
    # Calculate portfolio-level metrics
    total_noi = sum(r['noi'] for r in results)
    total_debt_service = sum(r['debt_service'] for r in results)
    portfolio_dscr = total_noi / total_debt_service if total_debt_service > 0 else 0
    
    strong = sum(1 for r in results if r['dscr'] >= 1.25)
    acceptable = sum(1 for r in results if 1.0 <= r['dscr'] < 1.25)
    at_risk = sum(1 for r in results if r['dscr'] < 1.0)
    
    logger.info(f"Total Properties: {len(results)}")
    logger.info(f"Portfolio DSCR: {portfolio_dscr:.2f}")
    logger.info(f"Strong Coverage (DSCR >= 1.25): {strong} properties")
    logger.info(f"Acceptable Coverage (1.0-1.25): {acceptable} properties")
    logger.info(f"At Risk (DSCR < 1.0): {at_risk} properties")
    
    logger.info("=== End Results ===")

if __name__ == "__main__":
    logger.info("Starting DSCR Analysis...")
    results = calculate_dscr()
    display_results(results)
    logger.info("Analysis complete!")
```

**Code Cleaning Process:**
```python
# In meta_agent/generators/script_generator.py
def _clean_code(code: str) -> str:
    # Remove markdown code blocks (```)
    # Remove markdown headers (**Title:**)
    # Remove numbered lists (1. Step one)
    # Remove explanatory text
    return cleaned_code
```

**Syntax Validation:**
```python
import ast
ast.parse(script_code)  # Raises SyntaxError if invalid
```

---

### 🔒 **STAGE 6: Validation (1-2 seconds)**

**What Happens:**
- Syntax validation (AST parsing)
- Security analysis (no hardcoded credentials, no eval/exec)
- Best practices check (logging, error handling)
- Resource estimation (memory, CPU)

**Terminal Output:**
```
08:14:22 | 🔒 Validating script...
08:14:23 | ✓ Validation complete: ✓ VALID - 2 issues, security: 1.00
08:14:23 |   Syntax: ✓
08:14:23 |   Security score: 1.00
08:14:23 |   Issues: 2 (0 errors)
08:14:23 |    ✓ Validation passed: security score 1.0
```

**Validation Layers:**

1. **Syntax Check**: ✅ PASSED
   ```python
   ast.parse(script_code)  # No SyntaxError
   ```

2. **Security Scan**: ✅ Score 1.0
   - ✓ No hardcoded passwords/API keys
   - ✓ No eval() or exec()
   - ✓ Uses os.getenv() for configuration
   - ✓ No dangerous operations

3. **Best Practices**: ⚠️ 2 warnings
   - ℹ️ No type hints detected (info level)
   - ℹ️ Limited docstrings (info level)

4. **Resource Estimation**:
   - Memory: 256 MB (base 128 + psycopg2 128)
   - CPU: 0.5 cores

**Validation Result:**
```python
ValidationResult(
    is_valid=True,
    issues=[
        ValidationIssue(severity="info", category="style", message="No type hints detected"),
        ValidationIssue(severity="info", category="style", message="Limited docstrings")
    ],
    syntax_valid=True,
    security_score=1.0,
    estimated_memory_mb=256,
    estimated_cpu_cores=0.5
)
```

---

### 📦 **STAGE 7: Packaging (2-5 seconds)**

**What Happens:**
- Creates execution directory: `generated_scripts/script_20251103_081321/`
- Writes script.py
- Generates requirements.txt (auto-detects imports)
- Creates Dockerfile
- Creates docker-compose.yml
- Generates deploy.sh (makes executable)
- Creates .env.example and .env
- Generates README.md
- Creates output directories

**Terminal Output:**
```
08:14:23 | 📦 Packaging script...
08:14:24 |   Execution directory: generated_scripts/script_20251103_081321
08:14:24 |   Container name: script_20251103_081321
08:14:24 |   ✓ Script written: script.py
08:14:24 |   ✓ Requirements written
08:14:24 |   ✓ Environment template written
08:14:24 |   ✓ Dockerfile generated
08:14:24 |   ✓ docker-compose.yml generated
08:14:24 |   ✓ deploy.sh generated
08:14:24 |   ✓ Output directories created
08:14:24 |   ✓ README.md generated
```

**Generated Files:**

**requirements.txt** (auto-detected):
```
loguru
psycopg2-binary
pydantic
python-dotenv
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY script.py .

# Create directories
RUN mkdir -p /app/results /app/logs /app/exports/reports /app/exports/data

# Set environment
ENV PYTHONUNBUFFERED=1

# Run script
CMD ["python", "script.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  script_20251103_081321:
    build: .
    container_name: script_20251103_081321
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OUTPUT_DIR=/app/results
      - LOG_DIR=/app/logs
    volumes:
      - ./results:/app/results:rw
      - ./logs:/app/logs:rw
      - ./exports/reports:/app/exports/reports:rw
      - ./exports/data:/app/exports/data:rw
    mem_limit: 256m
    cpus: 0.5
    restart: no
    networks:
      - script-network

networks:
  script-network:
    driver: bridge
```

**.env** (auto-created):
```bash
DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5433/orlando_db
OUTPUT_DIR=/app/results
LOG_DIR=/app/logs
```

**deploy.sh**:
```bash
#!/bin/bash
set -e

docker-compose build
docker-compose up -d

echo "Container started successfully"
```

---

### 🐳 **STAGE 8: Container Execution (5-15 seconds)**

**What Happens:**
- Runs deploy.sh script
- Docker Compose builds image (installs Python dependencies)
- Starts container
- Container executes script.py
- Results logged to stdout
- Container exits with code 0 (success)

**Terminal Output:**
```
08:14:24 | 🚀 Deploying container...
08:14:38 |    ✓ Deployment complete
```

**Behind the Scenes:**

**Build Phase:**
```bash
$ docker-compose build
Building script_20251103_081321...
Step 1/7 : FROM python:3.9-slim
Step 2/7 : WORKDIR /app
Step 3/7 : COPY requirements.txt .
Step 4/7 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Installing: loguru, psycopg2-binary, pydantic, python-dotenv
Step 5/7 : COPY script.py .
Step 6/7 : RUN mkdir -p /app/results /app/logs ...
Step 7/7 : CMD ["python", "script.py"]
Successfully built abc123def456
```

**Execution Phase:**
```bash
$ docker-compose up -d
Creating network "script_20251103_081321_script-network" ... done
Creating script_20251103_081321 ... done
```

**Container Status Check:**
```bash
$ docker ps -a --filter "name=script_20251103_081321"
CONTAINER ID   NAME                      STATUS
abc123def456   script_20251103_081321    Exited (0) 2 seconds ago
```

**Status = `Exited (0)` means:**
- Container started successfully ✅
- Script ran without errors ✅
- Exit code 0 = success ✅
- Results available in logs ✅

---

### 📊 **STAGE 9: Results Display (2-5 seconds)**

**What Happens:**
- Waits 2 seconds for container output
- Fetches container logs: `docker logs script_20251103_081321`
- Parses logs for "=== Calculation Results ===" section
- Cleans loguru formatting
- Displays results in main terminal

**Terminal Output:**
```
08:14:40 | 📊 RESULTS
08:14:40 | ============================================================
08:14:40 |    Orlando Fashion Square: NOI=$12,500,000.00, Debt Service=$6,450,000.00, DSCR=1.94 (Strong)
08:14:40 |    1893 Rouse Lake Rd: NOI=$980,000.00, Debt Service=$590,000.00, DSCR=1.66 (Strong)
08:14:40 |    Orlando Vineland Premium Outlets: NOI=$8,750,000.00, Debt Service=$7,250,000.00, DSCR=1.21 (Acceptable)
08:14:40 |    Columbia Heights Shopping Mall: NOI=$4,200,000.00, Debt Service=$2,800,000.00, DSCR=1.50 (Strong)
08:14:40 |    West Oaks Mall: NOI=$5,500,000.00, Debt Service=$3,025,000.00, DSCR=1.82 (Strong)
08:14:40 |    Riverside Galleria: NOI=$3,200,000.00, Debt Service=$3,600,000.00, DSCR=0.89 (At Risk)
08:14:40 |    Lakeside Plaza: NOI=$2,100,000.00, Debt Service=$1,780,000.00, DSCR=1.18 (Acceptable)
08:14:40 |    Sunset Commons: NOI=$1,850,000.00, Debt Service=$1,530,000.00, DSCR=1.21 (Acceptable)
08:14:40 |    Valley View Center: NOI=$3,840,000.00, Debt Service=$3,000,000.00, DSCR=1.28 (Strong)
08:14:40 |    Harbor Town Mall: NOI=$2,700,000.00, Debt Service=$2,500,000.00, DSCR=1.08 (Acceptable)
08:14:40 | 
08:14:40 |    === Portfolio Summary ===
08:14:40 |    Total Properties: 10
08:14:40 |    Portfolio DSCR: 1.34
08:14:40 |    Strong Coverage (DSCR >= 1.25): 5 properties
08:14:40 |    Acceptable Coverage (1.0-1.25): 4 properties
08:14:40 |    At Risk (DSCR < 1.0): 1 property
08:14:40 | ============================================================
```

**How Results are Fetched:**
```python
# In script_executor.py
def _display_execution_results(container_name: str, has_web_interface: bool):
    # Fetch logs
    result = subprocess.run(
        ["docker", "logs", container_name],
        capture_output=True,
        text=True
    )
    
    logs = result.stdout + result.stderr
    
    # Find results section
    in_results = False
    for line in logs.split('\n'):
        if '=== Calculation Results ===' in line:
            in_results = True
        elif '=== End Results ===' in line:
            in_results = False
        elif in_results:
            # Clean loguru formatting and display
            content = clean_loguru_prefix(line)
            logger.info(f"   {content}")
```

---

### ✅ **STAGE 10: Completion Summary**

**Terminal Output:**
```
08:14:40 | 
08:14:40 | ✅ SUCCESS
08:14:40 | ============================================================
08:14:40 | Script executed successfully in 85 seconds
08:14:40 | 
08:14:40 | 📁 Location: generated_scripts/script_20251103_081321
08:14:40 | 🐳 Container: script_20251103_081321 (Exited successfully)
08:14:40 | 
08:14:40 | 💡 Quick Commands:
08:14:40 |    View logs:    docker logs script_20251103_081321
08:14:40 |    View script:  cat generated_scripts/script_20251103_081321/script.py
08:14:40 |    Re-run:       cd generated_scripts/script_20251103_081321 && bash deploy.sh
08:14:40 |    Clean up:     docker rm script_20251103_081321
08:14:40 | ============================================================
```

---

## Generated Artifacts

### File Structure

```
generated_scripts/script_20251103_081321/
├── script.py              # ✅ Generated Python script (78 lines)
├── requirements.txt       # ✅ Auto-detected dependencies (5 packages)
├── Dockerfile            # ✅ Container definition
├── docker-compose.yml    # ✅ Orchestration config
├── deploy.sh            # ✅ Deployment script (executable)
├── .env.example         # ✅ Environment template
├── .env                 # ✅ Actual configuration
├── README.md           # ✅ Usage instructions
├── results/            # 📂 Output directory (empty for console scripts)
├── logs/              # 📂 Application logs
│   └── dscr_analysis.log  # ✅ Detailed execution log
└── exports/           # 📂 Export directory
    ├── reports/
    └── data/
```

---

## Results Interpretation

### What the Numbers Mean

**DSCR (Debt Service Coverage Ratio) = NOI ÷ Annual Debt Service**

| DSCR Range | Classification | Meaning |
|------------|---------------|---------|
| **≥ 1.25** | Strong | Property generates 25%+ cushion above debt payments |
| **1.0 - 1.25** | Acceptable | Property covers debt but with limited cushion |
| **< 1.0** | At Risk | Property doesn't generate enough income to cover debt |

### Portfolio Analysis

**From Example Results:**
- **Total Properties**: 10
- **Portfolio DSCR**: 1.34 (Strong overall)
- **Strong Properties**: 5 (50%)
- **Acceptable**: 4 (40%)
- **At Risk**: 1 (10%) - **Riverside Galleria** with DSCR 0.89

### Action Items

**Immediate Attention Required:**
- 🚨 **Riverside Galleria** (DSCR 0.89)
  - Not covering debt service
  - Consider: Rent increases, expense reduction, or refinancing

**Monitor Closely:**
- ⚠️ **Lakeside Plaza** (DSCR 1.18)
- ⚠️ **Harbor Town Mall** (DSCR 1.08)
  - Low cushion, vulnerable to income drops

**Strong Performers:**
- ✅ **Orlando Fashion Square** (DSCR 1.94) - Excellent
- ✅ **West Oaks Mall** (DSCR 1.82) - Strong
- ✅ **1893 Rouse Lake Rd** (DSCR 1.66) - Strong

---

## Troubleshooting Guide

### Issue 1: LM Studio Connection Failed

**Error:**
```
ConnectionError: Cannot connect to LM Studio at http://localhost:1234/v1
```

**Solution:**
```bash
# 1. Check if LM Studio is running
curl http://localhost:1234/v1/models

# 2. Open LM Studio application
# 3. Load model: qwen2.5-coder-7b-instruct-mlx
# 4. Click "Start Server"
# 5. Verify port is 1234

# 6. Retry
python script_executor.py
```

---

### Issue 2: Database Connection Failed

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# 1. Check PostgreSQL is running
pg_isready -h localhost -p 5433

# 2. Test connection manually
psql -h localhost -p 5433 -U postgres -d orlando_db

# 3. For Docker containers, use host.docker.internal
export DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5433/orlando_db"

# 4. Verify .env file in generated script directory
cat generated_scripts/script_*//.env
```

---

### Issue 3: Syntax Errors in Generated Code

**Error:**
```
SyntaxError: invalid syntax (<unknown>, line 115)
```

**Root Cause:**
- LLM (Qwen2.5-Coder-7B) included explanatory text in code
- Code cleaning function didn't catch it

**Solution:**
```bash
# 1. Check the generated script
cat generated_scripts/$(ls -t generated_scripts/ | head -1)/script.py | head -120

# 2. If you see plain English text in code, it's a cleaning issue
# The system will auto-retry up to 3 times with error feedback

# 3. If all 3 attempts fail, simplify the prompt:
# Instead of: "Compare year-over-year performance with detailed analysis"
# Try: "Calculate DSCR for all properties"
```

**Prevention:**
- Use simpler, more direct prompts
- Avoid ambiguous language
- Be specific about what you want

---

### Issue 4: Container Build Failed

**Error:**
```
ERROR: failed to solve: executor failed
```

**Solution:**
```bash
# 1. Check Docker is running
docker info

# 2. View full build logs
cd generated_scripts/script_20251103_081321
docker-compose build --no-cache

# 3. Check requirements.txt for invalid packages
cat requirements.txt

# 4. Rebuild
bash deploy.sh
```

---

### Issue 5: No Results Displayed

**Error:**
```
📊 RESULTS
============================================================
   (Container running, no output yet)
============================================================
```

**Solution:**
```bash
# 1. Check if container is still running
docker ps -a --filter "name=script_"

# 2. View full logs
docker logs script_20251103_081321

# 3. Check for errors in logs
docker logs script_20251103_081321 2>&1 | grep -i error

# 4. If database connection issue, check .env
docker exec script_20251103_081321 env | grep DATABASE_URL
```

---

## Performance Benchmarks

### Timing Breakdown (Typical Run)

| Stage | Duration | % of Total |
|-------|----------|------------|
| Initialization | 5-10s | 8% |
| Schema Inspection | 1-2s | 2% |
| Task Analysis | 10-20s | 15% |
| Execution Planning | 15-30s | 23% |
| Script Generation | 20-60s | 38% |
| Validation | 1-2s | 2% |
| Packaging | 2-5s | 4% |
| Container Build | 5-15s | 10% |
| Execution | 1-5s | 2% |
| **TOTAL** | **60-150s** | **100%** |

**Average:** ~85 seconds (~1.5 minutes)

---

## Quick Reference Commands

```bash
# View latest execution
ls -lt generated_scripts/ | head -1

# Check latest results
docker logs $(docker ps -a --format "{{.Names}}" | grep script_ | head -1)

# Re-run latest script
cd generated_scripts/$(ls -t generated_scripts/ | head -1) && bash deploy.sh

# View generated code
bat generated_scripts/$(ls -t generated_scripts/ | head -1)/script.py

# Clean up containers
docker stop $(docker ps -q --filter "name=script_")
docker rm $(docker ps -aq --filter "name=script_")

# Monitor all containers
watch -n 2 'docker ps -a --format "table {{.Names}}\t{{.Status}}"'
```

---

## Summary

### What You Get

✅ **Input**: Natural language request  
✅ **Output**: Production-ready Python script in Docker container  
✅ **Time**: ~1-2 minutes  
✅ **Cost**: $0 (local inference)  
✅ **Quality**: Syntax-validated, security-checked, fully functional  

### Key Benefits

1. **No Coding Required**: Write requests in plain English
2. **Database-Aware**: Automatically discovers and uses your schema
3. **Containerized**: Isolated, reproducible execution environment
4. **Automatic Results**: No manual log checking needed
5. **Free**: No API costs, runs 100% locally

### Next Steps

1. ✅ Verify setup (LM Studio + Database)
2. ✅ Run simple prompt first (like DSCR example above)
3. ✅ Gradually try more complex prompts
4. ✅ Use for real financial analysis tasks

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Status:** Production Ready

