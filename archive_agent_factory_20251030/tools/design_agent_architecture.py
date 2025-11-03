"""
Tool #2: Design Agent Architecture
Designs the agent system architecture from requirements using LLM.
NO FALLBACKS - Strictly requires LLM.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from loguru import logger

from meta_agent.utils.llm_client import LLMClient
from meta_agent.tools.analyze_requirements import RequirementsAnalysis


class AgentDesign(BaseModel):
    """Design for a single agent"""
    agent_name: str = Field(..., description="Name of the agent")
    agent_type: str = Field(..., description="Type: data_retrieval, calculation, analysis, decision, report, code_gen")
    role: str = Field(..., description="Role: tool, primary_agent, supporting_agent")
    responsibilities: List[str] = Field(..., description="List of responsibilities")
    dependencies: List[str] = Field(..., description="Dependencies on other components")
    complexity: str = Field(..., description="Complexity: LOW, MEDIUM, HIGH")
    internal_components: List[str] = Field(default_factory=list, description="Internal components (if complex)")
    uses_llm: bool = Field(default=False, description="Whether this agent uses LLM")


class AgentInteraction(BaseModel):
    """Interaction between agents"""
    from_agent: str = Field(..., alias="from", description="Source agent")
    to_agent: str = Field(..., alias="to", description="Target agent")
    interaction_type: str = Field(..., description="Type: tool_call, data_flow, coordination")
    method: str = Field(default="", description="Method name if tool_call")


class ArchitectureDesign(BaseModel):
    """Complete architecture design"""
    agents: List[AgentDesign] = Field(..., description="List of agent designs")
    interactions: List[AgentInteraction] = Field(..., description="Agent interactions")
    data_flow: str = Field(..., description="Description of data flow")
    no_orchestrator_needed: bool = Field(..., description="Whether orchestrator is needed")
    reasoning: str = Field(..., description="Reasoning for architecture decisions")


def design_agent_architecture(
    requirements: RequirementsAnalysis,
    llm_client: LLMClient
) -> ArchitectureDesign:
    """
    Design agent system architecture from requirements.
    
    Args:
        requirements: Analyzed requirements
        llm_client: LLM client instance
    
    Returns:
        Architecture design
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If LLM response is invalid
    """
    logger.info("Designing agent architecture...")
    logger.info(f"  Complexity: {requirements.complexity}")
    logger.info(f"  Estimated agents: {requirements.estimated_agents}")
    
    system_prompt = """You are an expert software architect specializing in agent-based systems.
Your task is to design a practical, efficient agent architecture based on requirements.

Given requirements, you must design:
1. Which specific agents are needed (DataAgent, CalcAgent, etc.)
2. Each agent's role (tool, primary_agent, supporting_agent)
3. Each agent's responsibilities
4. Dependencies between agents
5. Complexity level for each agent
6. Internal components (for complex agents)
7. Whether LLM integration is needed per agent
8. Data flow between agents
9. Whether an orchestrator is needed (usually NO for 2-agent systems)

GUIDELINES:
- For simple single-metric analysis: 2 agents (DataAgent as tool, CalcAgent as primary)
- DataAgent is always a simple tool (LOW complexity)
- CalcAgent complexity depends on modes and features
- LLM integration only for analysis/decision-making agents
- Multi-mode CalcAgent needs internal components:
  * ModeDetector
  * StandardCalculator
  * LibraryCalculator (if library mode)
  * CustomCalculator (if custom mode)
  * AnalysisEngine (if LLM analysis)
  * DecisionEngine (if LLM decisions)
  * ReportGenerator
- No orchestrator needed if <= 2 agents with simple interaction

Output MUST be valid JSON with this exact structure:
{
    "agents": [
        {
            "agent_name": "AgentName",
            "agent_type": "data_retrieval|calculation|analysis|decision|report|code_gen",
            "role": "tool|primary_agent|supporting_agent",
            "responsibilities": ["responsibility1", "responsibility2"],
            "dependencies": ["dependency1"],
            "complexity": "LOW|MEDIUM|HIGH",
            "internal_components": ["component1"],
            "uses_llm": true|false
        }
    ],
    "interactions": [
        {
            "from": "AgentA",
            "to": "AgentB",
            "interaction_type": "tool_call|data_flow|coordination",
            "method": "method_name"
        }
    ],
    "data_flow": "description of data flow",
    "no_orchestrator_needed": true|false,
    "reasoning": "explanation of architecture decisions"
}

IMPORTANT: Output ONLY the JSON, no other text."""

    user_prompt = f"""Design an agent architecture for these requirements:

PRIMARY GOAL: {requirements.primary_goal}
REQUIRED AGENTS: {', '.join(requirements.required_agents)}
DATA SOURCES: {', '.join(requirements.data_sources)}
CALCULATIONS: {len(requirements.calculations_needed)} calculations
MODES: {', '.join(requirements.modes_required)}
COMPLEXITY: {requirements.complexity}
LLM INTEGRATION: {requirements.llm_integration}
FEATURES: {', '.join(requirements.features_required)}

Design an efficient, practical architecture in the JSON format specified."""

    try:
        # Call LLM to design architecture
        response_json = llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )
        
        # Parse into Pydantic model for validation
        architecture = ArchitectureDesign(**response_json)
        
        logger.info(f"✓ Architecture designed successfully")
        logger.info(f"  Agents: {len(architecture.agents)}")
        for agent in architecture.agents:
            logger.info(f"    - {agent.agent_name} ({agent.agent_type}, {agent.role}, {agent.complexity})")
        logger.info(f"  Interactions: {len(architecture.interactions)}")
        logger.info(f"  Orchestrator needed: {not architecture.no_orchestrator_needed}")
        
        return architecture
        
    except Exception as e:
        logger.error(f"Failed to design architecture: {e}")
        raise RuntimeError(
            f"Architecture design failed: {e}. "
            f"This indicates an issue with LLM response or parsing."
        ) from e


def validate_architecture(architecture: ArchitectureDesign) -> bool:
    """
    Validate architecture design is complete and consistent.
    
    Args:
        architecture: Architecture design
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If architecture is invalid
    """
    logger.info("Validating architecture design...")
    
    if not architecture.agents:
        raise ValueError("At least one agent must be designed")
    
    # Check all agent names are unique
    agent_names = [a.agent_name for a in architecture.agents]
    if len(agent_names) != len(set(agent_names)):
        raise ValueError("Agent names must be unique")
    
    # Check interactions reference valid agents
    for interaction in architecture.interactions:
        if interaction.from_agent not in agent_names:
            raise ValueError(f"Interaction references unknown agent: {interaction.from_agent}")
        if interaction.to_agent not in agent_names:
            raise ValueError(f"Interaction references unknown agent: {interaction.to_agent}")
    
    # Check dependencies reference valid components
    for agent in architecture.agents:
        for dep in agent.dependencies:
            # Dependencies can be agents or external services
            if dep in agent_names:
                continue
            # External dependencies are OK (PostgreSQL, LLMClient, etc.)
            logger.debug(f"{agent.agent_name} depends on external: {dep}")
    
    # Check complexity values are valid
    for agent in architecture.agents:
        if agent.complexity not in ["LOW", "MEDIUM", "HIGH"]:
            raise ValueError(f"Invalid complexity for {agent.agent_name}: {agent.complexity}")
    
    logger.info("✓ Architecture validation passed")
    return True

