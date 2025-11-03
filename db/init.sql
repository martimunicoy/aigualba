CREATE TABLE IF NOT EXISTS parameters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    value VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO parameters (name, value) VALUES ('chlorine', '0.5 mg/L');
INSERT INTO parameters (name, value) VALUES ('ph', '7.2');
