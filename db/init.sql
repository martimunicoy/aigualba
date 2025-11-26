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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO parameters (name, value) VALUES
('pH', '7.0'),
('Temperature', '25.0');
