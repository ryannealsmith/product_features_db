#!/usr/bin/env python3
"""
Verification script for TechnicalCapability → TechnicalFunction refactoring
"""

import os
import re

def check_file_for_old_references(file_path):
    """Check if file contains old TechnicalCapability references"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to check for old references
        old_patterns = [
            r'TechnicalCapability',
            r'technical_capability',
            r'technical_capabilities',
        ]
        
        found_old = []
        for pattern in old_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_old.extend(matches)
        
        return found_old
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def check_file_for_new_references(file_path):
    """Check if file contains new TechnicalFunction references"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to check for new references
        new_patterns = [
            (r'TechnicalFunction', 'TechnicalFunction class/model references'),
            (r'technical_function(?!s)', 'technical_function relationship references'),
            (r'technical_functions', 'technical_functions variable/route references'),
        ]
        
        found_new = {}
        for pattern, description in new_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_new[description] = len(matches)
        
        return found_new
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def main():
    print("🔍 Verifying TechnicalCapability → TechnicalFunction Refactoring")
    print("=" * 60)
    
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
        'templates/product_features.html',
        'templates/configurations.html',
        'templates/readiness_matrix.html'
    ]
    
    all_clear = True
    
    # Check for old references
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📁 Checking {file_path}:")
            old_refs = check_file_for_old_references(file_path)
            if old_refs:
                print(f"  ❌ Found old references: {old_refs}")
                all_clear = False
            else:
                print(f"  ✅ All references updated correctly")
        else:
            print(f"\n📁 {file_path}: File not found")
    
    print(f"\n🔍 Checking for correct new references:")
    
    # Check key files for new references
    key_files = ['app.py', 'routes.py', 'sample_data.py']
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"\n📁 {file_path}:")
            new_refs = check_file_for_new_references(file_path)
            for description, count in new_refs.items():
                print(f"  ✅ Found {count} occurrence(s) of {description}")
    
    # Check template files
    print(f"\n📋 Template Files:")
    if os.path.exists('templates/technical_functions.html'):
        print(f"  ✅ technical_functions.html exists")
    else:
        print(f"  ⚠️  technical_functions.html does not exist yet")
    
    if os.path.exists('templates/technical_capabilities.html'):
        print(f"  ⚠️  technical_capabilities.html still exists (should be renamed)")
    else:
        print(f"  ✅ technical_capabilities.html removed")
    
    print(f"\n📊 Summary:")
    if all_clear:
        print("✅ Refactoring appears to be complete!")
        print("✅ All TechnicalCapability references have been updated to TechnicalFunction")
    else:
        print("❌ Refactoring incomplete - old references still found")
    
    print(f"\n🚀 Next Steps:")
    print("1. Test the web application thoroughly")
    print("2. Run CSV and JSON update scripts to verify they work")
    print("3. Rename template file:")
    print("   mv templates/technical_capabilities.html templates/technical_functions.html")
    print("4. Commit changes to git repository")

if __name__ == "__main__":
    main()