from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db, ProductFeature, TechnicalFunction, TechnicalReadinessLevel, VehiclePlatform, ODD, Environment, Trailer, ReadinessAssessment, Capabilities, capability_technical_functions
from sqlalchemy import and_
from datetime import datetime, date

# Helper functions for export
def get_status_color(status):
    """Get hex color code for status"""
    colors = {
        "green": "#4CAF50",
        "yellow": "#FFC107", 
        "red": "#F44336"
    }
    return colors.get(status, "#9E9E9E")

def calculate_timeline_position(assessment):
    """Calculate timeline position based on dates"""
    now = date.today()
    
    if assessment.scheduled_completion_date:
        # Position based on scheduled completion
        days_from_now = (assessment.scheduled_completion_date - now).days
        quarter = min(4, max(1, (days_from_now // 90) + 1))
        return {
            "quarter": quarter,
            "relative_position": (days_from_now % 90) / 90.0,
            "date": assessment.scheduled_completion_date.isoformat()
        }
    else:
        # Position based on current TRL level (earlier for lower TRL)
        trl_quarter_mapping = {
            1: 4, 2: 4, 3: 3,  # Research phase - future quarters
            4: 3, 5: 2, 6: 2,  # Development phase - mid-term
            7: 1, 8: 1, 9: 1   # Deployment phase - near-term
        }
        quarter = trl_quarter_mapping.get(assessment.readiness_level.level, 2)
        return {
            "quarter": quarter,
            "relative_position": 0.5,
            "date": None
        }

def generate_quarters():
    """Generate next 4 quarters from current date"""
    from datetime import datetime, timedelta
    import calendar
    
    quarters = []
    current_date = datetime.now()
    
    # Determine current quarter
    current_quarter = (current_date.month - 1) // 3 + 1
    current_year = current_date.year
    
    for i in range(4):
        quarter_num = ((current_quarter - 1 + i) % 4) + 1
        year = current_year + ((current_quarter - 1 + i) // 4)
        
        # Calculate quarter start and end dates
        start_month = (quarter_num - 1) * 3 + 1
        end_month = quarter_num * 3
        
        start_date = datetime(year, start_month, 1)
        end_date = datetime(year, end_month, calendar.monthrange(year, end_month)[1])
        
        quarters.append({
            "id": f"Q{quarter_num}_{year}",
            "name": f"Q{quarter_num} {year}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "quarter_number": quarter_num,
            "year": year
        })
    
    return quarters

def generate_milestones(assessments):
    """Generate milestones from assessment completion dates"""
    milestones = []
    
    # Group by completion dates
    completion_dates = {}
    for assessment in assessments:
        if assessment.scheduled_completion_date:
            date_key = assessment.scheduled_completion_date.isoformat()
            if date_key not in completion_dates:
                completion_dates[date_key] = []
            completion_dates[date_key].append(assessment)
    
    # Create milestones
    for date_str, date_assessments in completion_dates.items():
        if len(date_assessments) >= 2:  # Only create milestone if multiple items complete
            milestone = {
                "id": f"milestone_{date_str}",
                "title": f"Milestone: {len(date_assessments)} capabilities complete",
                "date": date_str,
                "items": [f"assessment_{a.id}" for a in date_assessments],
                "description": f"Completion of {', '.join([a.technical_function.name for a in date_assessments[:3]])}{'...' if len(date_assessments) > 3 else ''}",
                "miro_properties": {
                    "shape": "diamond",
                    "width": 100,
                    "height": 100,
                    "background_color": "#2196F3"
                }
            }
            milestones.append(milestone)
    
    return sorted(milestones, key=lambda x: x["date"])

@app.route('/')
def dashboard():
    """Main dashboard showing product feature readiness overview"""
    # Get all product features with their technical capabilities and readiness levels
    product_features = ProductFeature.query.all()
    
    # Get readiness statistics
    total_assessments = ReadinessAssessment.query.count()
    high_readiness = ReadinessAssessment.query.join(TechnicalReadinessLevel).filter(TechnicalReadinessLevel.level >= 7).count()
    medium_readiness = ReadinessAssessment.query.join(TechnicalReadinessLevel).filter(and_(TechnicalReadinessLevel.level >= 4, TechnicalReadinessLevel.level < 7)).count()
    low_readiness = ReadinessAssessment.query.join(TechnicalReadinessLevel).filter(TechnicalReadinessLevel.level < 4).count()
    
    readiness_stats = {
        'total': total_assessments,
        'high': high_readiness,
        'medium': medium_readiness,
        'low': low_readiness
    }
    
    return render_template('dashboard.html', 
                         product_features=product_features,
                         readiness_stats=readiness_stats)

@app.route('/product_features')
def product_features():
    """View all product features with eager loading to prevent N+1 queries"""
    from sqlalchemy.orm import joinedload
    
    features = ProductFeature.query.options(
        joinedload(ProductFeature.vehicle_platform),
        joinedload(ProductFeature.capabilities)
        .joinedload(Capabilities.technical_functions)
        .joinedload(TechnicalFunction.readiness_assessments)
        .joinedload(ReadinessAssessment.readiness_level)
    ).all()
    
    return render_template('product_features.html', features=features)

@app.route('/capabilities')
def capabilities():
    """Capabilities management page"""
    capabilities = Capabilities.query.all()
    return render_template('capabilities.html', capabilities=capabilities)

@app.route('/technical_capabilities')
def technical_capabilities():
    """Technical capabilities management page"""
    technical_functions = TechnicalFunction.query.all()
    return render_template('technical_functions.html', technical_functions=technical_functions)

@app.route('/readiness_assessments')
def readiness_assessments():
    """View all readiness assessments with filtering options"""
    # Get filter parameters
    product_id = request.args.get('product_id', type=int)
    technical_id = request.args.get('technical_id', type=int)
    platform_id = request.args.get('platform_id', type=int)
    min_trl = request.args.get('min_trl', type=int)
    
    # Build query with filters
    query = ReadinessAssessment.query
    
    if product_id:
        query = query.join(TechnicalFunction).filter(TechnicalFunction.product_feature_id == product_id)
    if technical_id:
        query = query.filter(ReadinessAssessment.technical_capability_id == technical_id)
    if platform_id:
        query = query.filter(ReadinessAssessment.vehicle_platform_id == platform_id)
    if min_trl:
        query = query.join(TechnicalReadinessLevel).filter(TechnicalReadinessLevel.level >= min_trl)
    
    assessments = query.all()
    
    # Get data for filter dropdowns
    product_features = ProductFeature.query.all()
    technical_functions = TechnicalFunction.query.all()
    vehicle_platforms = VehiclePlatform.query.all()
    
    return render_template('readiness_assessments.html', 
                         assessments=assessments,
                         product_features=product_features,
                         technical_capabilities=technical_functions,
                         vehicle_platforms=vehicle_platforms)

@app.route('/readiness_matrix')
def readiness_matrix():
    """Display readiness matrix view"""
    # Get all combinations of technical functions and configurations
    technical_functions = TechnicalFunction.query.all()
    vehicle_platforms = VehiclePlatform.query.all()
    odds = ODD.query.all()
    environments = Environment.query.all()
    
    # Create matrix data
    matrix_data = []
    for tech_cap in technical_functions:
        for platform in vehicle_platforms:
            for odd in odds:
                for env in environments:
                    assessment = ReadinessAssessment.query.filter_by(
                        technical_capability_id=tech_cap.id,
                        vehicle_platform_id=platform.id,
                        odd_id=odd.id,
                        environment_id=env.id
                    ).first()
                    
                    if assessment:
                        matrix_data.append({
                            'technical_capability': tech_cap.name,
                            'vehicle_platform': platform.name,
                            'odd': odd.name,
                            'environment': env.name,
                            'trl_level': assessment.readiness_level.level,
                            'trl_name': assessment.readiness_level.name,
                            'current_status': assessment.current_status,
                            'assessment_date': assessment.assessment_date
                        })
    
    return render_template('readiness_matrix.html', matrix_data=matrix_data)

@app.route('/configurations')
def configurations():
    """View and manage system configurations"""
    vehicle_platforms = VehiclePlatform.query.all()
    odds = ODD.query.all()
    environments = Environment.query.all()
    trailers = Trailer.query.all()
    readiness_levels = TechnicalReadinessLevel.query.order_by(TechnicalReadinessLevel.level).all()
    
    return render_template('configurations.html',
                         vehicle_platforms=vehicle_platforms,
                         odds=odds,
                         environments=environments,
                         trailers=trailers,
                         readiness_levels=readiness_levels)

@app.route('/add_assessment', methods=['GET', 'POST'])
def add_assessment():
    """Add new readiness assessment"""
    if request.method == 'POST':
        # Handle scheduled_completion_date conversion
        scheduled_completion_date = None
        if request.form.get('scheduled_completion_date'):
            from datetime import datetime
            scheduled_completion_date = datetime.strptime(request.form['scheduled_completion_date'], '%Y-%m-%d').date()
        
        assessment = ReadinessAssessment(
            technical_capability_id=request.form['technical_capability_id'],
            readiness_level_id=request.form['readiness_level_id'],
            vehicle_platform_id=request.form['vehicle_platform_id'],
            odd_id=request.form['odd_id'],
            environment_id=request.form['environment_id'],
            trailer_id=request.form.get('trailer_id') or None,
            assessor=request.form['assessor'],
            notes=request.form['notes'],
            current_status=request.form['current_status'],
            scheduled_completion_date=scheduled_completion_date
        )
        
        db.session.add(assessment)
        db.session.commit()
        flash('Assessment added successfully!', 'success')
        return redirect(url_for('readiness_assessments'))
    
    # GET request - show form
    technical_functions = TechnicalFunction.query.all()
    readiness_levels = TechnicalReadinessLevel.query.order_by(TechnicalReadinessLevel.level).all()
    vehicle_platforms = VehiclePlatform.query.all()
    odds = ODD.query.all()
    environments = Environment.query.all()
    trailers = Trailer.query.all()
    
    return render_template('add_assessment.html',
                         technical_functions=technical_functions,
                         readiness_levels=readiness_levels,
                         vehicle_platforms=vehicle_platforms,
                         odds=odds,
                         environments=environments,
                         trailers=trailers)

@app.route('/add_product_feature', methods=['GET', 'POST'])
def add_product_feature():
    """Add new product feature"""
    if request.method == 'POST':
        # Handle date conversions
        planned_start_date = None
        planned_end_date = None
        
        if request.form.get('planned_start_date'):
            from datetime import datetime
            planned_start_date = datetime.strptime(request.form['planned_start_date'], '%Y-%m-%d').date()
        
        if request.form.get('planned_end_date'):
            from datetime import datetime
            planned_end_date = datetime.strptime(request.form['planned_end_date'], '%Y-%m-%d').date()
        
        # Handle status_relative_to_tmos conversion
        status_relative_to_tmos = 0.0
        if request.form.get('status_relative_to_tmos'):
            try:
                status_relative_to_tmos = float(request.form['status_relative_to_tmos'])
            except ValueError:
                status_relative_to_tmos = 0.0
        
        product_feature = ProductFeature(
            name=request.form['name'],
            description=request.form.get('description', ''),
            vehicle_platform_id=request.form.get('vehicle_platform_id') or None,
            swimlane_decorators=request.form.get('swimlane_decorators', ''),
            label=request.form.get('label', ''),
            tmos=request.form.get('tmos', ''),
            status_relative_to_tmos=status_relative_to_tmos,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            active_flag=request.form.get('active_flag', 'next'),
            document_url=request.form.get('document_url', '')
        )
        
        try:
            db.session.add(product_feature)
            db.session.flush()  # Get the ID before committing
            
            # Note: With the new structure, capabilities are owned by product features
            # This route now focuses on creating the product feature
            # Capabilities can be added separately through a dedicated interface
            
            db.session.commit()
            flash('Product feature added successfully!', 'success')
            return redirect(url_for('product_features'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product feature: {str(e)}', 'danger')
    
    # GET request - show form
    vehicle_platforms = VehiclePlatform.query.all()
    
    return render_template('add_product_feature.html',
                         vehicle_platforms=vehicle_platforms)

@app.route('/add_capability', methods=['GET', 'POST'])
def add_capability():
    """Add new capability"""
    if request.method == 'POST':
        # Handle date conversions
        planned_start_date = None
        planned_end_date = None
        
        if request.form.get('planned_start_date'):
            from datetime import datetime
            planned_start_date = datetime.strptime(request.form['planned_start_date'], '%Y-%m-%d').date()
        
        if request.form.get('planned_end_date'):
            from datetime import datetime
            planned_end_date = datetime.strptime(request.form['planned_end_date'], '%Y-%m-%d').date()
        
        # Handle progress_relative_to_tmos conversion
        progress_relative_to_tmos = 0.0
        if request.form.get('progress_relative_to_tmos'):
            try:
                progress_relative_to_tmos = float(request.form['progress_relative_to_tmos'])
            except ValueError:
                progress_relative_to_tmos = 0.0
        
        capability = Capabilities(
            name=request.form['name'],
            success_criteria=request.form['success_criteria'],
            product_feature_id=request.form['product_feature_id'],
            vehicle_platform_id=request.form.get('vehicle_platform_id') or None,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            tmos=request.form.get('tmos', ''),
            progress_relative_to_tmos=progress_relative_to_tmos,
            document_url=request.form.get('document_url', '')
        )
        
        try:
            db.session.add(capability)
            db.session.flush()  # Get the ID before adding relationships
            
            # Add technical function dependencies if specified
            technical_function_ids = request.form.getlist('technical_function_ids')
            if technical_function_ids:
                technical_functions = TechnicalFunction.query.filter(TechnicalFunction.id.in_(technical_function_ids)).all()
                capability.technical_functions.extend(technical_functions)
            
            db.session.commit()
            flash('Capability added successfully!', 'success')
            return redirect(url_for('capabilities'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding capability: {str(e)}', 'danger')
    
    # GET request - show form
    vehicle_platforms = VehiclePlatform.query.all()
    product_features = ProductFeature.query.all()
    technical_functions = TechnicalFunction.query.all()
    
    return render_template('add_capability.html',
                         vehicle_platforms=vehicle_platforms,
                         product_features=product_features,
                         technical_functions=technical_functions)

@app.route('/add_technical_function', methods=['GET', 'POST'])
def add_technical_function():
    """Add new technical function"""
    if request.method == 'POST':
        # Handle date conversions
        planned_start_date = None
        planned_end_date = None
        
        if request.form.get('planned_start_date'):
            from datetime import datetime
            planned_start_date = datetime.strptime(request.form['planned_start_date'], '%Y-%m-%d').date()
        
        if request.form.get('planned_end_date'):
            from datetime import datetime
            planned_end_date = datetime.strptime(request.form['planned_end_date'], '%Y-%m-%d').date()
        
        # Handle status_relative_to_tmos conversion
        status_relative_to_tmos = 0.0
        if request.form.get('status_relative_to_tmos'):
            try:
                status_relative_to_tmos = float(request.form['status_relative_to_tmos'])
            except ValueError:
                status_relative_to_tmos = 0.0
        
        technical_function = TechnicalFunction(
            name=request.form['name'],
            description=request.form.get('description', ''),
            success_criteria=request.form['success_criteria'],
            vehicle_platform_id=request.form.get('vehicle_platform_id') or None,
            tmos=request.form.get('tmos', ''),
            status_relative_to_tmos=status_relative_to_tmos,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            document_url=request.form.get('document_url', '')
        )
        
        try:
            db.session.add(technical_function)
            db.session.flush()  # Get the ID before adding relationships
            
            # Add capability relationships if specified
            capability_ids = request.form.getlist('capability_ids')
            if capability_ids:
                capabilities = Capabilities.query.filter(Capabilities.id.in_(capability_ids)).all()
                technical_function.capabilities.extend(capabilities)
            
            db.session.commit()
            flash('Technical function added successfully!', 'success')
            return redirect(url_for('technical_capabilities'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding technical function: {str(e)}', 'danger')
    
    # GET request - show form
    vehicle_platforms = VehiclePlatform.query.all()
    capabilities = Capabilities.query.all()
    
    return render_template('add_technical_function.html',
                         vehicle_platforms=vehicle_platforms,
                         capabilities=capabilities)

@app.route('/api/readiness_data')
def api_readiness_data():
    """API endpoint for readiness data (for charts/graphs)"""
    # Get readiness distribution by TRL level
    trl_distribution = db.session.query(
        TechnicalReadinessLevel.level,
        TechnicalReadinessLevel.name,
        db.func.count(ReadinessAssessment.id).label('count')
    ).join(ReadinessAssessment).group_by(TechnicalReadinessLevel.level).all()
    
    # Get readiness by product feature - use explicit joins with the many-to-many relationship
    product_readiness = db.session.query(
        ProductFeature.name,
        db.func.avg(TechnicalReadinessLevel.level).label('avg_trl')
    ).select_from(ProductFeature)\
     .join(Capabilities, ProductFeature.id == Capabilities.product_feature_id)\
     .join(capability_technical_functions, Capabilities.id == capability_technical_functions.c.capability_id)\
     .join(TechnicalFunction, TechnicalFunction.id == capability_technical_functions.c.technical_function_id)\
     .join(ReadinessAssessment, TechnicalFunction.id == ReadinessAssessment.technical_function_id)\
     .join(TechnicalReadinessLevel, ReadinessAssessment.technical_readiness_level_id == TechnicalReadinessLevel.id)\
     .group_by(ProductFeature.name).all()
    
    return jsonify({
        'trl_distribution': [{'level': t.level, 'name': t.name, 'count': t.count} for t in trl_distribution],
        'product_readiness': [{'name': p.name, 'avg_trl': float(p.avg_trl)} for p in product_readiness]
    })

@app.route('/export')
def export_info():
    """Show export options and statistics"""
    # Get statistics for display
    total_assessments = ReadinessAssessment.query.count()
    product_features_count = ProductFeature.query.count()
    
    # Status distribution
    status_counts = {}
    for status in ['green', 'yellow', 'red']:
        status_counts[status] = ReadinessAssessment.query.filter_by(current_status=status).count()
    
    # Completion date statistics
    with_dates = ReadinessAssessment.query.filter(ReadinessAssessment.scheduled_completion_date.isnot(None)).count()
    without_dates = total_assessments - with_dates
    
    completion_stats = {
        'with_dates': with_dates,
        'without_dates': without_dates
    }
    
    return render_template('export_info.html',
                         total_assessments=total_assessments,
                         product_features_count=product_features_count,
                         status_counts=status_counts,
                         completion_stats=completion_stats)

@app.route('/export/miro_roadmap')
def export_miro_roadmap():
    """Export assessment data in a format suitable for Miro roadmap visualization"""
    from datetime import datetime, timedelta
    import json
    
    # Get all assessments with related data
    assessments = db.session.query(ReadinessAssessment).join(
        TechnicalFunction
    ).join(TechnicalReadinessLevel).all()
    
    # Create roadmap structure
    roadmap_data = {
        "meta": {
            "export_date": datetime.now().isoformat(),
            "total_assessments": len(assessments),
            "title": "Product Feature Readiness Roadmap",
            "description": "Technical readiness assessment roadmap for autonomous vehicle capabilities"
        },
        "timeline": {
            "quarters": generate_quarters(),
            "milestones": []
        },
        "swim_lanes": {},
        "items": []
    }
    
    # Group assessments by technical function (since we don't have direct product feature relationship)
    for assessment in assessments:
        tech_func = assessment.technical_function
        
        # Find product features through capabilities
        product_features = []
        for capability in tech_func.capabilities:
            if capability.product_feature:
                product_features.append(capability.product_feature)
        
        # Use the technical function as the swim lane if no product features found
        if not product_features:
            lane_name = f"Technical Function: {tech_func.name}"
            lane_description = tech_func.description or ""
            lane_doc_url = tech_func.document_url
        else:
            # Use the first product feature as the swim lane
            pf = product_features[0]
            lane_name = pf.name
            lane_description = pf.description or ""
            lane_doc_url = pf.document_url
        
        if lane_name not in roadmap_data["swim_lanes"]:
            roadmap_data["swim_lanes"][lane_name] = {
                "name": lane_name,
                "description": lane_description,
                "vehicle_type": assessment.vehicle_platform.vehicle_type if assessment.vehicle_platform else "truck",
                "document_url": lane_doc_url,
                "items": []
            }
        
        # Create roadmap item
        item = {
            "id": f"assessment_{assessment.id}",
            "title": tech_func.name,
            "description": assessment.notes or f"Assessment for {tech_func.name}",
            "swim_lane": lane_name,
            "product_feature_document_url": product_features[0].document_url if product_features else None,
            "technical_function_document_url": tech_func.document_url,
            "current_trl": assessment.readiness_level.level,
            "current_trl_name": assessment.readiness_level.name,
            "status": assessment.current_status,
            "status_color": get_status_color(assessment.current_status),
            "assessor": assessment.assessor,
            "platform": assessment.vehicle_platform.name,
            "odd": assessment.odd.name,
            "environment": assessment.environment.name,
            "trailer": assessment.trailer.name if assessment.trailer else None,
            "assessment_date": assessment.assessment_date.isoformat(),
            "scheduled_completion": assessment.scheduled_completion_date.isoformat() if assessment.scheduled_completion_date else None,
            "timeline_position": calculate_timeline_position(assessment),
            "miro_properties": {
                "shape": "sticky_note",
                "width": 200,
                "height": 150,
                "text_color": "#000000",
                "background_color": get_status_color(assessment.current_status)
            }
        }
        
        roadmap_data["items"].append(item)
        roadmap_data["swim_lanes"][product_name]["items"].append(item["id"])
    
    # Add milestones based on scheduled completion dates
    milestones = generate_milestones(assessments)
    roadmap_data["timeline"]["milestones"] = milestones
    
    # Return as JSON with proper headers for download
    response = app.response_class(
        response=json.dumps(roadmap_data, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = f'attachment; filename="miro_roadmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    return response

@app.route('/export/miro_csv')
def export_miro_csv():
    """Export assessment data as CSV for Miro import"""
    import csv
    import io
    from datetime import datetime
    
    # Get all assessments with proper joins
    assessments = db.session.query(ReadinessAssessment).join(
        TechnicalFunction
    ).join(TechnicalReadinessLevel).join(
        VehiclePlatform
    ).join(ODD).join(Environment).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV headers for Miro import
    writer.writerow([
        'Title', 'Description', 'Product Feature', 'Current TRL', 'Status', 
        'Status Color', 'Assessor', 'Platform', 'ODD', 'Environment', 
        'Assessment Date', 'Scheduled Completion', 'Timeline Quarter', 'Notes',
        'Product Feature Document URL', 'Technical Function Document URL'
    ])
    
    for assessment in assessments:
        tech_func = assessment.technical_function
        
        # Find product features through capabilities
        product_features = []
        for capability in tech_func.capabilities:
            if capability.product_feature:
                product_features.append(capability.product_feature)
        
        # Use first product feature or technical function name
        product_feature_name = product_features[0].name if product_features else f"Technical Function: {tech_func.name}"
        product_feature_doc_url = product_features[0].document_url if product_features else ""
        
        timeline_pos = calculate_timeline_position(assessment)
        
        # Get product features associated with this technical function
        product_features = [pf.name for pf in assessment.technical_function.capabilities]
        product_feature_name = ", ".join(product_features) if product_features else "No Product Feature"
        
        # Get document URLs
        doc_urls = [pf.document_url for pf in assessment.technical_function.capabilities if pf.document_url]
        doc_url = ", ".join(doc_urls) if doc_urls else ""
        
        writer.writerow([
            assessment.technical_function.name,
            assessment.technical_function.description or assessment.notes or "",
            product_feature_name,
            f"TRL {assessment.readiness_level.level}: {assessment.readiness_level.name}",
            assessment.current_status.upper() if assessment.current_status else "NOT_SET",
            get_status_color(assessment.current_status),
            assessment.assessor or "",
            assessment.vehicle_platform.name,
            assessment.odd.name,
            assessment.environment.name,
            assessment.assessment_date.strftime("%Y-%m-%d"),
            assessment.scheduled_completion_date.strftime("%Y-%m-%d") if assessment.scheduled_completion_date else "",
            f"Q{timeline_pos['quarter']}",
            assessment.notes or "",
            doc_url,
            assessment.technical_function.document_url or ""
        ])
    
    # Create temporary CSV file
    import tempfile
    import os
    
    # Create a temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', prefix='miro_roadmap_')
    
    try:
        # Write CSV content to temporary file
        with os.fdopen(temp_fd, 'w', encoding='utf-8', newline='') as temp_file:
            temp_file.write(output.getvalue())
        
        # Generate filename with timestamp
        filename = f"miro_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Send file as download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    except Exception as e:
        # Clean up temp file if error occurs
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e

@app.route('/timeline/product_features')
def product_features_timeline():
    """Timeline view for Product Features with start and end dates"""
    from datetime import datetime, timedelta
    
    # Get all product features with dates
    features = ProductFeature.query.filter(
        (ProductFeature.planned_start_date.isnot(None)) | 
        (ProductFeature.planned_end_date.isnot(None))
    ).order_by(ProductFeature.planned_start_date).all()
    
    # Calculate timeline range
    all_dates = []
    for feature in features:
        if feature.planned_start_date:
            all_dates.append(feature.planned_start_date)
        if feature.planned_end_date:
            all_dates.append(feature.planned_end_date)
    
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        # Add buffer to timeline
        timeline_start = min_date - timedelta(days=30)
        timeline_end = max_date + timedelta(days=30)
    else:
        # Default timeline if no dates
        today = datetime.now().date()
        timeline_start = today
        timeline_end = today + timedelta(days=365)
    
    # Prepare timeline data
    timeline_data = []
    for feature in features:
        item = {
            'id': feature.id,
            'name': feature.name,
            'description': feature.description,
            'vehicle_type': feature.vehicle_platform.vehicle_type if feature.vehicle_platform else 'Not specified',
            'swimlane_decorators': feature.swimlane_decorators,
            'status_relative_to_tmos': feature.status_relative_to_tmos,
            'planned_start_date': feature.planned_start_date.isoformat() if feature.planned_start_date else None,
            'planned_end_date': feature.planned_end_date.isoformat() if feature.planned_end_date else None,
            'active_flag': feature.active_flag,
            'document_url': feature.document_url,
            'duration_days': None,
            'progress_color': 'success' if feature.status_relative_to_tmos >= 80 else 'warning' if feature.status_relative_to_tmos >= 50 else 'danger'
        }
        
        # Calculate duration if both dates exist
        if feature.planned_start_date and feature.planned_end_date:
            duration = feature.planned_end_date - feature.planned_start_date
            item['duration_days'] = duration.days
        
        timeline_data.append(item)
    
    return render_template('timeline_product_features.html',
                         timeline_data=timeline_data,
                         timeline_start=timeline_start.isoformat(),
                         timeline_end=timeline_end.isoformat(),
                         page_title="Product Features Timeline")

@app.route('/timeline/capabilities')
def capabilities_timeline():
    """Timeline view for Capabilities with start and end dates"""
    from datetime import datetime, timedelta
    from app import Capabilities
    
    # Get all capabilities with dates
    capabilities = Capabilities.query.filter(
        (Capabilities.planned_start_date.isnot(None)) | 
        (Capabilities.planned_end_date.isnot(None))
    ).order_by(Capabilities.planned_start_date).all()
    
    # Calculate timeline range
    all_dates = []
    for capability in capabilities:
        if capability.planned_start_date:
            all_dates.append(capability.planned_start_date)
        if capability.planned_end_date:
            all_dates.append(capability.planned_end_date)
    
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        # Add buffer to timeline
        timeline_start = min_date - timedelta(days=30)
        timeline_end = max_date + timedelta(days=30)
    else:
        # Default timeline if no dates
        today = datetime.now().date()
        timeline_start = today
        timeline_end = today + timedelta(days=365)
    
    # Prepare timeline data
    timeline_data = []
    for capability in capabilities:
        item = {
            'id': capability.id,
            'name': capability.name,
            'success_criteria': capability.success_criteria,
            'vehicle_type': capability.vehicle_platform.vehicle_type if capability.vehicle_platform else 'Not specified',
            'tmos': capability.tmos,
            'progress_relative_to_tmos': capability.progress_relative_to_tmos,
            'planned_start_date': capability.planned_start_date.isoformat() if capability.planned_start_date else None,
            'planned_end_date': capability.planned_end_date.isoformat() if capability.planned_end_date else None,
            'document_url': capability.document_url,
            'duration_days': None,
            'progress_color': 'success' if capability.progress_relative_to_tmos >= 80 else 'warning' if capability.progress_relative_to_tmos >= 50 else 'danger',
            'technical_functions_count': len(capability.technical_functions),
            'product_features_count': 1 if capability.product_feature else 0
        }
        
        # Calculate duration if both dates exist
        if capability.planned_start_date and capability.planned_end_date:
            duration = capability.planned_end_date - capability.planned_start_date
            item['duration_days'] = duration.days
        
        timeline_data.append(item)
    
    return render_template('timeline_capabilities.html',
                         timeline_data=timeline_data,
                         timeline_start=timeline_start.isoformat(),
                         timeline_end=timeline_end.isoformat(),
                         page_title="Capabilities Timeline")

@app.route('/timeline/technical_functions')
def technical_functions_timeline():
    """Timeline view for Technical Functions with start and end dates"""
    from datetime import datetime, timedelta
    
    # Get all technical functions with dates
    tech_functions = TechnicalFunction.query.filter(
        (TechnicalFunction.planned_start_date.isnot(None)) | 
        (TechnicalFunction.planned_end_date.isnot(None))
    ).order_by(TechnicalFunction.planned_start_date).all()
    
    # Calculate timeline range
    all_dates = []
    for func in tech_functions:
        if func.planned_start_date:
            all_dates.append(func.planned_start_date)
        if func.planned_end_date:
            all_dates.append(func.planned_end_date)
    
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        # Add buffer to timeline
        timeline_start = min_date - timedelta(days=30)
        timeline_end = max_date + timedelta(days=30)
    else:
        # Default timeline if no dates
        today = datetime.now().date()
        timeline_start = today
        timeline_end = today + timedelta(days=365)
    
    # Prepare timeline data
    timeline_data = []
    for func in tech_functions:
        # Get latest readiness assessment for this function
        latest_assessment = ReadinessAssessment.query.filter_by(
            technical_capability_id=func.id
        ).order_by(ReadinessAssessment.assessment_date.desc()).first()
        
        item = {
            'id': func.id,
            'name': func.name,
            'description': func.description,
            'success_criteria': func.success_criteria,
            'vehicle_type': func.vehicle_platform.vehicle_type if func.vehicle_platform else 'Not specified',
            'tmos': func.tmos,
            'status_relative_to_tmos': func.status_relative_to_tmos,
            'planned_start_date': func.planned_start_date.isoformat() if func.planned_start_date else None,
            'planned_end_date': func.planned_end_date.isoformat() if func.planned_end_date else None,
            'document_url': func.document_url,
            'product_feature_name': func.capabilities[0].product_feature.name if func.capabilities and func.capabilities[0].product_feature else 'No Product Feature',
            'product_feature_id': func.capabilities[0].product_feature.id if func.capabilities and func.capabilities[0].product_feature else None,
            'duration_days': None,
            'progress_color': 'success' if func.status_relative_to_tmos >= 80 else 'warning' if func.status_relative_to_tmos >= 50 else 'danger',
            'current_trl': None,
            'current_status': None,
            'assessments_count': len(func.readiness_assessments)
        }
        
        # Add latest assessment info if available
        if latest_assessment:
            item['current_trl'] = latest_assessment.readiness_level.level
            item['current_status'] = latest_assessment.current_status
        
        # Calculate duration if both dates exist
        if func.planned_start_date and func.planned_end_date:
            duration = func.planned_end_date - func.planned_start_date
            item['duration_days'] = duration.days
        
        timeline_data.append(item)
    
    return render_template('timeline_technical_functions.html',
                         timeline_data=timeline_data,
                         timeline_start=timeline_start.isoformat(),
                         timeline_end=timeline_end.isoformat(),
                         page_title="Technical Functions Timeline")


# Configuration Management Routes

@app.route('/config/add/<config_type>', methods=['POST'])
def add_config_item(config_type):
    """Add new configuration item"""
    try:
        data = request.form.to_dict()
        
        if config_type == 'vehicle_platform':
            # Convert max_payload to float if provided
            if data.get('max_payload'):
                data['max_payload'] = float(data['max_payload'])
            
            new_item = VehiclePlatform(
                name=data['name'],
                description=data.get('description', ''),
                vehicle_type=data.get('vehicle_type', ''),
                max_payload=data.get('max_payload')
            )
            
        elif config_type == 'odd':
            # Convert max_speed to int if provided
            if data.get('max_speed'):
                data['max_speed'] = int(data['max_speed'])
            
            new_item = ODD(
                name=data['name'],
                description=data.get('description', ''),
                max_speed=data.get('max_speed'),
                direction=data.get('direction', ''),
                lanes=data.get('lanes', ''),
                intersections=data.get('intersections', ''),
                traction=data.get('traction', '')
            )
            
        elif config_type == 'environment':
            new_item = Environment(
                name=data['name'],
                description=data.get('description', ''),
                region=data.get('region', ''),
                climate=data.get('climate', ''),
                terrain=data.get('terrain', '')
            )
            
        elif config_type == 'trailer':
            # Convert numeric fields if provided
            if data.get('length'):
                data['length'] = float(data['length'])
            if data.get('max_weight'):
                data['max_weight'] = float(data['max_weight'])
            if data.get('axle_count'):
                data['axle_count'] = int(data['axle_count'])
            
            new_item = Trailer(
                name=data['name'],
                description=data.get('description', ''),
                trailer_type=data.get('trailer_type', ''),
                length=data.get('length'),
                max_weight=data.get('max_weight'),
                axle_count=data.get('axle_count')
            )
            
        else:
            return jsonify({'success': False, 'error': 'Invalid configuration type'}), 400
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{config_type.title()} added successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/config/delete/<config_type>/<int:item_id>', methods=['DELETE'])
def delete_config_item(config_type, item_id):
    """Delete configuration item"""
    try:
        if config_type == 'vehicle_platform':
            item = VehiclePlatform.query.get_or_404(item_id)
        elif config_type == 'odd':
            item = ODD.query.get_or_404(item_id)
        elif config_type == 'environment':
            item = Environment.query.get_or_404(item_id)
        elif config_type == 'trailer':
            item = Trailer.query.get_or_404(item_id)
        else:
            return jsonify({'success': False, 'error': 'Invalid configuration type'}), 400
        
        # Check if item is being used in any assessments
        if hasattr(item, 'readiness_assessments') and item.readiness_assessments:
            return jsonify({
                'success': False, 
                'error': f'Cannot delete {item.name} - it is being used in readiness assessments'
            }), 400
        
        # Check if vehicle platform is being used by product features, capabilities, or technical functions
        if config_type == 'vehicle_platform':
            if item.product_features or item.capabilities or item.technical_functions:
                return jsonify({
                    'success': False,
                    'error': f'Cannot delete {item.name} - it is being used by other entities'
                }), 400
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{config_type.title()} deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500