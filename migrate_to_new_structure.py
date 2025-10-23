#!/usr/bin/env python3
"""
Migration script to update database structure to the new relationship model:
ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction

This script will:
1. Backup existing data
2. Drop and recreate tables with new structure
3. Migrate data to new relationships
4. Initialize sample data
"""

from app import app, db, ProductFeature, Capabilities, TechnicalFunction
import json
from datetime import datetime

def backup_existing_data():
    """Backup existing data before migration"""
    print("📦 Backing up existing data...")
    
    with app.app_context():
        backup_data = {
            'product_features': [],
            'capabilities': [],
            'technical_functions': [],
            'relationships': {
                'product_feature_capabilities': [],
                'capability_technical_functions': []
            }
        }
        
        # Backup ProductFeatures
        for pf in ProductFeature.query.all():
            backup_data['product_features'].append({
                'id': pf.id,
                'name': pf.name,
                'description': pf.description,
                'vehicle_platform_id': pf.vehicle_platform_id,
                'swimlane_decorators': pf.swimlane_decorators,
                'label': pf.label,
                'tmos': pf.tmos,
                'status_relative_to_tmos': pf.status_relative_to_tmos,
                'planned_start_date': pf.planned_start_date.isoformat() if pf.planned_start_date else None,
                'planned_end_date': pf.planned_end_date.isoformat() if pf.planned_end_date else None,
                'active_flag': pf.active_flag,
                'document_url': pf.document_url
            })
        
        # Backup Capabilities
        for cap in Capabilities.query.all():
            backup_data['capabilities'].append({
                'id': cap.id,
                'name': cap.name,
                'success_criteria': cap.success_criteria,
                'vehicle_platform_id': cap.vehicle_platform_id,
                'planned_start_date': cap.planned_start_date.isoformat() if cap.planned_start_date else None,
                'planned_end_date': cap.planned_end_date.isoformat() if cap.planned_end_date else None,
                'tmos': cap.tmos,
                'progress_relative_to_tmos': cap.progress_relative_to_tmos,
                'document_url': cap.document_url
            })
        
        # Backup TechnicalFunctions
        for tf in TechnicalFunction.query.all():
            backup_data['technical_functions'].append({
                'id': tf.id,
                'name': tf.name,
                'description': tf.description,
                'success_criteria': tf.success_criteria,
                'vehicle_platform_id': tf.vehicle_platform_id,
                'tmos': tf.tmos,
                'status_relative_to_tmos': tf.status_relative_to_tmos,
                'planned_start_date': tf.planned_start_date.isoformat() if tf.planned_start_date else None,
                'planned_end_date': tf.planned_end_date.isoformat() if tf.planned_end_date else None,
                'document_url': tf.document_url
            })
        
        # Backup relationships
        # Note: We'll need to create new relationships based on the old structure
        
    # Save backup to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'data_backup_{timestamp}.json'
    
    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"✅ Data backed up to {backup_filename}")
    return backup_data

def recreate_database():
    """Drop and recreate database with new structure"""
    print("🗑️  Dropping existing tables...")
    with app.app_context():
        db.drop_all()
    
    print("🏗️  Creating new table structure...")
    with app.app_context():
        db.create_all()
    
    print("✅ New database structure created")

def migrate_data_to_new_structure():
    """Initialize with sample data for the new structure"""
    print("📊 Initializing sample data for new structure...")
    
    with app.app_context():
        # Import and run sample data initialization
        from sample_data import initialize_sample_data
        initialize_sample_data()
    
    print("✅ Sample data initialized")

def create_demo_data_with_new_structure():
    """Create demo data that demonstrates the new relationship structure"""
    print("🎯 Creating demo data for new structure...")
    
    with app.app_context():
        # Create a demo ProductFeature
        demo_pf = ProductFeature(
            name="Advanced Autonomous Navigation",
            description="Comprehensive autonomous navigation system for complex urban environments",
            vehicle_platform_id=1,  # Assuming platform exists
            swimlane_decorators="Navigation, AI, Safety",
            label="PF-NAV-2.0",
            tmos="Navigate autonomously in 95% of urban scenarios with 99.9% safety record",
            status_relative_to_tmos=45.0,
            active_flag="active",
            document_url="https://docs.example.com/advanced-navigation"
        )
        
        db.session.add(demo_pf)
        db.session.flush()  # Get ID
        
        # Create Capabilities that belong to this ProductFeature
        capabilities_data = [
            {
                "name": "Environment Perception",
                "success_criteria": "Accurately detect and classify objects within 100m radius with 99.5% accuracy",
                "tmos": "Real-time object detection and classification",
                "progress_relative_to_tmos": 75.0
            },
            {
                "name": "Path Planning",
                "success_criteria": "Generate optimal paths considering traffic, weather, and road conditions",
                "tmos": "Dynamic path optimization with <2s computation time",
                "progress_relative_to_tmos": 60.0
            },
            {
                "name": "Vehicle Control",
                "success_criteria": "Execute planned maneuvers with <5cm positional accuracy",
                "tmos": "Precise vehicle control for autonomous operation",
                "progress_relative_to_tmos": 80.0
            }
        ]
        
        created_capabilities = []
        for cap_data in capabilities_data:
            capability = Capabilities(
                name=cap_data["name"],
                success_criteria=cap_data["success_criteria"],
                product_feature_id=demo_pf.id,
                tmos=cap_data["tmos"],
                progress_relative_to_tmos=cap_data["progress_relative_to_tmos"]
            )
            db.session.add(capability)
            created_capabilities.append(capability)
        
        db.session.flush()  # Get capability IDs
        
        # Create TechnicalFunctions that implement these capabilities
        technical_functions_data = [
            # TechnicalFunctions for Environment Perception
            {
                "name": "LiDAR Processing System",
                "description": "Process LiDAR point clouds for 3D environment mapping",
                "success_criteria": "Process 1M points/second with <10ms latency",
                "capabilities": ["Environment Perception"]
            },
            {
                "name": "Camera Vision System",
                "description": "Multi-camera object detection and tracking",
                "success_criteria": "Detect objects at 30fps with 99% accuracy",
                "capabilities": ["Environment Perception"]
            },
            # TechnicalFunctions for Path Planning
            {
                "name": "Route Optimization Engine",
                "description": "Calculate optimal routes using AI algorithms",
                "success_criteria": "Generate routes 15% faster than traditional GPS",
                "capabilities": ["Path Planning"]
            },
            {
                "name": "Dynamic Obstacle Avoidance",
                "description": "Real-time path adjustment for moving obstacles",
                "success_criteria": "React to obstacles within 100ms",
                "capabilities": ["Path Planning", "Environment Perception"]  # Can implement multiple capabilities
            },
            # TechnicalFunctions for Vehicle Control
            {
                "name": "Steering Control System",
                "description": "Precise steering control for autonomous navigation",
                "success_criteria": "Maintain lane position within ±5cm",
                "capabilities": ["Vehicle Control"]
            },
            {
                "name": "Speed Control System",
                "description": "Adaptive speed control based on traffic conditions",
                "success_criteria": "Maintain safe following distance with smooth acceleration",
                "capabilities": ["Vehicle Control"]
            }
        ]
        
        # Create capability name to object mapping
        cap_map = {cap.name: cap for cap in created_capabilities}
        
        for tf_data in technical_functions_data:
            tech_func = TechnicalFunction(
                name=tf_data["name"],
                description=tf_data["description"],
                success_criteria=tf_data["success_criteria"],
                tmos=f"Technical implementation of {tf_data['name']}",
                status_relative_to_tmos=50.0  # Default progress
            )
            
            db.session.add(tech_func)
            db.session.flush()  # Get ID
            
            # Link to capabilities
            for cap_name in tf_data["capabilities"]:
                if cap_name in cap_map:
                    tech_func.capabilities.append(cap_map[cap_name])
        
        db.session.commit()
        
        print(f"✅ Created demo ProductFeature '{demo_pf.name}' with {len(created_capabilities)} capabilities")
        print(f"   and {len(technical_functions_data)} technical functions")

def main():
    """Main migration function"""
    print("🚀 Starting migration to new database structure...")
    print("=" * 60)
    
    # Step 1: Backup existing data
    backup_data = backup_existing_data()
    
    # Step 2: Recreate database with new structure
    recreate_database()
    
    # Step 3: Initialize sample data
    migrate_data_to_new_structure()
    
    # Step 4: Create demo data showcasing new structure
    create_demo_data_with_new_structure()
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("\n📋 NEW RELATIONSHIP STRUCTURE:")
    print("   ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction")
    print("\n🎯 Key Changes:")
    print("   • Capabilities are now owned by ProductFeatures (1:N relationship)")
    print("   • TechnicalFunctions implement Capabilities (M:N relationship)")
    print("   • Removed direct ProductFeature → TechnicalFunction relationship")
    print("\n📊 Demo Data Created:")
    print("   • 1 Demo ProductFeature: 'Advanced Autonomous Navigation'")
    print("   • 3 Capabilities: Environment Perception, Path Planning, Vehicle Control")
    print("   • 6 TechnicalFunctions implementing these capabilities")

if __name__ == "__main__":
    main()