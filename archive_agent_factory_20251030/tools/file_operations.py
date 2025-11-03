"""
File Operations Tools
Utilities for writing and reading files.
NO FALLBACKS - Strict file operations with proper error handling.
"""

from pathlib import Path
from typing import Dict, Any
from loguru import logger

from config import settings


def write_file(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        path: File path (relative to project root or absolute)
        content: Content to write
        overwrite: Whether to overwrite if file exists
    
    Returns:
        Dictionary with success status, path, and bytes written
    
    Raises:
        FileExistsError: If file exists and overwrite=False
        PermissionError: If no permission to write
        OSError: If other I/O error occurs
    """
    file_path = Path(path)
    
    # Make path absolute if relative
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    
    logger.info(f"Writing file: {file_path}")
    
    # Check if file exists
    if file_path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {file_path}. "
            f"Set overwrite=True to replace it."
        )
    
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write content
        file_path.write_text(content, encoding='utf-8')
        
        bytes_written = len(content.encode('utf-8'))
        
        logger.info(f"✓ File written: {file_path}")
        logger.info(f"  Size: {bytes_written} bytes")
        
        return {
            "success": True,
            "path": str(file_path),
            "bytes_written": bytes_written
        }
        
    except PermissionError as e:
        logger.error(f"Permission denied: {file_path}")
        raise PermissionError(
            f"No permission to write file: {file_path}"
        ) from e
    
    except OSError as e:
        logger.error(f"I/O error writing file: {e}")
        raise OSError(
            f"Failed to write file {file_path}: {e}"
        ) from e


def read_file(path: str) -> Dict[str, Any]:
    """
    Read content from a file.
    
    Args:
        path: File path (relative or absolute)
    
    Returns:
        Dictionary with content, exists status, and size
    
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no permission to read
        OSError: If other I/O error occurs
    """
    file_path = Path(path)
    
    # Make path absolute if relative
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    
    logger.info(f"Reading file: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise OSError(f"Not a file: {file_path}")
    
    try:
        content = file_path.read_text(encoding='utf-8')
        size = file_path.stat().st_size
        
        logger.info(f"✓ File read: {file_path}")
        logger.info(f"  Size: {size} bytes")
        
        return {
            "content": content,
            "exists": True,
            "size": size,
            "path": str(file_path)
        }
        
    except PermissionError as e:
        logger.error(f"Permission denied: {file_path}")
        raise PermissionError(
            f"No permission to read file: {file_path}"
        ) from e
    
    except OSError as e:
        logger.error(f"I/O error reading file: {e}")
        raise OSError(
            f"Failed to read file {file_path}: {e}"
        ) from e


def create_directory(path: str) -> Dict[str, Any]:
    """
    Create a directory (and parent directories if needed).
    
    Args:
        path: Directory path
    
    Returns:
        Dictionary with success status and path
    
    Raises:
        PermissionError: If no permission to create directory
        OSError: If other error occurs
    """
    dir_path = Path(path)
    
    # Make path absolute if relative
    if not dir_path.is_absolute():
        dir_path = Path.cwd() / dir_path
    
    logger.info(f"Creating directory: {dir_path}")
    
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✓ Directory created: {dir_path}")
        
        return {
            "success": True,
            "path": str(dir_path)
        }
        
    except PermissionError as e:
        logger.error(f"Permission denied: {dir_path}")
        raise PermissionError(
            f"No permission to create directory: {dir_path}"
        ) from e
    
    except OSError as e:
        logger.error(f"Error creating directory: {e}")
        raise OSError(
            f"Failed to create directory {dir_path}: {e}"
        ) from e


def write_agent_files(
    agent_name: str,
    code: str,
    specification: str,
    tests: str = ""
) -> Dict[str, str]:
    """
    Write all files for a generated agent.
    
    Args:
        agent_name: Name of the agent
        code: Python code
        specification: YAML specification
        tests: Test code (optional)
    
    Returns:
        Dictionary mapping file type to written path
    
    Raises:
        Various file I/O errors
    """
    logger.info(f"Writing files for agent: {agent_name}")
    
    written_files = {}
    
    # Write specification
    spec_path = settings.spec_dir / f"{agent_name.lower()}.yaml"
    write_file(str(spec_path), specification, overwrite=True)
    written_files["specification"] = str(spec_path)
    
    # Write code
    code_path = settings.output_dir / "agents" / f"{agent_name.lower()}.py"
    write_file(str(code_path), code, overwrite=True)
    written_files["code"] = str(code_path)
    
    # Write tests if provided
    if tests:
        test_path = settings.output_dir / "tests" / f"test_{agent_name.lower()}.py"
        write_file(str(test_path), tests, overwrite=True)
        written_files["tests"] = str(test_path)
    
    logger.info(f"✓ All files written for {agent_name}")
    for file_type, path in written_files.items():
        logger.info(f"  {file_type}: {path}")
    
    return written_files

