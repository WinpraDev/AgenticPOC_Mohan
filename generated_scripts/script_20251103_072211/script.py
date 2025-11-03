#!/usr/bin/env python3
import os
from loguru import logger
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration from environment variables
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', '8080'))
}

class TaskExecutor:
    def __init__(self):
        # DO NOT connect to database here!
        # Store config only, connect later when needed
        pass
    
    def get_connection(self):
        # Create connection when actually needed
        if not CONFIG['db_url']:
            raise ValueError("DATABASE_URL not configured")
        return psycopg2.connect(CONFIG['db_url'])
    
    def execute(self):
        conn = self.get_connection()
        try:
            # ... do work with connection ...
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Query all properties and their financial metrics
            query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
            cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                property_name = row.get('property_name', 'Unknown')
                noi = float(row.get('noi', 0))
                debt_service = float(row.get('annual_debt_service', 0))
                
                # Calculate DSCR
                if debt_service == 0:
                    dscr = float('inf')
                else:
                    dscr = noi / debt_service
                
                results.append({
                    'property_name': property_name,
                    'noi': noi,
                    'annual_debt_service': debt_service,
                    'dscr': dscr
                })
            
            return results
        
        finally:
            conn.close()

# Main execution block
if __name__ == "__main__":
    executor = TaskExecutor()
    
    try:
        results = executor.execute()
        
        # Print calculation results to terminal using logger.info()
        logger.info("=== Calculation Results ===")
        for result in results:
            logger.info(f"{result['property_name']}: DSCR = {result['dscr']:.2f}")
        logger.info("=== End Results ===")
        
    except Exception as e:
        logger.error(f"Error: {e}")