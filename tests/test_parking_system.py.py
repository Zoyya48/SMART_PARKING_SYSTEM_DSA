"""
test_parking_system.py - Comprehensive test suite for Smart Parking System
Tests all requirements from PDF:
1. Slot allocation correctness
2. Cross-zone allocation handling
3. Cancellation and rollback correctness
4. Invalid state transition detection
5. Analytics correctness after rollback
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ParkingSystem import ParkingSystem
from ParkingRequest import RequestState
from Vehicle import Vehicle


class TestParkingSystem:
    """Test suite for parking system"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.system = None
    
    def setup(self):
        """Initialize system before each test"""
        self.system = ParkingSystem()
        
        # Add zones with adjacency
        self.system.add_zone('ZONE_A', 'Downtown', ['ZONE_B'])
        self.system.add_zone('ZONE_B', 'Uptown', ['ZONE_A', 'ZONE_C'])
        self.system.add_zone('ZONE_C', 'Suburbs', ['ZONE_B'])
        
        # Add parking areas with limited slots for testing
        self.system.add_parking_area('ZONE_A', 'AREA_A1', 'Downtown Plaza', 2)  # Only 2 slots
        self.system.add_parking_area('ZONE_B', 'AREA_B1', 'Uptown Mall', 3)     # 3 slots
        self.system.add_parking_area('ZONE_C', 'AREA_C1', 'Suburb Center', 5)   # 5 slots
        
        # Register test vehicles
        self.system.register_vehicle('VEH_001', 'ZONE_A')
        self.system.register_vehicle('VEH_002', 'ZONE_A')
        self.system.register_vehicle('VEH_003', 'ZONE_B')
        self.system.register_vehicle('VEH_004', 'ZONE_C')
    
    def assert_equal(self, actual, expected, test_name):
        """Assert equality and track results"""
        if actual == expected:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
            return True
        else:
            print(f"❌ FAIL: {test_name}")
            print(f"   Expected: {expected}, Got: {actual}")
            self.tests_failed += 1
            return False
    
    def assert_true(self, condition, test_name):
        """Assert true condition"""
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
            return True
        else:
            print(f"❌ FAIL: {test_name}")
            self.tests_failed += 1
            return False
    
    # ==========================================
    # TEST 1: Slot Allocation Correctness
    # ==========================================
    def test_slot_allocation_correctness(self):
        """Test 1: Verify basic slot allocation works correctly"""
        print("\n--- Test 1: Slot Allocation Correctness ---")
        self.setup()
        
        # Create and allocate request
        request = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        result = self.system.allocate_parking(request.request_id)
        
        # Verify allocation success
        self.assert_true(result['success'], "1.1: Allocation should succeed")
        self.assert_equal(result['zone_id'], 'ZONE_A', "1.2: Should allocate in requested zone")
        self.assert_true(result['slot_id'].startswith('AREA_A1'), "1.3: Should allocate slot in correct area")
        
        # Verify request state changed
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.ALLOCATED, "1.4: Request state should be ALLOCATED")
        
        # Verify slot is marked as unavailable
        zone = self.system.get_zone('ZONE_A')
        available_slots = zone.get_available_slots()
        self.assert_equal(len(available_slots), 1, "1.5: Should have 1 available slot left (2-1=1)")
    
    # ==========================================
    # TEST 2: Cross-Zone Allocation Handling
    # ==========================================
    def test_cross_zone_allocation(self):
        """Test 2: Verify cross-zone allocation when requested zone is full"""
        print("\n--- Test 2: Cross-Zone Allocation ---")
        self.setup()
        
        # Fill ZONE_A (2 slots)
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req1.request_id)
        
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req2.request_id)
        
        # Try to allocate third vehicle to full ZONE_A
        req3 = self.system.create_request('VEH_003', 'ZONE_A', auto_allocate=False)
        result = self.system.allocate_parking(req3.request_id)
        
        # Should allocate to adjacent zone (ZONE_B)
        self.assert_true(result['success'], "2.1: Cross-zone allocation should succeed")
        self.assert_equal(result['zone_id'], 'ZONE_B', "2.2: Should allocate to adjacent ZONE_B")
        self.assert_true(result['is_cross_zone'], "2.3: Should be marked as cross-zone")
        
        # Verify penalty applied
        request = self.system.get_request_by_id(req3.request_id)
        self.assert_equal(request.cross_zone_penalty, 50, "2.4: Should apply 50-unit penalty")
    
    # ==========================================
    # TEST 3: Cancellation Correctness
    # ==========================================
    def test_cancellation_correctness(self):
        """Test 3: Verify cancellation restores slot availability"""
        print("\n--- Test 3: Cancellation Correctness ---")
        self.setup()
        
        # Allocate a slot
        request = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        result = self.system.allocate_parking(request.request_id)
        allocated_slot_id = result['slot_id']
        
        # Check available slots before cancellation
        zone = self.system.get_zone('ZONE_A')
        slots_before = len(zone.get_available_slots())
        
        # Cancel the request
        cancel_result = self.system.cancel_request(request.request_id)
        self.assert_true(cancel_result['success'], "3.1: Cancellation should succeed")
        
        # Verify slot is available again
        slots_after = len(zone.get_available_slots())
        self.assert_equal(slots_after, slots_before + 1, "3.2: Should restore slot availability")
        
        # Verify request state
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.CANCELLED, "3.3: Request state should be CANCELLED")
    
    # ==========================================
    # TEST 4: Rollback Operations (LIFO)
    # ==========================================
    def test_rollback_operations(self):
        """Test 4: Verify rollback undoes last k operations (Stack/LIFO)"""
        print("\n--- Test 4: Rollback Operations ---")
        self.setup()
        
        # Perform 3 allocations
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req1.request_id)
        
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req2.request_id)
        
        req3 = self.system.create_request('VEH_003', 'ZONE_B', auto_allocate=False)
        self.system.allocate_parking(req3.request_id)
        
        # Get zone availability before rollback
        zone_a = self.system.get_zone('ZONE_A')
        available_before = len(zone_a.get_available_slots())
        
        # Rollback last 2 operations (should undo req3 and req2)
        rollback_result = self.system.rollback_operations(2)
        
        self.assert_true(rollback_result['success'], "4.1: Rollback should succeed")
        self.assert_equal(rollback_result['rolled_back_count'], 2, "4.2: Should rollback 2 operations")
        
        # Verify req2 and req3 are back to REQUESTED state
        req2_after = self.system.get_request_by_id(req2.request_id)
        req3_after = self.system.get_request_by_id(req3.request_id)
        
        self.assert_equal(req2_after.state, RequestState.REQUESTED, "4.3: req2 should be REQUESTED after rollback")
        self.assert_equal(req3_after.state, RequestState.REQUESTED, "4.4: req3 should be REQUESTED after rollback")
        
        # Verify req1 is still ALLOCATED
        req1_after = self.system.get_request_by_id(req1.request_id)
        self.assert_equal(req1_after.state, RequestState.ALLOCATED, "4.5: req1 should still be ALLOCATED")
        
        # Verify slot availability restored
        available_after = len(zone_a.get_available_slots())
        self.assert_equal(available_after, available_before + 1, "4.6: Should restore 1 slot in ZONE_A")
    
    # ==========================================
    # TEST 5: Invalid State Transitions
    # ==========================================
    def test_invalid_state_transitions(self):
        """Test 5: Verify invalid state transitions are prevented"""
        print("\n--- Test 5: Invalid State Transitions ---")
        self.setup()
        
        # Create request in REQUESTED state
        request = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        
        # Try to occupy without allocating (REQUESTED → OCCUPIED is invalid)
        result = self.system.occupy_parking(request.request_id)
        self.assert_true(not result['success'], "5.1: Should prevent REQUESTED → OCCUPIED")
        
        # Allocate properly
        self.system.allocate_parking(request.request_id)
        
        # Try to release without occupying (ALLOCATED → RELEASED is invalid)
        result = self.system.release_parking(request.request_id)
        self.assert_true(not result['success'], "5.2: Should prevent ALLOCATED → RELEASED")
        
        # Occupy properly
        self.system.occupy_parking(request.request_id)
        
        # Try to cancel when occupied (OCCUPIED → CANCELLED is invalid)
        result = self.system.cancel_request(request.request_id)
        self.assert_true(not result['success'], "5.3: Should prevent OCCUPIED → CANCELLED")
        
        # Release properly
        result = self.system.release_parking(request.request_id)
        self.assert_true(result['success'], "5.4: Should allow OCCUPIED → RELEASED")
        
        # Verify request is in RELEASED state
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.RELEASED, "5.5: Final state should be RELEASED")
    
    # ==========================================
    # TEST 6: Analytics Correctness
    # ==========================================
    def test_analytics_correctness(self):
        """Test 6: Verify analytics calculations are correct"""
        print("\n--- Test 6: Analytics Correctness ---")
        self.setup()
        
        # Create complete lifecycle: allocate → occupy → release
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req1.request_id)
        self.system.occupy_parking(req1.request_id)
        self.system.release_parking(req1.request_id)
        
        # Create and cancel a request
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req2.request_id)
        self.system.cancel_request(req2.request_id)
        
        # Get analytics
        analytics = self.system.get_analytics()
        
        self.assert_equal(analytics['total_requests'], 2, "6.1: Total requests should be 2")
        self.assert_equal(analytics['completed_requests'], 1, "6.2: Completed requests should be 1")
        self.assert_equal(analytics['cancelled_requests'], 1, "6.3: Cancelled requests should be 1")
        self.assert_equal(analytics['completion_rate'], 50.0, "6.4: Completion rate should be 50%")
        self.assert_equal(analytics['cancellation_rate'], 50.0, "6.5: Cancellation rate should be 50%")
        
        # Verify zone utilization
        self.assert_true('zone_utilization' in analytics, "6.6: Should include zone utilization")
        self.assert_true('ZONE_A' in analytics['zone_utilization'], "6.7: Should have ZONE_A stats")
    
    # ==========================================
    # TEST 7: Analytics After Rollback
    # ==========================================
    def test_analytics_after_rollback(self):
        """Test 7: Verify analytics are correct after rollback operations"""
        print("\n--- Test 7: Analytics After Rollback ---")
        self.setup()
        
        # Allocate 2 requests
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req1.request_id)
        
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req2.request_id)
        
        # Rollback last allocation
        self.system.rollback_operations(1)
        
        # Verify req2 state after rollback
        req2_after = self.system.get_request_by_id(req2.request_id)
        self.assert_equal(req2_after.state, RequestState.REQUESTED, "7.1: req2 should be REQUESTED after rollback")
        
        # Check zone utilization after rollback
        zone = self.system.get_zone('ZONE_A')
        occupied = zone.get_occupied_slots()
        self.assert_equal(occupied, 1, "7.2: Should have 1 occupied slot after rollback")
        
        # Get analytics
        analytics = self.system.get_analytics()
        utilization = analytics['zone_utilization']['ZONE_A']['utilization_rate']
        self.assert_equal(utilization, 50.0, "7.3: ZONE_A utilization should be 50% (1/2)")
    
    # ==========================================
    # TEST 8: Queue Operations (FIFO)
    # ==========================================
    def test_queue_operations(self):
        """Test 8: Verify queue operates in FIFO order"""
        print("\n--- Test 8: Queue Operations (FIFO) ---")
        self.setup()
        
        # Create 3 requests without auto-allocate (add to queue)
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        req3 = self.system.create_request('VEH_003', 'ZONE_B', auto_allocate=False)
        
        # Add to queue
        self.system.add_to_queue(req1.request_id)
        self.system.add_to_queue(req2.request_id)
        self.system.add_to_queue(req3.request_id)
        
        # Check queue size
        queue_status = self.system.get_queue_status()
        self.assert_equal(queue_status['pending_count'], 3, "8.1: Queue should have 3 requests")
        
        # Process first request (should be req1 - FIFO)
        result = self.system.process_next_request()
        self.assert_equal(result['request_id'], req1.request_id, "8.2: Should process req1 first (FIFO)")
        
        # Process second request (should be req2)
        result = self.system.process_next_request()
        self.assert_equal(result['request_id'], req2.request_id, "8.3: Should process req2 second (FIFO)")
        
        # Check queue size after processing 2
        queue_status = self.system.get_queue_status()
        self.assert_equal(queue_status['pending_count'], 1, "8.4: Queue should have 1 request left")
    
    # ==========================================
    # TEST 9: Full Lifecycle Management
    # ==========================================
    def test_full_lifecycle(self):
        """Test 9: Test complete request lifecycle from creation to release"""
        print("\n--- Test 9: Full Lifecycle Management ---")
        self.setup()
        
        # Create request
        request = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.assert_equal(request.state, RequestState.REQUESTED, "9.1: Initial state should be REQUESTED")
        
        # Allocate
        result = self.system.allocate_parking(request.request_id)
        self.assert_true(result['success'], "9.2: Allocation should succeed")
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.ALLOCATED, "9.3: State should be ALLOCATED")
        
        # Occupy
        result = self.system.occupy_parking(request.request_id)
        self.assert_true(result['success'], "9.4: Occupation should succeed")
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.OCCUPIED, "9.5: State should be OCCUPIED")
        
        # Release
        result = self.system.release_parking(request.request_id)
        self.assert_true(result['success'], "9.6: Release should succeed")
        request = self.system.get_request_by_id(request.request_id)
        self.assert_equal(request.state, RequestState.RELEASED, "9.7: State should be RELEASED")
        
        # Verify state history
        self.assert_equal(len(request.state_history), 4, "9.8: Should have 4 states in history")
    
    # ==========================================
    # TEST 10: Zone Capacity Limits
    # ==========================================
    def test_zone_capacity_limits(self):
        """Test 10: Verify system handles zone capacity limits correctly"""
        print("\n--- Test 10: Zone Capacity Limits ---")
        self.setup()
        
        # ZONE_A has 2 slots, try to allocate 3 vehicles
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        result1 = self.system.allocate_parking(req1.request_id)
        self.assert_true(result1['success'], "10.1: First allocation should succeed")
        self.assert_equal(result1['zone_id'], 'ZONE_A', "10.2: Should allocate in ZONE_A")
        
        req2 = self.system.create_request('VEH_002', 'ZONE_A', auto_allocate=False)
        result2 = self.system.allocate_parking(req2.request_id)
        self.assert_true(result2['success'], "10.3: Second allocation should succeed")
        self.assert_equal(result2['zone_id'], 'ZONE_A', "10.4: Should allocate in ZONE_A")
        
        # Third should go to adjacent zone
        req3 = self.system.create_request('VEH_003', 'ZONE_A', auto_allocate=False)
        result3 = self.system.allocate_parking(req3.request_id)
        self.assert_true(result3['success'], "10.5: Third allocation should succeed")
        self.assert_true(result3['zone_id'] != 'ZONE_A', "10.6: Should allocate outside ZONE_A")
        self.assert_true(result3['is_cross_zone'], "10.7: Should be cross-zone allocation")
    
    # ==========================================
    # TEST 11: Multiple Rollback Operations
    # ==========================================
    def test_multiple_rollbacks(self):
        """Test 11: Test rolling back multiple operations sequentially"""
        print("\n--- Test 11: Multiple Rollback Operations ---")
        self.setup()
        
        # Create 4 requests and allocate
        requests = []
        for i in range(4):
            req = self.system.create_request(f'VEH_00{i+1}', 'ZONE_B', auto_allocate=False)
            self.system.allocate_parking(req.request_id)
            requests.append(req.request_id)
        
        # Rollback 2 operations
        result = self.system.rollback_operations(2)
        self.assert_equal(result['rolled_back_count'], 2, "11.1: Should rollback 2 operations")
        
        # Verify last 2 are REQUESTED
        req3 = self.system.get_request_by_id(requests[2])
        req4 = self.system.get_request_by_id(requests[3])
        self.assert_equal(req3.state, RequestState.REQUESTED, "11.2: req3 should be REQUESTED")
        self.assert_equal(req4.state, RequestState.REQUESTED, "11.3: req4 should be REQUESTED")
        
        # Rollback 1 more
        result = self.system.rollback_operations(1)
        self.assert_equal(result['rolled_back_count'], 1, "11.4: Should rollback 1 operation")
        
        # Verify req2 is REQUESTED, req1 is still ALLOCATED
        req2 = self.system.get_request_by_id(requests[1])
        req1 = self.system.get_request_by_id(requests[0])
        self.assert_equal(req2.state, RequestState.REQUESTED, "11.5: req2 should be REQUESTED")
        self.assert_equal(req1.state, RequestState.ALLOCATED, "11.6: req1 should still be ALLOCATED")
    
    # ==========================================
    # TEST 12: Mixed State Analytics
    # ==========================================
    def test_mixed_state_analytics(self):
        """Test 12: Verify analytics work with requests in various states"""
        print("\n--- Test 12: Mixed State Analytics ---")
        self.setup()
        
        # Create requests in different states
        # 1. Complete lifecycle (RELEASED)
        req1 = self.system.create_request('VEH_001', 'ZONE_A', auto_allocate=False)
        self.system.allocate_parking(req1.request_id)
        self.system.occupy_parking(req1.request_id)
        self.system.release_parking(req1.request_id)
        
        # 2. Cancelled after allocation
        req2 = self.system.create_request('VEH_002', 'ZONE_B', auto_allocate=False)
        self.system.allocate_parking(req2.request_id)
        self.system.cancel_request(req2.request_id)
        
        # 3. Still allocated
        req3 = self.system.create_request('VEH_003', 'ZONE_C', auto_allocate=False)
        self.system.allocate_parking(req3.request_id)
        
        # 4. Still occupied
        req4 = self.system.create_request('VEH_004', 'ZONE_C', auto_allocate=False)
        self.system.allocate_parking(req4.request_id)
        self.system.occupy_parking(req4.request_id)
        
        # Get analytics
        analytics = self.system.get_analytics()
        
        self.assert_equal(analytics['total_requests'], 2, "12.1: Should count completed/cancelled (2)")
        self.assert_equal(analytics['active_requests'], 2, "12.2: Should have 2 active requests")
        self.assert_equal(analytics['completed_requests'], 1, "12.3: Should have 1 completed")
        self.assert_equal(analytics['cancelled_requests'], 1, "12.4: Should have 1 cancelled")
        
        # Verify zone utilization includes all allocated slots
        zone_c_stats = analytics['zone_utilization']['ZONE_C']
        self.assert_equal(zone_c_stats['occupied_slots'], 2, "12.5: ZONE_C should have 2 occupied slots")
    
    # ==========================================
    # RUN ALL TESTS
    # ==========================================
    def run_all_tests(self):
        """Run all test cases"""
        print("="*70)
        print("SMART PARKING SYSTEM - COMPREHENSIVE TEST SUITE")
        print("Testing all PDF requirements:")
        print("1. Slot allocation correctness")
        print("2. Cross-zone allocation handling")
        print("3. Cancellation and rollback correctness")
        print("4. Invalid state transition detection")
        print("5. Analytics correctness after rollback")
        print("="*70)
        
        # Run all tests
        self.test_slot_allocation_correctness()
        self.test_cross_zone_allocation()
        self.test_cancellation_correctness()
        self.test_rollback_operations()
        self.test_invalid_state_transitions()
        self.test_analytics_correctness()
        self.test_analytics_after_rollback()
        self.test_queue_operations()
        self.test_full_lifecycle()
        self.test_zone_capacity_limits()
        self.test_multiple_rollbacks()
        self.test_mixed_state_analytics()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        total_tests = self.tests_passed + self.tests_failed
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/total_tests*100):.1f}%")
        print("="*70)
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is fully compliant with PDF requirements.")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please review the output above.")
        
        return self.tests_failed == 0


if __name__ == '__main__':
    """Run the test suite"""
    print("\n🧪 Starting Test Suite...\n")
    
    tester = TestParkingSystem()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
