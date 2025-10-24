#!/usr/bin/env python3
"""
Fix M:N relationships between Product Features and Capabilities
by re-processing the JSON data to establish missing links
"""
import json
from app import app, db, ProductFeature, Capabilities

def fix_mn_relationships():
    """Fix the M:N relationships between product features and capabilities"""
    with app.app_context():
        print("🔧 Fixing M:N relationships between Product Features and Capabilities...")
        
        # Load the JSON data
        try:
            with open('repository_update_data_final_colin3.json', 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            print("❌ JSON file not found!")
            return
        
        relationships_added = 0
        capabilities_processed = 0
        
        # Process all capability entities in the JSON
        for entity in json_data.get('entities', []):
            if entity.get('entity_type') == 'capability' and entity.get('operation') == 'create':
                cap_label = entity.get('label')
                if not cap_label:
                    continue
                
                # Find the capability in the database
                capability = Capabilities.query.filter_by(label=cap_label).first()
                if not capability:
                    print(f"⚠️  Capability {cap_label} not found in database")
                    continue
                
                capabilities_processed += 1
                
                # Get the product feature IDs this capability should link to
                product_feature_ids = entity.get('product_feature_ids', [])
                
                for pf_label in product_feature_ids:
                    # Find the product feature by label
                    product_feature = ProductFeature.query.filter_by(label=pf_label).first()
                    
                    if product_feature:
                        # Check if relationship already exists
                        if capability not in product_feature.capabilities:
                            product_feature.capabilities.append(capability)
                            relationships_added += 1
                            print(f"✅ Linked {pf_label} ↔ {cap_label}")
                    else:
                        print(f"⚠️  Product Feature {pf_label} not found for capability {cap_label}")
        
        # Also process product features that reference capabilities
        for entity in json_data.get('entities', []):
            if entity.get('entity_type') == 'product_feature' and entity.get('operation') == 'create':
                pf_label = entity.get('label')
                if not pf_label:
                    continue
                
                # Find the product feature in the database
                product_feature = ProductFeature.query.filter_by(label=pf_label).first()
                if not product_feature:
                    continue
                
                # Get the capabilities this product feature should link to
                capabilities_required = entity.get('capabilities_required', []) or entity.get('capabilities', [])
                
                for cap_label in capabilities_required:
                    # Find the capability by label
                    capability = Capabilities.query.filter_by(label=cap_label).first()
                    
                    if capability:
                        # Check if relationship already exists
                        if capability not in product_feature.capabilities:
                            product_feature.capabilities.append(capability)
                            relationships_added += 1
                            print(f"✅ Linked {pf_label} ↔ {cap_label}")
                    else:
                        print(f"⚠️  Capability {cap_label} not found for product feature {pf_label}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n🎉 Relationship fixing completed!")
        print(f"   Capabilities processed: {capabilities_processed}")
        print(f"   New relationships added: {relationships_added}")
        
        # Verify the results
        print("\n📊 Final verification:")
        total_pfs = ProductFeature.query.count()
        linked_pfs = ProductFeature.query.filter(ProductFeature.capabilities.any()).count()
        total_caps = Capabilities.query.count()
        linked_caps = Capabilities.query.filter(Capabilities.product_features.any()).count()
        total_relationships = db.session.execute(db.text('SELECT COUNT(*) FROM product_feature_capabilities')).scalar()
        
        print(f"   Product features with capabilities: {linked_pfs}/{total_pfs}")
        print(f"   Capabilities with product features: {linked_caps}/{total_caps}")
        print(f"   Total M:N relationships: {total_relationships}")

if __name__ == "__main__":
    fix_mn_relationships()