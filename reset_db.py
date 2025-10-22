#!/usr/bin/env python3
"""
Database reset script for Product Feature Readiness Database

Usage:
  ./venv/bin/python reset_db.py                    - Creates empty database
  ./venv/bin/python reset_db.py --with-sample-data - Creates database with sample data

This script will drop all tables and recreate them with the updated schema.
"""

import os
from app import app, db
from sample_data import initialize_sample_data

def reset_database(with_sample_data=False):
    """Drop all tables and recreate with updated schema"""
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating tables with updated schema...")
        db.create_all()
        
        if with_sample_data:
            print("Initializing with sample data...")
            initialize_sample_data()
            print("Database reset complete with sample data!")
        else:
            print("Database reset complete - empty database ready!")
            print("To add sample data, run: ./venv/bin/python -c \"from sample_data import initialize_sample_data; from app import app; app.app_context().push(); initialize_sample_data()\"")

if __name__ == '__main__':
    import sys
    
    # Check command line arguments
    with_sample_data = False
    if len(sys.argv) > 1 and sys.argv[1] == '--with-sample-data':
        with_sample_data = True
    
    # Remove existing database file if it exists
    db_path = 'instance/product_readiness.db'
    if os.path.exists(db_path):
        print(f"Removing existing database file: {db_path}")
        os.remove(db_path)
    
    reset_database(with_sample_data)