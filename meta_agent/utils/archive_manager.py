"""
Archive Manager
Handles archiving and cleanup of generated files after workflow completion
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from loguru import logger
import json


class ArchiveManager:
    """Manages archiving of generated files"""
    
    def __init__(self, base_archive_dir: Path = None):
        """
        Initialize archive manager
        
        Args:
            base_archive_dir: Base directory for archives (default: ./archives)
        """
        self.base_archive_dir = base_archive_dir or Path("archives")
        self.base_archive_dir.mkdir(exist_ok=True)
    
    def create_archive(
        self,
        project_name: str,
        generated_files: Dict[str, Any],
        cleanup: bool = True
    ) -> Path:
        """
        Archive all generated files with proper naming conventions
        
        Args:
            project_name: Name of the project/system
            generated_files: Dictionary containing all generated file paths
            cleanup: Whether to delete original files after archiving
            
        Returns:
            Path to created archive directory
        """
        # Create archive directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_'))[:50]
        archive_name = f"{safe_project_name}_{timestamp}"
        archive_dir = self.base_archive_dir / archive_name
        
        logger.info(f"Creating archive: {archive_name}")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories in archive
        (archive_dir / "agent_code").mkdir(exist_ok=True)
        (archive_dir / "specifications").mkdir(exist_ok=True)
        (archive_dir / "deployment").mkdir(exist_ok=True)
        (archive_dir / "monitoring").mkdir(exist_ok=True)
        (archive_dir / "documentation").mkdir(exist_ok=True)
        
        archived_files = []
        
        # Archive agent specifications
        if "specifications" in generated_files:
            for agent_name, spec_path in generated_files["specifications"].items():
                src = Path(spec_path)
                if src.exists():
                    dst = archive_dir / "specifications" / src.name
                    shutil.copy2(src, dst)
                    archived_files.append(f"specifications/{src.name}")
                    logger.info(f"  ✓ Archived: {src.name}")
        
        # Archive agent code
        if "agent_code" in generated_files:
            for agent_name, code_path in generated_files["agent_code"].items():
                src = Path(code_path)
                if src.exists():
                    dst = archive_dir / "agent_code" / src.name
                    shutil.copy2(src, dst)
                    archived_files.append(f"agent_code/{src.name}")
                    logger.info(f"  ✓ Archived: {src.name}")
        
        # Archive deployment directory (entire folder)
        if "deployment_dir" in generated_files:
            src = Path(generated_files["deployment_dir"])
            if src.exists():
                dst = archive_dir / "deployment" / src.name
                shutil.copytree(src, dst, dirs_exist_ok=True)
                archived_files.append(f"deployment/{src.name}/")
                logger.info(f"  ✓ Archived: deployment/{src.name}/")
        
        # Archive monitoring files
        if "monitoring" in generated_files:
            for agent_name, monitoring_dir in generated_files["monitoring"].items():
                src = Path(monitoring_dir)
                if src.exists():
                    dst = archive_dir / "monitoring" / agent_name
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    archived_files.append(f"monitoring/{agent_name}/")
                    logger.info(f"  ✓ Archived: monitoring/{agent_name}/")
        
        # Create archive summary
        summary = self._create_summary(
            project_name=project_name,
            archive_name=archive_name,
            generated_files=generated_files,
            archived_files=archived_files,
            timestamp=timestamp
        )
        
        summary_path = archive_dir / "ARCHIVE_SUMMARY.md"
        summary_path.write_text(summary)
        logger.info(f"  ✓ Created: ARCHIVE_SUMMARY.md")
        
        # Create manifest.json
        manifest = {
            "project_name": project_name,
            "archive_name": archive_name,
            "timestamp": timestamp,
            "archived_files": archived_files,
            "file_count": len(archived_files),
            "created_at": datetime.now().isoformat()
        }
        manifest_path = archive_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        logger.info(f"  ✓ Created: manifest.json")
        
        # Cleanup original files if requested
        if cleanup:
            self._cleanup_original_files(generated_files)
        
        logger.info(f"✓ Archive created: {archive_dir}")
        logger.info(f"  Total files: {len(archived_files)}")
        
        return archive_dir
    
    def _create_summary(
        self,
        project_name: str,
        archive_name: str,
        generated_files: Dict[str, Any],
        archived_files: List[str],
        timestamp: str
    ) -> str:
        """Create archive summary document"""
        
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        summary = f"""# Archive Summary: {project_name}

**Archive Name:** `{archive_name}`  
**Created:** {date_str}  
**Status:** ✅ Complete

---

## 📊 Archive Contents

**Total Files:** {len(archived_files)}

### Directory Structure

```
{archive_name}/
├── agent_code/           # Generated agent implementations
├── specifications/       # YAML specifications
├── deployment/           # Docker deployment files
├── monitoring/           # Monitoring configuration
├── documentation/        # Additional documentation
├── ARCHIVE_SUMMARY.md   # This file
└── manifest.json        # Archive metadata
```

---

## 📁 Archived Files

"""
        
        # Group files by directory
        by_directory = {}
        for file_path in sorted(archived_files):
            dir_name = file_path.split('/')[0]
            if dir_name not in by_directory:
                by_directory[dir_name] = []
            by_directory[dir_name].append(file_path)
        
        for dir_name, files in by_directory.items():
            summary += f"\n### {dir_name.replace('_', ' ').title()}\n\n"
            for file_path in files:
                summary += f"- `{file_path}`\n"
        
        summary += f"""

---

## 🚀 Usage

### Extract & Deploy

```bash
# Navigate to archive
cd archives/{archive_name}

# Review deployment
cd deployment/*

# Deploy system
bash deploy.sh
```

### Run Agents

```bash
# Run orchestrator
docker exec <container-name> python orchestrator.py

# Run simulations
docker exec <container-name> python run_simulation.py scenario
```

---

## 📝 Notes

- All files have been archived from the workspace
- Original files were cleaned up (if cleanup was enabled)
- This archive is self-contained and portable
- Deployment configurations are ready to use

---

**Generated by Meta-Agent System**  
**Archive Timestamp:** {timestamp}
"""
        
        return summary
    
    def _cleanup_original_files(self, generated_files: Dict[str, Any]):
        """Clean up original files after archiving"""
        
        logger.info("Cleaning up original files...")
        cleaned_count = 0
        
        # Clean up specifications
        if "specifications" in generated_files:
            for agent_name, spec_path in generated_files["specifications"].items():
                src = Path(spec_path)
                if src.exists():
                    src.unlink()
                    cleaned_count += 1
                    logger.info(f"  ✓ Deleted: {spec_path}")
        
        # Clean up agent code
        if "agent_code" in generated_files:
            for agent_name, code_path in generated_files["agent_code"].items():
                src = Path(code_path)
                if src.exists():
                    src.unlink()
                    cleaned_count += 1
                    logger.info(f"  ✓ Deleted: {code_path}")
        
        # Clean up deployment directory
        if "deployment_dir" in generated_files:
            src = Path(generated_files["deployment_dir"])
            if src.exists():
                shutil.rmtree(src)
                cleaned_count += 1
                logger.info(f"  ✓ Deleted: {generated_files['deployment_dir']}/")
        
        # Clean up monitoring directories
        if "monitoring" in generated_files:
            for agent_name, monitoring_dir in generated_files["monitoring"].items():
                src = Path(monitoring_dir)
                if src.exists():
                    shutil.rmtree(src)
                    cleaned_count += 1
                    logger.info(f"  ✓ Deleted: {monitoring_dir}/")
        
        # Clean up empty parent directories
        self._cleanup_empty_dirs()
        
        logger.info(f"✓ Cleanup complete: {cleaned_count} items removed")
    
    def _cleanup_empty_dirs(self):
        """Remove empty directories after cleanup"""
        dirs_to_check = [
            Path("agent_specs"),
            Path("generated_agents/agents"),
            Path("generated_agents"),
            Path("deployment"),
            Path("monitoring")
        ]
        
        for dir_path in dirs_to_check:
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                logger.info(f"  ✓ Removed empty directory: {dir_path}")


def archive_workflow_results(
    project_name: str,
    written_files: Dict[str, Dict[str, str]],
    deployment_result: Any,
    monitoring_results: Dict[str, Any],
    cleanup: bool = True
) -> Path:
    """
    Archive all workflow results
    
    Args:
        project_name: Name of the project
        written_files: Dictionary of agent_name -> {code: path, specification: path}
        deployment_result: Deployment result object
        monitoring_results: Dictionary of agent_name -> monitoring result
        cleanup: Whether to clean up original files
        
    Returns:
        Path to archive directory
    """
    
    # Prepare file structure for archiving
    generated_files = {
        "specifications": {},
        "agent_code": {},
        "deployment_dir": None,
        "monitoring": {}
    }
    
    # Collect specifications and code
    for agent_name, files in written_files.items():
        if "specification" in files:
            generated_files["specifications"][agent_name] = files["specification"]
        if "code" in files:
            generated_files["agent_code"][agent_name] = files["code"]
    
    # Add deployment directory
    if deployment_result and hasattr(deployment_result, 'container_name') and deployment_result.container_name:
        # Get deployment directory using container name
        deployment_dir = Path("deployment") / deployment_result.container_name
        if deployment_dir.exists():
            generated_files["deployment_dir"] = str(deployment_dir)
    elif deployment_result and hasattr(deployment_result, 'artifacts') and deployment_result.artifacts:
        # Fallback: Get deployment directory from first artifact and go up to the main deployment dir
        first_artifact = Path(deployment_result.artifacts[0])
        # Navigate up to find the deployment system directory (contains Dockerfile, docker-compose.yml, etc.)
        current = first_artifact.parent
        while current.name not in ["deployment", "."] and current.parent != current:
            if (current / "Dockerfile").exists() and (current / "docker-compose.yml").exists():
                generated_files["deployment_dir"] = str(current)
                break
            current = current.parent
    
    # Add monitoring directories
    for agent_name, monitoring_result in monitoring_results.items():
        if monitoring_result and hasattr(monitoring_result, 'monitoring_files') and monitoring_result.monitoring_files:
            # Get monitoring directory from first file
            first_file = Path(monitoring_result.monitoring_files[0])
            monitoring_dir = first_file.parent
            generated_files["monitoring"][agent_name] = str(monitoring_dir)
    
    # Create archive
    archive_manager = ArchiveManager()
    archive_path = archive_manager.create_archive(
        project_name=project_name,
        generated_files=generated_files,
        cleanup=cleanup
    )
    
    return archive_path

