from app import app, db, ProductFeature, TechnicalFunction, TechnicalReadinessLevel, VehiclePlatform, ODD, Environment, Trailer, ReadinessAssessment, Capabilities

def get_vehicle_platform_id(vehicle_type_str):
    """Map vehicle type string to platform ID"""
    # Create mapping based on existing vehicle platform data
    mapping = {
        "truck": 5,      # Truck Platform
        "van": 6,        # Van Platform  
        "car": 7,        # Car Platform
        "terberg": 1,    # Terberg ATT
        "ca500": 2,      # CA500
        "t800": 3,       # T800
        "aev": 4,        # AEV
        "all": 8     # Any Platform
    }
    return mapping.get(vehicle_type_str.lower(), 8)  # Default to Generic Platform

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
        ("Terberg: Driver-in operations (semi-trailer)", 
         "Forward only operations with driver in vehicle towing a trailer.", 
         "truck", "Baseline", "baseline", "Complete 500 consecutive operations with 99.5% safety record", 85.0, "2024-01-01", "2024-12-31", "active", "https://docs.terberg.com/driver-in-operations"),
        ("Terberg: Driver-Out, AV only, FWD", 
         "Forward only operations with no driver in vehicle, towing a trailer", 
         "truck", "Autonomous", "PF-AUTO-1.1", "Achieve 1000 hours autonomous operation with <0.1 disengagement rate", 65.0, "2024-03-01", "2025-08-31", "next", "https://docs.terberg.com/autonomous-operations"),
        ("Platooning", 
         "Multiple vehicles can follow each other closely in automated convoy", 
         "truck", "Advanced", "PF-ADV-2.1", "Demonstrate 3-vehicle platoon for 100km with 15% fuel savings", 45.0, "2024-06-01", "2025-12-31", "next", None),
        ("Remote Vehicle Operation", 
         "Vehicle can be operated remotely by a human operator", 
         "truck", "Remote", "PF-REM-1.0", "Control vehicle remotely with <200ms latency for 8-hour shifts", 30.0, "2024-09-01", "2025-06-30", "next", "https://wiki.company.com/remote-operations"),
        ("Cargo Handling Automation", 
         "Automated loading and unloading of cargo", 
         "truck", "Automation", "PF-AUTO-3.0", "Automate 95% of cargo handling operations without human intervention", 15.0, "2025-01-01", "2026-12-31", "future", None),
        ("Fleet Management", 
         "Centralized management and coordination of vehicle fleets", 
         "truck", "Management", "PF-MGMT-1.0", "Manage 50+ vehicle fleet with 99% uptime and optimal routing", 75.0, "2024-01-01", "2024-11-30", "active", "https://confluence.company.com/fleet-management")
    ]
    
    from datetime import datetime
    for name, description, vehicle_type, swimlane, label, tmos, status, start_date, end_date, active_flag, document_url in product_features:
        feature = ProductFeature(
            name=name, 
            description=description,
            vehicle_platform_id=get_vehicle_platform_id(vehicle_type),
            swimlane_decorators=swimlane,
            label=label,
            tmos=tmos,
            status_relative_to_tmos=status,
            planned_start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            planned_end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            active_flag=active_flag,
            document_url=document_url
        )
        db.session.add(feature)
    
    db.session.commit()  # Commit to get IDs
    
    # Technical Functions (formerly Technical Capabilities)
    technical_capabilities = [
        # Terberg: Driver-in operations (semi-trailer)
        ("Perception System", "Camera, LiDAR, and radar sensor fusion for environment perception", 
         "Successfully detect and classify 99.9% of relevant objects within 100m range in all weather conditions", 
         "truck", "Achieve 360-degree environmental awareness with <50ms latency", 85.0, "2024-01-01", "2024-10-31", 1, "https://docs.company.com/perception-system"),
        
        ("Path Planning", "Real-time trajectory planning and optimization", 
         "Generate collision-free paths in real-time for complex terminal environments", 
         "truck", "Plan optimal paths with <100ms computation time for 95% of scenarios", 75.0, "2024-02-01", "2024-11-30", 1, None),
        
        ("Vehicle Control", "Precise control of steering, acceleration, and braking", 
         "Maintain vehicle trajectory within 10cm accuracy at all operational speeds", 
         "truck", "Execute control commands with <20ms response time and ±5cm precision", 90.0, "2024-01-01", "2024-09-30", 1, "https://confluence.company.com/vehicle-control"),
        
        ("Localization", "High-precision vehicle positioning and mapping", 
         "Achieve centimeter-level positioning accuracy in GPS-denied environments", 
         "truck", "Maintain <5cm positioning accuracy 99% of the time", 70.0, "2024-03-01", "2024-12-31", 1, None),
        
        ("Detect proximal humans", "Switch to SAFESTATE when a human violates buffer", 
         "Detect humans within 5m safety buffer and trigger emergency stops within 200ms", 
         "truck", "100% detection rate for humans in safety zones with <200ms response", 65.0, "2024-04-01", "2025-01-31", 1, None),
        
        # Urban Autonomous Navigation
        ("Traffic Light Recognition", "Detection and interpretation of traffic signals", 
         "Accurately identify and respond to all standard traffic signals from 50m distance", 
         "truck", "99.5% accuracy in traffic signal detection and classification", 55.0, "2024-05-01", "2025-03-31", 2, None),
        
        ("Pedestrian Detection", "Detection and tracking of pedestrians", 
         "Detect and track pedestrians in all lighting and weather conditions", 
         "truck", "99.9% pedestrian detection rate with <1% false positives", 60.0, "2024-04-01", "2025-02-28", 2, None),
        
        ("Intersection Handling", "Safe navigation through complex intersections", 
         "Navigate intersections with mixed traffic including pedestrians and cyclists", 
         "truck", "Complete intersection traversals with 100% safety record", 40.0, "2024-06-01", "2025-06-30", 2, None),
        
        # Automated Parking
        ("Parking Space Detection", "Identification of suitable parking spaces", 
         "Identify and evaluate parking spaces suitable for vehicle dimensions", 
         "truck", "Detect 95% of available parking spaces with accurate size assessment", 70.0, "2024-03-01", "2024-12-31", 3, None),
        
        ("Low-Speed Maneuvering", "Precise control for parking maneuvers", 
         "Execute complex parking maneuvers in tight spaces with centimeter precision", 
         "truck", "Successfully park in spaces with <50cm clearance on each side", 80.0, "2024-02-01", "2024-11-30", 3, None),
        
        # Platooning
        ("Vehicle-to-Vehicle Communication", "V2V communication for coordination", 
         "Maintain reliable communication between vehicles in platoon formation", 
         "truck", "99.9% communication reliability with <50ms latency between vehicles", 35.0, "2024-07-01", "2025-08-31", 4, None),
        
        ("Convoy Formation", "Automatic formation and maintenance of vehicle convoys", 
         "Form and maintain multi-vehicle convoys with automated spacing control", 
         "truck", "Maintain 10m spacing ±1m in 3-vehicle convoys for 100km", 30.0, "2024-08-01", "2025-10-31", 4, None),
        
        # Remote Vehicle Operation
        ("Teleoperation Interface", "Human-machine interface for remote operation", 
         "Provide intuitive control interface for remote vehicle operation", 
         "truck", "Enable remote operation with <200ms control latency", 45.0, "2024-09-01", "2025-07-31", 5, None),
        
        ("Low-Latency Communication", "Real-time communication with remote operators", 
         "Maintain stable communication link between vehicle and operations center", 
         "truck", "Achieve 99.5% uptime with <150ms average latency", 50.0, "2024-08-01", "2025-06-30", 5, None),
        
        # Cargo Handling Automation
        ("Robotic Loading System", "Automated cargo loading and securing", 
         "Automate cargo loading and securing processes without human intervention", 
         "truck", "Load 95% of standard cargo types autonomously in <10 minutes", 20.0, "2025-01-01", "2026-06-30", 6, None),
        
        ("Cargo Tracking", "Real-time monitoring of cargo status", 
         "Monitor cargo location, condition, and security throughout transport", 
         "truck", "Provide real-time cargo status with 99% accuracy", 75.0, "2024-01-01", "2024-12-31", 7, None),
        
        # Fleet Management
        ("Route Optimization", "Dynamic route planning for multiple vehicles", 
         "Optimize routes for fleet efficiency considering traffic and cargo priorities", 
         "truck", "Reduce total fleet travel time by 15% compared to manual planning", 85.0, "2024-01-01", "2024-11-30", 7, None),
        
        ("Vehicle Health Monitoring", "Real-time monitoring of vehicle systems", 
         "Monitor vehicle health and predict maintenance needs", 
         "truck", "Predict 90% of maintenance needs 48 hours in advance", 70.0, "2024-02-01", "2024-12-31", 7, None)
    ]
    
    from datetime import datetime
    for (name, description, success_criteria, vehicle_type, tmos, status, 
         start_date, end_date, product_id, document_url) in technical_capabilities:
        capability = TechnicalFunction(
            name=name, 
            description=description,
            success_criteria=success_criteria,
            vehicle_platform_id=get_vehicle_platform_id(vehicle_type),
            tmos=tmos,
            status_relative_to_tmos=status,
            planned_start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            planned_end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            product_feature_id=product_id,
            document_url=document_url
        )
        db.session.add(capability)
    
    # Vehicle Platforms
    vehicle_platforms = [
        ("Terberg ATT", "Autonomous Terminal Tractor", "truck", 40000),
        ("CA500", "Autonomous Asset Monitoring Vehicle", "van", 500),
        ("T800", "Bradshaw T800 Towing Tractor", "truck", 800),
        ("AEV", "Applied EV Skateboard Platform", "car", 1000),
        ("Truck Platform", "Heavy-duty truck platform for cargo transport", "truck", 45000),
        ("Van Platform", "Light commercial vehicle platform", "van", 3500),
        ("Car Platform", "Passenger car platform", "car", 500),
        ("Generic Platform", "Generic vehicle platform", "generic", 2000)
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
    tech_caps = TechnicalFunction.query.all()
    platforms = VehiclePlatform.query.all()
    odds_list = ODD.query.all()
    envs = Environment.query.all()
    trailers_list = Trailer.query.all()
    trl_levels = TechnicalReadinessLevel.query.all()
    
    assessors = ["Dr. Smith", "Engineer Johnson", "Tech Lead Davis", "Manager Wilson"]
    current_status_options = ["green", "yellow", "red"]
    
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
                        current_status=random.choice(current_status_options),
                        next_review_date=date.today() + timedelta(days=random.randint(30, 180))
                    )
                    db.session.add(assessment)
    
    # Create sample Capabilities
    capabilities_data = [
        (
            "Autonomous Terminal Operations",
            "Vehicle can perform fully autonomous operations in terminal environment including navigation, cargo handling coordination, and safe interaction with infrastructure and personnel",
            "truck",
            "2024-01-01",
            "2025-06-30",
            "Successfully complete 100 consecutive autonomous terminal operations with 99.9% safety record and 95% efficiency compared to human operators",
            75.0,
            "https://docs.company.com/autonomous-terminal-ops"
        ),
        (
            "Highway Platooning",
            "Multiple vehicles can operate in close formation on highways with automated following and coordination",
            "truck", 
            "2024-03-01",
            "2025-12-31",
            "Demonstrate stable 3-vehicle platoon maintaining 10m spacing at 80km/h for 100km duration with 15% fuel savings",
            45.0,
            None
        ),
        (
            "Urban Delivery Operations", 
            "Autonomous vehicle can navigate urban environments and complete delivery tasks including parking, cargo access, and pedestrian interaction",
            "van",
            "2024-06-01", 
            "2026-03-31",
            "Complete 50 urban delivery routes with 98% on-time delivery rate and zero safety incidents involving pedestrians or cyclists",
            25.0,
            None
        ),
        (
            "Remote Monitoring and Control",
            "Human operators can monitor and control autonomous vehicles from remote operations center with full situational awareness",
            "truck",
            "2024-02-01",
            "2025-09-30", 
            "Achieve 200ms maximum latency for control commands and 99.5% uptime for monitoring systems across 50 vehicle fleet",
            60.0,
            "https://wiki.company.com/remote-operations-center"
        )
    ]
    
    from datetime import datetime
    for name, criteria, vehicle_type, start_date, end_date, tmos, progress, document_url in capabilities_data:
        capability = Capabilities(
            name=name,
            success_criteria=criteria,
            vehicle_platform_id=get_vehicle_platform_id(vehicle_type),
            planned_start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            planned_end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            tmos=tmos,
            progress_relative_to_tmos=progress,
            document_url=document_url
        )
        db.session.add(capability)
    
    db.session.commit()
    
    # Associate capabilities with technical functions and product features
    capabilities = Capabilities.query.all()
    product_features = ProductFeature.query.all()
    technical_functions = TechnicalFunction.query.all()
    
    # Associate "Autonomous Terminal Operations" with relevant functions and features
    terminal_ops = Capabilities.query.filter_by(name="Autonomous Terminal Operations").first()
    if terminal_ops:
        # Add technical functions
        perception = TechnicalFunction.query.filter_by(name="Perception System").first()
        path_planning = TechnicalFunction.query.filter_by(name="Path Planning").first()
        vehicle_control = TechnicalFunction.query.filter_by(name="Vehicle Control").first()
        localization = TechnicalFunction.query.filter_by(name="Localization").first()
        
        if perception:
            terminal_ops.technical_functions.append(perception)
        if path_planning:
            terminal_ops.technical_functions.append(path_planning)
        if vehicle_control:
            terminal_ops.technical_functions.append(vehicle_control)
        if localization:
            terminal_ops.technical_functions.append(localization)
            
        # Add product features
        terberg_ops = ProductFeature.query.filter_by(name="Terberg: Driver-in operations (semi-trailer)").first()
        if terberg_ops:
            terminal_ops.product_features.append(terberg_ops)
    
    # Associate "Highway Platooning" with relevant functions and features
    platooning = Capabilities.query.filter_by(name="Highway Platooning").first()
    if platooning:
        # Add technical functions
        v2v_comm = TechnicalFunction.query.filter_by(name="Vehicle-to-Vehicle Communication").first()
        convoy_formation = TechnicalFunction.query.filter_by(name="Convoy Formation").first()
        
        if v2v_comm:
            platooning.technical_functions.append(v2v_comm)
        if convoy_formation:
            platooning.technical_functions.append(convoy_formation)
        if vehicle_control:
            platooning.technical_functions.append(vehicle_control)
            
        # Add product features  
        platooning_feature = ProductFeature.query.filter_by(name="Platooning").first()
        if platooning_feature:
            platooning.product_features.append(platooning_feature)
    
    # Add sample product feature dependencies
    terberg_driver_in = ProductFeature.query.filter_by(name="Terberg: Driver-in operations (semi-trailer)").first()
    terberg_driver_out = ProductFeature.query.filter_by(name="Terberg: Driver-Out, AV only, FWD").first()
    platooning_pf = ProductFeature.query.filter_by(name="Platooning").first()
    remote_ops = ProductFeature.query.filter_by(name="Remote Vehicle Operation").first()
    fleet_mgmt = ProductFeature.query.filter_by(name="Fleet Management").first()
    cargo_automation = ProductFeature.query.filter_by(name="Cargo Handling Automation").first()
    
    # Set up dependencies: Driver-Out depends on Driver-in
    if terberg_driver_out and terberg_driver_in:
        terberg_driver_out.dependencies.append(terberg_driver_in)
    
    # Platooning depends on Driver-Out operations
    if platooning_pf and terberg_driver_out:
        platooning_pf.dependencies.append(terberg_driver_out)
    
    # Fleet Management depends on Remote Vehicle Operation
    if fleet_mgmt and remote_ops:
        fleet_mgmt.dependencies.append(remote_ops)
    
    # Cargo Automation depends on both Driver-Out and Fleet Management
    if cargo_automation and terberg_driver_out and fleet_mgmt:
        cargo_automation.dependencies.append(terberg_driver_out)
        cargo_automation.dependencies.append(fleet_mgmt)
    
    # Add sample technical function dependencies
    # Get technical functions for creating dependencies
    perception = TechnicalFunction.query.filter_by(name="Perception System").first()
    path_planning = TechnicalFunction.query.filter_by(name="Path Planning").first()
    vehicle_control = TechnicalFunction.query.filter_by(name="Vehicle Control").first()
    localization = TechnicalFunction.query.filter_by(name="Localization").first()
    v2v_comm = TechnicalFunction.query.filter_by(name="Vehicle-to-Vehicle Communication").first()
    convoy_formation = TechnicalFunction.query.filter_by(name="Convoy Formation").first()
    teleoperation = TechnicalFunction.query.filter_by(name="Teleoperation Interface").first()
    
    # Path Planning depends on Perception System and Localization product features
    if path_planning and terberg_driver_in:
        path_planning.product_feature_dependencies.append(terberg_driver_in)
    
    # Vehicle Control depends on multiple basic functions via product features
    if vehicle_control and terberg_driver_in:
        vehicle_control.product_feature_dependencies.append(terberg_driver_in)
    
    # Convoy Formation depends on V2V Communication
    if convoy_formation and v2v_comm:
        # These would need product feature dependencies if we had more complex relationships
        pass
    
    # Teleoperation depends on Remote Vehicle Operation capability
    if teleoperation and platooning:  # Using platooning capability as example
        teleoperation.capability_dependencies.append(platooning)
    
    db.session.commit()
    print("Sample data initialized successfully!")