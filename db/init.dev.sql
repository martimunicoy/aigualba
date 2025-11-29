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

-- Create indexes for better performance (same as production)
CREATE INDEX IF NOT EXISTS idx_mostres_data ON mostres(data DESC);
CREATE INDEX IF NOT EXISTS idx_mostres_punt_mostreig ON mostres(punt_mostreig);
CREATE INDEX IF NOT EXISTS idx_mostres_created_at ON mostres(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_parameters_name ON parameters(name);