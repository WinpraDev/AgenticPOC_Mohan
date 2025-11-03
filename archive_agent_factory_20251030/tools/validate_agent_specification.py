"""
Tool #4: Validate Agent Specification

This tool validates agent YAML specifications for completeness, consistency,
and adherence to the Meta-Agent specification schema.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from loguru import logger
import yaml
from pathlib import Path


class ValidationIssue(BaseModel):
    """Model for a validation issue"""
    severity: str = Field(..., description="error, warning, or info")
    field: str = Field(..., description="Field or section with the issue")
    message: str = Field(..., description="Description of the issue")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class SpecValidationResult(BaseModel):
    """Model for specification validation result"""
    is_valid: bool = Field(..., description="Whether the spec is valid")
    issues: List[ValidationIssue] = Field(default_factory=list, description="List of validation issues")
    warnings: int = Field(0, description="Number of warnings")
    errors: int = Field(0, description="Number of errors")
    completeness_score: float = Field(0.0, description="Completeness score (0-100)")
    
    @validator('completeness_score')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Completeness score must be between 0 and 100")
        return v


class ValidateAgentSpecificationTool:
    """
    Tool for validating agent specifications
    
    Validates:
    - Required fields presence
    - Data type correctness
    - Workflow logic consistency
    - Capability definitions
    - Dependency declarations
    - Test scenario completeness
    """
    
    REQUIRED_FIELDS = {
        "agent_name": str,
        "agent_type": str,
        "version": str,
        "description": str,
        "role": str,
        "capabilities": (list, dict),
        "workflow": dict,
        "dependencies": dict,
    }
    
    OPTIONAL_FIELDS = {
        "data_sources": (list, dict),
        "tools": list,
        "performance": dict,
        "logging": dict,
        "testing": dict,
    }
    
    VALID_AGENT_TYPES = [
        "data_retrieval",
        "calculation",
        "validation",
        "orchestration",
        "monitoring",
        "transformation"
    ]
    
    VALID_ROLES = [
        "primary_agent",
        "secondary_agent",
        "support_agent",
        "orchestrator"
    ]
    
    def __init__(self):
        """Initialize the validation tool"""
        logger.info("Initializing ValidateAgentSpecificationTool")
    
    def validate_specification(
        self,
        spec_content: str,
        strict_mode: bool = True
    ) -> SpecValidationResult:
        """
        Validate an agent specification
        
        Args:
            spec_content: YAML specification content as string
            strict_mode: Whether to enforce strict validation rules
            
        Returns:
            SpecValidationResult with validation details
        """
        logger.info("Validating agent specification")
        logger.info(f"  Strict mode: {strict_mode}")
        logger.info(f"  Spec size: {len(spec_content)} characters")
        
        issues: List[ValidationIssue] = []
        
        # Parse YAML
        try:
            spec = yaml.safe_load(spec_content)
            if not isinstance(spec, dict):
                issues.append(ValidationIssue(
                    severity="error",
                    field="root",
                    message="Specification must be a YAML dictionary",
                    suggestion="Ensure the YAML starts with key-value pairs"
                ))
                return self._create_result(issues, False)
        except yaml.YAMLError as e:
            issues.append(ValidationIssue(
                severity="error",
                field="yaml_syntax",
                message=f"YAML parsing error: {str(e)}",
                suggestion="Check YAML syntax and indentation"
            ))
            return self._create_result(issues, False)
        
        # Validate required fields
        issues.extend(self._validate_required_fields(spec))
        
        # Validate field types
        issues.extend(self._validate_field_types(spec))
        
        # Validate agent_type
        issues.extend(self._validate_agent_type(spec))
        
        # Validate role
        issues.extend(self._validate_role(spec))
        
        # Validate version format
        issues.extend(self._validate_version(spec))
        
        # Validate capabilities
        issues.extend(self._validate_capabilities(spec))
        
        # Validate workflow
        issues.extend(self._validate_workflow(spec))
        
        # Validate dependencies
        issues.extend(self._validate_dependencies(spec))
        
        # Validate testing scenarios (if present)
        if "testing" in spec:
            issues.extend(self._validate_testing(spec))
        
        # Check for optional but recommended fields
        if not strict_mode:
            issues.extend(self._check_optional_fields(spec))
        
        # Determine if valid (no errors)
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        is_valid = len(errors) == 0
        
        # Calculate completeness score
        completeness = self._calculate_completeness(spec)
        
        logger.info(f"✓ Validation complete")
        logger.info(f"  Valid: {is_valid}")
        logger.info(f"  Errors: {len(errors)}")
        logger.info(f"  Warnings: {len(warnings)}")
        logger.info(f"  Completeness: {completeness:.1f}%")
        
        return SpecValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=len(warnings),
            errors=len(errors),
            completeness_score=completeness
        )
    
    def _validate_required_fields(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate that all required fields are present"""
        issues = []
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in spec:
                issues.append(ValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' to the specification"
                ))
        return issues
    
    def _validate_field_types(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate field types"""
        issues = []
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field in spec:
                value = spec[field]
                if isinstance(expected_type, tuple):
                    if not isinstance(value, expected_type):
                        issues.append(ValidationIssue(
                            severity="error",
                            field=field,
                            message=f"Field '{field}' must be one of types {expected_type}",
                            suggestion=f"Change '{field}' to a valid type"
                        ))
                else:
                    if not isinstance(value, expected_type):
                        issues.append(ValidationIssue(
                            severity="error",
                            field=field,
                            message=f"Field '{field}' must be of type {expected_type.__name__}",
                            suggestion=f"Change '{field}' to {expected_type.__name__}"
                        ))
        return issues
    
    def _validate_agent_type(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate agent_type value"""
        issues = []
        if "agent_type" in spec:
            agent_type = spec["agent_type"]
            if agent_type not in self.VALID_AGENT_TYPES:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="agent_type",
                    message=f"Agent type '{agent_type}' is not in standard types",
                    suggestion=f"Consider using one of: {', '.join(self.VALID_AGENT_TYPES)}"
                ))
        return issues
    
    def _validate_role(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate role value"""
        issues = []
        if "role" in spec:
            role = spec["role"]
            if role not in self.VALID_ROLES:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="role",
                    message=f"Role '{role}' is not in standard roles",
                    suggestion=f"Consider using one of: {', '.join(self.VALID_ROLES)}"
                ))
        return issues
    
    def _validate_version(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate version format (semantic versioning)"""
        issues = []
        if "version" in spec:
            version = spec["version"]
            parts = version.split(".")
            if len(parts) != 3:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="version",
                    message="Version should follow semantic versioning (MAJOR.MINOR.PATCH)",
                    suggestion="Use format like '1.0.0'"
                ))
            else:
                for part in parts:
                    if not part.isdigit():
                        issues.append(ValidationIssue(
                            severity="warning",
                            field="version",
                            message="Version parts should be numeric",
                            suggestion="Use format like '1.0.0'"
                        ))
                        break
        return issues
    
    def _validate_capabilities(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate capabilities section"""
        issues = []
        if "capabilities" in spec:
            capabilities = spec["capabilities"]
            
            if isinstance(capabilities, list):
                if len(capabilities) == 0:
                    issues.append(ValidationIssue(
                        severity="warning",
                        field="capabilities",
                        message="Capabilities list is empty",
                        suggestion="Define at least one capability"
                    ))
                
                for i, cap in enumerate(capabilities):
                    if isinstance(cap, dict):
                        if "name" not in cap:
                            issues.append(ValidationIssue(
                                severity="error",
                                field=f"capabilities[{i}]",
                                message="Capability missing 'name' field",
                                suggestion="Add 'name' field to capability"
                            ))
                    elif not isinstance(cap, str):
                        issues.append(ValidationIssue(
                            severity="error",
                            field=f"capabilities[{i}]",
                            message="Capability must be a string or dictionary",
                            suggestion="Define capability as string or object with 'name'"
                        ))
        
        return issues
    
    def _validate_workflow(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate workflow section"""
        issues = []
        if "workflow" in spec:
            workflow = spec["workflow"]
            
            if not isinstance(workflow, dict):
                issues.append(ValidationIssue(
                    severity="error",
                    field="workflow",
                    message="Workflow must be a dictionary",
                    suggestion="Define workflow with 'steps' key"
                ))
                return issues
            
            if "steps" in workflow:
                steps = workflow["steps"]
                if not isinstance(steps, dict):
                    issues.append(ValidationIssue(
                        severity="error",
                        field="workflow.steps",
                        message="Workflow steps must be a dictionary",
                        suggestion="Define steps as key-value pairs"
                    ))
                elif len(steps) == 0:
                    issues.append(ValidationIssue(
                        severity="warning",
                        field="workflow.steps",
                        message="Workflow has no steps defined",
                        suggestion="Define at least one workflow step"
                    ))
            else:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="workflow",
                    message="Workflow missing 'steps' section",
                    suggestion="Add 'steps' to define workflow logic"
                ))
        
        return issues
    
    def _validate_dependencies(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate dependencies section"""
        issues = []
        if "dependencies" in spec:
            deps = spec["dependencies"]
            
            if not isinstance(deps, dict):
                issues.append(ValidationIssue(
                    severity="error",
                    field="dependencies",
                    message="Dependencies must be a dictionary",
                    suggestion="Define dependencies with keys like 'python_packages', 'internal_agents', etc."
                ))
                return issues
            
            # Check for empty dependencies
            if not any(deps.values()):
                issues.append(ValidationIssue(
                    severity="info",
                    field="dependencies",
                    message="No dependencies defined",
                    suggestion=None
                ))
        
        return issues
    
    def _validate_testing(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate testing section"""
        issues = []
        testing = spec.get("testing", {})
        
        if not isinstance(testing, dict):
            issues.append(ValidationIssue(
                severity="error",
                field="testing",
                message="Testing section must be a dictionary",
                suggestion="Define testing with 'test_scenarios'"
            ))
            return issues
        
        if "test_scenarios" in testing:
            scenarios = testing["test_scenarios"]
            if not isinstance(scenarios, list):
                issues.append(ValidationIssue(
                    severity="error",
                    field="testing.test_scenarios",
                    message="Test scenarios must be a list",
                    suggestion="Define test scenarios as a list of test cases"
                ))
            elif len(scenarios) == 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="testing.test_scenarios",
                    message="No test scenarios defined",
                    suggestion="Add at least one test scenario"
                ))
        else:
            issues.append(ValidationIssue(
                severity="info",
                field="testing",
                message="No test scenarios defined",
                suggestion="Consider adding 'test_scenarios' for automated testing"
            ))
        
        return issues
    
    def _check_optional_fields(self, spec: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for recommended optional fields"""
        issues = []
        
        if "performance" not in spec:
            issues.append(ValidationIssue(
                severity="info",
                field="performance",
                message="Performance settings not defined",
                suggestion="Consider adding timeout, caching, etc."
            ))
        
        if "logging" not in spec:
            issues.append(ValidationIssue(
                severity="info",
                field="logging",
                message="Logging configuration not defined",
                suggestion="Consider adding log level and options"
            ))
        
        return issues
    
    def _calculate_completeness(self, spec: Dict[str, Any]) -> float:
        """Calculate specification completeness score"""
        total_fields = len(self.REQUIRED_FIELDS) + len(self.OPTIONAL_FIELDS)
        present_fields = 0
        
        for field in self.REQUIRED_FIELDS.keys():
            if field in spec and spec[field]:
                present_fields += 1
        
        for field in self.OPTIONAL_FIELDS.keys():
            if field in spec and spec[field]:
                present_fields += 1
        
        return (present_fields / total_fields) * 100
    
    def _create_result(
        self,
        issues: List[ValidationIssue],
        is_valid: bool
    ) -> SpecValidationResult:
        """Create validation result"""
        errors = len([i for i in issues if i.severity == "error"])
        warnings = len([i for i in issues if i.severity == "warning"])
        
        return SpecValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            errors=errors,
            completeness_score=0.0 if not is_valid else 50.0
        )


def validate_specification_file(spec_file: Path) -> SpecValidationResult:
    """
    Convenience function to validate a specification file
    
    Args:
        spec_file: Path to YAML specification file
        
    Returns:
        SpecValidationResult
    """
    logger.info(f"Validating specification file: {spec_file}")
    
    if not spec_file.exists():
        return SpecValidationResult(
            is_valid=False,
            issues=[ValidationIssue(
                severity="error",
                field="file",
                message=f"Specification file not found: {spec_file}",
                suggestion="Check file path"
            )],
            warnings=0,
            errors=1,
            completeness_score=0.0
        )
    
    spec_content = spec_file.read_text()
    tool = ValidateAgentSpecificationTool()
    return tool.validate_specification(spec_content)

