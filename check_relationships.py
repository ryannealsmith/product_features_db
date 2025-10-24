#!/usr/bin/env python3
from app import app, db, ProductFeature, Capabilities
from sqlalchemy import text

def check_relationships():
    with app.app_context():
        # Check all tables with product/capability in name
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        all_tables = [row[0] for row in result.fetchall()]
        
        relevant_tables = [t for t in all_tables if 'product' in t.lower() or 'capabil' in t.lower()]
        
        print("Tables related to product features and capabilities:")
        for table in sorted(relevant_tables):
            count = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
            print(f'  {table}: {count} rows')
        
        # Check the M:N association table
        print("\nChecking product_feature_capabilities association table:")
        if 'product_feature_capabilities' in relevant_tables:
            result = db.session.execute(text('SELECT * FROM product_feature_capabilities LIMIT 10'))
            rows = result.fetchall()
            print("Sample associations:")
            for row in rows:
                print(f'  PF ID: {row[0]} ↔ Cap ID: {row[1]}')
            
            total = db.session.execute(text('SELECT COUNT(*) FROM product_feature_capabilities')).scalar()
            print(f'\nTotal M:N associations: {total}')
        
        # Check actual object relationships
        print("\nChecking ORM relationships:")
        pf_with_caps = ProductFeature.query.filter(ProductFeature.capabilities.any()).count()
        caps_with_pfs = Capabilities.query.filter(Capabilities.product_features.any()).count()
        
        print(f'Product Features with capabilities: {pf_with_caps}/100')
        print(f'Capabilities with product features: {caps_with_pfs}/100')
        
        # Show some examples
        print("\nSample relationships:")
        pfs_with_caps = ProductFeature.query.filter(ProductFeature.capabilities.any()).limit(5).all()
        for pf in pfs_with_caps:
            cap_labels = [cap.label for cap in pf.capabilities]
            print(f'  {pf.label} → {cap_labels}')

if __name__ == "__main__":
    check_relationships()