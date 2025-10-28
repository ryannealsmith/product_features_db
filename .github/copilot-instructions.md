# Product Feature Readiness Database System v4.1

This project implements a comprehensive web-based database system for tracking and displaying the readiness of canonical product features for autonomous vehicle development. The system uses Flask for the web framework, SQLite for the database, and includes an advanced JSON management system.

## Project Structure
- Flask web application with HTML/CSS UI and JSON Editor
- SQLite database with enhanced M:N relationship structure
- SQLAlchemy ORM for database operations with association tables
- Bootstrap 5 for responsive UI design
- Interactive JSON Editor with full CRUD operations
- Command-line JSON import/export system

## Key Features
- **Enhanced M:N Relationships**: Product Features ↔ Capabilities ↔ Technical Functions
- **Web-based JSON Editor**: Interactive entity management at `/json_editor`
- **Product Features**: Customer-facing autonomous vehicle capabilities
- **Capabilities**: Intermediate layer connecting features to technical functions
- **Technical Functions**: Technical components enabling autonomous capabilities (formerly technical_capabilities)
- **Technical Readiness Level (TRL)** assessment with confidence levels
- **Vehicle Platform** configuration for different autonomous vehicle types
- **ODD (Operational Design Domain)** management for operating conditions
- **Environment and Trailer** specifications for logistics scenarios
- **Dashboard** with interactive charts and readiness matrix view
- **JSON Management System**: Import/export, templates, and batch operations
- **Automatic Backups**: Timestamped backups before data modifications

## Database Schema (v4.1)
- **product_features** table with enhanced metadata
- **capabilities** table as intermediate M:N connector
- **technical_functions** table (renamed from technical_capabilities)
- **product_feature_capabilities** association table for M:N relationships
- **capability_technical_functions** association table for M:N relationships
- All foreign keys updated to reference `technical_functions` instead of `technical_capabilities`

## Development Guidelines
- Use SQLAlchemy for all database operations with proper M:N relationship handling
- Follow Flask best practices for routing and templates
- Maintain backwards compatibility with `/technical_capabilities` route as alias
- Use `/technical_functions` as primary route for technical function management
- Implement proper error handling and validation for both web and JSON interfaces
- Use Bootstrap 5 for consistent UI styling with modern components
- Include comprehensive sample data for autonomous vehicle industry scenarios
- Support both web-based JSON Editor and command-line JSON operations
- Ensure automatic backup creation before any data modifications
- Use `repository_update_data_final_colin3.json` as primary JSON data file

## JSON Management
- Primary data file: `repository_update_data_final_colin3.json`
- Web interface: `/json_editor` with full CRUD operations
- Command line: `update_from_json.py` script for batch operations
- Template generation: `python update_from_json.py --template`
- Export current state: `python update_from_json.py --export`
- Automatic validation and error reporting for all JSON operations