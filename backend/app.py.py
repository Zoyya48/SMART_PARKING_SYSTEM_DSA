"""
app.py - Flask REST API for Smart Parking System
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from ParkingSystem import ParkingSystem
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize parking system
parking_system = ParkingSystem()

# Initialize with sample data
def initialize_system():
    """Initialize system with zones and parking areas"""
    # Add zones
    parking_system.add_zone('ZONE_A', 'Downtown', ['ZONE_B'])
    parking_system.add_zone('ZONE_B', 'Uptown', ['ZONE_A', 'ZONE_C'])
    parking_system.add_zone('ZONE_C', 'Suburbs', ['ZONE_B'])
    parking_system.add_zone('ZONE_D', 'Industrial', [])
    
    # Add parking areas
    parking_system.add_parking_area('ZONE_A', 'AREA_A1', 'Downtown Plaza', 10)
    parking_system.add_parking_area('ZONE_A', 'AREA_A2', 'Main Street', 8)
    
    parking_system.add_parking_area('ZONE_B', 'AREA_B1', 'Uptown Mall', 12)
    parking_system.add_parking_area('ZONE_B', 'AREA_B2', 'Business District', 15)
    
    parking_system.add_parking_area('ZONE_C', 'AREA_C1', 'Suburb Center', 20)
    
    parking_system.add_parking_area('ZONE_D', 'AREA_D1', 'Industrial Park', 25)
    
    print("✓ System initialized with 4 zones and 6 parking areas")

# Initialize on startup
initialize_system()


# ==========================================
# SYSTEM ENDPOINTS
# ==========================================

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    status = parking_system.get_system_status()
    return jsonify(status)

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """Reset the entire system"""
    global parking_system
    parking_system = ParkingSystem()
    initialize_system()
    return jsonify({'success': True, 'message': 'System reset successfully'})


# ==========================================
# ZONE ENDPOINTS
# ==========================================

@app.route('/api/zones', methods=['GET'])
def get_all_zones():
    """Get all zones"""
    zones = []
    for zone in parking_system.get_all_zones():
        zones.append(zone.to_dict())
    return jsonify({'zones': zones})

@app.route('/api/zones/<zone_id>', methods=['GET'])
def get_zone(zone_id):
    """Get specific zone"""
    zone = parking_system.get_zone(zone_id)
    if zone:
        return jsonify(zone.to_dict())
    return jsonify({'error': 'Zone not found'}), 404


# ==========================================
# VEHICLE ENDPOINTS
# ==========================================

@app.route('/api/vehicle/register', methods=['POST'])
def register_vehicle():
    """Register a new vehicle"""
    data = request.json
    vehicle_id = data.get('vehicle_id')
    preferred_zone = data.get('preferred_zone')
    vehicle_type = data.get('vehicle_type', 'Car')
    
    vehicle = parking_system.register_vehicle(vehicle_id, preferred_zone, vehicle_type)
    if vehicle:
        return jsonify({'success': True, 'vehicle': vehicle.to_dict()})
    return jsonify({'success': False, 'error': 'Vehicle already registered'}), 400


# ==========================================
# REQUEST ENDPOINTS
# ==========================================

@app.route('/api/request/create', methods=['POST'])
def create_request():
    """Create a parking request"""
    data = request.json
    vehicle_id = data.get('vehicle_id')
    requested_zone = data.get('requested_zone')
    auto_allocate = data.get('auto_allocate', True)
    
    req = parking_system.create_request(vehicle_id, requested_zone, auto_allocate)
    return jsonify({'success': True, 'request': req.to_dict()})

@app.route('/api/request/<request_id>/allocate', methods=['POST'])
def allocate_parking(request_id):
    """Allocate parking for a request"""
    result = parking_system.allocate_parking(request_id)
    return jsonify(result)

@app.route('/api/request/<request_id>/occupy', methods=['POST'])
def occupy_parking(request_id):
    """Mark parking as occupied"""
    result = parking_system.occupy_parking(request_id)
    return jsonify(result)

@app.route('/api/request/<request_id>/release', methods=['POST'])
def release_parking(request_id):
    """Release parking"""
    result = parking_system.release_parking(request_id)
    return jsonify(result)

@app.route('/api/request/<request_id>/cancel', methods=['POST'])
def cancel_request(request_id):
    """Cancel a request"""
    result = parking_system.cancel_request(request_id)
    return jsonify(result)

@app.route('/api/request/<request_id>', methods=['GET'])
def get_request(request_id):
    """Get request details"""
    req = parking_system.get_request_by_id(request_id)
    if req:
        return jsonify(req.to_dict())
    return jsonify({'error': 'Request not found'}), 404

@app.route('/api/requests', methods=['GET'])
def get_all_requests():
    """Get all requests"""
    requests = []
    for req in parking_system.get_all_requests():
        requests.append(req.to_dict())
    return jsonify({'requests': requests})


# ==========================================
# QUEUE ENDPOINTS
# ==========================================

@app.route('/api/queue/status', methods=['GET'])
def get_queue_status():
    """Get queue status"""
    status = parking_system.get_queue_status()
    return jsonify(status)

@app.route('/api/queue/process', methods=['POST'])
def process_queue():
    """Process next request in queue"""
    result = parking_system.process_next_request()
    return jsonify(result)


# ==========================================
# ROLLBACK ENDPOINTS
# ==========================================

@app.route('/api/rollback', methods=['POST'])
def rollback_operations():
    """Rollback last k operations"""
    data = request.json
    k = data.get('k', 1)
    result = parking_system.rollback_operations(k)
    return jsonify(result)

@app.route('/api/rollback/history', methods=['GET'])
def get_rollback_history():
    """Get rollback history"""
    n = request.args.get('n', 10, type=int)
    history = parking_system.get_rollback_history(n)
    return jsonify({'history': history})


# ==========================================
# ANALYTICS ENDPOINTS
# ==========================================

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics"""
    analytics = parking_system.get_analytics()
    return jsonify(analytics)


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🅿️  SMART PARKING SYSTEM - API SERVER")
    print("="*60)
    print("✓ All custom data structures loaded:")
    print("  - Array (fixed-size)")
    print("  - LinkedList (singly-linked)")
    print("  - Stack (LIFO for rollback)")
    print("  - Queue (FIFO for pending requests)")
    print("  - HashTable (replaces dictionaries)")
    print("  - AdjacencyList (zone graph)")
    print("\n✓ No built-in dictionaries or maps used!")
    print("✓ Server running on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
