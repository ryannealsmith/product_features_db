#!/usr/bin/env python3
"""
Database reset script for Product Feature Readiness Database
This script will drop all tables and recreate them with the updated schema.
"""

import os
from app import app, db
from sample_data import initialize_sample_data

def reset_database():
    """Drop all tables and recreate with updated schema"""
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating tables with updated schema...")
        db.create_all()
        
        print("Initializing with sample data...")
        initialize_sample_data()
        
        print("Database reset complete!")

if __name__ == '__main__':
    # Remove existing database file if it exists
    db_path = 'instance/product_readiness.db'
    if os.path.exists(db_path):
        print(f"Removing existing database file: {db_path}")
        os.remove(db_path)
    
    reset_database()