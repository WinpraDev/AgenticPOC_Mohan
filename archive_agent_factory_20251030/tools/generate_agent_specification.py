"""
Tool #3: Generate Agent Specification
Generates detailed YAML specification for an agent using LLM.
NO FALLBACKS - Strictly requires LLM.
Includes auto-retry for invalid YAML.
"""

from typing import Dict, Any, Optional
from loguru import logger
import yaml

from meta_agent.utils.llm_client import LLMClient
from meta_agent.tools.design_agent_architecture import AgentDesign, ArchitectureDesign
from meta_agent.tools.analyze_requirements import RequirementsAnalysis


def _check_yaml_validity(yaml_text: str) -> Optional[str]:
    """
    Check if YAML is valid and return error message if not.
    
    Args:
        yaml_text: YAML text to check
    
    Returns:
        Error message if invalid, None if valid
    """
    try:
        yaml.safe_load(yaml_text)
        return None
    except yaml.YAMLError as e:
        return str(e)
    except Exception as e:
        return f"Parse error: {str(e)}"


def generate_agent_specification_with_retry(
    agent_design: AgentDesign,
    architecture: ArchitectureDesign,
    requirements: RequirementsAnalysis,
    llm_client: LLMClient,
    max_retries: int = 5
) -> str:
    """
    Generate YAML specification with automatic retry on invalid YAML.
    
    Args:
        agent_design: Design for the specific agent
        architecture: Full architecture context
        requirements: Original requirements
        llm_client: LLM client instance
        max_retries: Maximum number of retry attempts
    
    Returns:
        Valid YAML specification as string
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If specification generation fails after retries
    """
    logger.info("Generating specification with auto-retry...")
    
    additional_instructions = ""
    
    for attempt in range(max_retries):
        try:
            # Try to generate specification
            yaml_spec = generate_agent_specification(
                agent_design, architecture, requirements, llm_client, additional_instructions
            )
            
            # Check YAML validity
            yaml_error = _check_yaml_validity(yaml_spec)
            
            if yaml_error is None:
                # Success!
                if attempt > 0:
                    logger.info(f"✓ Specification generated successfully after {attempt} retries")
                return yaml_spec
            else:
                # YAML error found
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Invalid YAML detected")
                logger.warning(f"  Error: {yaml_error}")
                
                if attempt < max_retries - 1:
                    # Try again with feedback
                    logger.info(f"  Retrying with error feedback...")
                    
                    # Build specific error guidance
                    additional_instructions = f"""

# ⚠️ PREVIOUS ATTEMPT GENERATED INVALID YAML:
# Error: {yaml_error}
# 
# CRITICAL: Generate VALID YAML only. Common issues to avoid:
# - Don't use ':' in free text without quotes (e.g., "ErrorType: InvalidPropertyID" is invalid)
# - Always quote strings containing special characters
# - Ensure proper indentation (2 spaces per level)
# - Don't use unquoted strings with colons, brackets, or braces
# - Use proper YAML list syntax with '- ' prefix
# 
# Example CORRECT format:
#   test_scenarios:
#     - name: "Valid Test"
#       expected: "Some result"
# 
# Example INCORRECT format:
#   test_scenarios:
#     - name: Valid Test
#       expected: ErrorType: SomeError  # BAD - unquoted colon!
"""
                else:
                    # Final attempt failed
                    logger.error(f"Failed to generate valid YAML after {max_retries} attempts")
                    raise ValueError(
                        f"Specification generation failed after {max_retries} attempts. "
                        f"Last error: {yaml_error}"
                    )
        
        except ValueError as e:
            # Re-raise ValueError (includes final retry failure)
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries}: Generation error: {e}")
            if attempt >= max_retries - 1:
                raise RuntimeError(f"Specification generation failed after {max_retries} attempts: {e}") from e
    
    raise RuntimeError("Specification generation failed: Maximum retries reached")


def generate_agent_specification(
    agent_design: AgentDesign,
    architecture: ArchitectureDesign,
    requirements: RequirementsAnalysis,
    llm_client: LLMClient,
    additional_instructions: str = ""
) -> str:
    """
    Generate detailed YAML specification for an agent.
    
    Args:
        agent_design: Design for the specific agent
        architecture: Full architecture context
        requirements: Original requirements
        llm_client: LLM client instance
        additional_instructions: Additional instructions for retry attempts
    
    Returns:
        YAML specification as string
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If LLM response is invalid YAML
    """
    logger.info(f"Generating specification for {agent_design.agent_name}...")
    logger.info(f"  Type: {agent_design.agent_type}")
    logger.info(f"  Role: {agent_design.role}")
    logger.info(f"  Complexity: {agent_design.complexity}")
    
    # Build context about other agents for cross-references
    other_agents = [a.agent_name for a in architecture.agents if a.agent_name != agent_design.agent_name]
    
    system_prompt = """You are an expert in agent system design and YAML specification.
Your task is to generate a complete, detailed YAML specification for an agent.

The specification must follow this structure:

agent_name: AgentName
agent_type: type
version: 1.0.0
description: |
  Detailed description

role: tool|primary_agent|supporting_agent

capabilities:
  - name: capability_name
    description: What this capability does
    inputs:
      - name: input_name
        type: type
        required: true|false
        validation: validation_rule
    outputs:
      - name: output_name
        type: type
        schema: {...}
    error_handling:
      - error: ErrorType
        action: how_to_handle
        message: error_message

data_sources:  # If agent accesses data
  - type: postgresql|api|file
    connection: connection_string_or_config
    tables: [table1, table2]  # for databases

workflow:  # If agent has complex workflow
  steps:
    step_name:
      description: what this step does
      logic: |
        Detailed logic description
      branches: ...  # if conditional

tools:  # If agent uses other agents/tools
  - name: ToolName
    purpose: why this tool is used
    calls: [method1, method2]

dependencies:
  python_packages:
    - package==version
  internal_agents:
    - AgentName
  external_services:
    - name: ServiceName
      required: true|false

performance:
  timeout_seconds: 30
  cache_enabled: true|false

logging:
  level: INFO
  log_queries: true|false

testing:
  test_scenarios:
    - name: scenario_name
      input: {...}
      expected: result

IMPORTANT: 
- Be specific and detailed
- Include all capabilities
- Define clear inputs/outputs
- Specify error handling
- Output ONLY valid YAML, no other text
- Use proper YAML indentation (2 spaces)
"""

    user_prompt = f"""Generate a complete YAML specification for this agent:

AGENT NAME: {agent_design.agent_name}
AGENT TYPE: {agent_design.agent_type}
ROLE: {agent_design.role}
COMPLEXITY: {agent_design.complexity}

RESPONSIBILITIES:
{chr(10).join(['- ' + r for r in agent_design.responsibilities])}

DEPENDENCIES:
{chr(10).join(['- ' + d for d in agent_design.dependencies])}

INTERNAL COMPONENTS: {', '.join(agent_design.internal_components) if agent_design.internal_components else 'None'}
USES LLM: {agent_design.uses_llm}

OTHER AGENTS IN SYSTEM: {', '.join(other_agents)}

REQUIREMENTS CONTEXT:
- Primary Goal: {requirements.primary_goal}
- Data Sources: {', '.join(requirements.data_sources)}
- Calculations: {len(requirements.calculations_needed)} needed
- Modes: {', '.join(requirements.modes_required)}

Generate the complete YAML specification following the structure provided.
{additional_instructions}"""

    try:
        # Call LLM to generate specification
        yaml_spec = llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=4096  # Specs can be long
        )
        
        # Remove markdown code blocks if present
        yaml_spec = yaml_spec.strip()
        if yaml_spec.startswith("```yaml"):
            yaml_spec = yaml_spec[7:]
        if yaml_spec.startswith("```"):
            yaml_spec = yaml_spec[3:]
        if yaml_spec.endswith("```"):
            yaml_spec = yaml_spec[:-3]
        yaml_spec = yaml_spec.strip()
        
        # Validate YAML syntax
        try:
            yaml_dict = yaml.safe_load(yaml_spec)
            if not isinstance(yaml_dict, dict):
                raise ValueError("YAML must be a dictionary at root level")
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML syntax: {e}")
            raise ValueError(f"Generated specification has invalid YAML syntax: {e}") from e
        
        logger.info(f"✓ Specification generated for {agent_design.agent_name}")
        logger.info(f"  YAML size: {len(yaml_spec)} characters")
        logger.info(f"  Top-level keys: {list(yaml_dict.keys())}")
        
        return yaml_spec
        
    except Exception as e:
        logger.error(f"Failed to generate specification: {e}")
        raise RuntimeError(
            f"Specification generation failed: {e}. "
            f"This indicates an issue with LLM response."
        ) from e


def validate_specification_structure(yaml_spec: str) -> bool:
    """
    Validate that specification has required structure.
    
    Args:
        yaml_spec: YAML specification string
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If specification is invalid
    """
    logger.info("Validating specification structure...")
    
    try:
        spec_dict = yaml.safe_load(yaml_spec)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax: {e}") from e
    
    # Check required top-level fields
    required_fields = ["agent_name", "agent_type", "version", "description", "role"]
    for field in required_fields:
        if field not in spec_dict:
            raise ValueError(f"Missing required field: {field}")
    
    # Check capabilities if present
    if "capabilities" in spec_dict:
        if not isinstance(spec_dict["capabilities"], list):
            raise ValueError("capabilities must be a list")
        for cap in spec_dict["capabilities"]:
            if "name" not in cap:
                raise ValueError("Each capability must have a 'name'")
    
    # Check dependencies if present
    if "dependencies" in spec_dict:
        deps = spec_dict["dependencies"]
        if not isinstance(deps, dict):
            raise ValueError("dependencies must be a dictionary")
    
    logger.info("✓ Specification structure valid")
    return True

