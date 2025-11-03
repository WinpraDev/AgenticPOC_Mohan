"""
Tool #1: Analyze Requirements
Extracts structured requirements from natural language using LLM.
NO FALLBACKS - Strictly requires LLM.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from loguru import logger

from meta_agent.utils.llm_client import LLMClient


class RequirementsAnalysis(BaseModel):
    """Structured output from requirements analysis"""
    primary_goal: str = Field(..., description="Main objective of the agent system")
    required_agents: List[str] = Field(..., description="List of agents needed")
    data_sources: List[str] = Field(..., description="Data sources to connect to")
    calculations_needed: List[Dict[str, Any]] = Field(..., description="Calculations to perform")
    modes_required: List[str] = Field(..., description="Execution modes needed")
    validation_rules: List[Dict[str, Any]] = Field(..., description="Validation rules")
    output_format: str = Field(..., description="Expected output format")
    constraints: List[str] = Field(..., description="System constraints")
    complexity: str = Field(..., description="Overall complexity: LOW, MEDIUM, or HIGH")
    estimated_agents: int = Field(..., description="Estimated number of agents")
    llm_integration: bool = Field(..., description="Whether LLM integration is needed")
    features_required: List[str] = Field(..., description="Special features needed")


def analyze_requirements(user_request: str, llm_client: LLMClient) -> RequirementsAnalysis:
    """
    Analyze natural language requirements and extract structured information.
    
    Args:
        user_request: Natural language description of what user wants
        llm_client: LLM client instance
    
    Returns:
        Structured requirements analysis
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If LLM response is invalid
    """
    logger.info(f"Analyzing requirements from user request (length: {len(user_request)} chars)")
    
    system_prompt = """You are an expert system architect specializing in agent-based systems.
Your task is to analyze user requirements and extract structured information.

Given a natural language description of what the user wants to build, you must:
1. Identify the primary goal
2. Determine which agents are needed (DataAgent, CalcAgent, AnalysisAgent, etc.)
3. Identify data sources (PostgreSQL, APIs, files, etc.)
4. List calculations that need to be performed
5. Determine execution modes (standard, library, custom)
6. Define validation rules
7. Assess overall complexity (LOW, MEDIUM, HIGH)
8. Identify if LLM integration is needed for analysis/decisions
9. List any special features (code generation, sandbox, etc.)

Output MUST be valid JSON with this exact structure:
{
    "primary_goal": "description",
    "required_agents": ["agent1", "agent2"],
    "data_sources": ["source1", "source2"],
    "calculations_needed": [
        {"name": "metric_name", "formula": "formula", "inputs": ["input1"]}
    ],
    "modes_required": ["standard", "library", "custom"],
    "validation_rules": [
        {"metric": "name", "condition": ">=1.25", "status_if_pass": "PASS"}
    ],
    "output_format": "description",
    "constraints": ["constraint1", "constraint2"],
    "complexity": "LOW|MEDIUM|HIGH",
    "estimated_agents": 2,
    "llm_integration": true|false,
    "features_required": ["feature1", "feature2"]
}

IMPORTANT: Output ONLY the JSON, no other text."""

    user_prompt = f"""Analyze this user requirement and extract structured information:

USER REQUEST:
{user_request}

Provide the analysis in the JSON format specified."""

    try:
        # Call LLM to analyze requirements
        response_json = llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1  # Low temperature for consistency
        )
        
        # Parse into Pydantic model for validation
        requirements = RequirementsAnalysis(**response_json)
        
        logger.info(f"✓ Requirements analyzed successfully")
        logger.info(f"  Primary goal: {requirements.primary_goal}")
        logger.info(f"  Agents needed: {len(requirements.required_agents)}")
        logger.info(f"  Complexity: {requirements.complexity}")
        logger.info(f"  LLM integration: {requirements.llm_integration}")
        
        return requirements
        
    except Exception as e:
        logger.error(f"Failed to analyze requirements: {e}")
        raise RuntimeError(
            f"Requirements analysis failed: {e}. "
            f"This indicates an issue with LLM response or parsing."
        ) from e


def validate_requirements(requirements: RequirementsAnalysis) -> bool:
    """
    Validate that requirements are complete and feasible.
    
    Args:
        requirements: Analyzed requirements
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If requirements are incomplete or infeasible
    """
    logger.info("Validating requirements...")
    
    # Check required fields are not empty
    if not requirements.primary_goal:
        raise ValueError("Primary goal must be specified")
    
    if not requirements.required_agents:
        raise ValueError("At least one agent must be required")
    
    if requirements.estimated_agents < 1:
        raise ValueError("Estimated agents must be at least 1")
    
    if requirements.complexity not in ["LOW", "MEDIUM", "HIGH"]:
        raise ValueError(f"Invalid complexity: {requirements.complexity}")
    
    # Check for data sources if agents require data
    if any("Data" in agent for agent in requirements.required_agents):
        if not requirements.data_sources:
            raise ValueError("Data sources must be specified if DataAgent is required")
    
    # Check for calculation details if calculation agents present
    if any("Calc" in agent for agent in requirements.required_agents):
        if not requirements.calculations_needed:
            raise ValueError("Calculations must be specified if CalcAgent is required")
    
    logger.info("✓ Requirements validation passed")
    return True

