# DSCR POC Database

PostgreSQL database for commercial real estate portfolio management.

## Quick Start

```bash
# Initialize database (one command)
cd database
bash init_database.sh
```

The database will be available at:
- **URL:** `postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db`
- **Port:** 5433 (to avoid conflict with local PostgreSQL)

## What's Included

### Tables
- `properties` - 10 commercial properties
- `financial_metrics` - Financial performance data

### Views
- `v_property_financials` - Combined property and financial data with DSCR ratings

### Functions
- `calculate_dscr(noi, debt_service)` - Calculate DSCR
- `calculate_cap_rate(noi, property_value)` - Calculate cap rate
- `calculate_ltv(loan_amount, property_value)` - Calculate LTV
- `get_dscr_interpretation(dscr_value)` - Get text rating for DSCR

## Docker Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker-compose logs -f

# Connect to database
docker exec -it dscr_poc_postgres psql -U dscr_user -d dscr_poc_db

# Restart database
docker-compose restart
```

## Sample Queries

```sql
-- View all properties with financials
SELECT * FROM v_property_financials;

-- Properties by DSCR rating
SELECT 
    property_name, 
    dscr, 
    get_dscr_interpretation(dscr) as rating
FROM v_property_financials
ORDER BY dscr DESC;

-- Portfolio summary
SELECT 
    COUNT(*) as total_properties,
    ROUND(AVG(dscr), 2) as avg_dscr,
    ROUND(AVG(cap_rate) * 100, 2) as avg_cap_rate_pct,
    SUM(noi) as total_noi,
    SUM(annual_debt_service) as total_debt_service
FROM financial_metrics;
```

## Files

- `schema/01_create_tables.sql` - Database schema
- `data/02_sample_data.sql` - Sample data (10 properties)
- `docker-compose.yml` - PostgreSQL container configuration
- `init_database.sh` - One-command database setup

