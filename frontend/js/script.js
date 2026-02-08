// ============================================
// SMART PARKING SYSTEM - COMPLETE JAVASCRIPT
// With Rollback, State Machine, Live Updates, Analytics
// ============================================

const API_BASE = 'http://localhost:5000/api';

// Global State
let currentScreen = 'welcomeScreen';
let selectedVehicleType = null;
let selectedVehicleEmoji = '🚗';
let registeredVehicleId = null;
let selectedZoneId = null;
let selectedSpotId = null;
let currentRequestId = null;
let statusUpdateInterval = null;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🅿️ Smart Parking System Loaded');
    console.log('✅ Backend: http://localhost:5000');
    
    // Load initial data
    loadHeroStats();
    updateLivePanel();
    
    // Auto-refresh every 5 seconds
    setInterval(() => {
        loadHeroStats();
        updateLivePanel();
        updateStackSize();
    }, 5000);
});

// ============================================
// SCREEN NAVIGATION
// ============================================

function nextScreen(screenId) {
    // Hide current
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    
    // Show next
    document.getElementById(screenId).classList.add('active');
    currentScreen = screenId;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevScreen(screenId) {
    nextScreen(screenId);
}

// ============================================
// HERO STATS
// ============================================

async function loadHeroStats() {
    try {
        const response = await fetch(${API_BASE}/system/status);
        if (!response.ok) return;
        
        const data = await response.json();
        
        // Calculate available spots
        let totalAvailable = 0;
        if (data.zones) {
            Object.values(data.zones).forEach(zone => {
                totalAvailable += zone.available_slots || 0;
            });
        }
        
        document.getElementById('availableSpots').textContent = totalAvailable;
        document.getElementById('todayParked').textContent = data.total_requests || 0;
    } catch (error) {
        console.log('Backend not connected yet');
    }
}

// ============================================
// STEP 1: VEHICLE TYPE SELECTION
// ============================================

function selectVehicleType(type, emoji) {
    selectedVehicleType = type;
    selectedVehicleEmoji = emoji;
    
    showNotification(${emoji} ${type} selected, 'success');
    
    // Animate to next screen
    setTimeout(() => {
        nextScreen('registerScreen');
        document.getElementById('vehicleTypeDisplay').textContent = emoji;
    }, 500);
}

// ============================================
// STEP 2: VEHICLE REGISTRATION (ID CARD)
// ============================================

function updateIDCard() {
    const number = document.getElementById('vehicleNumber').value || '---';
    const name = document.getElementById('ownerName').value || '---';
    
    document.getElementById('previewNumber').textContent = number;
    document.getElementById('previewName').textContent = name;
}

async function submitRegistration() {
    const vehicleId = document.getElementById('vehicleNumber').value.trim();
    const ownerName = document.getElementById('ownerName').value.trim();
    const preferredZone = document.getElementById('preferredZone').value;
    
    if (!vehicleId || !ownerName || !preferredZone) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(${API_BASE}/vehicle/register, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                preferred_zone: preferredZone,
                vehicle_type: selectedVehicleType || 'Car'
            })
        });
        
        if (!response.ok) {
            // Vehicle might already exist, continue anyway
            console.log('Vehicle may already be registered');
        }
        
        registeredVehicleId = vehicleId;
        showNotification('✅ Vehicle registered!', 'success');
        
        setTimeout(() => {
            loadZones();
            nextScreen('zoneScreen');
            showLoading(false);
        }, 1000);
        
    } catch (error) {
        showLoading(false);
        showNotification('Registration failed', 'error');
    }
}

// ============================================
// STEP 3: ZONE SELECTION
// ============================================

async function loadZones() {
    try {
        const response = await fetch(${API_BASE}/zones);
        if (!response.ok) throw new Error('Failed to load zones');
        
        const data = await response.json();
        const zones = data.zones || [];
        
        const grid = document.getElementById('zoneGrid');
        grid.innerHTML = '';
        
        zones.forEach((zone, index) => {
            const available = zone.available_slots || 0;
            const total = zone.total_slots || 0;
            const isAvailable = available > 0;
            
            const card = document.createElement('div');
            card.className = 'zone-card';
            card.style.animationDelay = ${index * 0.1}s;
            card.onclick = () => selectZone(zone.zone_id, zone.zone_name);
            
            card.innerHTML = `
                <h3>${zone.zone_name}</h3>
                <p>${zone.zone_id}</p>
                <div class="zone-availability ${isAvailable ? 'available' : 'full'}">
                    ${available} / ${total} spots
                </div>
            `;
            
            grid.appendChild(card);
        });
        
    } catch (error) {
        showNotification('Failed to load zones', 'error');
    }
}

async function selectZone(zoneId, zoneName) {
    selectedZoneId = zoneId;
    
    showNotification(Zone selected: ${zoneName}, 'info');
    document.getElementById('selectedZoneName').textContent = zoneName;
    
    await loadParkingSpots(zoneId);
    nextScreen('spotScreen');
}

// ============================================
// STEP 4: PARKING SPOT SELECTION
// ============================================

async function loadParkingSpots(zoneId) {
    try {
        const response = await fetch(${API_BASE}/zones/${zoneId});
        if (!response.ok) throw new Error('Failed to load spots');
        
        const zone = await response.json();
        
        // Generate spots based on zone capacity
        const totalSlots = zone.total_slots || 20;
        const availableSlots = zone.available_slots || 10;
        
        const grid = document.getElementById('parkingGrid');
        grid.innerHTML = '';
        
        for (let i = 0; i < totalSlots; i++) {
            const isAvailable = i < availableSlots;
            const spotId = ${zoneId}_SLOT_${i + 1};
            
            const spot = document.createElement('div');
            spot.className = parking-spot ${isAvailable ? 'available' : 'occupied'};
            spot.dataset.spotId = spotId;
            spot.dataset.position = i;
            
            if (isAvailable) {
                spot.textContent = i + 1;
                spot.onclick = () => selectParkingSpot(spotId, i, isAvailable);
            } else {
                spot.textContent = selectedVehicleEmoji;
            }
            
            grid.appendChild(spot);
        }
        
    } catch (error) {
        showNotification('Failed to load parking spots', 'error');
    }
}

function selectParkingSpot(spotId, position, isAvailable) {
    if (!isAvailable) {
        showNotification('This spot is occupied', 'error');
        return;
    }
    
    // Deselect all
    document.querySelectorAll('.parking-spot').forEach(s => s.classList.remove('selected'));
    
    // Select this one
    const spot = document.querySelector([data-spot-id="${spotId}"]);
    spot.classList.add('selected');
    
    selectedSpotId = spotId;
    document.getElementById('confirmSpotBtn').disabled = false;
    
    // Animate vehicle to spot
    animateVehicleToSpot(position);
    
    showNotification('Spot selected!', 'success');
}

function animateVehicleToSpot(position) {
    const vehicle = document.getElementById('animatedVehicle');
    const spot = document.querySelector([data-position="${position}"]);
    if (!spot || !vehicle) return;
    
    const grid = document.getElementById('parkingGrid');
    const spotRect = spot.getBoundingClientRect();
    const gridRect = grid.getBoundingClientRect();
    
    const x = spotRect.left - gridRect.left + (spotRect.width / 2) - 24;
    const y = spotRect.top - gridRect.top + (spotRect.height / 2) - 24;
    
    vehicle.style.display = 'block';
    vehicle.style.left = '-100px';
    vehicle.style.top = ${y}px;
    
    document.getElementById('vehicleEmoji').textContent = selectedVehicleEmoji;
    
    setTimeout(() => {
        vehicle.style.left = ${x}px;
    }, 100);
}

// ============================================
// STEP 5: CONFIRM & CREATE REQUEST
// ============================================

async function confirmSpot() {
    if (!registeredVehicleId || !selectedZoneId) {
        showNotification('Session expired', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        // Create parking request
        const response = await fetch(${API_BASE}/request/create, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: registeredVehicleId,
                requested_zone: selectedZoneId,
                auto_allocate: true
            })
        });
        
        if (!response.ok) throw new Error('Failed to create request');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Failed');
        
        currentRequestId = data.request.request_id;
        
        // Display ticket
        displayTicket(data.request);
        
        // Start status monitoring
        startStatusMonitoring();
        
        showLoading(false);
        nextScreen('successScreen');
        showNotification('🎉 Parking confirmed!', 'success');
        
    } catch (error) {
        showLoading(false);
        showNotification('Failed to confirm parking', 'error');
    }
}

function displayTicket(request) {
    document.getElementById('ticketId').textContent = request.request_id || '---';
    document.getElementById('ticketVehicle').textContent = request.vehicle_id || '---';
    document.getElementById('ticketZone').textContent = request.allocated_zone || request.requested_zone || '---';
    document.getElementById('ticketSpot').textContent = request.allocated_slot || 'Pending';
    document.getElementById('ticketTime').textContent = new Date().toLocaleTimeString();
}

// ============================================
// STATE MACHINE & STATUS TRACKING
// ============================================

function startStatusMonitoring() {
    // Clear any existing interval
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    
    // Update immediately
    updateParkingStatus();
    
    // Update every 3 seconds
    statusUpdateInterval = setInterval(updateParkingStatus, 3000);
}

async function updateParkingStatus() {
    if (!currentRequestId) return;
    
    try {
        const response = await fetch(${API_BASE}/request/${currentRequestId});
        if (!response.ok) return;
        
        const request = await response.json();
        
        // Update state machine
        updateStateMachine(request.state);
        
        // Update status badge
        updateStatusDisplay(request);
        
        // Update action buttons
        updateActionButtons(request.state);
        
        // Update timer
        updateTimer(request);
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

function updateStateMachine(state) {
    const states = ['REQUESTED', 'ALLOCATED', 'OCCUPIED', 'RELEASED'];
    const currentIndex = states.indexOf(state);
    
    const steps = ['stepRequested', 'stepAllocated', 'stepOccupied', 'stepReleased'];
    
    steps.forEach((stepId, index) => {
        const step = document.getElementById(stepId);
        if (!step) return;
        
        step.classList.remove('completed', 'active');
        
        if (index < currentIndex) {
            step.classList.add('completed');
        } else if (index === currentIndex) {
            step.classList.add('active');
        }
    });
}

function updateStatusDisplay(request) {
    const statusBadge = document.getElementById('statusBadge');
    const stateLabels = {
        'REQUESTED': 'RESERVED',
        'ALLOCATED': 'CONFIRMED',
        'OCCUPIED': 'PARKED',
        'RELEASED': 'COMPLETE',
        'CANCELLED': 'CANCELLED'
    };
    
    statusBadge.textContent = stateLabels[request.state] || request.state;
}

function updateActionButtons(state) {
    const btnOccupy = document.getElementById('btnOccupy');
    const btnRelease = document.getElementById('btnRelease');
    
    if (!btnOccupy || !btnRelease) return;
    
    btnOccupy.classList.add('hidden');
    btnRelease.classList.add('hidden');
    
    if (state === 'ALLOCATED') {
        btnOccupy.classList.remove('hidden');
    } else if (state === 'OCCUPIED') {
        btnRelease.classList.remove('hidden');
    }
}

function updateTimer(request) {
    const timerElement = document.getElementById('statusTimer');
    if (!timerElement || !request.allocation_time) return;
    
    const startTime = new Date(request.allocation_time);
    const now = new Date();
    const minutes = Math.floor((now - startTime) / 60000);
    
    timerElement.textContent = ${minutes} min;
}

// ============================================
// STATE TRANSITIONS
// ============================================

async function markOccupied() {
    if (!currentRequestId) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(${API_BASE}/request/${currentRequestId}/occupy, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed');
        
        showNotification('✅ Marked as parked!', 'success');
        updateParkingStatus();
        
    } catch (error) {
        showNotification('Failed to update status', 'error');
    } finally {
        showLoading(false);
    }
}

async function markReleased() {
    if (!currentRequestId) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(${API_BASE}/request/${currentRequestId}/release, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed');
        
        showNotification('🎉 Thank you for using Smart Parking!', 'success');
        
        // Stop status monitoring
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
        
        // Wait then show analytics
        setTimeout(() => {
            loadAnalytics();
            nextScreen('analyticsScreen');
        }, 2000);
        
    } catch (error) {
        showNotification('Failed to release parking', 'error');
    } finally {
        showLoading(false);
    }
}

async function cancelParking() {
    if (!confirm('Are you sure you want to cancel?')) return;
    
    if (!currentRequestId) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(${API_BASE}/request/${currentRequestId}/cancel, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed');
        
        showNotification('Reservation cancelled', 'info');
        
        setTimeout(() => {
            startNewBooking();
        }, 1500);
        
    } catch (error) {
        showNotification('Failed to cancel', 'error');
    } finally {
        showLoading(false);
    }
}

// ============================================
// STEP 6: ANALYTICS DASHBOARD
// ============================================

async function loadAnalytics() {
    try {
        const response = await fetch(${API_BASE}/analytics);
        if (!response.ok) throw new Error('Failed to load analytics');
        
        const data = await response.json();
        
        // Update cards
        document.getElementById('analyticsTotal').textContent = data.total_requests || 0;
        document.getElementById('analyticsCompleted').textContent = data.completed_requests || 0;
        document.getElementById('analyticsCancelled').textContent = data.cancelled_requests || 0;
        document.getElementById('analyticsAvgTime').textContent = data.average_parking_duration_minutes?.toFixed(1) || '0';
        
        // Load zone utilization
        loadZoneUtilization(data.zone_utilization || {});
        
        // Load live requests
        loadLiveRequestsTable();
        
    } catch (error) {
        showNotification('Failed to load analytics', 'error');
    }
}

function loadZoneUtilization(zoneData) {
    const container = document.getElementById('utilizationBars');
    container.innerHTML = '';
    
    Object.entries(zoneData).forEach(([zoneId, zone]) => {
        const utilization = zone.utilization_rate || 0;
        
        const barDiv = document.createElement('div');
        barDiv.className = 'utilization-bar';
        barDiv.innerHTML = `
            <div class="bar-label">
                <span>${zone.zone_name || zoneId}</span>
                <span>${utilization.toFixed(1)}%</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${utilization}%">
                    ${zone.occupied_slots} / ${zone.total_slots}
                </div>
            </div>
        `;
        
        container.appendChild(barDiv);
    });
}

async function loadLiveRequestsTable() {
    try {
        const response = await fetch(${API_BASE}/requests);
        if (!response.ok) throw new Error('Failed');
        
        const data = await response.json();
        const requests = data.requests || [];
        
        // Filter active requests only
        const activeRequests = requests.filter(r => 
            !['RELEASED', 'CANCELLED'].includes(r.state)
        );
        
        const container = document.getElementById('requestsTable');
        
        if (activeRequests.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-muted)">No active requests</p>';
            return;
        }
        
        container.innerHTML = '';
        
        activeRequests.forEach(request => {
            const item = document.createElement('div');
            item.className = 'request-item';
            item.innerHTML = `
                <div class="request-info">
                    <strong>${request.request_id}</strong>
                    <small>${request.vehicle_id} • ${request.requested_zone}</small>
                </div>
                <span class="request-state-badge ${request.state}">
                    ${request.state}
                </span>
            `;
            container.appendChild(item);
        });
        
    } catch (error) {
        console.error('Failed to load requests:', error);
    }
}

// ============================================
// ROLLBACK FUNCTIONALITY
// ============================================

function toggleRollbackMenu() {
    const menu = document.getElementById('rollbackMenu');
    menu.classList.toggle('hidden');
    updateStackSize();
}

async function updateStackSize() {
    try {
        const response = await fetch(${API_BASE}/system/status);
        if (!response.ok) return;
        
        const data = await response.json();
        const stackSize = data.rollback_history_size || 0;
        
        document.getElementById('stackSizeDisplay').textContent = stackSize;
    } catch (error) {
        console.log('Failed to get stack size');
    }
}

async function performRollback() {
    const k = parseInt(document.getElementById('rollbackCount').value) || 1;
    
    if (k < 1 || k > 10) {
        showNotification('Enter 1-10 operations', 'error');
        return;
    }
    
    if (!confirm(Rollback last ${k} operation(s)?)) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(${API_BASE}/rollback, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ k })
        });
        
        if (!response.ok) throw new Error('Rollback failed');
        
        const data = await response.json();
        
        showNotification(✅ Rolled back ${data.rolled_back_count} operations, 'success');
        toggleRollbackMenu();
        
        // Refresh current data
        if (currentScreen === 'analyticsScreen') {
            loadAnalytics();
        }
        
    } catch (error) {
        showNotification('Rollback failed', 'error');
    } finally {
        showLoading(false);
    }
}

async function viewStackHistory() {
    try {
        const response = await fetch(${API_BASE}/rollback/history?n=20);
        if (!response.ok) throw new Error('Failed');
        
        const data = await response.json();
        const history = data.history || [];
        
        const modal = document.getElementById('stackModal');
        const content = document.getElementById('stackHistoryContent');
        
        if (history.length === 0) {
            content.innerHTML = '<p style="text-align:center;color:var(--text-muted)">Stack is empty</p>';
        } else {
            content.innerHTML = '';
            
            history.forEach((op, index) => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <strong>${index === 0 ? 'TOP → ' : ''}${op.type.toUpperCase()}</strong>
                    <div><small>Request: ${op.request_id}</small></div>
                    <div><small>Vehicle: ${op.vehicle_id}</small></div>
                    <div><small>Slot: ${op.slot_id || 'N/A'}</small></div>
                `;
                content.appendChild(item);
            });
        }
        
        modal.classList.remove('hidden');
        
    } catch (error) {
        showNotification('Failed to load history', 'error');
    }
}

function closeStackModal() {
    document.getElementById('stackModal').classList.add('hidden');
}

// ============================================
// LIVE UPDATES PANEL
// ============================================

function toggleLivePanel() {
    const content = document.getElementById('liveContent');
    const arrow = document.querySelector('.toggle-arrow');
    
    content.style.display = content.style.display === 'none' ? 'flex' : 'none';
    arrow.textContent = content.style.display === 'none' ? '▼' : '▲';
}

async function updateLivePanel() {
    try {
        const response = await fetch(${API_BASE}/system/status);
        if (!response.ok) return;
        
        const data = await response.json();
        
        document.getElementById('liveActive').textContent = data.active_requests || 0;
        document.getElementById('liveQueue').textContent = data.pending_queue_size || 0;
        
        // Get completed count from analytics
        const analyticsResponse = await fetch(${API_BASE}/analytics);
        if (analyticsResponse.ok) {
            const analytics = await analyticsResponse.json();
            document.getElementById('liveCompleted').textContent = analytics.completed_requests || 0;
        }
    } catch (error) {
        console.log('Live panel update failed');
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const textSpan = notification.querySelector('.notification-text');
    const iconSpan = notification.querySelector('.notification-icon');
    
    // Set icon based on type
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    iconSpan.textContent = icons[type] || 'ℹ️';
    textSpan.textContent = message;
    
    notification.className = notification show ${type};
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

function startNewBooking() {
    // Reset state
    currentRequestId = null;
    registeredVehicleId = null;
    selectedZoneId = null;
    selectedSpotId = null;
    selectedVehicleType = null;
    
    // Clear interval
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    
    // Reset forms
    document.getElementById('vehicleNumber').value = '';
    document.getElementById('ownerName').value = '';
    document.getElementById('preferredZone').value = '';
    
    // Go to welcome
    nextScreen('welcomeScreen');
    
    showNotification('Ready for new booking', 'success');
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', (e) => {
    // ESC to close modals
    if (e.key === 'Escape') {
        closeStackModal();
        const rollbackMenu = document.getElementById('rollbackMenu');
        if (!rollbackMenu.classList.contains('hidden')) {
            toggleRollbackMenu();
        }
    }
    
    // R for rollback menu
    if (e.key === 'r' || e.key === 'R') {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            toggleRollbackMenu();
        }
    }
});

// ============================================
// CONNECTION TEST (for instructor demo)
// ============================================

async function testBackendConnection() {
    console.log('🧪 Testing Backend Connection...');
    console.log('📡 API Base:', API_BASE);
    
    try {
        const response = await fetch(${API_BASE}/system/status);
        const data = await response.json();
        
        console.log('✅ Backend Connected!');
        console.log('📊 System Status:', data);
        console.log('🏢 Total Zones:', data.total_zones);
        console.log('🚗 Total Vehicles:', data.total_vehicles);
        console.log('📝 Total Requests:', data.total_requests);
        console.log('⚡ Active Requests:', data.active_requests);
        console.log('📚 Stack Size:', data.rollback_history_size);
        
        return true;
    } catch (error) {
        console.error('❌ Backend Connection Failed:', error);
        return false;
    }
}

// Run connection test on load
setTimeout(testBackendConnection, 1000);