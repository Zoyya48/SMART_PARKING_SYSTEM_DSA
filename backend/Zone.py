"""
Zone.py - City zone management with custom data structures
"""

from DataStructures import LinkedList, AdjacencyList

class Zone:
    """Represents a parking zone in the city"""
    
    def __init__(self, zone_id, zone_name, adjacent_zones=None):
        """
        Initialize a zone
        Args:
            zone_id: Unique identifier
            zone_name: Name of the zone
            adjacent_zones: List of adjacent zone IDs (for initialization)
        """
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.parking_areas = LinkedList()  # ✅ Custom LinkedList
        self.adjacent_zones = AdjacencyList()  # ✅ Custom AdjacencyList (graph)
        self.cross_zone_penalty = 50  # Penalty for cross-zone parking
        
        # Add adjacent zones if provided
        if adjacent_zones:
            for adj_zone_id in adjacent_zones:
                self.adjacent_zones.add_adjacent_zone(adj_zone_id)
    
    def add_parking_area(self, parking_area):
        """Add parking area to zone - O(n)"""
        self.parking_areas.append(parking_area)
        return True
    
    def get_available_slots(self):
        """Get all available slots in this zone - O(n*m)"""
        available_slots = []
        for area in self.parking_areas:  # LinkedList is iterable
            available_slots.extend(area.get_available_slots())
        return available_slots
    
    def get_total_slots(self):
        """Get total number of slots - O(n)"""
        total = 0
        for area in self.parking_areas:
            total += len(area.slots)
        return total
    
    def get_occupied_slots(self):
        """Get number of occupied slots - O(n*m)"""
        occupied = 0
        for area in self.parking_areas:
            for slot in area.slots:
                if not slot.is_available:
                    occupied += 1
        return occupied
    
    def get_utilization_rate(self):
        """Calculate utilization percentage - O(n)"""
        total = self.get_total_slots()
        if total == 0:
            return 0.0
        occupied = self.get_occupied_slots()
        return (occupied / total) * 100
    
    def is_adjacent(self, zone_id):
        """Check if zone is adjacent - O(n)"""
        return self.adjacent_zones.is_adjacent(zone_id)
    
    def get_adjacent_zone_list(self):
        """Get list of adjacent zones - O(n)"""
        return self.adjacent_zones.get_adjacent_zones()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'zone_id': self.zone_id,
            'zone_name': self.zone_name,
            'total_slots': self.get_total_slots(),
            'occupied_slots': self.get_occupied_slots(),
            'available_slots': len(self.get_available_slots()),
            'utilization_rate': round(self.get_utilization_rate(), 2),
            'adjacent_zones': self.adjacent_zones.get_adjacent_zones(),
            'cross_zone_penalty': self.cross_zone_penalty,
            'parking_areas_count': len(self.parking_areas)
        }
