#!/bin/bash

source .env
docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\copy (SELECT * FROM visits ORDER BY timestamp ASC) TO STDOUT WITH CSV HEADER" > visits.csv

