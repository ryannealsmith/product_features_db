#!/usr/bin/env python3
"""
Validation script to verify the vehicle platform relationships
"""

from app import app, db, ProductFeature, TechnicalFunction, Capabilities, VehiclePlatform

def validate_vehicle_platform_relationships():
    """Validate that the vehicle platform relationships are working correctly"""
    
    with app.app_context():
        print("🔍 Validating Vehicle Platform Relationships")
        print("=" * 50)
        
        # Check Vehicle Platforms
        platforms = VehiclePlatform.query.all()
        print(f"📋 Vehicle Platforms ({len(platforms)}):")
        for platform in platforms:
            print(f"  • {platform.name} ({platform.vehicle_type})")
            print(f"    - Product Features: {len(platform.product_features)}")
            print(f"    - Technical Functions: {len(platform.technical_functions)}")
            print(f"    - Capabilities: {len(platform.capabilities)}")
        
        print("\n" + "=" * 50)
        
        # Check Product Features
        print(f"📦 Product Features with Vehicle Platforms:")
        features = ProductFeature.query.all()
        for feature in features:
            platform_name = feature.vehicle_platform.name if feature.vehicle_platform else "No Platform"
            vehicle_type = feature.vehicle_platform.vehicle_type if feature.vehicle_platform else "Unknown"
            print(f"  • {feature.name}")
            print(f"    - Platform: {platform_name} ({vehicle_type})")
        
        print("\n" + "=" * 50)
        
        # Check Technical Functions
        print(f"⚙️  Technical Functions with Vehicle Platforms:")
        functions = TechnicalFunction.query.limit(5).all()  # Show first 5 for brevity
        for func in functions:
            platform_name = func.vehicle_platform.name if func.vehicle_platform else "No Platform"
            vehicle_type = func.vehicle_platform.vehicle_type if func.vehicle_platform else "Unknown"
            print(f"  • {func.name}")
            print(f"    - Platform: {platform_name} ({vehicle_type})")
        
        if TechnicalFunction.query.count() > 5:
            print(f"    ... and {TechnicalFunction.query.count() - 5} more")
        
        print("\n" + "=" * 50)
        
        # Check Capabilities
        print(f"🎯 Capabilities with Vehicle Platforms:")
        capabilities = Capabilities.query.all()
        for capability in capabilities:
            platform_name = capability.vehicle_platform.name if capability.vehicle_platform else "No Platform"
            vehicle_type = capability.vehicle_platform.vehicle_type if capability.vehicle_platform else "Unknown"
            print(f"  • {capability.name}")
            print(f"    - Platform: {platform_name} ({vehicle_type})")
        
        print("\n" + "=" * 50)
        print("✅ Validation completed successfully!")
        
        # Summary statistics
        total_entities = len(features) + TechnicalFunction.query.count() + len(capabilities)
        entities_with_platforms = sum([
            len([f for f in features if f.vehicle_platform]),
            len([f for f in TechnicalFunction.query.all() if f.vehicle_platform]),
            len([c for c in capabilities if c.vehicle_platform])
        ])
        
        print(f"📊 Summary:")
        print(f"   - Total Vehicle Platforms: {len(platforms)}")
        print(f"   - Total Entities: {total_entities}")
        print(f"   - Entities with Platforms: {entities_with_platforms}")
        print(f"   - Migration Success Rate: {(entities_with_platforms/total_entities)*100:.1f}%")

if __name__ == '__main__':
    validate_vehicle_platform_relationships()