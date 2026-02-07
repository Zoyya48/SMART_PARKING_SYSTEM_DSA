"""
RollbackManager.py - Rollback management using custom Stack
"""

from DataStructures import Stack

class RollbackManager:
    """
    Manages rollback of parking allocations using Stack (LIFO)
    No built-in list - uses custom Stack implementation!
    """
    
    def __init__(self, max_history=100):
        """
        Initialize rollback manager
        Args:
            max_history: Maximum operations to keep in history
        """
        self.operation_history = Stack(max_history)  # ✅ Custom Stack, not list
        self.max_history = max_history
    
    def record_operation(self, operation_type, request, slot_state, request_state):
        """
        Record an operation for potential rollback
        Args:
            operation_type: Type ('allocate', 'occupy', 'release')
            request: ParkingRequest object
            slot_state: Previous state of the slot
            request_state: Previous state of the request
        """
        operation = {
            'type': operation_type,
            'request_id': request.request_id,
            'vehicle_id': request.vehicle_id,
            'slot_id': request.allocated_slot,
            'zone_id': request.allocated_zone,
            'slot_previous_state': slot_state,
            'request_previous_state': request_state,
            'timestamp': request.request_time
        }
        
        try:
            self.operation_history.push(operation)  # ✅ Stack push
        except Exception:
            # Stack full - oldest operation dropped automatically
            pass
    
    def rollback(self, k, parking_system):
        """
        Rollback last k operations (LIFO order)
        Args:
            k: Number of operations to rollback
            parking_system: Reference to ParkingSystem
        Returns:
            List of rolled back operations
        """
        if k <= 0 or self.operation_history.is_empty():
            return []
        
        k = min(k, self.operation_history.size())
        rolled_back = []
        
        for _ in range(k):
            operation = self.operation_history.pop()  # ✅ Stack pop (LIFO)
            if operation is None:
                break
            
            # Get the slot and request
            slot = parking_system.allocation_engine.find_slot_by_id(operation['slot_id'])
            request = parking_system.get_request_by_id(operation['request_id'])
            
            if slot and request:
                # Restore slot state
                slot.restore_state(operation['slot_previous_state'])
                
                # Restore request state
                request.restore_state(operation['request_previous_state'])
                
                rolled_back.append({
                    'operation': operation['type'],
                    'request_id': operation['request_id'],
                    'vehicle_id': operation['vehicle_id'],
                    'slot_id': operation['slot_id'],
                    'timestamp': operation['timestamp']
                })
        
        return rolled_back
    
    def get_history_size(self):
        """Get number of operations in history - O(1)"""
        return self.operation_history.size()
    
    def clear_history(self):
        """Clear all operation history"""
        self.operation_history.clear()
    
    def get_recent_operations(self, n=10):
        """Get n most recent operations (without removing) - O(n)"""
        return self.operation_history.get_recent(n)
    
    def peek_last_operation(self):
        """View last operation without removing - O(1)"""
        return self.operation_history.peek()
