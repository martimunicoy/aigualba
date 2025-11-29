-- Development/Testing database initialization script
-- This script creates the necessary tables and includes DUMMY DATA for testing purposes
-- USE ONLY FOR DEVELOPMENT - NOT FOR PRODUCTION

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

-- Development parameters
INSERT INTO parameters (name, value) VALUES
('pH', '7.0'),
('Temperature', '25.0'),
('environment', 'development'),
('test_mode', 'true');

-- DUMMY SAMPLE DATA FOR TESTING - DO NOT USE IN PRODUCTION
INSERT INTO mostres (data, punt_mostreig, temperatura, ph, conductivitat_20c, terbolesa, color, olor, sabor, clor_lliure, clor_total, recompte_escherichia_coli, recompte_enterococ, recompte_microorganismes_aerobis_22c, recompte_coliformes_totals, acid_monocloroacetic, acid_dicloroacetic, acid_tricloroacetic, acid_monobromoacetic, acid_dibromoacetic, validated) VALUES
('2024-11-25', 'Dipòsit Vell Can Figueres', 20.5, 7.2, 250.0, 0.5, 5.0, 2.0, 2.0, 0.5, 0.8, 0.0, 0.0, 100.0, 0.0, 1.0, 2.0, 1.5, 0.5, 0.3, TRUE),
('2024-11-24', 'Font de la Plaça', 21.0, 7.1, 280.0, 0.3, 4.5, 1.5, 1.8, 0.6, 0.9, 0.0, 0.0, 95.0, 0.0, 0.8, 1.8, 1.2, 0.4, 0.2, TRUE),
('2024-11-23', 'Dipòsit Nou Can Figueres', 19.8, 7.3, 245.0, 0.4, 5.2, 2.1, 2.2, 0.4, 0.7, 0.0, 0.0, 110.0, 0.0, 1.1, 2.1, 1.4, 0.6, 0.4, TRUE),
('2024-11-22', 'Font Masia Can Figueres', 20.2, 7.0, 260.0, 0.6, 4.8, 1.9, 2.0, 0.5, 0.8, 0.0, 0.0, 105.0, 0.0, 0.9, 1.9, 1.3, 0.5, 0.3, TRUE),
('2024-11-21', 'Dipòsit Royal Park 1', 21.5, 7.2, 275.0, 0.2, 4.2, 1.6, 1.7, 0.7, 1.0, 0.0, 0.0, 90.0, 0.0, 1.2, 2.2, 1.6, 0.7, 0.5, TRUE);

-- Visits tracking table
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    page VARCHAR(100) NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample visit data for the last 30 days
INSERT INTO visits (page, user_agent, ip_address, timestamp) VALUES
('home', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.100', NOW() - INTERVAL '1 hour'),
('browse', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '192.168.1.101', NOW() - INTERVAL '2 hours'),
('submit', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '192.168.1.102', NOW() - INTERVAL '3 hours'),
('home', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)', '192.168.1.103', NOW() - INTERVAL '1 day'),
('browse', 'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0', '192.168.1.104', NOW() - INTERVAL '1 day'),
('home', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.105', NOW() - INTERVAL '2 days'),
('admin', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '192.168.1.106', NOW() - INTERVAL '2 days'),
('browse', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.107', NOW() - INTERVAL '3 days'),
('submit', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101', '192.168.1.108', NOW() - INTERVAL '4 days'),
('home', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '192.168.1.109', NOW() - INTERVAL '5 days'),
('browse', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.110', NOW() - INTERVAL '6 days'),
('home', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)', '192.168.1.111', NOW() - INTERVAL '7 days'),
('admin', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '192.168.1.112', NOW() - INTERVAL '8 days'),
('browse', 'Mozilla/5.0 (Android 12; Mobile; rv:91.0) Gecko/91.0', '192.168.1.113', NOW() - INTERVAL '9 days'),
('home', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.114', NOW() - INTERVAL '10 days'),
('submit', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '192.168.1.115', NOW() - INTERVAL '15 days'),
('browse', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '192.168.1.116', NOW() - INTERVAL '20 days'),
('home', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '192.168.1.117', NOW() - INTERVAL '25 days'),
('browse', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)', '192.168.1.118', NOW() - INTERVAL '28 days'),
('home', 'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0', '192.168.1.119', NOW() - INTERVAL '30 days');

-- Create indexes for better performance (same as production)
CREATE INDEX IF NOT EXISTS idx_mostres_data ON mostres(data DESC);
CREATE INDEX IF NOT EXISTS idx_mostres_punt_mostreig ON mostres(punt_mostreig);
CREATE INDEX IF NOT EXISTS idx_mostres_created_at ON mostres(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_parameters_name ON parameters(name);
CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON visits(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page ON visits(page);