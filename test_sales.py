#!/usr/bin/env python3
"""
Test script to verify the sales functionality is working correctly.
"""
import json
import os
from app import app

def test_sales_functionality():
    """Test that the sales API endpoints are working correctly"""
    print("Testing sales functionality...")
    
    # Test that data files exist and are valid
    data_files = [
        'data/sales.json',
        'data/pending_orders.json',
        'data/investment.json',
        'data/items.json'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"✓ {file_path} is valid JSON")
            except json.JSONDecodeError as e:
                print(f"✗ {file_path} contains invalid JSON: {e}")
        else:
            print(f"✗ {file_path} does not exist")
    
    # Test the Flask app
    with app.test_client() as client:
        print("\nTesting API endpoints...")
        
        # Test items endpoint
        response = client.get('/api/items')
        if response.status_code == 200:
            print("✓ /api/items endpoint working")
        else:
            print(f"✗ /api/items endpoint failed with status {response.status_code}")
        
        # Test sales GET endpoint
        response = client.get('/api/sales')
        if response.status_code == 200:
            print("✓ /api/sales GET endpoint working")
        else:
            print(f"✗ /api/sales GET endpoint failed with status {response.status_code}")
        
        # Test sales POST endpoint with sample data
        sample_sales = [{
            'item': 'Golgappay 8 in Plate',
            'quantity': 1,
            'amount': 200,
            'options': ''
        }]
        
        response = client.post('/api/sales', 
                              json=sample_sales,
                              content_type='application/json')
        if response.status_code == 200:
            print("✓ /api/sales POST endpoint working")
        else:
            print(f"✗ /api/sales POST endpoint failed with status {response.status_code}")
            print(f"Response: {response.get_json()}")
        
        # Test summary endpoint
        response = client.get('/api/summary')
        if response.status_code == 200:
            print("✓ /api/summary endpoint working")
        else:
            print(f"✗ /api/summary endpoint failed with status {response.status_code}")
    
    print("\nTest complete!")

if __name__ == '__main__':
    test_sales_functionality()
