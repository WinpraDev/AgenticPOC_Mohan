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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Step 1: Retrieve Properties Data
            query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
            cursor.execute(query)
            
            properties = cursor.fetchall()
            
            # Step 2: Calculate Cap Rates
            results = []
            for row in properties:
                property_name = row.get('property_name', 'Unknown')
                noi = float(row.get('noi', 0))
                cap_rate = float(row.get('cap_rate', 0)) if row.get('cap_rate') is not None else noi / float(row.get('property_value', 1))
                results.append({
                    'property_name': property_name,
                    'noi': noi,
                    'cap_rate': cap_rate
                })
            
            # Step 3: Rank Properties by Cap Rate
            results.sort(key=lambda x: x['cap_rate'], reverse=True)
            
            # Step 4: Identify Properties Below 5% Cap Rate
            below_5_percent = [prop for prop in results if prop['cap_rate'] < 0.05]
            
            # Print results to console
            logger.info("=== Property Cap Rate Ranking ===")
            for result in results:
                logger.info(f"{result['property_name']}: Cap Rate = {result['cap_rate']:.2%}")
            logger.info("=== Properties Below 5% Cap Rate ===")
            for result in below_5_percent:
                logger.info(f"{result['property_name']}: Cap Rate = {result['cap_rate']:.2%}")
            logger.info("=== End Results ===")
            
            return results, below_5_percent
        finally:
            conn.close()

# Main execution block
if __name__ == "__main__":
    executor = TaskExecutor()
    try:
        results, below_5_percent = executor.execute()
    except Exception as e:
        logger.error(f"Error: {e}")