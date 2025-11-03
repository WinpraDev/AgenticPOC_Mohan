# Meta-Agent Script-Based Architecture Plan

## 🎯 Vision: From Agent Generation to Script Orchestration

Transform the Meta-Agent from generating new agents to generating executable scripts that leverage a rich tool library to fulfill user requirements.

---

## 📊 Current vs. New Architecture

### Current Approach (Agent Generation)
```
User Request → Analyze → Design → Generate Agent Code → Deploy Agent → Run Agent
                                   (Full Agent System)
```

**Characteristics:**
- Generates complete agent systems for each request
- Each agent has its own code, deployment, monitoring
- Heavy infrastructure per request
- Focus: Code generation and validation

### New Approach (Script Orchestration)
```
User Request → Analyze → Plan → Generate Script → Containerize → Execute → Results
                                (Tool Orchestration)
```

**Characteristics:**
- Meta-Agent has a rich library of reusable tools
- Generates lightweight orchestration scripts
- Single agent with many capabilities
- Focus: Tool composition and orchestration

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         META-AGENT CORE                             │
│  • Analyzes user requirements                                       │
│  • Plans tool composition                                           │
│  • Generates orchestration scripts                                  │
│  • Manages execution lifecycle                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
        │   TOOL LIBRARY   │  │   SCRIPT     │  │  CONTAINER   │
        │                  │  │  GENERATOR   │  │  RUNTIME     │
        │ • Database Ops   │  │              │  │              │
        │ • Calculations   │  │ • Orchestr.  │  │ • Isolation  │
        │ • Data Processing│  │ • Validation │  │ • Simulation │
        │ • API Calls      │  │ • Error Hand.│  │ • Logs/Results│
        │ • File I/O       │  │ • Logging    │  │ • Monitoring │
        │ • Analytics      │  │              │  │              │
        └──────────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔧 Core Components

### 1. Tool Library (`meta_agent/tool_library/`)

Reusable, composable tools that the Meta-Agent can leverage:

#### **Database Tools** (`database_tools.py`)
```python
- query_database(query, params) → Results
- fetch_property_data(property_id) → PropertyData
- fetch_financial_data(property_id, metrics) → FinancialData
- batch_query(queries) → List[Results]
- aggregate_data(table, filters, aggregations) → AggregatedData
```

#### **Calculation Tools** (`calculation_tools.py`)
```python
- calculate_dscr(noi, debt_service) → float
- calculate_cap_rate(noi, property_value) → float
- calculate_irr(cash_flows, dates) → float
- calculate_roi(initial, final, period) → float
- financial_ratios(data) → Dict[str, float]
```

#### **Data Processing Tools** (`data_tools.py`)
```python
- transform_data(data, transformations) → TransformedData
- filter_data(data, conditions) → FilteredData
- aggregate_metrics(data, group_by) → AggregatedData
- export_to_csv(data, filename) → Path
- export_to_excel(data, filename, sheets) → Path
- export_to_pdf(data, template) → Path
```

#### **Analysis Tools** (`analysis_tools.py`)
```python
- trend_analysis(time_series_data) → TrendResults
- comparative_analysis(datasets) → ComparisonResults
- outlier_detection(data, method) → OutlierResults
- correlation_analysis(variables) → CorrelationMatrix
- scenario_analysis(base_case, scenarios) → ScenarioResults
```

#### **API/External Tools** (`external_tools.py`)
```python
- call_external_api(endpoint, params) → APIResponse
- geocode_address(address) → Coordinates
- fetch_market_data(location, radius) → MarketData
- get_demographics(location) → Demographics
```

#### **Validation Tools** (`validation_tools.py`)
```python
- validate_property_id(property_id) → bool
- validate_data_format(data, schema) → ValidationResult
- check_data_quality(data, rules) → QualityReport
- verify_calculations(inputs, outputs, expected) → VerificationResult
```

---

### 2. Script Generator (`meta_agent/script_generator/`)

Generates executable Python scripts that orchestrate tools.

#### **Script Generator Core** (`generator.py`)
```python
class ScriptGenerator:
    """Generates orchestration scripts from user requirements"""
    
    def analyze_requirements(self, user_request: str) -> RequirementAnalysis
    def plan_tool_composition(self, analysis: RequirementAnalysis) -> ExecutionPlan
    def generate_script(self, plan: ExecutionPlan) -> Script
    def validate_script(self, script: Script) -> ValidationResult
```

#### **Script Template** (Example Output)
```python
#!/usr/bin/env python3
"""
Generated Script: Calculate DSCR for Orlando Fashion Square
Generated: 2025-10-30 09:30:00
Requirements: Calculate debt coverage ratio using database data
"""

from tool_library.database_tools import fetch_property_data, fetch_financial_data
from tool_library.calculation_tools import calculate_dscr
from tool_library.validation_tools import validate_property_id
from tool_library.data_tools import export_to_csv, export_to_pdf
import logging

def main():
    """Main execution function"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Validate inputs
        property_id = "orlando_fashion_square"
        logger.info(f"Validating property ID: {property_id}")
        if not validate_property_id(property_id):
            raise ValueError(f"Invalid property ID: {property_id}")
        
        # Step 2: Fetch data
        logger.info("Fetching property and financial data...")
        property_data = fetch_property_data(property_id)
        financial_data = fetch_financial_data(
            property_id, 
            metrics=["noi", "debt_service"]
        )
        
        # Step 3: Calculate DSCR
        logger.info("Calculating DSCR...")
        dscr = calculate_dscr(
            noi=financial_data["noi"],
            debt_service=financial_data["debt_service"]
        )
        
        # Step 4: Prepare results
        results = {
            "property_id": property_id,
            "property_name": property_data["name"],
            "noi": financial_data["noi"],
            "debt_service": financial_data["debt_service"],
            "dscr": dscr,
            "status": "Healthy" if dscr >= 1.25 else "At Risk"
        }
        
        # Step 5: Export results
        logger.info("Exporting results...")
        export_to_csv([results], "/app/results/dscr_analysis.csv")
        export_to_pdf(results, "/app/results/dscr_report.pdf")
        
        logger.info(f"✅ DSCR Calculation Complete: {dscr:.2f}")
        return results
        
    except Exception as e:
        logger.error(f"❌ Script execution failed: {e}")
        raise

if __name__ == "__main__":
    main()
```

---

### 3. Container Runtime (`meta_agent/container_runtime/`)

Manages containerized execution of generated scripts.

#### **Container Manager** (`container_manager.py`)
```python
class ContainerManager:
    """Manages containerized script execution"""
    
    def prepare_container(self, script: Script) -> Container
    def mount_volumes(self, container: Container, volumes: Dict) → None
    def inject_dependencies(self, container: Container) → None
    def execute_script(self, container: Container, script: Script) → ExecutionResult
    def collect_results(self, container: Container) → Results
    def cleanup(self, container: Container) → None
```

#### **Container Configuration**
```yaml
# Base container for all scripts
FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir \
    psycopg2-binary \
    pandas \
    numpy \
    pydantic \
    loguru

# Copy tool library
COPY tool_library/ /app/tool_library/

# Create directories
RUN mkdir -p /app/scripts /app/results /app/logs /app/data

# Volume mounts:
# - /app/scripts  → Generated scripts
# - /app/results  → Output files
# - /app/logs     → Execution logs
# - /app/data     → Input data

WORKDIR /app
```

---

### 4. Simulation Framework (`meta_agent/simulation/`)

Enables batch execution, scenario testing, and what-if analysis.

#### **Simulation Runner** (`simulation_runner.py`)
```python
class SimulationRunner:
    """Runs scripts in simulation mode with various scenarios"""
    
    def define_scenario(self, name: str, parameters: Dict) → Scenario
    def run_single_simulation(self, script: Script, scenario: Scenario) → SimulationResult
    def run_batch_simulations(self, script: Script, scenarios: List[Scenario]) → List[SimulationResult]
    def compare_scenarios(self, results: List[SimulationResult]) → ComparisonReport
    def export_simulation_results(self, results: List[SimulationResult]) → Path
```

#### **Scenario Definition Example**
```python
scenarios = [
    {
        "name": "Base Case",
        "parameters": {
            "noi": 1_000_000,
            "debt_service": 750_000
        }
    },
    {
        "name": "Pessimistic",
        "parameters": {
            "noi": 800_000,
            "debt_service": 750_000
        }
    },
    {
        "name": "Optimistic",
        "parameters": {
            "noi": 1_200_000,
            "debt_service": 750_000
        }
    }
]
```

---

## 🔄 Workflow: User Request to Results

### Step-by-Step Process

```
1️⃣ User Request
   ↓
   "Calculate DSCR for all properties and identify at-risk assets"

2️⃣ Requirements Analysis (LLM-powered)
   ↓
   • Goal: Calculate DSCR and identify at-risk properties
   • Data needed: Property IDs, NOI, Debt Service
   • Tools required: database_tools, calculation_tools, data_tools
   • Outputs: CSV report, PDF summary, list of at-risk properties

3️⃣ Execution Planning
   ↓
   • Step 1: Fetch all property IDs from database
   • Step 2: For each property, fetch financial data
   • Step 3: Calculate DSCR for each property
   • Step 4: Filter properties with DSCR < 1.25
   • Step 5: Generate reports

4️⃣ Script Generation
   ↓
   • Generate orchestration script (Python)
   • Include error handling and logging
   • Add validation checks
   • Configure outputs

5️⃣ Script Validation
   ↓
   • Syntax check
   • Security scan (no hardcoded credentials)
   • Tool availability check
   • Output path validation

6️⃣ Containerization
   ↓
   • Prepare isolated container
   • Mount volumes (results, logs, data)
   • Inject environment variables
   • Copy script into container

7️⃣ Execution
   ↓
   • Run script in container
   • Stream logs in real-time
   • Monitor resource usage
   • Handle errors gracefully

8️⃣ Results Collection
   ↓
   • Collect output files (CSV, PDF, Excel)
   • Parse execution logs
   • Extract metrics and KPIs
   • Generate execution summary

9️⃣ Archiving
   ↓
   • Archive script + results + logs
   • Create timestamped folder
   • Generate manifest
   • Clean up containers
```

---

## 📁 Project Structure

```
AgenticPOC_Meta/
├── meta_agent/
│   ├── core/
│   │   ├── meta_agent.py              # Main Meta-Agent orchestrator
│   │   ├── requirement_analyzer.py    # Analyzes user requests
│   │   └── execution_planner.py       # Plans tool composition
│   │
│   ├── tool_library/                  # Reusable tool library
│   │   ├── __init__.py
│   │   ├── database_tools.py
│   │   ├── calculation_tools.py
│   │   ├── data_tools.py
│   │   ├── analysis_tools.py
│   │   ├── external_tools.py
│   │   ├── validation_tools.py
│   │   └── tool_registry.py           # Tracks available tools
│   │
│   ├── script_generator/              # Script generation
│   │   ├── __init__.py
│   │   ├── generator.py               # Main script generator
│   │   ├── templates.py               # Script templates
│   │   └── validator.py               # Script validation
│   │
│   ├── container_runtime/             # Container management
│   │   ├── __init__.py
│   │   ├── container_manager.py       # Container lifecycle
│   │   ├── executor.py                # Script execution
│   │   └── Dockerfile.base            # Base container image
│   │
│   ├── simulation/                    # Simulation framework
│   │   ├── __init__.py
│   │   ├── simulation_runner.py       # Run simulations
│   │   ├── scenario_manager.py        # Manage scenarios
│   │   └── results_analyzer.py        # Analyze results
│   │
│   └── utils/
│       ├── llm_client.py              # LLM integration
│       ├── logger.py                  # Structured logging
│       └── archive_manager.py         # Results archiving
│
├── scripts/                            # Generated scripts (mounted)
├── results/                            # Execution results (mounted)
├── logs/                               # Execution logs (mounted)
├── archives/                           # Archived executions
│
├── config.py                           # Configuration
├── requirements.txt                    # Dependencies
├── main.py                             # Entry point
└── docker-compose.yml                  # Container orchestration
```

---

## 🚀 Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Design tool library interface
- [ ] Implement database tools
- [ ] Implement calculation tools
- [ ] Create tool registry system
- [ ] Build requirement analyzer (LLM-powered)
- [ ] Create execution planner

### Phase 2: Script Generation (Week 2)
- [ ] Design script template system
- [ ] Implement script generator
- [ ] Add script validation
- [ ] Create error handling patterns
- [ ] Add logging integration
- [ ] Test with sample requirements

### Phase 3: Container Runtime (Week 3)
- [ ] Create base container image
- [ ] Implement container manager
- [ ] Add volume mounting logic
- [ ] Build script executor
- [ ] Implement results collection
- [ ] Add real-time log streaming

### Phase 4: Simulation Framework (Week 4)
- [ ] Design scenario system
- [ ] Implement simulation runner
- [ ] Add batch execution
- [ ] Create results analyzer
- [ ] Build comparison tools
- [ ] Add visualization

### Phase 5: Integration & Testing (Week 5)
- [ ] Integrate all components
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation
- [ ] User guides

---

## 💡 Example Use Cases

### Use Case 1: Portfolio Analysis
```
User: "Calculate DSCR for all properties and identify at-risk assets"

Meta-Agent:
1. Analyzes: Need to calculate DSCR for multiple properties
2. Plans: Fetch all properties → Calculate each DSCR → Filter at-risk
3. Generates: Script using database_tools + calculation_tools
4. Executes: In container with database access
5. Returns: CSV report, PDF summary, at-risk property list
```

### Use Case 2: Market Comparison
```
User: "Compare Orlando Fashion Square performance against 5 similar properties"

Meta-Agent:
1. Analyzes: Need property comparison with multiple metrics
2. Plans: Fetch target property → Find similar properties → Compare metrics
3. Generates: Script using database_tools + analysis_tools
4. Executes: In container with full data access
5. Returns: Comparison report, visualization, recommendations
```

### Use Case 3: Scenario Analysis
```
User: "Run DSCR scenarios with 10%, 20%, 30% NOI decrease for all properties"

Meta-Agent:
1. Analyzes: Need scenario-based simulation
2. Plans: Define scenarios → Run for each property → Compare results
3. Generates: Script using simulation framework
4. Executes: Batch simulation in container
5. Returns: Scenario comparison, risk analysis, sensitivity charts
```

### Use Case 4: Automated Reporting
```
User: "Generate monthly performance report for executive team"

Meta-Agent:
1. Analyzes: Need comprehensive multi-metric report
2. Plans: Fetch all metrics → Calculate KPIs → Format report
3. Generates: Script using data_tools + external_tools (PDF generation)
4. Executes: In container with template access
5. Returns: Executive PDF report, data export, email-ready summary
```

---

## 🔒 Security Considerations

### Container Isolation
- Each script runs in isolated container
- No host access except mounted volumes
- Read-only access to tool library
- Time limits and resource constraints

### Credential Management
- Environment variables for sensitive data
- No hardcoded credentials in scripts
- Secret injection at runtime
- Secure database connection pooling

### Script Validation
- Syntax validation before execution
- Security scanning (SQL injection, file access)
- Tool allowlist (only registered tools)
- Output path validation

---

## 📊 Monitoring & Observability

### Real-Time Monitoring
- Container resource usage (CPU, memory)
- Script execution progress
- Log streaming
- Error tracking

### Metrics Collection
- Execution time per script
- Success/failure rates
- Tool usage statistics
- Resource consumption

### Alerts
- Script failures
- Long-running executions
- Resource threshold breaches
- Data validation failures

---

## 🎯 Benefits of Script-Based Approach

### Advantages
1. **Faster Execution**: No agent generation overhead
2. **Reusability**: Tool library shared across all requests
3. **Maintainability**: Update tools once, benefit everywhere
4. **Scalability**: Run multiple scripts in parallel
5. **Flexibility**: Easy to add new tools
6. **Testability**: Test tools independently
7. **Transparency**: Scripts are human-readable
8. **Versioning**: Track script versions easily

### Comparison

| Aspect | Agent Generation | Script Orchestration |
|--------|------------------|---------------------|
| **Setup Time** | 5-15 minutes | 10-30 seconds |
| **Code Size** | Full agent (100s of lines) | Script (50-100 lines) |
| **Reusability** | Low (agent-specific) | High (shared tools) |
| **Maintenance** | Per-agent updates | Central tool updates |
| **Execution** | Deploy + Run | Generate + Run |
| **Scalability** | Limited (many containers) | High (parallel scripts) |
| **Learning Curve** | High (full agent) | Low (script + tools) |

---

## 🔄 Migration Strategy

### From Current to New Architecture

#### Step 1: Build Tool Library
- Extract common functionality from existing agents
- Create standardized tool interfaces
- Test each tool independently

#### Step 2: Implement Script Generator
- Use existing code generation logic
- Adapt to generate simpler orchestration scripts
- Leverage existing validation

#### Step 3: Container Runtime
- Adapt existing deployment tools
- Simplify to single-script execution
- Keep volume mounting and monitoring

#### Step 4: Parallel Operation
- Run both systems side-by-side
- Gradually migrate use cases
- Compare performance and results

#### Step 5: Full Migration
- Deprecate agent generation for simple requests
- Keep agent generation for complex multi-agent systems
- Use script orchestration as default

---

## 📈 Success Metrics

### Performance Metrics
- Script generation time: < 30 seconds
- Execution time: Task-dependent, optimized
- Success rate: > 95%
- Resource efficiency: < 512MB RAM per script

### Quality Metrics
- Script correctness: 100% syntax valid
- Security: Zero hardcoded credentials
- Error handling: All errors logged and handled
- Results accuracy: Validated against expected outcomes

---

## 🎓 Next Steps

1. **Review this plan** with stakeholders
2. **Validate approach** with sample use cases
3. **Prioritize tool library** (which tools first?)
4. **Start Phase 1** implementation
5. **Create proof of concept** with 1-2 tools
6. **Iterate based on feedback**

---

## 📝 Open Questions

1. Should we keep agent generation for complex multi-agent orchestration?
2. How do we handle tools that require human-in-the-loop?
3. What's the strategy for tool versioning?
4. How do we handle tool failures gracefully?
5. Should scripts be cached/reused for similar requests?
6. How do we handle long-running scripts (hours/days)?
7. What's the learning strategy for new tools?

---

**Status**: 📋 PLAN READY FOR REVIEW
**Next Action**: Stakeholder review and approval to proceed with Phase 1
**Timeline**: 5-week implementation plan
**Risk Level**: LOW (leverages existing infrastructure)

