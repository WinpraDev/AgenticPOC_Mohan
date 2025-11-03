"""
Tool: Deploy Multi-Agent System (Single Container)

This tool deploys all agents in a single Docker container with orchestration.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path
import yaml


class SystemDeploymentResult(BaseModel):
    """Model for system deployment result"""
    success: bool = Field(..., description="Whether deployment succeeded")
    deployment_type: str = Field(..., description="Type of deployment")
    container_name: str = Field(..., description="Docker container name")
    agents_deployed: List[str] = Field(..., description="List of deployed agents")
    artifacts: List[str] = Field(default_factory=list, description="Deployment artifacts created")
    logs: List[str] = Field(default_factory=list, description="Deployment logs")


class MultiAgentSystemDeployer:
    """
    Deploy multiple agents in a single container
    
    Creates:
    - Single Dockerfile for all agents
    - Orchestrator to coordinate agents
    - docker-compose.yml for easy deployment
    - Simulation runner
    - Deployment scripts
    """
    
    def __init__(self):
        logger.info("Initializing MultiAgentSystemDeployer")
    
    def deploy_system(
        self,
        system_name: str,
        agents: Dict[str, Dict[str, Any]],
        output_dir: Path = None
    ) -> SystemDeploymentResult:
        """
        Deploy complete multi-agent system in single container
        
        Args:
            system_name: Name of the system (e.g., "dscr-agent-system")
            agents: Dictionary of agent_name -> {code_path, spec}
            output_dir: Directory for deployment artifacts
            
        Returns:
            SystemDeploymentResult with deployment details
        """
        logger.info(f"Deploying multi-agent system: {system_name}")
        logger.info(f"  Agents: {len(agents)}")
        
        if output_dir is None:
            output_dir = Path("deployment") / system_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        agents_dir = output_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        artifacts = []
        logs = []
        
        # Copy all agent code to deployment directory
        for agent_name, agent_data in agents.items():
            code_path = Path(agent_data['code_path'])
            target_path = agents_dir / code_path.name
            target_path.write_text(code_path.read_text())
            artifacts.append(str(target_path))
            logs.append(f"Copied {agent_name} code to {target_path}")
        
        # Generate orchestrator
        orchestrator_code = self._generate_orchestrator(system_name, agents)
        orchestrator_path = output_dir / "orchestrator.py"
        orchestrator_path.write_text(orchestrator_code)
        artifacts.append(str(orchestrator_path))
        logs.append(f"Generated orchestrator: {orchestrator_path}")
        
        # Generate simulation runner
        simulation_code = self._generate_simulation_runner(system_name, agents)
        simulation_path = output_dir / "run_simulation.py"
        simulation_path.write_text(simulation_code)
        artifacts.append(str(simulation_path))
        logs.append(f"Generated simulation runner: {simulation_path}")
        
        # Generate Dockerfile
        dockerfile = self._generate_dockerfile(system_name, agents)
        dockerfile_path = output_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile)
        artifacts.append(str(dockerfile_path))
        logs.append(f"Generated Dockerfile: {dockerfile_path}")
        
        # Generate docker-compose.yml
        compose = self._generate_docker_compose(system_name, agents)
        compose_path = output_dir / "docker-compose.yml"
        compose_path.write_text(compose)
        artifacts.append(str(compose_path))
        logs.append(f"Generated docker-compose.yml: {compose_path}")
        
        # Generate .env.example
        env_file = self._generate_env_file(agents)
        env_path = output_dir / ".env.example"
        env_path.write_text(env_file)
        artifacts.append(str(env_path))
        logs.append(f"Generated .env.example: {env_path}")
        
        # Generate requirements.txt
        requirements = self._generate_requirements(agents)
        req_path = output_dir / "requirements.txt"
        req_path.write_text(requirements)
        artifacts.append(str(req_path))
        logs.append(f"Generated requirements.txt: {req_path}")
        
        # Generate deployment script
        deploy_script = self._generate_deploy_script(system_name)
        deploy_path = output_dir / "deploy.sh"
        deploy_path.write_text(deploy_script)
        deploy_path.chmod(0o755)
        artifacts.append(str(deploy_path))
        logs.append(f"Generated deploy.sh: {deploy_path}")
        
        # Generate README
        readme = self._generate_readme(system_name, agents)
        readme_path = output_dir / "README.md"
        readme_path.write_text(readme)
        artifacts.append(str(readme_path))
        logs.append(f"Generated README.md: {readme_path}")
        
        logger.info(f"✓ System deployment artifacts created: {len(artifacts)} files")
        
        return SystemDeploymentResult(
            success=True,
            deployment_type="docker-single-container",
            container_name=system_name,
            agents_deployed=list(agents.keys()),
            artifacts=artifacts,
            logs=logs
        )
    
    def _generate_orchestrator(self, system_name: str, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate orchestrator code"""
        agent_names = list(agents.keys())
        agent_classes = [name.capitalize() for name in agent_names]
        
        imports = "\n".join([
            f"from agents.{name.lower()} import {name.capitalize()}"
            for name in agent_names
        ])
        
        init_agents = "\n        ".join([
            f"self.{name.lower()} = {name.capitalize()}()"
            for name in agent_names
        ])
        
        # Determine workflow based on agent types
        workflow_code = self._generate_workflow_code(agents)
        
        return f'''"""
{system_name.replace("-", " ").title()} Orchestrator
Auto-generated by Meta-Agent System

Coordinates all agents in a single unified workflow
"""

import os
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
import json

# Add agents to path
sys.path.insert(0, str(Path(__file__).parent))

{imports}


class SystemOrchestrator:
    """Orchestrates all agents in a single workflow"""
    
    def __init__(self):
        {init_agents}
        logger.info("All agents initialized")
    
    def run_analysis(self, **kwargs) -> dict:
        """
        Run complete workflow
        
        Args:
            **kwargs: Input parameters for the workflow
            
        Returns:
            Complete analysis result
        """
        try:
            logger.info("Starting workflow...")
{workflow_code}
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {{e}}")
            raise
    
    def run_batch_analysis(self, inputs: list) -> list:
        """
        Run analysis for multiple inputs
        
        Args:
            inputs: List of input parameter dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        for idx, input_params in enumerate(inputs, 1):
            try:
                logger.info(f"Processing input {{idx}}/{{len(inputs)}}")
                result = self.run_analysis(**input_params)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process input {{idx}}: {{e}}")
                results.append({{"status": "ERROR", "error": str(e)}})
        return results
    
    def save_results(self, results: dict, output_file: str = None):
        """Save results to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"results/analysis_{{timestamp}}.json"
        
        # Ensure results directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {{output_file}}")
        return output_file


def main():
    """Main execution"""
    logger.add("logs/orchestrator.log", rotation="1 day")
    
    orchestrator = SystemOrchestrator()
    
    # Get input from environment or use defaults
    input_params = {{}}
    for key in os.environ:
        if key.startswith("INPUT_"):
            param_name = key.replace("INPUT_", "").lower()
            input_params[param_name] = os.getenv(key)
    
    # If no inputs provided, use defaults
    if not input_params:
        input_params = {{"property_name": "Orlando Fashion Square"}}  # Default example
    
    # Run analysis
    logger.info("="*70)
    logger.info("{system_name.upper()} - Starting Analysis")
    logger.info("="*70)
    
    result = orchestrator.run_analysis(**input_params)
    
    # Save and display results
    output_file = orchestrator.save_results(result)
    
    logger.info("\\n" + "="*70)
    logger.info("ANALYSIS COMPLETE")
    logger.info("="*70)
    logger.info(f"\\nResults saved to: {{output_file}}")
    logger.info("="*70)


if __name__ == "__main__":
    main()
'''
    
    def _generate_workflow_code(self, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate workflow code based on agent types"""
        # Simple sequential workflow
        agent_names = list(agents.keys())
        
        workflow_lines = []
        workflow_lines.append("            ")
        workflow_lines.append("            # Execute agents in sequence")
        
        for idx, agent_name in enumerate(agent_names):
            agent_var = agent_name.lower()
            if idx == 0:
                workflow_lines.append(f"            result = self.{agent_var}.run(**kwargs)")
                workflow_lines.append(f"            logger.info(f\"✓ {agent_name} completed\")")
            else:
                workflow_lines.append(f"            result = self.{agent_var}.run(result)")
                workflow_lines.append(f"            logger.info(f\"✓ {agent_name} completed\")")
        
        return "\n".join(workflow_lines)
    
    def _generate_simulation_runner(self, system_name: str, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate simulation runner"""
        return f'''"""
Simulation Runner for {system_name.replace("-", " ").title()}
Auto-generated by Meta-Agent System

Run multiple scenarios and simulations in single container
"""

import sys
from pathlib import Path
from loguru import logger
import json

sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SystemOrchestrator


def run_scenario_simulation():
    """Run multiple what-if scenarios"""
    
    orchestrator = SystemOrchestrator()
    
    # Define simulation scenarios
    scenarios = [
        {{
            "name": "Scenario 1",
            "description": "Base case analysis",
            "params": {{"property_name": "Orlando Fashion Square"}}
        }},
        {{
            "name": "Scenario 2",
            "description": "Alternative property",
            "params": {{"property_name": "Millenia Mall"}}
        }}
    ]
    
    logger.info("="*70)
    logger.info("RUNNING SIMULATIONS")
    logger.info("="*70)
    
    results = []
    
    for idx, scenario in enumerate(scenarios, 1):
        logger.info(f"\\n--- Scenario {{idx}}: {{scenario['name']}} ---")
        logger.info(f"Description: {{scenario['description']}}")
        
        try:
            result = orchestrator.run_analysis(**scenario['params'])
            result['scenario_name'] = scenario['name']
            result['scenario_description'] = scenario['description']
            results.append(result)
            logger.info(f"✓ {{scenario['name']}} completed")
        except Exception as e:
            logger.error(f"✗ {{scenario['name']}} failed: {{e}}")
    
    # Save simulation results
    output_file = orchestrator.save_results(
        {{"scenarios": results, "total_scenarios": len(scenarios)}},
        "results/simulation_results.json"
    )
    
    logger.info("\\n" + "="*70)
    logger.info("SIMULATION COMPLETE")
    logger.info("="*70)
    logger.info(f"Scenarios run: {{len(results)}}/{{len(scenarios)}}")
    logger.info(f"Results: {{output_file}}")


def run_batch_analysis():
    """Run analysis for multiple inputs"""
    
    orchestrator = SystemOrchestrator()
    
    # Define batch inputs
    inputs = [
        {{"property_name": "Orlando Fashion Square"}},
        {{"property_name": "Millenia Mall"}},
        {{"property_name": "Florida Mall"}}
    ]
    
    logger.info("="*70)
    logger.info("BATCH ANALYSIS")
    logger.info("="*70)
    
    results = orchestrator.run_batch_analysis(inputs)
    
    # Save results
    output_file = orchestrator.save_results(
        {{"results": results, "total_inputs": len(inputs)}},
        "results/batch_analysis.json"
    )
    
    logger.info("\\n" + "="*70)
    logger.info("BATCH ANALYSIS COMPLETE")
    logger.info("="*70)
    logger.info(f"Inputs processed: {{len(results)}}")
    logger.info(f"Results: {{output_file}}")


if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "scenario"
    
    if mode == "scenario":
        run_scenario_simulation()
    elif mode == "batch":
        run_batch_analysis()
    else:
        logger.error(f"Unknown mode: {{mode}}")
        logger.info("Usage: python run_simulation.py [scenario|batch]")
'''
    
    def _generate_dockerfile(self, system_name: str, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate Dockerfile for single container"""
        return f'''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all agents
COPY agents/ ./agents/

# Copy orchestrator and simulation runner
COPY orchestrator.py .
COPY run_simulation.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create directories for file storage
RUN mkdir -p logs results exports/reports exports/data data

# Expose ports (if needed for API)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command runs orchestrator
CMD ["python", "orchestrator.py"]
'''
    
    def _generate_docker_compose(self, system_name: str, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate docker-compose.yml"""
        return f'''version: '3.8'

services:
  {system_name}:
    build: .
    container_name: {system_name}
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - LOG_LEVEL=${{LOG_LEVEL:-INFO}}
      - SIMULATION_MODE=${{SIMULATION_MODE:-false}}
    volumes:
      # Agent code (for development hot-reload)
      - ./agents:/app/agents
      
      # Real-time file access (Host ↔ Container)
      - ./logs:/app/logs              # System logs
      - ./results:/app/results        # Analysis results (JSON)
      - ./exports:/app/exports        # User-requested files (PDF, Excel, etc.)
      - ./data:/app/data             # Input data files
    networks:
      - agent-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  agent-network:
    driver: bridge
'''
    
    def _generate_env_file(self, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate .env.example file"""
        env_vars = [
            "# Environment Configuration",
            "# Generated by Meta-Agent System",
            "",
            "# Database Configuration",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dscr_poc_db",
            "",
            "# Logging",
            "LOG_LEVEL=INFO",
            "",
            "# System Configuration",
            f"SYSTEM_NAME={list(agents.keys())[0] if agents else 'agent'}-system",
            "SIMULATION_MODE=false",
            "",
            "# Input Parameters (optional)",
            "INPUT_PROPERTY_NAME=Orlando Fashion Square",
            ""
        ]
        return "\n".join(env_vars)
    
    def _generate_requirements(self, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate requirements.txt"""
        # Collect unique dependencies from all agents
        deps = set([
            "pydantic>=2.0.0",
            "loguru>=0.7.0",
            "python-dotenv>=1.0.0",
            "psycopg2-binary>=2.9.0",
            "sqlalchemy>=2.0.0",
            "pyyaml>=6.0"
        ])
        
        # Add dependencies from agent specs
        for agent_data in agents.values():
            spec = agent_data.get('spec', {})
            if 'dependencies' in spec and 'python_packages' in spec['dependencies']:
                for pkg in spec['dependencies']['python_packages']:
                    deps.add(pkg)
        
        return "\n".join(sorted(deps)) + "\n"
    
    def _generate_deploy_script(self, system_name: str) -> str:
        """Generate deployment script"""
        return f'''#!/bin/bash
set -e

echo "========================================================================"
echo "Deploying {system_name.replace("-", " ").title()} (Single Container)"
echo "========================================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment
source .env

# Create necessary directories on host
echo "Creating directories for file storage..."
mkdir -p logs results exports/reports exports/data data

echo ""
echo "Directory Structure:"
echo "  logs/           - System logs"
echo "  results/        - Analysis results (JSON)"
echo "  exports/        - Generated reports and files"
echo "    ├── reports/  - PDF, Excel reports"
echo "    └── data/     - Exported data files"
echo "  data/           - Input data files"
echo ""

echo "Building Docker image..."
docker-compose build

echo "Starting container..."
docker-compose up -d

echo ""
echo "========================================================================"
echo "✓ {system_name.replace("-", " ").title()} deployed successfully!"
echo "========================================================================"
echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Run single analysis:"
echo "  docker exec {system_name} python orchestrator.py"
echo ""
echo "Run simulations:"
echo "  docker exec {system_name} python run_simulation.py scenario"
echo ""
echo "Run batch analysis:"
echo "  docker exec {system_name} python run_simulation.py batch"
echo ""
echo "Stop system:"
echo "  docker-compose down"
echo "========================================================================"
'''
    
    def _generate_readme(self, system_name: str, agents: Dict[str, Dict[str, Any]]) -> str:
        """Generate README.md"""
        agent_list = "\n".join([f"- **{name}**: {data.get('spec', {}).get('description', 'Agent')}"
                                 for name, data in agents.items()])
        
        return f'''# {system_name.replace("-", " ").title()}

**Auto-generated by Meta-Agent System**  
**Deployment Type:** Single Container  
**Agents:** {len(agents)}

---

## 📋 Overview

This system contains multiple agents deployed in a single Docker container:

{agent_list}

---

## 🚀 Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Deploy
```bash
bash deploy.sh
```

### 3. Run Analysis
```bash
# Single analysis
docker exec {system_name} python orchestrator.py

# With custom input
docker exec -e INPUT_PROPERTY_NAME="Your Property" {system_name} python orchestrator.py
```

### 4. Run Simulations
```bash
# Scenario simulations
docker exec {system_name} python run_simulation.py scenario

# Batch analysis
docker exec {system_name} python run_simulation.py batch
```

---

## 📁 Structure

```
.
├── Dockerfile              # Container definition
├── docker-compose.yml      # Container orchestration
├── orchestrator.py         # Agent coordinator
├── run_simulation.py       # Simulation runner
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── deploy.sh              # Deployment script
├── README.md              # This file
│
├── agents/                # All agent code
│   ├── agent1.py
│   ├── agent2.py
│   └── ...
│
├── logs/                  # System logs (real-time sync)
│   └── orchestrator.log
│
├── results/               # Analysis results (real-time sync)
│   ├── analysis_YYYYMMDD_HHMMSS.json
│   ├── simulation_results.json
│   └── batch_analysis.json
│
├── exports/               # User-requested files (real-time sync)
│   ├── reports/          # Generated reports
│   │   ├── property_report.pdf
│   │   └── investment_analysis.xlsx
│   └── data/             # Exported data
│       └── extracted_data.csv
│
└── data/                  # Input data files (real-time sync)
    └── input_properties.csv
```

**📊 Real-Time File Access:**
All directories marked "real-time sync" are immediately accessible on your local machine via Docker volume mounts!

---

## 🛠️ Usage

### View Logs
```bash
docker-compose logs -f
```

### Access Container
```bash
docker exec -it {system_name} bash
```

### View Results
```bash
cat results/analysis_*.json
```

### Stop System
```bash
docker-compose down
```

### Restart System
```bash
docker-compose restart
```

---

## 📂 File Storage & Real-Time Access

### Where Files Are Stored

All generated files are **immediately accessible** on your local machine:

| Directory | Purpose | Location | Real-Time |
|-----------|---------|----------|-----------|
| `logs/` | System logs | Both host & container | ✅ Yes |
| `results/` | Analysis outputs (JSON) | Both host & container | ✅ Yes |
| `exports/reports/` | Generated reports (PDF, Excel) | Both host & container | ✅ Yes |
| `exports/data/` | Exported data files (CSV, etc.) | Both host & container | ✅ Yes |
| `data/` | Input data files | Both host & container | ✅ Yes |

### Example File Locations

**Inside Container:**
```
/app/exports/reports/orlando_fashion_square_report.pdf
```

**On Your Local Machine:**
```
deployment/dscr-agent-system/exports/reports/orlando_fashion_square_report.pdf
```

### Access Generated Files

```bash
# View analysis results
cat results/analysis_*.json

# Open generated report
open exports/reports/property_report.pdf

# View logs
tail -f logs/orchestrator.log

# Copy files out
cp exports/reports/*.pdf ~/Documents/
```

### Upload Input Files

```bash
# Add input data
cp ~/my_properties.csv data/

# Files are immediately available inside container
docker exec {system_name} ls /app/data/
```

---

## 🔧 Configuration

Edit `.env` file to configure:
- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING)
- `INPUT_*`: Default input parameters

---

## 📊 Monitoring

### Health Check
```bash
docker exec {system_name} python -c "print('System is healthy')"
```

### Container Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats {system_name}
```

---

## 🎯 Next Steps

1. Review generated results in `results/` directory
2. Customize simulation scenarios in `run_simulation.py`
3. Modify orchestrator logic in `orchestrator.py` if needed
4. Scale by running multiple containers if required

---

**Generated by Meta-Agent System** 🤖
'''


def deploy_multi_agent_system(
    system_name: str,
    agents: Dict[str, Dict[str, Any]],
    output_dir: Path = None
) -> SystemDeploymentResult:
    """
    Main function to deploy multi-agent system in single container
    
    Args:
        system_name: Name of the system
        agents: Dictionary of agent_name -> {{code_path, spec}}
        output_dir: Output directory for deployment artifacts
        
    Returns:
        SystemDeploymentResult
    """
    deployer = MultiAgentSystemDeployer()
    return deployer.deploy_system(system_name, agents, output_dir)

