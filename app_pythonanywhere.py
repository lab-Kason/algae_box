"""
Flask REST API Server for Algae Box System - PythonAnywhere Version
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

        result = {
            'id': tank.id,
            'name': tank.name,
            'algae_type': tank.algae_type,
            'volume_liters': tank.volume_liters,
            'status': tank.status,
            'created_at': tank.created_at.isoformat(),
            'notes': tank.notes
        }
        return jsonify({'success': True, 'tank': result})
    finally:
        session.close()


@app.route('/api/tanks', methods=['POST'])
def create_tank():
    """Create new tank"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    required_fields = ['name', 'algae_type', 'volume_liters']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    session = db.get_session()
    try:
        # Check if species exists
        species = session.query(AlgaeSpecies).filter_by(name=data['algae_type']).first()
        if not species:
            return jsonify({'success': False, 'error': f'Unknown algae species: {data["algae_type"]}'}), 400

        tank = Tank(
            name=data['name'],
            algae_type=data['algae_type'],
            volume_liters=data['volume_liters'],
            status='active',
            notes=data.get('notes', '')
        )
        session.add(tank)
        session.commit()

        result = {
            'id': tank.id,
            'name': tank.name,
            'algae_type': tank.algae_type,
            'volume_liters': tank.volume_liters,
            'status': tank.status,
            'created_at': tank.created_at.isoformat(),
            'notes': tank.notes
        }
        return jsonify({'success': True, 'tank': result}), 201
    finally:
        session.close()


@app.route('/api/tanks/<int:tank_id>', methods=['DELETE'])
def delete_tank(tank_id):
    """Delete tank and all associated data"""
    session = db.get_session()
    try:
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404

        # Delete associated data (cascade delete should handle this, but explicit is safer)
        session.query(SensorReading).filter_by(tank_id=tank_id).delete()
        session.query(CollectionEvent).filter_by(tank_id=tank_id).delete()
        session.query(UserAction).filter_by(tank_id=tank_id).delete()

        session.delete(tank)
        session.commit()

        return jsonify({'success': True, 'message': f'Tank {tank_id} deleted successfully'})
    finally:
        session.close()


# ==================== SENSOR ENDPOINTS ====================

@app.route('/api/sensors/current/<int:tank_id>', methods=['GET'])
def get_current_sensors(tank_id):
    """Get latest sensor readings for tank"""
    session = db.get_session()
    try:
        # Get latest reading
        reading = session.query(SensorReading).filter_by(tank_id=tank_id)\
                     .order_by(desc(SensorReading.timestamp)).first()

        if not reading:
            return jsonify({'success': False, 'error': 'No sensor data found'}), 404

        # Get tank and species for optimal ranges
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404

        species = session.query(AlgaeSpecies).filter_by(name=tank.algae_type).first()
        if not species:
            # Default safe ranges if species not found
            ph_safe = 7.0 <= reading.ph <= 9.0
            temp_safe = 20.0 <= reading.temperature_c <= 30.0
            harvest_ready = reading.turbidity_ntu >= 300
        else:
            ph_safe = species.ph_min <= reading.ph <= species.ph_max
            temp_safe = species.temp_min_c <= reading.temperature_c <= species.temp_max_c
            harvest_ready = reading.turbidity_ntu >= species.harvest_turbidity_ntu

        result = {
            'timestamp': reading.timestamp.isoformat(),
            'ph': reading.ph,
            'temperature_c': reading.temperature_c,
            'turbidity_ntu': reading.turbidity_ntu,
            'ph_safe': ph_safe,
            'temperature_safe': temp_safe,
            'harvest_ready': harvest_ready
        }
        return jsonify({'success': True, 'reading': result})
    finally:
        session.close()


@app.route('/api/sensors/reading', methods=['POST'])
def post_sensor_reading():
    """Receive sensor data from ESP32"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    required_fields = ['tank_id', 'turbidity', 'ph', 'temperature']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    session = db.get_session()
    try:
        # Check if tank exists
        tank = session.query(Tank).filter_by(id=data['tank_id']).first()
        if not tank:
            return jsonify({'success': False, 'error': f'Tank {data["tank_id"]} not found'}), 404

        reading = SensorReading(
            tank_id=data['tank_id'],
            turbidity_ntu=data['turbidity'],
            ph=data['ph'],
            temperature_c=data['temperature']
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

@app.route('/api/collection/start/<int:tank_id>', methods=['POST'])
def start_collection(tank_id):
    """Start algae collection process"""
    session = db.get_session()
    try:
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404

        # Get latest sensor reading for turbidity
        reading = session.query(SensorReading).filter_by(tank_id=tank_id)\
                     .order_by(desc(SensorReading.timestamp)).first()

        if not reading:
            return jsonify({'success': False, 'error': 'No sensor data available'}), 400

        # Create collection event
        event = CollectionEvent(
            tank_id=tank_id,
            turbidity_before=reading.turbidity_ntu,
            estimated_yield_grams=reading.turbidity_ntu * tank.volume_liters * 0.1  # Rough estimate
        )
        session.add(event)
        session.commit()

        return jsonify({
            'success': True,
            'event_id': event.id,
            'message': f'Collection started for tank {tank_id}',
            'estimated_yield': event.estimated_yield_grams
        })
    finally:
        session.close()


# ==================== SPECIES ENDPOINTS ====================

@app.route('/api/species', methods=['GET'])
def get_species():
    """Get all available algae species"""
    session = db.get_session()
    try:
        species = session.query(AlgaeSpecies).all()
        result = [{
            'id': s.id,
            'name': s.name,
            'scientific_name': s.scientific_name,
            'ph_range': f"{s.ph_min}-{s.ph_max}",
            'ph_optimal': s.ph_optimal,
            'temp_range': f"{s.temp_min_c}-{s.temp_max_c}",
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


# ==================== RECOMMENDATIONS ====================

@app.route('/api/recommendations/<int:tank_id>', methods=['GET'])
def get_recommendations(tank_id):
    """Get maintenance recommendations for tank"""
    session = db.get_session()
    try:
        # Get tank and latest sensor data
        tank = session.query(Tank).filter_by(id=tank_id).first()
        if not tank:
            return jsonify({'success': False, 'error': 'Tank not found'}), 404

        reading = session.query(SensorReading).filter_by(tank_id=tank_id)\
                     .order_by(desc(SensorReading.timestamp)).first()

        if not reading:
            return jsonify({'success': False, 'error': 'No sensor data available'}), 404

        # Get species optimal values
        species = session.query(AlgaeSpecies).filter_by(name=tank.algae_type).first()
        if not species:
            return jsonify({'success': False, 'error': 'Species data not found'}), 404

        # Generate recommendations
        recommendations = []

        # pH check
        if reading.ph_level < species.ph_optimal - 0.5:
            recommendations.append({
                'type': 'warning',
                'message': f'pH too low ({reading.ph_level:.2f}). Target: {species.ph_optimal:.1f}',
                'action': 'Add CO2 or increase aeration'
            })
        elif reading.ph_level > species.ph_optimal + 0.5:
            recommendations.append({
                'type': 'warning',
                'message': f'pH too high ({reading.ph_level:.2f}). Target: {species.ph_optimal:.1f}',
                'action': 'Add acid or reduce CO2'
            })
        else:
            recommendations.append({
                'type': 'good',
                'message': f'pH optimal ({reading.ph_level:.2f})',
                'action': 'Keep current conditions'
            })

        # Temperature check
        if reading.temperature_c < species.temp_optimal_c - 2:
            recommendations.append({
                'type': 'warning',
                'message': f'Temperature too low ({reading.temperature_c:.1f}°C). Target: {species.temp_optimal_c:.1f}°C',
                'action': 'Increase heating'
            })
        elif reading.temperature_c > species.temp_optimal_c + 2:
            recommendations.append({
                'type': 'warning',
                'message': f'Temperature too high ({reading.temperature_c:.1f}°C). Target: {species.temp_optimal_c:.1f}°C',
                'action': 'Add cooling or reduce light'
            })
        else:
            recommendations.append({
                'type': 'good',
                'message': f'Temperature optimal ({reading.temperature_c:.1f}°C)',
                'action': 'Maintain current temperature'
            })

        # Turbidity check
        if reading.turbidity_ntu > species.turbidity_harvest_ntu:
            recommendations.append({
                'type': 'action',
                'message': f'Ready for harvest! Turbidity: {reading.turbidity_ntu:.1f} NTU (Target: {species.turbidity_harvest_ntu:.1f})',
                'action': 'Start collection process'
            })
        elif reading.turbidity_ntu > species.turbidity_harvest_ntu * 0.8:
            recommendations.append({
                'type': 'info',
                'message': f'Approaching harvest turbidity ({reading.turbidity_ntu:.1f}/{species.turbidity_harvest_ntu:.1f} NTU)',
                'action': 'Monitor closely'
            })
        else:
            recommendations.append({
                'type': 'info',
                'message': f'Growing well ({reading.turbidity_ntu:.1f} NTU)',
                'action': 'Continue normal operation'
            })

        return jsonify({
            'success': True,
            'tank_id': tank_id,
            'species': tank.algae_type,
            'recommendations': recommendations,
            'last_reading': {
                'turbidity': reading.turbidity_ntu,
                'ph': reading.ph_level,
                'temperature': reading.temperature_c,
                'timestamp': reading.timestamp.isoformat()
            }
        })
    finally:
        session.close()


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'name': 'Algae Box API',
        'version': '1.0.0',
        'description': 'REST API for algae cultivation monitoring system',
        'endpoints': {
            'tanks': '/api/tanks',
            'sensors': '/api/sensors/current/<tank_id>',
            'collection': '/api/collection/start/<tank_id>',
            'species': '/api/species',
            'recommendations': '/api/recommendations/<tank_id>',
            'health': '/api/health'
        }
    })


# For PythonAnywhere WSGI - no debug/run configuration needed
# The WSGI server handles the app object directly