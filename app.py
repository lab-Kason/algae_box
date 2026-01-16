"""
Flask REST API Server for Algae Box System
Provides endpoints for mobile app to interact with sensors and database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from database import db, Tank, SensorReading, CollectionEvent, AlgaeSpecies, UserAction
from sqlalchemy import desc
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app access

# Initialize database
db.init_db()


# ==================== TANK ENDPOINTS ====================

@app.route('/api/tanks', methods=['GET'])
def get_tanks():
    """Get all tanks"""
    session = db.get_session()
    try:
        tanks = session.query(Tank).all()
        result = [{
            'id': t.id,
            'name': t.name,
            'algae_type': t.algae_type,
            'volume_liters': t.volume_liters,
            'status': t.status,
            'created_at': t.created_at.isoformat(),
            'notes': t.notes
        } for t in tanks]
        return jsonify({'success': True, 'tanks': result})
    finally:
        session.close()


@app.route('/api/tanks/<int:tank_id>', methods=['GET'])
def get_tank(tank_id):
    """Get specific tank details"""
    session = db.get_session()
    try:
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404
        
        # Get algae species info
        species = session.query(AlgaeSpecies).filter_by(name=tank.algae_type).first()
        
        return jsonify({
            'success': True,
            'tank': {
                'id': tank.id,
                'name': tank.name,
                'algae_type': tank.algae_type,
                'volume_liters': tank.volume_liters,
                'status': tank.status,
                'created_at': tank.created_at.isoformat(),
                'notes': tank.notes,
                'species_info': {
                    'ph_range': f"{species.ph_min}-{species.ph_max}",
                    'temp_range': f"{species.temp_min_c}-{species.temp_max_c}°C",
                    'harvest_turbidity': species.harvest_turbidity_ntu,
                    'description': species.description
                } if species else None
            }
        })
    finally:
        session.close()


@app.route('/api/tanks', methods=['POST'])
def create_tank():
    """Create new tank"""
    data = request.json
    session = db.get_session()
    
    try:
        # Validate algae type exists
        species = session.query(AlgaeSpecies).filter_by(name=data['algae_type']).first()
        if not species:
            return jsonify({'success': False, 'error': 'Invalid algae type'}), 400
        
        tank = Tank(
            name=data['name'],
            algae_type=data['algae_type'],
            volume_liters=data['volume_liters'],
            notes=data.get('notes', '')
        )
        session.add(tank)
        session.commit()
        
        return jsonify({
            'success': True,
            'tank_id': tank.id,
            'message': f"Tank '{tank.name}' created successfully"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/tanks/<int:tank_id>', methods=['PUT'])
def update_tank(tank_id):
    """Update tank information"""
    data = request.json
    session = db.get_session()
    
    try:
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404
        
        # Update fields
        if 'name' in data:
            tank.name = data['name']
        if 'status' in data:
            tank.status = data['status']
        if 'notes' in data:
            tank.notes = data['notes']
        
        session.commit()
        return jsonify({'success': True, 'message': 'Tank updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ==================== SENSOR ENDPOINTS ====================

@app.route('/api/sensors/current/<int:tank_id>', methods=['GET'])
def get_current_sensors(tank_id):
    """Get most recent sensor readings for a tank"""
    session = db.get_session()
    try:
        # Get latest reading
        reading = session.query(SensorReading)\
            .filter_by(tank_id=tank_id)\
            .order_by(desc(SensorReading.timestamp))\
            .first()
        
        if not reading:
            return jsonify({'success': False, 'error': 'No sensor data available'}), 404
        
        return jsonify({
            'success': True,
            'reading': {
                'timestamp': reading.timestamp.isoformat(),
                'ph': reading.ph,
                'temperature_c': reading.temperature_c,
                'turbidity_ntu': reading.turbidity_ntu,
                'ph_safe': reading.ph_safe,
                'temperature_safe': reading.temperature_safe,
                'harvest_ready': reading.harvest_ready
            }
        })
    finally:
        session.close()


@app.route('/api/sensors/history/<int:tank_id>', methods=['GET'])
def get_sensor_history(tank_id):
    """Get historical sensor readings"""
    hours = request.args.get('hours', 24, type=int)
    session = db.get_session()
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        readings = session.query(SensorReading)\
            .filter(SensorReading.tank_id == tank_id)\
            .filter(SensorReading.timestamp >= cutoff_time)\
            .order_by(SensorReading.timestamp)\
            .all()
        
        result = [{
            'timestamp': r.timestamp.isoformat(),
            'ph': r.ph,
            'temperature_c': r.temperature_c,
            'turbidity_ntu': r.turbidity_ntu
        } for r in readings]
        
        return jsonify({'success': True, 'readings': result, 'count': len(result)})
    finally:
        session.close()


@app.route('/api/sensors/reading', methods=['POST'])
def add_sensor_reading():
    """Add new sensor reading (called by Pi sensor loop)"""
    data = request.json
    session = db.get_session()
    
    try:
        reading = SensorReading(
            tank_id=data['tank_id'],
            ph=data['ph'],
            temperature_c=data['temperature_c'],
            turbidity_ntu=data['turbidity_ntu'],
            ph_safe=data['ph_safe'],
            temperature_safe=data['temperature_safe'],
            harvest_ready=data['harvest_ready']
        )
        session.add(reading)
        session.commit()
        
        return jsonify({'success': True, 'reading_id': reading.id})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ==================== COLLECTION ENDPOINTS ====================

@app.route('/api/collection/history/<int:tank_id>', methods=['GET'])
def get_collection_history(tank_id):
    """Get collection event history"""
    session = db.get_session()
    try:
        events = session.query(CollectionEvent)\
            .filter_by(tank_id=tank_id)\
            .order_by(desc(CollectionEvent.timestamp))\
            .limit(50)\
            .all()
        
        result = [{
            'timestamp': e.timestamp.isoformat(),
            'success': e.success,
            'duration_seconds': e.duration_seconds,
            'turbidity_before': e.turbidity_before,
            'turbidity_after': e.turbidity_after,
            'estimated_amount_ml': e.estimated_amount_ml,
            'notes': e.notes
        } for e in events]
        
        return jsonify({'success': True, 'events': result})
    finally:
        session.close()


@app.route('/api/collection/start/<int:tank_id>', methods=['POST'])
def start_collection(tank_id):
    """Trigger algae collection (called from mobile app)"""
    session = db.get_session()
    
    try:
        # Get current turbidity
        latest = session.query(SensorReading)\
            .filter_by(tank_id=tank_id)\
            .order_by(desc(SensorReading.timestamp))\
            .first()
        
        if not latest:
            return jsonify({'success': False, 'error': 'No sensor data available'}), 400
        
        # TODO: Trigger actual collection hardware via GPIO
        # For now, simulate collection
        
        event = CollectionEvent(
            tank_id=tank_id,
            turbidity_before=latest.turbidity_ntu,
            turbidity_after=latest.turbidity_ntu * 0.3,  # Simulated reduction
            duration_seconds=300,  # 5 minutes
            success=True,
            estimated_amount_ml=100,
            notes='Manual collection triggered from mobile app'
        )
        session.add(event)
        session.commit()
        
        return jsonify({
            'success': True,
            'event_id': event.id,
            'message': 'Collection started successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


# ==================== ALGAE SPECIES ENDPOINTS ====================

@app.route('/api/species', methods=['GET'])
def get_algae_species():
    """Get all available algae species"""
    session = db.get_session()
    try:
        species = session.query(AlgaeSpecies).all()
        result = [{
            'name': s.name,
            'scientific_name': s.scientific_name,
            'ph_range': f"{s.ph_min}-{s.ph_max}",
            'ph_optimal': s.ph_optimal,
            'temp_range': f"{s.temp_min_c}-{s.temp_max_c}°C",
            'temp_optimal': s.temp_optimal_c,
            'harvest_turbidity': s.harvest_turbidity_ntu,
            'growth_days': s.growth_rate_days,
            'description': s.description,
            'uses': s.uses,
            'difficulty': s.difficulty
        } for s in species]
        
        return jsonify({'success': True, 'species': result})
    finally:
        session.close()


# ==================== RECOMMENDATIONS ENDPOINT ====================

@app.route('/api/recommendations/<int:tank_id>', methods=['GET'])
def get_recommendations(tank_id):
    """Get current recommendations for tank"""
    session = db.get_session()
    
    try:
        # Get tank and species info
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404
        
        species = session.query(AlgaeSpecies).filter_by(name=tank.algae_type).first()
        
        # Get latest reading
        reading = session.query(SensorReading)\
            .filter_by(tank_id=tank_id)\
            .order_by(desc(SensorReading.timestamp))\
            .first()
        
        if not reading:
            return jsonify({'success': False, 'error': 'No sensor data'}), 404
        
        recommendations = []
        
        # pH recommendations
        if reading.ph < species.ph_min:
            diff = species.ph_min - reading.ph
            recommendations.append({
                'priority': 'high',
                'category': 'pH',
                'issue': f'pH too low ({reading.ph:.2f})',
                'action': f'Add sodium bicarbonate (baking soda) to raise pH',
                'target': f'Target: {species.ph_optimal}',
                'severity': 'critical' if diff > 1.0 else 'warning'
            })
        elif reading.ph > species.ph_max:
            diff = reading.ph - species.ph_max
            recommendations.append({
                'priority': 'high',
                'category': 'pH',
                'issue': f'pH too high ({reading.ph:.2f})',
                'action': f'Add citric acid or vinegar to lower pH',
                'target': f'Target: {species.ph_optimal}',
                'severity': 'critical' if diff > 1.0 else 'warning'
            })
        
        # Temperature recommendations
        if reading.temperature_c < species.temp_min_c:
            recommendations.append({
                'priority': 'medium',
                'category': 'temperature',
                'issue': f'Temperature too low ({reading.temperature_c:.1f}°C)',
                'action': 'Increase water temperature or add heater',
                'target': f'Target: {species.temp_optimal_c}°C',
                'severity': 'warning'
            })
        elif reading.temperature_c > species.temp_max_c:
            recommendations.append({
                'priority': 'medium',
                'category': 'temperature',
                'issue': f'Temperature too high ({reading.temperature_c:.1f}°C)',
                'action': 'Reduce temperature or add cooling',
                'target': f'Target: {species.temp_optimal_c}°C',
                'severity': 'warning'
            })
        
        # Harvest recommendations
        if reading.harvest_ready:
            recommendations.append({
                'priority': 'high',
                'category': 'harvest',
                'issue': f'Harvest threshold reached ({reading.turbidity_ntu:.1f} NTU)',
                'action': 'Start collection process immediately',
                'target': f'Threshold: {species.harvest_turbidity_ntu} NTU',
                'severity': 'action_required'
            })
        
        # Optimal conditions message
        if not recommendations:
            recommendations.append({
                'priority': 'info',
                'category': 'status',
                'issue': 'All parameters optimal',
                'action': 'Continue normal monitoring',
                'target': 'System running well',
                'severity': 'ok'
            })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'current_status': {
                'ph': reading.ph,
                'temperature': reading.temperature_c,
                'turbidity': reading.turbidity_ntu,
                'timestamp': reading.timestamp.isoformat()
            }
        })
    finally:
        session.close()


# ==================== USER ACTIONS ENDPOINT ====================

@app.route('/api/actions/<int:tank_id>', methods=['POST'])
def log_user_action(tank_id):
    """Log user action (e.g., added nutrients, adjusted pH)"""
    data = request.json
    session = db.get_session()
    
    try:
        action = UserAction(
            tank_id=tank_id,
            action_type=data['action_type'],
            description=data.get('description', ''),
            notes=data.get('notes', '')
        )
        session.add(action)
        session.commit()
        
        return jsonify({'success': True, 'action_id': action.id})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/actions/history/<int:tank_id>', methods=['GET'])
def get_action_history(tank_id):
    """Get user action history"""
    session = db.get_session()
    try:
        actions = session.query(UserAction)\
            .filter_by(tank_id=tank_id)\
            .order_by(desc(UserAction.timestamp))\
            .limit(50)\
            .all()
        
        result = [{
            'timestamp': a.timestamp.isoformat(),
            'action_type': a.action_type,
            'description': a.description,
            'notes': a.notes
        } for a in actions]
        
        return jsonify({'success': True, 'actions': result})
    finally:
        session.close()


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'success': True,
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'Algae Box API',
        'version': '1.0.0',
        'endpoints': {
            'tanks': '/api/tanks',
            'sensors': '/api/sensors/current/<tank_id>',
            'collection': '/api/collection/start/<tank_id>',
            'species': '/api/species',
            'recommendations': '/api/recommendations/<tank_id>',
            'health': '/api/health'
        }
    })


if __name__ == '__main__':
    print("🌱 Starting Algae Box API Server...")
    print("📡 API will be available at: http://localhost:5001")
    print("📚 API docs at: http://localhost:5001/")
    app.run(host='0.0.0.0', port=5001, debug=True)
