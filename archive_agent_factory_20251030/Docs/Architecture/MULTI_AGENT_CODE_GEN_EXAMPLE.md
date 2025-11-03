# 🎯 Multi-Agent + Code Generation: Complete Example

**Transforming Current DSCR Workflow → Flexible Multi-Agent System**

---

## 📋 Table of Contents

1. [Current System Overview](#current-system-overview)
2. [Transformation Architecture](#transformation-architecture)
3. [Example 1: Standard Mode (No Changes)](#example-1-standard-mode)
4. [Example 2: Library Mode (Pre-approved Formula)](#example-2-library-mode)
5. [Example 3: Custom Mode (Code Generation)](#example-3-custom-mode)
6. [Agent Implementation Details](#agent-implementation-details)
7. [Code Generation Examples](#code-generation-examples)
8. [Security & Validation Flow](#security--validation-flow)
9. [Complete Execution Trace](#complete-execution-trace)

---

## 1. Current System Overview

### **Current Workflow (workflow.py)**

```
User runs: python test_workflow.py --property_id=5

LangGraph Workflow executes:
    ├─ Node 1: fetch_data_node
    │   Purpose: Fetch property data from PostgreSQL
    │   Logic: SQL query to get property + financial metrics
    │   Output: PropertyData object
    │
    ├─ Node 2: simulate_dscr_node
    │   Purpose: Calculate DSCR
    │   Logic: FIXED formula: annual_noi / annual_debt_service
    │   Output: dscr=1.35
    │
    ├─ Node 3: validate_results_node
    │   Purpose: Validate DSCR against thresholds
    │   Logic: FIXED rules (line 183 in workflow.py):
    │       if dscr >= 1.25: validation_status = "PASS"
    │       elif dscr >= 1.15: validation_status = "MARGINAL"
    │       else: validation_status = "FAIL"
    │   Output: validation_status="PASS"
    │
    ├─ Node 4: analyze_results_node_llm
    │   Purpose: AI analysis of results
    │   Logic: LLM analyzes DSCR + property context
    │   Output: "Strong coverage, low risk..."
    │
    ├─ Node 5: decide_next_step_llm
    │   Purpose: AI decision
    │   Logic: LLM decides ACCEPT/ADJUST/REJECT
    │   Output: decision="ACCEPT"
    │
    └─ Node 6: adjust_parameters_node_llm (if ADJUST)
        Purpose: Suggest parameter changes
        Logic: LLM suggests new loan terms
        Output: Loop back to Node 2

Result: Analysis complete with recommendation
```

### **Limitations of Current System**:
- ❌ Fixed DSCR formula (line 183: `elif dscr >= 1.25:`)
- ❌ Cannot customize thresholds without code changes
- ❌ Cannot add custom metrics without new nodes
- ❌ Single monolithic workflow
- ❌ Hard to test individual components
- ❌ No way to generate custom formulas

---

## 2. Transformation Architecture

### **New Multi-Agent System**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                           │
│  - Receives user request                                        │
│  - Classifies request type (Standard/Library/Custom)            │
│  - Creates execution plan                                       │
│  - Coordinates agent execution                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    ▼             ▼             ▼             ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ DATA   │  │ CALC   │  │ANALYSIS│  │DECISION│  │REPORT  │
│ AGENT  │  │ AGENT  │  │ AGENT  │  │ AGENT  │  │ AGENT  │
└────┬───┘  └───┬────┘  └────┬───┘  └────┬───┘  └───┬────┘
     │          │             │            │           │
     └──────────┴─────────────┴────────────┴───────────┘
                              │
           ┌──────────────────┴──────────────────┐
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │ CODE         │                    │ FORMULA      │
    │ GENERATOR    │                    │ LIBRARY      │
    │ AGENT        │                    │              │
    │ + Validator  │                    │ (Pre-approved│
    │ + Sandbox    │                    │  formulas)   │
    └──────────────┘                    └──────────────┘
```

### **Agent Mapping from Current Workflow**

| Current Node | New Agent | New Capabilities |
|--------------|-----------|------------------|
| `fetch_data_node` | **DataAgent** | + Data quality checks, + Multiple sources |
| `simulate_dscr_node` | **CalculationAgent** | + Execute custom code, + Multiple metrics |
| `validate_results_node` | **CalculationAgent** | + Dynamic thresholds, + Custom rules |
| `analyze_results_node_llm` | **AnalysisAgent** | + Pattern recognition, + Historical comparison |
| `decide_next_step_llm` | **DecisionAgent** | + Multi-criteria decisions, + Confidence scores |
| (NEW) | **ReportingAgent** | Generate formatted outputs |
| (NEW) | **CodeGeneratorAgent** | Generate custom formulas/scripts |
| (NEW) | **OrchestratorAgent** | Coordinate all agents |

---

## 3. Example 1: Standard Mode (No Changes)

### **User Request**:
```bash
python test_workflow.py --property_id=5
```

### **Execution Flow**:

```
STEP 1: Orchestrator Receives Request
───────────────────────────────────────
Request: "Analyze property 5"
Mode Detection: STANDARD (no custom requirements)
Agent Plan: DataAgent → CalculationAgent → AnalysisAgent → DecisionAgent → ReportingAgent

STEP 2: DataAgent Executes
───────────────────────────
Action: Fetch property from PostgreSQL
Query: SELECT * FROM properties WHERE id = 5
Query: SELECT * FROM financial_metrics WHERE property_id = 5
Result:
  property_name: "Valley View Center"
  location: "Dallas, TX"
  annual_noi: $2,700,000
  annual_debt_service: $2,000,000
  property_value: $40,000,000
  loan_amount: $28,000,000

STEP 3: CalculationAgent Executes
──────────────────────────────────
Input: Property data from DataAgent
Formula: STANDARD DSCR (built-in)
Code Used:
  def calculate_dscr(annual_noi, annual_debt_service):
      if annual_debt_service == 0:
          return None
      return annual_noi / annual_debt_service

Calculation:
  DSCR = $2,700,000 / $2,000,000 = 1.35

Validation: (line 183 logic)
  dscr >= 1.25 → validation_status = "PASS"

Output:
  dscr: 1.35
  validation_status: "PASS"
  ltv: 70.0%
  cap_rate: 6.75%

STEP 4: AnalysisAgent Executes
───────────────────────────────
Input: DSCR=1.35, validation=PASS
LLM Call: "Analyze this DSCR result..."
LLM Response:
  "Valley View Center demonstrates healthy debt service coverage 
   with a DSCR of 1.35. This provides a comfortable 35% cushion 
   above minimum debt obligations. The property's stable NOI and 
   reasonable debt service suggest low refinancing risk."

STEP 5: DecisionAgent Executes
───────────────────────────────
Input: DSCR=1.35, Analysis="healthy coverage..."
LLM Call: "Based on this analysis, what is your recommendation?"
LLM Response:
  Decision: ACCEPT
  Confidence: 92%
  Reasoning: "Strong coverage ratio exceeds industry standards. 
              Property fundamentals are sound. Approval recommended."

STEP 6: ReportingAgent Executes
────────────────────────────────
Input: All previous results
Output Format: Console text
Generated Report:
  ═══════════════════════════════════════════
  PROPERTY ANALYSIS REPORT
  ═══════════════════════════════════════════
  Property: Valley View Center (Dallas, TX)
  Analysis Date: 2024-01-15
  
  KEY METRICS:
  • DSCR: 1.35 ✓ PASS
  • LTV: 70.0%
  • Cap Rate: 6.75%
  
  ANALYSIS: Healthy debt service coverage...
  
  RECOMMENDATION: ACCEPT (92% confidence)
  ═══════════════════════════════════════════

Result: Same output as current system, but modular architecture
```

### **Key Point**: 
**Standard mode produces IDENTICAL results to current workflow** but with better architecture for future enhancements.

---

## 4. Example 2: Library Mode (Pre-approved Formula)

### **User Request**:
```bash
python test_workflow.py --property_id=5 --formula="conservative_dscr"
```

### **Execution Flow**:

```
STEP 1: Orchestrator Receives Request
───────────────────────────────────────
Request: "Analyze property 5 with conservative DSCR formula"
Mode Detection: LIBRARY (formula specified)
Agent Plan: DataAgent → FormulaLibrary → CalculationAgent → AnalysisAgent → DecisionAgent

STEP 2: DataAgent Executes
───────────────────────────
(Same as Example 1)
Result:
  annual_noi: $2,700,000
  annual_debt_service: $2,000,000

STEP 3: FormulaLibrary Lookup
──────────────────────────────
Formula Name: "conservative_dscr"
Query: SELECT * FROM formula_library WHERE name = 'conservative_dscr'
Result:
  formula_id: "uuid-123"
  name: "conservative_dscr"
  category: "debt_service"
  description: "Conservative DSCR with 90% NOI assumption"
  code: |
    def calculate_conservative_dscr(annual_noi, annual_debt_service):
        """
        Conservative DSCR calculation that assumes only 90% of 
        projected NOI is achievable (10% buffer for uncertainty)
        """
        adjusted_noi = annual_noi * 0.90
        if annual_debt_service == 0:
            return None
        return adjusted_noi / annual_debt_service
  
  validation_status: APPROVED
  safety_score: 100.0
  usage_count: 247

STEP 4: CalculationAgent Executes (with library code)
──────────────────────────────────────────────────────
Input: Property data + library code
Execution: Run pre-approved function
Calculation:
  adjusted_noi = $2,700,000 × 0.90 = $2,430,000
  DSCR = $2,430,000 / $2,000,000 = 1.215

Validation: (different thresholds for conservative)
  dscr >= 1.30 → PASS (conservative standard)
  dscr >= 1.20 → MARGINAL
  dscr < 1.20 → FAIL
  
  Result: validation_status = "MARGINAL"

Output:
  dscr: 1.215 (vs 1.35 standard)
  validation_status: "MARGINAL"
  formula_used: "conservative_dscr"
  adjustment_factor: 0.90

STEP 5: AnalysisAgent Executes
───────────────────────────────
Input: DSCR=1.215 (conservative), validation=MARGINAL
LLM Call: "Analyze this conservative DSCR..."
LLM Response:
  "Using conservative assumptions (90% NOI achievement), Valley View 
   Center shows a DSCR of 1.215, which is marginally acceptable. 
   This suggests the property has limited buffer against NOI volatility. 
   Consider stress-testing assumptions or requiring additional reserves."

STEP 6: DecisionAgent Executes
───────────────────────────────
Input: DSCR=1.215, Analysis="marginally acceptable..."
LLM Response:
  Decision: ADJUST
  Confidence: 65%
  Reasoning: "Conservative analysis reveals thinner coverage. 
              Recommend parameter adjustment to improve cushion."
  Suggested Adjustments:
    - Increase equity contribution (reduce loan amount by 5%)
    - Extend loan term to reduce debt service
    - Negotiate lower interest rate

STEP 7: Loop Back (ADJUST decision)
────────────────────────────────────
Orchestrator: Send to CalculationAgent with adjusted parameters
New Parameters: loan_amount reduced by 5% → $26,600,000
New Calculation:
  New debt service = $1,900,000
  Conservative DSCR = $2,430,000 / $1,900,000 = 1.28
  validation_status = "PASS" (barely)

Result: After adjustment, property meets conservative criteria
```

### **Key Point**:
**Library mode allows using pre-approved custom formulas** without code generation, providing flexibility while maintaining security.

---

## 5. Example 3: Custom Mode (Code Generation)

### **User Request** (Natural Language):
```bash
python test_workflow.py --property_id=5 --custom-query="Analyze this property 
but calculate DSCR with a 15% stress test on NOI to account for potential 
tenant bankruptcies, and require DSCR > 1.30 for approval"
```

### **Execution Flow**:

```
STEP 1: Orchestrator Receives Request
───────────────────────────────────────
Request: "Analyze with 15% NOI stress test, require DSCR > 1.30"
Mode Detection: CUSTOM (requires code generation)
Requirements Extracted:
  - Metric: DSCR
  - Modification: 15% NOI haircut
  - Custom threshold: 1.30 (vs default 1.25)
  - Reason: Tenant bankruptcy risk

Agent Plan: 
  DataAgent → CodeGeneratorAgent → CodeValidator → 
  SandboxExecutor → AnalysisAgent → DecisionAgent

STEP 2: DataAgent Executes
───────────────────────────
(Same as Example 1)
Result:
  annual_noi: $2,700,000
  annual_debt_service: $2,000,000

STEP 3: CodeGeneratorAgent Executes
────────────────────────────────────
LLM Prompt:
  "Generate a Python function to calculate DSCR with the following 
   requirements:
   - Apply 15% stress test to NOI (85% of projected NOI)
   - Return DSCR value
   - Include docstring explaining the stress test
   - Use only standard Python math operations
   - No external imports allowed"

LLM Response (Generated Code):
  ```python
  def stress_tested_dscr(annual_noi, annual_debt_service, stress_factor=0.15):
      """
      Calculate DSCR with stress test applied to NOI.
      
      Args:
          annual_noi: Annual Net Operating Income
          annual_debt_service: Annual Debt Service payments
          stress_factor: Percentage reduction to apply (default 0.15 = 15%)
      
      Returns:
          DSCR value after stress testing NOI
      
      Example:
          If NOI = $1,000,000 and stress_factor = 0.15:
          Stressed NOI = $1,000,000 * (1 - 0.15) = $850,000
      """
      if annual_debt_service == 0:
          raise ValueError("Annual debt service cannot be zero")
      
      # Apply stress test: reduce NOI by stress_factor
      stressed_noi = annual_noi * (1.0 - stress_factor)
      
      # Calculate DSCR
      dscr = stressed_noi / annual_debt_service
      
      return {
          'dscr': dscr,
          'stressed_noi': stressed_noi,
          'original_noi': annual_noi,
          'stress_factor': stress_factor,
          'debt_service': annual_debt_service
      }
  ```

STEP 4: CodeValidator Executes
───────────────────────────────
Input: Generated code from LLM

Validation Checks:

✓ Check 1: Syntax Validation
  Result: PASS (valid Python syntax)

✓ Check 2: Import Analysis
  Imports found: None
  Result: PASS (no imports)

✓ Check 3: Dangerous Function Detection
  Searching for: exec, eval, __import__, subprocess, os.system, open, 
                 compile, getattr, setattr, delattr, dir
  Result: PASS (no dangerous functions)

✓ Check 4: AST Security Analysis
  - Variable assignments: OK
  - Function calls: OK (only math operations)
  - Loops: None
  - File I/O: None
  - Network calls: None
  Result: PASS

✓ Check 5: Complexity Analysis
  - Lines of code: 25
  - Cyclomatic complexity: 2
  - Max nesting depth: 1
  Result: PASS (under limits)

✓ Check 6: Resource Estimation
  - Estimated memory: <1MB
  - Estimated execution time: <10ms
  - No loops with variable bounds
  Result: PASS

Overall Validation Result:
  is_safe: True
  violations: []
  warnings: []
  risk_score: 0.0 (safe)
  approved_for_execution: True

STEP 5: SandboxExecutor Executes
─────────────────────────────────
Container Setup:
  Image: python:3.11-slim
  CPU Limit: 0.5 cores
  Memory Limit: 256MB
  Timeout: 10 seconds
  Network: Disabled
  Filesystem: Read-only except /tmp

Code Injection:
  1. Write generated function to /tmp/custom_formula.py
  2. Write input data to /tmp/input_data.json:
     {
       "annual_noi": 2700000,
       "annual_debt_service": 2000000,
       "stress_factor": 0.15
     }

Execution Script:
  ```python
  import json
  import sys
  
  # Load generated function
  exec(open('/tmp/custom_formula.py').read())
  
  # Load input data
  with open('/tmp/input_data.json') as f:
      data = json.load(f)
  
  # Execute function
  result = stress_tested_dscr(**data)
  
  # Write result
  with open('/tmp/output.json', 'w') as f:
      json.dump(result, f)
  ```

Container Execution:
  Start Time: 10:30:45.123
  Status: Running...
  Duration: 47ms
  Memory Used: 18MB
  Exit Code: 0
  
Result Retrieved from /tmp/output.json:
  {
    "dscr": 1.1475,
    "stressed_noi": 2295000,
    "original_noi": 2700000,
    "stress_factor": 0.15,
    "debt_service": 2000000
  }

Container Cleanup:
  Status: Destroyed
  Total Time: 127ms

STEP 6: CalculationAgent Validation
────────────────────────────────────
Input: DSCR=1.1475 (stressed)
Custom Threshold: 1.30 (user requirement)

Validation:
  dscr = 1.1475
  required = 1.30
  1.1475 < 1.30 → validation_status = "FAIL"

Output:
  dscr: 1.1475
  validation_status: "FAIL"
  threshold_required: 1.30
  gap: -0.1525 (15.25% below requirement)
  stressed_noi: $2,295,000
  original_noi: $2,700,000

STEP 7: AnalysisAgent Executes
───────────────────────────────
Input: DSCR=1.1475 (stressed), validation=FAIL
LLM Prompt:
  "Analyze this stress-tested DSCR result. The property has DSCR of 
   1.1475 after applying a 15% NOI stress test, but requires 1.30. 
   What does this mean for risk?"

LLM Response:
  "The stress-tested DSCR of 1.1475 falls short of the required 1.30 
   threshold, indicating elevated risk under adverse scenarios. With 
   a 15% NOI reduction (simulating tenant bankruptcies or vacancies), 
   the property would have insufficient coverage.
   
   Key Concerns:
   • Only 14.75% buffer above break-even under stress
   • Falls 15.25% below required threshold
   • Vulnerable to tenant credit events
   • May face debt service challenges if NOI declines
   
   Risk Level: MODERATE-HIGH under stress scenarios"

STEP 8: DecisionAgent Executes
───────────────────────────────
Input: 
  - DSCR=1.1475 (stressed)
  - Analysis: "elevated risk under adverse scenarios"
  - validation_status: FAIL
  - gap: -15.25%

LLM Prompt:
  "Given this stress-tested analysis showing DSCR below requirements, 
   what is your recommendation?"

LLM Response:
  Decision: ADJUST
  Confidence: 85%
  Reasoning: 
    "Property fails stress test requirements, indicating insufficient 
     resilience. However, gap is addressable through structural changes."
  
  Recommended Adjustments:
    1. REDUCE LOAN AMOUNT by 12%
       Current: $28M → Proposed: $24.64M
       Impact: Reduces debt service to ~$1,760,000
       New stressed DSCR: 1.30 (meets requirement)
    
    2. INCREASE EQUITY by $3.36M (from $12M to $15.36M)
       LTV: 70% → 61.6% (more conservative)
    
    3. REQUIRE DEBT SERVICE RESERVE
       Amount: $400,000 (6 months coverage)
       Purpose: Buffer for NOI volatility
    
    4. TENANT DIVERSIFICATION COVENANT
       Require: No single tenant > 15% of NOI
       Purpose: Reduce bankruptcy risk

STEP 9: Loop Back with Adjustments
───────────────────────────────────
Orchestrator: Apply suggested adjustments
New Parameters:
  loan_amount: $24,640,000 (reduced 12%)
  new_debt_service: $1,760,000
  reserve_fund: $400,000

Re-execute Custom Code:
  Input:
    annual_noi: $2,700,000
    annual_debt_service: $1,760,000
    stress_factor: 0.15
  
  Result:
    stressed_noi: $2,295,000
    dscr: 1.304
    validation_status: "PASS" (barely)

STEP 10: Final Decision
───────────────────────
DecisionAgent (2nd iteration):
  Decision: ACCEPT (with conditions)
  Confidence: 78%
  
  Conditions:
    ✓ Loan amount reduced to $24.64M
    ✓ Debt service reserve established: $400K
    ✓ Tenant concentration limits imposed
    ✓ Quarterly NOI monitoring required
  
  Reasoning:
    "After structural adjustments, property meets stress-tested 
     requirements. Conservative LTV and reserve fund provide 
     adequate protection against downside scenarios."

STEP 11: ReportingAgent Final Output
─────────────────────────────────────
Generated Report:

  ═══════════════════════════════════════════════════════
  STRESS-TESTED PROPERTY ANALYSIS REPORT
  ═══════════════════════════════════════════════════════
  Property: Valley View Center (Dallas, TX)
  Analysis Type: Custom Stress Test (15% NOI Reduction)
  Analysis Date: 2024-01-15 10:31:22
  
  CUSTOM REQUIREMENTS:
  • Stress Test: 15% NOI reduction (tenant bankruptcy scenario)
  • Required DSCR: ≥ 1.30 (vs standard 1.25)
  
  INITIAL ANALYSIS (Original Structure):
  • Standard DSCR: 1.35 ✓
  • Stressed DSCR: 1.1475 ✗ (FAILED stress test)
  • Gap: -15.25% below requirement
  
  RECOMMENDED STRUCTURE:
  • Loan Amount: $28.0M → $24.64M (↓12%)
  • Equity: $12.0M → $15.36M (↑28%)
  • LTV: 70.0% → 61.6% (↓8.4pp)
  • Debt Service: $2.0M/yr → $1.76M/yr
  
  FINAL METRICS (Adjusted Structure):
  • Standard DSCR: 1.53 ✓✓ (Improved)
  • Stressed DSCR: 1.304 ✓ (PASS)
  • Reserve Fund: $400K (6 months coverage)
  
  RISK ASSESSMENT:
  • Standard Scenario: LOW RISK (strong coverage)
  • Stress Scenario: MODERATE RISK (minimal coverage)
  • Mitigation: Reserve fund + tenant limits
  
  RECOMMENDATION: ACCEPT WITH CONDITIONS
  
  CONDITIONS:
  ✓ Implement revised capital structure
  ✓ Establish debt service reserve ($400K)
  ✓ Tenant concentration limits (max 15% per tenant)
  ✓ Quarterly NOI monitoring and reporting
  
  Confidence: 78%
  ═══════════════════════════════════════════════════════

Result: Custom analysis completed with code generation
```

### **Key Point**:
**Custom mode enables flexible, user-defined analysis** while maintaining security through validation and sandboxing.

---

## 6. Agent Implementation Details

### **6.1 DataAgent**

**Current Code Location**: `workflow.py` → `fetch_data_node()` (lines ~50-100)

**Agent Structure**:
```
DataAgent:
├── Capabilities:
│   ├── fetch_property_data(property_id)
│   ├── fetch_financial_metrics(property_id)
│   ├── validate_data_completeness()
│   └── handle_missing_data()
│
├── State Management:
│   ├── Input: property_id
│   └── Output: PropertyData (dict with all fields)
│
├── Error Handling:
│   ├── Property not found → Return clear error
│   ├── Missing metrics → Use defaults or fail gracefully
│   └── Database connection issues → Retry logic
│
└── Future Enhancements:
    ├── Support multiple data sources (APIs, files)
    ├── Data quality scoring
    ├── Historical data retrieval
    └── Real-time data updates
```

### **6.2 CalculationAgent**

**Current Code Location**: 
- `workflow.py` → `simulate_dscr_node()` (lines ~130-160)
- `workflow.py` → `validate_results_node()` (lines ~180-220)

**Agent Structure**:
```
CalculationAgent:
├── Capabilities:
│   ├── Mode 1: execute_standard_formula(data)
│   │   → Uses built-in DSCR calculation
│   │
│   ├── Mode 2: execute_library_formula(formula_id, data)
│   │   → Fetches pre-approved code from database
│   │   → Executes in-process (trusted)
│   │
│   ├── Mode 3: execute_custom_code(generated_code, data)
│   │   → Sends to SandboxExecutor
│   │   → Waits for sandboxed result
│   │
│   ├── validate_results(results, thresholds)
│   │   → Applies validation rules
│   │   → Returns PASS/MARGINAL/FAIL
│   │
│   └── calculate_supporting_metrics(data)
│       → LTV, Cap Rate, NOI margin, etc.
│
├── Validation Logic:
│   ├── Standard Thresholds (line 183):
│   │   • DSCR ≥ 1.25 → PASS
│   │   • DSCR ≥ 1.15 → MARGINAL
│   │   • DSCR < 1.15 → FAIL
│   │
│   ├── Custom Thresholds:
│   │   • User-defined via request
│   │   • Formula-specific defaults
│   │
│   └── Multi-Metric Validation:
│       • DSCR + LTV combined rules
│       • Occupancy + DSCR correlations
│
└── Output Format:
    {
      "primary_metric": 1.35,
      "validation_status": "PASS",
      "supporting_metrics": {...},
      "execution_mode": "standard|library|custom",
      "execution_time_ms": 45
    }
```

### **6.3 AnalysisAgent**

**Current Code Location**: `workflow_with_llm.py` → `analyze_results_node_llm()` (lines ~200-250)

**Agent Structure**:
```
AnalysisAgent:
├── LLM Integration:
│   ├── Prompt Template:
│   │   "Analyze the following financial metrics for {property_name}:
│   │    - DSCR: {dscr}
│   │    - LTV: {ltv}
│   │    - Cap Rate: {cap_rate}
│   │    - Validation: {validation_status}
│   │    
│   │    Provide:
│   │    1. Risk assessment
│   │    2. Key strengths
│   │    3. Key concerns
│   │    4. Market context"
│   │
│   ├── Response Parsing:
│   │   → Extract structured insights
│   │   → Identify risk factors
│   │   → Generate risk score
│   │
│   └── Confidence Scoring:
│       → Based on data completeness
│       → Based on metric thresholds
│
├── Pattern Recognition (Future):
│   ├── Compare to historical analyses
│   ├── Identify similar properties
│   ├── Detect anomalies
│   └── Market trend analysis
│
└── Output Format:
    {
      "analysis_text": "Property demonstrates...",
      "risk_level": "LOW|MODERATE|HIGH",
      "strengths": [...],
      "concerns": [...],
      "confidence": 0.92
    }
```

### **6.4 DecisionAgent**

**Current Code Location**: `workflow_with_llm.py` → `decide_next_step_llm()` (lines ~270-310)

**Agent Structure**:
```
DecisionAgent:
├── Decision Logic:
│   ├── Input Synthesis:
│   │   • Property metrics
│   │   • Analysis results
│   │   • Validation status
│   │   • Historical performance (future)
│   │
│   ├── LLM Decision:
│   │   Prompt: "Based on the analysis, recommend:
│   │            - ACCEPT (ready for approval)
│   │            - ADJUST (needs modification)
│   │            - REJECT (fundamental issues)"
│   │
│   └── Decision Criteria:
│       • Validation status weight: 40%
│       • Risk assessment weight: 30%
│       • Market conditions weight: 20%
│       • Property fundamentals weight: 10%
│
├── Adjustment Suggestions:
│   If decision == ADJUST:
│     → Call adjust_parameters_node_llm
│     → Suggest specific changes:
│         • Increase equity
│         • Extend loan term
│         • Reduce loan amount
│         • Improve property NOI
│
└── Output Format:
    {
      "decision": "ACCEPT|ADJUST|REJECT",
      "confidence": 0.85,
      "reasoning": "Strong coverage ratio...",
      "suggested_adjustments": [...],
      "next_action": "approve|adjust|escalate"
    }
```

### **6.5 CodeGeneratorAgent** (NEW)

**Agent Structure**:
```
CodeGeneratorAgent:
├── Input Processing:
│   ├── Parse user requirements:
│   │   • Metric to calculate
│   │   • Custom modifications
│   │   • Validation thresholds
│   │   • Special conditions
│   │
│   └── Extract constraints:
│       • Allowed operations
│       • Required outputs
│       • Performance limits
│
├── Code Generation:
│   ├── LLM Prompt:
│   │   "Generate a Python function that:
│   │    - Calculates {metric} with {modifications}
│   │    - Takes inputs: {input_params}
│   │    - Returns: {output_format}
│   │    - Restrictions: {constraints}
│   │    - Include docstring and examples
│   │    - Use only standard Python (no imports)"
│   │
│   ├── Response Processing:
│   │   • Extract code from LLM response
│   │   • Remove markdown formatting
│   │   • Validate syntax
│   │
│   └── Metadata Tracking:
│       • Generation timestamp
│       • Model used
│       • Token count
│       • Requirements hash
│
├── Code Validation:
│   └── Send to CodeValidator (next step)
│
└── Output Format:
    {
      "generated_code": "def custom_metric(...)...",
      "code_hash": "sha256...",
      "metadata": {...},
      "validation_pending": true
    }
```

### **6.6 OrchestratorAgent** (NEW)

**Agent Structure**:
```
OrchestratorAgent:
├── Request Classification:
│   ├── Analyze user input:
│   │   • Standard request? → Mode 1
│   │   • Library formula? → Mode 2
│   │   • Custom requirements? → Mode 3
│   │
│   ├── Extract requirements:
│   │   • Property ID
│   │   • Metric(s) requested
│   │   • Custom modifications
│   │   • Output format
│   │
│   └── Determine execution plan:
│       • Which agents to call
│       • In what order
│       • Parallel vs sequential
│
├── Agent Coordination:
│   ├── Sequential Flow:
│   │   Agent1 → wait → Agent2 → wait → Agent3
│   │
│   ├── Parallel Flow:
│   │   Agent1 ──┐
│   │   Agent2 ──┼→ Merge → Next
│   │   Agent3 ──┘
│   │
│   └── Conditional Flow:
│       Agent1 → Decision → {
│         If PASS → Agent2A
│         If FAIL → Agent2B
│       }
│
├── State Management:
│   ├── Initialize state:
│   │   {
│   │     "request_id": "uuid",
│   │     "mode": "standard|library|custom",
│   │     "property_id": 5,
│   │     "execution_plan": [...]
│   │   }
│   │
│   ├── Update after each agent:
│   │   • Append results
│   │   • Track timing
│   │   • Log decisions
│   │
│   └── Handle loops:
│       • ADJUST decision → re-run calculation
│       • Max iterations: 3
│       • Track convergence
│
├── Error Handling:
│   ├── Agent failures:
│   │   • Retry logic (max 3)
│   │   • Fallback agents
│   │   • Graceful degradation
│   │
│   ├── Validation failures:
│   │   • Clear error messages
│   │   • Suggested fixes
│   │   • Escalation path
│   │
│   └── Timeout handling:
│       • Per-agent timeouts
│       • Overall timeout
│       • Partial result return
│
└── Monitoring & Logging:
    ├── Log every agent call
    ├── Track execution time
    ├── Measure LLM costs
    └── Generate execution trace
```

---

## 7. Code Generation Examples

### **Example 7.1: Custom DSCR with Seasonal Adjustment**

**User Query**:
```
"Calculate DSCR but adjust NOI for seasonality - reduce by 20% 
 for winter months (Nov-Feb) since this is a beach resort property"
```

**Generated Code**:
```python
def seasonal_dscr(annual_noi, annual_debt_service, current_month):
    """
    Calculate DSCR with seasonal NOI adjustment.
    
    Beach resort properties experience 20% NOI reduction
    during winter months (November through February).
    
    Args:
        annual_noi: Annual Net Operating Income (full year projection)
        annual_debt_service: Annual debt service obligation
        current_month: Current month (1-12)
    
    Returns:
        Dictionary with DSCR and seasonally-adjusted metrics
    """
    if annual_debt_service == 0:
        raise ValueError("Debt service cannot be zero")
    
    # Winter months: November (11), December (12), January (1), February (2)
    winter_months = [11, 12, 1, 2]
    
    # Calculate seasonal adjustment
    if current_month in winter_months:
        # Winter: 20% reduction for 4 months = 1/3 of year
        # Annual impact: (8 months * 100% + 4 months * 80%) / 12
        seasonal_factor = (8 * 1.0 + 4 * 0.8) / 12  # = 0.9333
    else:
        # Peak season: no adjustment
        seasonal_factor = 1.0
    
    adjusted_noi = annual_noi * seasonal_factor
    dscr = adjusted_noi / annual_debt_service
    
    return {
        'dscr': dscr,
        'original_noi': annual_noi,
        'adjusted_noi': adjusted_noi,
        'seasonal_factor': seasonal_factor,
        'current_month': current_month,
        'is_winter': current_month in winter_months
    }
```

**Validation**: ✓ PASS (safe, no dangerous operations)

**Execution Result**:
```json
{
  "dscr": 1.26,
  "original_noi": 2700000,
  "adjusted_noi": 2519991,
  "seasonal_factor": 0.9333,
  "current_month": 1,
  "is_winter": true
}
```

---

### **Example 7.2: Multi-Property Portfolio DSCR**

**User Query**:
```
"Calculate portfolio-level DSCR across all my properties, 
 weighted by property value"
```

**Generated Code**:
```python
def portfolio_dscr(properties_data):
    """
    Calculate portfolio-level DSCR weighted by property value.
    
    Args:
        properties_data: List of dictionaries with:
            - property_value: float
            - annual_noi: float
            - annual_debt_service: float
    
    Returns:
        Portfolio metrics including weighted DSCR
    """
    total_value = 0.0
    total_noi = 0.0
    total_debt_service = 0.0
    
    property_metrics = []
    
    for prop in properties_data:
        value = prop['property_value']
        noi = prop['annual_noi']
        debt_service = prop['annual_debt_service']
        
        # Individual property DSCR
        if debt_service > 0:
            prop_dscr = noi / debt_service
        else:
            prop_dscr = None
        
        property_metrics.append({
            'value': value,
            'noi': noi,
            'debt_service': debt_service,
            'dscr': prop_dscr,
            'weight': 0  # Will calculate after total known
        })
        
        total_value += value
        total_noi += noi
        total_debt_service += debt_service
    
    # Calculate weights and weighted DSCR
    for prop_metric in property_metrics:
        prop_metric['weight'] = prop_metric['value'] / total_value
    
    # Portfolio-level DSCR
    if total_debt_service > 0:
        portfolio_dscr = total_noi / total_debt_service
    else:
        portfolio_dscr = None
    
    return {
        'portfolio_dscr': portfolio_dscr,
        'total_value': total_value,
        'total_noi': total_noi,
        'total_debt_service': total_debt_service,
        'property_count': len(properties_data),
        'property_metrics': property_metrics
    }
```

**Validation**: ✓ PASS (safe, standard operations only)

---

### **Example 7.3: Monte Carlo DSCR Simulation** (REJECTED)

**User Query**:
```
"Run a Monte Carlo simulation on DSCR with 10,000 scenarios"
```

**Generated Code**:
```python
import numpy as np
import random

def monte_carlo_dscr(annual_noi, annual_debt_service, n_simulations=10000):
    """
    Monte Carlo simulation for DSCR analysis.
    """
    results = []
    for i in range(n_simulations):
        # Randomize NOI (±20% volatility)
        noi_scenario = annual_noi * (1 + random.uniform(-0.2, 0.2))
        dscr_scenario = noi_scenario / annual_debt_service
        results.append(dscr_scenario)
    
    return {
        'mean_dscr': np.mean(results),
        'p5_dscr': np.percentile(results, 5),
        'p95_dscr': np.percentile(results, 95),
        'scenarios': results
    }
```

**Validation**: ✗ FAIL

**Violations**:
- ❌ Uses `import numpy` (not whitelisted for basic tier)
- ❌ Uses `import random` (can introduce non-determinism)
- ❌ High complexity (10,000 iterations)
- ❌ Returns large array (memory concern)

**Error Message**:
```
Code validation failed:
• Restricted import: numpy (requires approval)
• Restricted import: random (non-deterministic behavior)
• Complexity warning: Loop with 10,000 iterations
• Memory warning: Returns array of 10,000 elements

Suggestions:
1. Reduce simulation count to < 1,000
2. Use math library instead of numpy
3. Request approval for advanced analytics tier
4. Return summary statistics only (not full array)
```

---

## 8. Security & Validation Flow

### **Complete Security Pipeline**:

```
USER INPUT
    ↓
┌─────────────────────────────────────────┐
│ LAYER 1: Input Validation              │
├─────────────────────────────────────────┤
│ • Sanitize user query                   │
│ • Check for injection attempts          │
│ • Validate property_id format           │
│ • Rate limiting                          │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ LAYER 2: Code Generation (if custom)   │
├─────────────────────────────────────────┤
│ • LLM prompt safety                     │
│ • Constrain LLM output                  │
│ • Extract code from response            │
│ • Basic syntax check                    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ LAYER 3: Static Analysis               │
├─────────────────────────────────────────┤
│ ✓ AST parsing                           │
│ ✓ Import whitelist check                │
│ ✓ Function blacklist check              │
│ ✓ Complexity analysis                   │
│ ✓ Variable scope analysis               │
│ ✓ Data access patterns                  │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ LAYER 4: Sandbox Execution             │
├─────────────────────────────────────────┤
│ Docker Container:                       │
│  • Isolated filesystem                  │
│  • No network access                    │
│  • CPU limit: 0.5 cores                 │
│  • Memory limit: 256MB                  │
│  • Timeout: 10 seconds                  │
│  • Read-only code                       │
│  • Temp output only                     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ LAYER 5: Result Validation             │
├─────────────────────────────────────────┤
│ • Check output format                   │
│ • Validate value ranges                 │
│ • Detect anomalies                      │
│ • Compare to expected bounds            │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ LAYER 6: Audit Logging                 │
├─────────────────────────────────────────┤
│ • Log all generated code                │
│ • Log execution results                 │
│ • Log user identity                     │
│ • Track resource usage                  │
│ • Alert on suspicious patterns          │
└─────────────────────────────────────────┘
                  ↓
              RESULTS
```

### **Whitelist Management**:

**Approved Imports (Basic Tier)**:
```
Standard Library Only:
  ✓ math        - Mathematical functions
  ✓ datetime    - Date/time operations
  ✓ decimal     - Precise decimal arithmetic
  ✓ fractions   - Rational number arithmetic
  ✓ statistics  - Basic statistics
  ✓ collections - Data structures (limited)

Forbidden:
  ✗ os, sys, subprocess - System access
  ✗ socket, urllib, requests - Network
  ✗ pickle, marshal - Serialization
  ✗ exec, eval, compile - Dynamic execution
  ✗ open, file - File I/O
  ✗ __import__, importlib - Dynamic imports
```

**Advanced Tier (Requires Approval)**:
```
  ✓ numpy      - Numerical operations
  ✓ pandas     - Data manipulation
  ✓ scipy      - Scientific computing
  ✓ matplotlib - Plotting (output only)
```

---

## 9. Complete Execution Trace

### **Trace for Example 3 (Custom Mode)**:

```
═══════════════════════════════════════════════════════════════
EXECUTION TRACE: Custom DSCR Analysis with Stress Test
═══════════════════════════════════════════════════════════════
Request ID: req_20240115_103045_abc123
Property ID: 5
Mode: CUSTOM
User: analyst@company.com
Timestamp: 2024-01-15 10:30:45

───────────────────────────────────────────────────────────────
[10:30:45.001] ORCHESTRATOR: Request received
───────────────────────────────────────────────────────────────
Input: "Analyze property 5 with 15% NOI stress test, require DSCR > 1.30"
Classification: CUSTOM (code generation required)
Extracted Requirements:
  • Metric: DSCR
  • Modification: 15% NOI stress
  • Threshold: 1.30
  • Reason: Tenant bankruptcy risk

Agent Plan Created:
  Step 1: DataAgent
  Step 2: CodeGeneratorAgent
  Step 3: CodeValidator
  Step 4: SandboxExecutor
  Step 5: CalculationAgent
  Step 6: AnalysisAgent
  Step 7: DecisionAgent
  Step 8: ReportingAgent

───────────────────────────────────────────────────────────────
[10:30:45.023] AGENT: DataAgent START
───────────────────────────────────────────────────────────────
Action: Fetch property data
Query: SELECT * FROM properties WHERE id = 5
Duration: 12ms
Result: Valley View Center (Dallas, TX)

Query: SELECT * FROM financial_metrics WHERE property_id = 5
Duration: 8ms
Result:
  annual_noi: $2,700,000
  annual_debt_service: $2,000,000
  property_value: $40,000,000
  loan_amount: $28,000,000

Validation: Data complete ✓
Output: PropertyData (8 fields)

───────────────────────────────────────────────────────────────
[10:30:45.051] AGENT: CodeGeneratorAgent START
───────────────────────────────────────────────────────────────
Action: Generate custom DSCR function
LLM Model: qwen3-4b-2507
LLM Temperature: 0.1
Prompt Length: 342 tokens

Prompt:
  "Generate a Python function to calculate DSCR with:
   - 15% stress test on NOI (multiply by 0.85)
   - Return DSCR value and stressed NOI
   - Include docstring
   - Use only standard Python
   - No imports allowed"

LLM Call Duration: 2,347ms
Response Tokens: 256
Cost: $0.0012

Generated Code: (25 lines)
  def stress_tested_dscr(annual_noi, annual_debt_service, stress_factor=0.15):
      ...

Code Hash: sha256:a7f3c...

───────────────────────────────────────────────────────────────
[10:30:47.412] AGENT: CodeValidator START
───────────────────────────────────────────────────────────────
Action: Validate generated code
Code Hash: sha256:a7f3c...

Check 1: Syntax Validation
  Parser: ast.parse()
  Result: ✓ PASS (valid Python 3.11)

Check 2: Import Analysis
  Imports Found: None
  Blacklisted: None
  Result: ✓ PASS

Check 3: Function Blacklist
  Searching: exec, eval, compile, __import__, ...
  Found: None
  Result: ✓ PASS

Check 4: Security Patterns
  File I/O: None
  Network: None
  System Calls: None
  Dynamic Execution: None
  Result: ✓ PASS

Check 5: Complexity
  Lines: 25
  Cyclomatic Complexity: 2
  Max Depth: 1
  Loops: 0
  Result: ✓ PASS (under limits)

Check 6: Resource Estimation
  Memory: <1MB
  Execution Time: <10ms
  Result: ✓ PASS

Overall Result: APPROVED FOR EXECUTION ✓
Risk Score: 0.0
Violations: 0
Warnings: 0

───────────────────────────────────────────────────────────────
[10:30:47.489] AGENT: SandboxExecutor START
───────────────────────────────────────────────────────────────
Action: Execute in Docker sandbox
Container: python:3.11-slim

Container Setup:
  CPU Limit: 0.5 cores
  Memory Limit: 256MB
  Network: DISABLED
  Timeout: 10 seconds
  Filesystem: Read-only + /tmp

Files Injected:
  /tmp/formula.py (generated code)
  /tmp/input.json (property data)

Execution Command:
  python /tmp/executor.py

Container Start: 10:30:47.512
Container Status: Running...
  [10:30:47.523] Loading function...
  [10:30:47.531] Loading input data...
  [10:30:47.542] Executing calculation...
  [10:30:47.559] Writing output...
Container Exit: 10:30:47.564

Duration: 52ms
Memory Used: 18.4MB
Exit Code: 0

Output Retrieved: /tmp/output.json
Result:
  {
    "dscr": 1.1475,
    "stressed_noi": 2295000,
    "original_noi": 2700000,
    "stress_factor": 0.15,
    "debt_service": 2000000
  }

Container Cleanup: Destroyed ✓

───────────────────────────────────────────────────────────────
[10:30:47.621] AGENT: CalculationAgent START
───────────────────────────────────────────────────────────────
Action: Validate DSCR result
Input: DSCR = 1.1475
Threshold: 1.30 (custom)

Validation:
  1.1475 < 1.30
  Gap: -0.1525 (15.25% below)
  Result: ✗ FAIL

Supporting Metrics:
  LTV: 70.0%
  Cap Rate: 6.75%
  NOI Margin: 13.5%

Output: validation_status = "FAIL"

───────────────────────────────────────────────────────────────
[10:30:47.634] AGENT: AnalysisAgent START
───────────────────────────────────────────────────────────────
Action: Analyze failed validation
LLM Model: qwen3-4b-2507
LLM Call Duration: 2,891ms

Prompt:
  "Analyze DSCR of 1.1475 (stressed) vs required 1.30.
   Property: Valley View Center
   Context: 15% NOI stress test for tenant bankruptcy risk"

LLM Response:
  "The stress-tested DSCR of 1.1475 falls short of the 1.30 
   threshold, indicating elevated risk under adverse scenarios.
   With a 15% NOI reduction, the property would have insufficient 
   coverage. Risk Level: MODERATE-HIGH under stress."

Analysis Output:
  risk_level: "MODERATE-HIGH"
  confidence: 88%
  concerns: ["Insufficient buffer", "Vulnerable to NOI decline"]

───────────────────────────────────────────────────────────────
[10:30:50.541] AGENT: DecisionAgent START
───────────────────────────────────────────────────────────────
Action: Make approval decision
Input: DSCR FAIL + MODERATE-HIGH risk
LLM Call Duration: 3,122ms

LLM Response:
  Decision: ADJUST
  Reasoning: "Gap is addressable through structural changes"
  
Suggested Adjustments:
  1. Reduce loan amount by 12% ($28M → $24.64M)
  2. Increase equity ($12M → $15.36M)
  3. Add debt service reserve ($400K)
  4. Tenant concentration limits

───────────────────────────────────────────────────────────────
[10:30:53.678] ORCHESTRATOR: Decision = ADJUST, Initiating Loop
───────────────────────────────────────────────────────────────
Loop Iteration: 2/3
Applying Adjustments:
  loan_amount: $28M → $24.64M
  debt_service: $2M → $1.76M

Re-executing: SandboxExecutor → CalculationAgent

───────────────────────────────────────────────────────────────
[10:30:53.701] AGENT: SandboxExecutor START (Iteration 2)
───────────────────────────────────────────────────────────────
Using cached code (same formula)
New Input:
  annual_noi: $2,700,000
  annual_debt_service: $1,760,000
  stress_factor: 0.15

Result:
  dscr: 1.304
  stressed_noi: $2,295,000

Duration: 43ms (faster due to warm container)

───────────────────────────────────────────────────────────────
[10:30:53.749] AGENT: CalculationAgent START (Iteration 2)
───────────────────────────────────────────────────────────────
Input: DSCR = 1.304
Threshold: 1.30

Validation:
  1.304 >= 1.30
  Gap: +0.004 (0.4% above)
  Result: ✓ PASS (barely)

───────────────────────────────────────────────────────────────
[10:30:53.762] AGENT: DecisionAgent START (Iteration 2)
───────────────────────────────────────────────────────────────
Action: Re-evaluate with adjusted structure
LLM Call Duration: 2,234ms

LLM Response:
  Decision: ACCEPT (with conditions)
  Confidence: 78%
  
Conditions:
  ✓ Loan reduction implemented
  ✓ Reserve fund required
  ✓ Tenant monitoring required

───────────────────────────────────────────────────────────────
[10:30:56.012] AGENT: ReportingAgent START
───────────────────────────────────────────────────────────────
Action: Generate final report
Format: Console (text)
Duration: 45ms

Report Generated: 1,247 characters
Sections:
  • Header
  • Custom Requirements
  • Initial Analysis (FAIL)
  • Recommended Structure
  • Final Metrics (PASS)
  • Risk Assessment
  • Recommendation
  • Conditions

───────────────────────────────────────────────────────────────
[10:30:56.063] EXECUTION COMPLETE
───────────────────────────────────────────────────────────────
Total Duration: 11.062 seconds
Agents Called: 8 (DataAgent, CodeGeneratorAgent, CodeValidator,
                   SandboxExecutor x2, CalculationAgent x2,
                   AnalysisAgent, DecisionAgent x2, ReportingAgent)
LLM Calls: 4
LLM Tokens: 1,847 tokens
Iterations: 2
Final Decision: ACCEPT (with conditions)

Resource Usage:
  CPU Time: 4.2 seconds
  Memory Peak: 342MB
  Database Queries: 4
  Docker Containers: 2
  Cost: $0.0089

═══════════════════════════════════════════════════════════════
```

---

## ✅ **Summary**

This document demonstrates:

1. ✅ **Current workflow** preserved in Standard Mode
2. ✅ **Library formulas** enable pre-approved customization
3. ✅ **Code generation** enables unlimited flexibility
4. ✅ **Multi-agent system** improves modularity
5. ✅ **Security layers** ensure safe execution
6. ✅ **Complete traceability** for audit and debugging

**Result**: A flexible, secure, and powerful evolution of the existing DSCR POC! 🚀

