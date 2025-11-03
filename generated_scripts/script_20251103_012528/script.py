#!/usr/bin/env python3
import os
from loguru import logger
import psycopg2

# Configuration from environment variables
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
}

class TaskExecutor:
    def __init__(self):
        # Store config only, connect later when needed
        pass
    
    def get_connection(self):
        if not CONFIG['db_url']:
            raise ValueError("DATABASE_URL not configured")
        return psycopg2.connect(CONFIG['db_url'])
    
    def execute(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Fetch all properties
            cursor.execute("SELECT * FROM properties")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                property_dict = dict(zip(columns, row))
                dscr = self.calculate_dscr(property_dict)
                property_dict['dscr'] = dscr
                results.append(property_dict)
            
            return results
        
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            conn.close()
    
    def calculate_dscr(self, property_dict):
        # Example calculation: DSCR = NOI / Total Debt
        noi = float(property_dict.get('noi', 0))
        total_debt = float(property_dict.get('total_debt', 1))  # Avoid division by zero
        return noi / total_debt

def main():
    if not CONFIG['db_url']:
        logger.error("Database URL is not configured. Please set DATABASE_URL in your environment variables.")
        return
    
    try:
        executor = TaskExecutor()
        results = executor.execute()
        
        # Print results to console
        logger.info("=== Calculation Results ===")
        for result in results:
            property_name = result.get('property_name', 'Unknown')
            dscr = float(result.get('dscr', 0))
            logger.info(f"{property_name}: DSCR = {dscr:.2f}")
        logger.info("=== End Results ===")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()