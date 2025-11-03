"""
Test Setup Script
Verifies that all components are properly configured.
NO FALLBACKS - Will fail clearly if any component is missing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
import httpx
from sqlalchemy import create_engine, text

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def test_configuration():
    """Test that configuration loads properly"""
    logger.info("Testing configuration...")
    
    try:
        from config import settings
        
        logger.info(f"✓ Configuration loaded")
        logger.info(f"  LLM URL: {settings.llm_base_url}")
        logger.info(f"  LLM Model: {settings.llm_model_name}")
        logger.info(f"  Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
        logger.info(f"  Strict Mode: {settings.meta_agent_strict_mode}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration failed: {e}")
        logger.error("\nPlease create .env file with required variables")
        return False


def test_llm_connection():
    """Test connection to LM Studio"""
    logger.info("\nTesting LM Studio connection...")
    
    try:
        from config import settings
        from meta_agent.utils.llm_client import LLMClient
        
        # Initialize client (will test connection)
        client = LLMClient()
        
        # Run health check
        client.verify_health()
        
        logger.info(f"✓ LM Studio connected successfully")
        logger.info(f"  Model: {client.model_name}")
        logger.info(f"  Temperature: {client.temperature}")
        
        return True
        
    except ConnectionError as e:
        logger.error(f"✗ Cannot connect to LM Studio")
        logger.error(f"  {str(e)}")
        logger.error("\nPlease ensure:")
        logger.error("  1. LM Studio is running")
        logger.error("  2. Model is loaded")
        logger.error("  3. Local server is started on port 1234")
        return False
    
    except Exception as e:
        logger.error(f"✗ LM Studio test failed: {e}")
        return False


def test_database_connection():
    """Test connection to PostgreSQL"""
    logger.info("\nTesting PostgreSQL connection...")
    
    try:
        from config import settings
        
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT COUNT(*) as count FROM properties"))
            count = result.fetchone()[0]
            
            logger.info(f"✓ PostgreSQL connected successfully")
            logger.info(f"  Properties in database: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error("\nPlease ensure:")
        logger.error("  1. PostgreSQL is running")
        logger.error("  2. Database exists")
        logger.error("  3. Credentials in .env are correct")
        logger.error("  4. 'properties' table exists")
        return False


def test_docker():
    """Test Docker availability"""
    logger.info("\nTesting Docker...")
    
    try:
        import docker
        
        client = docker.from_env()
        client.ping()
        
        logger.info(f"✓ Docker is available")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Docker test failed: {e}")
        logger.error("\nPlease ensure:")
        logger.error("  1. Docker Desktop is running")
        logger.error("  2. Docker daemon is accessible")
        logger.warning("\nNote: Docker is only required for custom code execution mode")
        return False


def test_tool_imports():
    """Test that all tools can be imported"""
    logger.info("\nTesting tool imports...")
    
    try:
        from meta_agent.tools.analyze_requirements import analyze_requirements
        from meta_agent.tools.design_agent_architecture import design_agent_architecture
        from meta_agent.tools.generate_agent_specification import generate_agent_specification
        from meta_agent.tools.generate_agent_code import generate_agent_code
        from meta_agent.tools.file_operations import write_file, read_file
        from meta_agent.validators.code_validator import validate_code
        
        logger.info(f"✓ All tools imported successfully")
        logger.info(f"  - analyze_requirements")
        logger.info(f"  - design_agent_architecture")
        logger.info(f"  - generate_agent_specification")
        logger.info(f"  - generate_agent_code")
        logger.info(f"  - file_operations")
        logger.info(f"  - code_validator")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Tool import failed: {e}")
        return False


def main():
    """Run all setup tests"""
    logger.info("="*70)
    logger.info("META-AGENT SETUP VERIFICATION")
    logger.info("="*70)
    
    results = {
        "Configuration": test_configuration(),
        "LM Studio": test_llm_connection(),
        "PostgreSQL": test_database_connection(),
        "Docker": test_docker(),
        "Tool Imports": test_tool_imports()
    }
    
    logger.info("\n" + "="*70)
    logger.info("TEST RESULTS")
    logger.info("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{test_name:20s}: {status}")
    
    # Calculate success
    required_tests = ["Configuration", "LM Studio", "PostgreSQL", "Tool Imports"]
    required_passed = all(results.get(test, False) for test in required_tests)
    
    logger.info("="*70)
    
    if required_passed:
        logger.info("✓ ALL REQUIRED TESTS PASSED")
        logger.info("\nSystem is ready to generate agents!")
        logger.info("\nNext steps:")
        logger.info("  1. Run: python simple_example.py")
        logger.info("  2. Or build your own meta-agent workflow")
        return 0
    else:
        logger.error("✗ SOME REQUIRED TESTS FAILED")
        logger.error("\nPlease fix the issues above before proceeding")
        logger.error("\nRequired:")
        logger.error("  - Configuration must load")
        logger.error("  - LM Studio must be connected")
        logger.error("  - PostgreSQL must be accessible")
        logger.error("  - Tools must import successfully")
        logger.error("\nOptional:")
        logger.error("  - Docker (only for custom code execution)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

