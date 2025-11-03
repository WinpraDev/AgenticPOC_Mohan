"""
Script Validator
Validates generated scripts for syntax, security, and resource compliance
"""

import ast
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel


class ValidationIssue(BaseModel):
    """Single validation issue"""
    severity: str  # "error", "warning", "info"
    category: str  # "syntax", "security", "resource", "style"
    message: str
    line_number: Optional[int] = None


class ValidationResult(BaseModel):
    """Result of script validation"""
    is_valid: bool
    issues: List[ValidationIssue]
    syntax_valid: bool
    security_score: float  # 0.0 to 1.0
    estimated_memory_mb: int
    estimated_cpu_cores: float
    
    def __str__(self) -> str:
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        return f"{status} - {len(self.issues)} issues, security: {self.security_score:.2f}"


def validate_script(script_code: str, strict_mode: bool = True) -> ValidationResult:
    """
    Validate generated script
    
    Args:
        script_code: Python script to validate
        strict_mode: Whether to enforce strict validation
        
    Returns:
        ValidationResult with all issues
        
    Raises:
        ValueError: If script is completely invalid
    """
    logger.debug("Validating generated script...")
    
    issues: List[ValidationIssue] = []
    
    # 1. Syntax validation
    syntax_valid = _validate_syntax(script_code, issues)
    
    # 2. Security validation
    security_score = _validate_security(script_code, issues, strict_mode)
    
    # 3. Resource estimation
    memory_mb, cpu_cores = _estimate_resources(script_code)
    
    # 4. Best practices
    _validate_best_practices(script_code, issues)
    
    # Determine if valid
    error_count = sum(1 for issue in issues if issue.severity == "error")
    is_valid = syntax_valid and error_count == 0 and security_score >= 0.8
    
    result = ValidationResult(
        is_valid=is_valid,
        issues=issues,
        syntax_valid=syntax_valid,
        security_score=security_score,
        estimated_memory_mb=memory_mb,
        estimated_cpu_cores=cpu_cores
    )
    
    logger.info(f"✓ Validation complete: {result}")
    logger.info(f"  Syntax: {'✓' if syntax_valid else '✗'}")
    logger.info(f"  Security score: {security_score:.2f}")
    logger.info(f"  Issues: {len(issues)} ({error_count} errors)")
    
    return result


def _validate_syntax(code: str, issues: List[ValidationIssue]) -> bool:
    """Validate Python syntax"""
    try:
        ast.parse(code)
        logger.debug("  ✓ Syntax validation passed")
        return True
    except SyntaxError as e:
        issues.append(ValidationIssue(
            severity="error",
            category="syntax",
            message=f"Syntax error: {e.msg}",
            line_number=e.lineno
        ))
        logger.error(f"  ✗ Syntax error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        issues.append(ValidationIssue(
            severity="error",
            category="syntax",
            message=f"Parse error: {str(e)}"
        ))
        logger.error(f"  ✗ Parse error: {e}")
        return False


def _validate_security(code: str, issues: List[ValidationIssue], strict: bool) -> float:
    """Validate security practices"""
    score = 1.0
    
    # Check for hardcoded credentials
    credential_patterns = [
        (r'password\s*=\s*["\'][^"\']{1,}["\']', 'Potential hardcoded password'),
        (r'api[_-]?key\s*=\s*["\'][^"\']{1,}["\']', 'Potential hardcoded API key'),
        (r'secret\s*=\s*["\'][^"\']{1,}["\']', 'Potential hardcoded secret'),
        (r'token\s*=\s*["\'][^"\']{1,}["\']', 'Potential hardcoded token'),
    ]
    
    for pattern, message in credential_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            # Check if it's using os.getenv()
            context = code[max(0, match.start() - 50):match.end() + 50]
            if 'os.getenv' in context or 'os.environ' in context:
                continue  # Safe usage
            
            # Check if it's an empty string
            if match.group().endswith('""') or match.group().endswith("''"):
                continue  # Empty default is ok
            
            issues.append(ValidationIssue(
                severity="error" if strict else "warning",
                category="security",
                message=message
            ))
            score -= 0.2
            logger.warning(f"  ⚠️  {message}")
    
    # Check for os.getenv() usage (good practice)
    if 'os.getenv' in code or 'os.environ.get' in code:
        logger.debug("  ✓ Using environment variables")
    else:
        issues.append(ValidationIssue(
            severity="warning",
            category="security",
            message="No environment variable usage detected"
        ))
        score -= 0.1
    
    # Check for dangerous operations
    dangerous_patterns = [
        (r'eval\s*\(', 'Use of eval() is dangerous'),
        (r'exec\s*\(', 'Use of exec() is dangerous'),
        (r'__import__\s*\(', 'Dynamic imports can be dangerous'),
    ]
    
    for pattern, message in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(ValidationIssue(
                severity="warning",
                category="security",
                message=message
            ))
            score -= 0.15
            logger.warning(f"  ⚠️  {message}")
    
    return max(0.0, score)


def _estimate_resources(code: str) -> tuple[int, float]:
    """Estimate resource requirements"""
    
    # Simple heuristic based on code characteristics
    lines = len(code.split('\n'))
    
    # Base memory
    memory_mb = 128
    
    # Add for data processing
    if 'pandas' in code:
        memory_mb += 256
    if 'numpy' in code:
        memory_mb += 128
    if 'torch' in code or 'tensorflow' in code:
        memory_mb += 1024
    
    # Add for web server
    if 'flask' in code.lower() or 'fastapi' in code.lower():
        memory_mb += 128
    
    # CPU estimation
    cpu_cores = 0.5
    if 'multiprocessing' in code or 'concurrent' in code:
        cpu_cores = 1.0
    
    return memory_mb, cpu_cores


def _validate_best_practices(code: str, issues: List[ValidationIssue]) -> None:
    """Validate coding best practices"""
    
    # Check for logging
    if 'logger' not in code and 'logging' not in code:
        issues.append(ValidationIssue(
            severity="warning",
            category="style",
            message="No logging detected - consider adding logging"
        ))
    
    # Check for error handling
    if 'try:' not in code:
        issues.append(ValidationIssue(
            severity="info",
            category="style",
            message="No error handling detected - consider adding try/except blocks"
        ))
    
    # Check for type hints
    if '->' not in code:
        issues.append(ValidationIssue(
            severity="info",
            category="style",
            message="No type hints detected - consider adding type annotations"
        ))
    
    # Check for docstrings
    if '"""' not in code and "'''" not in code:
        issues.append(ValidationIssue(
            severity="info",
            category="style",
            message="No docstrings detected - consider adding documentation"
        ))

