"""
Tool #4: Generate Agent Code
Generates Python code for an agent from YAML specification using LLM.
NO FALLBACKS - Strictly requires LLM.
Includes auto-retry mechanism for syntax errors.
"""

from typing import Dict, Any, Optional
from loguru import logger
import yaml
import ast

from meta_agent.utils.llm_client import LLMClient


def _check_syntax(code: str) -> Optional[str]:
    """
    Check code syntax and return error message if invalid.
    
    Args:
        code: Python code to check
    
    Returns:
        Error message if syntax is invalid, None otherwise
    """
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"Parse error: {str(e)}"


def generate_agent_code_with_retry(
    yaml_specification: str,
    llm_client: LLMClient,
    style_guide: str = "pep8",
    max_retries: int = 5
) -> Dict[str, Any]:
    """
    Generate Python code with automatic retry on syntax errors.
    
    Args:
        yaml_specification: YAML spec for the agent
        llm_client: LLM client instance
        style_guide: Code style to follow (default: pep8)
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Dictionary with:
            - code: Generated Python code as string
            - metadata: Information about generated code
            - retry_count: Number of retries needed
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If specification is invalid or code generation fails after retries
    """
    logger.info("Generating code with auto-retry...")
    
    additional_instructions = ""
    
    for attempt in range(max_retries):
        try:
            # Try to generate code
            result = generate_agent_code(yaml_specification, llm_client, style_guide, additional_instructions)
            code = result["code"]
            
            # Save for debugging if syntax error occurs
            debug_path = f"/tmp/generated_code_attempt_{attempt + 1}.py"
            with open(debug_path, 'w') as f:
                f.write(code)
            
            # Check syntax
            syntax_error = _check_syntax(code)
            
            if syntax_error is None:
                # Success!
                result["retry_count"] = attempt
                if attempt > 0:
                    logger.info(f"✓ Code generated successfully after {attempt} retries")
                return result
            else:
                # Syntax error found
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Syntax error detected")
                logger.warning(f"  Error: {syntax_error}")
                logger.warning(f"  Debug: Code saved to {debug_path}")
                
                if attempt < max_retries - 1:
                    # Try again with feedback
                    logger.info(f"  Retrying with error feedback...")
                    
                    # Get code snippet around error line for context
                    code_lines = code.split('\n')
                    error_line_num = int(syntax_error.split('line ')[1].split(':')[0]) if 'line ' in syntax_error else 0
                    context_start = max(0, error_line_num - 3)
                    context_end = min(len(code_lines), error_line_num + 2)
                    context = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(code_lines[context_start:context_end], start=context_start))
                    
                    # Build specific feedback for next attempt
                    additional_instructions = f"""

⚠️ PREVIOUS ATTEMPT FAILED WITH SYNTAX ERROR:
{syntax_error}

Code context around the error:
{context}

CRITICAL FIX REQUIRED:
1. The code MUST be syntactically valid Python
2. ALL brackets, parentheses, and braces MUST be properly closed
3. ALL function and class definitions MUST have proper bodies
4. ALL strings MUST have matching quotes
5. Check indentation carefully - Python requires consistent indentation
6. DO NOT leave any incomplete statements
7. DO NOT truncate the code - generate the COMPLETE implementation

Generate COMPLETE, VALID Python code. Every function must have a body. Every class must be complete.
"""
                else:
                    # Final attempt failed
                    logger.error(f"Failed to generate valid code after {max_retries} attempts")
                    logger.error(f"  Last generated code saved to: {debug_path}")
                    raise ValueError(
                        f"Code generation failed after {max_retries} attempts. "
                        f"Last error: {syntax_error}. "
                        f"Debug code at: {debug_path}"
                    )
        
        except ValueError as e:
            # Re-raise ValueError (includes final retry failure)
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries}: Generation error: {e}")
            if attempt >= max_retries - 1:
                raise RuntimeError(f"Code generation failed after {max_retries} attempts: {e}") from e
    
    raise RuntimeError("Code generation failed: Maximum retries reached")


def generate_agent_code(
    yaml_specification: str,
    llm_client: LLMClient,
    style_guide: str = "pep8",
    additional_instructions: str = ""
) -> Dict[str, Any]:
    """
    Generate Python code for an agent from YAML specification.
    
    Args:
        yaml_specification: YAML spec for the agent
        llm_client: LLM client instance
        style_guide: Code style to follow (default: pep8)
        additional_instructions: Additional instructions for retry attempts
    
    Returns:
        Dictionary with:
            - code: Generated Python code as string
            - metadata: Information about generated code (lines, complexity, etc.)
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If specification is invalid or code generation fails
    """
    # Parse YAML to get agent details
    try:
        spec = yaml.safe_load(yaml_specification)
        agent_name = spec.get("agent_name", "UnknownAgent")
        agent_type = spec.get("agent_type", "unknown")
        complexity = spec.get("complexity", "MEDIUM")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML specification: {e}") from e
    
    logger.info(f"Generating code for {agent_name}...")
    logger.info(f"  Type: {agent_type}")
    logger.info(f"  Complexity: {complexity}")
    
    system_prompt = """You are an expert Python developer specializing in agent systems.
Your task is to generate production-ready Python code from a YAML specification.

REQUIREMENTS:
1. Generate complete, working Python code
2. Follow PEP 8 style guide strictly
3. Use type hints throughout (from typing import ...)
4. Include comprehensive docstrings (Google style)
5. Use Pydantic for data validation
6. Use loguru for logging
7. Include error handling (try/except with specific exceptions)
8. NO hardcoded values - all config from environment or parameters
9. Make it compatible with the agent system (proper imports, structure)
10. Include __init__ method with proper initialization
11. All methods should have clear purpose and clean implementation
12. ENSURE ALL CODE IS SYNTACTICALLY VALID - no incomplete functions or classes
13. EVERY function and class MUST have a complete body
14. ALL brackets, parentheses, and quotes MUST be properly closed

SECURITY - CRITICAL RULES:
- NEVER hardcode passwords, API keys, tokens, or secrets
- ALWAYS use os.getenv() for sensitive configuration (e.g., os.getenv('DATABASE_URL'))
- Database credentials must come from environment variables
- Use empty strings "" for default password values, NOT example values like "admin" or "password123"
- Example: password = os.getenv('DB_PASSWORD', '') ✓
- Example: password = "admin" ✗ WRONG

CODE STRUCTURE:
- Imports at top (standard library, then third-party, then local)
- Pydantic models for data structures (if needed)
- Main agent class
- All methods with docstrings
- Proper error handling in each method
- Logger statements for key operations

CRITICAL - CODE COMPLETENESS:
- The generated code MUST parse without syntax errors
- DO NOT truncate output - generate the ENTIRE implementation
- Every function definition needs a body (cannot end with just a colon)
- Every class definition needs a body
- All strings must be properly quoted
- All parentheses, brackets, and braces must be balanced

IMPORTANT:
- Output ONLY Python code, no explanations
- Code must be syntactically correct and complete
- No placeholder or TODO comments
- Complete, working implementation based on spec
- All sensitive values from environment variables
"""

    user_prompt = f"""Generate complete Python code for this agent:

YAML SPECIFICATION:
```yaml
{yaml_specification}
```

Generate production-ready Python code following all requirements.
The code should be complete and directly usable.{additional_instructions}"""

    try:
        # Call LLM to generate code
        code = llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=4096
        )
        
        # Remove markdown code blocks if present
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()
        
        # Calculate metadata
        lines = len(code.split('\n'))
        has_docstrings = '"""' in code or "'''" in code
        has_type_hints = '->' in code or ': ' in code
        has_error_handling = 'try:' in code and 'except' in code
        
        metadata = {
            "lines": lines,
            "complexity": complexity,
            "has_docstrings": has_docstrings,
            "has_type_hints": has_type_hints,
            "has_error_handling": has_error_handling,
            "agent_name": agent_name,
            "agent_type": agent_type
        }
        
        logger.info(f"✓ Code generated for {agent_name}")
        logger.info(f"  Lines: {lines}")
        logger.info(f"  Docstrings: {'✓' if has_docstrings else '✗'}")
        logger.info(f"  Type hints: {'✓' if has_type_hints else '✗'}")
        logger.info(f"  Error handling: {'✓' if has_error_handling else '✗'}")
        
        return {
            "code": code,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Failed to generate code: {e}")
        raise RuntimeError(
            f"Code generation failed: {e}. "
            f"This indicates an issue with LLM response."
        ) from e


def generate_multi_file_code(
    yaml_specification: str,
    llm_client: LLMClient
) -> Dict[str, str]:
    """
    Generate code for complex agents that need multiple files.
    
    Args:
        yaml_specification: YAML spec for the agent
        llm_client: LLM client instance
    
    Returns:
        Dictionary mapping filename to code content
    
    Raises:
        RuntimeError: If LLM is not available
        ValueError: If specification is invalid
    """
    # Parse YAML to check for internal components
    try:
        spec = yaml.safe_load(yaml_specification)
        agent_name = spec.get("agent_name", "UnknownAgent")
        internal_components = spec.get("internal_components", [])
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML specification: {e}") from e
    
    # If no internal components, generate single file
    if not internal_components:
        logger.info(f"{agent_name} has no internal components, generating single file")
        result = generate_agent_code(yaml_specification, llm_client)
        return {f"{agent_name.lower()}.py": result["code"]}
    
    # Generate main agent file
    logger.info(f"Generating multi-file code for {agent_name} with {len(internal_components)} components")
    
    main_result = generate_agent_code(yaml_specification, llm_client)
    files = {
        f"{agent_name.lower()}.py": main_result["code"]
    }
    
    # Generate each component as separate file
    for component in internal_components:
        logger.info(f"  Generating component: {component}")
        
        # Create mini-spec for component
        component_spec = f"""
agent_name: {component}
agent_type: component
description: Component of {agent_name}
parent_agent: {agent_name}
role: internal_component
"""
        
        try:
            component_result = generate_agent_code(component_spec, llm_client)
            component_filename = f"{agent_name.lower()}_{component.lower()}.py"
            files[component_filename] = component_result["code"]
            logger.info(f"  ✓ Generated {component_filename}")
        except Exception as e:
            logger.warning(f"  Failed to generate {component}: {e}, will include in main file")
    
    return files

