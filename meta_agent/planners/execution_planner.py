"""
Execution Planner
Designs step-by-step execution plans from task analysis
"""

from typing import Dict, Any, List
from loguru import logger
from pydantic import BaseModel, Field

from meta_agent.utils.llm_client import LLMClient
from meta_agent.analyzers.task_analyzer import TaskAnalysis


class ExecutionStep(BaseModel):
    """Single step in execution plan"""
    step_number: int = Field(description="Step number in sequence")
    name: str = Field(description="Step name")
    action: str = Field(description="Action type: database_query, calculation, api_call, file_operation, report_generation, web_server")
    description: str = Field(description="What this step does")
    inputs: List[str] = Field(default_factory=list, description="Input variables needed")
    outputs: List[str] = Field(default_factory=list, description="Output variables produced")
    code_template: str = Field(default="", description="Code template or logic")
    error_handling: str = Field(default="log_and_continue", description="Error handling strategy")


class ExecutionPlan(BaseModel):
    """Complete execution plan"""
    plan_name: str = Field(description="Name of the execution plan")
    description: str = Field(description="Overall plan description")
    steps: List[ExecutionStep] = Field(description="Ordered list of execution steps")
    dependencies: List[str] = Field(default_factory=list, description="External dependencies needed")
    web_server_config: Dict[str, Any] = Field(default_factory=dict, description="Web server configuration if needed")
    simulation_config: Dict[str, Any] = Field(default_factory=dict, description="Simulation configuration if needed")
    estimated_lines_of_code: int = Field(description="Estimated LOC for implementation")


def design_execution_plan(task_analysis: TaskAnalysis, llm_client: LLMClient, max_retries: int = 3) -> ExecutionPlan:
    """
    Design step-by-step execution plan from task analysis (with retry on JSON errors)
    
    Args:
        task_analysis: Analyzed task requirements
        llm_client: LLM client for planning
        max_retries: Maximum number of retry attempts
        
    Returns:
        ExecutionPlan with detailed steps
        
    Raises:
        ValueError: If planning fails after all retries
    """
    logger.debug("Designing execution plan...")
    logger.info(f"  Task type: {task_analysis.task_type}")
    logger.info(f"  Complexity: {task_analysis.complexity}")
    
    system_prompt = """You are an expert software architect. Design detailed execution plans that can be implemented as Python scripts.

Break down tasks into clear, executable steps. Each step should be:
1. Specific and actionable
2. Have clear inputs and outputs
3. Include error handling strategy

For web interfaces, include Flask/FastAPI setup.
For simulations, include parameter variation logic.

CRITICAL: Output ONLY valid, complete JSON. Ensure ALL JSON objects are properly closed with closing braces and brackets.

Output structure:
{
    "plan_name": "descriptive_name",
    "description": "what this plan does",
    "steps": [
        {
            "step_number": 1,
            "name": "step_name",
            "action": "database_query|calculation|api_call|file_operation|report_generation|web_server",
            "description": "what this does",
            "inputs": ["input1", "input2"],
            "outputs": ["output1"],
            "code_template": "pseudocode or Python template",
            "error_handling": "strategy"
        }
    ],
    "dependencies": ["flask", "psycopg2", "pandas"],
    "web_server_config": {"port": 8080, "host": "0.0.0.0"},
    "simulation_config": {"parameters": [...], "scenarios": [...]},
    "estimated_lines_of_code": 200
}

IMPORTANT: Keep descriptions concise. Make sure the JSON is complete and valid."""

    user_prompt = f"""Design an execution plan for this task:

**Task Type:** {task_analysis.task_type}
**Goal:** {task_analysis.primary_goal}
**Web Interface Needed:** {task_analysis.requires_web_interface}
**Simulations Needed:** {task_analysis.requires_simulation}
**Data Sources:** {', '.join(task_analysis.data_sources)}
**Complexity:** {task_analysis.complexity}

**Required Inputs:**
{[inp for inp in task_analysis.required_inputs]}

**Expected Outputs:**
{[out for out in task_analysis.expected_outputs]}

Design a complete, step-by-step execution plan. Output ONLY the complete JSON, no explanations."""

    for attempt in range(max_retries):
        try:
            logger.info(f"  Attempt {attempt + 1}/{max_retries}...")
            
            # Call LLM for planning with increased tokens on retry
            max_tokens = 2000 + (attempt * 500)  # Increase tokens on retry
            result = llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=max_tokens
            )
            
            # Fix common field name mismatches (LLM sometimes uses 'name' instead of 'plan_name')
            if 'name' in result and 'plan_name' not in result:
                result['plan_name'] = result.pop('name')
            
            # Parse into ExecutionPlan
            plan = ExecutionPlan(**result)
            
            logger.debug("✓ Execution plan designed successfully")
            logger.info(f"  Plan: {plan.plan_name}")
            logger.info(f"  Steps: {len(plan.steps)}")
            logger.info(f"  Dependencies: {len(plan.dependencies)}")
            logger.info(f"  Estimated LOC: {plan.estimated_lines_of_code}")
            
            return plan
            
        except (ValueError, Exception) as e:
            logger.warning(f"  Attempt {attempt + 1} failed: {str(e)[:100]}")
            
            if attempt < max_retries - 1:
                logger.info(f"  Retrying with increased token limit...")
                # Add feedback to system prompt for next attempt
                system_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: {str(e)[:200]}\nPlease ensure the JSON is complete and properly formatted."
            else:
                logger.error(f"All {max_retries} attempts failed")
                raise ValueError(f"Failed to design execution plan after {max_retries} attempts: {e}") from e


def validate_execution_plan(plan: ExecutionPlan) -> bool:
    """
    Validate execution plan
    
    Args:
        plan: ExecutionPlan to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    logger.debug("Validating execution plan...")
    
    if not plan.plan_name:
        raise ValueError("Plan name is required")
    
    if not plan.steps or len(plan.steps) == 0:
        raise ValueError("Execution plan must have at least one step")
    
    # Validate step sequence
    step_numbers = [step.step_number for step in plan.steps]
    if step_numbers != list(range(1, len(step_numbers) + 1)):
        raise ValueError("Steps must be numbered sequentially starting from 1")
    
    # Validate action types (flexible - allow common variations)
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
            # Log warning but don't fail - LLM might use reasonable variations
            logger.warning(f"Unusual action type in step {step.step_number}: {step.action} (proceeding anyway)")
    
    logger.debug("✓ Execution plan validation passed")
    return True

