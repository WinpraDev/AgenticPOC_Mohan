-- ============================================================
-- DSCR POC DATABASE SCHEMA - EXACT REPLICA
-- ============================================================
-- Extracted from existing dscr_poc_db database
-- Version: 1.0
-- Created: November 2025
-- ============================================================

-- Drop existing objects
DROP VIEW IF EXISTS v_property_financials CASCADE;
DROP TABLE IF EXISTS financial_metrics CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP FUNCTION IF EXISTS get_dscr_interpretation(NUMERIC);
DROP FUNCTION IF EXISTS calculate_dscr(NUMERIC, NUMERIC);
DROP FUNCTION IF EXISTS calculate_cap_rate(NUMERIC, NUMERIC);
DROP FUNCTION IF EXISTS calculate_ltv(NUMERIC, NUMERIC);
DROP FUNCTION IF EXISTS update_updated_at_column();

-- ============================================================
-- PROPERTIES TABLE
-- ============================================================
CREATE TABLE properties (
    property_id SERIAL PRIMARY KEY,
    property_name VARCHAR(255) NOT NULL UNIQUE,
    property_address VARCHAR(500),
    property_type VARCHAR(100),
    total_gla_sqft NUMERIC,
    year_built INTEGER,
    last_renovation_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE properties IS 'Commercial real estate properties in the portfolio';
COMMENT ON COLUMN properties.property_id IS 'Unique identifier for each property';
COMMENT ON COLUMN properties.total_gla_sqft IS 'Total Gross Leasable Area in square feet';

-- ============================================================
-- FINANCIAL METRICS TABLE
-- ============================================================
CREATE TABLE financial_metrics (
    metric_id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    
    -- Income Components
    gross_rental_income NUMERIC(15,2),
    other_income NUMERIC(15,2),
    gross_operating_income NUMERIC(15,2),
    
    -- Expense Components
    operating_expenses NUMERIC(15,2),
    property_tax NUMERIC(15,2),
    insurance NUMERIC(15,2),
    utilities NUMERIC(15,2),
    maintenance NUMERIC(15,2),
    management_fees NUMERIC(15,2),
    
    -- Net Operating Income
    noi NUMERIC(15,2),
    
    -- Loan Information
    loan_amount NUMERIC(15,2),
    interest_rate NUMERIC(5,4),
    loan_term_years INTEGER,
    annual_debt_service NUMERIC(15,2),
    principal_payment NUMERIC(15,2),
    interest_payment NUMERIC(15,2),
    
    -- Property Valuation
    property_value NUMERIC(15,2),
    acquisition_cost NUMERIC(15,2),
    
    -- Financial Ratios
    dscr NUMERIC(10,4),
    ltv NUMERIC(5,4),
    cap_rate NUMERIC(5,4),
    
    -- Temporal Information
    calculation_date DATE,
    fiscal_year INTEGER,
    quarter INTEGER,
    
    -- Metadata
    data_source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

COMMENT ON TABLE financial_metrics IS 'Financial performance metrics for each property';
COMMENT ON COLUMN financial_metrics.noi IS 'Net Operating Income (GOI - Operating Expenses)';
COMMENT ON COLUMN financial_metrics.dscr IS 'Debt Service Coverage Ratio (NOI / Annual Debt Service)';
COMMENT ON COLUMN financial_metrics.ltv IS 'Loan-to-Value ratio';
COMMENT ON COLUMN financial_metrics.cap_rate IS 'Capitalization Rate';

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_properties_name ON properties(property_name);
CREATE INDEX idx_properties_type ON properties(property_type);
CREATE INDEX idx_financial_metrics_property ON financial_metrics(property_id);
CREATE INDEX idx_financial_metrics_date ON financial_metrics(calculation_date);
CREATE INDEX idx_financial_metrics_fiscal_year ON financial_metrics(fiscal_year);
CREATE INDEX idx_financial_metrics_dscr ON financial_metrics(dscr);

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- Function: calculate_cap_rate
CREATE OR REPLACE FUNCTION calculate_cap_rate(noi_value NUMERIC, property_val NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF property_val IS NULL OR property_val = 0 THEN
        RETURN NULL;
    END IF;
    RETURN ROUND(noi_value / property_val, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_cap_rate IS 'Calculate Capitalization Rate (NOI / Property Value)';

-- Function: calculate_dscr
CREATE OR REPLACE FUNCTION calculate_dscr(noi_value NUMERIC, debt_service NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF debt_service IS NULL OR debt_service = 0 THEN
        RETURN NULL;
    END IF;
    RETURN ROUND(noi_value / debt_service, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_dscr IS 'Calculate Debt Service Coverage Ratio';

-- Function: calculate_ltv
CREATE OR REPLACE FUNCTION calculate_ltv(loan_amt NUMERIC, property_val NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF property_val IS NULL OR property_val = 0 THEN
        RETURN NULL;
    END IF;
    RETURN ROUND(loan_amt / property_val, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_ltv IS 'Calculate Loan-to-Value ratio';

-- Function: get_dscr_interpretation
CREATE OR REPLACE FUNCTION get_dscr_interpretation(dscr_value NUMERIC)
RETURNS TEXT AS $$
BEGIN
    IF dscr_value IS NULL THEN
        RETURN 'N/A';
    ELSIF dscr_value < 1.0 THEN
        RETURN 'Poor (< 1.0)';
    ELSIF dscr_value >= 1.0 AND dscr_value < 1.25 THEN
        RETURN 'Fair (1.0-1.25)';
    ELSIF dscr_value >= 1.25 AND dscr_value < 1.5 THEN
        RETURN 'Good (1.25-1.5)';
    ELSIF dscr_value >= 1.5 AND dscr_value < 2.0 THEN
        RETURN 'Very Good (1.5-2.0)';
    ELSE
        RETURN 'Excellent (>= 2.0)';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION get_dscr_interpretation IS 'Get text interpretation of DSCR value';

-- Function: update_updated_at_column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TRIGGERS
-- ============================================================
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_metrics_updated_at
    BEFORE UPDATE ON financial_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VIEW: v_property_financials
-- ============================================================
CREATE OR REPLACE VIEW v_property_financials AS
SELECT 
    p.property_id,
    p.property_name,
    p.property_address,
    p.total_gla_sqft,
    fm.noi,
    fm.annual_debt_service,
    fm.dscr,
    get_dscr_interpretation(fm.dscr) AS dscr_rating,
    fm.ltv,
    fm.cap_rate,
    fm.property_value,
    fm.loan_amount,
    fm.interest_rate,
    fm.fiscal_year,
    fm.calculation_date
FROM properties p
LEFT JOIN financial_metrics fm ON p.property_id = fm.property_id;

COMMENT ON VIEW v_property_financials IS 'Combined property and financial metrics with DSCR interpretation';

-- ============================================================
-- GRANT PERMISSIONS
-- ============================================================
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_user WHERE usename = 'dscr_user') THEN
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dscr_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dscr_user;
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO dscr_user;
    END IF;
END
$$;

-- ============================================================
-- VERIFICATION
-- ============================================================
SELECT 'Schema created successfully' as status;

SELECT 'Table' as object_type, tablename as object_name 
FROM pg_tables WHERE schemaname = 'public'
UNION ALL
SELECT 'View' as object_type, viewname as object_name 
FROM pg_views WHERE schemaname = 'public'
UNION ALL
SELECT 'Function' as object_type, routine_name as object_name 
FROM information_schema.routines WHERE routine_schema = 'public'
ORDER BY object_type, object_name;

