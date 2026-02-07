"""
ParkingSlot.py - Individual parking slot management
"""

class ParkingSlot:
    """Represents a single parking slot"""
    
    def __init__(self, slot_id, area_id, zone_id):
        """
        Initialize a parking slot
        Args:
            slot_id: Unique identifier for the slot
            area_id: ID of the parking area
            zone_id: ID of the zone
        """
        self.slot_id = slot_id
        self.area_id = area_id
        self.zone_id = zone_id
        self.is_available = True
        self.current_vehicle = None
        self.current_request = None
    
    def allocate(self, vehicle_id, request_id):
        """
        Allocate slot to a vehicle
        Returns: True if successful, False otherwise
        """
        if not self.is_available:
            return False
        
        self.is_available = False
        self.current_vehicle = vehicle_id
        self.current_request = request_id
        return True
    
    def release(self):
        """
        Release the slot (make it available)
        Returns: True if successful
        """
        self.is_available = True
        self.current_vehicle = None
        self.current_request = None
        return True
    
    def get_state(self):
        """Get current state for rollback"""
        return {
            'is_available': self.is_available,
            'current_vehicle': self.current_vehicle,
            'current_request': self.current_request
        }
    
    def restore_state(self, state):
        """Restore previous state (for rollback)"""
        self.is_available = state['is_available']
        self.current_vehicle = state['current_vehicle']
        self.current_request = state['current_request']
        return True
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'slot_id': self.slot_id,
            'area_id': self.area_id,
            'zone_id': self.zone_id,
            'is_available': self.is_available,
            'current_vehicle': self.current_vehicle,
            'current_request': self.current_request
        }
