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
                row_dict = dict(zip(columns, row))
                property_name = row_dict.get('property_name', 'Unknown')
                noi = float(row_dict.get('noi', 0))
                debt_service = float(row_dict.get('debt_service', 0))
                
                if debt_service == 0:
                    dscr = float('inf')
                else:
                    dscr = noi / debt_service
                
                results.append({
                    'property_name': property_name,
                    'noi': noi,
                    'debt_service': debt_service,
                    'dscr': dscr
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            conn.close()

def calculate_dscr():
    executor = TaskExecutor()
    results = executor.execute()
    
    # Print results to console
    logger.info("=== Calculation Results ===")
    for result in results:
        logger.info(f"{result['property_name']}: DSCR = {result['dscr']:.2f}")
    logger.info("=== End Results ===")
    
    return results

if __name__ == "__main__":
    results = calculate_dscr()