#!/usr/bin/env python3
"""
Enhanced JSON Update Script for Product Feature Readiness Database
This script allows comprehensive CRUD operations for Product Features, Capabilities, and Technical Functions.
Supports creating, updating, and managing relationships between entities.
"""

import json
import sys
from datetime import datetime, date
from app import app, db, ProductFeature, TechnicalFunction, ReadinessAssessment, TechnicalReadinessLevel, Capabilities, VehiclePlatform, ODD, Environment, Trailer

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

def validate_entity_data(entity_data, entity_index):
    """Validate entity data for any type (product_feature, capability, technical_function)"""
    errors = []
    
    # Check required fields
    if 'entity_type' not in entity_data:
        errors.append("Missing required field 'entity_type'")
    elif entity_data['entity_type'].lower() not in ['product_feature', 'capability', 'technical_function']:
        errors.append(f"Invalid entity_type '{entity_data['entity_type']}'. Must be 'product_feature', 'capability', or 'technical_function'")
    
    if 'operation' not in entity_data:
        errors.append("Missing required field 'operation'")
    elif entity_data['operation'].lower() not in ['create', 'update', 'delete']:
        errors.append(f"Invalid operation '{entity_data['operation']}'. Must be 'create', 'update', or 'delete'")
    
    if 'name' not in entity_data:
        errors.append("Missing required field 'name'")
    elif not entity_data['name'].strip():
        errors.append("name cannot be empty")
    
    # Validate dates if provided
    for date_field in ['planned_start_date', 'planned_end_date']:
        if date_field in entity_data and entity_data[date_field]:
            if not parse_date(entity_data[date_field]):
                errors.append(f"Invalid {date_field} format '{entity_data[date_field]}'")
    
    # Validate percentage fields
    for percent_field in ['status_relative_to_tmos', 'progress_relative_to_tmos']:
        if percent_field in entity_data:
            try:
                value = float(entity_data[percent_field])
                if not (0.0 <= value <= 100.0):
                    errors.append(f"Invalid {percent_field} '{value}'. Must be 0.0-100.0")
            except (ValueError, TypeError):
                errors.append(f"Invalid {percent_field} '{entity_data[percent_field]}'. Must be a number 0.0-100.0")
    
    if errors:
        print(f"Validation errors for entity {entity_index + 1}:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def find_or_create_references(reference_data, entity_type):
    """Find or create reference entities based on names or labels"""
    references = []
    
    if not reference_data:
        return references
    
    for ref_name in reference_data:
        ref_entity = None
        
        if entity_type == 'product_feature':
            # Try by name first, then by label
            ref_entity = ProductFeature.query.filter_by(name=ref_name).first()
            if not ref_entity:
                ref_entity = ProductFeature.query.filter_by(label=ref_name).first()
        elif entity_type == 'capability':
            # Try by name first, then by label
            ref_entity = Capabilities.query.filter_by(name=ref_name).first()
            if not ref_entity:
                ref_entity = Capabilities.query.filter_by(label=ref_name).first()
        elif entity_type == 'technical_function':
            # Try by name first, then by label
            ref_entity = TechnicalFunction.query.filter_by(name=ref_name).first()
            if not ref_entity:
                ref_entity = TechnicalFunction.query.filter_by(label=ref_name).first()
        else:
            continue
        
        if ref_entity:
            references.append(ref_entity)
        else:
            print(f"Warning: Referenced {entity_type} '{ref_name}' not found by name or label, skipping")
    
    return references

def get_vehicle_platform_id(vehicle_type_or_id):
    """Get vehicle platform ID from vehicle type string or existing ID"""
    if not vehicle_type_or_id:
        return None
    
    # If it's already a number, return it
    if isinstance(vehicle_type_or_id, int):
        return vehicle_type_or_id
    
    # If it's a string number, convert it
    try:
        return int(vehicle_type_or_id)
    except (ValueError, TypeError):
        pass
    
    # Map vehicle type string to platform ID
    mapping = {
        "truck": 5,      # All (Generic Platform) - used for general truck features
        "van": 2,        # CA500 
        "car": 4,        # AEV
        "terberg": 1,    # Terberg ATT
        "ca500": 2,      # CA500
        "t800": 3,       # T800
        "aev": 4,        # AEV
        "generic": 5,    # All (Generic Platform)
        "all": 5         # All (Generic Platform)
    }
    
    platform_id = mapping.get(str(vehicle_type_or_id).lower(), 8)  # Default to Generic Platform
    return platform_id

def create_product_feature(data):
    """Create a new product feature with robust M:N capability linking"""
    try:
        # Check if already exists by name or label
        existing = None
        if 'name' in data and data['name']:
            existing = ProductFeature.query.filter_by(name=data['name']).first()
        if not existing and 'label' in data and data['label']:
            existing = ProductFeature.query.filter_by(label=data['label']).first()
        
        if existing:
            print(f"Product feature '{data.get('name', data.get('label', 'unknown'))}' already exists, skipping creation")
            return False
        
        # Handle both old and new vehicle field formats
        vehicle_platform_id = None
        if 'vehicle_platform_id' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
        elif 'vehicle_type' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
        
        product_feature = ProductFeature(
            name=data['name'],
            description=data.get('description', ''),
            vehicle_platform_id=vehicle_platform_id,
            swimlane_decorators=data.get('swimlane_decorators', ''),
            label=data.get('label', ''),
            tmos=data.get('tmos', ''),
            status_relative_to_tmos=float(data.get('status_relative_to_tmos', 0.0)),
            planned_start_date=parse_date(data.get('planned_start_date')),
            planned_end_date=parse_date(data.get('planned_end_date')),
            active_flag=data.get('active_flag', 'next'),
            document_url=data.get('document_url')
        )
        
        db.session.add(product_feature)
        db.session.flush()  # Get the ID
        
        # Handle M:N relationships with capabilities - use robust matching
        capabilities_list = data.get('capabilities') or data.get('capabilities_required', [])
        linked_capabilities = []
        
        if capabilities_list:
            for cap_ref in capabilities_list:
                # Try finding by label first (more reliable), then by name
                cap = Capabilities.query.filter_by(label=cap_ref).first()
                if not cap:
                    cap = Capabilities.query.filter_by(name=cap_ref).first()
                
                if cap:
                    if cap not in product_feature.capabilities:
                        product_feature.capabilities.append(cap)
                        linked_capabilities.append(cap)
                else:
                    print(f"⚠️  Capability '{cap_ref}' not found for product feature '{product_feature.label or product_feature.name}'")
        
        # Handle dependencies (other product features)
        if 'dependencies' in data:
            dependencies = find_or_create_references(data['dependencies'], 'product_feature')
            product_feature.dependencies.extend(dependencies)
        
        print(f"Created product feature: {product_feature.name} (linked to {len(linked_capabilities)} capabilities)")
        return True
        
    except Exception as e:
        print(f"Error creating product feature: {str(e)}")
        return False

def update_product_feature(data):
    """Update an existing product feature with robust M:N capability linking"""
    try:
        # Find product feature by name or label
        product_feature = None
        if 'name' in data and data['name']:
            product_feature = ProductFeature.query.filter_by(name=data['name']).first()
        if not product_feature and 'label' in data and data['label']:
            product_feature = ProductFeature.query.filter_by(label=data['label']).first()
        
        if not product_feature:
            print(f"Product feature '{data.get('name', data.get('label', 'unknown'))}' not found for update")
            return False
        
        # Update fields if provided
        fields_to_update = ['description', 'swimlane_decorators', 'label', 
                           'tmos', 'status_relative_to_tmos', 'active_flag', 'document_url']
        
        updates_made = []
        for field in fields_to_update:
            if field in data:
                if field == 'status_relative_to_tmos':
                    setattr(product_feature, field, float(data[field]))
                else:
                    setattr(product_feature, field, data[field])
                updates_made.append(field)
        
        # Handle vehicle platform updates
        if 'vehicle_platform_id' in data:
            product_feature.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
            updates_made.append('vehicle_platform_id')
        elif 'vehicle_type' in data:
            product_feature.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
            updates_made.append('vehicle_platform_id')
        
        # Update dates
        for date_field in ['planned_start_date', 'planned_end_date']:
            if date_field in data:
                setattr(product_feature, date_field, parse_date(data[date_field]))
                updates_made.append(date_field)
        
        # Update M:N relationships with capabilities - use robust matching
        capabilities_list = data.get('capabilities') or data.get('capabilities_required')
        if capabilities_list is not None:  # Check for None to allow empty lists
            product_feature.capabilities.clear()
            linked_capabilities = []
            
            for cap_ref in capabilities_list:
                # Try finding by label first (more reliable), then by name
                cap = Capabilities.query.filter_by(label=cap_ref).first()
                if not cap:
                    cap = Capabilities.query.filter_by(name=cap_ref).first()
                
                if cap:
                    if cap not in product_feature.capabilities:
                        product_feature.capabilities.append(cap)
                        linked_capabilities.append(cap)
                else:
                    print(f"⚠️  Capability '{cap_ref}' not found for product feature update")
            
            updates_made.append(f'capabilities ({len(linked_capabilities)} linked)')
        
        if 'dependencies' in data:
            product_feature.dependencies.clear()
            dependencies = find_or_create_references(data['dependencies'], 'product_feature')
            product_feature.dependencies.extend(dependencies)
            updates_made.append('dependencies')
        
        print(f"Updated product feature '{product_feature.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating product feature: {str(e)}")
        return False

def create_capability(data):
    """Create a new capability with many-to-many ProductFeature relationships"""
    try:
        # Check if already exists by name or label
        existing = None
        if 'name' in data and data['name']:
            existing = Capabilities.query.filter_by(name=data['name']).first()
        if not existing and 'label' in data and data['label']:
            existing = Capabilities.query.filter_by(label=data['label']).first()
        
        if existing:
            print(f"Capability '{data.get('name', data.get('label', 'unknown'))}' already exists, skipping creation")
            return False
        
        # Handle both old and new vehicle field formats
        vehicle_platform_id = None
        if 'vehicle_platform_id' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
        elif 'vehicle_type' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
        
        capability = Capabilities(
            name=data['name'],
            label=data.get('label', ''),
            success_criteria=data.get('success_criteria', ''),
            vehicle_platform_id=vehicle_platform_id,
            planned_start_date=parse_date(data.get('planned_start_date')),
            planned_end_date=parse_date(data.get('planned_end_date')),
            tmos=data.get('tmos', ''),
            progress_relative_to_tmos=float(data.get('progress_relative_to_tmos', 0.0)),
            document_url=data.get('document_url')
        )
        
        db.session.add(capability)
        db.session.flush()  # Get the ID
        
        # Handle M:N relationships with ProductFeatures - use robust matching
        product_features_to_link = []
        
        if 'product_feature_ids' in data and data['product_feature_ids']:
            # New M:N format - array of product feature names/labels
            for pf_ref in data['product_feature_ids']:
                # Try finding by label first (more reliable), then by name
                pf = ProductFeature.query.filter_by(label=pf_ref).first()
                if not pf:
                    pf = ProductFeature.query.filter_by(name=pf_ref).first()
                
                if pf:
                    product_features_to_link.append(pf)
                else:
                    print(f"⚠️  Product Feature '{pf_ref}' not found for capability '{capability.label or capability.name}'")
                    
        elif 'product_feature' in data and data['product_feature']:
            # Old 1:N format compatibility - single product feature name/label
            pf_ref = data['product_feature']
            pf = ProductFeature.query.filter_by(label=pf_ref).first()
            if not pf:
                pf = ProductFeature.query.filter_by(name=pf_ref).first()
            
            if pf:
                product_features_to_link.append(pf)
            else:
                print(f"⚠️  Product Feature '{pf_ref}' not found for capability '{capability.label or capability.name}'")
        
        # Link to ProductFeatures using the many-to-many relationship
        for pf in product_features_to_link:
            if capability not in pf.capabilities:
                pf.capabilities.append(capability)
        
        # Handle relationships with TechnicalFunctions
        if 'technical_functions' in data:
            tech_functions = find_or_create_references(data['technical_functions'], 'technical_function')
            capability.technical_functions.extend(tech_functions)
        
        print(f"Created capability: {capability.name} (linked to {len(product_features_to_link)} product features)")
        return True
        
    except Exception as e:
        print(f"Error creating capability: {str(e)}")
        return False

def update_capability(data):
    """Update an existing capability with M:N ProductFeature relationships"""
    try:
        # Find capability by name or label
        capability = None
        if 'name' in data and data['name']:
            capability = Capabilities.query.filter_by(name=data['name']).first()
        if not capability and 'label' in data and data['label']:
            capability = Capabilities.query.filter_by(label=data['label']).first()
        
        if not capability:
            print(f"Capability '{data.get('name', data.get('label', 'unknown'))}' not found for update")
            return False
        
        # Update fields if provided
        fields_to_update = ['label', 'success_criteria', 'tmos', 'progress_relative_to_tmos', 'document_url']
        
        updates_made = []
        for field in fields_to_update:
            if field in data:
                if field == 'progress_relative_to_tmos':
                    setattr(capability, field, float(data[field]))
                else:
                    setattr(capability, field, data[field])
                updates_made.append(field)
        
        # Handle vehicle platform updates
        if 'vehicle_platform_id' in data:
            capability.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
            updates_made.append('vehicle_platform_id')
        elif 'vehicle_type' in data:
            capability.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
            updates_made.append('vehicle_platform_id')
        
        # Update dates
        for date_field in ['planned_start_date', 'planned_end_date']:
            if date_field in data:
                setattr(capability, date_field, parse_date(data[date_field]))
                updates_made.append(date_field)
        
        # Update M:N relationships with ProductFeatures - use robust matching
        if 'product_feature_ids' in data:
            # New M:N format - clear existing and add new relationships with robust matching
            # Clear existing relationships by removing this capability from all product features
            for pf in list(capability.product_features):  # Use list() to avoid modification during iteration
                pf.capabilities.remove(capability)
            
            # Add new relationships with robust matching
            for pf_ref in data['product_feature_ids']:
                # Try finding by label first (more reliable), then by name
                pf = ProductFeature.query.filter_by(label=pf_ref).first()
                if not pf:
                    pf = ProductFeature.query.filter_by(name=pf_ref).first()
                
                if pf:
                    if capability not in pf.capabilities:
                        pf.capabilities.append(capability)
                else:
                    print(f"⚠️  Product Feature '{pf_ref}' not found for capability update")
            updates_made.append('product_feature_ids')
            
        elif 'product_feature' in data:
            # Old 1:N format compatibility - clear existing and add single relationship
            for pf in list(capability.product_features):
                pf.capabilities.remove(capability)
            
            pf_ref = data['product_feature']
            pf = ProductFeature.query.filter_by(label=pf_ref).first()
            if not pf:
                pf = ProductFeature.query.filter_by(name=pf_ref).first()
            
            if pf:
                if capability not in pf.capabilities:
                    pf.capabilities.append(capability)
                updates_made.append('product_feature')
            else:
                print(f"⚠️  Product Feature '{pf_ref}' not found for capability update")
        
        # Update relationships with TechnicalFunctions
        if 'technical_functions' in data:
            capability.technical_functions.clear()
            tech_functions = find_or_create_references(data['technical_functions'], 'technical_function')
            capability.technical_functions.extend(tech_functions)
            updates_made.append('technical_functions')
        
        print(f"Updated capability '{capability.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating capability: {str(e)}")
        return False

def create_technical_function(data):
    """Create a new technical function"""
    try:
        # Check if already exists
        existing = TechnicalFunction.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Technical function '{data['name']}' already exists, skipping creation")
            return False
        
        # Handle both old and new vehicle field formats
        vehicle_platform_id = None
        if 'vehicle_platform_id' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
        elif 'vehicle_type' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
        
        technical_function = TechnicalFunction(
            name=data['name'],
            description=data.get('description', ''),
            success_criteria=data.get('success_criteria', ''),
            vehicle_platform_id=vehicle_platform_id,
            tmos=data.get('tmos', ''),
            status_relative_to_tmos=float(data.get('status_relative_to_tmos', 0.0)),
            planned_start_date=parse_date(data.get('planned_start_date')),
            planned_end_date=parse_date(data.get('planned_end_date')),
            document_url=data.get('document_url')
        )
        
        db.session.add(technical_function)
        db.session.flush()  # Get the ID
        
        # Handle relationships - TechnicalFunctions are now linked through Capabilities
        if 'capabilities' in data:
            capabilities = find_or_create_references(data['capabilities'], 'capability')
            technical_function.capabilities.extend(capabilities)
        
        print(f"Created technical function: {technical_function.name}")
        return True
        
    except Exception as e:
        print(f"Error creating technical function: {str(e)}")
        return False

def update_technical_function(data):
    """Update an existing technical function"""
    try:
        technical_function = TechnicalFunction.query.filter_by(name=data['name']).first()
        if not technical_function:
            print(f"Technical function '{data['name']}' not found for update")
            return False
        
        # Update fields if provided
        fields_to_update = ['description', 'success_criteria', 'tmos', 'status_relative_to_tmos', 'document_url']
        
        updates_made = []
        for field in fields_to_update:
            if field in data:
                if field == 'status_relative_to_tmos':
                    setattr(technical_function, field, float(data[field]))
                else:
                    setattr(technical_function, field, data[field])
                updates_made.append(field)
        
        # Handle vehicle platform updates
        if 'vehicle_platform_id' in data:
            technical_function.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
            updates_made.append('vehicle_platform_id')
        elif 'vehicle_type' in data:
            technical_function.vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
            updates_made.append('vehicle_platform_id')
        
        # Update dates
        for date_field in ['planned_start_date', 'planned_end_date']:
            if date_field in data:
                setattr(technical_function, date_field, parse_date(data[date_field]))
                updates_made.append(date_field)
        
        # Update relationships - TechnicalFunctions are now linked through Capabilities
        if 'capabilities' in data:
            technical_function.capabilities.clear()
            capabilities = find_or_create_references(data['capabilities'], 'capability')
            technical_function.capabilities.extend(capabilities)
            updates_made.append('capabilities')
        
        print(f"Updated technical function '{technical_function.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating technical function: {str(e)}")
        return False

def delete_entity(data):
    """Delete an entity (product feature, capability, or technical function)"""
    try:
        entity_type = data['entity_type'].lower()
        name = data['name']
        
        if entity_type == 'product_feature':
            entity = ProductFeature.query.filter_by(name=name).first()
        elif entity_type == 'capability':
            entity = Capabilities.query.filter_by(name=name).first()
        elif entity_type == 'technical_function':
            entity = TechnicalFunction.query.filter_by(name=name).first()
        else:
            print(f"Unknown entity type: {entity_type}")
            return False
        
        if not entity:
            print(f"{entity_type.replace('_', ' ').title()} '{name}' not found for deletion")
            return False
        
        # Check for dependencies before deletion
        dependencies = []
        if entity_type == 'product_feature':
            # Check for capabilities linked to this product feature (M:N relationship)
            capabilities_count = len(entity.capabilities)
            if capabilities_count > 0:
                dependencies.append(f"{capabilities_count} capabilities")
        elif entity_type == 'capability':
            # Check for technical functions linked to this capability (M:N relationship)
            tech_functions_count = len(entity.technical_functions)
            if tech_functions_count > 0:
                dependencies.append(f"{tech_functions_count} technical functions")
            # Check for product features linked to this capability (M:N relationship)
            product_features_count = len(entity.product_features)
            if product_features_count > 0:
                dependencies.append(f"{product_features_count} product features")
        elif entity_type == 'technical_function':
            assessments = ReadinessAssessment.query.filter_by(technical_capability_id=entity.id).count()
            if assessments > 0:
                dependencies.append(f"{assessments} readiness assessments")
        
        if dependencies and not data.get('force_delete', False):
            print(f"Cannot delete {entity_type.replace('_', ' ')} '{name}': has {', '.join(dependencies)}")
            print("Use 'force_delete': true to override")
            return False
        
        db.session.delete(entity)
        print(f"Deleted {entity_type.replace('_', ' ')} '{name}'")
        return True
        
    except Exception as e:
        print(f"Error deleting entity: {str(e)}")
        return False

def process_entity(entity_data, entity_index):
    """Process a single entity (create, update, or delete)"""
    try:
        entity_type = entity_data['entity_type'].lower()
        operation = entity_data['operation'].lower()
        
        if operation == 'delete':
            return delete_entity(entity_data)
        elif operation == 'create':
            if entity_type == 'product_feature':
                return create_product_feature(entity_data)
            elif entity_type == 'capability':
                return create_capability(entity_data)
            elif entity_type == 'technical_function':
                return create_technical_function(entity_data)
        elif operation == 'update':
            if entity_type == 'product_feature':
                return update_product_feature(entity_data)
            elif entity_type == 'capability':
                return update_capability(entity_data)
            elif entity_type == 'technical_function':
                return update_technical_function(entity_data)
        
        print(f"Unknown operation: {operation}")
        return False
        
    except Exception as e:
        print(f"Error processing entity {entity_index + 1}: {str(e)}")
        return False

def create_technical_readiness_level(data):
    """Create a new Technical Readiness Level"""
    try:
        level = data.get('level')
        if level is None:
            print("Error: 'level' is required for TRL creation")
            return False
        
        # Check if TRL with this level already exists
        existing = TechnicalReadinessLevel.query.filter_by(level=level).first()
        if existing:
            print(f"Error: Technical Readiness Level with level {level} already exists")
            return False
        
        trl = TechnicalReadinessLevel(
            level=level,
            name=data.get('name', ''),
            description=data.get('description', '')
        )
        
        db.session.add(trl)
        print(f"Created Technical Readiness Level: {trl.name}")
        return True
    except Exception as e:
        print(f"Error creating Technical Readiness Level: {str(e)}")
        return False


def delete_vehicle_platform(data):
    """Delete a Vehicle Platform"""
    try:
        name = data.get('name')
        if not name:
            print("Error: 'name' is required for vehicle platform deletion")
            return False
        
        platform = VehiclePlatform.query.filter_by(name=name).first()
        if not platform:
            print(f"Error: Vehicle Platform '{name}' not found")
            return False
        
        db.session.delete(platform)
        print(f"Deleted Vehicle Platform: {name}")
        return True
    except Exception as e:
        print(f"Error deleting Vehicle Platform: {str(e)}")
        return False


def delete_odd(data):
    """Delete an ODD"""
    try:
        name = data.get('name')
        if not name:
            print("Error: 'name' is required for ODD deletion")
            return False
        
        odd = ODD.query.filter_by(name=name).first()
        if not odd:
            print(f"Error: ODD '{name}' not found")
            return False
        
        db.session.delete(odd)
        print(f"Deleted ODD: {name}")
        return True
    except Exception as e:
        print(f"Error deleting ODD: {str(e)}")
        return False


def delete_environment(data):
    """Delete an Environment"""
    try:
        name = data.get('name')
        if not name:
            print("Error: 'name' is required for environment deletion")
            return False
        
        environment = Environment.query.filter_by(name=name).first()
        if not environment:
            print(f"Error: Environment '{name}' not found")
            return False
        
        db.session.delete(environment)
        print(f"Deleted Environment: {name}")
        return True
    except Exception as e:
        print(f"Error deleting Environment: {str(e)}")
        return False


def delete_trailer(data):
    """Delete a Trailer"""
    try:
        name = data.get('name')
        if not name:
            print("Error: 'name' is required for trailer deletion")
            return False
        
        trailer = Trailer.query.filter_by(name=name).first()
        if not trailer:
            print(f"Error: Trailer '{name}' not found")
            return False
        
        db.session.delete(trailer)
        print(f"Deleted Trailer: {name}")
        return True
    except Exception as e:
        print(f"Error deleting Trailer: {str(e)}")
        return False


def delete_technical_readiness_level(data):
    """Delete a Technical Readiness Level"""
    try:
        level = data.get('level')
        if level is None:
            print("Error: 'level' is required for TRL deletion")
            return False
        
        trl = TechnicalReadinessLevel.query.filter_by(level=level).first()
        if not trl:
            print(f"Error: Technical Readiness Level with level {level} not found")
            return False
        
        db.session.delete(trl)
        print(f"Deleted Technical Readiness Level: {trl.name}")
        return True
    except Exception as e:
        print(f"Error deleting Technical Readiness Level: {str(e)}")
        return False


def validate_configuration_data(config, config_index):
    """Validate configuration data for system configurations"""
    errors = []
    
    # Handle both old format (direct fields) and new format (type/data nested)
    if 'config_type' in config:
        # Old format compatibility
        config_type = config.get('config_type', '').lower()
        operation = config.get('operation', '').lower()
        data = {k: v for k, v in config.items() if k not in ['config_type', 'operation', '_comment']}
    elif 'type' in config:
        # New format
        config_type = config.get('type', '').lower()
        operation = config.get('operation', '').lower()
        data = config.get('data', {})
    else:
        errors.append("Missing required field 'config_type' or 'type'")
        config_type = ''
        operation = ''
        data = {}
    
    # Validate config type
    if not config_type:
        errors.append("Missing configuration type")
    elif config_type not in ['vehicle_platform', 'odd', 'environment', 'trailer', 'technical_readiness_level']:
        errors.append(f"Invalid config type '{config_type}'. Must be 'vehicle_platform', 'odd', 'environment', 'trailer', or 'technical_readiness_level'")
    
    # Validate operation
    if not operation:
        errors.append("Missing required field 'operation'")
    elif operation not in ['create', 'update', 'delete']:
        errors.append(f"Invalid operation '{operation}'. Must be 'create', 'update', or 'delete'")
    
    # Validate data requirements
    if config_type == 'technical_readiness_level':
        if 'level' not in data:
            errors.append("Missing required field 'level' for technical_readiness_level")
        elif not isinstance(data['level'], int) or not (1 <= data['level'] <= 9):
            errors.append("level must be an integer between 1 and 9 for technical_readiness_level")
    else:
        if 'name' not in data:
            errors.append("Missing required field 'name'")
        elif not data['name'].strip():
            errors.append("name cannot be empty")
    
    # Validate numeric fields
    numeric_fields = ['max_payload', 'max_speed', 'length', 'max_weight', 'axle_count']
    for field in numeric_fields:
        if field in data:
            try:
                float(data[field])
            except (ValueError, TypeError):
                errors.append(f"Invalid {field} '{data[field]}'. Must be a number")
    
    if errors:
        print(f"Validation errors for configuration {config_index + 1}:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def create_vehicle_platform(data):
    """Create a new vehicle platform"""
    try:
        existing = VehiclePlatform.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Vehicle platform '{data['name']}' already exists, skipping creation")
            return False
        
        platform = VehiclePlatform(
            name=data['name'],
            description=data.get('description', ''),
            vehicle_type=data.get('vehicle_type', ''),
            max_payload=float(data['max_payload']) if 'max_payload' in data else None
        )
        
        db.session.add(platform)
        print(f"Created vehicle platform: {platform.name}")
        return True
        
    except Exception as e:
        print(f"Error creating vehicle platform: {str(e)}")
        return False

def update_vehicle_platform(data):
    """Update an existing vehicle platform"""
    try:
        platform = VehiclePlatform.query.filter_by(name=data['name']).first()
        if not platform:
            print(f"Vehicle platform '{data['name']}' not found for update")
            return False
        
        updates_made = []
        fields_to_update = ['description', 'vehicle_type', 'max_payload']
        
        for field in fields_to_update:
            if field in data:
                if field == 'max_payload':
                    setattr(platform, field, float(data[field]) if data[field] else None)
                else:
                    setattr(platform, field, data[field])
                updates_made.append(field)
        
        print(f"Updated vehicle platform '{platform.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating vehicle platform: {str(e)}")
        return False

def create_odd(data):
    """Create a new ODD"""
    try:
        existing = ODD.query.filter_by(name=data['name']).first()
        if existing:
            print(f"ODD '{data['name']}' already exists, skipping creation")
            return False
        
        odd = ODD(
            name=data['name'],
            description=data.get('description', ''),
            max_speed=int(data['max_speed']) if 'max_speed' in data else None,
            direction=data.get('direction', ''),
            lanes=data.get('lanes', ''),
            intersections=data.get('intersections', ''),
            infrastructure=data.get('infrastructure', ''),
            hazards=data.get('hazards', ''),
            actors=data.get('actors', ''),
            handling_equipment=data.get('handling_equipment', ''),
            traction=data.get('traction', ''),
            inclines=data.get('inclines', '')
        )
        
        db.session.add(odd)
        print(f"Created ODD: {odd.name}")
        return True
        
    except Exception as e:
        print(f"Error creating ODD: {str(e)}")
        return False

def update_odd(data):
    """Update an existing ODD"""
    try:
        odd = ODD.query.filter_by(name=data['name']).first()
        if not odd:
            print(f"ODD '{data['name']}' not found for update")
            return False
        
        updates_made = []
        fields_to_update = ['description', 'max_speed', 'direction', 'lanes', 'intersections', 
                           'infrastructure', 'hazards', 'actors', 'handling_equipment', 'traction', 'inclines']
        
        for field in fields_to_update:
            if field in data:
                if field == 'max_speed':
                    setattr(odd, field, int(data[field]) if data[field] else None)
                else:
                    setattr(odd, field, data[field])
                updates_made.append(field)
        
        print(f"Updated ODD '{odd.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating ODD: {str(e)}")
        return False

def create_environment(data):
    """Create a new environment"""
    try:
        existing = Environment.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Environment '{data['name']}' already exists, skipping creation")
            return False
        
        environment = Environment(
            name=data['name'],
            description=data.get('description', ''),
            region=data.get('region', ''),
            climate=data.get('climate', ''),
            terrain=data.get('terrain', '')
        )
        
        db.session.add(environment)
        print(f"Created environment: {environment.name}")
        return True
        
    except Exception as e:
        print(f"Error creating environment: {str(e)}")
        return False

def update_environment(data):
    """Update an existing environment"""
    try:
        environment = Environment.query.filter_by(name=data['name']).first()
        if not environment:
            print(f"Environment '{data['name']}' not found for update")
            return False
        
        updates_made = []
        fields_to_update = ['description', 'region', 'climate', 'terrain']
        
        for field in fields_to_update:
            if field in data:
                setattr(environment, field, data[field])
                updates_made.append(field)
        
        print(f"Updated environment '{environment.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating environment: {str(e)}")
        return False

def create_trailer(data):
    """Create a new trailer"""
    try:
        existing = Trailer.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Trailer '{data['name']}' already exists, skipping creation")
            return False
        
        trailer = Trailer(
            name=data['name'],
            description=data.get('description', ''),
            trailer_type=data.get('trailer_type', ''),
            length=float(data['length']) if 'length' in data else None,
            max_weight=float(data['max_weight']) if 'max_weight' in data else None,
            axle_count=int(data['axle_count']) if 'axle_count' in data else None
        )
        
        db.session.add(trailer)
        print(f"Created trailer: {trailer.name}")
        return True
        
    except Exception as e:
        print(f"Error creating trailer: {str(e)}")
        return False

def update_trailer(data):
    """Update an existing trailer"""
    try:
        trailer = Trailer.query.filter_by(name=data['name']).first()
        if not trailer:
            print(f"Trailer '{data['name']}' not found for update")
            return False
        
        updates_made = []
        fields_to_update = ['description', 'trailer_type', 'length', 'max_weight', 'axle_count']
        
        for field in fields_to_update:
            if field in data:
                if field in ['length', 'max_weight']:
                    setattr(trailer, field, float(data[field]) if data[field] else None)
                elif field == 'axle_count':
                    setattr(trailer, field, int(data[field]) if data[field] else None)
                else:
                    setattr(trailer, field, data[field])
                updates_made.append(field)
        
        print(f"Updated trailer '{trailer.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating trailer: {str(e)}")
        return False

def update_technical_readiness_level(data):
    """Update an existing technical readiness level"""
    try:
        trl = TechnicalReadinessLevel.query.filter_by(level=data['level']).first()
        if not trl:
            print(f"Technical Readiness Level {data['level']} not found for update")
            return False
        
        updates_made = []
        fields_to_update = ['name', 'description']
        
        for field in fields_to_update:
            if field in data:
                setattr(trl, field, data[field])
                updates_made.append(field)
        
        print(f"Updated TRL {trl.level} '{trl.name}': {', '.join(updates_made)}")
        return True
        
    except Exception as e:
        print(f"Error updating technical readiness level: {str(e)}")
        return False

def delete_configuration(data):
    """Delete a configuration entity"""
    try:
        config_type = data['config_type'].lower()
        
        if config_type == 'vehicle_platform':
            entity = VehiclePlatform.query.filter_by(name=data['name']).first()
        elif config_type == 'odd':
            entity = ODD.query.filter_by(name=data['name']).first()
        elif config_type == 'environment':
            entity = Environment.query.filter_by(name=data['name']).first()
        elif config_type == 'trailer':
            entity = Trailer.query.filter_by(name=data['name']).first()
        elif config_type == 'technical_readiness_level':
            print("Cannot delete Technical Readiness Levels - they are system-defined")
            return False
        else:
            print(f"Unknown configuration type: {config_type}")
            return False
        
        if not entity:
            identifier = data.get('name', data.get('level', 'unknown'))
            print(f"{config_type.replace('_', ' ').title()} '{identifier}' not found for deletion")
            return False
        
        # Check for dependencies
        dependencies = []
        if hasattr(entity, 'readiness_assessments'):
            assessment_count = len(entity.readiness_assessments)
            if assessment_count > 0:
                dependencies.append(f"{assessment_count} readiness assessments")
        
        if dependencies and not data.get('force_delete', False):
            print(f"Cannot delete {config_type.replace('_', ' ')} '{entity.name}': has {', '.join(dependencies)}")
            print("Use 'force_delete': true to override")
            return False
        
        db.session.delete(entity)
        print(f"Deleted {config_type.replace('_', ' ')} '{entity.name}'")
        return True
        
    except Exception as e:
        print(f"Error deleting configuration: {str(e)}")
        return False

def process_configuration(config_data, config_index):
    """Process a single configuration (create, update, or delete)"""
    try:
        config_type = config_data['config_type'].lower()
        operation = config_data['operation'].lower()
        
        if operation == 'delete':
            return delete_configuration(config_data)
        elif operation == 'create':
            if config_type == 'vehicle_platform':
                return create_vehicle_platform(config_data)
            elif config_type == 'odd':
                return create_odd(config_data)
            elif config_type == 'environment':
                return create_environment(config_data)
            elif config_type == 'trailer':
                return create_trailer(config_data)
            elif config_type == 'technical_readiness_level':
                print("Cannot create new Technical Readiness Levels - use update operation instead")
                return False
        elif operation == 'update':
            if config_type == 'vehicle_platform':
                return update_vehicle_platform(config_data)
            elif config_type == 'odd':
                return update_odd(config_data)
            elif config_type == 'environment':
                return update_environment(config_data)
            elif config_type == 'trailer':
                return update_trailer(config_data)
            elif config_type == 'technical_readiness_level':
                return update_technical_readiness_level(config_data)
        
        print(f"Unknown operation or configuration type: {operation}, {config_type}")
        return False
        
    except Exception as e:
        print(f"Error processing configuration {config_index + 1}: {str(e)}")
        return False

def process_configuration(config_data, config_index):
    """Process a single configuration based on its type and operation"""
    try:
        # Handle both old format (config_type) and new format (type)
        if 'config_type' in config_data:
            config_type = config_data['config_type']
            operation = config_data['operation'].lower()
            data = {k: v for k, v in config_data.items() if k not in ['config_type', 'operation', '_comment']}
        else:
            config_type = config_data['type']
            operation = config_data['operation'].lower()
            data = config_data['data']
        
        print(f"Configuration {config_index + 1}: {operation.upper()} {config_type}")
        
        # Route to appropriate function based on type and operation
        if config_type == 'vehicle_platform':
            if operation == 'create':
                return create_vehicle_platform(data)
            elif operation == 'update':
                return update_vehicle_platform(data)
            elif operation == 'delete':
                return delete_vehicle_platform(data)
        elif config_type == 'odd':
            if operation == 'create':
                return create_odd(data)
            elif operation == 'update':
                return update_odd(data)
            elif operation == 'delete':
                return delete_odd(data)
        elif config_type == 'environment':
            if operation == 'create':
                return create_environment(data)
            elif operation == 'update':
                return update_environment(data)
            elif operation == 'delete':
                return delete_environment(data)
        elif config_type == 'trailer':
            if operation == 'create':
                return create_trailer(data)
            elif operation == 'update':
                return update_trailer(data)
            elif operation == 'delete':
                return delete_trailer(data)
        elif config_type == 'technical_readiness_level':
            if operation == 'create':
                return create_technical_readiness_level(data)
            elif operation == 'update':
                return update_technical_readiness_level(data)
            elif operation == 'delete':
                return delete_technical_readiness_level(data)
        else:
            print(f"Configuration {config_index + 1}: Unknown configuration type '{config_type}'")
            return False
            
    except Exception as e:
        print(f"Configuration {config_index + 1}: Error processing configuration - {str(e)}")
        return False


def cleanup_demo_data():
    """Automatically detect and delete demo data containing 'DEMO' in their names"""
    
    try:
        # Find demo entities
        demo_product_features = ProductFeature.query.filter(ProductFeature.name.contains('DEMO')).all()
        demo_capabilities = Capabilities.query.filter(Capabilities.name.contains('DEMO')).all()
        demo_technical_functions = TechnicalFunction.query.filter(TechnicalFunction.name.contains('DEMO')).all()
        
        total_demo_entities = len(demo_product_features) + len(demo_capabilities) + len(demo_technical_functions)
        
        if total_demo_entities == 0:
            print("No demo data found containing 'DEMO' in names")
            return True
        
        print(f"Found {total_demo_entities} demo entities to clean up:")
        print(f"  - {len(demo_product_features)} demo Product Features")
        print(f"  - {len(demo_capabilities)} demo Capabilities")
        print(f"  - {len(demo_technical_functions)} demo Technical Functions")
        print("-" * 60)
        
        # Delete in reverse dependency order to avoid foreign key constraints
        # 1. Clear many-to-many relationships first
        for tf in demo_technical_functions:
            # Clear the relationship with capabilities (M:N)
            tf.capabilities.clear()
            print(f"Cleared relationships for Technical Function '{tf.name}'")
        
        for cap in demo_capabilities:
            # Clear relationships with product features and technical functions (M:N)
            cap.product_features.clear()
            cap.technical_functions.clear()
            print(f"Cleared relationships for Capability '{cap.name}'")
        
        for pf in demo_product_features:
            # Clear the relationship with capabilities (M:N)
            pf.capabilities.clear()
            print(f"Cleared relationships for Product Feature '{pf.name}'")
        
        # Commit relationship changes
        db.session.commit()
        
        # 2. Re-query entities after committing relationship changes to avoid stale references
        demo_product_features = ProductFeature.query.filter(ProductFeature.name.contains('DEMO')).all()
        demo_capabilities = Capabilities.query.filter(Capabilities.name.contains('DEMO')).all()
        demo_technical_functions = TechnicalFunction.query.filter(TechnicalFunction.name.contains('DEMO')).all()
        
        # 3. Now delete the entities in safe order
        # Delete Technical Functions first (no foreign keys pointing to them)
        for tf in demo_technical_functions:
            db.session.delete(tf)
            print(f"Deleted Technical Function '{tf.name}'")
        
        # Delete Capabilities next
        for cap in demo_capabilities:
            db.session.delete(cap)
            print(f"Deleted Capability '{cap.name}'")
        
        # Delete Product Features last
        for pf in demo_product_features:
            db.session.delete(pf)
            print(f"Deleted Product Feature '{pf.name}'")
        
        db.session.commit()
        print("-" * 60)
        print("Demo data cleanup completed successfully!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during demo data cleanup: {str(e)}")
        return False


def fix_missing_relationships(json_data):
    """Fix missing M:N relationships after main import process"""
    print("\n🔧 Post-processing: Fix missing M:N relationships...")
    
    relationships_added = 0
    
    # Process all capability entities in the JSON to establish missing relationships
    for entity in json_data.get('entities', []):
        if entity.get('entity_type') == 'capability' and entity.get('operation') == 'create':
            cap_label = entity.get('label')
            if not cap_label:
                continue
            
            # Find the capability in the database
            capability = Capabilities.query.filter_by(label=cap_label).first()
            if not capability:
                continue
            
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
                        print(f"✅ Fixed missing link: {pf_label} ↔ {cap_label}")
    
    # Also fix relationships from product feature side
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
                        print(f"✅ Fixed missing link: {pf_label} ↔ {cap_label}")
    
    if relationships_added > 0:
        print(f"🎉 Post-processing complete: Fixed {relationships_added} missing relationships")
    else:
        print("✅ Post-processing complete: No missing relationships found")
    
    return relationships_added

def update_from_json(json_file_path):
    """Update entities and configurations from JSON file"""
    
    with app.app_context():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            print(f"Processing JSON file: {json_file_path}")
            
            # Automatically clean up demo data before processing
            print("\nChecking for demo data to clean up...")
            cleanup_demo_data()
            print()
            
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
            
            # Check for entities or configurations
            has_entities = 'entities' in data and data['entities']
            has_configurations = 'configurations' in data and data['configurations']
            
            if not has_entities and not has_configurations:
                print("Error: No 'entities' or 'configurations' section found in JSON file")
                return False
            
            total_created = 0
            total_updated = 0
            total_deleted = 0
            total_errors = 0
            
            # Process entities if present
            if has_entities:
                entities = data['entities']
                if not isinstance(entities, list):
                    print("Error: 'entities' must be a list")
                    return False
                
                print(f"Found {len(entities)} entities to process")
                print("-" * 60)
                
                # Validate all entities first
                valid_entities = []
                for i, entity in enumerate(entities):
                    if validate_entity_data(entity, i):
                        valid_entities.append((i, entity))
                
                if valid_entities:
                    print(f"Processing {len(valid_entities)} valid entities...")
                    print("-" * 60)
                    
                    # Process valid entities
                    for entity_index, entity_data in valid_entities:
                        try:
                            operation = entity_data['operation'].lower()
                            if process_entity(entity_data, entity_index):
                                if operation == 'create':
                                    total_created += 1
                                elif operation == 'update':
                                    total_updated += 1
                                elif operation == 'delete':
                                    total_deleted += 1
                            else:
                                total_errors += 1
                        except Exception as e:
                            print(f"Entity {entity_index + 1}: Error processing entity - {str(e)}")
                            total_errors += 1
            
            # Process configurations if present
            if has_configurations:
                configurations = data['configurations']
                if not isinstance(configurations, list):
                    print("Error: 'configurations' must be a list")
                    return False
                
                print(f"Found {len(configurations)} configurations to process")
                print("-" * 60)
                
                # Validate all configurations first
                valid_configurations = []
                for i, config in enumerate(configurations):
                    if validate_configuration_data(config, i):
                        valid_configurations.append((i, config))
                
                if valid_configurations:
                    print(f"Processing {len(valid_configurations)} valid configurations...")
                    print("-" * 60)
                    
                    # Process valid configurations
                    for config_index, config_data in valid_configurations:
                        try:
                            operation = config_data['operation'].lower()
                            if process_configuration(config_data, config_index):
                                if operation == 'create':
                                    total_created += 1
                                elif operation == 'update':
                                    total_updated += 1
                                elif operation == 'delete':
                                    total_deleted += 1
                            else:
                                total_errors += 1
                        except Exception as e:
                            print(f"Configuration {config_index + 1}: Error processing configuration - {str(e)}")
                            total_errors += 1
            
            # Post-processing: Fix any missing M:N relationships
            if has_entities:
                fixed_relationships = fix_missing_relationships(data)
            else:
                fixed_relationships = 0
            
            # Commit all changes including relationship fixes
            db.session.commit()
            
            print("-" * 60)
            print(f"Update completed!")
            print(f"Created: {total_created} items")
            print(f"Updated: {total_updated} items")
            print(f"Deleted: {total_deleted} items")
            print(f"Fixed relationships: {fixed_relationships}")
            print(f"Errors encountered: {total_errors}")
            
            # Final verification of relationships
            if has_entities and (total_created > 0 or total_updated > 0 or fixed_relationships > 0):
                print("\n📊 Final relationship verification:")
                total_pfs = ProductFeature.query.count()
                linked_pfs = ProductFeature.query.filter(ProductFeature.capabilities.any()).count()
                total_caps = Capabilities.query.count()
                linked_caps = Capabilities.query.filter(Capabilities.product_features.any()).count()
                total_relationships = db.session.execute(db.text('SELECT COUNT(*) FROM product_feature_capabilities')).scalar()
                
                print(f"   Product features with capabilities: {linked_pfs}/{total_pfs}")
                print(f"   Capabilities with product features: {linked_caps}/{total_caps}")
                print(f"   Total M:N relationships: {total_relationships}")
            
            return total_errors == 0
            
        except FileNotFoundError:
            print(f"Error: JSON file '{json_file_path}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {str(e)}")
            return False
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}")
            return False

def export_current_data(output_file='current_data.json'):
    """Export current data for all entities to JSON for reference"""
    
    with app.app_context():
        try:
            export_data = {
                "metadata": {
                    "version": "2.0",
                    "description": "Complete database export from Product Feature Readiness Database",
                    "exported_by": "update_from_json.py",
                    "export_date": datetime.now().isoformat(),
                    "total_product_features": ProductFeature.query.count(),
                    "total_capabilities": Capabilities.query.count(),
                    "total_technical_functions": TechnicalFunction.query.count(),
                    "total_assessments": ReadinessAssessment.query.count()
                },
                "product_features": [],
                "capabilities": [],
                "technical_functions": []
            }
            
            # Export product features
            product_features = ProductFeature.query.all()
            for pf in product_features:
                pf_data = {
                    "name": pf.name,
                    "description": pf.description,
                    "vehicle_platform_id": pf.vehicle_platform_id,
                    "vehicle_platform_name": pf.vehicle_platform.name if pf.vehicle_platform else None,
                    "swimlane_decorators": pf.swimlane_decorators,
                    "label": pf.label,
                    "tmos": pf.tmos,
                    "status_relative_to_tmos": pf.status_relative_to_tmos,
                    "planned_start_date": pf.planned_start_date.isoformat() if pf.planned_start_date else None,
                    "planned_end_date": pf.planned_end_date.isoformat() if pf.planned_end_date else None,
                    "active_flag": pf.active_flag,
                    "document_url": pf.document_url,
                    "capabilities": [cap.name for cap in pf.capabilities],
                    "dependencies": [dep.name for dep in pf.dependencies],
                    "capabilities_count": len(pf.capabilities)
                }
                export_data["product_features"].append(pf_data)
            
            # Export capabilities
            capabilities = Capabilities.query.all()
            for cap in capabilities:
                cap_data = {
                    "name": cap.name,
                    "success_criteria": cap.success_criteria,
                    "product_feature_id": cap.product_feature_id,
                    "product_feature_name": cap.product_feature.name if cap.product_feature else None,
                    "vehicle_platform_id": cap.vehicle_platform_id,
                    "vehicle_platform_name": cap.vehicle_platform.name if cap.vehicle_platform else None,
                    "planned_start_date": cap.planned_start_date.isoformat() if cap.planned_start_date else None,
                    "planned_end_date": cap.planned_end_date.isoformat() if cap.planned_end_date else None,
                    "tmos": cap.tmos,
                    "progress_relative_to_tmos": cap.progress_relative_to_tmos,
                    "document_url": cap.document_url,
                    "technical_functions": [tf.name for tf in cap.technical_functions],
                    "technical_functions_count": len(cap.technical_functions)
                }
                export_data["capabilities"].append(cap_data)
            
            # Export technical functions
            tech_functions = TechnicalFunction.query.all()
            for tf in tech_functions:
                tf_data = {
                    "name": tf.name,
                    "description": tf.description,
                    "success_criteria": tf.success_criteria,
                    "vehicle_platform_id": tf.vehicle_platform_id,
                    "vehicle_platform_name": tf.vehicle_platform.name if tf.vehicle_platform else None,
                    "tmos": tf.tmos,
                    "status_relative_to_tmos": tf.status_relative_to_tmos,
                    "planned_start_date": tf.planned_start_date.isoformat() if tf.planned_start_date else None,
                    "planned_end_date": tf.planned_end_date.isoformat() if tf.planned_end_date else None,
                    "document_url": tf.document_url,
                    "capabilities": [cap.name for cap in tf.capabilities],
                    "capabilities_count": len(tf.capabilities),
                    "assessment_count": len(tf.readiness_assessments)
                }
                export_data["technical_functions"].append(tf_data)
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            print(f"Current database exported to: {output_file}")
            print(f"Product features: {len(export_data['product_features'])}")
            print(f"Capabilities: {len(export_data['capabilities'])}")
            print(f"Technical functions: {len(export_data['technical_functions'])}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("Enhanced JSON Update Script for Product Feature Readiness Database")
        print("Usage:")
        print("  python update_from_json.py <json_file_path>           # Update from JSON")
        print("  python update_from_json.py --export [output_file]     # Export current data")
        print("  python update_from_json.py --help                     # Show detailed help")
        print("  python update_from_json.py --template                 # Generate template JSON")
        print("  python update_from_json.py --clean-demo               # Clean up demo data only")
        return
    
    if sys.argv[1] == '--help':
        print("Enhanced JSON Update Script for Product Feature Readiness Database")
        print("")
        print("This script allows comprehensive CRUD operations for:")
        print("- Product Features")
        print("- Capabilities") 
        print("- Technical Functions")
        print("")
        print("Database Structure (v4.1 - Enhanced M:N Relationships):")
        print("  ProductFeature (M:N) ↔ Capabilities (M:N) ↔ TechnicalFunction")
        print("  • Robust label-based entity matching")
        print("  • Automatic relationship fix post-processing")
        print("  • Backward compatibility with old formats")
        print("")
        print("JSON Structure:")
        print("  {")
        print('    "metadata": {')
        print('      "version": "3.0",')
        print('      "description": "Description of updates",')
        print('      "created_by": "Ryan Smith",')
        print('      "created_date": "2025-10-21"')
        print("    },")
        print('    "entities": [')
        print("      {")
        print('        "entity_type": "product_feature|capability|technical_function",')
        print('        "operation": "create|update|delete",')
        print('        "name": "Entity Name",')
        print('        "description": "Entity description",')
        print('        "vehicle_platform_id": 5,  // Use platform ID, not vehicle_type')
        print('        "planned_start_date": "2025-01-01",')
        print('        "planned_end_date": "2025-12-31",')
        print('        "tmos": "Target Measure of Success",')
        print('        // Additional fields specific to entity type...')
        print("      }")
        print("    ]")
        print("  }")
        print("")
        print("Entity-specific fields:")
        print("Product Feature:")
        print('  "swimlane_decorators": "swimlane info",')
        print('  "label": "PF-SWIM-1.1",')
        print('  "status_relative_to_tmos": 85.5,')
        print('  "active_flag": "next",')
        print('  "document_url": "https://docs.example.com/doc",')
        print('  "capabilities": ["Capability 1", "Capability 2"],')
        print('  "dependencies": ["Other Product Feature"]')
        print("")
        print("Capability:")
        print('  "success_criteria": "Success criteria text",')
        print('  "product_feature_ids": ["Product Feature 1", "Product Feature 2"],  // M:N relationships')
        print('  "product_feature": "Single Product Feature Name",  // Old 1:N compatibility')
        print('  "progress_relative_to_tmos": 75.0,')
        print('  "document_url": "https://docs.example.com/doc",')
        print('  "technical_functions": ["Tech Function 1"]')
        print("")
        print("Technical Function:")
        print('  "success_criteria": "Success criteria text",')
        print('  "status_relative_to_tmos": 90.0,')
        print('  "document_url": "https://docs.example.com/doc",')
        print('  "capabilities": ["Related Capability"]  // Links through capabilities')
        print("")
        print("Vehicle Platform IDs:")
        print("  1: Terberg ATT, 2: CA500, 3: T800, 4: AEV")
        print("  5: Truck Platform, 6: Van Platform, 7: Car Platform, 8: Generic Platform")
        print("")
        print("Examples:")
        print("  python update_from_json.py my_updates.json")
        print("  python update_from_json.py --export current_data.json")
        return
    
    if sys.argv[1] == '--template':
        generate_template_json()
        return
    
    if sys.argv[1] == '--export':
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'current_data.json'
        export_current_data(output_file)
        return
    
    if sys.argv[1] == '--clean-demo':
        print("Manual demo data cleanup initiated...")
        with app.app_context():
            success = cleanup_demo_data()
            if success:
                print("Demo data cleanup completed successfully!")
            else:
                print("Demo data cleanup completed with errors.")
                sys.exit(1)
        return
    
    json_file_path = sys.argv[1]
    success = update_from_json(json_file_path)
    
    if success:
        print("Update completed successfully!")
    else:
        print("Update completed with errors. Please check the output above.")
        sys.exit(1)

def generate_template_json():
    """Generate a template JSON file with examples"""
    template_data = {
        "metadata": {
            "version": "4.1",
            "description": "Template for updating Product Feature Readiness Database - Enhanced M:N Relationships",
            "created_by": "Ryan Smith",
            "created_date": datetime.now().strftime('%Y-%m-%d'),
            "notes": "Enhanced with robust relationship handling and automatic post-processing fixes"
        },
        "entities": [
            {
                "entity_type": "product_feature",
                "operation": "create",
                "name": "Example Product Feature",
                "description": "This is an example product feature",
                "vehicle_platform_id": 5,  # Use platform ID instead of vehicle_type
                "swimlane_decorators": "ADAS",
                "label": "PF-ADAS-1.1",
                "tmos": "Achieve 99.9% uptime in highway conditions",
                "status_relative_to_tmos": 75.0,
                "planned_start_date": "2025-01-15",
                "planned_end_date": "2025-12-31",
                "active_flag": "next",
                "document_url": "https://docs.example.com/product-feature",
                "capabilities": ["Highway Navigation"],  # Changed from capabilities_required
                "dependencies": []
            },
            {
                "entity_type": "capability",
                "operation": "create",
                "name": "Highway Navigation",
                "success_criteria": "Successfully navigate highway routes with 99.9% accuracy",
                "product_feature_ids": ["Example Product Feature"],  # New M:N format
                "vehicle_platform_id": 5,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-11-30",
                "tmos": "Complete highway navigation capability",
                "progress_relative_to_tmos": 60.0,
                "document_url": "https://docs.example.com/highway-nav",
                "technical_functions": ["Path Planning", "Lane Detection"]
            },
            {
                "entity_type": "capability",
                "operation": "create",
                "name": "Shared Safety Monitoring",
                "success_criteria": "Advanced safety monitoring shared across multiple product features",
                "product_feature_ids": ["Example Product Feature", "Another Product Feature"],  # Demonstrates M:N
                "vehicle_platform_id": 5,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-11-30",
                "tmos": "Universal safety monitoring capability",
                "progress_relative_to_tmos": 45.0,
                "document_url": "https://docs.example.com/safety-monitoring",
                "technical_functions": ["Collision Detection", "Emergency Stop"]
            },
            {
                "entity_type": "technical_function",
                "operation": "create",
                "name": "Path Planning",
                "description": "Generate optimal paths for vehicle navigation",
                "success_criteria": "Generate paths within 100ms with 99% success rate",
                "vehicle_platform_id": 5,
                "tmos": "Real-time path planning for highway navigation",
                "status_relative_to_tmos": 80.0,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-08-31",
                "document_url": "https://docs.example.com/path-planning",
                "capabilities": ["Highway Navigation"]  # Links through capabilities
            },
            {
                "entity_type": "technical_function",
                "operation": "create",
                "name": "Lane Detection",
                "description": "Computer vision system for lane boundary detection",
                "success_criteria": "Detect lane boundaries with 99.5% accuracy in daylight",
                "vehicle_platform_id": 5,
                "tmos": "Reliable lane detection for highway navigation",
                "status_relative_to_tmos": 85.0,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-07-31",
                "document_url": "https://docs.example.com/lane-detection",
                "capabilities": ["Highway Navigation"]
            },
            {
                "entity_type": "product_feature",
                "operation": "update",
                "name": "Example Product Feature",
                "status_relative_to_tmos": 85.0,
                "description": "Updated description for the product feature"
            },
            {
                "entity_type": "capability",
                "operation": "update",
                "name": "Highway Navigation",
                "progress_relative_to_tmos": 70.0,
                "tmos": "Updated TMOS for highway navigation",
                "product_feature_ids": ["Example Product Feature", "Another Product Feature"]  # Update M:N relationships
            },
            {
                "entity_type": "technical_function",
                "operation": "delete",
                "name": "Obsolete Technical Function",
                "force_delete": False
            }
        ]
    }
    
    output_file = 'template_updates.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(template_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Template JSON file generated: {output_file}")
        print("Enhanced v4.1 Database Structure:")
        print("- ProductFeature (M:N) ↔ Capabilities (M:N) ↔ TechnicalFunction")
        print("- Robust label-based entity matching")
        print("- Automatic relationship fix post-processing")
        print("- Use product_feature_ids array for M:N capability relationships")
        print("- Use vehicle_platform_id instead of vehicle_type")
        print("- Capabilities can be shared across multiple ProductFeatures")
        print("- TechnicalFunctions link through capabilities")
        print("")
        print("Edit this file with your specific data and run:")
        print(f"python update_from_json.py {output_file}")
        
    except Exception as e:
        print(f"Error generating template: {str(e)}")

if __name__ == '__main__':
    main()