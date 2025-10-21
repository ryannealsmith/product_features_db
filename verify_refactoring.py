#!/usr/bin/env python3
"""
Verification script for ProductCapability -> ProductFeature refactoring
"""

import os
import re

def check_file_for_old_references(file_path, patterns_to_check):
    """Check a file for old references that should have been updated"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        for pattern, description in patterns_to_check:
            if re.search(pattern, content, re.IGNORECASE):
                matches = re.findall(pattern, content, re.IGNORECASE)
                issues.append(f"  ❌ Found {len(matches)} occurrence(s) of {description}")
        
        return issues
    except Exception as e:
        return [f"  ❌ Error reading file: {e}"]

def verify_refactoring():
    """Verify that all ProductCapability references have been updated to ProductFeature"""
    
    print("🔍 Verifying ProductCapability → ProductFeature Refactoring")
    print("=" * 60)
    
    # Define patterns to check for
    patterns_to_check = [
        (r'ProductCapability', 'ProductCapability class/model references'),
        (r'product_capability(?!\.)', 'product_capability relationship references'),
        (r'product_capabilities(?!\.)', 'product_capabilities variable/route references'),
        (r"'product_capabilities'", 'product_capabilities template variable references'),
        (r'product_capabilities\.html', 'product_capabilities.html template references'),
    ]
    
    # Files to check
    files_to_check = [
        'app.py',
        'routes.py', 
        'sample_data.py',
        'update_from_csv.py',
        'update_from_json.py',
        'templates/dashboard.html',
        'templates/readiness_assessments.html',
        'templates/technical_capabilities.html',
        'templates/add_assessment.html',
        'templates/base.html',
        'templates/product_features.html'
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📁 Checking {file_path}:")
            issues = check_file_for_old_references(file_path, patterns_to_check)
            if issues:
                for issue in issues:
                    print(issue)
                total_issues += len(issues)
            else:
                print("  ✅ All references updated correctly")
        else:
            print(f"\n📁 {file_path}: ⚠️  File not found")
    
    # Check for new references that should exist
    print(f"\n🔍 Checking for correct new references:")
    
    new_patterns = [
        (r'ProductFeature', 'ProductFeature class/model references'),
        (r'product_feature(?!s)', 'product_feature relationship references'),
        (r'product_features', 'product_features variable/route references'),
    ]
    
    key_files = ['app.py', 'routes.py', 'sample_data.py']
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"\n📁 {file_path}:")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern, description in new_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"  ✅ Found {len(matches)} occurrence(s) of {description}")
                else:
                    print(f"  ⚠️  No {description} found")
    
    # Check template files exist
    print(f"\n📋 Template Files:")
    if os.path.exists('templates/product_features.html'):
        print("  ✅ product_features.html exists")
    else:
        print("  ❌ product_features.html missing")
        
    if os.path.exists('templates/product_capabilities.html'):
        print("  ⚠️  product_capabilities.html still exists (should be removed)")
    else:
        print("  ✅ product_capabilities.html removed")
    
    # Summary
    print(f"\n📊 Summary:")
    if total_issues == 0:
        print("✅ Refactoring appears to be complete!")
        print("✅ All ProductCapability references have been updated to ProductFeature")
    else:
        print(f"❌ Found {total_issues} potential issues that need attention")
    
    # Next steps
    print(f"\n🚀 Next Steps:")
    print("1. Test the web application thoroughly")
    print("2. Run CSV and JSON update scripts to verify they work")
    print("3. Remove old template file if it exists:")
    print("   rm templates/product_capabilities.html")
    print("4. Commit changes to git repository")

if __name__ == '__main__':
    verify_refactoring()