#!/usr/bin/env python3
import os
from loguru import logger
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration from environment
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', '8080'))
}

class TaskExecutor:
    def __init__(self):
        # Store config only, connect later when needed
        pass
    
    def get_connection(self):
        if not CONFIG['db_url']:
            raise ValueError("DATABASE_URL not configured")
        return psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)
    
    def execute(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
            cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                property_name = row.get('property_name', 'Unknown')
                noi = float(row.get('noi', 0))
                debt_service = float(row.get('annual_debt_service', 0))
                
                if debt_service == 0:
                    dscr = float('inf')
                else:
                    dscr = noi / debt_service
                
                results.append({
                    'property_name': property_name,
                    'dscr': dscr
                })
            
            return results
        finally:
            conn.close()

def calculate_dscr():
    executor = TaskExecutor()
    results = executor.execute()
    
    logger.info("=== Calculation Results ===")
    for result in results:
        logger.info(f"{result['property_name']}: DSCR = {result['dscr']:.2f}")
    logger.info("=== End Results ===")
    
    return results

if __name__ == "__main__":
    try:
        results = calculate_dscr()
    except Exception as e:
        logger.error(f"Error: {e}")