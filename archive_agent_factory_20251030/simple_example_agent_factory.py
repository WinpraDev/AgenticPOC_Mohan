"""
Simple Example: Test the Meta-Agent Tools
Demonstrates the complete pipeline for generating a simple DSCR agent.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from meta_agent.utils.llm_client import LLMClient
from meta_agent.tools.analyze_requirements import analyze_requirements, validate_requirements
from meta_agent.tools.design_agent_architecture import design_agent_architecture, validate_architecture
from meta_agent.tools.generate_agent_specification import generate_agent_specification_with_retry, validate_specification_structure
from meta_agent.tools.generate_agent_code import generate_agent_code_with_retry
from meta_agent.validators.code_validator import validate_code
from meta_agent.tools.file_operations import write_agent_files
from meta_agent.tools.deploy_multi_agent_system import deploy_multi_agent_system
from meta_agent.tools.monitor_agent import setup_agent_monitoring, MonitoringConfig
from meta_agent.utils.archive_manager import archive_workflow_results
import yaml

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def main():
    """Run simple example"""
    logger.info("="*70)
    logger.info("SIMPLE EXAMPLE: Generate DSCR Agent (10 Steps)")
    logger.info("="*70)
    
    # User request
    user_request = user_request = """
Calculate the debt coverage ratio for Orlando Fashion Square property.
Check if the rental income is enough to cover debt payments.
Give me a clear recommendation.
"""
    
    logger.info(f"\nUser Request:\n{user_request}\n")
    
    try:
        # Step 1: Initialize LLM Client
        logger.info("STEP 1: Initializing LLM Client...")
        llm_client = LLMClient()
        logger.info("✓ LLM Client ready\n")
        
        # Step 2: Analyze Requirements
        logger.info("STEP 2: Analyzing Requirements...")
        requirements = analyze_requirements(user_request, llm_client)
        validate_requirements(requirements)
        logger.info(f"✓ Requirements analyzed")
        logger.info(f"  Primary Goal: {requirements.primary_goal}")
        logger.info(f"  Agents Needed: {', '.join(requirements.required_agents)}")
        logger.info(f"  Complexity: {requirements.complexity}\n")
        
        # Step 3: Design Architecture
        logger.info("STEP 3: Designing Architecture...")
        architecture = design_agent_architecture(requirements, llm_client)
        validate_architecture(architecture)
        logger.info(f"✓ Architecture designed")
        logger.info(f"  Agents: {len(architecture.agents)}")
        for agent in architecture.agents:
            logger.info(f"    - {agent.agent_name} ({agent.role}, {agent.complexity})")
        logger.info(f"  Orchestrator Needed: {not architecture.no_orchestrator_needed}\n")
        
        # Step 4: Generate Specifications
        logger.info("STEP 4: Generating Specifications...")
        specifications = {}
        for agent_design in architecture.agents:
            logger.info(f"  Generating spec for {agent_design.agent_name}...")
            yaml_spec = generate_agent_specification_with_retry(
                agent_design=agent_design,
                architecture=architecture,
                requirements=requirements,
                llm_client=llm_client
            )
            validate_specification_structure(yaml_spec)
            specifications[agent_design.agent_name] = yaml_spec
            logger.info(f"  ✓ {agent_design.agent_name} spec generated ({len(yaml_spec)} chars)")
        logger.info(f"✓ All specifications generated\n")
        
        # Step 5: Generate Code
        logger.info("STEP 5: Generating Code...")
        generated_code = {}
        for agent_name, yaml_spec in specifications.items():
            logger.info(f"  Generating code for {agent_name}...")
            result = generate_agent_code_with_retry(yaml_spec, llm_client, max_retries=5)
            code = result["code"]
            metadata = result["metadata"]
            retry_count = result.get("retry_count", 0)
            if retry_count > 0:
                logger.info(f"    (Required {retry_count} retries)")
            generated_code[agent_name] = {
                "code": code,
                "specification": yaml_spec,
                "metadata": metadata
            }
            logger.info(f"  ✓ {agent_name} code generated ({metadata['lines']} lines)")
        logger.info(f"✓ All code generated\n")
        
        # Step 6: Validate Code
        logger.info("STEP 6: Validating Code...")
        validation_results = {}
        for agent_name, data in generated_code.items():
            logger.info(f"  Validating {agent_name}...")
            validation = validate_code(data["code"])
            validation_results[agent_name] = validation
            
            if validation.valid:
                logger.info(f"  ✓ {agent_name} validation PASSED")
                logger.info(f"    Risk Score: {validation.risk_score:.2f}")
                logger.info(f"    Issues: {len(validation.issues)}")
            else:
                logger.error(f"  ✗ {agent_name} validation FAILED")
                logger.error(f"    Risk Score: {validation.risk_score:.2f}")
                logger.error(f"    Issues: {len(validation.issues)}")
                for issue in validation.issues[:3]:  # Show first 3 issues
                    logger.error(f"      - {issue.severity}: {issue.message}")
        
        # Check if all passed
        all_valid = all(v.valid for v in validation_results.values())
        if not all_valid:
            logger.error("\n✗ Some agents failed validation. Cannot proceed.")
            return 1
        
        logger.info(f"✓ All code validated\n")
        
        # Step 7: Write Files
        logger.info("STEP 7: Writing Files...")
        written_files = {}
        for agent_name, data in generated_code.items():
            logger.info(f"  Writing files for {agent_name}...")
            files = write_agent_files(
                agent_name=agent_name,
                code=data["code"],
                specification=data["specification"]
            )
            written_files[agent_name] = files
            logger.info(f"  ✓ {agent_name} files written")
        
        logger.info(f"✓ All files written\n")
        
        # Step 8: Deploy All Agents (Single Container)
        logger.info("STEP 8: Deploying Agent System (Single Container)...")
        
        # Prepare agents data for deployment
        agents_for_deployment = {}
        for agent_name, data in generated_code.items():
            agents_for_deployment[agent_name] = {
                'code_path': written_files[agent_name]["code"],
                'spec': yaml.safe_load(data["specification"])
            }
        
        # Determine system name from requirements or use default
        system_name = requirements.primary_goal.lower().replace(" ", "-")[:30] + "-system"
        system_name = "".join(c for c in system_name if c.isalnum() or c == '-')
        
        # Deploy all agents in single container
        deployment_result = deploy_multi_agent_system(
            system_name=system_name,
            agents=agents_for_deployment,
            output_dir=Path(f"deployment/{system_name}")
        )
        
        logger.info(f"  ✓ System deployed: {deployment_result.container_name}")
        logger.info(f"    Agents: {', '.join(deployment_result.agents_deployed)}")
        logger.info(f"    Artifacts: {len(deployment_result.artifacts)} files")
        logger.info(f"✓ Single-container deployment complete\n")
        
        # Step 9: Setup Monitoring
        logger.info("STEP 9: Setting Up Monitoring...")
        monitoring_results = {}
        for agent_name, data in generated_code.items():
            logger.info(f"  Setting up monitoring for {agent_name}...")
            
            # Parse YAML spec
            spec_dict = yaml.safe_load(data["specification"])
            
            # Setup monitoring
            monitoring = setup_agent_monitoring(
                agent_name=agent_name,
                agent_spec=spec_dict,
                output_dir=Path(f"monitoring/{agent_name}")
            )
            monitoring_results[agent_name] = monitoring
            logger.info(f"  ✓ {agent_name} monitoring configured")
            logger.info(f"    Files created: {len(monitoring.monitoring_files)}")
        
        logger.info(f"✓ All monitoring configured\n")
        
        # Step 10: Archive Results
        logger.info("STEP 10: Archiving Results...")
        
        # Determine archive name from requirements
        archive_name = requirements.primary_goal[:60].strip()
        
        # Archive all generated files
        archive_path = archive_workflow_results(
            project_name=archive_name,
            written_files=written_files,
            deployment_result=deployment_result,
            monitoring_results=monitoring_results,
            cleanup=True  # Clean up original files after archiving
        )
        
        logger.info(f"  ✓ All files archived: {archive_path}")
        logger.info(f"  ✓ Original files cleaned up")
        logger.info(f"✓ Archiving complete\n")
        
        # Summary
        logger.info("="*70)
        logger.info("✓ GENERATION, DEPLOYMENT, MONITORING & ARCHIVING COMPLETE")
        logger.info("="*70)
        logger.info(f"\nGenerated Agents: {len(generated_code)}")
        for agent_name, data in generated_code.items():
            logger.info(f"\n{agent_name}:")
            logger.info(f"  Lines of Code: {data['metadata']['lines']}")
            logger.info(f"  Complexity: {data['metadata']['complexity']}")
            logger.info(f"  Validation: ✓ PASSED")
            logger.info(f"  Files:")
            for file_type, path in written_files[agent_name].items():
                logger.info(f"    - {file_type}: {path}")
            logger.info(f"  Monitoring:")
            logger.info(f"    - Files: {len(monitoring_results[agent_name].monitoring_files)}")
            if monitoring_results[agent_name].monitoring_files:
                logger.info(f"    - First file: {monitoring_results[agent_name].monitoring_files[0]}")
        
        logger.info("\n" + "="*70)
        logger.info("Deployment Summary (Single Container):")
        logger.info(f"  Container: {deployment_result.container_name}")
        logger.info(f"  Agents: {', '.join(deployment_result.agents_deployed)}")
        logger.info(f"  Location: deployment/{deployment_result.container_name}/")
        logger.info(f"  Artifacts: {len(deployment_result.artifacts)} files")
        logger.info("="*70)
        logger.info("Agent Status:")
        logger.info("  1. ✓ Generated and validated")
        logger.info("  2. ✓ Deployed in single Docker container")
        logger.info("  3. ✓ Monitoring configured")
        logger.info("  4. ✓ Orchestrator ready")
        logger.info("  5. ✓ Simulation runner included")
        logger.info("  6. ✓ All files archived")
        logger.info("  7. ✓ Workspace cleaned up")
        logger.info("  8. Ready for production use!")
        logger.info("="*70)
        logger.info("\n📦 Archive Location:")
        logger.info(f"  {archive_path}/")
        logger.info("\n📋 Archive Contents:")
        logger.info("  - agent_code/           # Agent implementations")
        logger.info("  - specifications/       # YAML specs")
        logger.info("  - deployment/           # Docker deployment")
        logger.info("  - monitoring/           # Monitoring config")
        logger.info("  - ARCHIVE_SUMMARY.md   # Complete summary")
        logger.info("  - manifest.json        # Archive metadata")
        logger.info("\n🚀 To Deploy:")
        logger.info(f"  cd {archive_path}/deployment/*")
        logger.info("  bash deploy.sh")
        logger.info("\n📊 To Run Analysis:")
        logger.info("  docker exec <container-name> python orchestrator.py")
        logger.info("\n🔬 To Run Simulations:")
        logger.info("  docker exec <container-name> python run_simulation.py scenario")
        logger.info("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n✗ Generation failed: {e}")
        logger.exception("Full error:")
        return 1


if __name__ == "__main__":
    sys.exit(main())

