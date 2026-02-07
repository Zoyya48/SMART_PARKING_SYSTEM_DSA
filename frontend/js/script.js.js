/**
 * Smart Parking System - Admin Dashboard JavaScript
 * Handles all API interactions and UI updates
 */

const API_BASE = 'http://localhost:5000/api';

// ==================================
// INITIALIZATION
// ==================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🅿️ Smart Parking Admin Dashboard Loaded');
    console.log('✓ Custom Data Structures: Array, LinkedList, Stack, Queue, HashTable, AdjacencyList');
    
    // Initial load
    loadSystemData();
    
    // Auto-refresh every 5 seconds
    setInterval(loadSystemData, 5000);
});

// ==================================
// DATA LOADING
// ==================================

async function loadSystemData() {
    await loadSystemStatus();
    await loadZones();
    await loadRequests();
    await loadQueue();
    await loadAnalytics();
}

async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/system/status`);
        const data = await response.json();
        
        // Update header stats
        document.getElementById('activeRequests').textContent = data.active_requests || 0;
        document.getElementById('queueSize').textContent = data.pending_queue_size || 0;
        document.getElementById('stackSize').textContent = data.rollback_history_size || 0;
    } catch (error) {
        console.error('Error loading system status:', error);
    }
}

async function loadZones() {
    try {
        const response = await fetch(`${API_BASE}/zones`);
        const data = await response.json();
        
        const zonesGrid = document.getElementById('zonesGrid');
        zonesGrid.innerHTML = '';
        
        data.zones.forEach(zone => {
            const zoneCard = createZoneCard(zone);
            zonesGrid.appendChild(zoneCard);
        });
    } catch (error) {
        console.error('Error loading zones:', error);
    }
}

async function loadRequests() {
    try {
        const response = await fetch(`${API_BASE}/requests`);
        const data = await response.json();
        
        const requestsContainer = document.getElementById('liveRequests');
        
        // Filter active requests
        const activeRequests = data.requests.filter(r => 
            !['RELEASED', 'CANCELLED'].includes(r.state)
        );
        
        if (activeRequests.length === 0) {
            requestsContainer.innerHTML = '<div class="empty-state">No active requests</div>';
            return;
        }
        
        requestsContainer.innerHTML = '';
        activeRequests.forEach(request => {
            const requestCard = createRequestCard(request);
            requestsContainer.appendChild(requestCard);
            
            // Highlight current state in state machine
            highlightState(request.state);
        });
    } catch (error) {
        console.error('Error loading requests:', error);
    }
}

async function loadQueue() {
    try {
        const response = await fetch(`${API_BASE}/queue/status`);
        const data = await response.json();
        
        const queueItems = document.getElementById('queueItems');
        
        if (data.pending_count === 0) {
            queueItems.innerHTML = '<div class="empty-state">Queue is empty</div>';
            return;
        }
        
        queueItems.innerHTML = '';
        data.pending_requests.forEach(requestId => {
            const queueItem = document.createElement('div');
            queueItem.className = 'queue-item';
            queueItem.textContent = requestId;
            queueItems.appendChild(queueItem);
        });
    } catch (error) {
        console.error('Error loading queue:', error);
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/analytics`);
        const data = await response.json();
        
        const analyticsGrid = document.getElementById('analyticsGrid');
        analyticsGrid.innerHTML = '';
        
        // Create analytics cards
        const metrics = [
            { label: 'Total Requests', value: data.total_requests },
            { label: 'Completed', value: data.completed_requests },
            { label: 'Cancelled', value: data.cancelled_requests },
            { label: 'Active', value: data.active_requests },
            { label: 'Avg Duration (min)', value: data.average_parking_duration_minutes.toFixed(1) },
            { label: 'Completion Rate', value: data.completion_rate + '%' },
        ];
        
        metrics.forEach(metric => {
            const card = createAnalyticsCard(metric.label, metric.value);
            analyticsGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ==================================
// UI CREATORS
// ==================================

function createZoneCard(zone) {
    const card = document.createElement('div');
    card.className = 'zone-card';
    
    card.innerHTML = `
        <div class="zone-header">
            <div class="zone-name">${zone.zone_name}</div>
            <div class="zone-utilization">${zone.utilization_rate}%</div>
        </div>
        <div class="zone-stats">
            <div class="zone-stat">
                <div class="zone-stat-value">${zone.total_slots}</div>
                <div class="zone-stat-label">Total</div>
            </div>
            <div class="zone-stat">
                <div class="zone-stat-value">${zone.occupied_slots}</div>
                <div class="zone-stat-label">Occupied</div>
            </div>
            <div class="zone-stat">
                <div class="zone-stat-value">${zone.available_slots}</div>
                <div class="zone-stat-label">Available</div>
            </div>
        </div>
        <div class="zone-progress">
            <div class="zone-progress-bar" style="width: ${zone.utilization_rate}%"></div>
        </div>
        <div class="zone-adjacent">
            Adjacent: ${zone.adjacent_zones.length > 0 ? zone.adjacent_zones.join(', ') : 'None'}
        </div>
    `;
    
    return card;
}

function createRequestCard(request) {
    const card = document.createElement('div');
    card.className = 'request-card';
    
    card.innerHTML = `
        <div class="request-state ${request.state}">${request.state}</div>
        <div class="request-info">
            <div class="request-id">${request.request_id}</div>
            <div class="request-detail">Vehicle: ${request.vehicle_id}</div>
            <div class="request-detail">Zone: ${request.requested_zone}${request.allocated_zone !== request.requested_zone && request.allocated_zone ? ' → ' + request.allocated_zone : ''}</div>
            ${request.allocated_slot ? `<div class="request-detail">Slot: ${request.allocated_slot}</div>` : ''}
        </div>
        <div class="request-actions">
            ${request.state === 'REQUESTED' ? `<button class="btn-secondary" onclick="allocateParking('${request.request_id}')">Allocate</button>` : ''}
            ${request.state === 'ALLOCATED' ? `<button class="btn-secondary" onclick="occupyParking('${request.request_id}')">Occupy</button>` : ''}
            ${request.state === 'OCCUPIED' ? `<button class="btn-success" onclick="releaseParking('${request.request_id}')">Release</button>` : ''}
            ${['REQUESTED', 'ALLOCATED'].includes(request.state) ? `<button class="btn-danger" onclick="cancelRequest('${request.request_id}')">Cancel</button>` : ''}
        </div>
    `;
    
    return card;
}

function createAnalyticsCard(label, value) {
    const card = document.createElement('div');
    card.className = 'analytics-card';
    
    card.innerHTML = `
        <div class="analytics-value">${value}</div>
        <div class="analytics-label">${label}</div>
    `;
    
    return card;
}

function highlightState(state) {
    // Remove all active states
    document.querySelectorAll('.state-node').forEach(node => {
        node.classList.remove('active');
    });
    
    // Add active class to current state
    const stateNode = document.querySelector(`[data-state="${state}"]`);
    if (stateNode) {
        stateNode.classList.add('active');
    }
}

// ==================================
// API ACTIONS
// ==================================

async function registerVehicle() {
    const vehicleId = document.getElementById('vehicleId').value.trim();
    const preferredZone = document.getElementById('preferredZone').value;
    
    if (!vehicleId || !preferredZone) {
        showNotification('Please fill all fields', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/vehicle/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                preferred_zone: preferredZone,
                vehicle_type: 'Car'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Vehicle ${vehicleId} registered successfully`);
            document.getElementById('vehicleId').value = '';
            document.getElementById('preferredZone').value = '';
        } else {
            showNotification(data.error || 'Registration failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function createRequest() {
    const vehicleId = document.getElementById('requestVehicleId').value.trim();
    const requestedZone = document.getElementById('requestZone').value;
    const autoAllocate = document.getElementById('autoAllocate').checked;
    
    if (!vehicleId || !requestedZone) {
        showNotification('Please fill all fields', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                requested_zone: requestedZone,
                auto_allocate: autoAllocate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Request ${data.request.request_id} created`);
            document.getElementById('requestVehicleId').value = '';
            loadSystemData();
            
            // If auto-allocate, immediately allocate
            if (autoAllocate) {
                setTimeout(() => allocateParking(data.request.request_id), 500);
            }
        } else {
            showNotification(data.error || 'Request creation failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function allocateParking(requestId) {
    if (!requestId) {
        requestId = document.getElementById('actionRequestId').value.trim();
    }
    
    if (!requestId) {
        showNotification('Please enter request ID', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/${requestId}/allocate`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Allocated: ${data.slot_id} in ${data.zone_id}${data.is_cross_zone ? ' (Cross-zone)' : ''}`);
            loadSystemData();
        } else {
            showNotification(data.error || 'Allocation failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function occupyParking(requestId) {
    if (!requestId) {
        requestId = document.getElementById('actionRequestId').value.trim();
    }
    
    if (!requestId) {
        showNotification('Please enter request ID', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/${requestId}/occupy`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Request ${requestId} occupied`);
            loadSystemData();
        } else {
            showNotification(data.error || 'Occupy failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function releaseParking(requestId) {
    if (!requestId) {
        requestId = document.getElementById('actionRequestId').value.trim();
    }
    
    if (!requestId) {
        showNotification('Please enter request ID', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/${requestId}/release`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Request ${requestId} released (${data.duration_seconds}s)`);
            loadSystemData();
        } else {
            showNotification(data.error || 'Release failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function cancelRequest(requestId) {
    if (!requestId) {
        requestId = document.getElementById('actionRequestId').value.trim();
    }
    
    if (!requestId) {
        showNotification('Please enter request ID', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/request/${requestId}/cancel`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Request ${requestId} cancelled`);
            loadSystemData();
        } else {
            showNotification(data.error || 'Cancel failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function processQueue() {
    try {
        const response = await fetch(`${API_BASE}/queue/process`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Processed: ${data.request_id}`);
            loadSystemData();
        } else {
            showNotification(data.error || 'No requests in queue', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function performRollback() {
    const k = document.getElementById('rollbackK').value;
    
    if (!k || k < 1) {
        showNotification('Please enter number of operations', true);
        return;
    }
    
    if (!confirm(`Rollback last ${k} operation(s)?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/rollback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ k: parseInt(k) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Rolled back ${data.rolled_back_count} operation(s)`);
            loadSystemData();
        } else {
            showNotification('Rollback failed', true);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, true);
    }
}

async function viewStack() {
    try {
        const response = await fetch(`${API_BASE}/rollback/history?n=20`);
        const data = await response.json();
        
        const modal = document.getElementById('stackModal');
        const content = document.getElementById('stackContent');
        
        if (data.history.length === 0) {
            content.innerHTML = '<div class="empty-state">Stack is empty</div>';
        } else {
            content.innerHTML = '';
            data.history.forEach((operation, index) => {
                const item = document.createElement('div');
                item.className = 'stack-item';
                item.innerHTML = `
                    <div><strong>${index === 0 ? 'TOP → ' : ''}${operation.type.toUpperCase()}</strong></div>
                    <div>Request: ${operation.request_id}</div>
                    <div>Vehicle: ${operation.vehicle_id}</div>
                    <div>Slot: ${operation.slot_id || 'N/A'}</div>
                `;
                content.appendChild(item);
            });
        }
        
        modal.classList.add('show');
    } catch (error) {
        showNotification('Error loading stack: ' + error.message, true);
    }
}

function closeModal() {
    document.getElementById('stackModal').classList.remove('show');
}

// ==================================
// NOTIFICATIONS
// ==================================

function showNotification(message, isError = false) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.toggle('error', isError);
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// ==================================
// KEYBOARD SHORTCUTS
// ==================================

document.addEventListener('keydown', (e) => {
    // ESC to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
});
