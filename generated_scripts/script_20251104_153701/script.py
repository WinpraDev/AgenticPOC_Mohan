#!/usr/bin/env python3
import os
from loguru import logger
import psycopg2
from psycopg2.extras import RealDictCursor

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
        return psycopg2.connect(CONFIG['db_url'], cursor_factory=RealDictCursor)
    
    def execute(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Step 1: Retrieve Properties Data
            query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
            cursor.execute(query)
            
            properties = []
            for row in cursor.fetchall():
                property_name = row.get('property_name', 'Unknown')
                noi = float(row.get('noi', 0))
                debt_service = float(row.get('annual_debt_service', 0))
                
                properties.append({
                    'property_name': property_name,
                    'noi': noi,
                    'debt_service': debt_service
                })
            
            # Step 2: Calculate Average NOI
            total_noi = sum(prop['noi'] for prop in properties)
            average_noi = total_noi / len(properties) if properties else 0
            
            # Step 3: Calculate Total Debt Service
            total_debt_service = sum(prop['debt_service'] for prop in properties)
            
            # Step 4: Calculate Percentage of Properties with DSCR Above 1.25
            dscr_threshold = 1.25
            properties_above_dscr = [prop for prop in properties if prop['noi'] / prop['debt_service'] > dscr_threshold]
            percentage_above_dscr = (len(properties_above_dscr) / len(properties)) * 100 if properties else 0
            
            results = {
                'average_noi': average_noi,
                'total_debt_service': total_debt_service,
                'percentage_above_dscr': percentage_above_dscr
            }
            
            # Print results to console
            logger.info("=== Portfolio Summary ===")
            logger.info(f"Average NOI: {average_noi:.2f}")
            logger.info(f"Total Debt Service: {total_debt_service:.2f}")
            logger.info(f"Percentage of Properties with DSCR Above 1.25: {percentage_above_dscr:.2f}%")
            logger.info("=== End Summary ===")
            
            return results
        finally:
            conn.close()

# Main execution block
if __name__ == "__main__":
    executor = TaskExecutor()
    results = executor.execute()