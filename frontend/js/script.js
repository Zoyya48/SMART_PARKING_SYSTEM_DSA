/* ========================================
   SMART PARKING SYSTEM - FRONTEND LOGIC
   Backend Integration with Flask API
   ======================================== */

// Configuration
const API_BASE = 'http://localhost:5000/api';

// Zone mapping: UI names → Backend IDs
const ZONE_MAPPING = {
    'Defence': 'ZONE_A',
    'Model Town': 'ZONE_B',
    'Gulberg': 'ZONE_C'
};

// Reverse mapping: Backend IDs → UI names
const ZONE_NAMES = {
    'ZONE_A': 'Defence',
    'ZONE_B': 'Model Town',
    'ZONE_C': 'Gulberg'
};

// Pricing per zone (hardcoded)
const ZONE_PRICING = {
    'Defence': 100,
    'Model Town': 80,
    'Gulberg': 60
};

// State Management
let appState = {
    vehicleType: null,
    vehicleId: null,
    selectedZone: null,
    selectedZoneBackendId: null,
    requestId: null,
    allocatedSlot: null,
    allocatedSlotId: null,
    currentScreen: 'welcome',
    allZones: [],
    availableSlots: []
};

/* ========================================
   SCREEN NAVIGATION
   ======================================== */

function goToScreen(screenName) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show target screen
    const targetScreen = document.getElementById(`screen-${screenName}`);
    if (targetScreen) {
        targetScreen.classList.add('active');
        appState.currentScreen = screenName;
        
        // Execute screen-specific logic
        if (screenName === 'zone-selection') {
            loadZones();
        }
    }
}

/* ========================================
   STEP 1: SELECT VEHICLE TYPE
   ======================================== */

function selectVehicleType(type) {
    appState.vehicleType = type;
    
    // Update display on next screen
    document.getElementById('selectedVehicleType').textContent = type;
    
    // Animate selection
    const cards = document.querySelectorAll('.vehicle-card');
    cards.forEach(card => {
        if (card.textContent.includes(type)) {
            card.style.transform = 'scale(1.1)';
            card.style.borderColor = 'rgba(255, 255, 255, 0.6)';
            setTimeout(() => {
                goToScreen('vehicle-details');
            }, 300);
        }
    });
}

/* ========================================
   STEP 2: REGISTER VEHICLE
   ======================================== */

async function registerVehicle() {
    const vehicleId = document.getElementById('vehicleId').value.trim().toUpperCase();
    
    // Validation
    if (!vehicleId) {
        showNotification('Please enter vehicle registration number', 'error');
        return;
    }
    
    if (vehicleId.length < 5) {
        showNotification('Registration number too short', 'error');
        return;
    }
    
    // Save to state
    appState.vehicleId = vehicleId;
    
    // Update info displays
    document.getElementById('vehicleInfoType').textContent = appState.vehicleType;
    document.getElementById('vehicleInfoId').textContent = vehicleId;
    
    // Show loading
    showLoading();
    
    try {
        // Register vehicle with backend
        const response = await fetch(`${API_BASE}/vehicle/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                vehicle_type: appState.vehicleType,
                preferred_zone: 'ZONE_A' // Default preference
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success || response.ok) {
            showNotification('Vehicle registered successfully!', 'success');
            setTimeout(() => {
                goToScreen('zone-selection');
            }, 800);
        } else {
            // If vehicle already registered, continue anyway
            if (data.error && data.error.includes('already registered')) {
                showNotification('Vehicle already registered, continuing...', 'success');
                setTimeout(() => {
                    goToScreen('zone-selection');
                }, 800);
            } else {
                showNotification(data.error || 'Registration failed', 'error');
            }
        }
    } catch (error) {
        hideLoading();
        console.error('Registration error:', error);
        showNotification('Connection error. Please check if backend is running.', 'error');
    }
}

/* ========================================
   STEP 3: LOAD ZONES
   ======================================== */

async function loadZones() {
    const container = document.getElementById('zonesContainer');
    container.innerHTML = '<div class="loading-spinner">Loading zones...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/zones`);
        const data = await response.json();
        
        if (data.zones && data.zones.length > 0) {
            appState.allZones = data.zones;
            displayZones(data.zones);
        } else {
            container.innerHTML = '<div class="loading-spinner">No zones available</div>';
        }
    } catch (error) {
        console.error('Load zones error:', error);
        container.innerHTML = '<div class="loading-spinner">Failed to load zones. Check backend connection.</div>';
    }
}

function displayZones(zones) {
    const container = document.getElementById('zonesContainer');
    container.innerHTML = '';
    
    // Filter only the zones we want to show
    const displayZones = ['ZONE_A', 'ZONE_B', 'ZONE_C'];
    
    displayZones.forEach(zoneId => {
        const zone = zones.find(z => z.zone_id === zoneId);
        if (!zone) return;
        
        const uiName = ZONE_NAMES[zoneId];
        const pricing = ZONE_PRICING[uiName];
        const available = zone.available_slots || 0;
        
        const zoneCard = document.createElement('div');
        zoneCard.className = 'zone-card';
        zoneCard.onclick = () => selectZone(uiName, zoneId, zone);
        
        zoneCard.innerHTML = `
            <div class="zone-header">
                <h3 class="zone-name">${uiName}</h3>
                <span class="zone-availability">${available} spots</span>
            </div>
            <div class="zone-details">
                <span class="zone-location">📍 ${zone.zone_name}</span>
                <span class="zone-price">Rs. ${pricing}/hr</span>
            </div>
        `;
        
        container.appendChild(zoneCard);
    });
}

/* ========================================
   STEP 4: SELECT ZONE & CREATE REQUEST
   ======================================== */

async function selectZone(uiName, backendId, zoneData) {
    appState.selectedZone = uiName;
    appState.selectedZoneBackendId = backendId;
    
    // Update display
    document.getElementById('zoneTitleCard').innerHTML = `<h3>${uiName} Parking Area</h3>`;
    
    // Show loading
    showLoading();
    
    try {
        // Create parking request
        const requestResponse = await fetch(`${API_BASE}/request/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: appState.vehicleId,
                requested_zone: backendId,
                auto_allocate: false // We'll allocate manually after slot selection
            })
        });
        
        const requestData = await requestResponse.json();
        
        if (requestData.success && requestData.request) {
            appState.requestId = requestData.request.request_id;
            
            // Load available slots for this zone
            await loadSlots(backendId);
            
            hideLoading();
            showNotification(`${uiName} selected!`, 'success');
            
            setTimeout(() => {
                goToScreen('slot-selection');
            }, 500);
        } else {
            hideLoading();
            showNotification('Failed to create request', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Zone selection error:', error);
        showNotification('Connection error', 'error');
    }
}

/* ========================================
   STEP 5: LOAD & DISPLAY SLOTS
   ======================================== */

async function loadSlots(zoneId) {
    const zone = appState.allZones.find(z => z.zone_id === zoneId);
    if (!zone) return;
    
    // Get all parking areas in this zone
    try {
        const response = await fetch(`${API_BASE}/zones/${zoneId}`);
        const zoneDetails = await response.json();
        
        // For simplicity, create a grid of slots based on available count
        // In reality, you'd get actual slot IDs from backend
        const totalSlots = zoneDetails.total_slots || 10;
        const availableCount = zoneDetails.available_slots || 0;
        
        displaySlots(totalSlots, availableCount, zoneId);
    } catch (error) {
        console.error('Load slots error:', error);
        // Fallback: show generic slots
        displaySlots(10, 5, zoneId);
    }
}

function displaySlots(total, availableCount, zoneId) {
    const container = document.getElementById('slotsGrid');
    container.innerHTML = '';
    
    appState.availableSlots = [];
    
    // Create slot cards
    for (let i = 1; i <= total; i++) {
        const isAvailable = i <= availableCount;
        const slotId = `${zoneId}_SLOT_${i}`;
        
        if (isAvailable) {
            appState.availableSlots.push(slotId);
        }
        
        const slotCard = document.createElement('div');
        slotCard.className = `slot-card ${isAvailable ? 'available' : 'occupied'}`;
        
        if (isAvailable) {
            slotCard.onclick = () => selectSlot(slotId, i);
        }
        
        slotCard.innerHTML = `
            <div class="slot-icon">${isAvailable ? '🚗' : '🚫'}</div>
            <div class="slot-number">${i}</div>
            <div class="slot-status">${isAvailable ? 'Available' : 'Occupied'}</div>
        `;
        
        container.appendChild(slotCard);
    }
}

/* ========================================
   STEP 6: SELECT SLOT & ALLOCATE
   ======================================== */

async function selectSlot(slotId, slotNumber) {
    appState.allocatedSlotId = slotId;
    appState.allocatedSlot = slotNumber;
    
    // Show parking animation
    goToScreen('parking-animation');
    
    try {
        // Allocate the parking request
        const allocateResponse = await fetch(`${API_BASE}/request/${appState.requestId}/allocate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const allocateData = await allocateResponse.json();
        
        if (allocateData.success) {
            // Occupy the slot
            await new Promise(resolve => setTimeout(resolve, 2000)); // Animation time
            
            const occupyResponse = await fetch(`${API_BASE}/request/${appState.requestId}/occupy`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const occupyData = await occupyResponse.json();
            
            if (occupyData.success) {
                showConfirmation();
            } else {
                showNotification('Failed to occupy slot', 'error');
                goToScreen('slot-selection');
            }
        } else {
            showNotification('Failed to allocate slot', 'error');
            goToScreen('slot-selection');
        }
    } catch (error) {
        console.error('Slot allocation error:', error);
        showNotification('Connection error', 'error');
        goToScreen('slot-selection');
    }
}

/* ========================================
   STEP 7: SHOW CONFIRMATION
   ======================================== */

function showConfirmation() {
    // Generate ticket ID
    const ticketId = `PRK-${appState.vehicleId}-${Date.now().toString().slice(-6)}`;
    
    // Get current time
    const now = new Date();
    const timeString = now.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
    
    // Update ticket display
    document.getElementById('ticketId').textContent = ticketId;
    document.getElementById('ticketVehicleType').textContent = appState.vehicleType;
    document.getElementById('ticketRegistration').textContent = appState.vehicleId;
    document.getElementById('ticketZone').textContent = appState.selectedZone;
    document.getElementById('ticketSlot').textContent = `Slot ${appState.allocatedSlot}`;
    document.getElementById('ticketTime').textContent = timeString;
    
    // Show confirmation screen
    goToScreen('confirmation');
}

/* ========================================
   LEAVE PARKING (RELEASE)
   ======================================== */

function leaveParkingConfirm() {
    const modal = document.getElementById('modal-leave-parking');
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('modal-leave-parking');
    modal.classList.remove('active');
}

async function leaveParking() {
    closeModal();
    
    // Show leaving animation
    goToScreen('leave-animation');
    
    try {
        // Release parking via backend
        const response = await fetch(`${API_BASE}/request/${appState.requestId}/release`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        await new Promise(resolve => setTimeout(resolve, 2000)); // Animation time
        
        if (data.success) {
            // Update leave success screen
            document.getElementById('leaveVehicleId').textContent = appState.vehicleId;
            document.getElementById('leaveZone').textContent = appState.selectedZone;
            document.getElementById('leaveSlot').textContent = `Slot ${appState.allocatedSlot}`;
            
            goToScreen('leave-success');
            showNotification('Parking released successfully!', 'success');
        } else {
            showNotification('Failed to release parking', 'error');
            goToScreen('confirmation');
        }
    } catch (error) {
        console.error('Leave parking error:', error);
        showNotification('Connection error', 'error');
        goToScreen('confirmation');
    }
}

/* ========================================
   RESET APP
   ======================================== */

function resetApp() {
    // Reset state
    appState = {
        vehicleType: null,
        vehicleId: null,
        selectedZone: null,
        selectedZoneBackendId: null,
        requestId: null,
        allocatedSlot: null,
        allocatedSlotId: null,
        currentScreen: 'welcome',
        allZones: [],
        availableSlots: []
    };
    
    // Clear inputs
    document.getElementById('vehicleId').value = '';
    
    // Go to welcome screen
    goToScreen('welcome');
}

/* ========================================
   UTILITY FUNCTIONS
   ======================================== */

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
}

/* ========================================
   INITIALIZATION
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {
    console.log('🅿️ Smart Parking System Initialized');
    console.log('Backend API:', API_BASE);
    
    // Test backend connection
    fetch(`${API_BASE}/system/status`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Backend connected:', data);
        })
        .catch(error => {
            console.error('❌ Backend connection failed:', error);
            showNotification('Backend not connected. Please start Flask server.', 'error');
        });
    
    // Make sure welcome screen is active
    goToScreen('welcome');
});

/* ========================================
   KEYBOARD SHORTCUTS
   ======================================== */

document.addEventListener('keydown', (e) => {
    // Enter key on vehicle ID input
    if (e.key === 'Enter' && appState.currentScreen === 'vehicle-details') {
        registerVehicle();
    }
});
