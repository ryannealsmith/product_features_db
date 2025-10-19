# Product Feature Readiness Database System

A comprehensive web-based database system for tracking and displaying the readiness of canonical product features based on relational data about technical capabilities, vehicle platforms, operational design domains, and environments.

## Overview

This system helps organizations assess and track the maturity of product features by evaluating the Technical Readiness Level (TRL) of underlying technical capabilities across different operational configurations.

## Features

- **Dashboard**: Overview of readiness statistics and trends
- **Readiness Assessments**: Detailed tracking of TRL assessments
- **Readiness Matrix**: Matrix view of capabilities across configurations
- **Product Capabilities**: Management of product-level features
- **Technical Capabilities**: Technical components that enable products
- **System Configurations**: Vehicle platforms, ODDs, environments, and trailers
- **Interactive Charts**: Visual representation of readiness data

## Database Schema

### Core Entities

1. **Product Capabilities**: Customer-facing features (e.g., "Autonomous Highway Driving")
2. **Technical Capabilities**: Technical components needed for products (e.g., "Perception System")
3. **Technical Readiness Levels**: TRL 1-9 scale with descriptions
4. **Vehicle Platforms**: Different vehicle types and specifications
5. **ODDs (Operational Design Domains)**: Operating conditions and constraints
6. **Environments**: Geographic and climate conditions
7. **Trailers**: Cargo configurations
8. **Readiness Assessments**: TRL evaluations for specific configurations

### Relationships

- Product Capabilities contain multiple Technical Capabilities
- Technical Capabilities have multiple Readiness Assessments
- Each Assessment links a Technical Capability to a specific configuration (Platform + ODD + Environment + optional Trailer) with a TRL rating

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser to `http://localhost:5000`

## Project Structure

```
database/
├── app.py                 # Main Flask application with database models
├── routes.py              # Web routes and API endpoints
├── sample_data.py         # Sample data initialization
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # Main dashboard
│   ├── readiness_assessments.html
│   ├── readiness_matrix.html
│   ├── add_assessment.html
│   ├── product_capabilities.html
│   ├── technical_capabilities.html
│   └── configurations.html
└── product_readiness.db  # SQLite database (created on first run)
```

## Usage Guide

### Getting Started

1. **Dashboard**: Start at the dashboard to see overall readiness statistics
2. **View Data**: Explore existing product and technical capabilities
3. **Add Assessments**: Create new readiness assessments for different configurations
4. **Analyze**: Use the matrix view and charts to identify readiness gaps

### Technical Readiness Levels (TRL)

- **TRL 1-3 (Research Phase)**: Basic research and proof of concept
- **TRL 4-6 (Development Phase)**: Technology validation and demonstration
- **TRL 7-9 (Deployment Phase)**: System integration and operational deployment

### Adding Readiness Assessments

1. Navigate to "Assessments" → "New Assessment"
2. Select the technical capability to assess
3. Choose the TRL level based on current maturity
4. Select the operational configuration (platform, ODD, environment, trailer)
5. Add assessor information and confidence level
6. Include notes about the assessment

### Filtering and Analysis

- Use filters on the Assessments page to focus on specific capabilities or configurations
- The Readiness Matrix shows all assessed configurations in a tabular format
- Charts on the dashboard provide visual insights into readiness distribution

## Sample Data

The system initializes with comprehensive sample data including:

- 7 Product Capabilities (e.g., Autonomous Highway Driving, Urban Navigation)
- 17 Technical Capabilities (e.g., Perception System, Path Planning)
- 4 Vehicle Platforms (Class 8 Truck, Transit Van, etc.)
- 4 Operational Design Domains (Highway, Urban, Mixed Traffic, Controlled Access)
- 4 Operating Environments (North American Temperate, European Urban, etc.)
- 4 Trailer Configurations (53ft Dry Van, Container, Flatbed, Reefer)
- Multiple readiness assessments across different configurations

## API Endpoints

- `GET /api/readiness_data`: JSON data for charts and analysis
- Standard web routes for all CRUD operations

## Technical Details

- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (easily portable, no setup required)
- **Frontend**: Bootstrap 5 with responsive design
- **Charts**: Chart.js for interactive visualizations
- **Icons**: Font Awesome for consistent iconography

## Database Relationships

```sql
Product Capabilities (1) → (N) Technical Capabilities
Technical Capabilities (1) → (N) Readiness Assessments
Readiness Assessments (N) → (1) Technical Readiness Level
Readiness Assessments (N) → (1) Vehicle Platform
Readiness Assessments (N) → (1) ODD
Readiness Assessments (N) → (1) Environment
Readiness Assessments (N) → (0..1) Trailer
```

## Customization

### Adding New Entities

1. Define new model classes in `app.py`
2. Add corresponding routes in `routes.py`
3. Create templates for CRUD operations
4. Update navigation in `base.html`

### Modifying TRL Scale

The system uses the standard 9-level TRL scale, but can be customized by modifying the `TechnicalReadinessLevel` data in `sample_data.py`.

### Styling

The UI uses Bootstrap 5 with custom CSS classes for TRL badges and confidence indicators. Modify the `<style>` section in `base.html` to customize appearance.

## Contributing

1. Follow the existing code structure and naming conventions
2. Add proper error handling and validation
3. Include docstrings for new functions and classes
4. Test with sample data before committing changes

## License

This project is provided as-is for educational and demonstration purposes.