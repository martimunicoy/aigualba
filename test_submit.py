#!/usr/bin/env python3
"""
Test script to validate the sample submission functionality
"""

import requests
import json
from datetime import date, datetime

# Test data for sample submission
test_sample = {
    "data": str(date.today()),
    "punt_mostreig": "Test Location - Dipòsit principal",
    "temperatura": 20.5,
    "ph": 7.2,
    "conductivitat_20c": 250.0,
    "terbolesa": 0.5,
    "color": 5.0,
    "olor": 2.0,
    "sabor": 2.0,
    "clor_lliure": 0.5,
    "clor_total": 0.8,
    "recompte_escherichia_coli": 0.0,
    "recompte_enterococ": 0.0,
    "recompte_microorganismes_aerobis_22c": 100.0,
    "recompte_coliformes_totals": 0.0,
    "acid_monocloroacetic": 1.0,
    "acid_dicloroacetic": 2.0,
    "acid_tricloroacetic": 1.5,
    "acid_monobromoacetic": 0.5,
    "acid_dibromoacetic": 0.3
}

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    print(f"Base URL: {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✓ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test parameters endpoint
    try:
        response = requests.get(f"{base_url}/api/parameters")
        print(f"✓ Parameters endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"  Found {len(response.json())} parameters")
    except Exception as e:
        print(f"✗ Parameters endpoint failed: {e}")
    
    # Test mostres GET endpoint
    try:
        response = requests.get(f"{base_url}/api/mostres")
        print(f"✓ Mostres GET endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} samples")
    except Exception as e:
        print(f"✗ Mostres GET endpoint failed: {e}")
    
    # Test sample submission
    try:
        response = requests.post(f"{base_url}/api/mostres", json=test_sample)
        print(f"✓ Sample submission: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Sample created with ID: {result.get('id')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Sample submission failed: {e}")
    
    return True

def validate_frontend_data():
    """Validate the data format expected by frontend"""
    from frontend.utils.helpers import validate_sample_data
    
    print("\nTesting frontend validation...")
    validation = validate_sample_data(test_sample)
    
    if validation['errors']:
        print("✗ Validation errors found:")
        for error in validation['errors']:
            print(f"  - {error}")
    else:
        print("✓ No validation errors")
    
    if validation['warnings']:
        print("⚠ Validation warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    else:
        print("✓ No validation warnings")

if __name__ == "__main__":
    print("=== Testing Aigualba Sample Submission ===\n")
    
    print("Test sample data:")
    print(json.dumps(test_sample, indent=2))
    print()
    
    # Test API
    test_api_endpoints()
    
    # Test frontend validation
    try:
        validate_frontend_data()
    except ImportError as e:
        print(f"⚠ Frontend validation test skipped: {e}")
    
    print("\n=== Test completed ===")