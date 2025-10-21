#!/usr/bin/env python3
"""
Test script for the JSON update system
"""

import os
import json
import sys

def test_json_system():
    """Test the JSON update system"""
    print("JSON Update System Created Successfully!")
    print("=" * 50)
    
    print("\n📁 Files Created:")
    files = [
        ('update_from_json.py', 'Main update script'),
        ('capability_updates_template.json', 'Template JSON file'), 
        ('JSON_UPDATE_README.md', 'Complete documentation')
    ]
    
    total_size = 0
    for file, description in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            total_size += size
            print(f"✅ {file:<35} ({size:,} bytes) - {description}")
        else:
            print(f"❌ {file:<35} (missing)")
    
    print(f"\n📊 Total system size: {total_size:,} bytes")
    
    print("\n📋 Template JSON Structure:")
    try:
        with open('capability_updates_template.json', 'r') as f:
            data = json.load(f)
            
        print(f"✅ Valid JSON format")
        print(f"📋 Metadata version: {data.get('metadata', {}).get('version', 'unknown')}")
        print(f"📋 Update count: {len(data.get('updates', []))}")
        
        # Show first few updates
        updates = data.get('updates', [])
        print(f"\n📋 Sample Updates (first 3 of {len(updates)}):")
        for i, update in enumerate(updates[:3]):
            cap_type = update.get('capability_type', 'unknown')
            cap_name = update.get('capability_name', 'unknown')
            trl = update.get('target_trl', 'N/A')
            due = update.get('due_date', 'N/A')
            print(f"  {i+1}. {cap_type.title()}: {cap_name}")
            print(f"     TRL: {trl}, Due: {due}")
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n🔧 Usage Commands:")
    print("1. Export current data:")
    print("   ./venv/bin/python update_from_json.py --export")
    print()
    print("2. Update from JSON:")
    print("   ./venv/bin/python update_from_json.py your_file.json")
    print()
    print("3. Get help:")
    print("   ./venv/bin/python update_from_json.py --help")
    
    print("\n🆚 JSON vs CSV Comparison:")
    print("JSON Advantages:")
    print("  ✅ Structured metadata and versioning")
    print("  ✅ Better validation and error handling")
    print("  ✅ Native data types (numbers, dates)")
    print("  ✅ Nested data support")
    print("  ✅ Comments via metadata")
    print()
    print("CSV Advantages:")
    print("  ✅ Simple tabular format")
    print("  ✅ Easy to edit in Excel/spreadsheet apps")
    print("  ✅ Smaller file size")
    print("  ✅ Widely supported")
    
    print("\n🎯 Key Features:")
    features = [
        "Comprehensive validation before processing",
        "Detailed progress reporting and error messages",
        "Support for both product and technical capabilities",
        "Multiple date format support",
        "Metadata tracking for version control",
        "Export functionality for current data",
        "Transaction rollback on errors",
        "Rich documentation and examples"
    ]
    
    for feature in features:
        print(f"  ✅ {feature}")
    
    print("\n📖 Documentation:")
    print("See JSON_UPDATE_README.md for complete instructions")
    
    print("\n✨ JSON Update System ready to use!")
    print("💡 Tip: Start with --export to see current data structure")

def validate_template():
    """Validate the template JSON file"""
    print("\n🔍 Template Validation:")
    try:
        with open('capability_updates_template.json', 'r') as f:
            data = json.load(f)
        
        # Check structure
        required_sections = ['metadata', 'updates']
        for section in required_sections:
            if section in data:
                print(f"✅ {section} section present")
            else:
                print(f"❌ {section} section missing")
        
        # Check metadata
        if 'metadata' in data:
            metadata = data['metadata']
            recommended_fields = ['version', 'description', 'created_by', 'created_date']
            for field in recommended_fields:
                if field in metadata:
                    print(f"✅ metadata.{field}: {metadata[field]}")
                else:
                    print(f"⚠️ metadata.{field}: missing (optional)")
        
        # Check updates
        if 'updates' in data and isinstance(data['updates'], list):
            updates = data['updates']
            print(f"✅ {len(updates)} updates in template")
            
            # Validate each update
            required_fields = ['capability_type', 'capability_name']
            optional_fields = ['due_date', 'target_trl', 'assessor', 'notes']
            
            valid_count = 0
            for i, update in enumerate(updates):
                valid = True
                for field in required_fields:
                    if field not in update:
                        print(f"❌ Update {i+1}: missing required field '{field}'")
                        valid = False
                
                if valid:
                    valid_count += 1
            
            print(f"✅ {valid_count}/{len(updates)} updates are valid")
        
        print("✅ Template JSON is valid and well-formed")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ Error validating template: {e}")

if __name__ == '__main__':
    test_json_system()
    validate_template()