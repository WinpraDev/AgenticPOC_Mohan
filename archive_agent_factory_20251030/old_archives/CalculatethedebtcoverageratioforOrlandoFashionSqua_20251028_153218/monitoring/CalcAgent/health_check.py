"""
Health check for CalcAgent
"""

import os
import sys
from loguru import logger


def check_database_connection():
    """Check if database is accessible"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False


def check_agent_status():
    """Check if agent is running properly"""
    # Add custom health checks here
    return True


def main():
    """Run all health checks"""
    checks = {
        "database": check_database_connection(),
        "agent": check_agent_status()
    }
    
    all_passed = all(checks.values())
    
    if all_passed:
        logger.info("✅ All health checks passed")
        sys.exit(0)
    else:
        logger.error(f"❌ Health checks failed: {checks}")
        sys.exit(1)


if __name__ == "__main__":
    main()
