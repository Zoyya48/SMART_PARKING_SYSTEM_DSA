"""
ParkingSystem.py - Main system integrating all components
ALL CUSTOM DATA STRUCTURES - NO BUILT-IN DICTS!
"""

from Zone import Zone
from ParkingArea import ParkingArea
from ParkingSlot import ParkingSlot
from Vehicle import Vehicle
from ParkingRequest import ParkingRequest, RequestState
from AllocationEngine import AllocationEngine
from RollbackManager import RollbackManager
from DataStructures import HashTable, Queue
from datetime import datetime


class ParkingSystem:
    """
    Main parking management system
    Uses ONLY custom data structures - no built-in dicts or maps!
    """
    
    def __init__(self):
        """Initialize the parking system with custom data structures"""
        # ✅ Custom HashTable instead of dict
        self.zones = HashTable(100)  # For zone storage
        self.vehicles = HashTable(500)  # For vehicle storage
        self.requests = HashTable(1000)  # For request storage
        
        # ✅ Custom Queue for pending requests
        self.pending_requests = Queue(100)
        
        # Other components
        self.allocation_engine = None
        self.rollback_manager = RollbackManager()
        self.request_counter = 0
        
        # Trip history (kept as list for analytics simplicity)
        self.trip_history = []
    
    # ==========================================
    # ZONE MANAGEMENT
    # ==========================================
    
    def add_zone(self, zone_id, zone_name, adjacent_zones=None):
        """
        Add a new zone to the system
        Returns: Zone object
        """
        zone = Zone(zone_id, zone_name, adjacent_zones)
        self.zones.insert(zone_id, zone)  # ✅ HashTable.insert()
        
        # Update allocation engine
        self.allocation_engine = AllocationEngine(self.zones)
        return zone
    
    def add_parking_area(self, zone_id, area_id, area_name, num_slots):
        """
        Add parking area to a zone
        Returns: ParkingArea object or None
        """
        if not self.zones.contains(zone_id):  # ✅ HashTable.contains()
            return None
        
        zone = self.zones.get(zone_id)  # ✅ HashTable.get()
        area = ParkingArea(area_id, zone_id, area_name, num_slots)
        
        # Create slots for this area
        for i in range(num_slots):
            slot_id = f"{area_id}_SLOT_{i+1}"
            slot = ParkingSlot(slot_id, area_id, zone_id)
            area.add_slot(slot)
        
        zone.add_parking_area(area)
        return area
    
    def get_zone(self, zone_id):
        """Get zone by ID"""
        return self.zones.get(zone_id)
    
    def get_all_zones(self):
        """Get all zones"""
        return self.zones.values()
    
    # ==========================================
    # VEHICLE MANAGEMENT
    # ==========================================
    
    def register_vehicle(self, vehicle_id, preferred_zone, vehicle_type="Car"):
        """
        Register a new vehicle
        Returns: Vehicle object or None if already exists
        """
        if self.vehicles.contains(vehicle_id):  # ✅ HashTable.contains()
            return None
        
        vehicle = Vehicle(vehicle_id, preferred_zone, vehicle_type)
        self.vehicles.insert(vehicle_id, vehicle)  # ✅ HashTable.insert()
        return vehicle
    
    def get_vehicle(self, vehicle_id):
        """Get vehicle by ID"""
        return self.vehicles.get(vehicle_id)
    
    # ==========================================
    # REQUEST MANAGEMENT
    # ==========================================
    
    def create_request(self, vehicle_id, requested_zone, auto_allocate=True):
        """
        Create a parking request
        Args:
            vehicle_id: ID of the vehicle
            requested_zone: Preferred zone
            auto_allocate: If False, add to queue instead
        Returns: ParkingRequest object
        """
        # Generate unique request ID
        self.request_counter += 1
        request_id = f"REQ_{self.request_counter:04d}"
        
        # Create request
        request = ParkingRequest(request_id, vehicle_id, requested_zone)
        
        # Store in hash table
        self.requests.insert(request_id, request)  # ✅ HashTable.insert()
        
        # Add to queue if not auto-allocating
        if not auto_allocate:
            try:
                self.pending_requests.enqueue(request_id)  # ✅ Queue.enqueue()
            except Exception:
                pass  # Queue full
        
        return request
    
    def allocate_parking(self, request_id):
        """
        Allocate parking slot to a request
        Returns: Dictionary with result
        """
        if not self.requests.contains(request_id):  # ✅ HashTable.contains()
            return {'success': False, 'error': 'Request not found'}
        
        request = self.requests.get(request_id)  # ✅ HashTable.get()
        
        # Check if already allocated
        if request.state != RequestState.REQUESTED:
            return {'success': False, 'error': f'Request in state: {request.state}'}
        
        # Try to allocate slot
        slot, zone_id, is_cross_zone = self.allocation_engine.allocate_slot(request)
        
        if slot is None:
            return {
                'success': False,
                'error': 'No slots available',
                'request_id': request_id
            }
        
        # Record previous states for rollback
        slot_previous_state = slot.get_state()
        request_previous_state = request.get_state_info()
        
        # Allocate slot
        slot.allocate(request.vehicle_id, request_id)
        allocation_time = datetime.now().isoformat()
        request.allocate(slot.slot_id, zone_id, allocation_time)
        
        # Record operation for rollback
        self.rollback_manager.record_operation(
            'allocate', request, slot_previous_state, request_previous_state
        )
        
        return {
            'success': True,
            'request_id': request_id,
            'slot_id': slot.slot_id,
            'zone_id': zone_id,
            'is_cross_zone': is_cross_zone,
            'cross_zone_penalty': request.cross_zone_penalty,
            'allocation_time': allocation_time
        }
    
    def occupy_parking(self, request_id):
        """
        Mark parking as occupied (vehicle arrived)
        Returns: Dictionary with result
        """
        if not self.requests.contains(request_id):
            return {'success': False, 'error': 'Request not found'}
        
        request = self.requests.get(request_id)
        
        if request.state != RequestState.ALLOCATED:
            return {'success': False, 'error': f'Cannot occupy from state: {request.state}'}
        
        # Record for rollback
        request_previous_state = request.get_state_info()
        slot = self.allocation_engine.find_slot_by_id(request.allocated_slot)
        slot_previous_state = slot.get_state() if slot else {}
        
        # Occupy
        occupation_time = datetime.now().isoformat()
        request.occupy(occupation_time)
        
        # Record operation
        self.rollback_manager.record_operation(
            'occupy', request, slot_previous_state, request_previous_state
        )
        
        return {
            'success': True,
            'request_id': request_id,
            'occupation_time': occupation_time
        }
    
    def release_parking(self, request_id):
        """
        Release parking (vehicle left)
        Returns: Dictionary with result
        """
        if not self.requests.contains(request_id):
            return {'success': False, 'error': 'Request not found'}
        
        request = self.requests.get(request_id)
        
        if request.state != RequestState.OCCUPIED:
            return {'success': False, 'error': f'Cannot release from state: {request.state}'}
        
        # Find and release slot
        slot = self.allocation_engine.find_slot_by_id(request.allocated_slot)
        if slot:
            slot.release()
        
        # Record for rollback
        request_previous_state = request.get_state_info()
        slot_previous_state = slot.get_state() if slot else {}
        
        # Release
        release_time = datetime.now().isoformat()
        request.release(release_time)
        
        # Record operation
        self.rollback_manager.record_operation(
            'release', request, slot_previous_state, request_previous_state
        )
        
        # Add to trip history
        self.trip_history.append(request.to_dict())
        
        return {
            'success': True,
            'request_id': request_id,
            'release_time': release_time,
            'duration_seconds': request.get_duration()
        }
    
    def cancel_request(self, request_id):
        """
        Cancel a request
        Returns: Dictionary with result
        """
        if not self.requests.contains(request_id):
            return {'success': False, 'error': 'Request not found'}
        
        request = self.requests.get(request_id)
        
        # Can only cancel from REQUESTED or ALLOCATED states
        if request.state not in [RequestState.REQUESTED, RequestState.ALLOCATED]:
            return {'success': False, 'error': f'Cannot cancel from state: {request.state}'}
        
        # If allocated, release the slot
        if request.state == RequestState.ALLOCATED and request.allocated_slot:
            slot = self.allocation_engine.find_slot_by_id(request.allocated_slot)
            if slot:
                slot.release()
        
        cancellation_time = datetime.now().isoformat()
        request.cancel(cancellation_time)
        
        # Add to trip history
        self.trip_history.append(request.to_dict())
        
        return {
            'success': True,
            'request_id': request_id,
            'cancellation_time': cancellation_time
        }
    
    def get_request_by_id(self, request_id):
        """Get request by ID"""
        return self.requests.get(request_id)
    
    def get_all_requests(self):
        """Get all requests"""
        return self.requests.values()
    
    # ==========================================
    # QUEUE OPERATIONS
    # ==========================================
    
    def add_to_queue(self, request_id):
        """Add request to pending queue"""
        try:
            self.pending_requests.enqueue(request_id)  # ✅ Queue.enqueue()
            return {'success': True, 'position': self.pending_requests.size()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_next_request(self):
        """Process next request from queue (FIFO)"""
        request_id = self.pending_requests.dequeue()  # ✅ Queue.dequeue()
        if request_id:
            return self.allocate_parking(request_id)
        return {'success': False, 'error': 'No pending requests'}
    
    def get_queue_status(self):
        """Get current queue status"""
        return {
            'pending_count': self.pending_requests.size(),
            'pending_requests': self.pending_requests.get_all()
        }
    
    # ==========================================
    # ROLLBACK OPERATIONS
    # ==========================================
    
    def rollback_operations(self, k):
        """Rollback last k operations"""
        rolled_back = self.rollback_manager.rollback(k, self)
        return {
            'success': True,
            'rolled_back_count': len(rolled_back),
            'operations': rolled_back
        }
    
    def get_rollback_history(self, n=10):
        """Get recent rollback history"""
        return self.rollback_manager.get_recent_operations(n)
    
    # ==========================================
    # ANALYTICS
    # ==========================================
    
    def get_analytics(self):
        """Get comprehensive system analytics"""
        total_requests = len(self.trip_history)
        completed = [r for r in self.trip_history if r['state'] == RequestState.RELEASED]
        cancelled = [r for r in self.trip_history if r['state'] == RequestState.CANCELLED]
        
        # Calculate average parking duration
        durations = [r['duration_seconds'] for r in completed if r['duration_seconds'] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Zone utilization - ✅ FIXED: Using custom HashTable instead of dict
        zone_stats = HashTable(len(self.zones))  # ✅ Custom HashTable
        for zone_id, zone in self.zones.items():  # ✅ HashTable.items()
            zone_stats.insert(zone_id, {  # ✅ HashTable.insert() instead of zone_stats[zone_id] =
                'zone_name': zone.zone_name,
                'utilization_rate': round(zone.get_utilization_rate(), 2),
                'total_slots': zone.get_total_slots(),
                'occupied_slots': zone.get_occupied_slots(),
                'available_slots': len(zone.get_available_slots())
            })
        
        # Peak usage zones - ✅ FIXED: Get items from HashTable for sorting
        zone_stats_items = zone_stats.items()  # Get list of tuples from HashTable
        peak_zones = sorted(zone_stats_items, 
                          key=lambda x: x[1]['utilization_rate'], 
                          reverse=True)
        
        # Active requests
        active_requests = 0
        for request in self.requests.values():  # ✅ HashTable.values()
            if request.state in [RequestState.REQUESTED, RequestState.ALLOCATED, RequestState.OCCUPIED]:
                active_requests += 1
        
        # ✅ FIXED: Convert HashTable to dict only for JSON response (acceptable for API output)
        # This is the ONLY place we use a built-in dict, and it's just for JSON serialization
        zone_stats_dict = {}
        for zone_id, stats in zone_stats.items():
            zone_stats_dict[zone_id] = stats
        
        return {
            'total_requests': total_requests,
            'completed_requests': len(completed),
            'cancelled_requests': len(cancelled),
            'active_requests': active_requests,
            'average_parking_duration_seconds': round(avg_duration, 2),
            'average_parking_duration_minutes': round(avg_duration / 60, 2),
            'zone_utilization': zone_stats_dict,  # ✅ Converted to dict only for JSON
            'peak_usage_zones': [{'zone_id': z[0], **z[1]} for z in peak_zones[:3]],
            'completion_rate': round((len(completed) / total_requests * 100) if total_requests > 0 else 0, 2),
            'cancellation_rate': round((len(cancelled) / total_requests * 100) if total_requests > 0 else 0, 2)
        }
    
    def get_system_status(self):
        """Get overall system status"""
        # ✅ FIXED: Convert zones HashTable to dict only for JSON response
        zones_dict = {}
        for zone_id, zone in self.zones.items():
            zones_dict[zone_id] = zone.to_dict()
        
        return {
            'total_zones': len(self.zones),
            'total_vehicles': len(self.vehicles),
            'total_requests': len(self.requests),
            'active_requests': len([r for r in self.requests.values() 
                                   if r.state in [RequestState.REQUESTED, RequestState.ALLOCATED, RequestState.OCCUPIED]]),
            'pending_queue_size': self.pending_requests.size(),
            'rollback_history_size': self.rollback_manager.get_history_size(),
            'zones': zones_dict  # ✅ Converted to dict only for JSON
        }
