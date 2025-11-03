"""
Code Validators: Syntax and Security
Validates generated Python code for syntax correctness and security issues.
NO FALLBACKS - Strict validation only.
"""

import ast
import re
from typing import List, Dict, Any, Set
from pydantic import BaseModel
from loguru import logger


class ValidationIssue(BaseModel):
    """A validation issue found in code"""
    severity: str  # ERROR, WARNING, INFO
    issue_type: str  # syntax, security, quality
    message: str
    line_number: int = 0
    suggestion: str = ""


class ValidationResult(BaseModel):
    """Result of code validation"""
    valid: bool
    issues: List[ValidationIssue] = []
    risk_score: float = 0.0  # 0.0 = safe, 1.0 = dangerous
    summary: str = ""


# Security: Dangerous functions that should never appear in generated code
DANGEROUS_FUNCTIONS = {
    'eval', 'exec', 'compile', '__import__', 'execfile',
    'input',  # Can be dangerous in automated contexts
    'open'  # File I/O should be controlled
}

# Security: Dangerous imports (imports that should be scrutinized)
DANGEROUS_IMPORTS = {
    'subprocess', 'socket', 'urllib',
    'pickle', 'marshal',  # Serialization can be dangerous
    'ctypes', 'cffi'  # Low-level access
}

# Conditionally allowed imports (require specific safe usage patterns)
CONDITIONAL_IMPORTS = {
    'os': ['getenv', 'environ.get', 'path'],  # Only environment variables and path operations
    'sys': ['argv', 'exit'],  # Only basic sys functions
    'requests': []  # Network access - allow but track
}

# Allowed imports for agents
ALLOWED_IMPORTS = {
    # Standard library (safe subset)
    'typing', 'dataclasses', 'enum', 'abc', 'collections',
    'datetime', 'decimal', 'fractions', 'math', 'statistics',
    'json', 're', 'pathlib',
    
    # Required libraries
    'pydantic', 'loguru', 'sqlalchemy', 'psycopg2',
    'langchain', 'langchain_openai', 'langgraph',
    'yaml', 'httpx',
    
    # Conditionally allowed (will check usage)
    'os', 'sys', 'requests'
}


def validate_code_syntax(code: str) -> ValidationResult:
    """
    Validate Python code syntax using AST parsing.
    
    Args:
        code: Python code as string
    
    Returns:
        ValidationResult with syntax validation results
    """
    logger.info("Validating code syntax...")
    issues = []
    
    try:
        # Parse code into AST
        tree = ast.parse(code)
        
        # Check if code is empty
        if not tree.body:
            issues.append(ValidationIssue(
                severity="WARNING",
                issue_type="syntax",
                message="Code is empty or contains only comments",
                suggestion="Ensure code contains actual implementation"
            ))
        
        # Basic structure checks
        has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        
        if not has_class and not has_function:
            issues.append(ValidationIssue(
                severity="WARNING",
                issue_type="syntax",
                message="Code contains no classes or functions",
                suggestion="Agent code should contain at least a class definition"
            ))
        
        logger.info("✓ Syntax validation passed")
        
        return ValidationResult(
            valid=len([i for i in issues if i.severity == "ERROR"]) == 0,
            issues=issues,
            summary=f"Syntax valid, {len(issues)} warnings"
        )
        
    except SyntaxError as e:
        logger.error(f"Syntax error: {e}")
        issues.append(ValidationIssue(
            severity="ERROR",
            issue_type="syntax",
            message=f"Syntax error: {e.msg}",
            line_number=e.lineno or 0,
            suggestion="Fix syntax error before proceeding"
        ))
        
        return ValidationResult(
            valid=False,
            issues=issues,
            summary=f"Syntax error at line {e.lineno}: {e.msg}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during syntax validation: {e}")
        issues.append(ValidationIssue(
            severity="ERROR",
            issue_type="syntax",
            message=f"Failed to parse code: {str(e)}",
            suggestion="Check code structure"
        ))
        
        return ValidationResult(
            valid=False,
            issues=issues,
            summary=f"Validation error: {str(e)}"
        )


def validate_code_security(code: str) -> ValidationResult:
    """
    Validate code for security issues.
    
    Args:
        code: Python code as string
    
    Returns:
        ValidationResult with security validation results
    """
    logger.info("Validating code security...")
    issues = []
    risk_score = 0.0
    
    try:
        tree = ast.parse(code)
        
        # Check 1: Dangerous function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name in DANGEROUS_FUNCTIONS:
                    issues.append(ValidationIssue(
                        severity="ERROR",
                        issue_type="security",
                        message=f"Dangerous function call: {func_name}()",
                        line_number=getattr(node, 'lineno', 0),
                        suggestion=f"Remove {func_name}() - not allowed in generated agents"
                    ))
                    risk_score += 0.3
        
        # Check 2: Import validation
        imported_modules = set()
        conditional_modules = {}  # Track conditionally allowed modules
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    imported_modules.add(module)
                    
                    if module in DANGEROUS_IMPORTS:
                        issues.append(ValidationIssue(
                            severity="ERROR",
                            issue_type="security",
                            message=f"Dangerous import: {module}",
                            line_number=getattr(node, 'lineno', 0),
                            suggestion=f"Remove 'import {module}' - not allowed"
                        ))
                        risk_score += 0.4
                    elif module in CONDITIONAL_IMPORTS:
                        # Track for usage validation
                        conditional_modules[module] = CONDITIONAL_IMPORTS[module]
                    elif module not in ALLOWED_IMPORTS and not module.startswith('meta_agent'):
                        issues.append(ValidationIssue(
                            severity="WARNING",
                            issue_type="security",
                            message=f"Uncommon import: {module}",
                            line_number=getattr(node, 'lineno', 0),
                            suggestion=f"Verify {module} is necessary and safe"
                        ))
                        risk_score += 0.1
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    imported_modules.add(module)
                    
                    if module in DANGEROUS_IMPORTS:
                        issues.append(ValidationIssue(
                            severity="ERROR",
                            issue_type="security",
                            message=f"Dangerous import: from {module}",
                            line_number=getattr(node, 'lineno', 0),
                            suggestion=f"Remove 'from {module} import ...' - not allowed"
                        ))
                        risk_score += 0.4
                    elif module in CONDITIONAL_IMPORTS:
                        # Track for usage validation
                        conditional_modules[module] = CONDITIONAL_IMPORTS[module]
        
        # Check 2b: Validate usage of conditional imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for os.getenv(), os.environ.get(), etc.
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        module_name = node.func.value.id
                        func_name = node.func.attr
                        
                        if module_name in conditional_modules:
                            allowed_funcs = conditional_modules[module_name]
                            # If specific functions are defined, check if this one is allowed
                            if allowed_funcs and func_name not in allowed_funcs:
                                issues.append(ValidationIssue(
                                    severity="ERROR",
                                    issue_type="security",
                                    message=f"Unsafe usage of {module_name}.{func_name}()",
                                    line_number=getattr(node, 'lineno', 0),
                                    suggestion=f"Only {', '.join(allowed_funcs)} are allowed for {module_name}"
                                ))
                                risk_score += 0.3
                    
                    # Check for os.environ.get()
                    elif isinstance(node.func.value, ast.Attribute):
                        if isinstance(node.func.value.value, ast.Name):
                            module_name = node.func.value.value.id
                            attr_name = node.func.value.attr
                            func_name = node.func.attr
                            
                            if module_name == 'os' and attr_name == 'environ' and func_name == 'get':
                                # os.environ.get() is safe - do nothing
                                pass
        
        # Check 3: Hardcoded credentials/secrets
        # Patterns to detect actual hardcoded values (not env vars or empty strings)
        hardcoded_patterns = [
            (r'password\s*=\s*["\'][\w]{3,}["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\'\n]{8,}["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\'\n]{8,}["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\'\n]{8,}["\']', "Hardcoded token"),
        ]
        
        # Patterns that are OK (using env vars, empty strings, etc.)
        safe_patterns = [
            r'os\.getenv\(',
            r'os\.environ',
            r'getenv\(',
            r'=\s*["\']["\']',  # Empty string
            r'=\s*""',
            r"=\s*''",
        ]
        
        for pattern, message in hardcoded_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                matched_line = code[code.rfind('\n', 0, match.start())+1:code.find('\n', match.end())]
                
                # Check if this line uses safe patterns
                is_safe = any(re.search(safe_pattern, matched_line) for safe_pattern in safe_patterns)
                
                if not is_safe:
                    # Get line number
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        severity="ERROR",
                        issue_type="security",
                        message=message,
                        line_number=line_num,
                        suggestion="Use environment variables or config instead"
                    ))
                    risk_score += 0.3
        
        # Check 4: Complexity (too complex might hide issues)
        function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        
        if function_count > 50:
            issues.append(ValidationIssue(
                severity="WARNING",
                issue_type="quality",
                message=f"Very high function count: {function_count}",
                suggestion="Consider breaking into multiple files"
            ))
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine if code is safe
        has_errors = any(i.severity == "ERROR" for i in issues)
        is_safe = not has_errors and risk_score < 0.5
        
        logger.info(f"✓ Security validation complete")
        logger.info(f"  Risk score: {risk_score:.2f}")
        logger.info(f"  Issues: {len(issues)} ({len([i for i in issues if i.severity == 'ERROR'])} errors)")
        
        return ValidationResult(
            valid=is_safe,
            issues=issues,
            risk_score=risk_score,
            summary=f"Risk score: {risk_score:.2f}, {len(issues)} issues found"
        )
        
    except Exception as e:
        logger.error(f"Security validation error: {e}")
        return ValidationResult(
            valid=False,
            issues=[ValidationIssue(
                severity="ERROR",
                issue_type="security",
                message=f"Security validation failed: {str(e)}",
                suggestion="Fix syntax errors first"
            )],
            risk_score=1.0,
            summary=f"Validation failed: {str(e)}"
        )


def validate_code(code: str) -> ValidationResult:
    """
    Comprehensive code validation (syntax + security).
    
    Args:
        code: Python code as string
    
    Returns:
        Combined validation result
    """
    logger.info("Running comprehensive code validation...")
    
    # Step 1: Syntax validation (must pass first)
    syntax_result = validate_code_syntax(code)
    if not syntax_result.valid:
        logger.error("Syntax validation failed, skipping security validation")
        return syntax_result
    
    # Step 2: Security validation
    security_result = validate_code_security(code)
    
    # Combine results
    all_issues = syntax_result.issues + security_result.issues
    overall_valid = syntax_result.valid and security_result.valid
    
    combined_result = ValidationResult(
        valid=overall_valid,
        issues=all_issues,
        risk_score=security_result.risk_score,
        summary=f"{'✓ VALID' if overall_valid else '✗ INVALID'} - {len(all_issues)} issues, risk: {security_result.risk_score:.2f}"
    )
    
    logger.info(f"✓ Comprehensive validation complete: {combined_result.summary}")
    
    return combined_result

