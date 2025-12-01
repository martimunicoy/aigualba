-- Production database initialization script
-- This script creates the necessary tables and structure for the Aigualba water quality monitoring system
-- WITHOUT any dummy/test data

CREATE TABLE IF NOT EXISTS parameters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mostres (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    punt_mostreig VARCHAR(255) NOT NULL,
    temperatura DECIMAL(5,2), -- en Celsius
    clor_lliure DECIMAL(10,4), -- mg Cl2/l
    clor_total DECIMAL(10,4), -- mg Cl2/l
    recompte_escherichia_coli DECIMAL(10,2), -- NPM/100 ml
    recompte_enterococ DECIMAL(10,2), -- NPM/100 ml
    recompte_microorganismes_aerobis_22c DECIMAL(15,2), -- ufc/1 ml
    recompte_coliformes_totals DECIMAL(10,2), -- NMP/100 ml
    conductivitat_20c DECIMAL(10,2), -- 148 uS/cm
    ph DECIMAL(4,2), -- unitat de pH
    terbolesa DECIMAL(10,2), -- UNF
    color DECIMAL(10,2), -- mg/l Pt-Co
    olor DECIMAL(10,2), -- index dilució a 25ºC
    sabor DECIMAL(10,2), -- index dilució a 25ºC
    acid_monocloroacetic DECIMAL(10,2), -- ug/l
    acid_dicloroacetic DECIMAL(10,2), -- ug/l
    acid_tricloroacetic DECIMAL(10,2), -- ug/l
    acid_monobromoacetic DECIMAL(10,2), -- ug/l
    acid_dibromoacetic DECIMAL(10,2), -- ug/l
    validated BOOLEAN DEFAULT FALSE, -- Whether the sample has been admin-validated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Essential system parameters (production-ready)
INSERT INTO parameters (name, value) VALUES
('system_version', '1.0.0'),
('last_maintenance', CURRENT_DATE::VARCHAR);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_mostres_data ON mostres(data DESC);
CREATE INDEX IF NOT EXISTS idx_mostres_punt_mostreig ON mostres(punt_mostreig);
CREATE INDEX IF NOT EXISTS idx_mostres_created_at ON mostres(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_parameters_name ON parameters(name);

-- Add comments to tables for documentation
COMMENT ON TABLE parameters IS 'System configuration parameters';
COMMENT ON TABLE mostres IS 'Water quality samples and measurements';

COMMENT ON COLUMN mostres.data IS 'Sample collection date';
COMMENT ON COLUMN mostres.punt_mostreig IS 'Sampling location';
COMMENT ON COLUMN mostres.temperatura IS 'Water temperature in Celsius';
COMMENT ON COLUMN mostres.ph IS 'pH value';
COMMENT ON COLUMN mostres.conductivitat_20c IS 'Conductivity at 20°C in μS/cm';
COMMENT ON COLUMN mostres.terbolesa IS 'Turbidity in NTU';
COMMENT ON COLUMN mostres.clor_lliure IS 'Free chlorine in mg Cl2/L';
COMMENT ON COLUMN mostres.clor_total IS 'Total chlorine in mg Cl2/L';
COMMENT ON COLUMN mostres.recompte_escherichia_coli IS 'E.coli count in NPM/100ml';
COMMENT ON COLUMN mostres.recompte_enterococ IS 'Enterococci count in NPM/100ml';
COMMENT ON COLUMN mostres.recompte_microorganismes_aerobis_22c IS 'Aerobic microorganisms count at 22°C in UFC/ml';
COMMENT ON COLUMN mostres.recompte_coliformes_totals IS 'Total coliforms count in NMP/100ml';
COMMENT ON COLUMN mostres.validated IS 'Whether the sample has been admin-validated for public display';

CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    page VARCHAR(100) NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for visits
CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON visits(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page ON visits(page);

COMMENT ON TABLE visits IS 'Page visit tracking for admin/dashboard analytics';
