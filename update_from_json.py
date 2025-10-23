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
    """Find or create reference entities based on names"""
    references = []
    
    if not reference_data:
        return references
    
    for ref_name in reference_data:
        if entity_type == 'product_feature':
            ref_entity = ProductFeature.query.filter_by(name=ref_name).first()
        elif entity_type == 'capability':
            ref_entity = Capabilities.query.filter_by(name=ref_name).first()
        elif entity_type == 'technical_function':
            ref_entity = TechnicalFunction.query.filter_by(name=ref_name).first()
        else:
            continue
        
        if ref_entity:
            references.append(ref_entity)
        else:
            print(f"Warning: Referenced {entity_type} '{ref_name}' not found, skipping")
    
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
        "truck": 5,      # Truck Platform
        "van": 6,        # Van Platform  
        "car": 7,        # Car Platform
        "terberg": 1,    # Terberg ATT
        "ca500": 2,      # CA500
        "t800": 3,       # T800
        "aev": 4,        # AEV
        "generic": 8     # Generic Platform
    }
    
    platform_id = mapping.get(str(vehicle_type_or_id).lower(), 8)  # Default to Generic Platform
    return platform_id

def create_product_feature(data):
    """Create a new product feature"""
    try:
        # Check if already exists
        existing = ProductFeature.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Product feature '{data['name']}' already exists, skipping creation")
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
        
        # Handle relationships
        if 'capabilities_required' in data:
            capabilities = find_or_create_references(data['capabilities_required'], 'capability')
            product_feature.capabilities_required.extend(capabilities)
        
        if 'dependencies' in data:
            dependencies = find_or_create_references(data['dependencies'], 'product_feature')
            product_feature.dependencies.extend(dependencies)
        
        print(f"Created product feature: {product_feature.name}")
        return True
        
    except Exception as e:
        print(f"Error creating product feature: {str(e)}")
        return False

def update_product_feature(data):
    """Update an existing product feature"""
    try:
        product_feature = ProductFeature.query.filter_by(name=data['name']).first()
        if not product_feature:
            print(f"Product feature '{data['name']}' not found for update")
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
        
        # Update relationships
        if 'capabilities_required' in data:
            product_feature.capabilities_required.clear()
            capabilities = find_or_create_references(data['capabilities_required'], 'capability')
            product_feature.capabilities_required.extend(capabilities)
            updates_made.append('capabilities_required')
        
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
    """Create a new capability"""
    try:
        # Check if already exists
        existing = Capabilities.query.filter_by(name=data['name']).first()
        if existing:
            print(f"Capability '{data['name']}' already exists, skipping creation")
            return False
        
        # Handle both old and new vehicle field formats
        vehicle_platform_id = None
        if 'vehicle_platform_id' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
        elif 'vehicle_type' in data:
            vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])
        
        capability = Capabilities(
            name=data['name'],
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
        
        # Handle relationships
        if 'technical_functions' in data:
            tech_functions = find_or_create_references(data['technical_functions'], 'technical_function')
            capability.technical_functions.extend(tech_functions)
        
        if 'product_features' in data:
            product_features = find_or_create_references(data['product_features'], 'product_feature')
            capability.product_features.extend(product_features)
        
        print(f"Created capability: {capability.name}")
        return True
        
    except Exception as e:
        print(f"Error creating capability: {str(e)}")
        return False

def update_capability(data):
    """Update an existing capability"""
    try:
        capability = Capabilities.query.filter_by(name=data['name']).first()
        if not capability:
            print(f"Capability '{data['name']}' not found for update")
            return False
        
        # Update fields if provided
        fields_to_update = ['success_criteria', 'tmos', 'progress_relative_to_tmos', 'document_url']
        
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
        
        # Update relationships
        if 'technical_functions' in data:
            capability.technical_functions.clear()
            tech_functions = find_or_create_references(data['technical_functions'], 'technical_function')
            capability.technical_functions.extend(tech_functions)
            updates_made.append('technical_functions')
        
        if 'product_features' in data:
            capability.product_features.clear()
            product_features = find_or_create_references(data['product_features'], 'product_feature')
            capability.product_features.extend(product_features)
            updates_made.append('product_features')
        
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
        
        # Find required product feature
        product_feature = None
        if 'product_feature' in data:
            product_feature = ProductFeature.query.filter_by(name=data['product_feature']).first()
            if not product_feature:
                print(f"Product feature '{data['product_feature']}' not found for technical function")
                return False
        else:
            print("Product feature is required for technical function")
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
            product_feature_id=product_feature.id,
            document_url=data.get('document_url')
        )
        
        db.session.add(technical_function)
        db.session.flush()  # Get the ID
        
        # Handle relationships
        if 'capabilities' in data:
            capabilities = find_or_create_references(data['capabilities'], 'capability')
            technical_function.capabilities.extend(capabilities)
        
        if 'product_feature_dependencies' in data:
            pf_dependencies = find_or_create_references(data['product_feature_dependencies'], 'product_feature')
            technical_function.product_feature_dependencies.extend(pf_dependencies)
        
        if 'capability_dependencies' in data:
            cap_dependencies = find_or_create_references(data['capability_dependencies'], 'capability')
            technical_function.capability_dependencies.extend(cap_dependencies)
        
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
        
        # Update product feature if provided
        if 'product_feature' in data:
            product_feature = ProductFeature.query.filter_by(name=data['product_feature']).first()
            if product_feature:
                technical_function.product_feature_id = product_feature.id
                updates_made.append('product_feature')
            else:
                print(f"Warning: Product feature '{data['product_feature']}' not found")
        
        # Update relationships
        if 'capabilities' in data:
            technical_function.capabilities.clear()
            capabilities = find_or_create_references(data['capabilities'], 'capability')
            technical_function.capabilities.extend(capabilities)
            updates_made.append('capabilities')
        
        if 'product_feature_dependencies' in data:
            technical_function.product_feature_dependencies.clear()
            pf_dependencies = find_or_create_references(data['product_feature_dependencies'], 'product_feature')
            technical_function.product_feature_dependencies.extend(pf_dependencies)
            updates_made.append('product_feature_dependencies')
        
        if 'capability_dependencies' in data:
            technical_function.capability_dependencies.clear()
            cap_dependencies = find_or_create_references(data['capability_dependencies'], 'capability')
            technical_function.capability_dependencies.extend(cap_dependencies)
            updates_made.append('capability_dependencies')
        
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
            tech_functions = TechnicalFunction.query.filter_by(product_feature_id=entity.id).count()
            if tech_functions > 0:
                dependencies.append(f"{tech_functions} technical functions")
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


def update_from_json(json_file_path):
    """Update entities and configurations from JSON file"""
    
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
            
            # Commit all changes
            db.session.commit()
            
            print("-" * 60)
            print(f"Update completed!")
            print(f"Created: {total_created} items")
            print(f"Updated: {total_updated} items")
            print(f"Deleted: {total_deleted} items")
            print(f"Errors encountered: {total_errors}")
            
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
                    "vehicle_type": pf.vehicle_type,
                    "swimlane_decorators": pf.swimlane_decorators,
                    "label": pf.label,
                    "tmos": pf.tmos,
                    "status_relative_to_tmos": pf.status_relative_to_tmos,
                    "planned_start_date": pf.planned_start_date.isoformat() if pf.planned_start_date else None,
                    "planned_end_date": pf.planned_end_date.isoformat() if pf.planned_end_date else None,
                    "active_flag": pf.active_flag,
                    "capabilities_required": [cap.name for cap in pf.capabilities_required],
                    "dependencies": [dep.name for dep in pf.dependencies],
                    "technical_functions_count": len(pf.technical_capabilities)
                }
                export_data["product_features"].append(pf_data)
            
            # Export capabilities
            capabilities = Capabilities.query.all()
            for cap in capabilities:
                cap_data = {
                    "name": cap.name,
                    "success_criteria": cap.success_criteria,
                    "vehicle_type": cap.vehicle_type,
                    "planned_start_date": cap.planned_start_date.isoformat() if cap.planned_start_date else None,
                    "planned_end_date": cap.planned_end_date.isoformat() if cap.planned_end_date else None,
                    "tmos": cap.tmos,
                    "progress_relative_to_tmos": cap.progress_relative_to_tmos,
                    "technical_functions": [tf.name for tf in cap.technical_functions],
                    "product_features": [pf.name for pf in cap.product_features]
                }
                export_data["capabilities"].append(cap_data)
            
            # Export technical functions
            tech_functions = TechnicalFunction.query.all()
            for tf in tech_functions:
                tf_data = {
                    "name": tf.name,
                    "description": tf.description,
                    "success_criteria": tf.success_criteria,
                    "vehicle_type": tf.vehicle_type,
                    "tmos": tf.tmos,
                    "status_relative_to_tmos": tf.status_relative_to_tmos,
                    "planned_start_date": tf.planned_start_date.isoformat() if tf.planned_start_date else None,
                    "planned_end_date": tf.planned_end_date.isoformat() if tf.planned_end_date else None,
                    "product_feature": tf.product_feature.name if tf.product_feature else None,
                    "capabilities": [cap.name for cap in tf.capabilities],
                    "product_feature_dependencies": [pf.name for pf in tf.product_feature_dependencies],
                    "capability_dependencies": [cap.name for cap in tf.capability_dependencies],
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
        return
    
    if sys.argv[1] == '--help':
        print("Enhanced JSON Update Script for Product Feature Readiness Database")
        print("")
        print("This script allows comprehensive CRUD operations for:")
        print("- Product Features")
        print("- Capabilities") 
        print("- Technical Functions")
        print("")
        print("JSON Structure:")
        print("  {")
        print('    "metadata": {')
        print('      "version": "2.0",')
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
        print('        "vehicle_type": "truck|van|car",')
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
        print('  "capabilities_required": ["Capability 1", "Capability 2"],')
        print('  "dependencies": ["Other Product Feature"]')
        print("")
        print("Capability:")
        print('  "success_criteria": "Success criteria text",')
        print('  "progress_relative_to_tmos": 75.0,')
        print('  "technical_functions": ["Tech Function 1"],')
        print('  "product_features": ["Product Feature 1"]')
        print("")
        print("Technical Function:")
        print('  "success_criteria": "Success criteria text",')
        print('  "status_relative_to_tmos": 90.0,')
        print('  "product_feature": "Required Product Feature",')
        print('  "capabilities": ["Related Capability"],')
        print('  "product_feature_dependencies": ["PF Dependency"],')
        print('  "capability_dependencies": ["Cap Dependency"]')
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
            "version": "2.0",
            "description": "Template for updating Product Feature Readiness Database",
            "created_by": "Ryan Smith",
            "created_date": datetime.now().strftime('%Y-%m-%d')
        },
        "entities": [
            {
                "entity_type": "product_feature",
                "operation": "create",
                "name": "Example Product Feature",
                "description": "This is an example product feature",
                "vehicle_type": "truck",
                "swimlane_decorators": "ADAS",
                "label": "PF-ADAS-1.1",
                "tmos": "Achieve 99.9% uptime in highway conditions",
                "status_relative_to_tmos": 75.0,
                "planned_start_date": "2025-01-15",
                "planned_end_date": "2025-12-31",
                "active_flag": "next",
                "capabilities_required": ["Highway Navigation"],
                "dependencies": []
            },
            {
                "entity_type": "capability",
                "operation": "create",
                "name": "Highway Navigation",
                "success_criteria": "Successfully navigate highway routes with 99.9% accuracy",
                "vehicle_type": "truck",
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-11-30",
                "tmos": "Complete highway navigation capability",
                "progress_relative_to_tmos": 60.0,
                "technical_functions": ["Path Planning", "Lane Detection"],
                "product_features": []
            },
            {
                "entity_type": "technical_function",
                "operation": "create",
                "name": "Path Planning",
                "description": "Generate optimal paths for vehicle navigation",
                "success_criteria": "Generate paths within 100ms with 99% success rate",
                "vehicle_type": "truck",
                "tmos": "Real-time path planning for highway navigation",
                "status_relative_to_tmos": 80.0,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-08-31",
                "product_feature": "Example Product Feature",
                "capabilities": ["Highway Navigation"],
                "product_feature_dependencies": [],
                "capability_dependencies": []
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
                "operation": "delete",
                "name": "Obsolete Capability",
                "force_delete": False
            }
        ]
    }
    
    output_file = 'template_updates.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(template_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Template JSON file generated: {output_file}")
        print("Edit this file with your specific data and run:")
        print(f"python update_from_json.py {output_file}")
        
    except Exception as e:
        print(f"Error generating template: {str(e)}")

if __name__ == '__main__':
    main()