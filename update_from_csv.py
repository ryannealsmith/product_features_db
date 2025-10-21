#!/usr/bin/env python3
"""
CSV Update Script for Product Feature Readiness Database
This script updates due dates and TRL levels for capabilities from a CSV file.
"""

import csv
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
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date '{date_string}'. Skipping.")
    return None

def update_from_csv(csv_file_path):
    """Update capabilities and assessments from CSV file"""
    
    with app.app_context():
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate required columns
                required_columns = ['capability_type', 'capability_name']
                for col in required_columns:
                    if col not in reader.fieldnames:
                        print(f"Error: Required column '{col}' not found in CSV")
                        return False
                
                print(f"Processing CSV file: {csv_file_path}")
                print(f"Columns found: {', '.join(reader.fieldnames)}")
                print("-" * 60)
                
                updated_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    try:
                        capability_type = row['capability_type'].strip().lower()
                        capability_name = row['capability_name'].strip()
                        
                        if not capability_name:
                            print(f"Row {row_num}: Skipping empty capability name")
                            continue
                        
                        # Find the capability
                        if capability_type == 'product':
                            capability = ProductFeature.query.filter_by(name=capability_name).first()
                            if not capability:
                                print(f"Row {row_num}: Product feature '{capability_name}' not found")
                                error_count += 1
                                continue
                        elif capability_type == 'technical':
                            capability = TechnicalCapability.query.filter_by(name=capability_name).first()
                            if not capability:
                                print(f"Row {row_num}: Technical capability '{capability_name}' not found")
                                error_count += 1
                                continue
                        else:
                            print(f"Row {row_num}: Invalid capability_type '{capability_type}'. Must be 'product' or 'technical'")
                            error_count += 1
                            continue
                        
                        # Update due date if provided
                        if 'due_date' in row and row['due_date'].strip():
                            due_date = parse_date(row['due_date'])
                            if due_date:
                                # For technical capabilities, update all related assessments
                                if capability_type == 'technical':
                                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=capability.id).all()
                                    for assessment in assessments:
                                        assessment.next_review_date = due_date
                                    print(f"Row {row_num}: Updated due date for '{capability_name}' and {len(assessments)} assessments")
                                else:
                                    # For product features, update all related technical capability assessments
                                    tech_caps = TechnicalCapability.query.filter_by(product_feature_id=capability.id).all()
                                    assessment_count = 0
                                    for tech_cap in tech_caps:
                                        assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                                        for assessment in assessments:
                                            assessment.next_review_date = due_date
                                            assessment_count += 1
                                    print(f"Row {row_num}: Updated due date for '{capability_name}' and {assessment_count} related assessments")
                        
                        # Update TRL if provided
                        if 'target_trl' in row and row['target_trl'].strip():
                            try:
                                target_trl = int(row['target_trl'].strip())
                                if not (1 <= target_trl <= 9):
                                    print(f"Row {row_num}: Invalid TRL '{target_trl}'. Must be 1-9")
                                    error_count += 1
                                    continue
                                
                                trl_level = TechnicalReadinessLevel.query.filter_by(level=target_trl).first()
                                if not trl_level:
                                    print(f"Row {row_num}: TRL level {target_trl} not found in database")
                                    error_count += 1
                                    continue
                                
                                # Update TRL for technical capabilities
                                if capability_type == 'technical':
                                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=capability.id).all()
                                    for assessment in assessments:
                                        assessment.readiness_level_id = trl_level.id
                                        if 'assessor' in row and row['assessor'].strip():
                                            assessment.assessor = row['assessor'].strip()
                                        if 'notes' in row and row['notes'].strip():
                                            assessment.notes = row['notes'].strip()
                                        assessment.assessment_date = datetime.utcnow()
                                    print(f"Row {row_num}: Updated TRL to {target_trl} for '{capability_name}' and {len(assessments)} assessments")
                                else:
                                    # For product features, update all related technical capability assessments
                                    tech_caps = TechnicalCapability.query.filter_by(product_feature_id=capability.id).all()
                                    assessment_count = 0
                                    for tech_cap in tech_caps:
                                        assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                                        for assessment in assessments:
                                            assessment.readiness_level_id = trl_level.id
                                            if 'assessor' in row and row['assessor'].strip():
                                                assessment.assessor = row['assessor'].strip()
                                            if 'notes' in row and row['notes'].strip():
                                                assessment.notes = row['notes'].strip()
                                            assessment.assessment_date = datetime.utcnow()
                                            assessment_count += 1
                                    print(f"Row {row_num}: Updated TRL to {target_trl} for '{capability_name}' and {assessment_count} related assessments")
                            
                            except ValueError:
                                print(f"Row {row_num}: Invalid TRL value '{row['target_trl']}'. Must be a number 1-9")
                                error_count += 1
                                continue
                        
                        updated_count += 1
                        
                    except Exception as e:
                        print(f"Row {row_num}: Error processing row - {str(e)}")
                        error_count += 1
                        continue
                
                # Commit all changes
                db.session.commit()
                
                print("-" * 60)
                print(f"Update completed!")
                print(f"Successfully updated: {updated_count} capabilities")
                print(f"Errors encountered: {error_count}")
                
                return error_count == 0
                
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file_path}' not found")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return False

def export_current_data(output_file='current_capabilities.csv'):
    """Export current capabilities data to CSV for reference"""
    
    with app.app_context():
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['capability_type', 'capability_name', 'description', 'current_avg_trl', 'assessment_count', 'last_updated']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Export product features
                product_features = ProductFeature.query.all()
                for cap in product_features:
                    tech_caps = TechnicalCapability.query.filter_by(product_feature_id=cap.id).all()
                    total_assessments = 0
                    total_trl = 0
                    last_updated = None
                    
                    for tech_cap in tech_caps:
                        assessments = ReadinessAssessment.query.filter_by(technical_capability_id=tech_cap.id).all()
                        total_assessments += len(assessments)
                        for assessment in assessments:
                            total_trl += assessment.readiness_level.level
                            if not last_updated or assessment.assessment_date > last_updated:
                                last_updated = assessment.assessment_date
                    
                    avg_trl = round(total_trl / total_assessments, 1) if total_assessments > 0 else 0
                    
                    writer.writerow({
                        'capability_type': 'product',
                        'capability_name': cap.name,
                        'description': cap.description,
                        'current_avg_trl': avg_trl,
                        'assessment_count': total_assessments,
                        'last_updated': last_updated.strftime('%Y-%m-%d') if last_updated else ''
                    })
                
                # Export technical capabilities
                tech_caps = TechnicalCapability.query.all()
                for cap in tech_caps:
                    assessments = ReadinessAssessment.query.filter_by(technical_capability_id=cap.id).all()
                    total_trl = sum(assessment.readiness_level.level for assessment in assessments)
                    avg_trl = round(total_trl / len(assessments), 1) if assessments else 0
                    last_updated = max((assessment.assessment_date for assessment in assessments), default=None)
                    
                    writer.writerow({
                        'capability_type': 'technical',
                        'capability_name': cap.name,
                        'description': cap.description,
                        'current_avg_trl': avg_trl,
                        'assessment_count': len(assessments),
                        'last_updated': last_updated.strftime('%Y-%m-%d') if last_updated else ''
                    })
            
            print(f"Current capabilities data exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_from_csv.py <csv_file_path>           # Update from CSV")
        print("  python update_from_csv.py --export [output_file]    # Export current data")
        print("  python update_from_csv.py --help                    # Show this help")
        return
    
    if sys.argv[1] == '--help':
        print("CSV Update Script for Product Feature Readiness Database")
        print("")
        print("This script allows you to update due dates and TRL levels for capabilities")
        print("from a CSV file, or export current data for reference.")
        print("")
        print("CSV Format:")
        print("  Required columns: capability_type, capability_name")
        print("  Optional columns: due_date, target_trl, assessor, notes")
        print("")
        print("capability_type: 'product' or 'technical'")
        print("due_date: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, etc.")
        print("target_trl: 1-9")
        print("")
        print("Examples:")
        print("  python update_from_csv.py updates.csv")
        print("  python update_from_csv.py --export current_data.csv")
        return
    
    if sys.argv[1] == '--export':
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'current_capabilities.csv'
        export_current_data(output_file)
        return
    
    csv_file_path = sys.argv[1]
    success = update_from_csv(csv_file_path)
    
    if success:
        print("Update completed successfully!")
    else:
        print("Update completed with errors. Please check the output above.")
        sys.exit(1)

if __name__ == '__main__':
    main()