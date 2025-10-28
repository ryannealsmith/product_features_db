# Enhanced JSON Update System v4.1

This enhanced JSON update script provides comprehensive CRUD (Create, Read, Update, Delete) operations for the Product Feature Readiness Database. You can manage **Product Features**, **Capabilities**, and **Technical Functions** through structured JSON files or the web-based JSON Editor interface.

## Features

- ✅ **Web-based JSON Editor** with interactive CRUD interface at `/json_editor`
- ✅ **Create** new entities with full relationship mapping
- ✅ **Update** existing entities and their relationships  
- ✅ **Delete** entities with dependency checking
- ✅ **Export** current database state to JSON
- ✅ **Template generation** for easy JSON creation
- ✅ **Comprehensive validation** with detailed error reporting
- ✅ **Enhanced M:N relationships** between Product Features ↔ Capabilities ↔ Technical Functions
- ✅ **Automatic backups** before save operations
- ✅ **Command-line and web interface** options

## Quick Start

### 1. Generate a Template
```bash
python update_from_json.py --template
```
This creates `template_updates.json` with examples of all operations.

### 2. Export Current Data
```bash
python update_from_json.py --export current_data.json
```
This exports the complete current database state for reference.

### 3. Update from JSON
```bash
# Command line method
./.venv/bin/python update_from_json.py repository_update_data_final_colin3.json

# Or use the web interface
# Navigate to http://localhost:8080/json_editor
```

### 4. Get Help
```bash
python update_from_json.py --help
```

## JSON Structure

### Basic Structure (v4.1)
```json
{
  "metadata": {
    "version": "4.1",
    "description": "Description of your updates",
    "created_by": "Your Name",
    "created_date": "2025-10-21"
  },
  "entities": [
    {
      "entity_type": "product_feature|capability|technical_function",
      "operation": "create|update|delete",
      "label": "Entity Label (PF-001, CAP-001, TF-001)",
      "name": "Entity Name",
      // Additional fields based on entity type and operation
    }
  ]
}
```

## Entity Types and Fields

### Product Features

#### Create/Update Operations
```json
{
  "entity_type": "product_feature",
  "operation": "create",
  "name": "Highway Autonomous Driving",
  "description": "Full autonomous driving capability on highways",
  "vehicle_type": "truck",
  "swimlane_decorators": "ADAS",
  "label": "PF-ADAS-1.1",
  "tmos": "Achieve 99.9% successful highway navigation",
  "status_relative_to_tmos": 75.0,
  "planned_start_date": "2025-01-15",
  "planned_end_date": "2025-12-31",
  "active_flag": "next",
  "capabilities_required": ["Highway Navigation", "Lane Keeping"],
  "dependencies": ["Basic Navigation System"]
}
```

**Available Fields:**
- `name` *(required)*: Unique name for the product feature
- `description`: Detailed description
- `vehicle_type`: "truck", "van", or "car"
- `swimlane_decorators`: Swimlane categorization
- `label`: Product feature label (e.g., "PF-ADAS-1.1")
- `tmos`: Target Measure of Success
- `status_relative_to_tmos`: Progress percentage (0.0-100.0)
- `planned_start_date`: Start date (YYYY-MM-DD)
- `planned_end_date`: End date (YYYY-MM-DD)
- `active_flag`: Status flag (default: "next")
- `capabilities_required`: List of capability names
- `dependencies`: List of dependent product feature names

### Capabilities

#### Create/Update Operations
```json
{
  "entity_type": "capability",
  "operation": "create",
  "name": "Highway Navigation",
  "success_criteria": "Navigate highways with 99.9% accuracy and safety",
  "vehicle_type": "truck",
  "planned_start_date": "2025-01-01",
  "planned_end_date": "2025-11-30",
  "tmos": "Complete highway navigation capability",
  "progress_relative_to_tmos": 60.0,
  "technical_functions": ["Path Planning", "Lane Detection"],
  "product_features": ["Highway Autonomous Driving"]
}
```

**Available Fields:**
- `name` *(required)*: Unique name for the capability
- `success_criteria`: Detailed success criteria
- `vehicle_type`: "truck", "van", or "car"
- `planned_start_date`: Start date (YYYY-MM-DD)
- `planned_end_date`: End date (YYYY-MM-DD)
- `tmos`: Target Measure of Success
- `progress_relative_to_tmos`: Progress percentage (0.0-100.0)
- `technical_functions`: List of technical function names
- `product_features`: List of product feature names

### Technical Functions

#### Create/Update Operations
```json
{
  "entity_type": "technical_function",
  "operation": "create",
  "name": "Path Planning",
  "description": "Generate optimal navigation paths",
  "success_criteria": "Generate paths within 100ms with 99% success rate",
  "vehicle_type": "truck",
  "tmos": "Real-time path planning for navigation",
  "status_relative_to_tmos": 80.0,
  "planned_start_date": "2025-01-01",
  "planned_end_date": "2025-08-31",
  "product_feature": "Highway Autonomous Driving",
  "capabilities": ["Highway Navigation"],
  "product_feature_dependencies": ["Basic Navigation System"],
  "capability_dependencies": ["Sensor Fusion"]
}
```

**Available Fields:**
- `name` *(required)*: Unique name for the technical function
- `description`: Detailed description
- `success_criteria`: Technical success criteria
- `vehicle_type`: "truck", "van", or "car"
- `tmos`: Target Measure of Success
- `status_relative_to_tmos`: Progress percentage (0.0-100.0)
- `planned_start_date`: Start date (YYYY-MM-DD)
- `planned_end_date`: End date (YYYY-MM-DD)
- `product_feature` *(required for create)*: Parent product feature name
- `capabilities`: List of related capability names
- `product_feature_dependencies`: List of dependent product feature names
- `capability_dependencies`: List of dependent capability names

## Operations

### Create Operation
Creates a new entity. Will skip if entity with same name already exists.

```json
{
  "entity_type": "product_feature",
  "operation": "create",
  "name": "New Feature",
  // ... other fields
}
```

### Update Operation
Updates an existing entity. Only updates fields that are specified.

```json
{
  "entity_type": "product_feature", 
  "operation": "update",
  "name": "Existing Feature",
  "status_relative_to_tmos": 85.0,
  "description": "Updated description"
}
```

### Delete Operation
Deletes an entity. Includes dependency checking for safety.

```json
{
  "entity_type": "capability",
  "operation": "delete", 
  "name": "Obsolete Capability",
  "force_delete": false
}
```

**Delete Options:**
- `force_delete: false` (default): Prevents deletion if dependencies exist
- `force_delete: true`: Forces deletion despite dependencies

## Examples

### Example 1: Create Complete Feature Set
```json
{
  "metadata": {
    "version": "2.0",
    "description": "Add new autonomous parking feature",
    "created_by": "Development Team",
    "created_date": "2025-10-21"
  },
  "entities": [
    {
      "entity_type": "capability",
      "operation": "create",
      "name": "Autonomous Parking",
      "success_criteria": "Park vehicle in standard spots with 99% success rate",
      "vehicle_type": "truck",
      "planned_start_date": "2025-01-01",
      "planned_end_date": "2025-06-30",
      "tmos": "Fully automated parking capability",
      "progress_relative_to_tmos": 0.0
    },
    {
      "entity_type": "product_feature",
      "operation": "create",
      "name": "Automated Parking System",
      "description": "Complete automated parking solution for urban environments",
      "vehicle_type": "truck",
      "swimlane_decorators": "PARKING",
      "label": "PF-PARK-1.0",
      "tmos": "Enable hands-free parking in urban areas",
      "status_relative_to_tmos": 25.0,
      "planned_start_date": "2025-01-15",
      "planned_end_date": "2025-08-31",
      "active_flag": "next",
      "capabilities_required": ["Autonomous Parking"]
    },
    {
      "entity_type": "technical_function",
      "operation": "create",
      "name": "Parking Space Detection",
      "description": "Detect and analyze available parking spaces",
      "success_criteria": "Detect parking spaces with 95% accuracy in various lighting conditions",
      "vehicle_type": "truck",
      "tmos": "Real-time parking space detection",
      "status_relative_to_tmos": 40.0,
      "planned_start_date": "2025-01-01",
      "planned_end_date": "2025-05-31",
      "product_feature": "Automated Parking System",
      "capabilities": ["Autonomous Parking"]
    }
  ]
}
```

### Example 2: Update Progress
```json
{
  "metadata": {
    "version": "2.0",
    "description": "Monthly progress update",
    "created_by": "Project Manager",
    "created_date": "2025-10-21"
  },
  "entities": [
    {
      "entity_type": "product_feature",
      "operation": "update",
      "name": "Automated Parking System",
      "status_relative_to_tmos": 65.0
    },
    {
      "entity_type": "technical_function",
      "operation": "update", 
      "name": "Parking Space Detection",
      "status_relative_to_tmos": 80.0,
      "description": "Enhanced with machine learning algorithms"
    }
  ]
}
```

## Best Practices

1. **Start with Template**: Use `--template` to generate example JSON
2. **Export Before Major Changes**: Use `--export` to backup current state
3. **Incremental Updates**: Process changes in small batches for easier debugging
4. **Validate Relationships**: Ensure referenced entities exist before creating relationships
5. **Use Descriptive Metadata**: Include clear descriptions and attribution
6. **Test Deletions**: Use `force_delete: false` first to check dependencies

## Troubleshooting

### Common Issues

**Entity Not Found**
```
Warning: Referenced capability 'Missing Capability' not found, skipping
```
*Solution*: Create the referenced entity first or check the spelling

**Validation Errors**
```
Validation errors for entity 1:
  - Invalid status_relative_to_tmos '150.0'. Must be 0.0-100.0
```
*Solution*: Fix the validation error in your JSON file

**Dependency Conflicts**
```
Cannot delete technical_function 'Path Planning': has 3 readiness assessments
Use 'force_delete': true to override
```
*Solution*: Use `force_delete: true` or clean up dependencies first

## Integration

This system integrates with:
- **Flask web application** for real-time updates and web interface
- **Database models** with enhanced M:N relationship support
- **JSON Editor** web interface at `/json_editor` for interactive management
- **Sample data system** for testing and initialization
- **Automatic backup system** for data safety
- **Export/Import functionality** through both CLI and web interface

### Web Interface Features
- Interactive entity cards with edit/delete/duplicate actions
- Modal forms for adding and editing entities
- Real-time validation and error handling
- Automatic save to `repository_update_data_final_colin3.json`
- Export functionality with timestamped files

The JSON update system provides a powerful, flexible way to manage your autonomous vehicle capability database both programmatically and through an intuitive web interface, while maintaining data integrity and relationships in the enhanced v4.1 structure.