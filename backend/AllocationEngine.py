"""
AllocationEngine.py - Slot allocation logic with custom data structures
"""

class AllocationEngine:
    """
    Engine for allocating parking slots based on availability and zone rules
    Uses custom HashTable for zone storage (no built-in dictionaries!)
    """
    
    def __init__(self, zones_hashtable):
        """
        Initialize allocation engine
        Args:
            zones_hashtable: HashTable of Zone objects
        """
        self.zones = zones_hashtable  # ✅ Custom HashTable, not dict
    
    def allocate_slot(self, request):
        """
        Allocate parking slot using strategy:
        1. Try requested zone (same-zone preference)
        2. Try adjacent zones (cross-zone with penalty)
        3. Try any available zone (last resort)
        
        Args:
            request: ParkingRequest object
        Returns:
            Tuple (slot, zone_id, is_cross_zone) or (None, None, False)
        """
        requested_zone = request.requested_zone
        
        # Step 1: Try requested zone first (same-zone preference)
        if self.zones.contains(requested_zone):
            zone = self.zones.get(requested_zone)
            available_slots = zone.get_available_slots()
            if available_slots:
                # First-available slot strategy
                return (available_slots[0], requested_zone, False)
        
        # Step 2: Try adjacent zones (cross-zone allocation)
        if self.zones.contains(requested_zone):
            zone = self.zones.get(requested_zone)
            adjacent_zone_ids = zone.get_adjacent_zone_list()
            
            for adjacent_zone_id in adjacent_zone_ids:
                if self.zones.contains(adjacent_zone_id):
                    adjacent_zone = self.zones.get(adjacent_zone_id)
                    available_slots = adjacent_zone.get_available_slots()
                    if available_slots:
                        return (available_slots[0], adjacent_zone_id, True)
        
        # Step 3: Try any available zone (last resort)
        all_zones = self.zones.items()  # Get all (zone_id, zone) tuples
        for zone_id, zone in all_zones:
            if zone_id != requested_zone:
                available_slots = zone.get_available_slots()
                if available_slots:
                    return (available_slots[0], zone_id, True)
        
        # No slots available anywhere
        return (None, None, False)
    
    def find_slot_by_id(self, slot_id):
        """
        Find slot by ID across all zones - O(n*m)
        Args:
            slot_id: ID of the slot to find
        Returns:
            ParkingSlot object or None
        """
        all_zones = self.zones.values()  # Get all Zone objects
        for zone in all_zones:
            for area in zone.parking_areas:  # LinkedList iteration
                slot = area.get_slot_by_id(slot_id)
                if slot:
                    return slot
        return None
    
    def get_zone_availability(self):
        """Get availability status for all zones"""
        availability = {}
        all_zones = self.zones.items()  # Get (zone_id, zone) tuples
        
        for zone_id, zone in all_zones:
            availability[zone_id] = {
                'zone_name': zone.zone_name,
                'total_slots': zone.get_total_slots(),
                'available_slots': len(zone.get_available_slots()),
                'occupied_slots': zone.get_occupied_slots(),
                'utilization_rate': round(zone.get_utilization_rate(), 2)
            }
        return availability
    
    def get_best_zone_suggestion(self, preferred_zone):
        """
        Suggest best alternative zone if preferred is full
        Args:
            preferred_zone: Preferred zone ID
        Returns:
            Best alternative zone ID or None
        """
        if self.zones.contains(preferred_zone):
            zone = self.zones.get(preferred_zone)
            
            # Check adjacent zones first
            adjacent_zone_ids = zone.get_adjacent_zone_list()
            for adj_zone_id in adjacent_zone_ids:
                if self.zones.contains(adj_zone_id):
                    adj_zone = self.zones.get(adj_zone_id)
                    if len(adj_zone.get_available_slots()) > 0:
                        return adj_zone_id
        
        # Find zone with most availability
        best_zone = None
        max_available = 0
        all_zones = self.zones.items()
        
        for zone_id, zone in all_zones:
            available = len(zone.get_available_slots())
            if available > max_available:
                max_available = available
                best_zone = zone_id
        
        return best_zone
