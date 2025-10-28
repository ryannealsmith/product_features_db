# CSV Update System for Product Feature Readiness Database v4.1

This system allows you to update due dates and Technical Readiness Levels (TRL) for both product features and technical functions using CSV files. Updated for the enhanced M:N relationship structure.

## Files

- `update_from_csv.py` - Main script for updating from CSV files
- `capability_updates_template.csv` - Template CSV file with examples

## CSV Format

### Required Columns
- `capability_type` - Must be "capability" for capabilities or "technical_function" for technical functions
- `capability_name` - Exact name of the entity as it appears in the database

### Optional Columns
- `due_date` - Target completion date (supports multiple formats)
- `target_trl` - Target Technical Readiness Level (1-9)
- `assessor` - Name of the person making the assessment
- `notes` - Additional notes for the assessment

### Date Formats Supported
- `YYYY-MM-DD` (2025-12-31)
- `MM/DD/YYYY` (12/31/2025)
- `DD/MM/YYYY` (31/12/2025)
- `YYYY/MM/DD` (2025/12/31)
- `MM-DD-YYYY` (12-31-2025)
- `DD-MM-YYYY` (31-12-2025)

## Usage

### 1. Update from CSV File
```bash
python update_from_csv.py your_updates.csv
```

### 2. Export Current Data
```bash
# Export to default file (current_capabilities.csv)
python update_from_csv.py --export

# Export to specific file
python update_from_csv.py --export my_export.csv
```

### 3. Get Help
```bash
python update_from_csv.py --help
```

## How It Works

### For Capabilities
When you update a capability:
- **Due Date**: Updates the `next_review_date` for ALL readiness assessments of ALL technical functions linked to that capability
- **Target TRL**: Updates the TRL for ALL readiness assessments of ALL technical functions linked to that capability through the M:N relationship

### For Technical Functions  
When you update a technical function:
- **Due Date**: Updates the `next_review_date` for ALL readiness assessments of that specific technical function
- **Target TRL**: Updates the TRL for ALL readiness assessments of that specific technical function

### Assessment Updates
When TRL is updated, the script also:
- Sets the `assessment_date` to the current timestamp
- Updates the `assessor` if provided in CSV
- Updates the `notes` if provided in CSV

## Example Workflow

1. **Export current data** to see what capabilities exist:
   ```bash
   python update_from_csv.py --export current_status.csv
   ```

2. **Create your update file** based on the template:
   ```bash
   cp capability_updates_template.csv my_updates.csv
   # Edit my_updates.csv with your changes
   ```

3. **Apply the updates**:
   ```bash
   python update_from_csv.py my_updates.csv
   ```

4. **Verify changes** in the web application or export again to check

## Error Handling

The script provides detailed feedback:
- ✅ Successfully updated capabilities
- ⚠️ Warnings for unparseable dates or missing capabilities
- ❌ Errors for invalid data or missing required columns
- 📊 Summary of updates and errors at the end

## Current Entities in Database (v4.1 Structure)

### Product Features (7 total)
- Autonomous Highway Driving
- Urban Navigation and Maneuvering  
- Platooning Capability
- Automated Docking and Loading
- Emergency Response System
- Fleet Coordination
- Remote Monitoring and Diagnostics

### Capabilities (Connected via M:N relationships)
- Highway Navigation
- Lane Keeping  
- Traffic Management
- Collision Avoidance
- Vehicle Communication
- Cargo Operations
- Safety Monitoring

### Technical Functions (17 total)
- Perception System (LiDAR, Camera, Radar)
- Localization and Mapping
- Path Planning and Decision Making
- Vehicle Control Systems
- V2X Communication
- Safety Monitoring System
- Traffic Light Recognition
- Pedestrian Detection
- Intersection Handling
- Parking Space Detection
- Low-Speed Maneuvering
- Vehicle-to-Vehicle Communication
- Convoy Formation
- Teleoperation Interface
- Robotic Loading System
- Route Optimization
- Vehicle Health Monitoring

## Notes

- The script uses the Flask application context, so make sure your virtual environment is activated
- All database changes are committed as a single transaction
- If any errors occur, the entire update is rolled back
- Case-sensitive capability names - use exact matches from the database
- Empty cells in optional columns are ignored
- The script preserves existing data not specified in the CSV

## Troubleshooting

1. **"Capability not found"** - Check the exact spelling and case of capability names
2. **"Invalid date format"** - Use one of the supported date formats
3. **"Invalid TRL"** - TRL must be a number between 1 and 9
4. **"Module not found"** - Make sure you're in the project directory with virtual environment activated