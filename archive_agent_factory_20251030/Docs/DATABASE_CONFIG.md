# Database Configuration

**Meta-Agent uses the DSCR POC database from the WinPrA Agentic POC project.**

---

## Database Details

**Source Project**: WinPrA Agentic POC  
**Database Name**: `dscr_poc_db`  
**Database Type**: PostgreSQL 15  
**Connection**: Docker container  

### Connection Parameters

```
Host: localhost
Port: 5433
Database: dscr_poc_db
Username: dscr_user
Password: dscr_password_change_me
```

### Connection String

```
DATABASE_URL=postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db
```

---

## Setup Instructions

### 1. Start the Database

The database runs in Docker. Start it from the WinPrA Agentic POC project:

```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose up -d postgres
```

### 2. Verify Database is Running

```bash
# Check Docker containers
docker ps | grep dscr_poc_postgres

# Expected output:
# dscr_poc_postgres   postgres:15-alpine   Up X minutes   0.0.0.0:5433->5432/tcp
```

### 3. Test Connection

```bash
# Using psql
psql -h localhost -p 5433 -U dscr_user -d dscr_poc_db

# When prompted, enter password: dscr_password_change_me
```

### 4. Verify Data

```sql
-- Check tables
\dt

-- Expected tables:
--   properties
--   financial_metrics
--   simulation_runs
--   formula_library

-- Check sample data
SELECT COUNT(*) FROM properties;
SELECT COUNT(*) FROM financial_metrics;
```

---

## Database Schema

### Main Tables

#### **properties**
- `id` - Property ID
- `property_name` - Property name
- `location` - Property location
- `property_value` - Property value
- `loan_amount` - Loan amount
- `interest_rate` - Interest rate
- `loan_term_years` - Loan term in years

#### **financial_metrics**
- `id` - Metric ID
- `property_id` - Reference to property
- `year` - Year
- `quarter` - Quarter
- `annual_noi` - Annual Net Operating Income
- `annual_debt_service` - Annual Debt Service
- `current_dscr` - Current DSCR value
- `cap_rate` - Capitalization rate
- `ltv_ratio` - Loan-to-Value ratio

#### **simulation_runs**
- Run history and results

#### **formula_library**
- Pre-approved custom formulas

---

## Configuration in Meta-Agent

### .env File

Create `.env` file in project root (or run `./setup_env.sh`):

```bash
# Database Configuration (REQUIRED)
DATABASE_URL=postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db
```

### Verification

Run the setup test to verify connection:

```bash
python test_setup.py
```

Expected output:
```
Testing PostgreSQL connection...
✓ PostgreSQL connected successfully
  Properties in database: 10
```

---

## Troubleshooting

### Connection Refused

**Error**: `Connection refused` or `could not connect to server`

**Solutions**:
1. Check if Docker container is running:
   ```bash
   docker ps | grep dscr_poc_postgres
   ```

2. Start the database:
   ```bash
   cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
   docker-compose up -d postgres
   ```

3. Wait for database to be ready (check health):
   ```bash
   docker logs dscr_poc_postgres
   ```

### Wrong Port

**Error**: `Connection to localhost:5432 refused`

**Solution**: The database runs on port **5433** (not 5432). Update your connection string.

### Authentication Failed

**Error**: `authentication failed for user "dscr_user"`

**Solution**: Ensure you're using the correct password: `dscr_password_change_me`

### Database Does Not Exist

**Error**: `database "dscr_poc_db" does not exist`

**Solution**: 
1. Database is created automatically by docker-compose
2. Restart the container:
   ```bash
   cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
   docker-compose down
   docker-compose up -d postgres
   ```

### No Data in Tables

**Error**: `SELECT COUNT(*) FROM properties` returns 0

**Solution**: Load the sample data:
```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
python database/seeds/load_data.py
```

---

## Why This Database?

The DSCR POC database contains:

✅ **Sample Property Data** - 10 properties with financial metrics  
✅ **Financial Metrics** - Annual NOI, debt service, DSCR, etc.  
✅ **Test Cases** - Including challenging scenarios  
✅ **Formula Library** - Pre-approved custom formulas  
✅ **Proven Schema** - Already tested with DSCR calculations  

This provides realistic data for testing the Meta-Agent's ability to generate agents that work with real financial data.

---

## Example Usage in Generated Agents

When Meta-Agent generates a DataAgent, it will use these connection details:

```python
# Generated DataAgent will connect to:
DATABASE_URL = "postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db"

# And query tables like:
SELECT * FROM properties WHERE id = 5;
SELECT * FROM financial_metrics WHERE property_id = 5;
```

---

## Security Note

⚠️ **Default Credentials**: The database uses default credentials suitable for local development.

For production use:
1. Change the password in docker-compose.yml
2. Update DATABASE_URL in .env
3. Use environment variables for sensitive data
4. Enable SSL/TLS for connections

---

**Database Status**: ✅ Configured  
**Connection**: WinPrA Agentic POC → DSCR POC Database (PostgreSQL 15)  
**Port**: 5433  
**Ready for**: Agent generation and testing

