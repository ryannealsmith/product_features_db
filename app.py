from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_readiness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models

class ProductFeature(db.Model):
    """Product features that can be delivered to customers"""
    __tablename__ = 'product_features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    vehicle_type = db.Column(db.String(50))  # e.g., truck, van, car
    swimlane_decorators = db.Column(db.String(200))  # Swimlane categorization
    label = db.Column(db.String(50))  # e.g., "baseline" or "PF-<SWIM_LANE>-1.1"
    tmos = db.Column(db.Text)  # Target Measure of Success
    status_relative_to_tmos = db.Column(db.Float, default=0.0)  # Percentage (0.0 to 100.0)
    planned_start_date = db.Column(db.Date, nullable=True)
    planned_end_date = db.Column(db.Date, nullable=True)
    active_flag = db.Column(db.String(10), default="next")  # "next" or other status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    technical_capabilities = db.relationship('TechnicalFunction', back_populates='product_feature')
    
    # Many-to-many relationship with Capabilities (list of capabilities required)
    capabilities_required = db.relationship('Capabilities',
                                          secondary='capability_product_features',
                                          back_populates='product_features')
    
    # Self-referential many-to-many for co-dependencies on other product features
    dependencies = db.relationship('ProductFeature',
                                 secondary='product_feature_dependencies',
                                 primaryjoin='ProductFeature.id == product_feature_dependencies.c.product_feature_id',
                                 secondaryjoin='ProductFeature.id == product_feature_dependencies.c.dependency_id',
                                 back_populates='dependent_features')
    
    dependent_features = db.relationship('ProductFeature',
                                       secondary='product_feature_dependencies',
                                       primaryjoin='ProductFeature.id == product_feature_dependencies.c.dependency_id',
                                       secondaryjoin='ProductFeature.id == product_feature_dependencies.c.product_feature_id',
                                       back_populates='dependencies')

    def __repr__(self):
        return f'<ProductFeature {self.name}>'


class TechnicalFunction(db.Model):
    """Technical functions required to enable product features"""
    __tablename__ = 'technical_capabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    product_feature_id = db.Column(db.Integer, db.ForeignKey('product_features.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product_feature = db.relationship('ProductFeature', back_populates='technical_capabilities')
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='technical_function')
    capabilities = db.relationship('Capabilities',
                                  secondary='capability_technical_functions',
                                  back_populates='technical_functions')

    def __repr__(self):
        return f'<TechnicalFunction {self.name}>'


class TechnicalReadinessLevel(db.Model):
    """Technical Readiness Levels (TRL) scale from 1-9"""
    __tablename__ = 'technical_readiness_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='readiness_level')

    def __repr__(self):
        return f'<TRL {self.level}: {self.name}>'


class VehiclePlatform(db.Model):
    """Vehicle platforms where capabilities can be deployed"""
    __tablename__ = 'vehicle_platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    vehicle_type = db.Column(db.String(50))  # e.g., truck, van, car
    max_payload = db.Column(db.Float)  # in kg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='vehicle_platform')

    def __repr__(self):
        return f'<VehiclePlatform {self.name}>'


class ODD(db.Model):
    """Operational Design Domain - conditions under which system operates"""
    __tablename__ = 'odds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    max_speed = db.Column(db.Integer)  # km/h
    direction = db.Column(db.String(50))  # e.g., one-way, two-way, fwd, reverse
    lanes = db.Column(db.String(75))  # e.g., Nominal lanes width (+1m - +2.0m buffer), Queueing lanes width (+0.5m buffer), Lane change, Lane borrow
    intersections = db.Column(db.String(200))  # e.g., junctions, accomodate trailers
    infrastructure = db.Column(db.String(200))  # e.g., bridges, tunnels
    hazards = db.Column(db.String(200))  # e.g., pedestrian crossings, school zones
    actors = db.Column(db.String(200))  # e.g., pedestrians, cyclists, other vehicles
    handling_equipment = db.Column(db.String(200))  # e.g., crane, reach stacker, gantry (mobile), gantry (stacked)
    traction = db.Column(db.String(200)) # e.g., dry , wet , snow, ice
    inclines = db.Column(db.String(100))  # e.g., max uphill, max downhill
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='odd')

    def __repr__(self):
        return f'<ODD {self.name}>'


class Environment(db.Model):
    """Operating environments and geographic conditions"""
    __tablename__ = 'environments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    region = db.Column(db.String(100))
    climate = db.Column(db.String(50))  # e.g., temperate, tropical, arctic
    terrain = db.Column(db.String(100))  # e.g., flat, hilly, mountainous
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='environment')

    def __repr__(self):
        return f'<Environment {self.name}>'


class Trailer(db.Model):
    """Trailer configurations for cargo transport"""
    __tablename__ = 'trailers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    trailer_type = db.Column(db.String(50))  # e.g., flatbed, box, tanker
    length = db.Column(db.Float)  # in meters
    max_weight = db.Column(db.Float)  # in kg
    axle_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    readiness_assessments = db.relationship('ReadinessAssessment', back_populates='trailer')

    def __repr__(self):
        return f'<Trailer {self.name}>'


class Capabilities(db.Model):
    """High-level capabilities that combine technical functions and product features"""
    __tablename__ = 'capabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    success_criteria = db.Column(db.Text, nullable=False)
    vehicle_type = db.Column(db.String(50))  # e.g., truck, van, car
    planned_start_date = db.Column(db.Date, nullable=True)
    planned_end_date = db.Column(db.Date, nullable=True)
    tmos = db.Column(db.Text)  # Target Measure of Success
    progress_relative_to_tmos = db.Column(db.Float, default=0.0)  # Percentage (0.0 to 100.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - many-to-many with technical functions and product features
    # Technical functions required for this capability
    technical_functions = db.relationship('TechnicalFunction', 
                                        secondary='capability_technical_functions',
                                        back_populates='capabilities')
    
    # Related product feature items
    product_features = db.relationship('ProductFeature',
                                     secondary='capability_product_features', 
                                     back_populates='capabilities_required')

    def __repr__(self):
        return f'<Capabilities {self.name}>'


# Association tables for many-to-many relationships
capability_technical_functions = db.Table('capability_technical_functions',
    db.Column('capability_id', db.Integer, db.ForeignKey('capabilities.id'), primary_key=True),
    db.Column('technical_function_id', db.Integer, db.ForeignKey('technical_capabilities.id'), primary_key=True)
)

capability_product_features = db.Table('capability_product_features',
    db.Column('capability_id', db.Integer, db.ForeignKey('capabilities.id'), primary_key=True),
    db.Column('product_feature_id', db.Integer, db.ForeignKey('product_features.id'), primary_key=True)
)

product_feature_dependencies = db.Table('product_feature_dependencies',
    db.Column('product_feature_id', db.Integer, db.ForeignKey('product_features.id'), primary_key=True),
    db.Column('dependency_id', db.Integer, db.ForeignKey('product_features.id'), primary_key=True)
)


class ReadinessAssessment(db.Model):
    """Assessment of technical function readiness for specific configurations"""
    __tablename__ = 'readiness_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    technical_capability_id = db.Column(db.Integer, db.ForeignKey('technical_capabilities.id'), nullable=False)
    readiness_level_id = db.Column(db.Integer, db.ForeignKey('technical_readiness_levels.id'), nullable=False)
    vehicle_platform_id = db.Column(db.Integer, db.ForeignKey('vehicle_platforms.id'), nullable=False)
    odd_id = db.Column(db.Integer, db.ForeignKey('odds.id'), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey('environments.id'), nullable=False)
    trailer_id = db.Column(db.Integer, db.ForeignKey('trailers.id'), nullable=True)
    
    # Assessment details
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    assessor = db.Column(db.String(100))
    notes = db.Column(db.Text)
    confidence_level = db.Column(db.String(20))  # high, medium, low
    next_review_date = db.Column(db.Date)
    
    # Relationships
    technical_function = db.relationship('TechnicalFunction', back_populates='readiness_assessments')
    readiness_level = db.relationship('TechnicalReadinessLevel', back_populates='readiness_assessments')
    vehicle_platform = db.relationship('VehiclePlatform', back_populates='readiness_assessments')
    odd = db.relationship('ODD', back_populates='readiness_assessments')
    environment = db.relationship('Environment', back_populates='readiness_assessments')
    trailer = db.relationship('Trailer', back_populates='readiness_assessments')

    def __repr__(self):
        return f'<ReadinessAssessment {self.technical_function.name} - TRL{self.readiness_level.level}>'


# Import routes after models are defined
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize with sample data if database is empty
        if ProductFeature.query.count() == 0:
            from sample_data import initialize_sample_data
            initialize_sample_data()
    
    app.run(debug=True, port=8080)