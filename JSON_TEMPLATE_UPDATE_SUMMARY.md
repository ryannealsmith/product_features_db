# JSON Templates and Import Files Update Summary

## Database Structure Changes

The database has been updated from the old structure to a new hierarchical relationship model:

**Old Structure:**
- ProductFeature → TechnicalFunction (direct relationship)
- Capabilities as separate entities

**New Structure:**
- ProductFeature (1:N) → Capabilities (M:N) → TechnicalFunction
- Hierarchical relationship with proper separation of concerns

## Updated Files

### 1. update_from_json.py
**Major Changes:**
- Updated `create_capability()` to require `product_feature` parameter
- Updated `create_technical_function()` to work through capabilities (no direct product_feature_id)
- Updated `update_capability()` and `update_technical_function()` for new relationships
- Updated `export_current_data()` to reflect new database structure
- Updated help documentation and template generation
- Changed from `vehicle_type` strings to `vehicle_platform_id` integers

**Key Relationship Changes:**
- ProductFeature.capabilities (was capabilities_required)
- Capabilities.product_feature_id (required field)
- TechnicalFunction.capabilities (links through association table)
- Removed old relationship fields: product_feature_dependencies, capability_dependencies

### 2. system_configurations_template.json
**Changes:**
- Updated metadata version to 3.0
- Added notes about vehicle platform ID mappings
- Template remains compatible (configurations unchanged)

### 3. New Files Created

#### new_structure_template.json
- Comprehensive example showing new relationship structure
- Demonstrates ProductFeature → Capabilities → TechnicalFunction hierarchy
- Includes realistic port operations example
- Shows proper use of vehicle_platform_id instead of vehicle_type

#### template_updates.json (regenerated)
- Updated template with new structure
- Shows proper field mappings
- Includes documentation of vehicle platform IDs

#### updated_database_export.json (generated)
- Current database export showing new structure
- Demonstrates actual relationships in use

## Vehicle Platform ID Mapping

Replace `vehicle_type` strings with `vehicle_platform_id` integers:

```json
{
  "1": "Terberg ATT",
  "2": "CA500", 
  "3": "T800",
  "4": "AEV",
  "5": "Truck Platform",
  "6": "Van Platform",
  "7": "Car Platform", 
  "8": "Generic Platform"
}
```

## Usage Examples

### Creating a Product Feature with Capabilities and Technical Functions

```json
{
  "entities": [
    {
      "entity_type": "product_feature",
      "operation": "create",
      "name": "My Product Feature",
      "vehicle_platform_id": 5,
      "capabilities": []
    },
    {
      "entity_type": "capability", 
      "operation": "create",
      "name": "My Capability",
      "product_feature": "My Product Feature",
      "technical_functions": ["My Technical Function"]
    },
    {
      "entity_type": "technical_function",
      "operation": "create", 
      "name": "My Technical Function",
      "capabilities": ["My Capability"]
    }
  ]
}
```

### Key Requirements in New Structure

1. **Capabilities must specify a product_feature** (required field)
2. **Use vehicle_platform_id instead of vehicle_type**
3. **TechnicalFunctions link through capabilities** (no direct product feature link)
4. **ProductFeatures reference capabilities** (not capabilities_required)

## Testing

The updated import system has been tested with:
- ✅ New template generation
- ✅ Database export functionality  
- ✅ Import with new relationship structure
- ✅ Backward compatibility for vehicle platform mapping

## Migration Notes

For existing JSON files:
1. Change `vehicle_type: "truck"` to `vehicle_platform_id: 5`
2. Change `capabilities_required` to `capabilities` 
3. For capabilities, add required `product_feature` field
4. Remove `product_feature` field from technical functions
5. Update version to "3.0" in metadata

The import script maintains backward compatibility for vehicle type mapping but the new structure is recommended for all new files.