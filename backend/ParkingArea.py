"""
ParkingArea.py - Manages parking areas with custom Array data structure
"""

from DataStructures import Array

class ParkingArea:
    """Represents a parking area within a zone"""
    
    def __init__(self, area_id, zone_id, area_name, max_slots=100):
        """
        Initialize a parking area
        Args:
            area_id: Unique identifier
            zone_id: ID of the zone this area belongs to
            area_name: Name of the area
            max_slots: Maximum capacity (fixed-size array)
        """
        self.area_id = area_id
        self.zone_id = zone_id
        self.area_name = area_name
        self.slots = Array(max_slots)  # ✅ Custom Array instead of list
        self.max_slots = max_slots
    
    def add_slot(self, slot):
        """Add a parking slot - O(1)"""
        try:
            self.slots.append(slot)
            return True
        except Exception as e:
            return False
    
    def get_available_slots(self):
        """Get all available slots - O(n)"""
        available = []
        for slot in self.slots:  # Array is iterable
            if slot.is_available:
                available.append(slot)
        return available
    
    def get_slot_by_id(self, slot_id):
        """Find slot by ID - O(n)"""
        for slot in self.slots:
            if slot.slot_id == slot_id:
                return slot
        return None
    
    def get_total_slots(self):
        """Get total number of slots - O(1)"""
        return len(self.slots)
    
    def get_occupied_slots(self):
        """Get number of occupied slots - O(n)"""
        count = 0
        for slot in self.slots:
            if not slot.is_available:
                count += 1
        return count
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'area_id': self.area_id,
            'zone_id': self.zone_id,
            'area_name': self.area_name,
            'total_slots': self.get_total_slots(),
            'available_slots': len(self.get_available_slots()),
            'occupied_slots': self.get_occupied_slots(),
            'max_capacity': self.max_slots
        }
