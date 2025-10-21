from app import app, db, ProductFeature, TechnicalCapability, TechnicalReadinessLevel, VehiclePlatform, ODD, Environment, Trailer, ReadinessAssessment

def initialize_sample_data():
    """Initialize the database with sample data"""
    
    # Technical Readiness Levels (TRL 1-9)
    trl_data = [
        (1, "Basic principles observed", "Scientific research begins to be translated into applied research and development"),
        (2, "Technology concept formulated", "Practical applications can be invented"),
        (3, "Experimental proof of concept", "Active research and development is initiated"),
        (4, "Technology validated in lab", "Basic technological components are integrated"),
        (5, "Technology validated in environment", "Technology components and/or basic technology subsystems are integrated with realistic supporting elements"),
        (6, "Technology demonstrated in environment", "Representative model or prototype system is tested in a relevant environment"),
        (7, "System prototype demonstrated", "Prototype near or at planned operational system"),
        (8, "System complete and qualified", "Technology has been proven to work in its final form and under expected conditions"),
        (9, "Actual system proven in operational environment", "Actual application of technology in its final form")
    ]
    
    for level, name, description in trl_data:
        trl = TechnicalReadinessLevel(level=level, name=name, description=description)
        db.session.add(trl)
    
    # Product Features
    product_features = [
        ("Terberg: Driver-in operations (semi-trailer)", "Forward only operations with driver in vehicle towing a trailer."),
        ("Terberg: Driver-Out, AV only, FWD", "Forward only operations with no driver in vehicle, towing a trailer"),
        ("Platooning", "Multiple vehicles can follow each other closely in automated convoy"),
        ("Remote Vehicle Operation", "Vehicle can be operated remotely by a human operator"),
        ("Cargo Handling Automation", "Automated loading and unloading of cargo"),
        ("Fleet Management", "Centralized management and coordination of vehicle fleets")
    ]
    
    for name, description in product_features:
        feature = ProductFeature(name=name, description=description)
        db.session.add(feature)
    
    db.session.commit()  # Commit to get IDs
    
    # Technical Capabilities
    technical_capabilities = [
        # Terberg: Driver-in operations (semi-trailer)
        ("Perception System", "Camera, LiDAR, and radar sensor fusion for environment perception", 1),
        ("Path Planning", "Real-time trajectory planning and optimization", 1),
        ("Vehicle Control", "Precise control of steering, acceleration, and braking", 1),
        ("Localization", "High-precision vehicle positioning and mapping", 1),
        ("Detect proximal humans", "Switch to SAFESTATE when a human violates buffer", 1),
        
        # Urban Autonomous Navigation
        ("Traffic Light Recognition", "Detection and interpretation of traffic signals", 2),
        ("Pedestrian Detection", "Detection and tracking of pedestrians", 2),
        ("Intersection Handling", "Safe navigation through complex intersections", 2),
        
        # Automated Parking
        ("Parking Space Detection", "Identification of suitable parking spaces", 3),
        ("Low-Speed Maneuvering", "Precise control for parking maneuvers", 3),
        
        # Platooning
        ("Vehicle-to-Vehicle Communication", "V2V communication for coordination", 4),
        ("Convoy Formation", "Automatic formation and maintenance of vehicle convoys", 4),
        
        # Remote Vehicle Operation
        ("Teleoperation Interface", "Human-machine interface for remote operation", 5),
        ("Low-Latency Communication", "Real-time communication with remote operators", 5),
        
        # Cargo Handling Automation
        ("Robotic Loading System", "Automated cargo loading and securing", 6),
        ("Cargo Tracking", "Real-time monitoring of cargo status", 6),
        
        # Fleet Management
        ("Route Optimization", "Dynamic route planning for multiple vehicles", 7),
        ("Vehicle Health Monitoring", "Real-time monitoring of vehicle systems", 7)
    ]
    
    for name, description, product_id in technical_capabilities:
        capability = TechnicalCapability(name=name, description=description, product_feature_id=product_id)
        db.session.add(capability)
    
    # Vehicle Platforms
    vehicle_platforms = [
        ("Terberg ATT", "Autonomous Terminal Tractork", "ATT", 40000),
        ("CA500", "Autonomous Asset Monitoring Vehicle", "CA500", 500),
        ("T800", "Bradshaw T800 Towing Tractor", "T800", 800),
        ("AEV", "Applied EV Skateboard Platform", "AEV", 1000)
    ]
    
    for name, description, vehicle_type, max_payload in vehicle_platforms:
        platform = VehiclePlatform(name=name, description=description, vehicle_type=vehicle_type, max_payload=max_payload)
        db.session.add(platform)
    
    # ODDs (Operational Design Domains)
    odds = [
        ("Port Baseline", "Forward towing of a semi-trailer", 25, "two-way", "Nominal lanes width (+1m - +2.0m buffer)", "junctions", "bridges", "pedestrian crossings", "pedestrians, other vehicles", "crane, reach stacker", "dry, wet", "max uphill 5%, max downhill 5%"),
        ("Port: AV-Ped interaction", "Baseline with Pedestrian interaction", 25, "two-way", "Queueing lanes width (+0.5m buffer)", "junctions, accomodate trailers", "bridges", "pedestrian crossings, school zones", "pedestrians, cyclists, other vehicles", "crane, reach stacker", "dry, wet", "max uphill 3%, max downhill 3%"),
        ("Port: Movable pinning stations", "Baseline with human-robot interaction", 25, "two-way", "Lane change, Lane borrow", "junctions", "bridges", "pedestrian crossings", "pedestrians, other vehicles", "gantry (mobile), gantry (stacked)", "dry, wet, fog", "max uphill 5%, max downhill 5%"),
        ("Factory: baseline", "Limited access roads and depots", 8, "one-way", "Nominal lanes width (+1m - +2.0m buffer)", "junctions", "tunnels", "school zones", "pedestrians, cyclists", "crane, gantry (stacked)", "dry", "max uphill 2%, max downhill 2%")
    ]
    
    for name, description, max_speed, direction, lanes, intersections, infrastructure, hazards, actors, handling_equipment, traction, inclines in odds:
        odd = ODD(name=name, description=description, max_speed=max_speed, 
                 direction=direction, lanes=lanes, intersections=intersections,
                 infrastructure=infrastructure, hazards=hazards, actors=actors,
                 handling_equipment=handling_equipment, traction=traction, inclines=inclines)
        db.session.add(odd)
    
    # Environments
    environments = [
        ("North American Temperate", "Temperate climate regions of North America", "North America", "temperate", "varied"),
        ("European Urban", "Dense European urban environments", "Europe", "temperate", "flat to hilly"),
        ("Desert Regions", "Hot, dry desert environments", "Global", "arid", "flat"),
        ("Cold Climate", "Northern regions with harsh winters", "Global", "arctic", "varied")
    ]
    
    for name, description, region, climate, terrain in environments:
        env = Environment(name=name, description=description, region=region, 
                         climate=climate, terrain=terrain)
        db.session.add(env)
    
    # Trailers
    trailers = [
        ("No trailer", "Driving without a trailer", "bobtailing", None, 0, 0),
        ("Semi-trailer: Boxcar; Vantec model; variable weight", "Semi-trailer with a boxcar design", "VTsemi", 16.15, 34000, 2),
        ("Semi-trailer: Chassis; City Terminal model; chassis + container (variable weight)", "Semi-trailer chassis for container transport", "CTchassis", 16.15, 34000, 2),
        ("Semi-trailer: Chassis; Jebel Ali model; chassis + container (variable weight)", "Semi-trailer chassis for container transport", "JAchassis", 16.15, 34000, 2),
        ("Unloaded bomb cart", "Unloaded bomb cart", "unloaded", 15, 8000, 2),
        ("Bomb cart with an empty 20ft container", "Empty 20ft container", "empty20", 20, 10000, 2),
        ("Bomb cart with a fully-loaded 20ft container", "Loaded 20ft container", "loaded20", 20, 24000, 2),
        ("Bomb cart with an empty 40ft container", "Empty 40ft container", "empty40", 40, 12000, 2),
        ("Bomb cart with a fully-loaded 40ft container", "Loaded 40ft container", "loaded40", 40, 38000, 2),
        ("Semi-trailer: Boat; Robotraz model; chassis + container (variable weight)", "T800 Boat trailer", "RBboat", 16.15, 500, 1),
        ("Drawbar trailer: XX model, single, variable weight", "Drawbar trailer", "DBsingle", 12, 15000, 1)
    ]
    
    for name, description, trailer_type, length, max_weight, axle_count in trailers:
        trailer = Trailer(name=name, description=description, trailer_type=trailer_type,
                         length=length, max_weight=max_weight, axle_count=axle_count)
        db.session.add(trailer)
    
    db.session.commit()  # Commit to get all IDs
    
    # Sample Readiness Assessments
    import random
    from datetime import date, timedelta
    
    # Get all entities for creating assessments
    tech_caps = TechnicalCapability.query.all()
    platforms = VehiclePlatform.query.all()
    odds_list = ODD.query.all()
    envs = Environment.query.all()
    trailers_list = Trailer.query.all()
    trl_levels = TechnicalReadinessLevel.query.all()
    
    assessors = ["Dr. Smith", "Engineer Johnson", "Tech Lead Davis", "Manager Wilson"]
    confidence_levels = ["high", "medium", "low"]
    
    # Create sample assessments
    for tech_cap in tech_caps[:10]:  # Limit to first 10 for demo
        for platform in platforms[:2]:  # First 2 platforms
            for odd in odds_list[:2]:  # First 2 ODDs
                for env in envs[:2]:  # First 2 environments
                    # Randomly assign TRL based on capability maturity
                    if "Perception" in tech_cap.name or "Control" in tech_cap.name:
                        trl_level = random.choice([trl for trl in trl_levels if trl.level >= 6])
                    elif "Communication" in tech_cap.name or "Planning" in tech_cap.name:
                        trl_level = random.choice([trl for trl in trl_levels if 4 <= trl.level <= 7])
                    else:
                        trl_level = random.choice(trl_levels)
                    
                    assessment = ReadinessAssessment(
                        technical_capability_id=tech_cap.id,
                        readiness_level_id=trl_level.id,
                        vehicle_platform_id=platform.id,
                        odd_id=odd.id,
                        environment_id=env.id,
                        trailer_id=random.choice(trailers_list).id if random.random() > 0.3 else None,
                        assessor=random.choice(assessors),
                        notes=f"Assessment for {tech_cap.name} on {platform.name}",
                        confidence_level=random.choice(confidence_levels),
                        next_review_date=date.today() + timedelta(days=random.randint(30, 180))
                    )
                    db.session.add(assessment)
    
    db.session.commit()
    print("Sample data initialized successfully!")