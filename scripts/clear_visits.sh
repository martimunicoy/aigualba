#!/bin/bash

# Script to clear all visits from the database
# This script removes all records from the visits table and resets the ID sequence

# Load environment variables
source .env

echo "=== AIGUALBA VISITS CLEANER ==="
echo "Timestamp: $(date -Iseconds)"

# Check if database is accessible
if ! docker exec aigualba_db_1 pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo "ERROR: Database is not accessible"
    exit 1
fi

echo "✓ Database connection successful"

# Get visits summary
echo ""
echo "=== VISITS SUMMARY ==="

# Get total count
TOTAL_VISITS=$(docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM visits;" 2>/dev/null | xargs)

if [ "$TOTAL_VISITS" = "0" ] || [ -z "$TOTAL_VISITS" ]; then
    echo "No visits found in the database."
    exit 0
fi

echo "Total visits: $TOTAL_VISITS"

# Get visits by page
echo ""
echo "Visits by page:"
docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT '  ' || page || ': ' || COUNT(*) || ' visits' 
    FROM visits 
    GROUP BY page 
    ORDER BY COUNT(*) DESC;
" -t 2>/dev/null | grep -v '^$'

# Get date range
echo ""
echo "Date range:"
docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT '  First visit: ' || MIN(timestamp) || E'\\n' || '  Last visit: ' || MAX(timestamp) 
    FROM visits;
" -t 2>/dev/null | grep -v '^$'

# Get unique visitors
UNIQUE_VISITORS=$(docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "
    SELECT COUNT(DISTINCT ip_address) 
    FROM visits 
    WHERE ip_address IS NOT NULL AND ip_address != '';
" 2>/dev/null | xargs)

echo "  Unique visitors (by IP): $UNIQUE_VISITORS"
echo "======================="

echo ""
echo "======================="

# Ask for confirmation
echo -n "Are you sure you want to delete all $TOTAL_VISITS visits? (yes/no): "
read -r response

if [ "$response" != "yes" ] && [ "$response" != "y" ]; then
    echo "Operation cancelled."
    exit 0
fi

# Delete all visits and reset sequence
echo "Deleting all visits..."
docker exec -i aigualba_db_1 psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    DELETE FROM visits;
    ALTER SEQUENCE visits_id_seq RESTART WITH 1;
    SELECT 'Successfully deleted ' || $TOTAL_VISITS || ' visits from the database.';
    SELECT 'Visit ID sequence has been reset.';
" 2>/dev/null | grep -E "(Successfully|Visit ID)" | sed 's/^[ ]*//g'

echo ""
echo "Operation completed."