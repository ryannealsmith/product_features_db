#!/usr/bin/env python3
"""
Database migration to add capability_id column to readiness_assessments table
"""
from app import app, db
from sqlalchemy import text, inspect

def migrate_database():
    """Add capability_id column to readiness_assessments table"""
    with app.app_context():
        # Check if column already exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('readiness_assessments')]
        
        if 'capability_id' in columns:
            print("capability_id column already exists in readiness_assessments table")
            return
        
        try:
            # Add the capability_id column
            with db.engine.connect() as connection:
                # Start a transaction
                trans = connection.begin()
                try:
                    print("Adding capability_id column to readiness_assessments table...")
                    connection.execute(text('ALTER TABLE readiness_assessments ADD COLUMN capability_id INTEGER'))
                    
                    # Add foreign key constraint (SQLite doesn't support adding FK constraints after table creation,
                    # but we can still add the column and rely on SQLAlchemy relationships)
                    print("Successfully added capability_id column")
                    
                    trans.commit()
                    print("Database migration completed successfully!")
                    
                except Exception as e:
                    trans.rollback()
                    raise e
                    
        except Exception as e:
            print(f"Error during migration: {e}")
            raise

if __name__ == "__main__":
    migrate_database()