#!/usr/bin/env python3
"""
Sample data initialization script for Product Feature Readiness Database
This script adds sample data to an existing database.
"""

from app import app
from sample_data import initialize_sample_data

def add_sample_data():
    """Add sample data to the existing database"""
    with app.app_context():
        print("Adding sample data to database...")
        initialize_sample_data()
        print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data()