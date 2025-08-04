#!/usr/bin/env python3
"""
Startup script for the Sales Tracker application.
This script ensures all data files are properly initialized before starting the Flask app.
"""
import os
import json
from app import app, initialize_data_files

def main():
    """Main function to start the application"""
    print("🚀 Starting Sales Tracker Application...")
    print("=" * 50)
    
    # Initialize data files
    print("📁 Initializing data files...")
    initialize_data_files()
    
    # Check if all required files exist
    required_files = [
        'data/sales.json',
        'data/pending_orders.json', 
        'data/investment.json',
        'data/items.json',
        'data/users.json'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} - Missing!")
    
    print("\n🌐 Starting Flask web server...")
    print("   Access the application at: http://localhost:5000")
    print("   Admin credentials:")
    print("     Username: 01-135231-091")
    print("     Password: ali2525W")
    print("   OR")
    print("     Username: 01-135231-041") 
    print("     Password: ali2525W")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

if __name__ == '__main__':
    main()
