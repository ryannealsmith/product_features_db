# JSON Update System for Product Feature Readiness Database

This system allows you to update due dates and Technical Readiness Levels (TRL) for both product capabilities and technical capabilities using structured JSON files.

## Files

- `update_from_json.py` - Main script for updating from JSON files
- `capability_updates_template.json` - Template JSON file with comprehensive examples

## JSON Structure

### Root Level
```json
{
  "metadata": { ... },
  "updates": [ ... ]
}
```

### Metadata Section (Optional)
```json
{
  "metadata": {
    "version": "1.0",
    "description": "Description of this update batch",
    "created_by": "Your Name",
    "created_date": "2025-10-21T00:00:00Z",
    "notes": "Additional information"
  }
}
```

### Updates Section (Required)
```json
{
  "updates": [
    {
      "capability_type": "product",           // Required: "product" or "technical"
      "capability_name": "Exact Name",        // Required: must match database exactly
      "due_date": "2025-12-31",              // Optional: YYYY-MM-DD format
      "target_trl": 7,                       // Optional: 1-9
      "assessor": "Dr. Smith",               // Optional: assessor name
      "notes": "Assessment notes"            // Optional: detailed notes
    }
  ]
}
```

### Field Details

**Required Fields:**
- `capability_type` - Must be either "product" or "technical"
- `capability_name` - Exact name of the capability as it appears in the database

**Optional Fields:**
- `due_date` - Target completion date (multiple formats supported)
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
- `YYYY-MM-DDTHH:MM:SS` (2025-12-31T23:59:59)
- `YYYY-MM-DDTHH:MM:SSZ` (2025-12-31T23:59:59Z)

## Usage

### 1. Update from JSON File
```bash
python update_from_json.py your_updates.json
```

### 2. Export Current Data
```bash
# Export to default file (current_capabilities.json)
python update_from_json.py --export

# Export to specific file
python update_from_json.py --export my_export.json
```

### 3. Get Help
```bash
python update_from_json.py --help
```

## How It Works

### For Product Capabilities
When you update a product capability:
- **Due Date**: Updates the `next_review_date` for ALL readiness assessments of ALL technical capabilities under that product capability
- **Target TRL**: Updates the TRL for ALL readiness assessments of ALL technical capabilities under that product capability

### For Technical Capabilities
When you update a technical capability:
- **Due Date**: Updates the `next_review_date` for ALL readiness assessments of that specific technical capability
- **Target TRL**: Updates the TRL for ALL readiness assessments of that specific technical capability

### Assessment Updates
When TRL is updated, the script also:
- Sets the `assessment_date` to the current timestamp
- Updates the `assessor` if provided in JSON
- Updates the `notes` if provided in JSON

## Example Workflow

1. **Export current data** to see what capabilities exist:
   ```bash
   python update_from_json.py --export current_status.json
   ```

2. **Create your update file** based on the template:
   ```bash
   cp capability_updates_template.json my_updates.json
   # Edit my_updates.json with your changes
   ```

3. **Apply the updates**:
   ```bash
   python update_from_json.py my_updates.json
   ```

4. **Verify changes** in the web application or export again to check

## Validation and Error Handling

The script provides comprehensive validation:

### Pre-processing Validation
- ✅ JSON format validation
- ✅ Required field presence
- ✅ Capability type validation (product/technical)
- ✅ TRL range validation (1-9)
- ✅ Date format validation
- ✅ Capability name existence in database

### Processing Feedback
- 📊 Detailed progress reporting
- ⚠️ Warnings for missing capabilities or invalid data
- ❌ Clear error messages with specific issues
- 📈 Summary statistics at completion

### Example Output
```
Processing JSON file: my_updates.json
Version: 1.0
Description: Q4 2025 capability updates
Created by: Project Manager
Created: 2025-10-21T00:00:00Z
Found 12 updates to process
------------------------------------------------------------
Processing 12 valid updates...
------------------------------------------------------------
Update 1: Updated Terberg: Driver-in operations (semi-trailer) - due date to 2025-12-31 for 8 related assessments, TRL to 7 for 8 related assessments
Update 2: Updated Perception System - due date to 2025-11-15 for 4 assessments, TRL to 8 for 4 assessments
...
------------------------------------------------------------
Update completed!
Successfully updated: 12 capabilities
Errors encountered: 0
Total processed: 12
```

## Advantages of JSON Format

### Over CSV:
- **Structured Data**: Better organization with metadata and validation
- **Nested Information**: Support for complex data structures
- **Comments**: Metadata section for documentation
- **Type Safety**: Native support for numbers, booleans, dates
- **Validation**: Built-in JSON schema validation capabilities

### Rich Metadata:
- Version tracking
- Creation timestamps
- Batch descriptions
- Processing history

### Better Error Handling:
- Line-by-line validation before processing
- Detailed error reporting with context
- Rollback capability on errors

## Current Capabilities in Database

### Product Capabilities
- Terberg: Driver-in operations (semi-trailer)
- Terberg: Driver-Out, AV only, FWD
- Platooning
- Remote Vehicle Operation
- Cargo Handling Automation
- Fleet Management

### Technical Capabilities
- Perception System
- Path Planning
- Vehicle Control
- Localization
- Detect proximal humans
- Traffic Light Recognition
- Pedestrian Detection
- Intersection Handling
- Parking Space Detection
- Low-Speed Maneuvering
- Vehicle-to-Vehicle Communication
- Convoy Formation
- Teleoperation Interface
- Low-Latency Communication
- Robotic Loading System
- Cargo Tracking
- Route Optimization
- Vehicle Health Monitoring

## Template Examples

The template includes realistic update scenarios:
- **Q4 2025 Production Targets**: High TRL goals for core systems
- **Safety-Critical Systems**: Enhanced requirements for human detection
- **Research Phase Capabilities**: Early TRL for experimental features
- **Milestone-Based Updates**: Specific due dates tied to project phases

## Best Practices

1. **Use Metadata**: Always include version and description for tracking
2. **Batch Updates**: Group related updates in single JSON files
3. **Validate First**: Use the export feature to verify capability names
4. **Backup Data**: Export current state before major updates
5. **Incremental Updates**: Process small batches to isolate issues
6. **Documentation**: Use notes fields to explain TRL changes

## Troubleshooting

1. **"JSON decode error"** - Check JSON syntax with a validator
2. **"Capability not found"** - Verify exact spelling and case
3. **"Invalid date format"** - Use supported date formats
4. **"Invalid TRL"** - Ensure TRL is a number between 1 and 9
5. **"Module not found"** - Activate virtual environment and check directory

## Integration

The JSON update system integrates seamlessly with:
- **Web Application**: Changes reflect immediately in the UI
- **CSV System**: Can be used alongside CSV updates
- **Export Features**: JSON exports can be modified and re-imported
- **Version Control**: JSON files work well with Git for change tracking