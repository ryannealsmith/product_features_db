# Product Feature Readiness Database System

A comprehensive web-based database system for tracking and displaying the readiness of canonical product features for autonomous vehicle development. The system manages technical capabilities, vehicle platforms, operational design domains, and environments with advanced JSON-based update capabilities.

## Overview

This system helps autonomous vehicle organizations assess and track the maturity of product features by evaluating the Technical Readiness Level (TRL) of underlying technical capabilities across different operational configurations. Built specifically for the autonomous vehicle industry with realistic examples and comprehensive data management.

## Features

### Core Functionality
- **Dashboard**: Overview of readiness statistics and trends with interactive charts
- **Readiness Assessments**: Detailed tracking of TRL assessments with confidence levels
- **Readiness Matrix**: Matrix view of capabilities across configurations
- **Product Features**: Management of customer-facing autonomous vehicle features
- **Technical Functions**: Technical components that enable autonomous capabilities
- **System Configurations**: Vehicle platforms, ODDs, environments, and trailers

### Advanced JSON Management System
- **Comprehensive CRUD Operations**: Create, read, update, delete via JSON templates
- **Entity Management**: Product Features, Technical Functions, and Readiness Assessments
- **Configuration Management**: Vehicle Platforms, ODDs, Environments, Trailers, TRL definitions
- **Batch Processing**: Update multiple items simultaneously through structured JSON files
- **Template Library**: Pre-built JSON templates for common operations
- **Validation System**: Comprehensive data validation and error reporting

## Database Schema

### Core Entities

1. **Product Features**: Customer-facing autonomous vehicle capabilities (e.g., "Autonomous Highway Driving", "Platooning")
2. **Technical Functions**: Technical components needed for autonomous features (e.g., "Perception System", "Path Planning")
3. **Technical Readiness Levels**: TRL 1-9 scale with detailed descriptions for autonomous vehicle development
4. **Vehicle Platforms**: Autonomous vehicle types and specifications (e.g., "Terberg YT222", "Mercedes-Benz Actros")
5. **ODDs (Operational Design Domains)**: Operating conditions and constraints (e.g., "Port Terminal Operations", "Highway Corridor")
6. **Environments**: Geographic and climate conditions (e.g., "Northern European Maritime", "Continental Highway Network")
7. **Trailers**: Cargo configurations for autonomous trucking (e.g., "40ft Container Chassis", "53ft Dry Van")
8. **Readiness Assessments**: TRL evaluations for specific operational configurations

### Relationships

- Product Features contain multiple Technical Functions
- Technical Functions have multiple Readiness Assessments
- Each Assessment links a Technical Function to a specific configuration (Platform + ODD + Environment + optional Trailer) with a TRL rating and confidence level

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ryannealsmith/product_features_db.git
   cd product_features_db
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database with sample data**:
   ```bash
   python -c "from sample_data import initialize_sample_data; initialize_sample_data()"
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser to `http://localhost:8080`

## Project Structure

```
product_features_db/
├── app.py                              # Main Flask application with database models
├── routes.py                           # Web routes and API endpoints
├── sample_data.py                      # Sample data initialization
├── update_from_json.py                 # JSON-based database update system
├── requirements.txt                    # Python dependencies
├── README.md                           # This documentation
├── venv/                               # Virtual environment (created during setup)
├── instance/                           # SQLite database storage
│   └── product_readiness.db           # SQLite database
├── templates/                          # HTML templates
│   ├── base.html                      # Base template with navigation
│   ├── dashboard.html                 # Main dashboard with charts
│   ├── readiness_assessments.html     # Assessment management
│   ├── readiness_matrix.html          # Matrix view of readiness
│   ├── add_assessment.html            # Assessment creation form
│   ├── product_capabilities.html      # Product feature management
│   ├── technical_capabilities.html    # Technical function management
│   └── configurations.html            # System configuration management
├── JSON Templates/                     # Template library for JSON updates
│   ├── repository_update_template.json    # Comprehensive update template
│   ├── simple_update_template.json        # Basic operations template
│   ├── monthly_progress_template.json     # Progress tracking template
│   ├── system_configurations_template.json # Configuration management template
│   └── TEMPLATE_GUIDE.md              # Template usage documentation
└── __pycache__/                        # Python bytecode cache
```

## Usage Guide

### Getting Started

1. **Dashboard**: Start at the dashboard (`http://localhost:8080`) to see overall readiness statistics
2. **View Data**: Explore existing product features and technical functions
3. **Add Assessments**: Create new readiness assessments for different configurations
4. **Analyze**: Use the matrix view and charts to identify readiness gaps
5. **JSON Updates**: Use template files for batch operations

### JSON-Based Data Management

The system includes a powerful JSON update system for batch operations:

#### Available Templates
- **`repository_update_template.json`**: Comprehensive CRUD operations
- **`simple_update_template.json`**: Basic create/update operations
- **`monthly_progress_template.json`**: Progress tracking updates
- **`system_configurations_template.json`**: Configuration management

#### Using JSON Updates
```bash
# Update entities (Product Features, Technical Functions, Assessments)
python -c "from update_from_json import update_from_json; update_from_json('repository_update_template.json')"

# Update system configurations (Platforms, ODDs, Environments, Trailers)
python -c "from update_from_json import update_from_json; update_from_json('system_configurations_template.json')"
```

#### JSON Template Structure
```json
{
  "metadata": {
    "version": "2.0",
    "description": "Template description",
    "created_by": "Your Name",
    "created_date": "2025-10-21"
  },
  "entities": [
    {
      "type": "product_feature",
      "operation": "create",
      "data": {
        "name": "Advanced Highway Autopilot",
        "description": "Full autonomous highway driving capability"
      }
    }
  ],
  "configurations": [
    {
      "config_type": "vehicle_platform",
      "operation": "create",
      "name": "Tesla Semi",
      "max_payload": 36000.0
    }
  ]
}
```

### Technical Readiness Levels (TRL)

- **TRL 1-3 (Research Phase)**: Basic research and proof of concept
- **TRL 4-6 (Development Phase)**: Technology validation and demonstration
- **TRL 7-9 (Deployment Phase)**: System integration and operational deployment

### Adding Readiness Assessments

1. Navigate to "Assessments" → "New Assessment"
2. Select the technical function to assess
3. Choose the TRL level based on current maturity
4. Select the operational configuration (platform, ODD, environment, trailer)
5. Add assessor information and confidence level (1-5 scale)
6. Include notes about the assessment rationale

### Filtering and Analysis

- Use filters on the Assessments page to focus on specific functions or configurations
- The Readiness Matrix shows all assessed configurations in a comprehensive tabular format
- Dashboard charts provide visual insights into readiness distribution and trends
- Export capabilities for reporting and further analysis

## Sample Data

The system initializes with comprehensive autonomous vehicle industry sample data including:

### Product Features (7 total)
- Autonomous Highway Driving
- Urban Navigation and Maneuvering  
- Platooning Capability
- Automated Docking and Loading
- Emergency Response System
- Fleet Coordination
- Remote Monitoring and Diagnostics

### Technical Functions (17 total)
- Perception System (LiDAR, Camera, Radar)
- Localization and Mapping
- Path Planning and Decision Making
- Vehicle Control Systems
- V2X Communication
- Safety Monitoring System
- And 11 additional technical components

### System Configurations
- **Vehicle Platforms**: Heavy-duty trucks, terminal tractors, delivery vehicles
- **ODDs**: Highway corridors, port terminals, urban environments, mixed traffic
- **Environments**: European maritime, continental highway, Mediterranean logistics
- **Trailers**: Container chassis, dry van, flatbed, refrigerated

### Readiness Assessments
- 50+ assessment examples across different TRL levels
- Multiple configurations per technical function
- Realistic confidence levels and assessment notes
- Progress tracking over time

## API Endpoints

### Web Interface
- `/` - Main dashboard with charts and statistics
- `/product_features` - Product feature management
- `/technical_capabilities` - Technical function management  
- `/readiness_assessments` - Assessment tracking and creation
- `/readiness_matrix` - Matrix view of all assessments
- `/configurations` - System configuration management

### REST API
- `GET /api/readiness_data` - JSON data for charts and analysis
- Additional API endpoints for programmatic access

### JSON Update System
- Command-line interface for batch updates
- Template-based operations for consistency
- Comprehensive validation and error reporting

## Technical Details

- **Framework**: Flask 2.3.3 with SQLAlchemy 3.0.5 ORM
- **Database**: SQLite (easily portable, no setup required)
- **Frontend**: Bootstrap 5 with responsive design and modern UI components
- **Charts**: Chart.js for interactive visualizations and analytics
- **Icons**: Font Awesome for consistent iconography
- **JSON Processing**: Custom validation and batch update system
- **Error Handling**: Comprehensive error reporting and recovery
- **Data Integrity**: Foreign key constraints and validation rules

### Performance Considerations
- Optimized queries for large datasets
- Efficient JSON processing for batch operations
- Responsive design for various screen sizes
- Caching for improved dashboard performance

## Database Relationships

```sql
Product Features (1) → (N) Technical Functions
Technical Functions (1) → (N) Readiness Assessments  
Readiness Assessments (N) → (1) Technical Readiness Level
Readiness Assessments (N) → (1) Vehicle Platform
Readiness Assessments (N) → (1) ODD
Readiness Assessments (N) → (1) Environment
Readiness Assessments (N) → (0..1) Trailer
```

### Entity Relationship Details
- **Cascade Deletes**: Proper cleanup when parent entities are removed
- **Foreign Key Constraints**: Data integrity enforcement
- **Many-to-Many**: Product Features can share Technical Functions
- **Optional Relationships**: Trailers are optional for some assessments

## Customization

### Adding New Entities

1. Define new model classes in `app.py` with proper relationships
2. Add corresponding routes in `routes.py` for CRUD operations
3. Create HTML templates for user interface
4. Update navigation in `base.html`
5. Add JSON template support in `update_from_json.py`

### Modifying TRL Scale

The system uses the standard 9-level TRL scale for autonomous vehicle development, but can be customized by:
1. Modifying `TechnicalReadinessLevel` data in `sample_data.py`
2. Updating validation rules in `update_from_json.py`
3. Adjusting UI components for new TRL ranges

### Styling and Branding

The UI uses Bootstrap 5 with custom CSS classes for:
- TRL badges with color coding
- Confidence indicators with visual scales  
- Responsive charts and data visualizations
- Industry-specific terminology and icons

Modify the `<style>` section in `base.html` to customize appearance.

### JSON Template Customization

Create custom JSON templates by:
1. Following the structure in existing templates
2. Adding validation rules for new entity types
3. Testing with small datasets before production use
4. Documenting custom fields and operations

## Contributing

1. **Code Standards**: Follow existing code structure and naming conventions
2. **Error Handling**: Add proper error handling and validation for all operations
3. **Documentation**: Include docstrings for new functions and classes
4. **Testing**: Test with sample data and JSON templates before committing changes
5. **JSON Templates**: Update template files when adding new entity types
6. **Database Changes**: Include migration scripts for schema modifications

### Development Workflow

1. Create feature branches for new functionality
2. Test locally with sample data
3. Validate JSON update capabilities 
4. Update documentation as needed
5. Submit pull requests with detailed descriptions

## Version History

- **v2.0** (October 2025): Added comprehensive JSON management system, enhanced UI, configuration management
- **v1.0** (Initial): Basic readiness tracking with web interface

## Repository

**GitHub**: https://github.com/ryannealsmith/product_features_db

## License

This project is provided for educational and demonstration purposes in autonomous vehicle development.