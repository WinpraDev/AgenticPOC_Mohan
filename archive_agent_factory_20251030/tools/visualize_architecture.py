"""
Tool #15: Visualize Architecture

This tool generates visual diagrams and documentation for agent architectures
including flowcharts, component diagrams, and data flow visualizations.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path


class VisualizationResult(BaseModel):
    """Model for visualization result"""
    architecture_diagram: str = Field(..., description="Architecture diagram (Mermaid)")
    component_diagram: str = Field(..., description="Component diagram (Mermaid)")
    data_flow_diagram: str = Field(..., description="Data flow diagram (Mermaid)")
    workflow_diagram: Optional[str] = Field(None, description="Workflow diagram")
    files_generated: List[str] = Field(default_factory=list, description="Generated files")


class VisualizeArchitectureTool:
    """
    Tool for visualizing agent architectures
    
    Generates:
    - Architecture overview diagrams
    - Component interaction diagrams
    - Data flow visualizations
    - Workflow flowcharts
    - Sequence diagrams
    
    Uses Mermaid diagram syntax for broad compatibility
    """
    
    def __init__(self):
        """Initialize the visualization tool"""
        logger.info("Initializing VisualizeArchitectureTool")
    
    def visualize_agent(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any],
        architecture_design: Optional[Dict[str, Any]],
        output_dir: Path
    ) -> VisualizationResult:
        """
        Generate visualizations for an agent
        
        Args:
            agent_name: Name of the agent
            agent_spec: Agent specification
            architecture_design: Architecture design (if multi-agent)
            output_dir: Directory for output files
            
        Returns:
            VisualizationResult with generated diagrams
        """
        logger.info(f"Generating visualizations for {agent_name}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate different diagram types
        architecture_diagram = self._generate_architecture_diagram(agent_name, agent_spec)
        component_diagram = self._generate_component_diagram(agent_name, agent_spec)
        data_flow_diagram = self._generate_data_flow_diagram(agent_name, agent_spec)
        workflow_diagram = self._generate_workflow_diagram(agent_name, agent_spec)
        
        # Save diagrams
        files_generated = []
        
        # Create master visualization document
        master_doc = self._create_master_document(
            agent_name,
            architecture_diagram,
            component_diagram,
            data_flow_diagram,
            workflow_diagram
        )
        
        master_path = output_dir / f"{agent_name}_architecture.md"
        master_path.write_text(master_doc)
        files_generated.append(str(master_path))
        logger.info(f"  ✓ Generated: {master_path}")
        
        # Save individual diagrams
        arch_path = output_dir / f"{agent_name}_architecture_diagram.md"
        arch_path.write_text(f"# Architecture Diagram\n\n{architecture_diagram}")
        files_generated.append(str(arch_path))
        
        logger.info(f"✓ Visualizations generated")
        logger.info(f"  Files created: {len(files_generated)}")
        
        return VisualizationResult(
            architecture_diagram=architecture_diagram,
            component_diagram=component_diagram,
            data_flow_diagram=data_flow_diagram,
            workflow_diagram=workflow_diagram,
            files_generated=files_generated
        )
    
    def _generate_architecture_diagram(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any]
    ) -> str:
        """Generate high-level architecture diagram"""
        agent_type = agent_spec.get('agent_type', 'unknown')
        
        diagram = f"""```mermaid
graph TB
    subgraph "{agent_name}"
        Agent["{agent_name}<br/>{agent_type}"]
        
"""
        
        # Add data sources
        data_sources = agent_spec.get('data_sources', [])
        if data_sources:
            diagram += "        subgraph DataSources[\"Data Sources\"]\n"
            if isinstance(data_sources, list):
                for i, ds in enumerate(data_sources):
                    ds_info = ds if isinstance(ds, str) else ds.get('type', f'Source{i}')
                    diagram += f"            DS{i}[\"{ds_info}\"]\n"
            diagram += "        end\n"
            diagram += "        DataSources --> Agent\n"
        
        # Add capabilities
        capabilities = agent_spec.get('capabilities', [])
        if capabilities:
            diagram += "        subgraph Capabilities[\"Capabilities\"]\n"
            if isinstance(capabilities, list):
                for i, cap in enumerate(capabilities):
                    cap_name = cap if isinstance(cap, str) else cap.get('name', f'Capability{i}')
                    diagram += f"            CAP{i}[\"{cap_name}\"]\n"
            diagram += "        end\n"
            diagram += "        Agent --> Capabilities\n"
        
        # Add output
        diagram += "        Agent --> Output[\"Results\"]\n"
        
        diagram += "    end\n```"
        
        return diagram
    
    def _generate_component_diagram(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any]
    ) -> str:
        """Generate component interaction diagram"""
        diagram = f"""```mermaid
graph LR
    subgraph "{agent_name} Components"
        Input[Input Data] --> Validation[Validation]
        Validation --> Processing[Processing]
        Processing --> Output[Output]
        
"""
        
        # Add workflow steps as components
        workflow = agent_spec.get('workflow', {})
        steps = workflow.get('steps', {})
        
        if steps:
            for i, (step_name, _) in enumerate(steps.items()):
                safe_name = step_name.replace(' ', '_')
                diagram += f"        Processing --> Step{i}[{step_name}]\n"
        
        diagram += "    end\n```"
        
        return diagram
    
    def _generate_data_flow_diagram(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any]
    ) -> str:
        """Generate data flow diagram"""
        diagram = f"""```mermaid
flowchart LR
    Start([Start]) --> Input{{\"Input Data\"}}
    Input --> Fetch[\"Fetch Data\"]
    
"""
        
        # Add workflow steps
        workflow = agent_spec.get('workflow', {})
        steps = workflow.get('steps', {})
        
        prev_step = "Fetch"
        for i, (step_name, details) in enumerate(steps.items()):
            safe_name = f"Step{i}"
            step_desc = details.get('description', step_name) if isinstance(details, dict) else step_name
            
            diagram += f"    {prev_step} --> {safe_name}[\"{step_desc}\"]\n"
            prev_step = safe_name
        
        diagram += f"    {prev_step} --> End([End])\n```"
        
        return diagram
    
    def _generate_workflow_diagram(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any]
    ) -> str:
        """Generate detailed workflow flowchart"""
        diagram = f"""```mermaid
flowchart TD
    Start([Start: {agent_name}])
    Start --> Init[Initialize Agent]
    Init --> ValidateInput{{\"Validate Input\"}}
    
    ValidateInput -->|Valid| Process[Process Request]
    ValidateInput -->|Invalid| Error1[Return Error]
    
"""
        
        # Add workflow steps with error handling
        workflow = agent_spec.get('workflow', {})
        steps = workflow.get('steps', {})
        
        if steps:
            prev_node = "Process"
            for i, (step_name, details) in enumerate(steps.items()):
                step_id = f"Step{i}"
                diagram += f"    {prev_node} --> {step_id}[\"{step_name}\"]\n"
                
                # Add error handling for each step
                error_id = f"Error{i+2}"
                diagram += f"    {step_id} -->|Error| {error_id}[Handle Error]\n"
                diagram += f"    {error_id} --> Retry{{\"Retry?\"}}\n"
                diagram += f"    Retry -->|Yes| {step_id}\n"
                diagram += f"    Retry -->|No| End([End])\n"
                
                prev_node = step_id
            
            diagram += f"    {prev_node} --> Success[Format Response]\n"
            diagram += "    Success --> End\n"
        else:
            diagram += "    Process --> Success[Format Response]\n"
            diagram += "    Success --> End([End])\n"
        
        diagram += "    Error1 --> End\n```"
        
        return diagram
    
    def _create_master_document(
        self,
        agent_name: str,
        architecture: str,
        components: str,
        data_flow: str,
        workflow: Optional[str]
    ) -> str:
        """Create master documentation with all diagrams"""
        doc = f"""# {agent_name} - Architecture Visualization

**Generated by Meta-Agent**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Diagram](#component-diagram)
3. [Data Flow](#data-flow)
4. [Detailed Workflow](#detailed-workflow)

---

## Architecture Overview

High-level view of the agent architecture, showing data sources, capabilities, and outputs.

{architecture}

---

## Component Diagram

Shows the internal components and their interactions within the agent.

{components}

---

## Data Flow

Illustrates how data flows through the agent from input to output.

{data_flow}

---

## Detailed Workflow

Detailed flowchart showing the complete execution flow including error handling.

{workflow or "Workflow diagram not available"}

---

## How to View

These diagrams use Mermaid syntax. To view them:

1. **GitHub/GitLab**: Renders automatically in markdown files
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Online**: Copy to [mermaid.live](https://mermaid.live/)
4. **Documentation Sites**: Supported by MkDocs, Docusaurus, etc.

---

## Legend

### Node Types
- `[Rectangle]`: Process/Action
- `{{Diamond}}`: Decision Point
- `([Rounded])`: Start/End
- `[[Subroutine]]`: Sub-process

### Arrow Types
- `-->`: Sequential flow
- `-.->`: Optional/Conditional
- `==>`: Data flow
- `--x`: Error/Exception

---

**Note**: This visualization is auto-generated based on the agent specification.
For the most accurate representation, ensure the spec is up-to-date.
"""
        
        return doc
    
    def visualize_multi_agent_system(
        self,
        agents: List[str],
        interactions: List[Dict[str, str]],
        output_dir: Path
    ) -> str:
        """Generate system-level diagram for multiple agents"""
        logger.info("Generating multi-agent system diagram")
        
        diagram = """```mermaid
graph TB
    subgraph "Multi-Agent System"
"""
        
        # Add agents
        for agent in agents:
            diagram += f"        {agent}[\"{agent}\"]\n"
        
        # Add interactions
        for interaction in interactions:
            from_agent = interaction.get('from')
            to_agent = interaction.get('to')
            label = interaction.get('data', '')
            
            if from_agent and to_agent:
                arrow = f"|{label}|" if label else ""
                diagram += f"        {from_agent} -->{arrow} {to_agent}\n"
        
        diagram += "    end\n```"
        
        # Save diagram
        output_dir.mkdir(parents=True, exist_ok=True)
        diagram_path = output_dir / "multi_agent_system.md"
        diagram_path.write_text(f"# Multi-Agent System\n\n{diagram}")
        logger.info(f"  ✓ Generated: {diagram_path}")
        
        return diagram


def visualize_agent_architecture(
    agent_name: str,
    agent_spec: Dict[str, Any],
    output_dir: Path,
    architecture_design: Optional[Dict[str, Any]] = None
) -> VisualizationResult:
    """
    Convenience function to visualize agent architecture
    
    Args:
        agent_name: Agent name
        agent_spec: Agent specification
        output_dir: Output directory
        architecture_design: Optional architecture design
        
    Returns:
        VisualizationResult
    """
    tool = VisualizeArchitectureTool()
    return tool.visualize_agent(agent_name, agent_spec, architecture_design, output_dir)

