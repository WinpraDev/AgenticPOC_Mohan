"""
Task Analyzer
Analyzes user requests to understand what needs to be executed
"""

from typing import Dict, Any, List
from loguru import logger
from pydantic import BaseModel, Field

from meta_agent.utils.llm_client import LLMClient


class TaskAnalysis(BaseModel):
    """Result of task analysis"""
    task_type: str = Field(description="Type of task: calculation, data_processing, analysis, report, web_app")
    primary_goal: str = Field(description="Main objective")
    requires_web_interface: bool = Field(default=False, description="Whether a web interface is needed")
    requires_simulation: bool = Field(default=False, description="Whether simulations are needed")
    data_sources: List[str] = Field(default_factory=list, description="Required data sources")
    required_inputs: List[Dict[str, Any]] = Field(default_factory=list, description="Required input parameters")
    expected_outputs: List[Dict[str, Any]] = Field(default_factory=list, description="Expected outputs")
    complexity: str = Field(description="Task complexity: LOW, MEDIUM, HIGH")
    estimated_execution_time: str = Field(description="Estimated time to execute")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "calculation",
                "primary_goal": "Calculate DSCR for property",
                "requires_web_interface": True,
                "requires_simulation": True,
                "data_sources": ["postgresql"],
                "required_inputs": [{"name": "property_id", "type": "string"}],
                "expected_outputs": [{"name": "dscr_value", "type": "float"}],
                "complexity": "LOW",
                "estimated_execution_time": "5 seconds"
            }
        }


def analyze_task(user_request: str, llm_client: LLMClient) -> TaskAnalysis:
    """
    Analyze user's task requirements
    
    Args:
        user_request: Natural language task description
        llm_client: LLM client for analysis
        
    Returns:
        TaskAnalysis with structured task information
        
    Raises:
        ValueError: If analysis fails or request is invalid
    """
    logger.info(f"Analyzing task from user request (length: {len(user_request)} chars)")
    
    system_prompt = """You are an expert system analyst. Analyze user requests to understand what needs to be executed.

Your task is to extract:
1. Task type (calculation, data_processing, analysis, report_generation, web_app)
2. Primary goal
3. Whether a web interface is needed (look for keywords: website, dashboard, web, interface, visualize)
4. Whether simulations are needed (look for keywords: scenarios, what-if, simulate, compare)
5. Required data sources (databases, APIs, files)
6. Required inputs
7. Expected outputs
8. Complexity (LOW/MEDIUM/HIGH)
9. Estimated execution time

Output ONLY valid JSON matching this structure:
{
    "task_type": "calculation|data_processing|analysis|report_generation|web_app",
    "primary_goal": "clear description",
    "requires_web_interface": true|false,
    "requires_simulation": true|false,
    "data_sources": ["postgresql", "api", etc],
    "required_inputs": [{"name": "input_name", "type": "string|int|float"}],
    "expected_outputs": [{"name": "output_name", "type": "string|int|float"}],
    "complexity": "LOW|MEDIUM|HIGH",
    "estimated_execution_time": "X seconds"
}

Be accurate and specific."""

    user_prompt = f"""Analyze this task request:

{user_request}

Extract all task requirements and output JSON."""

    try:
        # Call LLM for analysis
        result = llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse into TaskAnalysis
        analysis = TaskAnalysis(**result)
        
        logger.debug("✓ Task analyzed successfully")
        logger.info(f"  Task type: {analysis.task_type}")
        logger.info(f"  Web interface: {analysis.requires_web_interface}")
        logger.info(f"  Simulations: {analysis.requires_simulation}")
        logger.info(f"  Complexity: {analysis.complexity}")
        
        # Log detailed task analysis
        logger.debug("="*60)
        logger.debug("TASK ANALYSIS DETAILS")
        logger.debug("="*60)
        logger.debug(f"Task Type: {analysis.task_type}")
        logger.debug(f"Complexity: {analysis.complexity}")
        logger.debug(f"Estimated Execution Time: {analysis.estimated_execution_time}")
        logger.debug(f"")
        logger.debug(f"Primary Goal:")
        logger.debug(f"  {analysis.primary_goal}")
        logger.debug(f"")
        
        if analysis.data_sources:
            logger.debug(f"Data Sources ({len(analysis.data_sources)}):")
            for source in analysis.data_sources:
                logger.debug(f"  • {source}")
            logger.debug(f"")
        
        if analysis.required_inputs:
            logger.debug(f"Required Inputs ({len(analysis.required_inputs)}):")
            for inp in analysis.required_inputs:
                name = inp.get('name', 'unknown')
                inp_type = inp.get('type', 'unknown')
                logger.debug(f"  • {name} ({inp_type})")
            logger.debug(f"")
        
        if analysis.expected_outputs:
            logger.debug(f"Expected Outputs ({len(analysis.expected_outputs)}):")
            for out in analysis.expected_outputs:
                name = out.get('name', 'unknown')
                out_type = out.get('type', 'unknown')
                logger.debug(f"  • {name} ({out_type})")
            logger.debug(f"")
        
        logger.debug(f"Features:")
        logger.debug(f"  Web Interface: {analysis.requires_web_interface}")
        logger.debug(f"  Simulations: {analysis.requires_simulation}")
        logger.debug(f"")
        
        logger.debug("="*60)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Task analysis failed: {e}")
        raise ValueError(f"Failed to analyze task: {e}") from e


def validate_task_analysis(analysis: TaskAnalysis) -> bool:
    """
    Validate task analysis results
    
    Args:
        analysis: TaskAnalysis to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    logger.debug("Validating task analysis...")
    
    # Check required fields
    if not analysis.task_type:
        raise ValueError("Task type is required")
    
    if not analysis.primary_goal:
        raise ValueError("Primary goal is required")
    
    if not analysis.complexity:
        raise ValueError("Complexity assessment is required")
    
    # Validate task type
    valid_types = ["calculation", "data_processing", "analysis", "report_generation", "web_app"]
    if analysis.task_type not in valid_types:
        raise ValueError(f"Invalid task type: {analysis.task_type}. Must be one of {valid_types}")
    
    # Validate complexity
    if analysis.complexity not in ["LOW", "MEDIUM", "HIGH"]:
        raise ValueError(f"Invalid complexity: {analysis.complexity}")
    
    logger.debug("✓ Task analysis validation passed")
    return True

