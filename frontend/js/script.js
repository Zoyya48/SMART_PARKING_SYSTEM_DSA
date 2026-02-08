// API Configuration
const API_BASE = 'http://localhost:5000/api';

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = notification show ${type};
    setTimeout(() => notification.classList.remove('show'), 3000);
}

function showSection(sectionId) {
    document.querySelectorAll('.step-section, .hero-section').forEach(s => s.classList.add('hidden'));
    document.getElementById(sectionId).classList.remove('hidden');
}

// Hero - Load Stats
async function loadHeroStats() {
    try {
        const response = await fetch(${API_BASE}/system/status);
        if (!response.ok) return;
        const data = await response.json();
        document.getElementById('availableSpots').textContent = data.total_available_slots || 0;
        document.getElementById('todayParked').textContent = data.total_requests || 0;
    } catch (error) {
        console.log('Backend not running');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadHeroStats();
    setInterval(loadHeroStats, 10000);
});

// Step 1: Vehicle Entry
function startBooking() {
    showSection('vehicleSection');
}

async function submitVehicle() {
    const vehicleId = document.getElementById('vehicleNumber').value.trim();
    
    if (!vehicleId) {
        showNotification('Please enter your vehicle number', 'error');
        return;
    }
    
    try {
        const response = await fetch(${API_BASE}/vehicle/register, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                preferred_zone: 'ZONE_A'
            })
        });
        
        if (!response.ok) throw new Error('Registration failed');
        
        sessionStorage.setItem('vehicleId', vehicleId);
        await loadZones();
        showSection('zoneSection');
        
    } catch (error) {
        showNotification('Failed to register vehicle', 'error');
    }
}

// Step 2: Zone Selection
async function loadZones() {
    try {
        const response = await fetch(${API_BASE}/zones);
        if (!response.ok) throw new Error('Failed to load zones');
        
        const zones = await response.json();
        const grid = document.getElementById('zoneGrid');
        
        grid.innerHTML = zones.map(zone => {
            const available = zone.available_slots || 0;
            const total = zone.total_slots || 0;
            const isAvailable = available > 0;
            
            return `
                <div class="zone-card" onclick="selectZone('${zone.id}', '${zone.name}')">
                    <h3>${zone.name}</h3>
                    <p>${zone.location || 'Parking Area'}</p>
                    <div class="zone-availability ${isAvailable ? 'available' : 'full'}">
                        ${available} / ${total} spots
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        showNotification('Failed to load zones', 'error');
    }
}

async function selectZone(zoneId, zoneName) {
    sessionStorage.setItem('selectedZone', zoneId);
    document.getElementById('selectedZoneName').textContent = zoneName;
    await loadParkingSpots(zoneId);
    showSection('spotSection');
}

// Step 3: Spot Selection
let selectedSpotId = null;

async function loadParkingSpots(zoneId) {
    try {
        const response = await fetch(${API_BASE}/zones);
        if (!response.ok) throw new Error('Failed to load spots');
        
        const zones = await response.json();
        const zone = zones.find(z => z.id === zoneId);
        
        if (!zone || !zone.parking_areas) throw new Error('Zone not found');
        
        let allSlots = [];
        zone.parking_areas.forEach(area => {
            if (area.slots) {
                allSlots = allSlots.concat(area.slots.map(slot => ({
                    ...slot,
                    area_id: area.id
                })));
            }
        });
        
        const grid = document.getElementById('parkingGrid');
        grid.innerHTML = allSlots.map((slot, index) => `
            <div class="parking-spot ${slot.is_available ? 'available' : 'occupied'}"
                 data-slot-id="${slot.id}"
                 data-position="${index}"
                 onclick="selectSpot('${slot.id}', ${index}, ${slot.is_available})">
                ${slot.is_available ? (index + 1) : '🚗'}
            </div>
        `).join('');
        
    } catch (error) {
        showNotification('Failed to load parking spots', 'error');
    }
}

function selectSpot(spotId, position, isAvailable) {
    if (!isAvailable) {
        showNotification('This spot is occupied', 'error');
        return;
    }
    
    document.querySelectorAll('.parking-spot').forEach(s => s.classList.remove('selected'));
    document.querySelector([data-slot-id="${spotId}"]).classList.add('selected');
    
    selectedSpotId = spotId;
    sessionStorage.setItem('selectedSpot', spotId);
    document.getElementById('confirmBtn').disabled = false;
    
    animateCarToSpot(position);
}

function animateCarToSpot(position) {
    const car = document.getElementById('animatedCar');
    const spot = document.querySelector([data-position="${position}"]);
    if (!spot) return;
    
    const spotRect = spot.getBoundingClientRect();
    const gridRect = document.getElementById('parkingGrid').getBoundingClientRect();
    
    const x = spotRect.left - gridRect.left + (spotRect.width / 2) - 16;
    const y = spotRect.top - gridRect.top + (spotRect.height / 2) - 16;
    
    car.style.display = 'block';
    car.style.left = '-50px';
    car.style.top = ${y}px;
    
    setTimeout(() => {
        car.style.left = ${x}px;
    }, 100);
}

// Step 4: Confirm & Create Request
async function confirmSpot() {
    const vehicleId = sessionStorage.getItem('vehicleId');
    const zoneId = sessionStorage.getItem('selectedZone');
    
    if (!vehicleId || !zoneId) {
        showNotification('Session expired', 'error');
        location.reload();
        return;
    }
    
    try {
        const response = await fetch(${API_BASE}/request/create, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                requested_zone: zoneId,
                auto_allocate: true
            })
        });
        
        if (!response.ok) throw new Error('Failed to create request');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Failed');
        
        sessionStorage.setItem('requestId', data.request.id);
        displayConfirmation(data.request);
        showSection('confirmationSection');
        
    } catch (error) {
        showNotification('Failed to confirm spot', 'error');
    }
}

function displayConfirmation(request) {
    document.getElementById('ticketVehicle').textContent = request.vehicle_id || '-';
    document.getElementById('ticketZone').textContent = request.allocated_zone || request.requested_zone || '-';
    document.getElementById('ticketSpot').textContent = request.allocated_slot || 'Pending';
}

// Step 5: Tracking
function goToTracking() {
    loadParkingStatus();
    showSection('trackingSection');
}

async function loadParkingStatus() {
    const requestId = sessionStorage.getItem('requestId');
    if (!requestId) {
        showNotification('No active parking session', 'error');
        return;
    }
    
    try {
        const response = await fetch(${API_BASE}/requests);
        if (!response.ok) throw new Error('Failed to load status');
        
        const requests = await response.json();
        const request = requests.find(r => r.id === requestId);
        if (!request) throw new Error('Request not found');
        
        updateJourneyTracker(request.state);
        document.getElementById('currentStatus').textContent = getStateLabel(request.state);
        document.getElementById('statusVehicle').textContent = request.vehicle_id;
        document.getElementById('statusZone').textContent = request.allocated_zone || request.requested_zone;
        
        if (request.allocation_time) {
            const minutes = Math.floor((Date.now() - new Date(request.allocation_time)) / 60000);
            document.getElementById('statusDuration').textContent = ${minutes} min;
        }
        
        showActionButtons(request.state);
        
    } catch (error) {
        showNotification('Failed to load status', 'error');
    }
}

function updateJourneyTracker(state) {
    const steps = {
        'REQUESTED': ['stepReserved'],
        'ALLOCATED': ['stepReserved', 'stepConfirmed'],
        'OCCUPIED': ['stepReserved', 'stepConfirmed', 'stepParked'],
        'RELEASED': ['stepReserved', 'stepConfirmed', 'stepParked', 'stepComplete']
    };
    
    const activeSteps = steps[state] || [];
    
    ['stepReserved', 'stepConfirmed', 'stepParked', 'stepComplete'].forEach(id => {
        document.getElementById(id).classList.remove('completed', 'active');
    });
    
    activeSteps.forEach((stepId, index) => {
        const element = document.getElementById(stepId);
        if (index < activeSteps.length - 1) {
            element.classList.add('completed');
        } else {
            element.classList.add('active');
        }
    });
}

function getStateLabel(state) {
    const labels = {
        'REQUESTED': 'Reserved',
        'ALLOCATED': 'Confirmed',
        'OCCUPIED': 'Parked',
        'RELEASED': 'Complete',
        'CANCELLED': 'Cancelled'
    };
    return labels[state] || state;
}

function showActionButtons(state) {
    const btnOccupy = document.getElementById('btnOccupy');
    const btnRelease = document.getElementById('btnRelease');
    const btnCancel = document.getElementById('btnCancel');
    
    btnOccupy.style.display = 'none';
    btnRelease.style.display = 'none';
    btnCancel.style.display = 'none';
    
    if (state === 'REQUESTED' || state === 'ALLOCATED') {
        btnOccupy.style.display = 'block';
        btnCancel.style.display = 'block';
    } else if (state === 'OCCUPIED') {
        btnRelease.style.display = 'block';
    }
}

// Action Handlers
async function markOccupied() {
    const requestId = sessionStorage.getItem('requestId');
    try {
        const response = await fetch(${API_BASE}/request/${requestId}/occupy, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed');
        showNotification('Marked as parked!', 'success');
        loadParkingStatus();
    } catch (error) {
        showNotification('Failed to update status', 'error');
    }
}

async function markReleased() {
    const requestId = sessionStorage.getItem('requestId');
    try {
        const response = await fetch(${API_BASE}/request/${requestId}/release, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed');
        showNotification('Thank you for using Smart Parking!', 'success');
        setTimeout(() => {
            sessionStorage.clear();
            location.reload();
        }, 2000);
    } catch (error) {
        showNotification('Failed to update status', 'error');
    }
}

async function cancelParking() {
    if (!confirm('Are you sure you want to cancel?')) return;
    
    const requestId = sessionStorage.getItem('requestId');
    try {
        const response = await fetch(${API_BASE}/request/${requestId}/cancel, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed');
        showNotification('Reservation cancelled', 'info');
        setTimeout(() => {
            sessionStorage.clear();
            location.reload();
        }, 2000);
    } catch (error) {
        showNotification('Failed to cancel', 'error');
    }
}

// Auto-refresh status
setInterval(() => {
    const trackingSection = document.getElementById('trackingSection');
    if (trackingSection && !trackingSection.classList.contains('hidden')) {
        loadParkingStatus();
    }
}, 5000);