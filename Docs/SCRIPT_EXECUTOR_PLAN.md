# Meta-Agent Script Executor Architecture Plan

**Version:** 2.0.0  
**Date:** October 30, 2025  
**Status:** 🎯 Planning Phase

---

## 🎯 Vision

Transform the Meta-Agent from an **Agent Factory** to a **Script Executor** that:
- Generates executable scripts directly from natural language requirements
- Containerizes scripts for isolated execution
- Runs simulations and returns results
- No persistent agents - ephemeral, task-focused execution

---

## 📊 Architecture Comparison

### Current Model (Agent Factory)

```
User Request
     ↓
Analyze Requirements
     ↓
Design Agent Architecture
     ↓
Generate Agent Specifications (YAML)
     ↓
Generate Agent Code (Python)
     ↓
Validate & Deploy Agents
     ↓
Persistent Agents Ready for Use
```

**Output:** Reusable agents that can be deployed and called multiple times

---

### New Model (Script Executor)

```
User Request
     ↓
Analyze Task Requirements
     ↓
Design Execution Plan
     ↓
Generate Execution Scripts
     ↓
Validate Scripts
     ↓
Containerize & Execute
     ↓
Run Simulations
     ↓
Return Results
```

**Output:** Task results with simulation data, ephemeral execution

---

## 🏗️ New Architecture Components

### 1. Task Analyzer (Enhanced)

**Purpose:** Understand what the user wants to accomplish

**Inputs:**
- Natural language request
- Context (database, APIs, data sources)

**Outputs:**
- Task type (calculation, data processing, analysis, report generation)
- Required data sources
- Expected output format
- Complexity assessment

**Example:**
```yaml
task:
  type: calculation
  goal: Calculate DSCR for Orlando Fashion Square
  data_sources:
    - postgresql://dscr_poc_db
  required_data:
    - property_info
    - financial_data
  outputs:
    - dscr_value: float
    - recommendation: string
    - report: pdf
  complexity: LOW
```

---

### 2. Execution Plan Designer

**Purpose:** Break down the task into executable steps

**Inputs:**
- Task analysis
- Available tools/APIs
- Data source schemas

**Outputs:**
- Step-by-step execution plan
- Data flow diagram
- Resource requirements

**Example:**
```yaml
execution_plan:
  name: dscr_calculation
  steps:
    - step: 1
      name: fetch_property_data
      action: database_query
      query: "SELECT * FROM properties WHERE name = 'Orlando Fashion Square'"
      output: property_data
      
    - step: 2
      name: fetch_financial_data
      action: database_query
      query: "SELECT * FROM financials WHERE property_id = {property_data.id}"
      output: financial_data
      
    - step: 3
      name: calculate_dscr
      action: python_calculation
      formula: "(financial_data.noi / financial_data.debt_service) * 12"
      output: dscr_result
      
    - step: 4
      name: generate_recommendation
      action: conditional_logic
      conditions:
        - if: dscr_result >= 1.25
          then: "APPROVE - Strong debt coverage"
        - if: dscr_result < 1.15
          then: "REJECT - Insufficient coverage"
        - else: "REVIEW - Borderline coverage"
      output: recommendation
      
    - step: 5
      name: generate_report
      action: report_generation
      template: dscr_report
      data: [property_data, financial_data, dscr_result, recommendation]
      output: report_pdf
```

---

### 3. Script Generator

**Purpose:** Generate executable Python scripts from execution plan

**Inputs:**
- Execution plan
- Available libraries/dependencies

**Outputs:**
- Python script with all steps implemented
- Dependencies list (requirements.txt)
- Environment configuration

**Script Structure:**
```python
#!/usr/bin/env python3
"""
Auto-generated script: DSCR Calculation
Generated: 2025-10-30 15:45:00
Task: Calculate debt coverage ratio for Orlando Fashion Square
"""

import os
import psycopg2
from typing import Dict, Any
from loguru import logger
from fpdf import FPDF

# Configuration from environment
DB_URL = os.getenv('DATABASE_URL')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/results')

class TaskExecutor:
    def __init__(self):
        self.results = {}
        
    def step_1_fetch_property_data(self) -> Dict[str, Any]:
        """Fetch property data from database"""
        logger.info("Step 1: Fetching property data")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties WHERE name = %s", 
                      ("Orlando Fashion Square",))
        result = cursor.fetchone()
        conn.close()
        return dict(result)
    
    def step_2_fetch_financial_data(self, property_id: str) -> Dict[str, Any]:
        """Fetch financial data from database"""
        logger.info("Step 2: Fetching financial data")
        # ... implementation
        
    def step_3_calculate_dscr(self, financial_data: Dict) -> float:
        """Calculate DSCR"""
        logger.info("Step 3: Calculating DSCR")
        noi = financial_data['net_operating_income']
        debt_service = financial_data['debt_service']
        dscr = (noi / debt_service) * 12
        return dscr
    
    def step_4_generate_recommendation(self, dscr: float) -> str:
        """Generate recommendation based on DSCR"""
        logger.info("Step 4: Generating recommendation")
        if dscr >= 1.25:
            return "APPROVE - Strong debt coverage"
        elif dscr < 1.15:
            return "REJECT - Insufficient coverage"
        else:
            return "REVIEW - Borderline coverage"
    
    def step_5_generate_report(self, **data) -> str:
        """Generate PDF report"""
        logger.info("Step 5: Generating report")
        # ... PDF generation
        
    def execute(self) -> Dict[str, Any]:
        """Execute all steps"""
        try:
            property_data = self.step_1_fetch_property_data()
            financial_data = self.step_2_fetch_financial_data(property_data['id'])
            dscr_result = self.step_3_calculate_dscr(financial_data)
            recommendation = self.step_4_generate_recommendation(dscr_result)
            report_path = self.step_5_generate_report(
                property_data=property_data,
                financial_data=financial_data,
                dscr_result=dscr_result,
                recommendation=recommendation
            )
            
            return {
                'status': 'success',
                'dscr': dscr_result,
                'recommendation': recommendation,
                'report': report_path,
                'execution_time': '2.5s'
            }
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

if __name__ == '__main__':
    executor = TaskExecutor()
    result = executor.execute()
    print(json.dumps(result, indent=2))
```

---

### 4. Script Validator

**Purpose:** Ensure generated scripts are safe and correct

**Checks:**
- Syntax validation
- Security checks (no hardcoded credentials)
- Resource limits validation
- Dependency compatibility

---

### 5. Containerization System

**Purpose:** Package scripts into isolated Docker containers

**Components:**

#### A. Dockerfile Generator

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY script.py .

# Create output directory
RUN mkdir -p /app/results /app/logs

# Set environment
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/app/results

# Run script
CMD ["python", "script.py"]
```

#### B. Docker Compose Generator

```yaml
version: '3.8'

services:
  task-executor:
    build: .
    container_name: dscr-calculation-executor
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OUTPUT_DIR=/app/results
    volumes:
      - ./results:/app/results:rw
      - ./logs:/app/logs:rw
    networks:
      - task-network
    mem_limit: 512m
    cpus: 0.5
    restart: no

networks:
  task-network:
    driver: bridge
```

---

### 6. Simulation Runner

**Purpose:** Execute scripts with different parameters/scenarios

**Features:**
- Run multiple scenarios in parallel
- Compare results across scenarios
- Generate simulation reports
- Performance metrics

**Example Simulations:**
```yaml
simulations:
  - name: base_case
    parameters:
      property: "Orlando Fashion Square"
      scenario: "current"
    
  - name: optimistic
    parameters:
      property: "Orlando Fashion Square"
      scenario: "10% revenue increase"
    
  - name: pessimistic
    parameters:
      property: "Orlando Fashion Square"
      scenario: "10% revenue decrease"
    
  - name: stress_test
    parameters:
      property: "Orlando Fashion Square"
      scenario: "20% revenue decrease, 5% expense increase"
```

**Simulation Output:**
```json
{
  "simulations": {
    "base_case": {
      "dscr": 1.35,
      "recommendation": "APPROVE",
      "execution_time": "2.1s"
    },
    "optimistic": {
      "dscr": 1.48,
      "recommendation": "APPROVE",
      "execution_time": "2.3s"
    },
    "pessimistic": {
      "dscr": 1.22,
      "recommendation": "REVIEW",
      "execution_time": "2.2s"
    },
    "stress_test": {
      "dscr": 1.08,
      "recommendation": "REJECT",
      "execution_time": "2.4s"
    }
  },
  "summary": {
    "total_scenarios": 4,
    "passed": 2,
    "review": 1,
    "failed": 1,
    "average_execution_time": "2.25s"
  }
}
```

---

### 7. Result Aggregator

**Purpose:** Collect, analyze, and present execution results

**Outputs:**
- Execution logs
- Calculated values
- Generated reports (PDF, Excel, HTML)
- Comparison charts
- Performance metrics

---

## 🔄 Complete Workflow

### Step-by-Step Process

```
1. USER REQUEST
   ↓
   "Calculate DSCR for Orlando Fashion Square with 3 scenarios"

2. TASK ANALYZER
   ↓
   {
     task_type: "financial_calculation",
     requires_simulation: true,
     scenario_count: 3,
     complexity: "MEDIUM"
   }

3. EXECUTION PLAN DESIGNER
   ↓
   {
     steps: [fetch_data, calculate, compare, report],
     simulations: [base, optimistic, pessimistic]
   }

4. SCRIPT GENERATOR
   ↓
   - script.py (200 lines)
   - requirements.txt
   - .env.example

5. SCRIPT VALIDATOR
   ↓
   ✓ Syntax: PASS
   ✓ Security: PASS
   ✓ Resources: PASS

6. CONTAINERIZATION
   ↓
   - Dockerfile
   - docker-compose.yml
   - Build image

7. SIMULATION RUNNER
   ↓
   - Run base scenario
   - Run optimistic scenario
   - Run pessimistic scenario
   - Collect results

8. RESULT AGGREGATOR
   ↓
   - Execution summary
   - Comparison report
   - Performance metrics
   - Generated PDFs

9. ARCHIVE & CLEANUP
   ↓
   - Archive all outputs
   - Clean up containers
   - Store results
```

---

## 📂 New Directory Structure

```
AgenticPOC_Meta/
├── config.py
├── requirements.txt
├── .env
│
├── meta_agent/
│   ├── analyzers/
│   │   ├── task_analyzer.py          # NEW
│   │   └── complexity_assessor.py    # NEW
│   │
│   ├── planners/
│   │   ├── execution_planner.py      # NEW
│   │   └── simulation_designer.py    # NEW
│   │
│   ├── generators/
│   │   ├── script_generator.py       # NEW
│   │   ├── dockerfile_generator.py   # NEW
│   │   └── compose_generator.py      # NEW
│   │
│   ├── validators/
│   │   ├── script_validator.py       # NEW
│   │   └── resource_validator.py     # NEW
│   │
│   ├── executors/
│   │   ├── container_executor.py     # NEW
│   │   ├── simulation_runner.py      # NEW
│   │   └── result_aggregator.py      # NEW
│   │
│   └── utils/
│       ├── llm_client.py             # EXISTING
│       └── archive_manager.py        # EXISTING
│
├── execution_plans/                   # NEW
│   └── [generated plans]
│
├── generated_scripts/                 # NEW
│   └── [timestamped folders with scripts]
│
├── containers/                        # NEW
│   └── [built containers]
│
├── results/                          # NEW
│   └── [simulation results]
│
└── archives/                         # EXISTING
    └── [archived executions]
```

---

## 🛠️ Tools to Build

### New Tools (8 tools)

1. **`analyze_task.py`**
   - Understand user's task requirements
   - Identify required data sources
   - Determine task complexity

2. **`design_execution_plan.py`**
   - Break task into executable steps
   - Design data flow
   - Plan resource allocation

3. **`generate_script.py`**
   - Generate Python script from plan
   - Include all necessary functions
   - Add logging and error handling

4. **`validate_script.py`**
   - Syntax validation
   - Security checks
   - Resource limit verification

5. **`containerize_script.py`**
   - Generate Dockerfile
   - Generate docker-compose.yml
   - Build container image

6. **`run_simulation.py`**
   - Execute script with parameters
   - Handle multiple scenarios
   - Collect execution metrics

7. **`aggregate_results.py`**
   - Collect all simulation results
   - Generate comparison reports
   - Create visualizations

8. **`archive_execution.py`**
   - Archive scripts and results
   - Clean up containers
   - Store for future reference

---

## 🎯 Example Use Cases

### Use Case 1: DSCR Calculation

**User Request:**
> "Calculate the debt coverage ratio for Orlando Fashion Square property and tell me if the rental income is enough to cover debt payments."

**System Response:**
```
1. Analyzing task... ✓
2. Designing execution plan... ✓
3. Generating script (150 lines)... ✓
4. Validating script... ✓
5. Building container... ✓
6. Running simulation... ✓

Results:
- DSCR: 1.35
- Recommendation: APPROVE - Strong debt coverage
- Report: results/dscr_report_20251030_154500.pdf

Execution Time: 8.2 seconds
```

---

### Use Case 2: Multi-Scenario Analysis

**User Request:**
> "Calculate DSCR for Orlando Fashion Square under 3 scenarios: base case, 10% revenue increase, and 10% revenue decrease."

**System Response:**
```
1. Analyzing task... ✓
2. Designing execution plan (3 scenarios)... ✓
3. Generating script (250 lines)... ✓
4. Validating script... ✓
5. Building container... ✓
6. Running simulations...
   - Base case... ✓ (DSCR: 1.35)
   - Optimistic (+10%)... ✓ (DSCR: 1.48)
   - Pessimistic (-10%)... ✓ (DSCR: 1.22)

Comparison Report: results/dscr_comparison_20251030_154500.pdf

Summary:
- All scenarios show adequate coverage
- Risk: Low (all above 1.20)
- Recommendation: APPROVE

Execution Time: 12.5 seconds
```

---

### Use Case 3: Data Processing Pipeline

**User Request:**
> "Extract all property data from the database, calculate key metrics for each property, and generate a summary report."

**System Response:**
```
1. Analyzing task... ✓
2. Designing execution plan (batch processing)... ✓
3. Generating script (400 lines)... ✓
4. Validating script... ✓
5. Building container... ✓
6. Processing properties...
   - Fetched 25 properties... ✓
   - Calculated metrics... ✓
   - Generated report... ✓

Output Files:
- results/property_metrics_20251030_154500.xlsx
- results/property_summary_20251030_154500.pdf
- results/visualization_charts.png

Execution Time: 25.3 seconds
```

---

## 🔐 Security & Safety

### Container Isolation

**Resource Limits:**
```yaml
resources:
  mem_limit: 512m
  cpus: 0.5
  pids_limit: 100
  timeout: 300s
```

**Network Restrictions:**
```yaml
network:
  mode: isolated
  allowed_hosts:
    - database_host
  blocked_ports:
    - 22 (SSH)
    - 3389 (RDP)
```

**File System:**
```yaml
filesystem:
  read_only: true
  volumes:
    - ./results:/app/results:rw  # Only results writable
    - ./logs:/app/logs:rw        # Only logs writable
```

---

## 📊 Benefits Over Agent Factory

### Agent Factory Model

❌ Creates persistent agents (may not be needed)  
❌ Requires deployment infrastructure  
❌ More complex for one-time tasks  
✅ Good for reusable agents  
✅ Good for long-running services  

### Script Executor Model

✅ Direct execution - faster results  
✅ Ephemeral - no deployment needed  
✅ Perfect for one-time tasks  
✅ Easier to understand and debug  
✅ Built-in simulation support  
✅ Lower resource overhead  
❌ Not suitable for persistent services  

---

## 🎯 Implementation Phases

### Phase 1: Core Components (Week 1)
- [ ] Task Analyzer
- [ ] Execution Plan Designer
- [ ] Script Generator
- [ ] Script Validator

### Phase 2: Containerization (Week 2)
- [ ] Dockerfile Generator
- [ ] Docker Compose Generator
- [ ] Container Builder
- [ ] Container Executor

### Phase 3: Simulation (Week 3)
- [ ] Simulation Designer
- [ ] Simulation Runner
- [ ] Result Aggregator
- [ ] Comparison Reporter

### Phase 4: Integration & Testing (Week 4)
- [ ] End-to-end workflow
- [ ] Error handling
- [ ] Performance optimization
- [ ] Documentation

---

## 🔄 Migration Path

### From Agent Factory to Script Executor

**Option 1: Keep Both**
- AgenticPOC_New: Agent Factory (for persistent agents)
- AgenticPOC_Meta: Script Executor (for tasks)

**Option 2: Hybrid**
- Let user choose mode:
  - `--mode=agent` → Generate persistent agents
  - `--mode=script` → Generate and execute scripts

**Option 3: Full Migration**
- Replace agent generation with script generation
- Focus entirely on task execution

**Recommendation:** Option 1 or 2 for maximum flexibility

---

## 💡 Key Design Decisions

### 1. Script Language
**Decision:** Python  
**Rationale:** Same as current agents, rich ecosystem, easy to containerize

### 2. Container Technology
**Decision:** Docker + Docker Compose  
**Rationale:** Industry standard, good isolation, easy to use

### 3. Simulation Approach
**Decision:** Parameter-based scenarios  
**Rationale:** Flexible, easy to configure, parallel execution

### 4. Result Storage
**Decision:** Volume mounts + Archive system  
**Rationale:** Real-time access, persistent storage

### 5. LLM Usage
**Decision:** Same LM Studio setup  
**Rationale:** Already working, no additional cost

---

## 📝 Next Steps

1. **Review this plan** with stakeholders
2. **Choose migration strategy** (Option 1, 2, or 3)
3. **Build Phase 1 components** (Task Analyzer, Planner, Generator)
4. **Test with DSCR example**
5. **Iterate and refine**

---

## 🎯 Success Criteria

✅ Generate executable scripts from natural language  
✅ Execute scripts in isolated containers  
✅ Run multi-scenario simulations  
✅ Return results in < 30 seconds for simple tasks  
✅ Achieve 95%+ script generation success rate  
✅ Zero security incidents  
✅ Complete documentation  

---

**Ready to transform the Meta-Agent!** 🚀

