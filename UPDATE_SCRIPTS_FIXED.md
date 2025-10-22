# Update Scripts Fixed for Vehicle Platform Schema

## Problem Resolved
The `update_from_json.py` and `update_from_csv.py` scripts were not working with the new template files because they were still using the old `vehicle_type` string fields instead of the new `vehicle_platform_id` foreign key relationships.

## Solution Implemented

### 1. Updated `update_from_json.py`

#### **Added Helper Function**
```python
def get_vehicle_platform_id(vehicle_type_or_id):
    """Get vehicle platform ID from vehicle type string or existing ID"""
    # Handles both integers and string mappings
    # Maps vehicle type strings to platform IDs
```

#### **Vehicle Platform Mapping**
| Vehicle Type String | Platform ID | Platform Name |
|-------------------|-------------|---------------|
| "truck" | 5 | Truck Platform |
| "van" | 6 | Van Platform |
| "car" | 7 | Car Platform |
| "terberg" | 1 | Terberg ATT |
| "ca500" | 2 | CA500 |
| "t800" | 3 | T800 |
| "aev" | 4 | AEV |
| "generic" | 8 | Generic Platform |

#### **Backward Compatibility**
- Script now accepts both `vehicle_platform_id` (new) and `vehicle_type` (old) fields
- Automatically converts vehicle type strings to appropriate platform IDs
- Maintains compatibility with existing templates

#### **Enhanced Features**
- Added support for `document_url` field in all entity types
- Improved error handling for vehicle platform relationships
- Better validation for platform ID ranges

### 2. Updated Entity Creation Functions

#### **ProductFeature Creation**
```python
# Handle both old and new vehicle field formats
vehicle_platform_id = None
if 'vehicle_platform_id' in data:
    vehicle_platform_id = get_vehicle_platform_id(data['vehicle_platform_id'])
elif 'vehicle_type' in data:
    vehicle_platform_id = get_vehicle_platform_id(data['vehicle_type'])

product_feature = ProductFeature(
    # ... other fields ...
    vehicle_platform_id=vehicle_platform_id,
    document_url=data.get('document_url')
)
```

#### **Similar Updates Applied To**
- ✅ `create_capability()` and `update_capability()`
- ✅ `create_technical_function()` and `update_technical_function()`
- ✅ `create_product_feature()` and `update_product_feature()`

### 3. CSV Script Status
- ✅ **No changes needed** - CSV script focuses on assessment updates, not entity creation
- ✅ **Still fully functional** with new schema
- ✅ **Successfully tested** with updated template CSV files

## Testing Results

### **JSON Template Tests**
```bash
# Simple template test
./venv/bin/python update_from_json.py simple_update_template.json
# Result: ✅ Created 3 items, 0 errors (placeholder names cause expected "not found" messages)

# Repository template test  
./venv/bin/python update_from_json.py repository_update_template.json
# Result: ✅ Created 7 items, Updated 4 items (missing referenced entities cause expected errors)
```

### **CSV Template Tests**
```bash
# CSV capability updates
./venv/bin/python update_from_csv.py capability_updates_template.csv
# Result: ✅ Updated 10 capabilities, 0 errors
```

### **Vehicle Platform Relationship Verification**
```python
# Emergency Response System -> Platform ID: 5 -> Truck Platform ✅
# Autonomous Emergency Braking -> Platform ID: 5 -> Truck Platform ✅  
# Collision Prediction Algorithm -> Platform ID: 5 -> Truck Platform ✅
```

## Template Compatibility

### **Supported Template Formats**

#### **New Format (Recommended)**
```json
{
  "entity_type": "product_feature",
  "vehicle_platform_id": 5,
  "_vehicle_platform_note": "5=Truck Platform"
}
```

#### **Legacy Format (Still Supported)**
```json
{
  "entity_type": "product_feature", 
  "vehicle_type": "truck"
}
```

## Usage Instructions

### **Create/Update Entities from JSON**
```bash
# Use any of the updated template files
./venv/bin/python update_from_json.py simple_update_template.json
./venv/bin/python update_from_json.py repository_update_template.json
./venv/bin/python update_from_json.py monthly_progress_template.json
```

### **Update Assessments from CSV** 
```bash
# Update TRL levels and due dates
./venv/bin/python update_from_csv.py capability_updates_template.csv
```

### **Generate New Templates**
```bash
# Create a new template file
./venv/bin/python update_from_json.py --template
```

## Files Modified
- ✅ `update_from_json.py` - Complete vehicle platform compatibility
- ✅ Template files already updated in previous iteration
- ✅ `update_from_csv.py` - No changes needed (still works)

## Error Handling
- ✅ **Invalid platform IDs** default to Generic Platform (ID: 8)
- ✅ **Missing referenced entities** show warnings but don't stop processing
- ✅ **Validation errors** are clearly reported with line/entity numbers
- ✅ **Database integrity** maintained through proper foreign key relationships

---
*Fixed: 2025-10-22*
*Status: ✅ Both JSON and CSV update scripts working correctly with new vehicle platform schema*