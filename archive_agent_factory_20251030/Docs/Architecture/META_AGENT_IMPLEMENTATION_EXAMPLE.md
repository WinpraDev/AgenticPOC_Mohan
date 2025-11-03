# 🤖 Meta-Agent Implementation: Tool-Calling Agent Writer

**Complete Example: From User Request → Generated Agents**

---

## 📋 Table of Contents

1. [Meta-Agent Overview](#meta-agent-overview)
2. [Tool Catalog](#tool-catalog)
3. [Complete Implementation Flow](#complete-implementation-flow)
4. [Example 1: Simple DSCR Request](#example-1-simple-dscr-request)
5. [Example 2: Complex Multi-Mode Request](#example-2-complex-multi-mode-request)
6. [Meta-Agent Decision Making](#meta-agent-decision-making)
7. [Error Handling & Recovery](#error-handling--recovery)

---

## 1. Meta-Agent Overview

### **Meta-Agent Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    META-AGENT (Agent Writer)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Core Capabilities:                                          │
│  ├─ Natural Language Understanding (LLM-powered)             │
│  ├─ Requirement Analysis                                     │
│  ├─ Agent Design & Specification                            │
│  ├─ Code Generation via Tool Calling                        │
│  ├─ Code Validation & Testing                               │
│  └─ Deployment & Documentation                              │
│                                                              │
│  LLM Configuration:                                          │
│  ├─ Model: GPT-4 / Claude / Qwen-Coder                      │
│  ├─ Temperature: 0.1 (deterministic)                        │
│  ├─ Max Tokens: 8000                                         │
│  └─ Tool Calling: Enabled                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────┐
        │         AVAILABLE TOOLS             │
        ├─────────────────────────────────────┤
        │ 1.  analyze_requirements            │
        │ 2.  design_agent_architecture       │
        │ 3.  generate_agent_specification    │
        │ 4.  validate_specification          │
        │ 5.  generate_agent_code             │
        │ 6.  validate_code_syntax            │
        │ 7.  validate_code_security          │
        │ 8.  generate_unit_tests             │
        │ 9.  run_tests                       │
        │ 10. generate_documentation          │
        │ 11. write_file                      │
        │ 12. read_file                       │
        │ 13. create_directory                │
        │ 14. deploy_agent                    │
        │ 15. verify_agent_health             │
        └─────────────────────────────────────┘
```

### **Meta-Agent Workflow Pattern**

```
USER REQUEST (Natural Language)
    ↓
Meta-Agent receives and analyzes
    ↓
Meta-Agent thinks: "I need to generate 2 agents for DSCR analysis"
    ↓
Meta-Agent makes tool calls:
    ├─ Tool 1: analyze_requirements(user_request)
    ├─ Tool 2: design_agent_architecture(requirements)
    ├─ Tool 3: generate_agent_specification(design)
    ├─ Tool 4: generate_agent_code(spec)
    ├─ Tool 5: validate_code(code)
    ├─ Tool 6: generate_unit_tests(code)
    ├─ Tool 7: run_tests(tests)
    └─ Tool 8: deploy_agent(validated_code)
    ↓
AGENTS DEPLOYED & READY
```

---

## 2. Tool Catalog

### **Tool 1: analyze_requirements**
```
Name: analyze_requirements
Purpose: Extract structured requirements from natural language request
Input: user_request (string)
Output: {
  "primary_goal": string,
  "required_agents": list[string],
  "data_sources": list[string],
  "calculations_needed": list[string],
  "modes_required": list[string],
  "validation_rules": list[string],
  "output_format": string,
  "constraints": list[string]
}
```

### **Tool 2: design_agent_architecture**
```
Name: design_agent_architecture
Purpose: Design the agent system architecture
Input: requirements (dict from Tool 1)
Output: {
  "agents": [
    {
      "agent_name": string,
      "agent_type": string,
      "role": string,
      "responsibilities": list[string],
      "dependencies": list[string],
      "complexity": string
    }
  ],
  "interactions": [
    {
      "from": string,
      "to": string,
      "type": string
    }
  ],
  "data_flow": string
}
```

### **Tool 3: generate_agent_specification**
```
Name: generate_agent_specification
Purpose: Create detailed YAML specification for an agent
Input: {
  "agent_name": string,
  "architecture_design": dict,
  "requirements": dict
}
Output: yaml_specification (string)
```

### **Tool 4: validate_specification**
```
Name: validate_specification
Purpose: Validate specification against schema
Input: yaml_specification (string)
Output: {
  "valid": boolean,
  "errors": list[string],
  "warnings": list[string],
  "suggestions": list[string]
}
```

### **Tool 5: generate_agent_code**
```
Name: generate_agent_code
Purpose: Generate Python code from specification (LLM-powered)
Input: {
  "specification": yaml_specification,
  "template": string (optional),
  "style_guide": string (optional)
}
Output: {
  "code": string,
  "metadata": {
    "lines": int,
    "complexity": string,
    "dependencies": list[string]
  }
}
```

### **Tool 6: validate_code_syntax**
```
Name: validate_code_syntax
Purpose: Parse and validate Python syntax
Input: code (string)
Output: {
  "valid": boolean,
  "syntax_errors": list[string],
  "ast": dict (if valid)
}
```

### **Tool 7: validate_code_security**
```
Name: validate_code_security
Purpose: Check for security vulnerabilities
Input: code (string)
Output: {
  "safe": boolean,
  "security_issues": list[dict],
  "risk_score": float,
  "recommendations": list[string]
}
```

### **Tool 8: generate_unit_tests**
```
Name: generate_unit_tests
Purpose: Generate pytest tests for agent (LLM-powered)
Input: {
  "agent_code": string,
  "specification": yaml,
  "test_scenarios": list[dict]
}
Output: test_code (string)
```

### **Tool 9: run_tests**
```
Name: run_tests
Purpose: Execute test suite
Input: {
  "test_file": string,
  "test_type": string (unit/integration)
}
Output: {
  "passed": int,
  "failed": int,
  "errors": list[dict],
  "coverage": float
}
```

### **Tool 10: generate_documentation**
```
Name: generate_documentation
Purpose: Create markdown documentation
Input: {
  "agent_code": string,
  "specification": yaml,
  "examples": list[dict]
}
Output: documentation_markdown (string)
```

### **Tool 11: write_file**
```
Name: write_file
Purpose: Write content to filesystem
Input: {
  "path": string,
  "content": string,
  "overwrite": boolean
}
Output: {
  "success": boolean,
  "path": string,
  "bytes_written": int
}
```

### **Tool 12: read_file**
```
Name: read_file
Purpose: Read file from filesystem
Input: path (string)
Output: {
  "content": string,
  "exists": boolean,
  "size": int
}
```

### **Tool 13: create_directory**
```
Name: create_directory
Purpose: Create directory structure
Input: path (string)
Output: {
  "success": boolean,
  "path": string
}
```

### **Tool 14: deploy_agent**
```
Name: deploy_agent
Purpose: Deploy agent to runtime environment
Input: {
  "agent_name": string,
  "code_path": string,
  "config": dict
}
Output: {
  "deployed": boolean,
  "endpoint": string,
  "health_status": string
}
```

### **Tool 15: verify_agent_health**
```
Name: verify_agent_health
Purpose: Check if agent is operational
Input: agent_name (string)
Output: {
  "healthy": boolean,
  "response_time_ms": int,
  "errors": list[string]
}
```

---

## 3. Complete Implementation Flow

### **Meta-Agent Internal Process**

```
═══════════════════════════════════════════════════════════════
META-AGENT EXECUTION FLOW
═══════════════════════════════════════════════════════════════

PHASE 1: Understanding
├─ Receive user request
├─ Use LLM to understand intent
├─ Extract key requirements
└─ Plan generation strategy

PHASE 2: Architecture Design
├─ Determine number of agents needed
├─ Define agent responsibilities
├─ Design data flow
└─ Plan integration points

PHASE 3: Specification Generation
├─ For each agent:
│   ├─ Create YAML specification
│   ├─ Validate specification
│   └─ Store specification
└─ Generate integration specs

PHASE 4: Code Generation
├─ For each agent:
│   ├─ Generate Python code from spec
│   ├─ Validate syntax
│   ├─ Validate security
│   ├─ Generate tests
│   ├─ Run tests
│   └─ Fix if needed (iterate)
└─ Generate integration code

PHASE 5: Documentation & Deployment
├─ Generate documentation
├─ Create deployment configs
├─ Deploy agents
├─ Verify health
└─ Report success

═══════════════════════════════════════════════════════════════
```

---

## 4. Example 1: Simple DSCR Request

### **User Request**

```
USER: "I need an agent system to calculate DSCR for commercial 
properties. Fetch data from PostgreSQL and calculate the debt 
service coverage ratio. Use the formula: annual NOI divided by 
annual debt service. Validate that DSCR is above 1.25."
```

### **Meta-Agent Execution Trace**

```
═══════════════════════════════════════════════════════════════
META-AGENT SESSION START
═══════════════════════════════════════════════════════════════
Timestamp: 2024-01-15 14:30:00
User: analyst@company.com
Request ID: req_20240115_143000

───────────────────────────────────────────────────────────────
[14:30:00.001] META-AGENT: Request Received
───────────────────────────────────────────────────────────────

User Request:
  "I need an agent system to calculate DSCR for commercial 
   properties. Fetch data from PostgreSQL and calculate the debt 
   service coverage ratio. Use the formula: annual NOI divided by 
   annual debt service. Validate that DSCR is above 1.25."

───────────────────────────────────────────────────────────────
[14:30:00.025] META-AGENT: Internal Reasoning (LLM)
───────────────────────────────────────────────────────────────

Meta-Agent thinks:
  "Let me analyze this request:
   
   1. Primary goal: Calculate DSCR for properties
   2. Data source: PostgreSQL
   3. Calculation: NOI / Debt Service
   4. Validation: DSCR >= 1.25
   5. No mention of multiple modes or custom formulas
   
   Architecture needed:
   - DataAgent: Simple tool to fetch data from PostgreSQL
   - CalcAgent: Calculate DSCR, validate, return result
   
   This is a straightforward 2-agent system.
   
   I should:
   1. Analyze requirements in detail
   2. Design architecture
   3. Generate specifications
   4. Generate code
   5. Test and deploy"

───────────────────────────────────────────────────────────────
[14:30:00.156] META-AGENT: Tool Call #1
───────────────────────────────────────────────────────────────

Tool: analyze_requirements
Input:
  {
    "user_request": "I need an agent system to calculate DSCR..."
  }

Tool Execution Time: 234ms

Tool Response:
  {
    "primary_goal": "Calculate DSCR for commercial properties",
    "required_agents": ["DataAgent", "CalcAgent"],
    "data_sources": ["PostgreSQL"],
    "calculations_needed": [
      {
        "name": "DSCR",
        "formula": "annual_noi / annual_debt_service",
        "inputs": ["annual_noi", "annual_debt_service"]
      }
    ],
    "modes_required": ["standard"],
    "validation_rules": [
      {
        "metric": "DSCR",
        "condition": ">= 1.25",
        "status_if_pass": "PASS",
        "status_if_fail": "FAIL"
      }
    ],
    "output_format": "structured_result",
    "constraints": [
      "Use PostgreSQL for data",
      "Simple calculation (no stress tests)",
      "Basic validation only"
    ],
    "complexity": "LOW",
    "estimated_agents": 2
  }

Meta-Agent: "Requirements extracted successfully. Proceeding to architecture design."

───────────────────────────────────────────────────────────────
[14:30:00.398] META-AGENT: Tool Call #2
───────────────────────────────────────────────────────────────

Tool: design_agent_architecture
Input:
  {
    "requirements": {... from Tool #1 ...}
  }

Tool Execution Time: 445ms

Tool Response:
  {
    "agents": [
      {
        "agent_name": "DataAgent",
        "agent_type": "data_retrieval",
        "role": "tool",
        "responsibilities": [
          "Connect to PostgreSQL database",
          "Fetch property data by property_id",
          "Fetch financial metrics (NOI, debt service)",
          "Validate data completeness",
          "Handle database errors"
        ],
        "dependencies": ["psycopg2", "sqlalchemy"],
        "complexity": "LOW"
      },
      {
        "agent_name": "CalcAgent",
        "agent_type": "calculation",
        "role": "primary_agent",
        "responsibilities": [
          "Call DataAgent to get property data",
          "Calculate DSCR using formula",
          "Validate DSCR against threshold (1.25)",
          "Return structured result",
          "Handle calculation errors"
        ],
        "dependencies": ["DataAgent", "pydantic", "loguru"],
        "complexity": "LOW",
        "uses_llm": false
      }
    ],
    "interactions": [
      {
        "from": "CalcAgent",
        "to": "DataAgent",
        "type": "tool_call",
        "method": "fetch_property_data"
      }
    ],
    "data_flow": "User → CalcAgent → DataAgent → CalcAgent → User",
    "no_orchestrator_needed": true,
    "reasoning": "Simple single-metric calculation requires only 2 agents"
  }

Meta-Agent: "Architecture designed. DataAgent is a simple tool, CalcAgent is the smart agent."

───────────────────────────────────────────────────────────────
[14:30:00.851] META-AGENT: Decision Point
───────────────────────────────────────────────────────────────

Meta-Agent thinks:
  "I need to generate 2 agents:
   1. DataAgent (simpler, generate first)
   2. CalcAgent (depends on DataAgent, generate second)
   
   For each agent:
   - Generate specification
   - Generate code
   - Validate code
   - Generate tests
   - Run tests
   
   Let's start with DataAgent."

───────────────────────────────────────────────────────────────
[14:30:00.867] META-AGENT: Generating DataAgent
───────────────────────────────────────────────────────────────

Meta-Agent: "Starting DataAgent generation..."

───────────────────────────────────────────────────────────────
[14:30:00.872] META-AGENT: Tool Call #3
───────────────────────────────────────────────────────────────

Tool: generate_agent_specification
Input:
  {
    "agent_name": "DataAgent",
    "architecture_design": {
      "agent_type": "data_retrieval",
      "role": "tool",
      "responsibilities": [...]
    },
    "requirements": {... from Tool #1 ...}
  }

Tool Execution Time: 1,234ms (LLM generates YAML)

Tool Response:
  {
    "specification": """
agent_name: DataAgent
agent_type: data_retrieval
version: 1.0.0
description: Fetches property and financial data from PostgreSQL

role: tool

capabilities:
  - name: fetch_property_data
    description: Retrieve property data by ID
    inputs:
      - name: property_id
        type: integer
        required: true
    outputs:
      - name: property_data
        type: dict
        schema:
          property_id: int
          annual_noi: float
          annual_debt_service: float

data_sources:
  - type: postgresql
    connection: ${DATABASE_URL}
    tables:
      - properties
      - financial_metrics

dependencies:
  python_packages:
    - psycopg2-binary==2.9.9
    - sqlalchemy==2.0.23

performance:
  timeout_seconds: 30
""",
    "validation_status": "pending"
  }

───────────────────────────────────────────────────────────────
[14:30:02.112] META-AGENT: Tool Call #4
───────────────────────────────────────────────────────────────

Tool: validate_specification
Input:
  {
    "specification": "agent_name: DataAgent\n..."
  }

Tool Execution Time: 89ms

Tool Response:
  {
    "valid": true,
    "errors": [],
    "warnings": [],
    "suggestions": [
      "Consider adding retry logic for database connections"
    ]
  }

Meta-Agent: "DataAgent specification validated successfully."

───────────────────────────────────────────────────────────────
[14:30:02.206] META-AGENT: Tool Call #5
───────────────────────────────────────────────────────────────

Tool: write_file
Input:
  {
    "path": "agent_specs/data_agent.yaml",
    "content": "agent_name: DataAgent\n...",
    "overwrite": false
  }

Tool Response:
  {
    "success": true,
    "path": "agent_specs/data_agent.yaml",
    "bytes_written": 432
  }

───────────────────────────────────────────────────────────────
[14:30:02.215] META-AGENT: Tool Call #6
───────────────────────────────────────────────────────────────

Tool: generate_agent_code
Input:
  {
    "specification": "agent_name: DataAgent\n...",
    "template": "agent_base_template",
    "style_guide": "pep8"
  }

Tool Execution Time: 3,456ms (LLM generates Python code)

Tool Response:
  {
    "code": """
from typing import Dict, Optional
from sqlalchemy import create_engine, text
from loguru import logger
import os

class DataAgent:
    '''
    DataAgent: Fetches property and financial data from PostgreSQL.
    Acts as a tool for CalcAgent.
    '''
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.database_url, pool_pre_ping=True)
        logger.info('DataAgent initialized')
    
    def fetch_property_data(self, property_id: int) -> Dict:
        '''
        Fetch property data from database.
        
        Args:
            property_id: Unique property identifier
        
        Returns:
            Dictionary with property_id, annual_noi, annual_debt_service
        
        Raises:
            ValueError: If property not found
            Exception: For database errors
        '''
        try:
            query = text('''
                SELECT 
                    p.id as property_id,
                    fm.annual_noi,
                    fm.annual_debt_service
                FROM properties p
                JOIN financial_metrics fm ON p.id = fm.property_id
                WHERE p.id = :property_id
            ''')
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {'property_id': property_id})
                row = result.fetchone()
                
                if row is None:
                    raise ValueError(f'Property {property_id} not found')
                
                return {
                    'property_id': row.property_id,
                    'annual_noi': float(row.annual_noi),
                    'annual_debt_service': float(row.annual_debt_service)
                }
        
        except Exception as e:
            logger.error(f'Error fetching property {property_id}: {e}')
            raise
""",
    "metadata": {
      "lines": 52,
      "complexity": "LOW",
      "dependencies": ["sqlalchemy", "loguru", "psycopg2"]
    }
  }

Meta-Agent: "DataAgent code generated. Validating..."

───────────────────────────────────────────────────────────────
[14:30:05.678] META-AGENT: Tool Call #7
───────────────────────────────────────────────────────────────

Tool: validate_code_syntax
Input:
  {
    "code": "from typing import Dict...\n..."
  }

Tool Response:
  {
    "valid": true,
    "syntax_errors": []
  }

───────────────────────────────────────────────────────────────
[14:30:05.723] META-AGENT: Tool Call #8
───────────────────────────────────────────────────────────────

Tool: validate_code_security
Input:
  {
    "code": "from typing import Dict...\n..."
  }

Tool Response:
  {
    "safe": true,
    "security_issues": [],
    "risk_score": 0.0,
    "recommendations": [
      "Good: Using parameterized queries",
      "Good: Using connection pooling",
      "Good: Proper error handling"
    ]
  }

Meta-Agent: "DataAgent code is safe. Generating tests..."

───────────────────────────────────────────────────────────────
[14:30:05.767] META-AGENT: Tool Call #9
───────────────────────────────────────────────────────────────

Tool: generate_unit_tests
Input:
  {
    "agent_code": "from typing import Dict...\n...",
    "specification": "agent_name: DataAgent\n...",
    "test_scenarios": [
      {"name": "happy_path", "property_id": 5},
      {"name": "not_found", "property_id": 99999}
    ]
  }

Tool Execution Time: 2,134ms (LLM generates tests)

Tool Response:
  {
    "test_code": """
import pytest
from unittest.mock import Mock, patch
from src.agents.data_agent import DataAgent

def test_fetch_property_data_happy_path():
    '''Test successful data retrieval'''
    agent = DataAgent()
    
    # Mock database response
    mock_row = Mock()
    mock_row.property_id = 5
    mock_row.annual_noi = 2700000.0
    mock_row.annual_debt_service = 2000000.0
    
    with patch.object(agent.engine, 'connect') as mock_connect:
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = mock_row
        mock_conn.execute.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = agent.fetch_property_data(5)
        
        assert result['property_id'] == 5
        assert result['annual_noi'] == 2700000.0
        assert result['annual_debt_service'] == 2000000.0

def test_fetch_property_data_not_found():
    '''Test property not found error'''
    agent = DataAgent()
    
    with patch.object(agent.engine, 'connect') as mock_connect:
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        with pytest.raises(ValueError, match='Property 99999 not found'):
            agent.fetch_property_data(99999)
"""
  }

───────────────────────────────────────────────────────────────
[14:30:07.908] META-AGENT: Tool Call #10
───────────────────────────────────────────────────────────────

Tool: write_file
Input:
  {
    "path": "src/agents/data_agent.py",
    "content": "from typing import Dict...\n..."
  }

Tool Response:
  {
    "success": true,
    "path": "src/agents/data_agent.py"
  }

───────────────────────────────────────────────────────────────
[14:30:07.921] META-AGENT: Tool Call #11
───────────────────────────────────────────────────────────────

Tool: write_file
Input:
  {
    "path": "tests/agents/test_data_agent.py",
    "content": "import pytest\n..."
  }

Tool Response:
  {
    "success": true,
    "path": "tests/agents/test_data_agent.py"
  }

───────────────────────────────────────────────────────────────
[14:30:07.934] META-AGENT: Tool Call #12
───────────────────────────────────────────────────────────────

Tool: run_tests
Input:
  {
    "test_file": "tests/agents/test_data_agent.py",
    "test_type": "unit"
  }

Tool Execution Time: 567ms

Tool Response:
  {
    "passed": 2,
    "failed": 0,
    "errors": [],
    "coverage": 94.2
  }

Meta-Agent: "✓ DataAgent tests passed! DataAgent is complete."

───────────────────────────────────────────────────────────────
[14:30:08.506] META-AGENT: Generating CalcAgent
───────────────────────────────────────────────────────────────

Meta-Agent: "DataAgent complete. Now generating CalcAgent..."

───────────────────────────────────────────────────────────────
[14:30:08.523] META-AGENT: Tool Call #13
───────────────────────────────────────────────────────────────

Tool: generate_agent_specification
Input:
  {
    "agent_name": "CalcAgent",
    "architecture_design": {
      "agent_type": "calculation",
      "role": "primary_agent",
      "uses_tool": "DataAgent",
      "responsibilities": [...]
    },
    "requirements": {... from Tool #1 ...}
  }

Tool Execution Time: 1,789ms (LLM generates YAML)

Tool Response:
  {
    "specification": """
agent_name: CalcAgent
agent_type: calculation
version: 1.0.0
description: Calculates and validates DSCR for properties

role: primary_agent

uses_tools:
  - DataAgent

capabilities:
  - name: calculate_dscr
    description: Calculate DSCR and validate
    inputs:
      - name: property_id
        type: integer
        required: true
      - name: validation_threshold
        type: float
        default: 1.25
    outputs:
      - name: result
        type: dict
        schema:
          property_id: int
          dscr: float
          validation_status: str
          annual_noi: float
          annual_debt_service: float

calculation:
  formula: annual_noi / annual_debt_service
  validation_rules:
    - dscr >= 1.25: PASS
    - dscr < 1.25: FAIL

dependencies:
  python_packages:
    - pydantic==2.5.0
    - loguru==0.7.2
  internal_agents:
    - DataAgent
"""
  }

───────────────────────────────────────────────────────────────
[14:30:10.318] META-AGENT: Tool Call #14
───────────────────────────────────────────────────────────────

Tool: validate_specification
Input: {CalcAgent spec}

Tool Response:
  {
    "valid": true,
    "errors": [],
    "warnings": []
  }

───────────────────────────────────────────────────────────────
[14:30:10.412] META-AGENT: Tool Call #15
───────────────────────────────────────────────────────────────

Tool: write_file
Input: {Save CalcAgent spec}

───────────────────────────────────────────────────────────────
[14:30:10.425] META-AGENT: Tool Call #16
───────────────────────────────────────────────────────────────

Tool: generate_agent_code
Input:
  {
    "specification": "agent_name: CalcAgent\n...",
    "template": "agent_base_template"
  }

Tool Execution Time: 4,234ms (LLM generates Python code)

Tool Response:
  {
    "code": """
from typing import Dict
from pydantic import BaseModel
from loguru import logger
from src.agents.data_agent import DataAgent

class DSCRResult(BaseModel):
    property_id: int
    dscr: float
    validation_status: str
    annual_noi: float
    annual_debt_service: float

class CalcAgent:
    '''
    CalcAgent: Calculates and validates DSCR for properties.
    Uses DataAgent to fetch data.
    '''
    
    def __init__(self):
        self.data_agent = DataAgent()
        logger.info('CalcAgent initialized')
    
    def calculate_dscr(
        self, 
        property_id: int, 
        validation_threshold: float = 1.25
    ) -> DSCRResult:
        '''
        Calculate DSCR for a property.
        
        Args:
            property_id: Property to analyze
            validation_threshold: Minimum acceptable DSCR
        
        Returns:
            DSCRResult with calculation and validation
        '''
        logger.info(f'Calculating DSCR for property {property_id}')
        
        # Step 1: Fetch data using DataAgent
        property_data = self.data_agent.fetch_property_data(property_id)
        
        annual_noi = property_data['annual_noi']
        annual_debt_service = property_data['annual_debt_service']
        
        # Step 2: Calculate DSCR
        if annual_debt_service == 0:
            raise ValueError('Annual debt service cannot be zero')
        
        dscr = annual_noi / annual_debt_service
        
        # Step 3: Validate
        if dscr >= validation_threshold:
            validation_status = 'PASS'
        else:
            validation_status = 'FAIL'
        
        # Step 4: Return result
        result = DSCRResult(
            property_id=property_id,
            dscr=dscr,
            validation_status=validation_status,
            annual_noi=annual_noi,
            annual_debt_service=annual_debt_service
        )
        
        logger.info(
            f'DSCR calculated: {dscr:.2f}, Status: {validation_status}'
        )
        
        return result
""",
    "metadata": {
      "lines": 68,
      "complexity": "LOW"
    }
  }

───────────────────────────────────────────────────────────────
[14:30:14.665] META-AGENT: Tool Call #17 & #18
───────────────────────────────────────────────────────────────

Tool: validate_code_syntax (✓ PASS)
Tool: validate_code_security (✓ PASS, risk_score: 0.0)

───────────────────────────────────────────────────────────────
[14:30:14.789] META-AGENT: Tool Call #19
───────────────────────────────────────────────────────────────

Tool: generate_unit_tests
Input: {CalcAgent code + spec}

Tool Response:
  {
    "test_code": """
import pytest
from src.agents.calc_agent import CalcAgent, DSCRResult

def test_calculate_dscr_pass():
    '''Test DSCR calculation - passing case'''
    agent = CalcAgent()
    
    # Mock DataAgent response
    agent.data_agent.fetch_property_data = lambda x: {
        'property_id': 5,
        'annual_noi': 2700000.0,
        'annual_debt_service': 2000000.0
    }
    
    result = agent.calculate_dscr(5)
    
    assert result.property_id == 5
    assert result.dscr == 1.35
    assert result.validation_status == 'PASS'

def test_calculate_dscr_fail():
    '''Test DSCR calculation - failing case'''
    agent = CalcAgent()
    
    agent.data_agent.fetch_property_data = lambda x: {
        'property_id': 9,
        'annual_noi': 1000000.0,
        'annual_debt_service': 900000.0
    }
    
    result = agent.calculate_dscr(9)
    
    assert result.dscr == 1.111
    assert result.validation_status == 'FAIL'
"""
  }

───────────────────────────────────────────────────────────────
[14:30:16.923] META-AGENT: Tool Calls #20, #21, #22
───────────────────────────────────────────────────────────────

Tool: write_file (CalcAgent code)
Tool: write_file (CalcAgent tests)
Tool: run_tests (✓ 2/2 tests passed)

Meta-Agent: "✓ CalcAgent tests passed! CalcAgent is complete."

───────────────────────────────────────────────────────────────
[14:30:17.501] META-AGENT: Generating Documentation
───────────────────────────────────────────────────────────────

───────────────────────────────────────────────────────────────
[14:30:17.515] META-AGENT: Tool Call #23
───────────────────────────────────────────────────────────────

Tool: generate_documentation
Input:
  {
    "agents": ["DataAgent", "CalcAgent"],
    "specifications": [...],
    "examples": [...]
  }

Tool Response:
  {
    "documentation": """
# DSCR Agent System

## Overview
This system calculates Debt Service Coverage Ratio (DSCR) for 
commercial properties using a 2-agent architecture.

## Agents

### DataAgent
Fetches property data from PostgreSQL.

Usage:
  data_agent = DataAgent()
  data = data_agent.fetch_property_data(5)

### CalcAgent
Calculates DSCR and validates result.

Usage:
  calc_agent = CalcAgent()
  result = calc_agent.calculate_dscr(5)
  print(result.dscr, result.validation_status)

## Example
  calc_agent = CalcAgent()
  result = calc_agent.calculate_dscr(property_id=5)
  
  Output:
    DSCRResult(
      property_id=5,
      dscr=1.35,
      validation_status='PASS',
      annual_noi=2700000.0,
      annual_debt_service=2000000.0
    )
"""
  }

───────────────────────────────────────────────────────────────
[14:30:19.678] META-AGENT: Tool Call #24
───────────────────────────────────────────────────────────────

Tool: write_file
Input:
  {
    "path": "docs/SYSTEM_OVERVIEW.md",
    "content": "# DSCR Agent System\n..."
  }

───────────────────────────────────────────────────────────────
[14:30:19.692] META-AGENT: Final Summary
───────────────────────────────────────────────────────────────

Meta-Agent: "Generation complete! Summary:"

Agents Generated: 2
  ✓ DataAgent (52 lines, 2 tests)
  ✓ CalcAgent (68 lines, 2 tests)

Files Created: 6
  ✓ agent_specs/data_agent.yaml
  ✓ agent_specs/calc_agent.yaml
  ✓ src/agents/data_agent.py
  ✓ src/agents/calc_agent.py
  ✓ tests/agents/test_data_agent.py
  ✓ tests/agents/test_calc_agent.py
  ✓ docs/SYSTEM_OVERVIEW.md

Tests: 4/4 passed
Coverage: 92.5%

Time Elapsed: 19.7 seconds
Tool Calls Made: 24
LLM Calls: 4 (spec generation, code generation x2, docs)

System Status: ✓ READY TO USE

═══════════════════════════════════════════════════════════════
META-AGENT SESSION END
═══════════════════════════════════════════════════════════════
```

### **Generated File Structure**

```
project_root/
├── agent_specs/
│   ├── data_agent.yaml        (Generated by Tool #3)
│   └── calc_agent.yaml        (Generated by Tool #13)
│
├── src/agents/
│   ├── data_agent.py          (Generated by Tool #6)
│   └── calc_agent.py          (Generated by Tool #16)
│
├── tests/agents/
│   ├── test_data_agent.py     (Generated by Tool #9)
│   └── test_calc_agent.py     (Generated by Tool #19)
│
└── docs/
    └── SYSTEM_OVERVIEW.md     (Generated by Tool #23)
```

---

## 5. Example 2: Complex Multi-Mode Request

### **User Request**

```
USER: "Build me a DSCR analysis system that supports three modes:
1. Standard calculation (simple NOI/debt service)
2. Conservative mode that applies a 10% haircut to NOI
3. Custom mode where I can describe stress tests in natural language 
   and the system generates the code for me

Also need LLM-powered analysis to interpret results and make 
recommendations. If DSCR is marginal, suggest parameter adjustments."
```

### **Meta-Agent Execution (Abbreviated)**

```
═══════════════════════════════════════════════════════════════
META-AGENT SESSION START - Complex Request
═══════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────
[15:00:00.001] META-AGENT: Request Received
───────────────────────────────────────────────────────────────

Meta-Agent thinks:
  "This is significantly more complex:
   - 3 execution modes (standard, library, custom)
   - Custom mode requires code generation capability
   - Need LLM integration for analysis
   - Need decision-making logic
   - Need adjustment loop
   
   This requires:
   - DataAgent (same as before)
   - CalcAgent (much more complex):
       * Mode detection
       * Standard calculator
       * Library calculator
       * Custom calculator (with code gen + sandbox)
       * LLM integration
       * Decision engine
       * Adjustment loop
   
   This is a HIGH complexity request."

───────────────────────────────────────────────────────────────
[15:00:00.234] META-AGENT: Tool Call #1 - analyze_requirements
───────────────────────────────────────────────────────────────

Tool Response:
  {
    "primary_goal": "Multi-mode DSCR analysis with AI decision-making",
    "required_agents": ["DataAgent", "CalcAgent"],
    "modes_required": ["standard", "library", "custom"],
    "calculations_needed": [
      "standard_dscr",
      "conservative_dscr",
      "custom_dscr (code-generated)"
    ],
    "llm_integration": true,
    "llm_purposes": ["analysis", "decision_making", "code_generation"],
    "features_required": [
      "Mode detection",
      "Code generation for custom mode",
      "Code validation",
      "Sandbox execution",
      "LLM analysis",
      "Parameter adjustment suggestions",
      "Iterative refinement"
    ],
    "complexity": "HIGH",
    "estimated_agents": 2,
    "estimated_components": 8
  }

───────────────────────────────────────────────────────────────
[15:00:00.567] META-AGENT: Tool Call #2 - design_agent_architecture
───────────────────────────────────────────────────────────────

Tool Response:
  {
    "agents": [
      {
        "agent_name": "DataAgent",
        "complexity": "LOW",
        "same_as_simple_example": true
      },
      {
        "agent_name": "CalcAgent",
        "complexity": "HIGH",
        "internal_components": [
          "ModeDetector",
          "StandardCalculator",
          "LibraryCalculator",
          "CustomCalculator",
          "CodeGenerator",
          "CodeValidator",
          "SandboxExecutor",
          "AnalysisEngine (LLM)",
          "DecisionEngine (LLM)",
          "AdjustmentLoop",
          "ReportGenerator"
        ],
        "external_dependencies": [
          "DataAgent",
          "LLMClient",
          "FormulaLibrary (database)",
          "Docker (for sandbox)"
        ]
      }
    ],
    "estimated_code_lines": {
      "DataAgent": 150,
      "CalcAgent": 800
    }
  }

───────────────────────────────────────────────────────────────
[15:00:00.923] META-AGENT: Decision
───────────────────────────────────────────────────────────────

Meta-Agent thinks:
  "CalcAgent is very complex with 11 internal components.
   
   Strategy:
   1. Generate DataAgent (same as before, ~2 minutes)
   2. Generate CalcAgent specification (complex, ~3 minutes)
   3. Generate CalcAgent code in modular fashion:
      - Main CalcAgent class
      - Each component as separate module
      - Integration code
   4. This will take longer (~8 minutes for CalcAgent)
   
   Total estimated time: 10-12 minutes"

───────────────────────────────────────────────────────────────
[15:00:01.000] META-AGENT: Generating DataAgent
───────────────────────────────────────────────────────────────

(Same process as Example 1)

✓ DataAgent complete in 2.1 minutes

───────────────────────────────────────────────────────────────
[15:02:07.500] META-AGENT: Generating CalcAgent (Complex)
───────────────────────────────────────────────────────────────

───────────────────────────────────────────────────────────────
Tool Call: generate_agent_specification
───────────────────────────────────────────────────────────────

Meta-Agent → LLM:
  "Generate a comprehensive YAML specification for CalcAgent with:
   - 3 execution modes
   - Code generation capability
   - LLM integration
   - All features from requirements"

LLM generates 350-line YAML specification (takes 3.2 minutes)

Specification includes:
  - Mode detection logic
  - All 11 components defined
  - Tool integrations
  - Workflow steps
  - Error handling
  - Testing scenarios

───────────────────────────────────────────────────────────────
Tool Call: generate_agent_code
───────────────────────────────────────────────────────────────

Meta-Agent → LLM:
  "Generate Python code for CalcAgent from this specification.
   Create modular components.
   Main class should orchestrate components."

LLM generates:
  1. calc_agent.py (main class, 200 lines)
  2. calc_agent_mode_detector.py (100 lines)
  3. calc_agent_standard.py (150 lines)
  4. calc_agent_library.py (200 lines)
  5. calc_agent_custom.py (400 lines)
     - Includes CodeGenerator
     - Includes CodeValidator
     - Includes SandboxExecutor
  6. calc_agent_analysis.py (200 lines)
  7. calc_agent_decision.py (180 lines)
  8. calc_agent_report.py (150 lines)

Total: 1,580 lines across 8 files

Generation time: 6.8 minutes (multiple LLM calls)

───────────────────────────────────────────────────────────────
Tool Calls: Validation
───────────────────────────────────────────────────────────────

validate_code_syntax: ✓ All 8 files valid
validate_code_security: ✓ All safe
  Warning: Custom mode uses Docker sandbox (as intended)

───────────────────────────────────────────────────────────────
Tool Call: generate_unit_tests
───────────────────────────────────────────────────────────────

LLM generates 25 test cases across 3 test files:
  - test_calc_agent.py (15 tests)
  - test_calc_agent_custom.py (8 tests)
  - test_integration.py (2 tests)

───────────────────────────────────────────────────────────────
Tool Call: run_tests
───────────────────────────────────────────────────────────────

Running tests...

Results:
  ✓ 23/25 tests passed
  ✗ 2/25 tests failed:
    - test_custom_mode_sandbox_execution (timeout)
    - test_adjustment_loop_max_iterations (assertion error)

───────────────────────────────────────────────────────────────
[15:10:34.500] META-AGENT: Error Recovery
───────────────────────────────────────────────────────────────

Meta-Agent thinks:
  "2 tests failed. I need to fix these issues.
   
   Issue 1: Sandbox timeout - need to increase timeout
   Issue 2: Adjustment loop - off-by-one error in iteration count
   
   I'll regenerate the affected components."

───────────────────────────────────────────────────────────────
Tool Call: generate_agent_code (targeted fix)
───────────────────────────────────────────────────────────────

Meta-Agent → LLM:
  "Regenerate calc_agent_custom.py with sandbox_timeout=30 instead of 10"

Meta-Agent → LLM:
  "Fix calc_agent_decision.py adjustment loop to correctly track iterations"

Regeneration time: 1.2 minutes

───────────────────────────────────────────────────────────────
Tool Call: run_tests (retry)
───────────────────────────────────────────────────────────────

Results:
  ✓ 25/25 tests passed
  Coverage: 89.3%

Meta-Agent: "All tests passed! CalcAgent is complete."

───────────────────────────────────────────────────────────────
[15:12:15.800] META-AGENT: Final Summary
───────────────────────────────────────────────────────────────

Agents Generated: 2
  ✓ DataAgent (150 lines, 2 tests)
  ✓ CalcAgent (1,580 lines across 8 files, 25 tests)

Total Files Created: 18
  - 2 specifications
  - 9 source files
  - 4 test files
  - 3 documentation files

Tests: 27/27 passed
Coverage: 90.1%

Time Elapsed: 12 minutes 16 seconds
Tool Calls Made: 47
LLM Calls: 12

Features Implemented:
  ✓ 3 execution modes (standard, library, custom)
  ✓ Code generation for custom mode
  ✓ Code validation & sandbox execution
  ✓ LLM-powered analysis
  ✓ Decision making with confidence scores
  ✓ Parameter adjustment suggestions
  ✓ Iterative refinement loop (max 3 iterations)
  ✓ Comprehensive error handling

System Status: ✓ READY FOR PRODUCTION

═══════════════════════════════════════════════════════════════
```

---

## 6. Meta-Agent Decision Making

### **6.1 How Meta-Agent Reasons**

The Meta-Agent uses its LLM to reason about each step:

```
USER REQUEST
    ↓
Meta-Agent Internal Dialogue:

"Let me break this down:
 - User wants to calculate DSCR
 - Data from PostgreSQL
 - Simple formula mentioned
 - Basic validation
 
 This is a straightforward request.
 
 Architecture decision:
 - Need data fetching → DataAgent
 - Need calculation → CalcAgent
 - No mention of complex features
 - No LLM analysis requested
 
 Complexity assessment: LOW
 
 Generation strategy:
 1. Generate simple DataAgent first (easier)
 2. Then generate CalcAgent (depends on DataAgent)
 3. Keep both agents simple
 4. Should complete in ~2 minutes per agent
 
 Let me start with analyzing requirements..."

[Makes tool call: analyze_requirements]

"Okay, requirements confirmed my assessment.
 Next, I need to design the architecture..."

[Makes tool call: design_agent_architecture]

"Architecture looks good. 2 agents, simple interaction.
 Now I'll generate specifications..."

[Makes tool call: generate_agent_specification]

"Specification generated. Let me validate it..."

[Makes tool call: validate_specification]

"Valid! Now I can generate the code..."

[Makes tool call: generate_agent_code]

"Code generated. Critical: I must validate before proceeding..."

[Makes tool call: validate_code_syntax]
[Makes tool call: validate_code_security]

"Code is safe. Now I need tests to ensure correctness..."

[Makes tool call: generate_unit_tests]

"Tests generated. Let me run them to verify everything works..."

[Makes tool call: run_tests]

"All tests passed! This agent is complete.
 Moving on to the next agent..."
```

### **6.2 Adaptive Strategy**

Meta-Agent adapts its strategy based on complexity:

```
IF complexity == LOW:
    Strategy:
      - Generate sequentially
      - Simple specifications
      - Minimal components
      - Basic tests
      - Fast generation
    
    Expected time: 2-4 minutes per agent

ELIF complexity == MEDIUM:
    Strategy:
      - Generate sequentially
      - Detailed specifications
      - Modular components
      - Comprehensive tests
      - Careful validation
    
    Expected time: 5-8 minutes per agent

ELIF complexity == HIGH:
    Strategy:
      - Break into smaller components
      - Generate component by component
      - Extensive testing
      - Iterative refinement
      - Multiple validation passes
    
    Expected time: 10-15 minutes per agent

IF tests fail:
    Strategy:
      - Analyze failure
      - Identify root cause
      - Regenerate affected component only
      - Retry tests
      - Max 3 retry attempts
```

### **6.3 Self-Correction**

When errors occur, Meta-Agent fixes them:

```
───────────────────────────────────────────────────────────────
EXAMPLE: Test Failure Recovery
───────────────────────────────────────────────────────────────

[15:10:30] Test failed: test_custom_mode_sandbox_execution
Error: "Sandbox execution timed out after 10 seconds"

Meta-Agent thinks:
  "Test failed due to timeout. Let me analyze:
   - Sandbox timeout set to 10 seconds
   - Custom code generation can take longer
   - This is a configuration issue, not a logic bug
   
   Solution: Increase sandbox timeout to 30 seconds
   
   I need to:
   1. Regenerate calc_agent_custom.py with updated timeout
   2. Re-run tests
   3. Verify fix works"

[Makes tool call: generate_agent_code with specific instructions]

"Code regenerated with timeout=30. Running tests again..."

[Makes tool call: run_tests]

"✓ Test passed! Issue resolved."
```

---

## 7. Error Handling & Recovery

### **7.1 Common Errors and Solutions**

```
ERROR TYPE 1: Code Syntax Error
────────────────────────────────
Detection: validate_code_syntax returns errors
Meta-Agent Action:
  1. Analyze syntax error message
  2. Regenerate code with fix instructions
  3. Re-validate
  4. Max 3 attempts

Example:
  Error: "Missing colon after function definition"
  Fix: Regenerate with explicit instruction: "Ensure all function 
       definitions have colons"

ERROR TYPE 2: Security Violation
────────────────────────────────
Detection: validate_code_security flags dangerous code
Meta-Agent Action:
  1. Identify specific security issue
  2. Regenerate with security constraints
  3. Re-validate
  4. If still fails after 3 attempts, alert user

Example:
  Error: "Code uses eval() function"
  Fix: Regenerate with instruction: "Do not use eval, exec, or 
       any dynamic code execution"

ERROR TYPE 3: Test Failures
────────────────────────────────
Detection: run_tests returns failures
Meta-Agent Action:
  1. Analyze test failure details
  2. Determine if logic error or config issue
  3. Regenerate affected component
  4. Re-run tests

Example:
  Error: "Expected DSCR 1.35, got 1.30"
  Analysis: Calculation error or test expectation wrong
  Fix: Review calculation logic, regenerate if needed

ERROR TYPE 4: Specification Validation Error
────────────────────────────────────────────
Detection: validate_specification returns errors
Meta-Agent Action:
  1. Identify schema violation
  2. Regenerate specification with corrections
  3. Re-validate

Example:
  Error: "Missing required field: agent_type"
  Fix: Regenerate spec ensuring all required fields present

ERROR TYPE 5: LLM Generation Failure
────────────────────────────────────
Detection: LLM returns invalid or incomplete response
Meta-Agent Action:
  1. Retry with refined prompt
  2. Add explicit output format requirements
  3. If still fails, use template fallback

Example:
  Error: LLM returns code without proper structure
  Fix: Regenerate with explicit structure template
```

### **7.2 Recovery Flow**

```
ATTEMPT 1: Initial Generation
    ↓
Validation
    ↓
    ├─ PASS → Continue
    │
    └─ FAIL → Analyze Error
                  ↓
              ATTEMPT 2: Regenerate with fix
                  ↓
              Validation
                  ↓
                  ├─ PASS → Continue
                  │
                  └─ FAIL → Refine fix
                              ↓
                          ATTEMPT 3: Regenerate with refined fix
                              ↓
                          Validation
                              ↓
                              ├─ PASS → Continue
                              │
                              └─ FAIL → Alert user, provide diagnostics
```

---

## ✅ Summary

### **Key Points**

1. **Meta-Agent is Tool-Powered**
   - Uses 15+ specialized tools
   - Makes intelligent decisions about which tools to call
   - Adapts strategy based on complexity

2. **Natural Language → Working Code**
   - Accepts natural language requests
   - Analyzes requirements
   - Generates complete agent systems
   - Tests and validates everything

3. **Self-Correcting**
   - Validates at every step
   - Detects and fixes errors
   - Iterates until tests pass

4. **Efficient**
   - Simple agents: 2-4 minutes
   - Complex agents: 10-15 minutes
   - Fully automated

5. **Complete System Generation**
   - Source code
   - Tests
   - Documentation
   - Specifications
   - Deployment configs

### **Meta-Agent Value Proposition**

**Instead of:**
- Manually coding 2 agents (2-3 days)
- Writing tests (1 day)
- Writing documentation (0.5 day)
- Total: 3-4 days

**Meta-Agent does:**
- Everything in 10-20 minutes
- Higher consistency
- Comprehensive tests
- Complete documentation
- Ready to deploy

**Result: 100x faster agent development! 🚀**

