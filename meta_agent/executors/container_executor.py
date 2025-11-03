"""
Container Executor
Builds and executes scripts in Docker containers
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from meta_agent.generators.dockerfile_generator import (
    generate_dockerfile,
    generate_docker_compose,
    generate_deploy_script
)


class ExecutionResult(Dict[str, Any]):
    """Result of script execution"""
    pass


def execute_script_in_container(
    script_code: str,
    script_name: str,
    requirements: str,
    env_example: str,
    has_web_interface: bool = False,
    port: int = 8080,
    memory_limit: str = "512m",
    cpu_limit: float = 0.5,
    auto_start: bool = True
) -> ExecutionResult:
    """
    Execute script in Docker container
    
    Args:
        script_code: Python script content
        script_name: Name for the script file
        requirements: requirements.txt content
        env_example: .env.example content
        has_web_interface: Whether script has web interface
        port: Port for web interface
        memory_limit: Container memory limit
        cpu_limit: Container CPU limit
        auto_start: Whether to automatically start container
        
    Returns:
        ExecutionResult with paths and status
    """
    logger.debug("Preparing container execution...")
    
    # Create execution directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    container_name = f"{script_name.replace('.py', '')}_{timestamp}"
    exec_dir = Path("generated_scripts") / container_name
    exec_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"  Execution directory: {exec_dir}")
    logger.info(f"  Container name: {container_name}")
    
    try:
        # Write script file
        script_path = exec_dir / script_name
        script_path.write_text(script_code)
        logger.info(f"  ✓ Script written: {script_name}")
        
        # Write requirements.txt
        req_path = exec_dir / "requirements.txt"
        req_path.write_text(requirements)
        logger.info(f"  ✓ Requirements written")
        
        # Write .env.example
        env_path = exec_dir / ".env.example"
        env_path.write_text(env_example)
        logger.info(f"  ✓ Environment template written")
        
        # Generate Dockerfile
        dockerfile_content = generate_dockerfile(
            script_name=script_name,
            requirements=requirements,
            has_web_interface=has_web_interface,
            port=port
        )
        dockerfile_path = exec_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        logger.info(f"  ✓ Dockerfile generated")
        
        # Generate docker-compose.yml
        compose_content = generate_docker_compose(
            container_name=container_name,
            script_name=script_name,
            has_web_interface=has_web_interface,
            port=port,
            memory_limit=memory_limit,
            cpu_limit=cpu_limit
        )
        compose_path = exec_dir / "docker-compose.yml"
        compose_path.write_text(compose_content)
        logger.info(f"  ✓ docker-compose.yml generated")
        
        # Generate deploy script
        deploy_script = generate_deploy_script(
            container_name=container_name,
            has_web_interface=has_web_interface,
            port=port
        )
        deploy_path = exec_dir / "deploy.sh"
        deploy_path.write_text(deploy_script)
        deploy_path.chmod(0o755)  # Make executable
        logger.info(f"  ✓ deploy.sh generated")
        
        # Create required directories
        (exec_dir / "results").mkdir(exist_ok=True)
        (exec_dir / "logs").mkdir(exist_ok=True)
        (exec_dir / "exports" / "reports").mkdir(parents=True, exist_ok=True)
        (exec_dir / "exports" / "data").mkdir(parents=True, exist_ok=True)
        (exec_dir / "data").mkdir(exist_ok=True)
        logger.info(f"  ✓ Output directories created")
        
        # Generate README
        readme = _generate_readme(
            container_name=container_name,
            script_name=script_name,
            has_web_interface=has_web_interface,
            port=port
        )
        readme_path = exec_dir / "README.md"
        readme_path.write_text(readme)
        logger.info(f"  ✓ README.md generated")
        
        # Build container if auto_start
        if auto_start:
            logger.debug("Preparing for automatic deployment...")
            
            # Create .env from .env.example for auto-deployment
            # User can edit later if needed
            env_file = exec_dir / ".env"
            if not env_file.exists():
                logger.debug("  Creating .env from template...")
                env_file.write_text(env_example)
                logger.debug("  ✓ .env created (edit if needed)")
            
            logger.info("Building and starting container...")
            _build_and_start_container(exec_dir, container_name)
        else:
            logger.info("Container setup complete (not started)")
        
        result = {
            "status": "success",
            "container_name": container_name,
            "execution_dir": str(exec_dir),
            "script_path": str(script_path),
            "has_web_interface": has_web_interface,
            "port": port if has_web_interface else None,
            "url": f"http://localhost:{port}" if has_web_interface else None,
            "auto_started": auto_start,
            "files_generated": [
                str(script_path),
                str(req_path),
                str(env_path),
                str(dockerfile_path),
                str(compose_path),
                str(deploy_path),
                str(readme_path)
            ]
        }
        
        logger.debug("✓ Container execution setup complete")
        if has_web_interface and auto_start:
            logger.info(f"  🌐 Web interface: http://localhost:{port}")
        
        return result
        
    except Exception as e:
        logger.error(f"Container execution setup failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_dir": str(exec_dir) if exec_dir else None
        }


def _build_and_start_container(exec_dir: Path, container_name: str) -> None:
    """Build and start Docker container"""
    
    try:
        # Check if Docker is available
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            cwd=exec_dir
        )
        if result.returncode != 0:
            raise RuntimeError("Docker is not running or not available")
        
        # Run deploy script
        logger.debug("  Running deploy.sh...")
        result = subprocess.run(
            ["bash", "deploy.sh"],
            capture_output=True,
            text=True,
            cwd=exec_dir
        )
        
        # Check container status (more reliable than returncode)
        # Docker Compose outputs warnings to stderr even on success
        
        # Check both running and recently exited containers
        check_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", 
             "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        if container_name in check_result.stdout:
            status = check_result.stdout.strip().split('\t')[1] if '\t' in check_result.stdout else ""
            
            # Console scripts exit after completion (exit code 0 = success)
            # Web scripts stay running
            is_success = (
                'Up' in status or  # Still running (web interface)
                'Exited (0)' in status  # Completed successfully (console script)
            )
            
            if is_success:
                if 'Up' in status:
                    logger.debug("  ✓ Container running")
                else:
                    logger.debug("  ✓ Container executed successfully")
                
                # Log warnings if any, but don't treat them as errors
                if result.stderr and "level=warning" in result.stderr.lower():
                    logger.debug("  ℹ️  Docker Compose warnings (non-critical)")
            else:
                # Container failed (non-zero exit code)
                logger.error(f"  ✗ Container failed: {status}")
                raise RuntimeError(f"Container deployment failed: {status}")
        else:
            # Container not found - real error
            error_lines = []
            for line in result.stderr.split('\n'):
                if line.strip() and 'level=warning' not in line.lower():
                    error_lines.append(line)
            
            error_msg = '\n'.join(error_lines) if error_lines else result.stderr
            logger.error(f"  ✗ Container not created: {error_msg}")
            raise RuntimeError(f"Container deployment failed: {error_msg}")
            
    except Exception as e:
        logger.error(f"Failed to build/start container: {e}")
        raise


def _generate_readme(
    container_name: str,
    script_name: str,
    has_web_interface: bool,
    port: int
) -> str:
    """Generate README for the execution"""
    
    readme = f"""# {container_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Script:** {script_name}  
**Container:** {container_name}

---

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Deploy

```bash
bash deploy.sh
```

---

## 📊 Usage

"""
    
    if has_web_interface:
        readme += f"""### Web Interface

Open your browser:
```
http://localhost:{port}
```

The web interface provides:
- View current results
- Run simulations with different parameters
- Download reports
- Real-time updates

### API Endpoints

```bash
# Health check
curl http://localhost:{port}/health

# Get results
curl http://localhost:{port}/api/results

# Run simulation
curl -X POST http://localhost:{port}/api/simulate \\
  -H "Content-Type: application/json" \\
  -d '{{"scenario": "optimistic"}}'
```

"""
    else:
        readme += """### Running the Script

The script executes automatically when the container starts.

View logs:
```bash
docker-compose logs -f
```

Check results:
```bash
ls -la results/
```

"""
    
    readme += """---

## 📁 Directory Structure

```
.
├── {script_name}           # Main Python script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Container orchestration
├── deploy.sh               # Deployment script
├── .env.example            # Environment template
├── .env                    # Your configuration (create this)
├── results/                # Execution results
├── logs/                   # Application logs
├── exports/
│   ├── reports/            # Generated reports
│   └── data/               # Exported data
└── data/                   # Input data
```

---

## 🛠️ Management

### View Logs

```bash
docker-compose logs -f
```

### Restart Container

```bash
docker-compose restart
```

### Stop Container

```bash
docker-compose down
```

### Rebuild Container

```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Accessing Results

All results are available in real-time on your local machine:

- **Results:** `./results/`
- **Logs:** `./logs/`
- **Reports:** `./exports/reports/`
- **Data:** `./exports/data/`

No need to access the container directly - everything is mounted!

---

## 🔍 Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs
```

### Permission Issues

Fix directory permissions:
```bash
chmod -R 755 results logs exports data
```

### Port Already in Use

Change port in docker-compose.yml and .env

---

**Generated by Meta-Agent Script Executor**
"""
    
    return readme

