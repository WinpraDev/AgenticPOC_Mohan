# Backend Technical Workflow - Meta-Agent Script Executor

**Complete Implementation Guide**  
**Version:** 2.0  
**Date:** November 3, 2025  
**Status:** Production

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Component Interaction Map](#component-interaction-map)
3. [Detailed Step-by-Step Workflow](#detailed-step-by-step-workflow)
4. [Tool Descriptions & Usage](#tool-descriptions--usage)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [LLM Integration Details](#llm-integration-details)
7. [Database Operations](#database-operations)
8. [Container Lifecycle Management](#container-lifecycle-management)
9. [Error Handling & Recovery](#error-handling--recovery)
10. [Results Processing Pipeline](#results-processing-pipeline)

---

## System Architecture Overview

### High-Level Component Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                  │
│              (Natural Language Request String)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SCRIPT EXECUTOR                                  │
│                  (script_executor.py)                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  1. Initialize Environment                                   │ │
│  │     - Load environment variables                             │ │
│  │     - Configure logger (loguru)                              │ │
│  │     - Set up output directories                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  2. Initialize LLM Client                                    │ │
│  │     - Connect to LM Studio (localhost:1234)                  │ │
│  │     - Verify Qwen2.5-Coder-7B-Instruct-MLX loaded            │ │
│  │     - Set temperature, max_tokens                            │ │
│  │     - Perform health check (NO FALLBACKS)                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  3. Database Schema Inspection (if DB detected)              │ │
│  │     - Parse DATABASE_URL from environment                    │ │
│  │     - Connect via SQLAlchemy                                 │ │
│  │     - Extract tables, columns, relationships                 │ │
│  │     - Format schema for LLM consumption                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                              │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Task      │→ │  Execution   │→ │   Script     │             │
│  │  Analyzer   │  │   Planner    │  │  Generator   │             │
│  └─────────────┘  └──────────────┘  └──────────────┘             │
│         │                 │                  │                     │
│         ▼                 ▼                  ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         LLM CLIENT (LM Studio + Qwen2.5-Coder-7B-MLX)       │  │
│  │   - Local inference (NO OpenAI/GPT-4)                      │  │
│  │   - Structured JSON outputs (Pydantic models)              │  │
│  │   - Retry logic with exponential backoff                   │  │
│  │   - 32K context window, 4K max output tokens               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│         │                 │                  │                     │
│         ▼                 ▼                  ▼                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │TaskAnalysis  │  │ExecutionPlan │  │Generated     │            │
│  │(Pydantic)    │  │(Pydantic)    │  │Script Code   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATION & PACKAGING                           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Script Validator                                            │ │
│  │   - AST syntax parsing                                       │ │
│  │   - Security analysis (credentials, eval, exec)              │ │
│  │   - Best practices check                                     │ │
│  │   - Resource estimation (memory, CPU)                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Package Generator                                           │ │
│  │   - Dockerfile creation                                      │ │
│  │   - docker-compose.yml generation                            │ │
│  │   - requirements.txt (with auto-detection)                   │ │
│  │   - .env.example template                                    │ │
│  │   - deploy.sh script (executable)                            │ │
│  │   - README.md documentation                                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTAINERIZATION                                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Docker Build                                                │ │
│  │   - Build image from Dockerfile                              │ │
│  │   - Install Python dependencies                              │ │
│  │   - Copy script into container                               │ │
│  │   - Set up working directory                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Container Execution                                         │ │
│  │   - Start container via docker-compose                       │ │
│  │   - Mount volumes (results, logs, exports)                   │ │
│  │   - Pass environment variables                               │ │
│  │   - Execute script.py                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Status Monitoring                                           │ │
│  │   - Check container state (docker ps -a)                     │ │
│  │   - Distinguish: Running vs Exited(0) vs Exited(1)          │ │
│  │   - Filter warnings from errors                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESULTS PROCESSING                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Log Fetching                                                │ │
│  │   - docker logs <container_name>                             │ │
│  │   - Capture stdout + stderr                                  │ │
│  │   - Parse loguru formatted output                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Results Parsing                                             │ │
│  │   - Find "=== Calculation Results ===" markers               │ │
│  │   - Extract lines between markers                            │ │
│  │   - Remove formatting (timestamps, module names)             │ │
│  │   - Clean and format for display                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Terminal Display                                            │ │
│  │   - Format with logger.info()                                │ │
│  │   - Add separators and headers                               │ │
│  │   - Color coding (green=success, red=error)                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                      │
│                                                                     │
│  ✅ Script executed successfully                                   │
│  📊 Results displayed in terminal                                  │
│  📁 Generated files saved in generated_scripts/                    │
│  🐳 Container ready for reuse/inspection                           │
│  💡 Quick commands provided for management                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Map

### File System Structure

```
AgenticPOC_Meta/
├── script_executor.py              # Main orchestrator
├── config.py                       # Configuration management
├── requirements.txt                # System dependencies
│
├── meta_agent/
│   ├── __init__.py
│   │
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── task_analyzer.py       # NL → TaskAnalysis
│   │
│   ├── planners/
│   │   ├── __init__.py
│   │   └── execution_planner.py   # TaskAnalysis → ExecutionPlan
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── script_generator.py    # ExecutionPlan → Python Code
│   │   └── dockerfile_generator.py # Container definitions
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   └── script_validator.py    # Multi-layer validation
│   │
│   ├── executors/
│   │   ├── __init__.py
│   │   └── container_executor.py  # Docker execution
│   │
│   └── utils/
│       ├── __init__.py
│       ├── llm_client.py          # LM Studio integration (Qwen2.5-Coder-7B)
│       └── database_inspector.py  # Schema discovery
│
├── generated_scripts/              # Output directory
│   └── script_YYYYMMDD_HHMMSS/    # Each execution
│       ├── script.py               # Generated Python script
│       ├── requirements.txt        # Script dependencies
│       ├── Dockerfile              # Container definition
│       ├── docker-compose.yml      # Orchestration config
│       ├── deploy.sh               # Deployment script
│       ├── .env.example            # Environment template
│       ├── .env                    # Actual configuration
│       ├── README.md               # Usage instructions
│       ├── results/                # Execution output
│       ├── logs/                   # Application logs
│       └── exports/                # Generated files
│           ├── reports/
│           └── data/
│
└── Docs/
    ├── TECHNICAL_DOCUMENTATION.md
    ├── BACKEND_WORKFLOW_TECHNICAL.md  # This file
    └── TEST_RESULTS_NOV_3_2025.md
```

---

## Detailed Step-by-Step Workflow

### STEP 1: User Input Processing

**Location**: `script_executor.py` (lines 115-131)

```python
def main():
    # User provides natural language request
    user_request = """
    I need to review the debt service coverage for our entire property portfolio.
    Can you pull all properties from the database and calculate their DSCR?
    """
    
    logger.info("📝 Request:")
    logger.info(f"   {user_request.strip()}\n")
```

**What Happens:**
1. User request is captured as a string
2. Logged to console with timestamp
3. Passed to processing pipeline
4. No validation at this stage (flexible input)

**Tool Used:** Python string, loguru logger

---

### STEP 2: LLM Client Initialization

**Location**: `meta_agent/utils/llm_client.py`

**CRITICAL**: This system uses **LM Studio** with **Qwen2.5-Coder-7B-Instruct-MLX**, NOT OpenAI/GPT-4!

**Code Flow:**
```python
class LLMClient:
    """
    Client for LM Studio LLM API.
    STRICT MODE: NO FALLBACKS - fails explicitly if LM Studio unavailable
    """
    
    def __init__(self):
        # Load configuration from settings
        self.base_url = settings.llm_base_url  # http://localhost:1234/v1
        self.model_name = settings.llm_model_name  # qwen2.5-coder-7b-instruct-mlx
        self.temperature = settings.llm_temperature  # 0.3
        self.max_tokens = settings.llm_max_tokens  # 4000
        self.context_length = settings.llm_context_length  # 32768
        
        logger.debug(f"Initializing LLM client: {self.model_name}")
        logger.debug(f"LM Studio URL: {self.base_url}")
        
        self._initialize()
    
    def _initialize(self) -> None:
        """
        Initialize and verify LM Studio connection
        
        Raises:
            ConnectionError: If cannot connect to LM Studio
            RuntimeError: If model not loaded
        """
        # Step 1: Verify LM Studio server is accessible
        response = httpx.get(f"{self.base_url}/models", timeout=10.0)
        response.raise_for_status()
        models = response.json()
        
        # Step 2: Verify Qwen2.5-Coder-7B is loaded
        if models.get("data"):
            loaded_models = [m.get("id") for m in models["data"]]
            if self.model_name not in loaded_models:
                raise RuntimeError(
                    f"Model '{self.model_name}' not loaded in LM Studio. "
                    f"Please load the model and try again."
                )
        
        # Step 3: Initialize LangChain client (using OpenAI-compatible API)
        self.llm = ChatOpenAI(
            base_url=self.base_url,
            api_key="lm-studio",  # Placeholder (LM Studio doesn't require real key)
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=180.0,  # 3 minutes for local 7B model
            max_retries=0  # Fail fast, no retries
        )
        
        # Step 4: Health check
        test_response = self.llm.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Respond with 'OK'")
        ])
        
        if test_response.content:
            self.available = True
            logger.debug("✓ LLM client initialized successfully")
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """Generate structured JSON output from Qwen2.5-Coder"""
        
        # Ensure JSON output requested
        if "json" not in system_prompt.lower():
            system_prompt += "\n\nIMPORTANT: Output MUST be valid JSON only."
        
        # Generate response
        response_text = self.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Clean markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        return json.loads(response_text.strip())
```

**What Happens:**
1. **Load Configuration**: Get LM Studio URL and model name from settings
2. **Server Check**: Verify LM Studio is running at localhost:1234
3. **Model Verification**: Ensure Qwen2.5-Coder-7B-Instruct-MLX is loaded
4. **Initialize LangChain**: Create ChatOpenAI adapter for LM Studio
5. **Health Check**: Test with simple message
6. **Fail Fast**: If any step fails, raise explicit error (NO FALLBACK to OpenAI)

**Tools Used:**
- `httpx` - HTTP client for LM Studio API checks
- `langchain_openai.ChatOpenAI` - OpenAI-compatible adapter for LM Studio
- `langchain_core.messages` - Message formatting
- `json.loads()` - JSON parsing (with markdown cleanup)
- `loguru` - Logging

**Configuration:**
- **Model**: `qwen2.5-coder-7b-instruct-mlx` (7B parameter code-focused model)
- **Server**: `http://localhost:1234/v1` (LM Studio local server)
- **Temperature**: 0.3 (low for consistent code generation)
- **Max Tokens**: 4000 (expandable on retry)
- **Context Length**: 32768 tokens (32K context window)
- **Cost**: FREE (local inference, no API costs)

---

### STEP 3: Database Schema Inspection

**Location**: `meta_agent/utils/database_inspector.py`

**Code Flow:**
```python
def inspect_database_schema(db_url: Optional[str] = None) -> Optional[DatabaseSchema]:
    """
    Inspect PostgreSQL database and extract schema information
    """
    if not db_url:
        db_url = os.getenv('DATABASE_URL')
    
    if not db_url or 'postgresql' not in db_url:
        return None
    
    try:
        # Step 1: Connect with SQLAlchemy
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        tables = []
        relationships = []
        
        # Step 2: For each table, extract structure
        for table_name in inspector.get_table_names():
            columns = []
            
            # Step 3: Get column information
            for column in inspector.get_columns(table_name):
                col_schema = ColumnSchema(
                    name=column['name'],
                    data_type=str(column['type']),
                    is_nullable=column['nullable'],
                    is_primary_key=False,  # Updated below
                    is_foreign_key=False,  # Updated below
                    foreign_table=None
                )
                columns.append(col_schema)
            
            # Step 4: Mark primary keys
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint:
                for col in columns:
                    if col.name in pk_constraint['constrained_columns']:
                        col.is_primary_key = True
            
            # Step 5: Mark foreign keys
            for fk in inspector.get_foreign_keys(table_name):
                for col in columns:
                    if col.name in fk['constrained_columns']:
                        col.is_foreign_key = True
                        col.foreign_table = fk['referred_table']
                
                # Step 6: Record relationship
                relationships.append({
                    'from_table': table_name,
                    'from_column': fk['constrained_columns'][0],
                    'to_table': fk['referred_table']
                })
            
            # Step 7: Count rows (for context)
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
            
            # Step 8: Create table schema
            table_schema = TableSchema(
                name=table_name,
                columns=columns,
                row_count=row_count
            )
            tables.append(table_schema)
        
        # Step 9: Return complete schema
        return DatabaseSchema(
            tables=tables,
            relationships=relationships
        )
        
    except Exception as e:
        logger.warning(f"Could not inspect database: {e}")
        return None

def format_schema_for_llm(schema: Optional[DatabaseSchema]) -> str:
    """
    Format schema information for LLM consumption (concise)
    """
    if not schema:
        return ""
    
    lines = ["\n**DATABASE SCHEMA:**"]
    
    for table in schema.tables:
        # Show key columns and first 8 regular columns
        key_cols = []
        other_cols = []
        
        for col in table.columns:
            if col.is_primary_key or col.is_foreign_key:
                markers = []
                if col.is_primary_key:
                    markers.append("PK")
                if col.is_foreign_key:
                    markers.append(f"FK→{col.foreign_table}")
                key_cols.append(f"{col.name}[{','.join(markers)}]")
            else:
                other_cols.append(col.name)
        
        # Concise format
        notable = other_cols[:8]
        more = f" +{len(other_cols)-8} more" if len(other_cols) > 8 else ""
        all_cols = key_cols + notable
        lines.append(f"`{table.name}`({table.row_count} rows): {', '.join(all_cols)}{more}")
    
    # Add JOIN instructions
    if schema.relationships:
        lines.append("\n**JOIN INSTRUCTIONS:**")
        for rel in schema.relationships[:5]:
            lines.append(f"  • JOIN {rel['to_table']} ON {rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_table']}_id")
    
    # Add query pattern
    lines.append("\n**QUERY PATTERN (CRITICAL):**")
    lines.append("```python")
    lines.append("from psycopg2.extras import RealDictCursor")
    lines.append("conn = psycopg2.connect(url, cursor_factory=RealDictCursor)")
    lines.append("# Rows are dicts! Access: row['property_name']")
    lines.append("```")
    
    return "\n".join(lines)
```

**What Happens:**
1. **Connection**: SQLAlchemy connects to PostgreSQL
2. **Table Discovery**: List all tables in database
3. **Column Extraction**: For each table, get columns with data types
4. **Primary Key Detection**: Mark PK columns
5. **Foreign Key Detection**: Mark FK columns and record relationships
6. **Row Counting**: Get row count for each table (context for LLM)
7. **Schema Compilation**: Build `DatabaseSchema` Pydantic model
8. **LLM Formatting**: Convert to concise, readable format
9. **Pattern Inclusion**: Add RealDictCursor example

**Tools Used:**
- `sqlalchemy` - Database abstraction and introspection
- `sqlalchemy.inspect()` - Schema inspection
- `psycopg2` - PostgreSQL adapter (implicit via SQLAlchemy)
- `pydantic` - Data validation (DatabaseSchema, TableSchema, ColumnSchema)
- `text()` - SQL text construction for queries

**Output Example:**
```
**DATABASE SCHEMA:**
`properties`(10 rows): property_id[PK], property_name, property_address, property_type, total_gla_sqft, +3 more
`financial_metrics`(10 rows): metric_id[PK], property_id[FK→properties], noi, annual_debt_service, dscr, +4 more

**JOIN INSTRUCTIONS:**
  • JOIN financial_metrics ON properties.property_id = financial_metrics.property_id

**QUERY PATTERN (CRITICAL):**
```python
from psycopg2.extras import RealDictCursor
conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
# Rows are dicts! Access: row['property_name']
```
```

---

### STEP 4: Task Analysis

**Location**: `meta_agent/analyzers/task_analyzer.py`

**Code Flow:**
```python
def analyze_task(user_request: str, llm_client: LLMClient, max_retries: int = 3) -> TaskAnalysis:
    """
    Analyze user request and extract structured information
    """
    
    # Build system prompt
    system_prompt = """You are an expert task analyzer. Analyze the user's request and return structured JSON.

Extract:
1. Primary goal (main objective)
2. Task type (calculation/data_processing/reporting/analysis)
3. Whether a web interface is needed (look for: website, dashboard, web, interface, UI)
4. Whether simulations are needed (look for: what-if, scenario, simulation, different values)
5. Data sources (databases, APIs, files)
6. Key entities mentioned (property names, IDs, etc.)
7. Complexity (LOW/MEDIUM/COMPLEX)
8. Estimated execution time

Return JSON with these exact fields:
{
  "primary_goal": "string",
  "task_type": "calculation|data_processing|reporting|analysis",
  "requires_web_interface": boolean,
  "requires_simulation": boolean,
  "data_sources": ["postgresql", "api", "csv"],
  "key_entities": ["entity1", "entity2"],
  "complexity": "LOW|MEDIUM|COMPLEX",
  "estimated_execution_time_seconds": integer
}
"""
    
    user_prompt = f"""Analyze this request:

{user_request}

Return the analysis as JSON."""
    
    for attempt in range(max_retries):
        try:
            # Call LLM
            result = llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse into Pydantic model
            analysis = TaskAnalysis(**result)
            
            # Log results
            logger.info(f"  Task type: {analysis.task_type}")
            logger.info(f"  Web interface: {analysis.requires_web_interface}")
            logger.info(f"  Simulations: {analysis.requires_simulation}")
            logger.info(f"  Complexity: {analysis.complexity}")
            
            return analysis
            
        except Exception as e:
            logger.warning(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info("  Retrying...")
                continue
            else:
                raise ValueError(f"Failed to analyze task after {max_retries} attempts")
```

**Pydantic Model:**
```python
class TaskAnalysis(BaseModel):
    primary_goal: str
    task_type: str  # calculation, data_processing, reporting, analysis
    requires_web_interface: bool
    requires_simulation: bool
    data_sources: List[str]
    key_entities: List[str]
    complexity: str  # LOW, MEDIUM, COMPLEX
    estimated_execution_time_seconds: int
```

**What Happens:**
1. **Prompt Construction**: Build system prompt with JSON schema
2. **LLM Call**: Send to GPT-4 with structured output request
3. **JSON Parsing**: Parse LLM response to dict
4. **Pydantic Validation**: Validate against `TaskAnalysis` model
5. **Logging**: Display key findings
6. **Retry Logic**: Up to 3 attempts on failure

**Tools Used:**
- `pydantic.BaseModel` - Data validation
- `json.loads()` - JSON parsing
- LM Studio + Qwen2.5-Coder-7B - Local text analysis (NO OpenAI)
- Retry pattern with exponential backoff

**Example Input:**
```
"I need to review the debt service coverage for our entire property portfolio."
```

**Example Output:**
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

### STEP 5: Execution Planning

**Location**: `meta_agent/planners/execution_planner.py`

**Code Flow:**
```python
def design_execution_plan(
    task_analysis: TaskAnalysis,
    llm_client: LLMClient,
    max_retries: int = 3
) -> ExecutionPlan:
    """
    Design step-by-step execution plan
    """
    
    system_prompt = """You are an expert execution planner. Design a step-by-step plan.

Return JSON with these exact fields:
{
  "plan_name": "string",
  "description": "string",
  "steps": [
    {
      "step_number": 1,
      "name": "string",
      "description": "string",
      "action": "database_query|calculation|api_call|file_operation|report_generation|web_server",
      "depends_on": []
    }
  ],
  "dependencies": ["psycopg2", "pandas", "flask"],
  "estimated_lines_of_code": integer,
  "web_server_config": {"host": "0.0.0.0", "port": 8080} or null,
  "simulation_config": {...} or null
}
"""
    
    user_prompt = f"""Design an execution plan for this task:

**Goal:** {task_analysis.primary_goal}
**Type:** {task_analysis.task_type}
**Complexity:** {task_analysis.complexity}
**Data Sources:** {', '.join(task_analysis.data_sources)}
**Web Interface:** {task_analysis.requires_web_interface}
**Simulations:** {task_analysis.requires_simulation}

Design a plan with sequential steps to accomplish this goal."""
    
    for attempt in range(max_retries):
        try:
            result = llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2000 + (attempt * 500)  # Increase on retry
            )
            
            # Fix common field mismatches
            if 'name' in result and 'plan_name' not in result:
                result['plan_name'] = result.pop('name')
            
            # Parse into Pydantic model
            plan = ExecutionPlan(**result)
            
            # Validate plan
            validate_execution_plan(plan)
            
            logger.info(f"  Plan: {plan.plan_name}")
            logger.info(f"  Steps: {len(plan.steps)}")
            logger.info(f"  Dependencies: {len(plan.dependencies)}")
            
            return plan
            
        except Exception as e:
            logger.warning(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                system_prompt += f"\n\nPREVIOUS ERROR: {str(e)}\nPlease fix and retry."
                continue
            else:
                raise ValueError(f"Failed to design plan after {max_retries} attempts")

def validate_execution_plan(plan: ExecutionPlan) -> bool:
    """Validate execution plan structure"""
    
    if not plan.plan_name:
        raise ValueError("Plan name is required")
    
    if not plan.steps or len(plan.steps) == 0:
        raise ValueError("Plan must have at least one step")
    
    # Validate step sequence
    step_numbers = [step.step_number for step in plan.steps]
    if step_numbers != list(range(1, len(step_numbers) + 1)):
        raise ValueError("Steps must be numbered sequentially")
    
    # Validate action types (flexible)
    valid_actions = [
        "database_query", "database_operation", "db_query", "query",
        "calculation", "compute", "analyze",
        "api_call", "http_request",
        "file_operation", "file_io", "write", "read",
        "report_generation", "generate_report", "export",
        "web_server", "server", "flask_app"
    ]
    
    for step in plan.steps:
        if step.action not in valid_actions:
            logger.warning(f"Unusual action type: {step.action} (proceeding)")
    
    return True
```

**Pydantic Models:**
```python
class ExecutionStep(BaseModel):
    step_number: int
    name: str
    description: str
    action: str
    depends_on: List[int] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    plan_name: str
    description: str
    steps: List[ExecutionStep]
    dependencies: List[str]
    estimated_lines_of_code: int
    web_server_config: Optional[Dict[str, Any]] = None
    simulation_config: Optional[Dict[str, Any]] = None
```

**What Happens:**
1. **Prompt Building**: Include task analysis context
2. **LLM Call**: Request structured execution plan
3. **Field Fix**: Auto-correct `name` → `plan_name` mismatch
4. **Pydantic Validation**: Validate against `ExecutionPlan` model
5. **Plan Validation**: Check step sequence and action types
6. **Logging**: Display plan summary
7. **Retry with Feedback**: Include previous error in retry prompt

**Tools Used:**
- `pydantic` - Structured validation
- LM Studio + Qwen2.5-Coder-7B - Local planning generation (NO OpenAI)
- Field name correction logic
- Flexible action type validation

**Example Output:**
```python
ExecutionPlan(
    plan_name="Debt Service Coverage Review",
    description="Calculate DSCR for all properties",
    steps=[
        ExecutionStep(
            step_number=1,
            name="Connect to Database",
            description="Establish PostgreSQL connection",
            action="database_query",
            depends_on=[]
        ),
        ExecutionStep(
            step_number=2,
            name="Query Properties and Financial Data",
            description="JOIN properties with financial_metrics",
            action="database_query",
            depends_on=[1]
        ),
        ExecutionStep(
            step_number=3,
            name="Calculate DSCR",
            description="Compute NOI / Annual Debt Service",
            action="calculation",
            depends_on=[2]
        ),
        ExecutionStep(
            step_number=4,
            name="Display Results",
            description="Print formatted results to console",
            action="report_generation",
            depends_on=[3]
        )
    ],
    dependencies=["psycopg2"],
    estimated_lines_of_code=50,
    web_server_config=None,
    simulation_config=None
)
```

---

### STEP 6: Script Generation

**Location**: `meta_agent/generators/script_generator.py`

This is the most complex component. Let me break it down:

**Main Function:**
```python
def generate_script(
    task_analysis: TaskAnalysis,
    execution_plan: ExecutionPlan,
    llm_client: LLMClient,
    database_schema: Optional[DatabaseSchema] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Generate complete Python script from execution plan
    """
    
    for attempt in range(max_retries):
        try:
            # Step 1: Build system prompt (CRITICAL)
            system_prompt = _build_system_prompt()
            
            # Step 2: Build user prompt with context
            user_prompt = _build_user_prompt(
                task_analysis,
                execution_plan,
                database_schema
            )
            
            # Step 3: Call LLM for code generation
            response = llm_client.client.chat.completions.create(
                model=llm_client.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            script_code = response.choices[0].message.content
            
            # Step 4: Clean code (remove markdown artifacts)
            script_code = _clean_code(script_code)
            
            # Step 5: Validate syntax
            ast.parse(script_code)  # Raises SyntaxError if invalid
            
            # Step 6: Generate requirements.txt (with auto-detection)
            requirements = _generate_requirements(
                execution_plan,
                task_analysis.requires_web_interface,
                script_code  # Pass for import detection
            )
            
            # Step 7: Generate .env.example
            env_example = _generate_env_example(task_analysis, execution_plan)
            
            # Step 8: Build metadata
            metadata = {
                'task_type': task_analysis.task_type,
                'complexity': task_analysis.complexity,
                'has_web_interface': task_analysis.requires_web_interface,
                'dependencies': execution_plan.dependencies,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"  Lines of code: {len(script_code.splitlines())}")
            logger.info(f"  Dependencies: {len(requirements.splitlines())}")
            
            return {
                'script': script_code,
                'requirements': requirements,
                'env_example': env_example,
                'metadata': metadata
            }
            
        except SyntaxError as e:
            logger.warning(f"  ✗ Syntax error at line {e.lineno}: {e.msg}")
            
            if attempt < max_retries - 1:
                logger.info("  Retrying with error feedback...")
                
                # Build error context
                code_lines = script_code.split('\n')
                error_line_num = e.lineno - 1
                context_start = max(0, error_line_num - 3)
                context_end = min(len(code_lines), error_line_num + 3)
                context = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(code_lines[context_start:context_end], start=context_start))
                
                # Add error feedback to system prompt
                additional_instructions = f"""
SYNTAX ERROR DETECTED at line {e.lineno}:
{e.msg}

Code context:
{context}

Please fix this error and regenerate the complete script.
DO NOT include any markdown, headers, or explanatory text.
Return ONLY valid Python code."""
                
                system_prompt += "\n\n" + additional_instructions
                continue
            else:
                raise
```

**System Prompt (Critical Component):**
```python
def _build_system_prompt() -> str:
    return """You are an expert Python developer. Generate production-ready, executable Python scripts.

CRITICAL REQUIREMENTS:
1. Generate COMPLETE, working Python code
2. Use environment variables for ALL configuration (os.getenv())
3. NEVER hardcode credentials, URLs, or sensitive data
4. Include proper error handling (try/except)
5. Add logging with loguru
6. Use type hints throughout
7. Follow PEP 8 style
8. Make code self-contained and executable

FOR CONSOLE-ONLY SCRIPTS (NO WEB INTERFACE):
**CRITICAL: If user did NOT request a website/web interface/dashboard:**
- DO NOT import flask
- DO NOT create HTML templates
- DO NOT start a web server
- ONLY use logger.info() or print() for output
- Print results to console/terminal/stdout only
- Script should run, calculate, print results, and exit

FOR WEB INTERFACES:
- Use Flask for simplicity
- Create HTML templates inline or as strings
- Display results FIRST on homepage (dashboard view)
- Calculate for ALL records from database (not just one)
- Run calculation automatically when app starts
- Show pre-calculated results prominently for ALL entities
- Then provide simulation form below for what-if scenarios
- Add API endpoints for re-running calculations
- Serve on configurable host and port
- CRITICAL: Flask app.run() MUST use: app.run(host=CONFIG['host'], port=CONFIG['port'])
- CONFIG must include BOTH 'host' and 'port' keys

TERMINAL/CONSOLE OUTPUT (REQUIRED):
- Print calculation results to terminal/stdout
- After calculating for all records, print a summary table to console
- Use logger.info() to show results in a formatted way
- Example:
  ```python
  logger.info("=== Calculation Results ===")
  for result in results:
      logger.info(f"{result['property_name']}: DSCR = {result['dscr']:.2f}")
  logger.info("=== End Results ===")
  ```
- This allows users to see results in terminal AND in browser
- Print results before starting the Flask server

ERROR HANDLING TEMPLATES (ONLY FOR WEB INTERFACES):
**ONLY generate these if web interface is requested:**
**YOU MUST GENERATE THESE 3 TEMPLATES AS STRING CONSTANTS** at the top after imports:
- DB_NOT_CONFIGURED_TEMPLATE (triple-quoted string with HTML)
- ERROR_TEMPLATE (triple-quoted string with HTML, uses {{error}} variable)
- EMPTY_DATABASE_TEMPLATE (triple-quoted string with HTML)

DATABASE QUERIES (CRITICAL - MUST FOLLOW):
- Real-world databases have multiple related tables
- Use SQL JOINs to combine data from related tables  
- **USE RealDictCursor TO GET ROWS AS DICTIONARIES** (MANDATORY!)

**CORRECT PATTERN** (MANDATORY - MUST USE EXACTLY THIS):
```python
import psycopg2
from psycopg2.extras import RealDictCursor

# ✅ CORRECT: Connect with RealDictCursor to get rows as dicts automatically!
conn = psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Use SELECT * with JOINs (you don't know actual column names!)
query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
cursor.execute(query)

# With RealDictCursor, rows are already dictionaries!
for row in cursor.fetchall():
    # Access by column name directly!
    property_name = row.get('property_name', 'Unknown')
    noi = float(row.get('noi', 0))
    debt_service = float(row.get('annual_debt_service', 0))
```

**WRONG PATTERNS** (NEVER DO THESE):
```python
# ❌ WRONG: Listing specific columns - you don't know actual names!
cursor.execute("SELECT p.name, p.address, p.rental_income FROM properties p")

# ❌ WRONG: Accessing by index - fragile and error-prone!
row[0], row[1], row[2]

# ❌ WRONG: Hardcoding column names in SELECT without knowing schema
cursor.execute("SELECT property_name, noi FROM ...")  # These columns might not exist!
```

DATABASE CONNECTION (CRITICAL):
- NEVER connect to database in __init__ or module level
- ALWAYS defer connection until needed (in a method/function)
- Always close connections in finally block
- Example:
  ```python
  class DataHandler:
      def __init__(self):
          pass  # NO connection here!
      
      def get_connection(self):
          if not CONFIG['db_url']:
              raise ValueError("DATABASE_URL not configured")
          return psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)
      
      def execute(self):
          conn = self.get_connection()  # Connect when needed
          try:
              cursor = conn.cursor()
              # ... do work ...
          finally:
              conn.close()  # Always close
  ```

CONFIGURATION PATTERN:
```python
import os
from loguru import logger

# Configuration from environment variables
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
    'host': os.getenv('HOST', '0.0.0.0'),  # For web interfaces
    'port': int(os.getenv('PORT', 8080))   # For web interfaces
}
```

OUTPUT FORMAT:
- DO NOT include markdown formatting (```, **text**, etc.)
- DO NOT include explanatory comments like "This script does..."
- DO NOT include numbered lists like "1. Import libraries"
- ONLY return valid Python code that can be executed directly
- Return the COMPLETE script from imports to main execution

VALIDATION:
Before returning, verify:
✓ No markdown artifacts (```, **bold**, etc.)
✓ All imports at top
✓ CONFIG dictionary with environment variables
✓ Proper error handling
✓ Logger configured
✓ Main execution block (if __name__ == "__main__":)
✓ For web: Flask app with routes and app.run()
✓ For console: Direct execution with output
"""
```

**User Prompt Builder:**
```python
def _build_user_prompt(
    task_analysis: TaskAnalysis,
    execution_plan: ExecutionPlan,
    database_schema: Optional[DatabaseSchema]
) -> str:
    from meta_agent.utils.database_inspector import format_schema_for_llm
    
    steps_description = "\n".join([
        f"{step.step_number}. {step.name} ({step.action}): {step.description}"
        for step in execution_plan.steps
    ])
    
    # Add schema information if available
    schema_info = format_schema_for_llm(database_schema)
    
    # Add JOIN example if schema shows foreign keys
    join_example = ""
    if database_schema and database_schema.relationships:
        join_example = """

**EXAMPLE JOIN QUERY (use this pattern):**
```python
query = \"\"\"
SELECT * 
FROM properties p
JOIN financial_metrics fm ON p.property_id = fm.property_id
\"\"\"
cursor.execute(query)
columns = [desc[0] for desc in cursor.description]
for row in cursor.fetchall():
    row_dict = dict(zip(columns, row))
    # Now row_dict has columns from BOTH tables
```
"""
    
    return f"""Generate a complete Python script for this task:

**Goal:** {task_analysis.primary_goal}
{schema_info}
{join_example}

**Execution Plan:** {execution_plan.plan_name}
{execution_plan.description}

**Steps:**
{steps_description}

**Requirements:**
- Web Interface: {"YES - Create web interface" if task_analysis.requires_web_interface else "NO - Console/terminal output only"}
- Simulations: {task_analysis.requires_simulation}
- Data Sources: {', '.join(task_analysis.data_sources)}

**Dependencies Available:** {', '.join(execution_plan.dependencies)}

Generate COMPLETE, executable Python code."""
```

**Code Cleaning:**
```python
def _clean_code(code: str) -> str:
    """Clean generated code of markdown artifacts"""
    import re
    
    code = code.strip()
    
    # Remove markdown code blocks
    while code.startswith("```python") or code.startswith("```"):
        if code.startswith("```python"):
            code = code[9:].strip()
        elif code.startswith("```"):
            code = code[3:].strip()
    
    while code.endswith("```"):
        code = code[:-3].strip()
    
    # Process line by line
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip markdown fences
        if stripped in ["```", "```python", "```bash", "```json"]:
            continue
        
        # Skip markdown headers
        if stripped.startswith('**') and stripped.endswith('**'):
            continue
        if stripped.startswith('###') or stripped.startswith('##'):
            if not line.lstrip().startswith('#'):  # Not a Python comment
                continue
        
        # Skip numbered lists (e.g., "1. All necessary imports")
        if re.match(r'^\d+\.\s+[A-Z]', stripped):
            continue
        
        # Skip explanatory patterns
        if any(phrase in stripped.lower() for phrase in [
            '**html template', '**note:', '**explanation:',
            'this script', 'this code', 'the above code',
            'to run this', 'to use this', 'example usage'
        ]):
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()
```

**Requirements Generator with Auto-Detection:**
```python
def _generate_requirements(
    execution_plan: ExecutionPlan,
    has_web_interface: bool = False,
    script_code: str = ""
) -> str:
    """Generate requirements.txt with auto-detection"""
    
    requirements = set(execution_plan.dependencies)
    
    # Auto-detect imports from script code
    if script_code:
        if "import psycopg2" in script_code or "from psycopg2" in script_code:
            requirements.add("psycopg2")
        if "import pandas" in script_code or "from pandas" in script_code:
            requirements.add("pandas")
        if "import numpy" in script_code or "from numpy" in script_code:
            requirements.add("numpy")
        if "import sqlalchemy" in script_code or "from sqlalchemy" in script_code:
            requirements.add("sqlalchemy")
        if "import flask" in script_code or "from flask" in script_code:
            requirements.add("flask")
    
    # Replace psycopg2 with psycopg2-binary for Docker
    if "psycopg2" in requirements:
        requirements.remove("psycopg2")
        requirements.add("psycopg2-binary")
    
    # Add Flask for web interfaces
    if has_web_interface:
        requirements.add("flask")
    
    # Add common dependencies
    requirements.add("loguru")
    requirements.add("python-dotenv")
    requirements.add("pydantic")
    
    # Sort and format
    req_list = sorted(requirements)
    return "\n".join(req_list)
```

**What Happens:**
1. **System Prompt**: Comprehensive instructions (300+ lines)
2. **User Prompt**: Task context + schema + plan
3. **LLM Generation**: Qwen2.5-Coder-7B generates Python code locally
4. **Code Cleaning**: Remove markdown artifacts (Qwen often uses code blocks)
5. **Syntax Validation**: AST parsing
6. **Import Detection**: Auto-detect from code
7. **Requirements**: Generate with auto-detection
8. **Environment Template**: Create .env.example
9. **Retry with Feedback**: Include syntax error context
10. **Return Package**: Script + requirements + env + metadata

**Tools Used:**
- `ast.parse()` - Python syntax validation
- `re` (regex) - Pattern matching for cleaning
- LM Studio + Qwen2.5-Coder-7B - Local code generation (NO OpenAI)
- String manipulation - Cleaning and formatting
- Set operations - Dependency management

---

### STEP 7: Script Validation

**Location**: `meta_agent/validators/script_validator.py`

**Code Flow:**
```python
def validate_script(script_code: str, requirements: str) -> ValidationResult:
    """
    Multi-layer validation of generated script
    """
    
    issues = []
    
    # Layer 1: Syntax Validation
    try:
        ast.parse(script_code)
    except SyntaxError as e:
        issues.append(ValidationIssue(
            severity="ERROR",
            category="syntax",
            message=f"Syntax error at line {e.lineno}: {e.msg}",
            line_number=e.lineno
        ))
    
    # Layer 2: Security Analysis
    security_score = 1.0
    
    # Check for hardcoded credentials
    for line_num, line in enumerate(script_code.split('\n'), 1):
        # Detect hardcoded passwords
        if re.search(r'password\s*=\s*["\'].+["\']', line.lower()):
            if "os.getenv" not in line:
                issues.append(ValidationIssue(
                    severity="ERROR",
                    category="security",
                    message="Hardcoded password detected",
                    line_number=line_num
                ))
                security_score -= 0.3
        
        # Detect eval/exec (dangerous)
        if re.search(r'\beval\(|\bexec\(', line):
            issues.append(ValidationIssue(
                severity="ERROR",
                category="security",
                message="Use of eval/exec is dangerous",
                line_number=line_num
            ))
            security_score -= 0.5
        
        # Check for os.getenv (good practice)
        if "os.getenv" in line:
            security_score += 0.05  # Small bonus
    
    # Layer 3: Best Practices
    
    # Check for error handling
    if "try:" not in script_code or "except" not in script_code:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="best_practices",
            message="No error handling detected",
            line_number=None
        ))
    
    # Check for logging
    if "logger" not in script_code and "logging" not in script_code:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="best_practices",
            message="No logging configured",
            line_number=None
        ))
    
    # Layer 4: Resource Estimation
    lines_of_code = len([l for l in script_code.split('\n') if l.strip()])
    
    # Estimate memory based on dependencies
    estimated_memory = 128  # Base
    if "pandas" in requirements:
        estimated_memory += 256
    if "flask" in requirements:
        estimated_memory += 128
    
    # Estimate CPU
    estimated_cpu = 0.5
    if "calculation" in script_code.lower():
        estimated_cpu = 1.0
    
    # Build result
    is_valid = not any(issue.severity == "ERROR" for issue in issues)
    
    return ValidationResult(
        is_valid=is_valid,
        issues=issues,
        security_score=max(0.0, min(1.0, security_score)),
        estimated_memory_mb=estimated_memory,
        estimated_cpu_cores=estimated_cpu,
        lines_of_code=lines_of_code
    )
```

**Pydantic Models:**
```python
class ValidationIssue(BaseModel):
    severity: str  # ERROR, WARNING, INFO
    category: str  # syntax, security, best_practices, performance
    message: str
    line_number: Optional[int] = None

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue]
    security_score: float  # 0.0 to 1.0
    estimated_memory_mb: int
    estimated_cpu_cores: float
    lines_of_code: int
```

**What Happens:**
1. **Syntax Check**: AST parsing for Python validity
2. **Security Scan**:
   - Hardcoded credentials
   - Dangerous functions (eval, exec)
   - Environment variable usage
3. **Best Practices**:
   - Error handling presence
   - Logging configuration
4. **Resource Estimation**:
   - Memory based on dependencies
   - CPU based on task type
5. **Score Calculation**: Security score 0.0-1.0
6. **Result Compilation**: All findings in structured format

**Tools Used:**
- `ast.parse()` - Syntax validation
- `re` (regex) - Pattern detection
- Heuristic analysis - Resource estimation
- `pydantic` - Result validation

---

### STEP 8: Container Packaging

**Location**: `meta_agent/executors/container_executor.py`

**Main Function:**
```python
def execute_script_in_container(
    script_code: str,
    script_name: str,
    requirements: str,
    env_example: str,
    has_web_interface: bool = False,
    port: int = 8080,
    memory_limit: str = "512m",
    cpu_limit: float = 0.5,
    auto_start: bool = True
) -> ExecutionResult:
    """Execute script in Docker container"""
    
    # Step 1: Create execution directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    container_name = f"{script_name.replace('.py', '')}_{timestamp}"
    exec_dir = Path("generated_scripts") / container_name
    exec_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"  Execution directory: {exec_dir}")
    logger.info(f"  Container name: {container_name}")
    
    try:
        # Step 2: Write script file
        script_path = exec_dir / script_name
        script_path.write_text(script_code)
        logger.info(f"  ✓ Script written: {script_name}")
        
        # Step 3: Write requirements.txt
        req_path = exec_dir / "requirements.txt"
        req_path.write_text(requirements)
        logger.info(f"  ✓ Requirements written")
        
        # Step 4: Write .env.example
        env_path = exec_dir / ".env.example"
        env_path.write_text(env_example)
        logger.info(f"  ✓ Environment template written")
        
        # Step 5: Generate Dockerfile
        dockerfile_content = generate_dockerfile(
            script_name=script_name,
            requirements=requirements,
            has_web_interface=has_web_interface,
            port=port
        )
        dockerfile_path = exec_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        logger.info(f"  ✓ Dockerfile generated")
        
        # Step 6: Generate docker-compose.yml
        compose_content = generate_docker_compose(
            container_name=container_name,
            script_name=script_name,
            has_web_interface=has_web_interface,
            port=port,
            memory_limit=memory_limit,
            cpu_limit=cpu_limit
        )
        compose_path = exec_dir / "docker-compose.yml"
        compose_path.write_text(compose_content)
        logger.info(f"  ✓ docker-compose.yml generated")
        
        # Step 7: Generate deploy script
        deploy_script = generate_deploy_script(
            container_name=container_name,
            has_web_interface=has_web_interface,
            port=port
        )
        deploy_path = exec_dir / "deploy.sh"
        deploy_path.write_text(deploy_script)
        deploy_path.chmod(0o755)  # Make executable
        logger.info(f"  ✓ deploy.sh generated")
        
        # Step 8: Create required directories
        (exec_dir / "results").mkdir(exist_ok=True)
        (exec_dir / "logs").mkdir(exist_ok=True)
        (exec_dir / "exports" / "reports").mkdir(parents=True, exist_ok=True)
        (exec_dir / "exports" / "data").mkdir(parents=True, exist_ok=True)
        (exec_dir / "data").mkdir(exist_ok=True)
        logger.info(f"  ✓ Output directories created")
        
        # Step 9: Generate README
        readme = _generate_readme(
            container_name=container_name,
            script_name=script_name,
            has_web_interface=has_web_interface,
            port=port
        )
        readme_path = exec_dir / "README.md"
        readme_path.write_text(readme)
        logger.info(f"  ✓ README.md generated")
        
        # Step 10: Build and start container if auto_start
        if auto_start:
            # Create .env from .env.example
            env_file = exec_dir / ".env"
            if not env_file.exists():
                env_file.write_text(env_example)
            
            logger.info("Building and starting container...")
            _build_and_start_container(exec_dir, container_name)
        
        # Step 11: Return result
        return {
            "status": "success",
            "container_name": container_name,
            "execution_dir": str(exec_dir),
            "script_path": str(script_path),
            "has_web_interface": has_web_interface,
            "port": port if has_web_interface else None,
            "url": f"http://localhost:{port}" if has_web_interface else None,
            "auto_started": auto_start,
            "files_generated": [
                str(script_path), str(req_path), str(env_path),
                str(dockerfile_path), str(compose_path),
                str(deploy_path), str(readme_path)
            ]
        }
        
    except Exception as e:
        logger.error(f"Container execution setup failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_dir": str(exec_dir) if exec_dir else None
        }
```

**Dockerfile Generator:**
```python
def generate_dockerfile(
    script_name: str,
    requirements: str,
    has_web_interface: bool,
    port: int
) -> str:
    """Generate Dockerfile content"""
    
    expose_line = f"EXPOSE {port}" if has_web_interface else ""
    
    return f"""FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY {script_name} .

# Create directories
RUN mkdir -p /app/results /app/logs /app/exports/reports /app/exports/data /app/data

{expose_line}

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run script
CMD ["python", "{script_name}"]
"""
```

**Docker Compose Generator:**
```python
def generate_docker_compose(
    container_name: str,
    script_name: str,
    has_web_interface: bool,
    port: int,
    memory_limit: str,
    cpu_limit: float
) -> str:
    """Generate docker-compose.yml content"""
    
    ports_section = f"""    ports:
      - "{port}:{port}" """ if has_web_interface else ""
    
    return f"""version: '3.8'

services:
  {container_name}:
    build: .
    container_name: {container_name}
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - OUTPUT_DIR=/app/results
      - LOG_DIR=/app/logs
      - HOST=0.0.0.0
      - PORT={port}
{ports_section}
    volumes:
      - ./results:/app/results:rw
      - ./logs:/app/logs:rw
      - ./exports/reports:/app/exports/reports:rw
      - ./exports/data:/app/exports/data:rw
      - ./data:/app/data:rw
    mem_limit: {memory_limit}
    cpus: {cpu_limit}
    restart: {'unless-stopped' if has_web_interface else 'no'}
    networks:
      - script-network

networks:
  script-network:
    driver: bridge
"""
```

**What Happens:**
1. **Directory Creation**: `generated_scripts/script_YYYYMMDD_HHMMSS/`
2. **File Writing**:
   - `script.py` - Generated Python code
   - `requirements.txt` - Dependencies
   - `.env.example` - Environment template
   - `Dockerfile` - Container definition
   - `docker-compose.yml` - Orchestration
   - `deploy.sh` - Deployment script
   - `README.md` - Documentation
3. **Directory Structure**: Create `results/`, `logs/`, `exports/`
4. **Permissions**: Make `deploy.sh` executable
5. **Auto-start**: Optionally build and start container

**Tools Used:**
- `pathlib.Path` - File system operations
- `datetime` - Timestamp generation
- String formatting - File content generation
- File I/O - Writing files
- `chmod` - Setting permissions

---

### STEP 9: Container Build and Execution

**Location**: `meta_agent/executors/container_executor.py`

**Build and Start Function:**
```python
def _build_and_start_container(exec_dir: Path, container_name: str) -> None:
    """Build and start Docker container"""
    
    try:
        # Step 1: Check if Docker is available
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            cwd=exec_dir
        )
        if result.returncode != 0:
            raise RuntimeError("Docker is not running or not available")
        
        # Step 2: Run deploy script
        logger.debug("  Running deploy.sh...")
        result = subprocess.run(
            ["bash", "deploy.sh"],
            capture_output=True,
            text=True,
            cwd=exec_dir
        )
        
        # Step 3: Check container status
        # Docker Compose outputs warnings to stderr even on success
        check_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}",
             "--format", "{{.Names}}\\t{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        if container_name in check_result.stdout:
            status = check_result.stdout.strip().split('\\t')[1] if '\\t' in check_result.stdout else ""
            
            # Console scripts exit after completion (exit code 0 = success)
            # Web scripts stay running
            is_success = (
                'Up' in status or          # Still running (web interface)
                'Exited (0)' in status     # Completed successfully (console script)
            )
            
            if is_success:
                if 'Up' in status:
                    logger.debug("  ✓ Container running")
                else:
                    logger.debug("  ✓ Container executed successfully")
                
                # Log warnings if any, but don't treat them as errors
                if result.stderr and "level=warning" in result.stderr.lower():
                    logger.debug("  ℹ️  Docker Compose warnings (non-critical)")
            else:
                # Container failed (non-zero exit code)
                logger.error(f"  ✗ Container failed: {status}")
                raise RuntimeError(f"Container deployment failed: {status}")
        else:
            # Container not found - real error
            error_lines = []
            for line in result.stderr.split('\\n'):
                if line.strip() and 'level=warning' not in line.lower():
                    error_lines.append(line)
            
            error_msg = '\\n'.join(error_lines) if error_lines else result.stderr
            logger.error(f"  ✗ Container not created: {error_msg}")
            raise RuntimeError(f"Container deployment failed: {error_msg}")
            
    except Exception as e:
        logger.error(f"Failed to build/start container: {e}")
        raise
```

**Deploy Script (deploy.sh):**
```bash
#!/bin/bash
set -e

# Build and start container
docker-compose build
docker-compose up -d

echo "Container started successfully"
```

**What Happens:**
1. **Docker Check**: Verify Docker daemon is running
2. **Deploy Execution**: Run `bash deploy.sh`
   - `docker-compose build` - Build image
   - `docker-compose up -d` - Start container
3. **Status Verification**:
   - Run `docker ps -a` with filter
   - Get container name and status
   - Parse status string
4. **Success Determination**:
   - `Up` → Web interface running (success)
   - `Exited (0)` → Console script completed (success)
   - `Exited (1)` → Error occurred (failure)
5. **Warning Filtering**:
   - Ignore Docker Compose "version obsolete" warnings
   - Only treat real errors as failures
6. **Error Reporting**: Provide clear error messages

**Tools Used:**
- `subprocess.run()` - Execute shell commands
- `docker` CLI - Docker commands
- `docker-compose` CLI - Orchestration
- String parsing - Status interpretation
- Error filtering - Warning vs error distinction

---

### STEP 10: Results Processing

**Location**: `script_executor.py`

**Results Display Function:**
```python
def _display_execution_results(container_name: str, has_web_interface: bool) -> None:
    """
    Fetch and display the execution results from the container
    """
    try:
        # Step 1: Wait for execution (give container time to produce output)
        time.sleep(2)
        
        # Step 2: Fetch container logs
        result = subprocess.run(
            ["docker", "logs", container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout + result.stderr
        
        # Step 3: Check for output
        if not logs.strip():
            logger.info("📊 RESULTS")
            logger.info("   (Container running, no output yet)")
            if has_web_interface:
                logger.info("   Check the web interface for results\\n")
            return
        
        # Step 4: Parse and display results
        logger.info("📊 RESULTS")
        logger.info("="*60)
        
        # Step 5: Look for calculation results section
        in_results = False
        result_lines = []
        
        for line in logs.split('\\n'):
            # Detect results section markers
            if '=== Calculation Results ===' in line or '=== Results ===' in line:
                in_results = True
                continue
            elif '=== End Results ===' in line or '===' in line and in_results:
                in_results = False
                continue
            
            # Capture result lines (filter out loguru formatting)
            if in_results:
                # Extract actual content after loguru timestamp/level
                if '|' in line:
                    content = line.split('|')[-1].strip()
                    # Remove module/line number prefix (e.g., "__main__:<module>:71 - ")
                    if ' - ' in content and ':' in content.split(' - ')[0]:
                        content = content.split(' - ', 1)[1].strip()
                    if content:
                        result_lines.append(content)
                elif line.strip():
                    result_lines.append(line.strip())
        
        # Step 6: Display results
        if result_lines:
            for line in result_lines:
                logger.info(f"   {line}")
        else:
            # No structured results, show last few meaningful lines
            meaningful_lines = [
                line for line in logs.split('\\n')[-10:]
                if line.strip() and 'INFO' in line
            ]
            for line in meaningful_lines[-5:]:
                if '|' in line:
                    content = line.split('|')[-1].strip()
                    logger.info(f"   {content}")
        
        logger.info("="*60 + "\\n")
        
    except subprocess.TimeoutExpired:
        logger.warning("   (Container still processing...)")
        if has_web_interface:
            logger.info("   Check the web interface for results\\n")
    except Exception as e:
        logger.debug(f"   Could not fetch results: {e}")
```

**What Happens:**
1. **Wait**: 2-second delay for container execution
2. **Log Fetch**: `docker logs <container_name>`
3. **Empty Check**: Handle no output case
4. **Section Detection**: Find `=== Calculation Results ===` markers
5. **Line Extraction**: Capture lines between markers
6. **Format Cleaning**:
   - Remove loguru timestamps
   - Remove module prefixes
   - Clean whitespace
7. **Display**: Format with logger.info()
8. **Fallback**: Show last meaningful lines if no structured output
9. **Error Handling**: Graceful degradation

**Tools Used:**
- `subprocess.run()` - Execute docker logs
- `time.sleep()` - Delay for output generation
- String parsing - Log analysis
- Regex patterns - Content extraction
- `loguru` - Formatted display

---

## LLM Integration Details

### LM Studio + Qwen2.5-Coder-7B Configuration

**IMPORTANT**: This system uses **LM Studio** with **Qwen2.5-Coder-7B-Instruct-MLX**, NOT OpenAI/GPT-4!

**Connection Setup:**
```python
from langchain_openai import ChatOpenAI
import httpx

# Step 1: Verify LM Studio is running
response = httpx.get("http://localhost:1234/v1/models", timeout=10.0)
models = response.json()

# Step 2: Initialize LangChain with LM Studio endpoint
client = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",  # Placeholder (not validated by LM Studio)
    model="qwen2.5-coder-7b-instruct-mlx",
    temperature=0.3,
    max_tokens=4000,
    timeout=180.0  # 3 minutes for 7B model on M4 Mac
)
```

**Model Details:**
- **Model**: Qwen2.5-Coder-7B-Instruct-MLX
- **Size**: 7 billion parameters
- **Optimization**: MLX (Apple Silicon optimization)
- **Context Window**: 32,768 tokens (32K)
- **Max Output**: 4,000 tokens (configurable)
- **Hardware**: Runs on M4 Mac (local inference)
- **Fallback**: NONE - fails explicitly if LM Studio unavailable

**Parameters:**
```python
{
    "model": "qwen2.5-coder-7b-instruct-mlx",
    "temperature": 0.2-0.3,  # Low for consistent code generation
    "max_tokens": 1000-4000,  # Varies by stage
    "context_length": 32768,  # 32K context window
    "timeout": 180.0,  # 3 minutes per request
    "max_retries": 0  # Fail fast, no automatic retries
}
```

### Token Management

**Estimation (Qwen2.5-Coder-7B):**
- System prompt: ~800-1000 tokens
- User prompt: ~200-500 tokens (includes database schema)
- Response: ~500-2000 tokens
- **Total per call**: ~1500-3500 tokens
- **Well within 32K context window**

**Cost Calculation:**
- **Cost**: $0.00 (FREE - runs locally on M4 Mac)
- **No API charges**
- **No rate limits** (limited only by local hardware)
- **Privacy**: All data stays local (no external API calls)

**Performance:**
- **Speed**: ~20-50 tokens/second on M4 Mac
- **Latency**: 10-60 seconds per generation (varies by complexity)
- **Memory**: ~8-12 GB RAM for model + inference

### Retry Strategy

**Exponential Backoff:**
```python
for attempt in range(max_retries):
    try:
        response = llm_client.generate_json(...)
        return response
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
            continue
        else:
            raise
```

**LM Studio-Specific Error Handling:**
- `ConnectionError`: LM Studio not running → Clear error message
- `RuntimeError`: Model not loaded → Prompt user to load Qwen2.5-Coder-7B
- `TimeoutError`: Generation taking too long → Increase timeout or simplify prompt
- `JSONDecodeError`: Invalid JSON response → Clean markdown and retry

---

## Error Handling & Recovery

### Error Categories

1. **LLM Errors** (LM Studio + Qwen2.5-Coder-7B):
   - LM Studio not running → Immediate failure with setup instructions
   - Model not loaded → Explicit error, prompt to load model
   - Connection timeout → Verify LM Studio server is responsive
   - Invalid JSON → Clean markdown artifacts and retry
   - Empty response → Model may have crashed, verify LM Studio

2. **Validation Errors**:
   - Syntax error → Feedback and regenerate
   - Security issue → Log warning, continue
   - Missing field → Auto-correct and continue

3. **Container Errors**:
   - Docker not running → Clear error message
   - Build failure → Show build logs
   - Runtime error → Show container logs
   - Module missing → Already caught by auto-detection

4. **Database Errors**:
   - Connection failed → Graceful error page
   - Table not found → Show available tables
   - Schema mismatch → Suggest corrections

### Recovery Mechanisms

**Auto-Correction:**
```python
# Field name mismatches
if 'name' in result and 'plan_name' not in result:
    result['plan_name'] = result.pop('name')

# Import detection
if "import psycopg2" in script_code:
    requirements.add("psycopg2-binary")
```

**Retry with Feedback:**
```python
try:
    script = generate_script(...)
except SyntaxError as e:
    # Include error context in next attempt
    system_prompt += f"\\n\\nPREVIOUS ERROR: {e}\\nPlease fix."
    retry_generate(system_prompt)
```

---

## Complete Data Flow

```
USER INPUT (string)
    │
    ├→ LLMClient.init()
    │   ├→ Connect to LM Studio (localhost:1234)
    │   ├→ Verify Qwen2.5-Coder-7B-Instruct-MLX is loaded
    │   └→ Health check (no fallback)
    │
    ├→ inspect_database_schema()
    │   ├→ SQLAlchemy.inspect()
    │   ├→ Extract tables/columns/relationships
    │   └→ Format for LLM
    │       └→ schema_info (string)
    │
    ├→ analyze_task()
    │   ├→ Build system prompt
    │   ├→ Build user prompt with context
    │   ├→ LLM call (JSON mode)
    │   ├→ Parse JSON response
    │   └→ TaskAnalysis (Pydantic)
    │
    ├→ design_execution_plan()
    │   ├→ Build system prompt
    │   ├→ Build user prompt with TaskAnalysis
    │   ├→ LLM call (JSON mode)
    │   ├→ Parse JSON response
    │   ├→ Auto-fix field names
    │   ├→ Pydantic validation
    │   ├→ Plan validation
    │   └→ ExecutionPlan (Pydantic)
    │
    ├→ generate_script()
    │   ├→ Build system prompt (300+ lines)
    │   ├→ Build user prompt with:
    │   │   ├─ TaskAnalysis
    │   │   ├─ ExecutionPlan
    │   │   └─ schema_info
    │   ├→ LLM call (text mode)
    │   ├→ Clean code (remove markdown)
    │   ├→ Validate syntax (AST)
    │   ├→ Auto-detect imports
    │   ├→ Generate requirements.txt
    │   ├→ Generate .env.example
    │   └→ Return {script, requirements, env, metadata}
    │
    ├→ validate_script()
    │   ├→ Syntax validation (AST)
    │   ├→ Security analysis (regex)
    │   ├→ Best practices check
    │   ├→ Resource estimation
    │   └→ ValidationResult (Pydantic)
    │
    ├→ execute_script_in_container()
    │   ├→ Create execution directory
    │   ├→ Write script.py
    │   ├→ Write requirements.txt
    │   ├→ Write .env.example
    │   ├→ Generate Dockerfile
    │   ├→ Generate docker-compose.yml
    │   ├→ Generate deploy.sh
    │   ├→ Generate README.md
    │   ├→ Create directories (results, logs, exports)
    │   ├→ Build Docker image
    │   │   └→ docker-compose build
    │   ├→ Start container
    │   │   └→ docker-compose up -d
    │   └→ Check container status
    │       ├→ docker ps -a
    │       ├→ Parse status
    │       └→ Determine success/failure
    │
    ├→ _display_execution_results()
    │   ├→ Wait 2 seconds
    │   ├→ docker logs <container_name>
    │   ├→ Parse logs
    │   ├→ Extract results section
    │   ├→ Clean formatting
    │   └→ Display with logger.info()
    │
    └→ OUTPUT
        ├→ Results displayed in terminal
        ├→ Files saved in generated_scripts/
        └→ Container ready for inspection
```

---

## Tools & Dependencies Summary

### Python Libraries

| Library | Purpose | Usage |
|---------|---------|-------|
| `langchain_openai` | LLM Integration | LM Studio adapter (OpenAI-compatible) |
| `httpx` | HTTP Client | LM Studio health checks |
| `pydantic` | Data validation | Structured outputs |
| `loguru` | Logging | Color-coded terminal output |
| `sqlalchemy` | Database ORM | Schema inspection |
| `psycopg2` | PostgreSQL | Database connection |
| `python-dotenv` | Environment | Load .env files |
| `ast` | Syntax validation | Python code parsing |
| `subprocess` | Process execution | Docker commands |
| `pathlib` | File operations | Path management |
| `json` | JSON parsing | LLM response handling |
| `re` | Regex | Pattern matching |
| `datetime` | Timestamps | File naming |

### External Tools

| Tool | Purpose | Commands Used |
|------|---------|---------------|
| Docker | Containerization | `docker build`, `docker ps`, `docker logs` |
| Docker Compose | Orchestration | `docker-compose build`, `docker-compose up` |
| PostgreSQL | Database | SQL queries via psycopg2 |
| Bash | Scripting | deploy.sh execution |

### File Formats

- **Python (.py)**: Generated scripts
- **Text (.txt)**: Requirements files
- **YAML (.yml)**: Docker Compose configs
- **Dockerfile**: Container definitions
- **Bash (.sh)**: Deployment scripts
- **Markdown (.md)**: Documentation
- **ENV (.env)**: Environment variables

---

## Performance Metrics

### Timing Breakdown

| Stage | Duration | % of Total |
|-------|----------|------------|
| LLM Init | 5-10s | 8% |
| Schema Inspection | 1-2s | 2% |
| Task Analysis | 10-20s | 15% |
| Execution Planning | 15-30s | 23% |
| Script Generation | 20-60s | 38% |
| Validation | 1-2s | 2% |
| Container Build | 5-15s | 10% |
| Execution | 1-5s | 2% |
| **TOTAL** | **60-150s** | **100%** |

### Resource Usage

**Memory:**
- Script Executor: ~100 MB
- LLM Client: ~50 MB
- Container (base): ~128 MB
- Container (with pandas): ~384 MB
- **Peak Total**: ~662 MB

**CPU:**
- Script Executor: 0.1-0.5 cores
- Container: 0.5-1.0 cores
- **Peak Total**: 1.5 cores

**Disk:**
- Generated script directory: ~5 KB
- Docker image (base): ~150 MB
- Docker image (with deps): ~200-400 MB
- **Total per execution**: ~400 MB

### Scalability

**Current Limits:**
- Sequential execution (1 request at a time)
- Local hardware limits (M4 Mac: ~8-12 GB RAM for model)
- Inference speed (~20-50 tokens/sec on M4)
- Docker disk space (~10-20 GB for 50 containers)

**Optimization Opportunities:**
- Parallel validation and packaging
- LLM response caching
- Docker image layer caching
- Base image reuse

---

## Conclusion

This backend workflow demonstrates a sophisticated multi-stage pipeline that transforms natural language into executable code through:

1. **Intelligent Analysis**: LLM-powered understanding of user intent
2. **Dynamic Schema Discovery**: Real-time database inspection
3. **Structured Planning**: Step-by-step execution design
4. **Production-Quality Code**: Generation with best practices
5. **Multi-Layer Validation**: Security and quality checks
6. **Containerized Execution**: Isolated, reproducible environments
7. **Automatic Results**: Parsed and displayed output

The system leverages 12+ Python libraries, 4+ external tools, and 10+ data formats to deliver a seamless experience from prompt to results in approximately 2 minutes.

**Key Technical Achievements:**
- 100% structured LLM outputs (Pydantic validation)
- Automatic error recovery with retries
- Dynamic database schema discovery
- Container status detection (console vs web)
- Automatic import detection
- Clean code generation without markdown artifacts

**Production Readiness:**
- Security score validation (threshold: 0.7)
- Syntax validation before execution
- Error handling at every stage
- Comprehensive logging for debugging
- Graceful degradation on failures

---

**Document Version:** 1.0  
**Author:** Meta-Agent Development Team  
**Last Updated:** November 3, 2025

