from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db, ProductFeature, TechnicalFunction, TechnicalReadinessLevel, VehiclePlatform, ODD, Environment, Trailer, ReadinessAssessment
from sqlalchemy import and_

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
    """View all product features"""
    features = ProductFeature.query.all()
    return render_template('product_features.html', features=features)

@app.route('/technical_capabilities')
def technical_capabilities():
    """Technical functions management page"""
    capabilities = TechnicalFunction.query.all()
    return render_template('technical_functions.html', capabilities=capabilities)

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
                         technical_capabilities=technical_capabilities,
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
                            'confidence': assessment.confidence_level,
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
        assessment = ReadinessAssessment(
            technical_capability_id=request.form['technical_capability_id'],
            readiness_level_id=request.form['readiness_level_id'],
            vehicle_platform_id=request.form['vehicle_platform_id'],
            odd_id=request.form['odd_id'],
            environment_id=request.form['environment_id'],
            trailer_id=request.form.get('trailer_id') or None,
            assessor=request.form['assessor'],
            notes=request.form['notes'],
            confidence_level=request.form['confidence_level']
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
                         technical_capabilities=technical_functions,
                         readiness_levels=readiness_levels,
                         vehicle_platforms=vehicle_platforms,
                         odds=odds,
                         environments=environments,
                         trailers=trailers)

@app.route('/api/readiness_data')
def api_readiness_data():
    """API endpoint for readiness data (for charts/graphs)"""
    # Get readiness distribution by TRL level
    trl_distribution = db.session.query(
        TechnicalReadinessLevel.level,
        TechnicalReadinessLevel.name,
        db.func.count(ReadinessAssessment.id).label('count')
    ).join(ReadinessAssessment).group_by(TechnicalReadinessLevel.level).all()
    
    # Get readiness by product feature
    product_readiness = db.session.query(
        ProductFeature.name,
        db.func.avg(TechnicalReadinessLevel.level).label('avg_trl')
    ).join(TechnicalFunction).join(ReadinessAssessment).join(TechnicalReadinessLevel).group_by(ProductFeature.name).all()
    
    return jsonify({
        'trl_distribution': [{'level': t.level, 'name': t.name, 'count': t.count} for t in trl_distribution],
        'product_readiness': [{'name': p.name, 'avg_trl': float(p.avg_trl)} for p in product_readiness]
    })