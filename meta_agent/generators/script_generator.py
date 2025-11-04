"""
Script Generator
Generates executable Python scripts from execution plans
"""

import os
import ast
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from meta_agent.utils.llm_client import LLMClient
from meta_agent.planners.execution_planner import ExecutionPlan
from meta_agent.analyzers.task_analyzer import TaskAnalysis


class GeneratedScript(Dict[str, Any]):
    """Container for generated script and metadata"""
    pass


def generate_script(
    task_analysis: TaskAnalysis,
    execution_plan: ExecutionPlan,
    llm_client: LLMClient,
    database_schema=None,
    max_retries: int = 3
) -> GeneratedScript:
    """
    Generate executable Python script from execution plan (with retry on syntax errors)
    
    Args:
        task_analysis: Task analysis
        execution_plan: Execution plan
        llm_client: LLM client for generation
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with script, requirements, and metadata
        
    Raises:
        ValueError: If generation fails after all retries
    """
    logger.debug("Generating Python script...")
    logger.info(f"  Plan: {execution_plan.plan_name}")
    logger.info(f"  Steps: {len(execution_plan.steps)}")
    logger.info(f"  Web interface: {task_analysis.requires_web_interface}")
    logger.info(f"  Simulations: {task_analysis.requires_simulation}")
    
    # Build comprehensive prompts
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(task_analysis, execution_plan, database_schema)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"  Attempt {attempt + 1}/{max_retries}...")
            
            # Generate script
            script_code = llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=4096
            )
            
            # Clean up markdown if present
            script_code = _clean_code(script_code)
            
            # Validate syntax
            try:
                ast.parse(script_code)
                logger.debug("  ✓ Syntax validation passed")
            except SyntaxError as syntax_err:
                error_msg = f"Syntax error at line {syntax_err.lineno}: {syntax_err.msg}"
                logger.warning(f"  ✗ {error_msg}")
                
                if attempt < max_retries - 1:
                    # Provide feedback for retry
                    lines = script_code.split('\n')
                    error_line = syntax_err.lineno if syntax_err.lineno else 1
                    context_start = max(0, error_line - 3)
                    context_end = min(len(lines), error_line + 3)
                    context = '\n'.join(f"{i+1}: {lines[i]}" for i in range(context_start, context_end))
                    
                    system_prompt += f"\n\nPREVIOUS ATTEMPT HAD SYNTAX ERROR:\nError: {error_msg}\nContext:\n{context}\n\nCRITICAL FIX REQUIRED:\n- Check all brackets (), [], {{}} are properly closed\n- Check all quotes are properly closed\n- Ensure proper indentation\n- Make sure all function/class bodies are complete"
                    logger.info(f"  Retrying with error feedback...")
                    continue
                else:
                    raise
            
            # Generate requirements.txt (pass script for auto-detection)
            requirements = _generate_requirements(execution_plan, task_analysis.requires_web_interface, script_code)
            
            # Generate .env.example
            env_example = _generate_env_example(task_analysis, execution_plan, script_code)
            
            # Metadata
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "task_type": task_analysis.task_type,
                "plan_name": execution_plan.plan_name,
                "lines_of_code": len(script_code.split('\n')),
                "requires_web": task_analysis.requires_web_interface,
                "requires_simulation": task_analysis.requires_simulation,
                "dependencies": execution_plan.dependencies
            }
            
            logger.debug("✓ Script generated successfully")
            logger.info(f"  Lines of code: {metadata['lines_of_code']}")
            logger.info(f"  Dependencies: {len(requirements.split())}")
            
            return {
                "script": script_code,
                "requirements": requirements,
                "env_example": env_example,
                "metadata": metadata
            }
            
        except SyntaxError as e:
            if attempt >= max_retries - 1:
                logger.error(f"All {max_retries} attempts failed due to syntax errors")
                raise ValueError(f"Failed to generate valid script after {max_retries} attempts: {e}") from e
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise ValueError(f"Failed to generate script: {e}") from e


def _build_system_prompt() -> str:
    """Build system prompt for script generation"""
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
- IMPORTANT: Display results FIRST on homepage (dashboard view)
- Calculate for ALL records from database (not just one)
- Run calculation automatically when app starts
- Show pre-calculated results prominently for ALL entities
- Then provide simulation form below for what-if scenarios
- Add API endpoints for re-running calculations
- Serve on configurable host and port
- CRITICAL: Flask app.run() MUST use: app.run(host=CONFIG['host'], port=CONFIG['port'])
- CONFIG must include BOTH 'host' and 'port' keys

TERMINAL/CONSOLE OUTPUT (REQUIRED):
- Print calculation results to terminal/stdout as well as web
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

1. DB_NOT_CONFIGURED_TEMPLATE - When DATABASE_URL is empty/not set
   - Yellow warning box styling  
   - Clear instructions: "Edit .env file and add DATABASE_URL"
   - Show example DATABASE_URL format
   - Include restart instructions
   
2. ERROR_TEMPLATE - When ANY error occurs (connection, query, etc.)
   - Red error box styling
   - Show the actual error message using {{error}} template variable
   - Troubleshooting steps (check if DB is running, verify credentials, check schema, etc.)
   - MUST be defined or render_template_string(ERROR_TEMPLATE, error=str(e)) will crash!
   
3. EMPTY_DATABASE_TEMPLATE - When query returns no results
   - Blue info box styling
   - Message: "Database is connected but empty"
   - Show sample SQL INSERT statement to add data

**CRITICAL**: All 3 templates MUST be defined as module-level constants BEFORE any route handlers!

WEB INTERFACE STRUCTURE:
1. Homepage (/) should:
   - Query database to get available entities/properties
   - Auto-execute calculation for ALL entities found
   - Display results in a dashboard/table format showing all entities
   - Show key metrics prominently for each entity
   - If user mentioned specific entity, highlight it but show all
   - Include a "Run Simulation" section below results
   - Allow users to adjust parameters and re-calculate

2. Data Loading Strategy:
   - NEVER hardcode entity names in the script
   - Query database: SELECT * FROM [relevant_table]
   - Calculate for all entities found
   - Display results in a table/list
   - If specific entity mentioned in request, show it prominently but include others
   - Handle empty database gracefully with helpful message

FOR SIMULATIONS:
- Separate section BELOW the results dashboard
- Accept parameters from web form
- Calculate multiple scenarios on demand
- Show comparison between base case and scenarios
- Return results as JSON and HTML

DATABASE CONNECTION (CRITICAL):
- NEVER connect to database in __init__() - it will crash if DATABASE_URL is empty
- Check if DATABASE_URL is configured before attempting connection
- Defer connection until the route/function that needs it
- Pattern:
  ```python
  @app.route('/')
  def index():
      if not CONFIG['db_url']:
          return render_error_page("Database not configured")
      try:
          conn = psycopg2.connect(CONFIG['db_url'])
          # ... use connection ...
      except Exception as e:
          return render_error_page(f"Database error: {e}")
  ```
- DO NOT: self.conn = psycopg2.connect() in __init__ ❌
- DO: Connect only when needed, with error handling ✅

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

# ❌ WRONG: Accessing by index
property_name = row[0]
rental_income = row[3]
```

**CRITICAL RULES**:
1. ALWAYS use "SELECT *" - never list column names
2. ALWAYS use cursor.description to discover column names  
3. ALWAYS use dict(zip(columns, row)) to convert to dictionary
4. ALWAYS use row_dict.get() with defaults for safe access

- ALWAYS use cursor.description to get column names
- ALWAYS convert row tuples to dictionaries using zip(columns, row)
- ALWAYS use .get() with defaults for safe access
- Convert to appropriate types: float(), int(), str() as needed
- Handle None values gracefully

SECURITY:
- ALL database connections from env vars
- ALL API keys from env vars
- ALL sensitive config from env vars
- Use empty string defaults: os.getenv('KEY', '')

CODE STRUCTURE:
```python
#!/usr/bin/env python3
import os
from loguru import logger
# ... other imports

# Configuration from environment
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', '8080'))
}

class TaskExecutor:
    def __init__(self):
        # DO NOT connect to database here!
        # Store config only, connect later when needed
        pass
    
    def get_connection(self):
        # Create connection when actually needed
        if not CONFIG['db_url']:
            raise ValueError("DATABASE_URL not configured")
        return psycopg2.connect(CONFIG['db_url'])
    
    def execute(self):
        conn = self.get_connection()
        try:
            # ... do work with connection ...
            pass
        finally:
            conn.close()

# For Flask apps:
@app.route('/')
def index():
    # Check configuration first
    if not CONFIG['db_url']:
        return render_template_string(DB_NOT_CONFIGURED_TEMPLATE)
    
    try:
        executor = TaskExecutor()
        results = executor.execute()
        return render_template_string(RESULTS_TEMPLATE, results=results)
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template_string(ERROR_TEMPLATE, error=str(e))
```

OUTPUT RULES - CRITICAL:
- Output ONLY executable Python code
- NO explanations, NO comments outside the code
- NO markdown formatting (NO **, NO ###, NO ```)
- NO descriptions, NO notes, NO headers
- NO text like "HTML Template:" or "Example:" or "Note:"
- Start with #!/usr/bin/env python3
- End with the last line of actual Python code
- Do NOT add "This script..." or "Usage:" or any text after the code
- If including HTML templates, put them in Python strings ONLY
- ONLY Python code that can be directly executed
- Every single line must be valid Python syntax"""


def _build_user_prompt(task_analysis: TaskAnalysis, execution_plan: ExecutionPlan, database_schema=None) -> str:
    """Build user prompt with task and plan details"""
    from meta_agent.utils.database_inspector import format_schema_for_llm
    
    steps_description = "\n".join([
        f"{step.step_number}. {step.name} ({step.action}): {step.description}"
        for step in execution_plan.steps
    ])
    
    # Extract entity name if mentioned (for highlighting, not hardcoding)
    entity_name = None
    goal_lower = task_analysis.primary_goal.lower()
    if "orlando fashion square" in goal_lower:
        entity_name = "Orlando Fashion Square"
    elif "for " in goal_lower:
        # Try to extract entity after "for"
        parts = task_analysis.primary_goal.split("for ")
        if len(parts) > 1:
            entity_part = parts[1].split()[0:3]  # Get next few words
            entity_name = " ".join(entity_part).strip(".,;")
    
    entity_instruction = ""
    if entity_name:
        entity_instruction = f"""

**SPECIFIC ENTITY MENTIONED:** {entity_name}
IMPORTANT: Do NOT hardcode "{entity_name}" in your script.
Instead:
- Query database to fetch ALL available entities/properties
- Calculate results for ALL entities found
- Display all results in the dashboard
- Optionally highlight or sort "{entity_name}" first if found
- If no entities in database, show helpful message
- Script should work with any entities in the database, not just "{entity_name}"

Example:
```python
# Good: Query all properties
properties = fetch_all_properties()
for prop in properties:
    calculate_for(prop)

# Bad: Hardcoding
result = calculate_for("Orlando Fashion Square")  # ← NEVER DO THIS
```
"""
    else:
        entity_instruction = """

**NO SPECIFIC ENTITY MENTIONED**
- Query database to fetch ALL available entities/properties
- Calculate results for ALL entities found
- Display all results in the dashboard
- If no entities in database, show helpful message asking user to add data
"""
    
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
    # Access like: row_dict.get('property_name'), row_dict.get('noi'), etc.
```
"""
    
    return f"""Generate a complete Python script for this task:

**Goal:** {task_analysis.primary_goal}
{entity_instruction}
{schema_info}

**Execution Plan:** {execution_plan.plan_name}
{execution_plan.description}

**Steps:**
{steps_description}

**Requirements:**
- Web Interface: {"YES - Create web interface" if task_analysis.requires_web_interface else "NO - Console/terminal output only"}
- Simulations: {task_analysis.requires_simulation}
- Data Sources: {', '.join(task_analysis.data_sources)}

**Web Server Config:** {execution_plan.web_server_config if task_analysis.requires_web_interface else 'Not needed'}

**Simulation Config:** {execution_plan.simulation_config if task_analysis.requires_simulation else 'Not needed'}

**Dependencies Available:** {', '.join(execution_plan.dependencies)}

Generate COMPLETE, executable Python code. Include:
1. All imports (DO NOT import flask unless web interface is required)
2. Configuration from environment variables
3. Complete implementation of all steps
4. Error handling
5. Logging
6. Main execution block

{"**CRITICAL: NO WEB INTERFACE REQUESTED**" if not task_analysis.requires_web_interface else ""}
{"- DO NOT import flask" if not task_analysis.requires_web_interface else ""}
{"- DO NOT create HTML templates or routes" if not task_analysis.requires_web_interface else ""}
{"- DO NOT start a web server" if not task_analysis.requires_web_interface else ""}
{"- ONLY print results to console using logger.info()" if not task_analysis.requires_web_interface else ""}
{"- Script should calculate, print results, and exit" if not task_analysis.requires_web_interface else ""}

If web interface is needed:
- Calculate results for ALL records BEFORE starting Flask app
- Print results to terminal/console for user visibility
- Flask app with routes
- Homepage (/) that displays pre-calculated results
- HTML dashboard showing:
  * Pre-calculated results prominently displayed for ALL records
  * Key metrics in a clean layout
  * Table showing ALL entities from database
- Simulation form BELOW the results for what-if scenarios
- API endpoint for recalculation
- Make the page load show results immediately (no blank page)

CODE FLOW FOR WEB APPS (EXAMPLE):
Step 1: Calculate results for all records
Step 2: Print results to terminal using logger.info()
Step 3: Store results in global variable or pass to Flask routes
Step 4: Start Flask server and serve pre-calculated results
Example: Print each property name and its calculated metric to console before starting server

CRITICAL for web interfaces:
- The homepage MUST show calculation results on first load
- Query database to get ALL entities/properties dynamically
- Calculate and display results for ALL entities found
- NEVER hardcode specific entity names (like "Orlando Fashion Square")
- User should see results for all available entities immediately
- Simulation form is secondary, below the results

DATA LOADING STRATEGY (CRITICAL):
- On app startup or homepage load:
  1. Query with JOINs if data spans multiple tables
  2. Example: SELECT p.*, fm.* FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id
  3. Loop through all results
  4. Calculate metrics for each entity
  5. Display all in a table
- For financial/business calculations:
  * Data often split across: entity table + metrics/financial table
  * Use JOIN to combine property info + financial data
  * Handle cases where JOIN returns no rows (empty database)
- If specific entity was mentioned in request, optionally:
  * Highlight that row in the table
  * Sort it to top
  * But still show all other entities too
- Handle empty database gracefully with helpful error message

If simulations are needed:
- Accept scenario parameters in a form
- Run multiple scenarios (base, optimistic, pessimistic)
- Show comparison table with all scenarios
- Highlight differences between scenarios
- Generate comparison report
- Allow simulation for any entity (dropdown to select)

EXAMPLE STRUCTURE:
```python
@app.route('/')
def index():
    # Query all entities from database
    properties = query_all_properties()
    results = []
    for prop in properties:
        result = calculate_for(prop)
        results.append(result)
    return render_dashboard(results)
```

Make the code self-contained, dynamic, and immediately runnable with visible results for ALL database entities."""


def _clean_code(code: str) -> str:
    """Clean generated code of markdown artifacts and other issues"""
    import re
    code = code.strip()
    
    # Remove markdown code blocks from start
    while code.startswith("```python") or code.startswith("```"):
        if code.startswith("```python"):
            code = code[9:].strip()
        elif code.startswith("```"):
            code = code[3:].strip()
    
    # Remove markdown code blocks from end
    while code.endswith("```"):
        code = code[:-3].strip()
    
    # Remove any standalone ``` lines and markdown artifacts in the middle
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        
        # Skip lines that are just markdown fences
        if stripped in ["```", "```python", "```bash", "```json", "```yaml", "```html"]:
            continue
            
        # Skip markdown headers and formatting
        if stripped.startswith('**') and stripped.endswith('**'):
            continue
        if stripped.startswith('###') or stripped.startswith('##') or stripped.startswith('#'):
            # Only skip if it's a markdown header, not a Python comment
            if not line.lstrip().startswith('#'):
                continue
        
        # Skip numbered lists (markdown explanations)
        if re.match(r'^\d+\.\s+[A-Z]', stripped):  # e.g., "1. All necessary imports"
            continue
        
        # Skip common explanatory patterns
        if any(phrase in stripped.lower() for phrase in [
            '**html template', '**note:', '**explanation:', '**usage:',
            'this script', 'this code', 'the above code', 'this will',
            'to run this', 'to use this', 'example usage'
        ]):
            continue
        
        cleaned_lines.append(line)
    
    code = '\n'.join(cleaned_lines)
    
    # Remove trailing explanatory text that's not Python code
    # Look for common patterns that indicate explanatory text after code
    lines = code.split('\n')
    last_valid_line = len(lines) - 1
    
    # Find the last line that looks like valid Python code
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        # Skip empty lines
        if not line:
            continue
        # Check if this looks like explanatory text (no Python syntax)
        if any(phrase in line.lower() for phrase in [
            'this script', 'this code', 'note:', 'explanation:',
            'to use', 'to run', 'usage:', 'example:',
            'the above', 'this will', 'this implementation'
        ]):
            last_valid_line = i - 1
            continue
        # If it doesn't start with valid Python (comment, code, etc.)
        if line and not (
            line.startswith('#') or 
            line.startswith('"""') or 
            line.startswith("'''") or
            line[0].isalpha() or 
            line[0] in '()[]{}@' or
            line[0].isspace()
        ):
            last_valid_line = i - 1
            continue
        break
    
    # Trim to last valid line
    if last_valid_line < len(lines) - 1:
        code = '\n'.join(lines[:last_valid_line + 1])
    
    return code.strip()


def _generate_requirements(execution_plan: ExecutionPlan, has_web_interface: bool = False, script_code: str = "") -> str:
    """Generate requirements.txt content"""
    
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
    
    # Replace psycopg2 with psycopg2-binary for Docker compatibility
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


def _generate_env_example(task_analysis: TaskAnalysis, execution_plan: ExecutionPlan, script_code: str = "") -> str:
    """Generate .env.example content"""
    
    env_vars = []
    
    # Database if needed - check both data_sources and if psycopg2 is imported
    needs_database = (
        "postgresql" in task_analysis.data_sources or
        "import psycopg2" in script_code or
        "from psycopg2" in script_code
    )
    
    if needs_database:
        # Try to use actual DATABASE_URL from environment or config file
        db_url = os.getenv('DATABASE_URL')
        
        # If not in environment, try reading from project .env file
        if not db_url:
            try:
                from pathlib import Path
                env_file = Path(__file__).parent.parent.parent / '.env'
                if env_file.exists():
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('DATABASE_URL='):
                                db_url = line.split('=', 1)[1].strip()
                                break
            except Exception:
                pass
        
        # Default to known working DATABASE_URL if still not found
        if not db_url:
            # Use the DSCR POC database from setup_env.sh as default
            db_url = 'postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db'
        
        # For Docker containers, replace localhost with host.docker.internal
        if '@localhost:' in db_url:
            db_url = db_url.replace('@localhost:', '@host.docker.internal:')
        
        env_vars.append(f"DATABASE_URL={db_url}")
    
    # Web server if needed
    if task_analysis.requires_web_interface:
        port = execution_plan.web_server_config.get('port', 8080)
        env_vars.append(f"PORT={port}")
        env_vars.append("HOST=0.0.0.0")
    
    # Output directory
    env_vars.append("OUTPUT_DIR=./results")
    
    # Log level
    env_vars.append("LOG_LEVEL=INFO")
    
    return "\n".join(env_vars)

