#!/usr/bin/env python3
"""
Migration script to convert vehicle_type string fields to vehicle_platform_id foreign keys
"""

from app import app, db, ProductFeature, TechnicalFunction, Capabilities, VehiclePlatform
from sqlalchemy import text

def migrate_vehicle_types():
    """Migrate from vehicle_type strings to vehicle_platform_id foreign keys"""
    
    with app.app_context():
        print("🔄 Starting migration: vehicle_type to vehicle_platform_id")
        
        # Check if migration is needed by looking for old columns
        try:
            # Try to access old columns to see if they exist
            db.session.execute(text("SELECT vehicle_type FROM product_features LIMIT 1"))
            print("✅ Old schema detected - migration needed")
        except Exception:
            print("ℹ️  New schema already in place - migration not needed")
            return
        
        # Step 1: Create default vehicle platforms if they don't exist
        print("📋 Creating default vehicle platforms...")
        
        default_platforms = [
            {'name': 'Truck Platform', 'vehicle_type': 'truck', 'description': 'Heavy-duty truck platform for cargo transport'},
            {'name': 'Van Platform', 'vehicle_type': 'van', 'description': 'Light commercial vehicle platform'},
            {'name': 'Car Platform', 'vehicle_type': 'car', 'description': 'Passenger car platform'},
            {'name': 'Generic Platform', 'vehicle_type': 'generic', 'description': 'Generic vehicle platform'}
        ]
        
        platform_mapping = {}
        
        for platform_data in default_platforms:
            platform = VehiclePlatform.query.filter_by(name=platform_data['name']).first()
            if not platform:
                platform = VehiclePlatform(
                    name=platform_data['name'],
                    vehicle_type=platform_data['vehicle_type'],
                    description=platform_data['description']
                )
                db.session.add(platform)
                print(f"  ➕ Created: {platform_data['name']}")
            
            platform_mapping[platform_data['vehicle_type']] = platform
        
        db.session.commit()
        
        # Step 2: Add new columns if they don't exist
        print("🔧 Adding new foreign key columns...")
        
        try:
            # Add vehicle_platform_id to ProductFeature
            db.session.execute(text("ALTER TABLE product_features ADD COLUMN vehicle_platform_id INTEGER"))
            print("  ➕ Added vehicle_platform_id to product_features")
        except Exception:
            print("  ℹ️  vehicle_platform_id already exists in product_features")
        
        try:
            # Add vehicle_platform_id to TechnicalFunction
            db.session.execute(text("ALTER TABLE technical_functions ADD COLUMN vehicle_platform_id INTEGER"))
            print("  ➕ Added vehicle_platform_id to technical_functions")
        except Exception:
            print("  ℹ️  vehicle_platform_id already exists in technical_functions")
        
        try:
            # Add vehicle_platform_id to Capabilities
            db.session.execute(text("ALTER TABLE capabilities ADD COLUMN vehicle_platform_id INTEGER"))
            print("  ➕ Added vehicle_platform_id to capabilities")
        except Exception:
            print("  ℹ️  vehicle_platform_id already exists in capabilities")
        
        db.session.commit()
        
        # Step 3: Migrate data for ProductFeatures
        print("📊 Migrating ProductFeature data...")
        product_features = ProductFeature.query.all()
        
        for pf in product_features:
            try:
                # Get the old vehicle_type value
                old_type = db.session.execute(text("SELECT vehicle_type FROM product_features WHERE id = :id"), {"id": pf.id}).fetchone()
                if old_type and old_type[0]:
                    vehicle_type = old_type[0]
                    platform = platform_mapping.get(vehicle_type, platform_mapping['generic'])
                    
                    # Update with new foreign key
                    db.session.execute(text("UPDATE product_features SET vehicle_platform_id = :platform_id WHERE id = :id"), 
                                     {"platform_id": platform.id, "id": pf.id})
                    print(f"  ✅ Updated ProductFeature '{pf.name}': {vehicle_type} -> {platform.name}")
            except Exception as e:
                print(f"  ⚠️  Error migrating ProductFeature {pf.name}: {e}")
        
        # Step 4: Migrate data for TechnicalFunctions
        print("📊 Migrating TechnicalFunction data...")
        technical_functions = TechnicalFunction.query.all()
        
        for tf in technical_functions:
            try:
                # Get the old vehicle_type value
                old_type = db.session.execute(text("SELECT vehicle_type FROM technical_functions WHERE id = :id"), {"id": tf.id}).fetchone()
                if old_type and old_type[0]:
                    vehicle_type = old_type[0]
                    platform = platform_mapping.get(vehicle_type, platform_mapping['generic'])
                    
                    # Update with new foreign key
                    db.session.execute(text("UPDATE technical_functions SET vehicle_platform_id = :platform_id WHERE id = :id"), 
                                     {"platform_id": platform.id, "id": tf.id})
                    print(f"  ✅ Updated TechnicalFunction '{tf.name}': {vehicle_type} -> {platform.name}")
            except Exception as e:
                print(f"  ⚠️  Error migrating TechnicalFunction {tf.name}: {e}")
        
        # Step 5: Migrate data for Capabilities
        print("📊 Migrating Capabilities data...")
        capabilities = Capabilities.query.all()
        
        for cap in capabilities:
            try:
                # Get the old vehicle_type value
                old_type = db.session.execute(text("SELECT vehicle_type FROM capabilities WHERE id = :id"), {"id": cap.id}).fetchone()
                if old_type and old_type[0]:
                    vehicle_type = old_type[0]
                    platform = platform_mapping.get(vehicle_type, platform_mapping['generic'])
                    
                    # Update with new foreign key
                    db.session.execute(text("UPDATE capabilities SET vehicle_platform_id = :platform_id WHERE id = :id"), 
                                     {"platform_id": platform.id, "id": cap.id})
                    print(f"  ✅ Updated Capability '{cap.name}': {vehicle_type} -> {platform.name}")
            except Exception as e:
                print(f"  ⚠️  Error migrating Capability {cap.name}: {e}")
        
        db.session.commit()
        
        # Step 6: Drop old columns (commented out for safety)
        print("🗑️  Old vehicle_type columns can be dropped manually if needed:")
        print("     ALTER TABLE product_features DROP COLUMN vehicle_type;")
        print("     ALTER TABLE technical_functions DROP COLUMN vehicle_type;")
        print("     ALTER TABLE capabilities DROP COLUMN vehicle_type;")
        
        print("✅ Migration completed successfully!")
        print("📋 Summary:")
        print(f"   - Created {len(default_platforms)} vehicle platforms")
        print(f"   - Migrated {len(product_features)} product features")
        print(f"   - Migrated {len(technical_functions)} technical functions")
        print(f"   - Migrated {len(capabilities)} capabilities")

if __name__ == '__main__':
    migrate_vehicle_types()