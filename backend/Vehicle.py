"""
Vehicle.py - Vehicle registration and management
"""

class Vehicle:
    """Represents a registered vehicle"""
    
    def __init__(self, vehicle_id, preferred_zone, vehicle_type="Car"):
        """
        Initialize a vehicle
        Args:
            vehicle_id: Unique identifier (e.g., license plate)
            preferred_zone: Preferred parking zone
            vehicle_type: Type of vehicle (Car, SUV, etc.)
        """
        self.vehicle_id = vehicle_id
        self.preferred_zone = preferred_zone
        self.vehicle_type = vehicle_type
        self.is_parked = False
        self.current_request = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'vehicle_id': self.vehicle_id,
            'preferred_zone': self.preferred_zone,
            'vehicle_type': self.vehicle_type,
            'is_parked': self.is_parked,
            'current_request': self.current_request
        }
