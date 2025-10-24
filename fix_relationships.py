#!/usr/bin/env python3
"""
Fix relationships between existing Product Features and Capabilities
"""
from app import app, db, ProductFeature, Capabilities

def fix_relationships():
    """Fix the broken relationships between product features and capabilities"""
    with app.app_context():
        print("🔧 Fixing Product Feature ↔ Capability relationships...")
        
        # Get all product features and capabilities
        product_features = ProductFeature.query.all()
        capabilities = Capabilities.query.all()
        
        print(f"Found {len(product_features)} product features and {len(capabilities)} capabilities")
        
        # Create lookup dictionaries
        pf_by_label = {pf.label: pf for pf in product_features if pf.label}
        cap_by_label = {cap.label: cap for cap in capabilities if cap.label}
        
        print(f"Product features with labels: {len(pf_by_label)}")
        print(f"Capabilities with labels: {len(cap_by_label)}")
        
        relationships_fixed = 0
        
        # Fix relationships where capability references product feature
        for cap in capabilities:
            if cap.label and cap.label.startswith('CA-'):
                # Convert CA-ACT-1.1 to PF-ACT-1.1
                expected_pf_label = cap.label.replace('CA-', 'PF-')
                
                if expected_pf_label in pf_by_label:
                    pf = pf_by_label[expected_pf_label]
                    
                    # Check if relationship already exists
                    if cap not in pf.capabilities:
                        pf.capabilities.append(cap)
                        relationships_fixed += 1
                        print(f"✅ Linked {pf.label} ↔ {cap.label}")
        
        # Commit the changes
        db.session.commit()
        
        print(f"🎉 Fixed {relationships_fixed} relationships!")
        
        # Verify the results
        print("\n📊 Verification:")
        linked_pfs = ProductFeature.query.filter(ProductFeature.capabilities.any()).count()
        linked_caps = Capabilities.query.filter(Capabilities.product_features.any()).count()
        print(f"Product features with capabilities: {linked_pfs}")
        print(f"Capabilities with product features: {linked_caps}")

if __name__ == "__main__":
    fix_relationships()