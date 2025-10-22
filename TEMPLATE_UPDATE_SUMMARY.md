# Template Update Summary - Vehicle Platform ID Migration

## Overview
Updated all JSON and CSV template files to reflect the database schema change from `vehicle_type` string fields to `vehicle_platform_id` foreign key references.

## Files Updated

### 1. `simple_update_template.json`
- **Version**: 2.1 → 3.0
- **Changes**: 
  - Replaced `vehicle_type: "truck"` with `vehicle_platform_id: 5`
  - Added `_vehicle_platform_note` with available platform IDs and descriptions
  - Updated metadata notes

### 2. `repository_update_template.json`
- **Version**: 2.1 → 3.0
- **Changes**:
  - Updated all entity creation examples to use `vehicle_platform_id`
  - Added platform ID notes for reference
  - Updated 7 entity creation examples with appropriate platform IDs
  - Enhanced metadata description

### 3. `monthly_progress_template.json`
- **Version**: 2.1 → 3.0
- **Changes**:
  - Updated metadata to reflect schema changes
  - Note: This template focuses on updates, so no vehicle_platform_id fields needed

### 4. `capability_updates_template.csv`
- **Changes**:
  - Added `vehicle_platform_id` column after `notes` column
  - Updated all rows with appropriate platform IDs:
    - Terberg operations: ID 1 (Terberg ATT)
    - General truck operations: ID 5 (Truck Platform)
    - Urban/van operations: ID 6 (Van Platform)
    - Generic operations: ID 8 (Generic Platform)

### 5. `capability_updates_template.json`
- **Version**: 1.1 → 2.0
- **Changes**:
  - Added `vehicle_platform_id` fields to multiple capability entries
  - Added explanatory notes for platform ID selection
  - Updated metadata to reflect changes

### 6. `template_updates.json`
- **Version**: 2.0 → 3.0
- **Changes**:
  - Replaced all `vehicle_type` fields with `vehicle_platform_id`
  - Added platform reference notes
  - Updated 3 entity examples with platform IDs

### 7. `system_configurations_template.json`
- **Status**: No changes required
- **Reason**: This template manages platform creation/configuration, not references to existing platforms

## Vehicle Platform Reference

The following vehicle platforms are available in the database:

| ID | Name | Description |
|----|------|-------------|
| 1 | Terberg ATT | Autonomous Terminal Tractor |
| 2 | CA500 | Autonomous Asset Monitoring Vehicle |
| 3 | T800 | Bradshaw T800 Towing Tractor |
| 4 | AEV | Applied EV Skateboard Platform |
| 5 | Truck Platform | Heavy-duty truck platform for cargo transport |
| 6 | Van Platform | Light commercial vehicle platform |
| 7 | Car Platform | Passenger car platform |
| 8 | Generic Platform | Generic vehicle platform |

## Usage Guidelines

When creating new entities using these templates:

1. **Use `vehicle_platform_id` instead of `vehicle_type`**
2. **Select appropriate platform ID** based on the entity's intended deployment
3. **Reference the platform table** above for correct ID selection
4. **Remove `_vehicle_platform_note` fields** - these are for reference only

## Database Schema Alignment

These template updates ensure compatibility with the new database schema where:
- `ProductFeature.vehicle_platform_id` references `VehiclePlatform.id`
- `TechnicalFunction.vehicle_platform_id` references `VehiclePlatform.id`
- `Capabilities.vehicle_platform_id` references `VehiclePlatform.id`

All templates now properly use foreign key references instead of string values, ensuring data integrity and enabling proper relational queries.

---
*Updated: 2025-10-21*
*Migration Status: Complete*