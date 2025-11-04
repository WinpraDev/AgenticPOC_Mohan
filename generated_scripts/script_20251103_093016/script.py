#!/usr/bin/env python3
import os
from loguru import logger
from flask import Flask, render_template_string

# Configuration from environment variables
CONFIG = {
    'db_url': os.getenv('DATABASE_URL', ''),
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', '8080'))
}

# HTML templates as string constants
DB_NOT_CONFIGURED_TEMPLATE = """
<div style="background-color: yellow; padding: 20px; border-radius: 5px;">
    <h3>Database not configured</h3>
    <p>Edit .env file and add DATABASE_URL.</p>
    <p>Example: DATABASE_URL=postgresql://user:password@localhost/dbname</p>
    <p>Restart the application after updating .env.</p>
</div>
"""

ERROR_TEMPLATE = """
<div style="background-color: red; padding: 20px; border-radius: 5px;">
    <h3>Error</h3>
    <p>{{error}}</p>
    <p>Check if the database is running, verify credentials, and check the schema.</p>
</div>
"""

EMPTY_DATABASE_TEMPLATE = """
<div style="background-color: blue; padding: 20px; border-radius: 5px;">
    <h3>Database is connected but empty</h3>
    <pre>INSERT INTO properties (property_name, rental_income) VALUES ('Sample Property', 1000);</pre>
</div>
"""

# Flask app
app = Flask(__name__)

class TaskExecutor:
    def __init__(self):
        pass
    
    def get_connection(self):
        if not CONFIG['db_url']:
            raise ValueError("DATABASE_URL not configured")
        return psycopg2.connect(CONFIG['db_url'])
    
    def execute(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Query all properties and financial metrics
            query = "SELECT * FROM properties p JOIN financial_metrics fm ON p.property_id = fm.property_id"
            cursor.execute(query)
            
            properties = []
            for row in cursor.fetchall():
                property_name = row.get('property_name', 'Unknown')
                rental_income = float(row.get('rental_income', 0))
                annual_debt_service = float(row.get('annual_debt_service', 0))
                
                # Calculate metrics
                noi = rental_income - annual_debt_service
                dscr = noi / annual_debt_service if annual_debt_service != 0 else float('inf')
                property_value = noi * 1.5  # Example calculation
                ltv_ratio = annual_debt_service / property_value if property_value != 0 else float('inf')
                
                # Color code DSCR
                dscr_color = 'green' if dscr >= 1.2 else ('yellow' if dscr >= 0.8 else 'red')
                
                properties.append({
                    'property_name': property_name,
                    'noi': noi,
                    'annual_debt_service': annual_debt_service,
                    'dscr': dscr,
                    'property_value': property_value,
                    'ltv_ratio': ltv_ratio,
                    'dscr_color': dscr_color
                })
            
            return properties
        
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            conn.close()

# For Flask apps:
@app.route('/')
def index():
    if not CONFIG['db_url']:
        return render_template_string(DB_NOT_CONFIGURED_TEMPLATE)
    
    try:
        executor = TaskExecutor()
        results = executor.execute()
        
        # Sort properties by DSCR
        results.sort(key=lambda x: x['dscr'], reverse=True)
        
        return render_template_string(RESULTS_TEMPLATE, results=results)
    except Exception as e:
        logger.error(f"Error: {e}")
        return render_template_string(ERROR_TEMPLATE, error=str(e))

# HTML template for results
RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Property Dashboard</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        .green { color: green; }
        .yellow { color: yellow; }
        .red { color: red; }
    </style>
</head>
<body>
    <h1>Property Dashboard</h1>
    {% if not results %}
        {{ EMPTY_DATABASE_TEMPLATE }}
    {% else %}
        <table>
            <tr>
                <th>Property Name</th>
                <th>NOI</th>
                <th>Annual Debt Service</th>
                <th>DSCR</th>
                <th>Property Value</th>
                <th>LTV Ratio</th>
            </tr>
            {% for result in results %}
            <tr style="color: {{ result.dscr_color }}">
                <td>{{ result.property_name }}</td>
                <td>{{ result.noi | floatformat:2 }}</td>
                <td>{{ result.annual_debt_service | floatformat:2 }}</td>
                <td>{{ result.dscr | floatformat:2 }}</td>
                <td>{{ result.property_value | floatformat:2 }}</td>
                <td>{{ result.ltv_ratio | floatformat:2 }}</td>
            </tr>
            {% endfor %}
        </table>
    {% endif %}
</body>
</html>
"""

# Main execution block
if __name__ == '__main__':
    if not CONFIG['db_url']:
        logger.info(DB_NOT_CONFIGURED_TEMPLATE)
    else:
        try:
            executor = TaskExecutor()
            results = executor.execute()
            
            # Sort properties by DSCR
            results.sort(key=lambda x: x['dscr'], reverse=True)
            
            logger.info("Calculated results:")
            for result in results:
                logger.info(f"{result['property_name']}: NOI={result['noi']:,.2f}, ADS={result['annual_debt_service']:,.2f}, DSCR={result['dscr']:,.2f}, Property Value={result['property_value']:,.2f}, LTV Ratio={result['ltv_ratio']:,.2f}")
            
            app.run(host=CONFIG['host'], port=CONFIG['port'])
        except Exception as e:
            logger.error(f"Error: {e}")