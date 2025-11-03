#!/usr/bin/env python3
"""
Meta-Agent Script Executor
Generates and executes scripts directly from natural language
"""

import sys
import time
import subprocess
from pathlib import Path
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from meta_agent.utils.llm_client import LLMClient
from meta_agent.utils.database_inspector import inspect_database_schema, format_schema_for_llm
from meta_agent.analyzers.task_analyzer import analyze_task, validate_task_analysis
from meta_agent.planners.execution_planner import design_execution_plan, validate_execution_plan
from meta_agent.generators.script_generator import generate_script
from meta_agent.validators.script_validator import validate_script
from meta_agent.executors.container_executor import execute_script_in_container

# Configure logger for clean, developer-friendly output with timestamps
logger.remove()
logger.add(
    sys.stdout,
    format="<dim>{time:HH:mm:ss}</dim> | <level>{message}</level>",
    level="INFO",
    colorize=True
)


def _display_execution_results(container_name: str, has_web_interface: bool) -> None:
    """
    Fetch and display the execution results from the container
    
    Args:
        container_name: Name of the Docker container
        has_web_interface: Whether the script has a web interface
    """
    try:
        # Wait a moment for container to produce output
        time.sleep(2)
        
        # Fetch container logs
        result = subprocess.run(
            ["docker", "logs", container_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout + result.stderr
        
        if not logs.strip():
            logger.info("📊 RESULTS")
            logger.info("   (Container running, no output yet)")
            if has_web_interface:
                logger.info("   Check the web interface for results\n")
            return
        
        # Parse and display results
        logger.info("📊 RESULTS")
        logger.info("="*60)
        
        # Look for calculation results section
        in_results = False
        result_lines = []
        
        for line in logs.split('\n'):
            # Detect results section markers
            if '=== Calculation Results ===' in line or '=== Results ===' in line:
                in_results = True
                continue
            elif '=== End Results ===' in line or '===' in line and in_results:
                in_results = False
                continue
            
            # Capture result lines (filter out loguru formatting)
            if in_results:
                # Extract actual content after loguru timestamp/level
                if '|' in line:
                    content = line.split('|')[-1].strip()
                    # Remove module/line number prefix (e.g., "__main__:<module>:71 - ")
                    if ' - ' in content and ':' in content.split(' - ')[0]:
                        content = content.split(' - ', 1)[1].strip()
                    if content:
                        result_lines.append(content)
                elif line.strip():
                    result_lines.append(line.strip())
        
        # Display results
        if result_lines:
            for line in result_lines:
                logger.info(f"   {line}")
        else:
            # No structured results, show last few meaningful lines
            meaningful_lines = [
                line for line in logs.split('\n')[-10:] 
                if line.strip() and 'INFO' in line
            ]
            for line in meaningful_lines[-5:]:
                if '|' in line:
                    content = line.split('|')[-1].strip()
                    logger.info(f"   {content}")
        
        logger.info("="*60 + "\n")
        
    except subprocess.TimeoutExpired:
        logger.warning("   (Container still processing...)")
        if has_web_interface:
            logger.info("   Check the web interface for results\n")
    except Exception as e:
        logger.debug(f"   Could not fetch results: {e}")


def main():
    """Execute the Script Executor workflow"""
    logger.info("\n" + "="*60)
    logger.info("🚀  META-AGENT SCRIPT EXECUTOR")
    logger.info("="*60 + "\n")
    
    # User request - TEST 5: Property Aggregation
    user_request = """
What's the total square footage across all properties? 
Group them by property type and show average GLA per type.
"""
    
    logger.info("📝 Request:")
    logger.info(f"   {user_request.strip()}\n")
    
    try:
        # STEP 1: Initialize LLM
        logger.info("⚙️  Initializing LLM...")
        llm_client = LLMClient()
        logger.success("   ✓ LLM initialized\n")
        
        # STEP 2: Analyze Task
        logger.info("🔍 Analyzing task...")
        task_analysis = analyze_task(user_request, llm_client)
        validate_task_analysis(task_analysis)
        logger.success(f"   ✓ Task analyzed: {task_analysis.task_type}, {task_analysis.complexity}\n")
        
        # STEP 3: Design Execution Plan
        logger.info("📋 Designing execution plan...")
        execution_plan = design_execution_plan(task_analysis, llm_client)
        validate_execution_plan(execution_plan)
        logger.success(f"   ✓ Plan created: {len(execution_plan.steps)} steps\n")
        
        # STEP 3.5: Inspect Database Schema (if database is involved)
        database_schema = None
        if "postgresql" in task_analysis.data_sources or "database" in task_analysis.primary_goal.lower():
            logger.info("🗄️  Inspecting database schema...")
            database_schema = inspect_database_schema()
            if database_schema:
                logger.success(f"   ✓ Schema discovered: {len(database_schema.tables)} tables\n")
                # Log schema summary for visibility
                for table in database_schema.tables:
                    logger.info(f"      • {table.name}: {len(table.columns)} columns, {table.row_count} rows")
            else:
                logger.info("   ⚠ Database not accessible - will use generic patterns\n")
        
        # STEP 4: Generate Script
        logger.info("⚡ Generating script...")
        generated = generate_script(task_analysis, execution_plan, llm_client, database_schema=database_schema)
        logger.success(f"   ✓ Script generated: {generated['metadata']['lines_of_code']} lines\n")
        
        # STEP 5: Validate Script
        logger.info("🔒 Validating script...")
        validation = validate_script(generated['script'], strict_mode=True)
        logger.success(f"   ✓ Validation passed: security score {validation.security_score:.1f}\n")
        
        if not validation.is_valid:
            logger.error("❌ Validation failed\n")
            for issue in validation.issues:
                if issue.severity == "error":
                    logger.error(f"   • {issue.message}")
            return 1
        
        # STEP 6: Containerize and Execute
        logger.info("📦 Creating container...")
        execution_result = execute_script_in_container(
            script_code=generated['script'],
            script_name="script.py",
            requirements=generated['requirements'],
            env_example=generated['env_example'],
            has_web_interface=task_analysis.requires_web_interface,
            port=execution_plan.web_server_config.get('port', 8080) if task_analysis.requires_web_interface else 8080,
            memory_limit=f"{validation.estimated_memory_mb}m",
            cpu_limit=validation.estimated_cpu_cores,
            auto_start=True  # Automatically deploy container
        )
        
        if execution_result.get('status') == 'success':
            logger.success("   ✓ Container created\n")
            
            # STEP 7: Deploy
            if execution_result['auto_started']:
                logger.info("🚀 Deploying container...")
                logger.success("   ✓ Deployment complete\n")
                
                # STEP 8: Fetch and display results
                _display_execution_results(
                    execution_result['container_name'],
                    execution_result['has_web_interface']
                )
            
            # Summary
            logger.info("="*60)
            logger.success("✨  COMPLETED SUCCESSFULLY")
            logger.info("="*60 + "\n")
            
            logger.info(f"📂 Location: {Path(execution_result['execution_dir']).name}")
            logger.info(f"🐳 Container: {execution_result['container_name']}\n")
            
            if execution_result['has_web_interface']:
                logger.info("🌐 WEB INTERFACE")
                logger.info(f"   URL: http://localhost:{execution_result['port']}")
                logger.info(f"   Status: {'🟢 LIVE' if execution_result['auto_started'] else '⏸️  Ready'}\n")
            
            if execution_result['auto_started']:
                logger.info("💡 QUICK COMMANDS")
                if execution_result['has_web_interface']:
                    logger.info(f"   • Open: http://localhost:{execution_result['port']}")
                logger.info(f"   • Logs: docker-compose -f {execution_result['execution_dir']}/docker-compose.yml logs -f")
                logger.info(f"   • Stop: docker-compose -f {execution_result['execution_dir']}/docker-compose.yml down")
            else:
                logger.info("🚀 TO DEPLOY")
                logger.info(f"   cd {execution_result['execution_dir']}")
                logger.info(f"   bash deploy.sh")
            
            logger.info("\n" + "="*60 + "\n")
            
            return 0
        else:
            logger.error(f"❌ Failed\n")
            logger.error(f"   Error: {execution_result.get('error')}")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

