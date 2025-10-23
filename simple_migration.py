#!/usr/bin/env python3
"""
Simple migration script to recreate database with new relationship structure:
ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction
"""

from app import app, db, ProductFeature, Capabilities, TechnicalFunction, VehiclePlatform
from datetime import datetime, date

def recreate_database_with_new_structure():
    """Drop and recreate database with new structure and sample data"""
    print("🗑️  Dropping existing tables...")
    with app.app_context():
        db.drop_all()
    
    print("🏗️  Creating new table structure...")
    with app.app_context():
        db.create_all()
    
    print("📊 Initializing sample data...")
    with app.app_context():
        # First ensure we have vehicle platforms
        from sample_data import initialize_sample_data
        initialize_sample_data()
        
        # Create a demo ProductFeature showcasing the new structure
        demo_pf = ProductFeature(
            name="Advanced Autonomous Navigation System",
            description="Comprehensive autonomous navigation for complex urban environments with AI-powered decision making",
            vehicle_platform_id=1,  # Truck Platform
            swimlane_decorators="Navigation, AI, Safety, Urban",
            label="PF-NAV-2.0",
            tmos="Navigate autonomously in 95% of urban scenarios with 99.9% safety record and <2s decision time",
            status_relative_to_tmos=45.0,
            planned_start_date=date(2024, 1, 1),
            planned_end_date=date(2025, 6, 30),
            active_flag="active",
            document_url="https://docs.example.com/advanced-navigation"
        )
        
        db.session.add(demo_pf)
        db.session.flush()  # Get ID
        
        # Create Capabilities that belong to this ProductFeature
        capabilities_data = [
            {
                "name": "Environment Perception",
                "success_criteria": "Accurately detect and classify objects within 100m radius with 99.5% accuracy in all weather conditions",
                "tmos": "Real-time object detection and classification with weather adaptation",
                "progress_relative_to_tmos": 75.0,
                "document_url": "https://docs.example.com/environment-perception"
            },
            {
                "name": "Dynamic Path Planning", 
                "success_criteria": "Generate optimal paths considering traffic, weather, and road conditions with <2s computation",
                "tmos": "AI-powered dynamic path optimization with real-time adaptation",
                "progress_relative_to_tmos": 60.0,
                "document_url": "https://docs.example.com/path-planning"
            },
            {
                "name": "Precise Vehicle Control",
                "success_criteria": "Execute planned maneuvers with <5cm positional accuracy and smooth motion",
                "tmos": "Millimeter-precise vehicle control for complex autonomous maneuvers",
                "progress_relative_to_tmos": 80.0,
                "document_url": "https://docs.example.com/vehicle-control"
            }
        ]
        
        created_capabilities = []
        for cap_data in capabilities_data:
            capability = Capabilities(
                name=cap_data["name"],
                success_criteria=cap_data["success_criteria"],
                product_feature_id=demo_pf.id,
                vehicle_platform_id=1,
                planned_start_date=date(2024, 1, 15),
                planned_end_date=date(2025, 3, 31),
                tmos=cap_data["tmos"],
                progress_relative_to_tmos=cap_data["progress_relative_to_tmos"],
                document_url=cap_data["document_url"]
            )
            db.session.add(capability)
            created_capabilities.append(capability)
        
        db.session.flush()  # Get capability IDs
        
        # Create TechnicalFunctions that implement these capabilities
        technical_functions_data = [
            # TechnicalFunctions for Environment Perception
            {
                "name": "Multi-Sensor LiDAR Processing",
                "description": "Advanced LiDAR point cloud processing with AI-enhanced object recognition",
                "success_criteria": "Process 2M points/second with <5ms latency and 99.8% object classification accuracy",
                "tmos": "Real-time 3D environment mapping with AI classification",
                "status_relative_to_tmos": 70.0,
                "capabilities": ["Environment Perception"],
                "document_url": "https://docs.example.com/lidar-processing"
            },
            {
                "name": "AI Camera Vision System",
                "description": "Multi-camera AI-powered object detection, tracking, and behavioral prediction",
                "success_criteria": "Detect and track objects at 60fps with 99.5% accuracy and predict behavior 3s ahead",
                "tmos": "AI-powered visual perception with predictive analytics",
                "status_relative_to_tmos": 85.0,
                "capabilities": ["Environment Perception"],
                "document_url": "https://docs.example.com/ai-vision"
            },
            {
                "name": "Weather-Adaptive Sensor Fusion",
                "description": "Intelligent sensor fusion that adapts to weather conditions and visibility",
                "success_criteria": "Maintain 95% perception accuracy in adverse weather (rain, snow, fog)",
                "tmos": "All-weather perception reliability",
                "status_relative_to_tmos": 60.0,
                "capabilities": ["Environment Perception"],
                "document_url": "https://docs.example.com/sensor-fusion"
            },
            # TechnicalFunctions for Dynamic Path Planning
            {
                "name": "AI Route Optimization Engine",
                "description": "Machine learning-based route optimization with real-time traffic and condition analysis",
                "success_criteria": "Generate routes 20% faster than traditional GPS with 95% accuracy prediction",
                "tmos": "AI-powered optimal routing with predictive optimization",
                "status_relative_to_tmos": 65.0,
                "capabilities": ["Dynamic Path Planning"],
                "document_url": "https://docs.example.com/ai-routing"
            },
            {
                "name": "Real-Time Obstacle Avoidance",
                "description": "Dynamic path adjustment for moving obstacles with predictive collision avoidance",
                "success_criteria": "React to obstacles within 50ms with 99.99% collision avoidance rate",
                "tmos": "Instantaneous obstacle avoidance with predictive safety",
                "status_relative_to_tmos": 75.0,
                "capabilities": ["Dynamic Path Planning", "Environment Perception"],  # Implements multiple capabilities
                "document_url": "https://docs.example.com/obstacle-avoidance"
            },
            {
                "name": "Traffic-Aware Decision Making",
                "description": "AI-powered decision making considering traffic patterns, signals, and pedestrian behavior",
                "success_criteria": "Make optimal decisions in 98% of traffic scenarios with <1s response time",
                "tmos": "Human-like traffic decision making with superhuman reaction time",
                "status_relative_to_tmos": 50.0,
                "capabilities": ["Dynamic Path Planning", "Environment Perception"],
                "document_url": "https://docs.example.com/traffic-decisions"
            },
            # TechnicalFunctions for Precise Vehicle Control  
            {
                "name": "High-Precision Steering Control",
                "description": "Millimeter-precise steering control system with adaptive road surface compensation",
                "success_criteria": "Maintain lane position within ±2cm with adaptive surface compensation",
                "tmos": "Professional driver-level precision with enhanced stability",
                "status_relative_to_tmos": 90.0,
                "capabilities": ["Precise Vehicle Control"],
                "document_url": "https://docs.example.com/steering-control"
            },
            {
                "name": "Adaptive Speed Control System",
                "description": "AI-powered speed control with traffic flow optimization and comfort prioritization",
                "success_criteria": "Maintain optimal speed with 95% passenger comfort rating and fuel efficiency",
                "tmos": "Smooth, efficient speed control optimized for passenger comfort",
                "status_relative_to_tmos": 80.0,
                "capabilities": ["Precise Vehicle Control"],
                "document_url": "https://docs.example.com/speed-control"
            },
            {
                "name": "Integrated Motion Control",
                "description": "Coordinated control of steering, braking, and acceleration for complex maneuvers",
                "success_criteria": "Execute complex maneuvers with <3cm accuracy and passenger comfort priority",
                "tmos": "Seamless motion control for complex autonomous maneuvers",
                "status_relative_to_tmos": 70.0,
                "capabilities": ["Precise Vehicle Control", "Dynamic Path Planning"],
                "document_url": "https://docs.example.com/motion-control"
            }
        ]
        
        # Create capability name to object mapping
        cap_map = {cap.name: cap for cap in created_capabilities}
        
        for tf_data in technical_functions_data:
            tech_func = TechnicalFunction(
                name=tf_data["name"],
                description=tf_data["description"],
                success_criteria=tf_data["success_criteria"],
                vehicle_platform_id=1,
                tmos=tf_data["tmos"],
                status_relative_to_tmos=tf_data["status_relative_to_tmos"],
                planned_start_date=date(2024, 2, 1),
                planned_end_date=date(2025, 1, 31),
                document_url=tf_data["document_url"]
            )
            
            db.session.add(tech_func)
            db.session.flush()  # Get ID
            
            # Link to capabilities (Many-to-Many relationship)
            for cap_name in tf_data["capabilities"]:
                if cap_name in cap_map:
                    tech_func.capabilities.append(cap_map[cap_name])
        
        db.session.commit()
        
        print(f"✅ Created ProductFeature: '{demo_pf.name}'")
        print(f"   └── {len(created_capabilities)} Capabilities:")
        for cap in created_capabilities:
            print(f"       • {cap.name}")
        print(f"   └── {len(technical_functions_data)} TechnicalFunctions implementing these capabilities")
        
        # Show the relationship structure
        print(f"\n📊 Relationship Summary:")
        for cap in created_capabilities:
            implementing_functions = [tf.name for tf in cap.technical_functions]
            print(f"   {cap.name} → implemented by {len(implementing_functions)} TechnicalFunction(s)")
    
    print("\n✅ Database migration completed successfully!")

def main():
    """Main migration function"""
    print("🚀 Migrating to new database relationship structure...")
    print("=" * 70)
    print("NEW STRUCTURE: ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction")
    print("=" * 70)
    
    recreate_database_with_new_structure()
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED!")
    print("\n🎯 New Relationship Structure:")
    print("   • ProductFeature owns multiple Capabilities (1:N)")
    print("   • Capabilities are implemented by TechnicalFunctions (M:N)")
    print("   • TechnicalFunctions can implement multiple Capabilities")
    print("\n📋 Sample Data Created:")
    print("   • 1 Advanced ProductFeature with comprehensive capabilities")
    print("   • 3 Core Capabilities covering autonomous navigation")
    print("   • 9 TechnicalFunctions with realistic implementation details")
    print("   • Full many-to-many relationships demonstrating the new structure")

if __name__ == "__main__":
    main()