# Database Reset Functionality - Fixed

## Problem Solved
The `reset_db.py` script was automatically adding sample data even when users wanted an empty database.

## Solution Implemented

### 1. Updated `reset_db.py`
- **Added optional parameter**: `--with-sample-data` flag
- **Default behavior**: Creates empty database (no sample data)
- **Optional behavior**: Creates database with sample data when flag is provided

### 2. Created `add_sample_data.py` 
- **Purpose**: Standalone script to add sample data to existing empty database
- **Usage**: `./venv/bin/python add_sample_data.py`

### 3. Fixed Sample Data Schema Issues
- **Updated all entity creation** to use `vehicle_platform_id` instead of `vehicle_type`
- **Added helper function** `get_vehicle_platform_id()` to map vehicle type strings to platform IDs
- **Expanded vehicle platforms** from 4 to 8 platforms to match the migration expectations
- **Fixed relationships** between ProductFeature, TechnicalFunction, Capabilities and VehiclePlatform

## Usage Instructions

### Create Empty Database
```bash
./venv/bin/python reset_db.py
```
Output: `Database reset complete - empty database ready!`

### Create Database with Sample Data  
```bash
./venv/bin/python reset_db.py --with-sample-data
```
Output: `Database reset complete with sample data!`

### Add Sample Data to Existing Empty Database
```bash
./venv/bin/python add_sample_data.py
```
Output: `Sample data added successfully!`

## Database Schema Compatibility

### Vehicle Platform Mapping
The sample data now correctly uses the refactored schema:

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

### Sample Data Distribution
After successful sample data initialization:
- **8 Vehicle Platforms** (all platform types)
- **6 Product Features** (all using Truck Platform)
- **18 Technical Functions** (all using Truck Platform)
- **4 Capabilities** (3 using Truck Platform, 1 using Van Platform)

## Verification Commands

Check database is empty:
```python
from app import app, db, ProductFeature, Capabilities, TechnicalFunction, VehiclePlatform
with app.app_context():
    total = (ProductFeature.query.count() + Capabilities.query.count() + 
             TechnicalFunction.query.count() + VehiclePlatform.query.count())
    print(f"Total records: {total}")
```

Check platform relationships:
```python
with app.app_context():
    pf = ProductFeature.query.first()
    print(f"Platform: {pf.vehicle_platform.name if pf.vehicle_platform else 'None'}")
```

## Files Modified
- ✅ `reset_db.py` - Enhanced with command-line options
- ✅ `add_sample_data.py` - New standalone sample data script  
- ✅ `sample_data.py` - Fixed schema compatibility with vehicle_platform_id foreign keys

---
*Fixed: 2025-10-22*
*Status: ✅ Working correctly*