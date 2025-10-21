#!/usr/bin/env python3
"""
JSON Update Script for Product Feature Readiness Database
This script updates due dates and TRL levels for capabilities from a JSON file.
"""

import json
import sys
from datetime import datetime, date
from app import app, db, ProductFeature, TechnicalCapability, ReadinessAssessment, TechnicalReadinessLevel

def parse_date(date_string):
    """Parse date string in various formats"""
    if not date_string or date_string.strip() == '':
        return None
    
    date_string = date_string.strip()
    date_formats = [
        '%Y-%m-%d',        # 2025-12-31
        '%m/%d/%Y',        # 12/31/2025
        '%d/%m/%Y',        # 31/12/2025
        '%Y/%m/%d',        # 2025/12/31
        '%m-%d-%Y',        # 12-31-2025
        '%d-%m-%Y',        # 31-12-2025
        '%Y-%m-%dT%H:%M:%S',  # 2025-12-31T23:59:59
        '%Y-%m-%dT%H:%M:%SZ', # 2025-12-31T23:59:59Z
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date '{date_string}'. Skipping.")
    return None

def validate_capability_update(update_data, update_index):
    """Validate a single capability update entry"""
    errors = []
    
    # Check required fields
    if 'capability_type' not in update_data:
        errors.append("Missing required field 'capability_type'")
    elif update_data['capability_type'].lower() not in ['product', 'technical']:
        errors.append(f"Invalid capability_type '{update_data['capability_type']}'. Must be 'product' or 'technical'")
    
    if 'capability_name' not in update_data:
        errors.append("Missing required field 'capability_name'")
    elif not update_data['capability_name'].strip():
        errors.append("capability_name cannot be empty")
    
    # Validate optional fields
    if 'target_trl' in update_data:
        try:
            trl = int(update_data['target_trl'])
            if not (1 <= trl <= 9):
                errors.append(f"Invalid target_trl '{trl}'. Must be 1-9")
        except (ValueError, TypeError):
            errors.append(f"Invalid target_trl '{update_data['target_trl']}'. Must be a number 1-9")
    
    if 'due_date' in update_data and update_data['due_date']:
        if not parse_date(update_data['due_date']):
            errors.append(f"Invalid due_date format '{update_data['due_date']}'")
    
    if errors:
        print(f"Validation errors for update {update_index + 1}:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def update_capability(update_data, update_index):
    """Update a single capability based on the update data"""
    capability_type = update_data['capability_type'].strip().lower()
    capability_name = update_data['capability_name'].strip()
    
    # Find the capability
    if capability_type == 'product':
        capability = ProductFeature.query.filter_by(name=capability_name).first()
        if not capability:
            print(f"Update {update_index + 1}: Product feature '{capability_name}' not found")
            return False
    else:  # technical
        capability = TechnicalCapability.query.filter_by(name=capability_name).first()
        if not capability:
            print(f"Update {update_index + 1}: Technical capability '{capability_name}' not found")
            return False
    
    updates_made = []
    
    # Update due date if provided
    if 'due_date' in update_data and update_data['due_date']:
        due_date = parse_date(update_data['due_date'])
        if due_date:
            if capability_type == 'technical':
                assessments = ReadinessAssessment.query.filter_by(technical_capability_id=capability.id).all()
                for assessment in assessments:
                    assessment.next_review_date = due_date
                updates_made.append(f"due date to {due_date} for {len(assessments)} assessments")
            else:  # product
                tech_caps = TechnicalCapability.query.filter_by(product_feature_id=capability.id).all()
                assessment_count = 0
                for tech_cap in tech_caps:
                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                    for assessment in assessments:
                        assessment.next_review_date = due_date
                        assessment_count += 1
                updates_made.append(f"due date to {due_date} for {assessment_count} related assessments")
    
    # Update TRL if provided
    if 'target_trl' in update_data:
        target_trl = int(update_data['target_trl'])
        trl_level = TechnicalReadinessLevel.query.filter_by(level=target_trl).first()
        
        if trl_level:
            if capability_type == 'technical':
                assessments = ReadinessAssessment.query.filter_by(technical_capability_id=capability.id).all()
                for assessment in assessments:
                    assessment.readiness_level_id = trl_level.id
                    assessment.assessment_date = datetime.utcnow()
                    if 'assessor' in update_data:
                        assessment.assessor = update_data['assessor']
                    if 'notes' in update_data:
                        assessment.notes = update_data['notes']
                updates_made.append(f"TRL to {target_trl} for {len(assessments)} assessments")
            else:  # product
                tech_caps = TechnicalCapability.query.filter_by(product_feature_id=capability.id).all()
                assessment_count = 0
                for tech_cap in tech_caps:
                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                    for assessment in assessments:
                        assessment.readiness_level_id = trl_level.id
                        assessment.assessment_date = datetime.utcnow()
                        if 'assessor' in update_data:
                            assessment.assessor = update_data['assessor']
                        if 'notes' in update_data:
                            assessment.notes = update_data['notes']
                        assessment_count += 1
                updates_made.append(f"TRL to {target_trl} for {assessment_count} related assessments")
    
    if updates_made:
        print(f"Update {update_index + 1}: Updated {capability_name} - {', '.join(updates_made)}")
        return True
    else:
        print(f"Update {update_index + 1}: No updates specified for {capability_name}")
        return False

def update_from_json(json_file_path):
    """Update capabilities and assessments from JSON file"""
    
    with app.app_context():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            print(f"Processing JSON file: {json_file_path}")
            
            # Validate JSON structure
            if 'metadata' not in data:
                print("Warning: No metadata section found in JSON")
            else:
                metadata = data['metadata']
                print(f"Version: {metadata.get('version', 'unknown')}")
                print(f"Description: {metadata.get('description', 'no description')}")
                print(f"Created by: {metadata.get('created_by', 'unknown')}")
                if 'created_date' in metadata:
                    print(f"Created: {metadata['created_date']}")
            
            if 'updates' not in data:
                print("Error: No 'updates' section found in JSON file")
                return False
            
            updates = data['updates']
            if not isinstance(updates, list):
                print("Error: 'updates' must be a list")
                return False
            
            print(f"Found {len(updates)} updates to process")
            print("-" * 60)
            
            # Validate all updates first
            valid_updates = []
            for i, update in enumerate(updates):
                if validate_capability_update(update, i):
                    valid_updates.append((i, update))
            
            if not valid_updates:
                print("No valid updates found. Please fix validation errors and try again.")
                return False
            
            print(f"Processing {len(valid_updates)} valid updates...")
            print("-" * 60)
            
            updated_count = 0
            error_count = 0
            
            # Process valid updates
            for update_index, update_data in valid_updates:
                try:
                    if update_capability(update_data, update_index):
                        updated_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"Update {update_index + 1}: Error processing update - {str(e)}")
                    error_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print("-" * 60)
            print(f"Update completed!")
            print(f"Successfully updated: {updated_count} capabilities")
            print(f"Errors encountered: {error_count}")
            print(f"Total processed: {len(valid_updates)}")
            
            return error_count == 0
            
        except FileNotFoundError:
            print(f"Error: JSON file '{json_file_path}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {str(e)}")
            return False
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}")
            return False

def export_current_data(output_file='current_capabilities.json'):
    """Export current capabilities data to JSON for reference"""
    
    with app.app_context():
        try:
            export_data = {
                "metadata": {
                    "version": "1.0",
                    "description": "Current capabilities and readiness levels from Product Feature Readiness Database",
                    "exported_by": "update_from_json.py",
                    "export_date": datetime.now().isoformat(),
                    "total_product_features": ProductFeature.query.count(),
                    "total_technical_capabilities": TechnicalCapability.query.count(),
                    "total_assessments": ReadinessAssessment.query.count()
                },
                "product_features": [],
                "technical_capabilities": []
            }
            
            # Export product features
            product_features = ProductFeature.query.all()
            for cap in product_features:
                tech_caps = TechnicalCapability.query.filter_by(product_feature_id=cap.id).all()
                total_assessments = 0
                total_trl = 0
                last_updated = None
                next_review_dates = []
                
                for tech_cap in tech_caps:
                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                    total_assessments += len(assessments)
                    for assessment in assessments:
                        total_trl += assessment.readiness_level.level
                        if not last_updated or assessment.assessment_date > last_updated:
                            last_updated = assessment.assessment_date
                        if assessment.next_review_date:
                            next_review_dates.append(assessment.next_review_date.isoformat())
                
                avg_trl = round(total_trl / total_assessments, 1) if total_assessments > 0 else 0
                earliest_due = min(next_review_dates) if next_review_dates else None
                
                product_data = {
                    "capability_name": cap.name,
                    "description": cap.description,
                    "current_avg_trl": avg_trl,
                    "assessment_count": total_assessments,
                    "last_updated": last_updated.isoformat() if last_updated else None,
                    "earliest_due_date": earliest_due,
                    "technical_capabilities_count": len(tech_caps)
                }
                export_data["product_features"].append(product_data)
            
            # Export technical capabilities
            tech_caps = TechnicalCapability.query.all()
            for cap in tech_caps:
                assessments = ReadinessAssessment.query.filter_by(technical_capability_id=cap.id).all()
                total_trl = sum(assessment.readiness_level.level for assessment in assessments)
                avg_trl = round(total_trl / len(assessments), 1) if assessments else 0
                last_updated = max((assessment.assessment_date for assessment in assessments), default=None)
                due_dates = [assessment.next_review_date.isoformat() for assessment in assessments if assessment.next_review_date]
                earliest_due = min(due_dates) if due_dates else None
                
                technical_data = {
                    "capability_name": cap.name,
                    "description": cap.description,
                    "product_feature": cap.product_feature.name,
                    "current_avg_trl": avg_trl,
                    "assessment_count": len(assessments),
                    "last_updated": last_updated.isoformat() if last_updated else None,
                    "earliest_due_date": earliest_due
                }
                export_data["technical_capabilities"].append(technical_data)
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            print(f"Current capabilities data exported to: {output_file}")
            print(f"Product features: {len(export_data['product_features'])}")
            print(f"Technical capabilities: {len(export_data['technical_capabilities'])}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_from_json.py <json_file_path>           # Update from JSON")
        print("  python update_from_json.py --export [output_file]     # Export current data")
        print("  python update_from_json.py --help                     # Show this help")
        return
    
    if sys.argv[1] == '--help':
        print("JSON Update Script for Product Feature Readiness Database")
        print("")
        print("This script allows you to update due dates and TRL levels for capabilities")
        print("from a JSON file, or export current data for reference.")
        print("")
        print("JSON Structure:")
        print("  {")
        print('    "metadata": { ... },')
        print('    "updates": [')
        print("      {")
        print('        "capability_type": "product" or "technical",')
        print('        "capability_name": "exact capability name",')
        print('        "due_date": "YYYY-MM-DD",')
        print('        "target_trl": 1-9,')
        print('        "assessor": "assessor name",')
        print('        "notes": "assessment notes"')
        print("      }")
        print("    ]")
        print("  }")
        print("")
        print("Examples:")
        print("  python update_from_json.py updates.json")
        print("  python update_from_json.py --export current_data.json")
        return
    
    if sys.argv[1] == '--export':
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'current_capabilities.json'
        export_current_data(output_file)
        return
    
    json_file_path = sys.argv[1]
    success = update_from_json(json_file_path)
    
    if success:
        print("Update completed successfully!")
    else:
        print("Update completed with errors. Please check the output above.")
        sys.exit(1)

if __name__ == '__main__':
    main()