#!/usr/bin/env python3
"""
Create clean database with new relationship structure and minimal data
"""

from app import app, db, ProductFeature, Capabilities, TechnicalFunction, VehiclePlatform, TechnicalReadinessLevel, ODD, Environment, Trailer
from datetime import datetime, date

def create_clean_database():
    """Create clean database with new structure"""
    print("🗑️  Dropping existing tables...")
    with app.app_context():
        db.drop_all()
    
    print("🏗️  Creating new table structure...")
    with app.app_context():
        db.create_all()
    
    print("📊 Creating basic configuration data...")
    with app.app_context():
        # Vehicle Platforms
        vehicle_platforms = [
            ("Terberg ATT", "Autonomous Terminal Tractor", "truck", 40000),
            ("CA500", "Autonomous Asset Monitoring Vehicle", "van", 500),
            ("T800", "Bradshaw T800 Towing Tractor", "truck", 800),
            ("AEV", "Applied EV Skateboard Platform", "car", 1000),
            ("All", "All vehicle platforms", "generic", 2000)
        ]
        
        for name, description, vehicle_type, max_payload in vehicle_platforms:
            platform = VehiclePlatform(name=name, description=description, vehicle_type=vehicle_type, max_payload=max_payload)
            db.session.add(platform)
        
        # Technical Readiness Levels (TRL 1-9)
        trl_data = [
            (1, "Basic principles observed", "Scientific research begins to be translated into applied research and development"),
            (2, "Technology concept formulated", "Practical applications can be invented"),
            (3, "Experimental proof of concept", "Active research and development is initiated"),
            (4, "Technology validated in lab", "Basic technological components are integrated"),
            (5, "Technology validated in environment", "Technology components and/or basic technology subsystems are integrated with realistic supporting elements"),
            (6, "Technology demonstrated in environment", "Representative model or prototype system is tested in a relevant environment"),
            (7, "System prototype demonstrated", "Prototype near or at planned operational system"),
            (8, "System complete and qualified", "Technology has been proven to work in its final form and under expected conditions"),
            (9, "Actual system proven in operational environment", "Actual application of technology in its final form")
        ]
        
        for level, name, description in trl_data:
            trl = TechnicalReadinessLevel(level=level, name=name, description=description)
            db.session.add(trl)
        
        # ODDs (Operational Design Domains)
        odds = [
            ("Port Baseline", "Forward towing of a semi-trailer", 25, "two-way", "Nominal lanes width (+1m - +2.0m buffer)", "junctions", "bridges", "pedestrian crossings", "pedestrians, other vehicles", "crane, reach stacker", "dry, wet", "max uphill 5%, max downhill 5%"),
            ("Port: AV-Ped interaction", "Baseline with Pedestrian interaction", 25, "two-way", "Queueing lanes width (+0.5m buffer)", "junctions, accomodate trailers", "bridges", "pedestrian crossings, school zones", "pedestrians, cyclists, other vehicles", "crane, reach stacker", "dry, wet", "max uphill 3%, max downhill 3%"),
            ("Port: Movable pinning stations", "Baseline with human-robot interaction", 25, "two-way", "Lane change, Lane borrow", "junctions", "bridges", "pedestrian crossings", "pedestrians, other vehicles", "gantry (mobile), gantry (stacked)", "dry, wet, fog", "max uphill 5%, max downhill 5%"),
            ("Factory: baseline", "Limited access roads and depots", 8, "one-way", "Nominal lanes width (+1m - +2.0m buffer)", "junctions", "tunnels", "school zones", "pedestrians, cyclists", "crane, gantry (stacked)", "dry", "max uphill 2%, max downhill 2%")
        ]
        
        for name, description, max_speed, direction, lanes, intersections, infrastructure, hazards, actors, handling_equipment, traction, inclines in odds:
            odd = ODD(name=name, description=description, max_speed=max_speed, 
                     direction=direction, lanes=lanes, intersections=intersections,
                     infrastructure=infrastructure, hazards=hazards, actors=actors,
                     handling_equipment=handling_equipment, traction=traction, inclines=inclines)
            db.session.add(odd)
        
        # Environments
        environments = [
            ("North American Temperate", "Temperate climate regions of North America", "North America", "temperate", "varied"),
            ("European Urban", "Dense European urban environments", "Europe", "temperate", "flat to hilly"),
            ("Desert Regions", "Hot, dry desert environments", "Global", "arid", "flat"),
            ("Cold Climate", "Northern regions with harsh winters", "Global", "arctic", "varied")
        ]
        
        for name, description, region, climate, terrain in environments:
            env = Environment(name=name, description=description, region=region, 
                             climate=climate, terrain=terrain)
            db.session.add(env)
        
        # Trailers
        trailers = [
            ("No trailer", "Driving without a trailer", "bobtailing", None, 0, 0),
            ("Semi-trailer: Boxcar; Vantec model; variable weight", "Semi-trailer with a boxcar design", "VTsemi", 16.15, 34000, 2),
            ("Semi-trailer: Chassis; City Terminal model; chassis + container (variable weight)", "Semi-trailer chassis for container transport", "CTchassis", 16.15, 34000, 2),
            ("Semi-trailer: Chassis; Jebel Ali model; chassis + container (variable weight)", "Semi-trailer chassis for container transport", "JAchassis", 16.15, 34000, 2),
            ("Unloaded bomb cart", "Unloaded bomb cart", "unloaded", 15, 8000, 2),
            ("Bomb cart with an empty 20ft container", "Empty 20ft container", "empty20", 20, 10000, 2),
            ("Bomb cart with a fully-loaded 20ft container", "Loaded 20ft container", "loaded20", 20, 24000, 2),
            ("Bomb cart with an empty 40ft container", "Empty 40ft container", "empty40", 40, 12000, 2),
            ("Bomb cart with a fully-loaded 40ft container", "Loaded 40ft container", "loaded40", 40, 38000, 2),
            ("Semi-trailer: Boat; Robotraz model; chassis + container (variable weight)", "T800 Boat trailer", "RBboat", 16.15, 500, 1),
            ("Drawbar trailer: XX model, single, variable weight", "Drawbar trailer", "DBsingle", 12, 15000, 1)
        ]
        
        for name, description, trailer_type, length, max_weight, axle_count in trailers:
            trailer = Trailer(name=name, description=description, trailer_type=trailer_type,
                             length=length, max_weight=max_weight, axle_count=axle_count)
            db.session.add(trailer)
        
        db.session.commit()
        
        print("✅ Basic configuration data created")

def create_demo_data():
    """Create demo data showcasing the new relationship structure"""
    print("🎯 Creating demo data...")
    
    with app.app_context():
        # Create demo ProductFeature
        demo_pf = ProductFeature(
            name="Autonomous Port Operations",
            description="DEMO DATA: Complete autonomous vehicle operations for a port environment",
            vehicle_platform_id=1,  # Truck Platform
            swimlane_decorators="Port, Autonomous, Safety",
            label="PF-PORT-1.0",
            tmos="Operate autonomously in port environment with 99% uptime",
            status_relative_to_tmos=60.0,
            planned_start_date=date(2024, 1, 1),
            planned_end_date=date(2025, 12, 31),
            active_flag="active",
            document_url="https://docs.example.com/port-operations"
        )
        
        db.session.add(demo_pf)
        db.session.flush()
        
        # Create Capabilities owned by this ProductFeature
        capabilities_data = [
            {
                "name": "DEMO: Port Navigation",
                "success_criteria": "Navigate port layout with 5 cm accuracy",
                "tmos": "Efficient navigation through complex port environments.",
                "progress": 70.0
            },
            {
                "name": "DEMO: Container Handling Coordination", 
                "success_criteria": "Coordinate with port equipment for safe container operations",
                "tmos": "Seamless integration with port handling equipment",
                "progress": 50.0
            },
            {
                "name": "DEMO: Safety Monitoring",
                "success_criteria": "Detect and respond to safety hazards.",
                "tmos": "Proactive safety monitoring and hazard response",
                "progress": 80.0
            }
        ]
        
        created_capabilities = []
        for cap_data in capabilities_data:
            capability = Capabilities(
                name=cap_data["name"],
                success_criteria=cap_data["success_criteria"],
                product_feature_id=demo_pf.id,
                vehicle_platform_id=1,
                tmos=cap_data["tmos"],
                progress_relative_to_tmos=cap_data["progress"],
                planned_start_date=date(2024, 2, 1),
                planned_end_date=date(2025, 10, 31)
            )
            db.session.add(capability)
            created_capabilities.append(capability)
        
        db.session.flush()
        
        # Create TechnicalFunctions that implement these capabilities
        tech_functions_data = [
            {
                "name": "DEMO: GPS/IMU Navigation System",
                "description": "High-precision navigation using GPS and inertial measurement",
                "success_criteria": "Provide position accuracy within 5 cm",
                "capabilities": ["Port Navigation"]
            },
            {
                "name": "DEMO: Port Layout Mapping",
                "description": "Real-time mapping and localization within port environment",
                "success_criteria": "Maintain accurate position in GPS-denied areas",
                "capabilities": ["Port Navigation"]
            },
            {
                "name": "DEMO: Equipment Communication Interface",
                "description": "Communication system for coordinating with port equipment",
                "success_criteria": "Maintain 90% communication connectivity",
                "capabilities": ["Container Handling Coordination"]
            },
            {
                "name": "DEMO: Collision Avoidance System",
                "description": "Active collision avoidance with multiple sensor types",
                "success_criteria": "Detect obstacles and humans within 72 m range",
                "capabilities": ["Safety Monitoring", "Port Navigation"]  # Multiple capabilities
            },
            {
                "name": "DEMO: Emergency Stop System",
                "description": "Fail-safe emergency stop with multiple redundancy",
                "success_criteria": "Stop vehicle within 5 m from its maximum speed",
                "capabilities": ["Safety Monitoring"]
            }
        ]
        
        # Create capability mapping
        cap_map = {cap.name: cap for cap in created_capabilities}
        
        for tf_data in tech_functions_data:
            tech_func = TechnicalFunction(
                name=tf_data["name"],
                description=tf_data["description"],
                success_criteria=tf_data["success_criteria"],
                vehicle_platform_id=1,
                tmos=f"Technical implementation: {tf_data['name']}",
                status_relative_to_tmos=60.0,
                planned_start_date=date(2024, 3, 1),
                planned_end_date=date(2025, 8, 31)
            )
            
            db.session.add(tech_func)
            db.session.flush()
            
            # Link to capabilities
            for cap_name in tf_data["capabilities"]:
                if cap_name in cap_map:
                    tech_func.capabilities.append(cap_map[cap_name])
        
        db.session.commit()
        
        print(f"✅ Created demo data:")
        print(f"   • ProductFeature: {demo_pf.name}")
        print(f"   • {len(created_capabilities)} Capabilities")
        print(f"   • {len(tech_functions_data)} TechnicalFunctions")

def main():
    """Main function"""
    print("🚀 Creating clean database with new relationship structure...")
    print("=" * 60)
    print("STRUCTURE: ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction")
    print("=" * 60)
    
    create_clean_database()
    create_demo_data()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE CREATED SUCCESSFULLY!")
    print("\n🎯 New Relationship Structure:")
    print("   • ProductFeature owns Capabilities (1:N)")
    print("   • Capabilities implemented by TechnicalFunctions (M:N)")
    print("   • Clean separation of concerns")
    print("\n📊 Ready for testing with the Flask application!")

if __name__ == "__main__":
    main()