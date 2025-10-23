#!/usr/bin/env python3
"""
Migration script to convert ProductFeature-Capability relationship from 1:n to m:n

This script:
1. Creates the new product_feature_capabilities association table
2. Migrates existing relationships to the new table
3. Removes the old product_feature_id column from capabilities table
"""

import os
import sys
import sqlite3
from datetime import datetime

def run_migration():
    """Run the migration to convert to many-to-many relationship"""
    
    db_path = os.path.join('instance', 'database.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Creating fresh database with new schema.")
        return True
    
    print(f"Starting migration at {datetime.now()}")
    print(f"Database path: {db_path}")
    
    # Create backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating backup: {backup_path}")
    
    try:
        # Create backup
        import shutil
        shutil.copy2(db_path, backup_path)
        print("✅ Backup created successfully")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(capabilities)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'product_feature_id' not in columns:
            print("✅ Migration already completed - product_feature_id column not found")
            conn.close()
            return True
            
        # Check if new table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_feature_capabilities'")
        if cursor.fetchone():
            print("✅ Association table already exists")
        else:
            # Create the new association table
            print("📋 Creating product_feature_capabilities association table...")
            cursor.execute("""
                CREATE TABLE product_feature_capabilities (
                    product_feature_id INTEGER NOT NULL,
                    capability_id INTEGER NOT NULL,
                    PRIMARY KEY (product_feature_id, capability_id),
                    FOREIGN KEY (product_feature_id) REFERENCES product_features(id),
                    FOREIGN KEY (capability_id) REFERENCES capabilities(id)
                )
            """)
            print("✅ Association table created")
        
        # Migrate existing relationships
        print("📋 Migrating existing relationships...")
        cursor.execute("""
            SELECT id, product_feature_id 
            FROM capabilities 
            WHERE product_feature_id IS NOT NULL
        """)
        
        relationships = cursor.fetchall()
        migrated_count = 0
        
        for capability_id, product_feature_id in relationships:
            # Check if relationship already exists
            cursor.execute("""
                SELECT 1 FROM product_feature_capabilities 
                WHERE product_feature_id = ? AND capability_id = ?
            """, (product_feature_id, capability_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO product_feature_capabilities (product_feature_id, capability_id)
                    VALUES (?, ?)
                """, (product_feature_id, capability_id))
                migrated_count += 1
        
        print(f"✅ Migrated {migrated_count} relationships")
        
        # Create new capabilities table without product_feature_id
        print("📋 Creating new capabilities table structure...")
        
        cursor.execute("""
            CREATE TABLE capabilities_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                success_criteria TEXT NOT NULL,
                vehicle_platform_id INTEGER,
                planned_start_date DATE,
                planned_end_date DATE,
                tmos TEXT,
                progress_relative_to_tmos FLOAT DEFAULT 0.0,
                document_url VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_platform_id) REFERENCES vehicle_platforms(id)
            )
        """)
        
        # Copy data to new table (excluding product_feature_id)
        cursor.execute("""
            INSERT INTO capabilities_new (
                id, name, success_criteria, vehicle_platform_id, 
                planned_start_date, planned_end_date, tmos, 
                progress_relative_to_tmos, document_url, created_at
            )
            SELECT 
                id, name, success_criteria, vehicle_platform_id,
                planned_start_date, planned_end_date, tmos,
                progress_relative_to_tmos, document_url, created_at
            FROM capabilities
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE capabilities")
        cursor.execute("ALTER TABLE capabilities_new RENAME TO capabilities")
        
        print("✅ Updated capabilities table structure")
        
        # Commit all changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify migration
        print("📋 Verifying migration...")
        cursor.execute("SELECT COUNT(*) FROM product_feature_capabilities")
        relationship_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM capabilities")
        capability_count = cursor.fetchone()[0]
        
        print(f"✅ Verification complete:")
        print(f"   - {capability_count} capabilities")
        print(f"   - {relationship_count} product feature relationships")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
        # Restore backup if it exists
        if os.path.exists(backup_path):
            print(f"🔄 Restoring backup from {backup_path}")
            shutil.copy2(backup_path, db_path)
            print("✅ Backup restored")
        
        return False

if __name__ == "__main__":
    print("=== ProductFeature-Capability Relationship Migration ===")
    print("Converting from 1:n to m:n relationship")
    print()
    
    success = run_migration()
    
    if success:
        print()
        print("🎉 Migration completed successfully!")
        print("The ProductFeature-Capability relationship is now many-to-many.")
        print()
        print("Next steps:")
        print("1. Restart your Flask application")
        print("2. Verify that capabilities can now be associated with multiple product features")
        print("3. Test the add/edit capability forms")
    else:
        print()
        print("💥 Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)