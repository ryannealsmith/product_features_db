#!/usr/bin/env python3
"""
Script to fix capability relationships for existing Product Features
"""

import json
from app import app, db, ProductFeature, Capabilities

def fix_capability_relationships(json_file):
    """Fix capability relationships by re-processing existing product features"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    with app.app_context():
        updated_count = 0
        
        for entity in data['entities']:
            if entity.get('entity_type') == 'product_feature':
                pf_name = entity['name']
                capabilities_required = entity.get('capabilities_required', [])
                
                if not capabilities_required:
                    continue
                
                # Find the product feature
                pf = ProductFeature.query.filter_by(name=pf_name).first()
                if not pf:
                    print(f"Product Feature '{pf_name}' not found, skipping")
                    continue
                
                # Clear existing relationships
                pf.capabilities.clear()
                
                # Add new relationships
                linked_capabilities = []
                for cap_label in capabilities_required:
                    # Try to find capability by label first, then by name
                    capability = Capabilities.query.filter_by(label=cap_label).first()
                    if not capability:
                        capability = Capabilities.query.filter_by(name=cap_label).first()
                    
                    if capability:
                        pf.capabilities.append(capability)
                        linked_capabilities.append(capability.name)
                    else:
                        print(f"  Warning: Capability '{cap_label}' not found")
                
                if linked_capabilities:
                    print(f"Updated '{pf_name}' with capabilities: {linked_capabilities}")
                    updated_count += 1
        
        # Commit all changes
        db.session.commit()
        print(f"\nSuccessfully updated {updated_count} product features with capability relationships")

if __name__ == "__main__":
    fix_capability_relationships('repository_update_data_final_colin.json')