"""
ParkingRequest.py - Parking request with strict state machine
"""

from datetime import datetime

class RequestState:
    """Enumeration of request states"""
    REQUESTED = "REQUESTED"
    ALLOCATED = "ALLOCATED"
    OCCUPIED = "OCCUPIED"
    RELEASED = "RELEASED"
    CANCELLED = "CANCELLED"


class ParkingRequest:
    """
    Represents a parking request with state machine lifecycle
    
    State Machine:
    REQUESTED → ALLOCATED → OCCUPIED → RELEASED
    REQUESTED → CANCELLED
    ALLOCATED → CANCELLED
    """
    
    # Valid state transitions (enforced strictly)
    VALID_TRANSITIONS = {
        RequestState.REQUESTED: [RequestState.ALLOCATED, RequestState.CANCELLED],
        RequestState.ALLOCATED: [RequestState.OCCUPIED, RequestState.CANCELLED],
        RequestState.OCCUPIED: [RequestState.RELEASED],
        RequestState.RELEASED: [],  # Terminal state
        RequestState.CANCELLED: []  # Terminal state
    }
    
    def __init__(self, request_id, vehicle_id, requested_zone, request_time=None):
        """
        Initialize a parking request
        Args:
            request_id: Unique identifier
            vehicle_id: ID of the requesting vehicle
            requested_zone: Preferred zone
            request_time: Time of request
        """
        self.request_id = request_id
        self.vehicle_id = vehicle_id
        self.requested_zone = requested_zone
        self.request_time = request_time if request_time else datetime.now().isoformat()
        
        # State machine
        self.state = RequestState.REQUESTED
        self.state_history = [RequestState.REQUESTED]
        
        # Allocation details
        self.allocated_slot = None
        self.allocated_zone = None
        self.allocation_time = None
        
        # Timing
        self.occupation_time = None
        self.release_time = None
        self.cancellation_time = None
        
        # Penalties
        self.cross_zone_penalty = 0
    
    def transition_to(self, new_state):
        """
        Transition to new state with validation
        Returns: True if valid transition, False otherwise
        """
        # Check if transition is valid
        valid_next_states = self.VALID_TRANSITIONS.get(self.state, [])
        if new_state not in valid_next_states:
            return False
        
        # Perform transition
        self.state = new_state
        self.state_history.append(new_state)
        return True
    
    def allocate(self, slot_id, zone_id, allocation_time=None):
        """
        Allocate slot to this request
        Returns: True if successful, False if invalid state
        """
        if not self.transition_to(RequestState.ALLOCATED):
            return False
        
        self.allocated_slot = slot_id
        self.allocated_zone = zone_id
        self.allocation_time = allocation_time if allocation_time else datetime.now().isoformat()
        
        # Calculate cross-zone penalty
        if zone_id != self.requested_zone:
            self.cross_zone_penalty = 50
        
        return True
    
    def occupy(self, occupation_time=None):
        """
        Mark as occupied (vehicle arrived)
        Returns: True if successful
        """
        if not self.transition_to(RequestState.OCCUPIED):
            return False
        
        self.occupation_time = occupation_time if occupation_time else datetime.now().isoformat()
        return True
    
    def release(self, release_time=None):
        """
        Release parking (vehicle left)
        Returns: True if successful
        """
        if not self.transition_to(RequestState.RELEASED):
            return False
        
        self.release_time = release_time if release_time else datetime.now().isoformat()
        return True
    
    def cancel(self, cancellation_time=None):
        """
        Cancel the request
        Returns: True if successful
        """
        if not self.transition_to(RequestState.CANCELLED):
            return False
        
        self.cancellation_time = cancellation_time if cancellation_time else datetime.now().isoformat()
        return True
    
    def get_duration(self):
        """Calculate parking duration in seconds"""
        if self.occupation_time and self.release_time:
            try:
                occupy = datetime.fromisoformat(self.occupation_time)
                release = datetime.fromisoformat(self.release_time)
                return (release - occupy).total_seconds()
            except:
                return 0
        return 0
    
    def is_completed(self):
        """Check if request is in terminal state"""
        return self.state in [RequestState.RELEASED, RequestState.CANCELLED]
    
    def get_state_info(self):
        """Get current state for rollback"""
        return {
            'state': self.state,
            'allocated_slot': self.allocated_slot,
            'allocated_zone': self.allocated_zone,
            'allocation_time': self.allocation_time,
            'occupation_time': self.occupation_time,
            'release_time': self.release_time,
            'cancellation_time': self.cancellation_time,
            'cross_zone_penalty': self.cross_zone_penalty
        }
    
    def restore_state(self, state_info):
        """Restore previous state (for rollback)"""
        self.state = state_info['state']
        self.allocated_slot = state_info['allocated_slot']
        self.allocated_zone = state_info['allocated_zone']
        self.allocation_time = state_info['allocation_time']
        self.occupation_time = state_info['occupation_time']
        self.release_time = state_info['release_time']
        self.cancellation_time = state_info['cancellation_time']
        self.cross_zone_penalty = state_info['cross_zone_penalty']
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'vehicle_id': self.vehicle_id,
            'requested_zone': self.requested_zone,
            'allocated_zone': self.allocated_zone,
            'allocated_slot': self.allocated_slot,
            'state': self.state,
            'state_history': self.state_history,
            'request_time': self.request_time,
            'allocation_time': self.allocation_time,
            'occupation_time': self.occupation_time,
            'release_time': self.release_time,
            'cancellation_time': self.cancellation_time,
            'cross_zone_penalty': self.cross_zone_penalty,
            'duration_seconds': self.get_duration(),
            'is_completed': self.is_completed()
        }
