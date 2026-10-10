/**
 * LIPTIS USA SALs App - Core Application Engine
 * Interactive Multi-Flight Event & Travel Management Platform
 */

// Global State Store
const state = {
  activeTab: 'itinerary',
  selectedFlightId: null,
  eventData: null,
  flights: [],
  itinerary: null,
  sections: {},
  contacts: [],
  isLoading: true,
  offline: !navigator.onLine,
  
  // Administrator State
  isAdminLoggedIn: false,
  adminToken: localStorage.getItem('liptis_admin_token') || null,
  adminUser: null,
  adminViewTab: 'events',
  allEvents: [],
  selectedAdminEventId: null,
  adminEventDetail: null,
  conflicts: [],
  isPreviewMode: false,
  hasUnpublishedChanges: false
};

// Toast Notifications Helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none;border:none;cursor:pointer;font-weight:bold;margin-left:8px;" onclick="this.parentElement.remove()">×</button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// API Utilities
async function fetchAPI(endpoint, options = {}) {
  const headers = options.headers || {};
  if (state.adminToken) {
    headers['Authorization'] = `Bearer ${state.adminToken}`;
  }
  headers['Content-Type'] = 'application/json';

  try {
    const res = await fetch(endpoint, { ...options, headers });
    if (res.status === 401 && endpoint.startsWith('/api/admin/')) {
      logoutAdmin();
      showToast('Administrator session expired. Please log in again.', 'warning');
      throw new Error('Unauthorized');
    }
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'An error occurred while processing your request.');
    }
    return data;
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}

// Application Initialization
document.addEventListener('DOMContentLoaded', async () => {
  initNetworkListeners();
  initLocalClock();
  setupPWA();
  
  // Check admin session if token exists
  if (state.adminToken) {
    try {
      state.adminUser = await fetchAPI('/api/admin/me');
      state.isAdminLoggedIn = true;
    } catch {
      localStorage.removeItem('liptis_admin_token');
      state.adminToken = null;
    }
  }

  await loadParticipantEvent();
  renderApp();
});

// Network Listeners
function initNetworkListeners() {
  window.addEventListener('online', () => {
    state.offline = false;
    showToast('Network restored. Synchronized with server.', 'success');
    renderApp();
  });
  window.addEventListener('offline', () => {
    state.offline = true;
    showToast('Offline mode active. Using cached trip itinerary.', 'warning');
    renderApp();
  });
}

// PWA Setup
function setupPWA() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
      console.log('SW registration note:', err);
    });
  }
}

// Real-Time Local Clock (KSA Time GMT+3)
function initLocalClock() {
  setInterval(() => {
    const clockEl = document.getElementById('live-ksa-clock');
    if (!clockEl) return;
    
    // KSA is UTC+3
    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const ksaTime = new Date(utc + (3600000 * 3));
    
    const timeString = ksaTime.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    clockEl.innerText = `${timeString} AST (GMT+3)`;
  }, 1000);
}

// Load Active Published Event for Participants
async function loadParticipantEvent() {
  state.isLoading = true;
  try {
    const activeSummary = await fetchAPI('/api/public/events/active');
    const details = await fetchAPI(`/api/public/events/${activeSummary.id}`);
    
    state.eventData = details.event;
    state.flights = details.flights;
    state.sections = details.sections;
    state.contacts = details.contacts;
    state.selectedAdminEventId = details.event.id;
    
    // Set default selected flight if not chosen yet
    if (!state.selectedFlightId && state.flights.length > 0) {
      state.selectedFlightId = state.flights[0].id;
    }
    
    await loadFlightItinerary(state.selectedFlightId);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    state.isLoading = false;
  }
}

// Load Itinerary for Specific Flight Group
async function loadFlightItinerary(flightGroupId) {
  if (!state.eventData || !flightGroupId) return;
  try {
    const data = await fetchAPI(`/api/public/events/${state.eventData.id}/itinerary?flight_group_id=${flightGroupId}`);
    state.itinerary = data;
    state.selectedFlightId = flightGroupId;
  } catch (err) {
    showToast('Failed to load flight itinerary.', 'error');
  }
}

// Main Render Function
function renderApp() {
  const root = document.getElementById('app-root');
  if (!root) return;

  if (state.isLoading) {
    root.innerHTML = `
      <div style="min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem;">
        <div style="width:48px;height:48px;border:4px solid #e2e8f0;border-top-color:#c8102e;border-radius:50%;animation:spin 1s linear infinite;"></div>
        <p style="font-weight:600;color:#64748b;">Loading LIPTIS USA Travel Details...</p>
      </div>
      <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
    `;
    return;
  }

  // If in Administrator Mode (and not previewing)
  if (state.isAdminLoggedIn && !state.isPreviewMode) {
    root.innerHTML = renderAdminDashboard();
    attachAdminEvents();
    return;
  }

  // Participant / Viewer View (or Admin Preview)
  root.innerHTML = renderParticipantView();
  attachParticipantEvents();
}

// ================= PARTICIPANT VIEW RENDERER =================

function renderParticipantView() {
  const event = state.eventData || {};
  const selectedFlight = state.flights.find(f => f.id === state.selectedFlightId) || state.flights[0] || {};
  const welcomeSec = state.sections['welcome_letter']?.content || {};

  return `
    ${state.isPreviewMode ? `
      <div class="admin-banner" style="background:#b91c1c;">
        <div><strong>ADMIN PREVIEW MODE</strong> — Viewing event as participant sees it.</div>
        <button class="btn-secondary" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="exitPreviewMode()">Exit Preview</button>
      </div>
    ` : ''}

    ${state.offline ? `
      <div style="background:#fef3c7;color:#92400e;padding:0.5rem;text-align:center;font-size:0.85rem;font-weight:600;">
        ⚠️ You are currently offline. Viewing saved trip information.
      </div>
    ` : ''}

    <!-- Official PDF Header Ribbons -->
    <div style="background:#ffffff;border-bottom:1px solid #e2e8f0;padding:1rem 1rem 0 1rem;text-align:center;">
      <div class="pdf-welcome-pill">
        <span>🕋</span>
        <span>${welcomeSec.banner_text || 'Welcome to Saudi Arabia'}</span>
      </div>
    </div>
    <div class="pdf-ribbon-bar">
      ${welcomeSec.dates || event.date_display || '15-18 October 2026'}, at ${welcomeSec.hotels || event.destination || 'Rotana Jabal Omar Hotel, Mecca & Peninsula Worth Hotel Madinah'}
    </div>

    <!-- Print-Only Official Document Header -->
    <div class="print-header">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h2 style="color:#c8102e;font-size:1.4rem;font-weight:800;">LIPTIS USA — Official Event Itinerary</h2>
          <p style="font-weight:700;">${event.title || 'Exclusive Event for Eminent Physicians'}</p>
          <p style="font-size:0.9rem;color:#475569;">${event.destination}</p>
        </div>
        <div style="text-align:right;">
          <p style="font-weight:700;color:#c8102e;">Flight: ${selectedFlight.outbound_flight_number || 'N/A'}</p>
          <p style="font-size:0.85rem;">Dates: ${event.date_display}</p>
        </div>
      </div>
    </div>

    <div style="max-width:1200px;margin:1.5rem auto;padding:0 1rem;width:100%;">
      
      <!-- Welcome Card from PDF Page 3 -->
      <div class="hero-card">
        <div class="hero-body">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
              <span style="font-size:0.8rem;font-weight:700;color:#c8102e;text-transform:uppercase;letter-spacing:0.05em;">LIPTIS USA Exclusive Delegation</span>
              <h1 class="hero-title">${event.title || 'Exclusive Event for Eminent Physicians'}</h1>
              <p style="font-size:0.95rem;color:#475569;margin-top:0.35rem;max-width:800px;line-height:1.6;">
                <strong>${welcomeSec.recipient || 'Dear Doctor,'}</strong> ${welcomeSec.body || 'It is our pleasure to welcome you to LIPTIS exclusive event for the eminent physicians being held in Mecca.'}
              </p>
            </div>
            <div style="display:flex;gap:0.5rem;" class="btn-print">
              <button class="btn-secondary" onclick="window.print()" title="Print or save as PDF">
                <span>🖨️</span> Print / Save PDF
              </button>
            </div>
          </div>

          <div class="hero-meta">
            <div class="hero-meta-item">
              <span>📅</span> <strong>${event.date_display}</strong>
            </div>
            <div class="hero-meta-item">
              <span>📍</span> <strong>${event.destination}</strong>
            </div>
            <div class="hero-meta-item">
              <span>✈️</span> Selected: <strong>${selectedFlight.airline} (${selectedFlight.outbound_flight_number})</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs (Faithfully organizing all 15 PDF topics) -->
      <div class="nav-tabs">
        <button class="nav-tab-btn ${state.activeTab === 'itinerary' ? 'active' : ''}" onclick="switchTab('itinerary')">
          <span>🕒</span> Itinerary & Flights
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'umrah' ? 'active' : ''}" onclick="switchTab('umrah')">
          <span>🕋</span> مناسك العمرة (Umrah Guide)
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'logistics' ? 'active' : ''}" onclick="switchTab('logistics')">
          <span>🏨</span> Hotel & Airport Details
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'attractions' ? 'active' : ''}" onclick="switchTab('attractions')">
          <span>🕌</span> Attractions & Haram
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'contacts' ? 'active' : ''}" onclick="switchTab('contacts')">
          <span>📞</span> Guest Care Contacts (${state.contacts.length})
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'travel-info' ? 'active' : ''}" onclick="switchTab('travel-info')">
          <span>🌤️</span> Weather, Currency & Plugs
        </button>
        <button class="nav-tab-btn ${state.activeTab === 'vat-refund' ? 'active' : ''}" onclick="switchTab('vat-refund')">
          <span>🏷️</span> VAT Tax Refund
        </button>
      </div>

      <!-- TAB 1: ITINERARY & FLIGHT SELECTION (CORE MANDATORY FEATURE) -->
      ${state.activeTab === 'itinerary' ? renderItineraryTab(selectedFlight) : ''}

      <!-- TAB 2: UMRAH RITUALS (PDF Page 2) -->
      ${state.activeTab === 'umrah' ? renderUmrahTab() : ''}

      <!-- TAB 3: HOTEL & LOGISTICS (PDF Page 3 & 4) -->
      ${state.activeTab === 'logistics' ? renderLogisticsTab() : ''}

      <!-- TAB 4: ATTRACTIONS & DISTANCE TO HARAM (PDF Page 4) -->
      ${state.activeTab === 'attractions' ? renderAttractionsTab() : ''}

      <!-- TAB 5: GUEST CARE CONTACTS (PDF Page 5) -->
      ${state.activeTab === 'contacts' ? renderContactsTab() : ''}

      <!-- TAB 6: TRAVEL INFO (Weather, Time, Currency, Plugs - PDF Page 5) -->
      ${state.activeTab === 'travel-info' ? renderTravelInfoTab() : ''}

      <!-- TAB 7: VAT TAX REFUND (PDF Page 8) -->
      ${state.activeTab === 'vat-refund' ? renderVatRefundTab() : ''}

    </div>

    <!-- Official PDF Brand Products Footer (Pages 3, 4, 5, 6, 7, 8) -->
    ${renderProductFooter()}
  `;
}

// Tab 1: Itinerary & Flight Selection
function renderItineraryTab(selectedFlight) {
  const datesObj = state.itinerary?.dates || {};
  const dateKeys = Object.keys(datesObj).sort();

  return `
    <!-- Mandatory Multi-Flight Selection Section -->
    <div class="flight-selector-container">
      <div class="flight-selector-title">
        <span>✈️</span>
        <span>Select Your Flight (تحديد موعد وتفاصيل رحلتك)</span>
      </div>
      <div class="flight-selector-subtitle">
        Your personalized itinerary, airport transfer, and hotel check-in times adapt automatically to your selected flight group.
      </div>

      <div class="flight-cards-grid">
        ${state.flights.map((fg, idx) => `
          <div class="flight-card ${fg.id === state.selectedFlightId ? 'selected' : ''}" onclick="selectFlight('${fg.id}')">
            ${fg.id === state.selectedFlightId ? '<div class="flight-card-badge">Selected Itinerary</div>' : ''}
            <div class="flight-card-name">${fg.name}</div>
            
            <div style="font-size:0.85rem;color:#475569;margin-bottom:0.4rem;">
              <strong>${fg.airline} ${fg.outbound_flight_number}</strong> — Direct Flight
            </div>

            <div style="display:flex;align-items:center;justify-content:space-between;font-size:0.9rem;margin-top:0.4rem;">
              <div>
                <div style="font-weight:700;color:#0f172a;">${fg.departure_time}</div>
                <div style="font-size:0.75rem;color:#64748b;">Cairo (CAI)</div>
              </div>
              <div style="font-size:0.8rem;color:#c8102e;font-weight:600;padding:0 0.5rem;">✈️ 2h 25m ➔</div>
              <div style="text-align:right;">
                <div style="font-weight:700;color:#0f172a;">${fg.arrival_time}</div>
                <div style="font-size:0.75rem;color:#64748b;">Jeddah (JED)</div>
              </div>
            </div>

            ${fg.return_flight_number ? `
              <div class="flight-details-row">
                <span style="font-size:0.75rem;color:#64748b;">Return: ${fg.return_departure_date || '18 Oct'}</span>
                <span class="flight-route-pill">${fg.return_flight_number} (${fg.return_departure_time})</span>
              </div>
            ` : ''}

            ${fg.notes ? `
              <div style="font-size:0.75rem;color:#b45309;background:#fef3c7;padding:0.25rem 0.5rem;border-radius:4px;margin-top:0.5rem;">
                📌 ${fg.notes}
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Active Flight Banner Notification -->
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:0.75rem 1rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
      <div style="font-size:0.875rem;color:#1e40af;">
        <strong>Currently Displaying:</strong> Itinerary for <strong>${selectedFlight.name || 'Selected Flight'}</strong>. 
        Airport transfers and schedule times are synchronized.
      </div>
      <div style="display:flex;gap:0.5rem;">
        <span class="timeline-tag tag-flight-group">Flight-Specific Schedule</span>
        <span class="timeline-tag tag-shared">Shared Program</span>
      </div>
    </div>

    <!-- Timeline Entries Grouped by Date -->
    ${dateKeys.length === 0 ? `
      <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:2.5rem;text-align:center;color:#64748b;">
        <p style="font-size:1.1rem;font-weight:600;">No itinerary items configured for this flight yet.</p>
      </div>
    ` : dateKeys.map(dateStr => {
      const dayEntries = datesObj[dateStr] || [];
      // Format nice day name
      const dateObj = new Date(dateStr);
      const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });

      return `
        <div class="itinerary-day-card">
          <div class="itinerary-day-header">
            <span>📅 ${dayName}</span>
            <span style="font-size:0.8rem;background:rgba(255,255,255,0.2);padding:0.2rem 0.6rem;border-radius:9999px;">
              ${dayEntries.length} Activities
            </span>
          </div>

          <ul class="timeline-list">
            ${dayEntries.map(entry => `
              <li class="timeline-item ${entry.is_shared ? 'shared' : ''}">
                <div class="timeline-item-dot"></div>
                
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.25rem;">
                  <span class="timeline-time-badge">
                    ⏰ ${entry.start_time}${entry.end_time ? ` – ${entry.end_time}` : ''}
                  </span>

                  <div>
                    ${entry.is_shared 
                      ? `<span class="timeline-tag tag-shared">🌐 Shared Activity</span>` 
                      : `<span class="timeline-tag tag-flight-group">✈️ Group Specific (${selectedFlight.outbound_flight_number})</span>`
                    }
                    <span class="timeline-tag tag-${entry.category}">${entry.category.toUpperCase()}</span>
                  </div>
                </div>

                <div class="timeline-title">${entry.title}</div>

                ${entry.description ? `<div class="timeline-desc">${entry.description}</div>` : ''}

                <div style="display:flex;flex-wrap:wrap;gap:0.75rem;font-size:0.8rem;color:#475569;margin-top:0.35rem;">
                  ${entry.location ? `<div>📍 <strong>Location:</strong> ${entry.location}</div>` : ''}
                  ${entry.meeting_point ? `<div>🚩 <strong>Meeting Point:</strong> ${entry.meeting_point}</div>` : ''}
                  ${entry.transportation_notes ? `<div>🚌 <strong>Transport:</strong> ${entry.transportation_notes}</div>` : ''}
                  ${entry.special_instructions ? `<div>⚠️ <strong>Note:</strong> ${entry.special_instructions}</div>` : ''}
                </div>
              </li>
            `).join('')}
          </ul>
        </div>
      `;
    }).join('')}
  `;
}

// Tab 2: Umrah Rituals (PDF Page 2)
function renderUmrahTab() {
  const umrah = state.sections['umrah_rituals']?.content || {};
  const youtubeUrl = umrah.youtube_url || 'https://www.youtube.com/watch?v=IUjFKJGa9Jw';

  return `
    <div class="info-card" style="text-align:center;padding:2rem 1.5rem;">
      <div class="section-ribbon-header">مناسك العمرة والمعلومات الهامة</div>
      
      <h2 style="font-size:1.5rem;margin:1rem 0;color:#0f172a;direction:rtl;">
        ${umrah.title_ar || 'لمعرفة مناسك العمرة ومعلومات هامة عنها'}
      </h2>

      <p style="font-size:1.05rem;color:#475569;margin-bottom:1.5rem;direction:rtl;">
        ${umrah.instruction_ar || 'يرجى مسح رمز الاستجابة السريعة (QR Code) أو الضغط على الرابط أسفل الصورة'}
      </p>

      <!-- Interactive QR Code SVG Box -->
      <div style="display:inline-block;background:#ffffff;padding:1.5rem;border:2px solid #e2e8f0;border-radius:16px;box-shadow:var(--shadow-md);margin-bottom:1.5rem;">
        <div style="font-size:0.75rem;font-weight:700;color:#64748b;margin-bottom:0.75rem;">SCAN WITH SMARTPHONE CAMERA</div>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(youtubeUrl)}" alt="Umrah Guide QR Code" style="width:180px;height:180px;display:block;margin:0 auto;" />
        <div style="font-size:0.75rem;color:#94a3b8;margin-top:0.75rem;">Official LIPTIS Umrah Video Guide</div>
      </div>

      <div>
        <a href="${youtubeUrl}" target="_blank" rel="noopener noreferrer" class="btn-primary" style="font-size:1rem;padding:0.75rem 1.75rem;text-decoration:none;">
          <span>▶️</span> شاهد فيديو مناسك العمرة على YouTube
        </a>
      </div>

      <div style="margin-top:1.5rem;font-size:0.85rem;color:#64748b;">
        Direct link: <a href="${youtubeUrl}" target="_blank" style="color:#c8102e;word-break:break-all;">${youtubeUrl}</a>
      </div>
    </div>
  `;
}

// Tab 3: Hotel & Logistics (PDF Page 3 & 4)
function renderLogisticsTab() {
  const arrival = state.sections['airport_arrival']?.content || {};
  const hotel = state.sections['hotel_details']?.content || {};
  const mecca = hotel.mecca_hotel || {};
  const madinah = hotel.madinah_hotel || {};
  const finance = state.sections['finance_policy']?.content || {};

  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:1.5rem;">
      
      <!-- Airport Arrival Guide (PDF Page 3) -->
      <div class="info-card">
        <div class="section-ribbon-header">Arrival at King Abdulaziz International Airport</div>
        
        <p style="font-size:0.95rem;color:#334155;line-height:1.6;margin-bottom:1rem;">
          ${arrival.instructions || 'Delegate is expected to arrive at King Abdulaziz International Airport, Jeddah.'}
        </p>

        <div style="background:#eff6ff;border-left:4px solid #1e40af;padding:0.75rem 1rem;border-radius:4px;margin-bottom:1rem;font-size:0.875rem;">
          <strong>Meet & Assist:</strong> A representative holding a <strong>${arrival.sign_label || 'LIPTIS welcome sign'}</strong> will be waiting at the arrival hall to assist with the transfer to the hotel in Mecca. Please make yourselves known to this representative.
        </div>

        <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:0.75rem;border-radius:8px;font-size:0.875rem;">
          ⏱️ <strong>Transfer Time:</strong> ${arrival.transfer_time || 'Approximately 90 minutes by bus to Rotana Jabal Omar Hotel.'}
        </div>
      </div>

      <!-- Mecca Hotel Details (PDF Page 3) -->
      <div class="info-card">
        <div class="section-ribbon-header">Hotel Details: ${mecca.name || 'Rotana Jabal Omar Hotel'}</div>
        
        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.8rem;color:#64748b;">Address:</div>
          <div style="font-weight:600;color:#0f172a;">${mecca.address || 'Jarham District 3045, Jarham Northern 1196978, Mecca'}</div>
        </div>

        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.8rem;color:#64748b;">Phone:</div>
          <div style="font-weight:600;color:#c8102e;">${mecca.phone || '+966 12 553 8400'}</div>
        </div>

        <div style="font-size:0.8rem;color:#64748b;margin-bottom:0.4rem;">Most Popular Facilities:</div>
        <div style="display:flex;flex-wrap:wrap;gap:0.35rem;">
          ${(mecca.facilities || []).map(f => `
            <span style="background:#f1f5f9;color:#334155;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.75rem;font-weight:600;">
              ✓ ${f}
            </span>
          `).join('')}
        </div>

        <div style="margin-top:1rem;">
          <a href="https://maps.google.com/?q=Rotana+Jabal+Omar+Hotel+Makkah" target="_blank" class="btn-secondary" style="font-size:0.8rem;width:100%;justify-content:center;text-decoration:none;">
            📍 Open Mecca Hotel in Google Maps
          </a>
        </div>
      </div>

      <!-- Madinah Hotel Details (PDF Page 7) -->
      <div class="info-card">
        <div class="section-ribbon-header">Hotel Details: ${madinah.name || 'Peninsula Worth Hotel'}</div>
        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.8rem;color:#64748b;">City & Location:</div>
          <div style="font-weight:600;color:#0f172a;">${madinah.address || 'Central Northern Area, Al-Madinah Al-Munawwarah'}</div>
        </div>
        <div style="margin-bottom:0.75rem;">
          <div style="font-size:0.8rem;color:#64748b;">Dining Facility:</div>
          <div style="font-weight:600;color:#0f172a;">${madinah.dining || 'Main Restaurant on the R floor'}</div>
        </div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:0.75rem;border-radius:8px;font-size:0.85rem;">
          📅 <strong>Stay Period:</strong> ${madinah.stay_period || '17-18 October 2026 (Check-out on 18 Oct)'}
        </div>
      </div>

      <!-- Finance & Policy (PDF Page 4) -->
      <div class="info-card">
        <div class="section-ribbon-header">Finance & Congress Policy</div>
        <div style="font-weight:700;color:#0f172a;margin-bottom:0.5rem;">${finance.policy_title || 'Global LIPTIS Congress Policy'}</div>
        <div style="background:#fff1f2;border-left:4px solid #c8102e;padding:0.75rem;border-radius:4px;margin-bottom:0.75rem;font-size:0.85rem;color:#881337;">
          <strong>Personal Settlement:</strong> ${finance.personal_expenses || 'We kindly ask you to settle your own Telephone, Laundry and Room Service bills upon checkout.'}
        </div>
        <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:0.75rem;border-radius:4px;font-size:0.85rem;color:#14532d;">
          <strong>Covered by LIPTIS:</strong> ${finance.covered_expenses || 'LIPTIS will cover all transportation, hotel accommodation and all meals included in the program.'}
        </div>
      </div>

    </div>
  `;
}

// Tab 4: Attractions & Distance to Haram (PDF Page 4)
function renderAttractionsTab() {
  const dist = state.sections['distance_haram']?.content || {};
  const transport = state.sections['transportation']?.content || {};
  const attrSec = state.sections['key_attractions']?.content || {};
  const attractions = attrSec.attractions || [];

  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:1.5rem;">
      
      <!-- Distance from Haram (PDF Page 4) -->
      <div class="info-card">
        <div class="section-ribbon-header">Distance from Masjid al-Haram</div>
        <div style="display:flex;align-items:center;gap:1.5rem;padding:1rem 0;">
          <div style="font-size:2.5rem;line-height:1;">🕋</div>
          <div>
            <div style="font-size:1.5rem;font-weight:800;color:#c8102e;">${dist.distance || '400 Meters'}</div>
            <div style="font-size:1.1rem;font-weight:700;color:#0f172a;">${dist.walking_time || '5 Minutes Walk'}</div>
          </div>
        </div>
        <p style="font-size:0.85rem;color:#475569;">
          ${dist.details || 'Walking access to Masjid al-Haram courtyard from Rotana Jabal Omar Hotel.'}
        </p>
      </div>

      <!-- Transportation in KSA (PDF Page 4) -->
      <div class="info-card">
        <div class="section-ribbon-header">Transportation</div>
        <ul style="list-style:none;padding:0;">
          ${(transport.items || []).map(item => `
            <li style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.75rem;font-size:0.9rem;color:#334155;">
              <span style="color:#c8102e;font-weight:bold;">•</span>
              <span>${item}</span>
            </li>
          `).join('')}
        </ul>
      </div>

      <!-- Key Attractions (PDF Page 4) -->
      <div class="info-card" style="grid-column:1/-1;">
        <div class="section-ribbon-header">Key Attractions in Mecca and Madinah</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:1rem;margin-top:0.5rem;">
          ${attractions.map(att => `
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:1rem;">
              <div style="font-weight:700;font-size:1rem;color:#0f172a;">${att.name}</div>
              <div style="font-size:0.75rem;font-weight:600;color:#c8102e;text-transform:uppercase;margin:0.2rem 0 0.4rem 0;">${att.city}</div>
              <div style="font-size:0.85rem;color:#64748b;">${att.description || ''}</div>
            </div>
          `).join('')}
        </div>
      </div>

    </div>
  `;
}

// Tab 5: Guest Care Contacts (PDF Page 5)
function renderContactsTab() {
  return `
    <div class="info-card">
      <div class="section-ribbon-header">Guest Care Contacts</div>
      <p style="font-size:0.95rem;color:#475569;margin-bottom:1.25rem;">
        Staff from <strong>LIPTIS USA</strong> will be on-site to provide round-the-clock assistance throughout your visit.
      </p>

      <div class="contacts-grid">
        ${state.contacts.map(c => `
          <div class="contact-card">
            <div>
              <div class="contact-name">${c.name}</div>
              <div class="contact-title">${c.title}</div>
              <div style="font-size:0.75rem;color:#64748b;margin-bottom:0.5rem;">
                Department: <span style="font-weight:600;color:#0f172a;">${c.category}</span>
              </div>
              <div style="font-size:0.85rem;font-weight:700;color:#0f172a;margin-bottom:0.75rem;">
                📞 ${c.phone}
              </div>
            </div>

            <div class="contact-actions">
              <a href="tel:${c.phone}" class="btn-contact btn-call">
                <span>📞</span> Call
              </a>
              <a href="https://wa.me/${c.phone.replace(/[^0-9]/g, '')}" target="_blank" class="btn-contact btn-whatsapp">
                <span>💬</span> WhatsApp
              </a>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Tab 6: Travel Info - Weather, Time, Currency & Plugs (PDF Page 5)
function renderTravelInfoTab() {
  const weather = state.sections['weather']?.content || {};
  const localTime = state.sections['local_time']?.content || {};
  const forex = state.sections['foreign_exchange']?.content || {};
  const electric = state.sections['electric_appliances']?.content || {};

  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1.5rem;">
      
      <!-- Weather Section -->
      <div class="info-card">
        <div class="section-ribbon-header">Weather</div>
        <div style="font-size:0.85rem;color:#64748b;margin-bottom:0.5rem;">${weather.summary || 'During our trip the average temperature is expected to be:'}</div>
        
        <div style="display:flex;align-items:center;justify-content:space-around;padding:1rem 0;background:#f8fafc;border-radius:8px;margin-bottom:0.75rem;">
          <div style="text-align:center;">
            <div style="font-size:0.75rem;color:#dc2626;font-weight:700;">AVERAGE HIGH</div>
            <div style="font-size:1.6rem;font-weight:800;color:#0f172a;">${weather.avg_high || '38° C'}</div>
          </div>
          <div style="font-size:1.5rem;color:#cbd5e1;">|</div>
          <div style="text-align:center;">
            <div style="font-size:0.75rem;color:#2563eb;font-weight:700;">AVERAGE LOW</div>
            <div style="font-size:1.6rem;font-weight:800;color:#0f172a;">${weather.avg_low || '22° C'}</div>
          </div>
        </div>

        <div style="font-size:0.85rem;color:#475569;background:#fef2f2;padding:0.6rem;border-radius:6px;border-left:3px solid #c8102e;">
          👔 <strong>Recommended Clothing:</strong> ${weather.clothing || 'Light, breathable cotton, and a hat.'}
        </div>
      </div>

      <!-- Local Time Section -->
      <div class="info-card">
        <div class="section-ribbon-header">Local Time</div>
        <div style="font-size:0.85rem;color:#64748b;margin-bottom:0.25rem;">${localTime.zone_name || 'KSA Local Time Zone'}</div>
        <div style="font-weight:700;font-size:1rem;color:#0f172a;margin-bottom:0.5rem;">${localTime.offset || 'GMT+3 hours'}, ${localTime.comparison || 'the same Cairo Local Time.'}</div>

        <div style="background:#0f172a;color:#38bdf8;padding:1rem;border-radius:8px;text-align:center;margin-top:0.75rem;">
          <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;">LIVE KSA CLOCK</div>
          <div id="live-ksa-clock" style="font-size:1.4rem;font-weight:800;font-family:monospace;margin-top:0.25rem;">
            Calculating...
          </div>
        </div>
      </div>

      <!-- Foreign Exchange Section & Calculator -->
      <div class="info-card">
        <div class="section-ribbon-header">Foreign Exchange</div>
        <div style="font-size:0.9rem;font-weight:700;color:#0f172a;">Currency: ${forex.currency || 'Saudi Riyal (SAR)'}</div>
        <div style="font-size:0.8rem;color:#64748b;margin-bottom:0.5rem;">Language: ${forex.language || 'Arabic'} | ${forex.notes || 'ATMs available at hotels and malls'}</div>

        <div style="display:flex;gap:0.5rem;margin-bottom:0.75rem;">
          <div style="flex:1;background:#f1f5f9;padding:0.5rem;border-radius:6px;text-align:center;font-size:0.85rem;font-weight:600;">
            1 USD ≈ 3.75 SAR
          </div>
          <div style="flex:1;background:#f1f5f9;padding:0.5rem;border-radius:6px;text-align:center;font-size:0.85rem;font-weight:600;">
            1 SAR ≈ 13.90 EGP
          </div>
        </div>

        <!-- Interactive Currency Converter -->
        <div class="calculator-box">
          <div style="font-size:0.75rem;font-weight:700;color:#475569;margin-bottom:0.4rem;">QUICK CONVERTER:</div>
          <div class="calc-row">
            <input type="number" id="calc-sar" class="calc-input" placeholder="SAR" value="100" oninput="convertCurrency('sar')" />
            <span style="font-weight:bold;">SAR =</span>
            <input type="number" id="calc-usd" class="calc-input" placeholder="USD" oninput="convertCurrency('usd')" />
            <span style="font-weight:bold;">USD</span>
          </div>
          <div style="font-size:0.8rem;color:#64748b;" id="calc-egp-label">
            ≈ 1,390.00 Egyptian Pounds (EGP)
          </div>
        </div>
      </div>

      <!-- Electric Appliances (PDF Page 5) -->
      <div class="info-card">
        <div class="section-ribbon-header">Electric Appliances</div>
        <div style="font-size:0.9rem;font-weight:700;color:#0f172a;">
          Standard voltage is ${electric.voltage || '220 V'} and frequency of ${electric.frequency || '60Hz'}
        </div>
        <p style="font-size:0.85rem;color:#64748b;margin-top:0.35rem;">
          ${electric.notes || 'Europlug (Type C) and Schuko (Type F) round-pin plugs standard in hotel rooms.'}
        </p>

        <div class="plug-cards">
          <div class="plug-card" style="flex:1;">
            <div style="font-size:1.75rem;">🔌</div>
            <div>Type C</div>
            <div style="font-size:0.7rem;color:#64748b;">Europlug 2-Pin</div>
          </div>
          <div class="plug-card" style="flex:1;">
            <div style="font-size:1.75rem;">🔌</div>
            <div>Type F</div>
            <div style="font-size:0.7rem;color:#64748b;">Schuko Grounded</div>
          </div>
        </div>
      </div>

    </div>
  `;
}

// Tab 7: VAT Refund Information (PDF Page 8)
function renderVatRefundTab() {
  const vat = state.sections['vat_refund']?.content || {};
  const steps = vat.process || [];

  return `
    <div class="info-card" style="padding:1.5rem;">
      <div class="section-ribbon-header">VAT (Value Added Tax) Refund Information</div>
      
      <p style="font-size:0.95rem;color:#334155;line-height:1.6;margin-bottom:1rem;">
        Foreigners (tourists and non-residents) in Saudi Arabia can claim a <strong>VAT refund of ${vat.rate || '15%'}</strong> on eligible purchases made at participating stores.
      </p>

      <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:1rem;border-radius:8px;margin-bottom:1.25rem;">
        <div style="font-weight:700;font-size:0.9rem;color:#0f172a;margin-bottom:0.35rem;">Eligibility Criteria:</div>
        <ul style="padding-left:1.25rem;font-size:0.875rem;color:#475569;line-height:1.5;">
          <li>Buyer must be a non-resident tourist or GCC national aged 18 or older.</li>
          <li>Spend at least <strong>${vat.min_spend || 'SAR 500 (about USD 133)'}</strong> in a single transaction or combined receipts from the same store on the same day.</li>
          <li>Purchased physical goods must be unused, for personal use, and exported out of Saudi Arabia within 90 days.</li>
        </ul>
      </div>

      <h4 style="font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:0.75rem;">To Claim the Tax Refund, the Process Includes:</h4>
      <div style="display:flex;flex-direction:column;gap:0.75rem;margin-bottom:1.5rem;">
        ${steps.map((st, i) => `
          <div style="display:flex;align-items:flex-start;gap:0.75rem;background:#ffffff;border:1px solid #e2e8f0;padding:0.85rem;border-radius:8px;">
            <div style="background:#c8102e;color:#ffffff;font-weight:800;font-size:0.85rem;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
              ${i + 1}
            </div>
            <div style="font-size:0.9rem;color:#334155;line-height:1.5;">${st}</div>
          </div>
        `).join('')}
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1rem;">
        <div style="background:#fff1f2;padding:0.85rem;border-radius:8px;border-left:3px solid #c8102e;font-size:0.85rem;color:#881337;">
          <strong>Excluded Items:</strong> ${vat.excluded_items || 'Services (hotels, dining), food and beverages, tobacco, fuel, vehicles, boats, and large-ticket items.'}
        </div>
        <div style="background:#f0fdf4;padding:0.85rem;border-radius:8px;border-left:3px solid #16a34a;font-size:0.85rem;color:#14532d;">
          <strong>Validity:</strong> ${vat.validity || 'Valid within six months of purchase; procedure designed to encourage tourism and shopping in Saudi Arabia.'}
        </div>
      </div>
    </div>
  `;
}

// Brand Products Footer matching all PDF pages
function renderProductFooter() {
  const portfolio = state.sections['product_portfolio']?.content || {};
  const products = portfolio.products || [
    { name: "JointGuard", indication: "Cartilage Protection" },
    { name: "JointGuard Plus", indication: "Advanced Formula" },
    { name: "JointGuard Ultra", indication: "Maximum Strength" },
    { name: "Xyrkux", indication: "Etoricoxib 60mg, 90mg, 120mg" }
  ];

  return `
    <footer class="products-footer">
      <div style="max-width:1200px;margin:0 auto;">
        <div class="products-badge-row">
          ${products.map(p => `
            <div class="product-item" title="${p.indication}">
              ${p.name.includes('Plus') ? 'JointGuard <span>Plus</span>' : p.name.includes('Ultra') ? 'JointGuard <span>Ultra</span>' : p.name}
            </div>
          `).join('')}
        </div>
        <div class="footer-closing">
          ${portfolio.closing_wish || 'LIPTIS USA Wishes you a nice time'}
        </div>
        <div style="font-size:0.75rem;color:#94a3b8;margin-top:0.75rem;">
          © ${new Date().getFullYear()} LIPTIS USA SALs App • Corporate Travel Management Platform
        </div>
      </div>
    </footer>
  `;
}

// Attach event listeners for Participant View
function attachParticipantEvents() {
  // Convert currency input on first load
  convertCurrency('sar');
}

// Tab Switching
function switchTab(tabKey) {
  state.activeTab = tabKey;
  renderApp();
}

// Flight Selection
async function selectFlight(flightId) {
  state.selectedFlightId = flightId;
  await loadFlightItinerary(flightId);
  renderApp();
  showToast('Itinerary updated for selected flight group.', 'info');
}

// Currency Conversion Calculation
function convertCurrency(source) {
  const sarInput = document.getElementById('calc-sar');
  const usdInput = document.getElementById('calc-usd');
  const egpLabel = document.getElementById('calc-egp-label');
  if (!sarInput || !usdInput || !egpLabel) return;

  const SAR_TO_USD = 1 / 3.75;
  const SAR_TO_EGP = 13.90;

  if (source === 'sar') {
    const sar = parseFloat(sarInput.value) || 0;
    usdInput.value = (sar * SAR_TO_USD).toFixed(2);
    egpLabel.innerText = `≈ ${(sar * SAR_TO_EGP).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Egyptian Pounds (EGP)`;
  } else {
    const usd = parseFloat(usdInput.value) || 0;
    const sar = usd * 3.75;
    sarInput.value = sar.toFixed(2);
    egpLabel.innerText = `≈ ${(sar * SAR_TO_EGP).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Egyptian Pounds (EGP)`;
  }
}

// ================= ADMINISTRATOR DASHBOARD =================

function renderAdminDashboard() {
  const detail = state.adminEventDetail;
  const ev = detail?.event || state.eventData || {};

  return `
    <!-- Administrator Mode Banner -->
    <div class="admin-banner">
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <span style="font-size:1.2rem;">🔒</span>
        <div>
          <strong style="color:#ffffff;">LIPTIS USA Administrator Control Center</strong>
          <span style="font-size:0.75rem;color:#94a3b8;margin-left:0.5rem;">User: ${state.adminUser?.full_name || 'Admin'}</span>
        </div>
      </div>
      <div style="display:flex;gap:0.5rem;">
        <button class="btn-secondary" style="font-size:0.75rem;padding:0.35rem 0.75rem;" onclick="enterPreviewMode()">
          👁️ Preview Viewer Mode
        </button>
        <button class="btn-danger" style="font-size:0.75rem;padding:0.35rem 0.75rem;" onclick="logoutAdmin()">
          Logout
        </button>
      </div>
    </div>

    <div style="max-width:1200px;margin:1.5rem auto;padding:0 1rem;width:100%;">
      
      <!-- Event Publication Status Alert -->
      ${ev.has_unpublished_changes ? `
        <div class="admin-alert-unpublished">
          <div>
            ⚠️ <strong>Unpublished Changes Detected!</strong> Participants cannot see recent updates until published.
          </div>
          <button class="btn-primary" style="padding:0.35rem 0.85rem;font-size:0.8rem;" onclick="publishCurrentEvent('${ev.id}')">
            🚀 Publish Changes Now
          </button>
        </div>
      ` : `
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;color:#166534;padding:0.6rem 1rem;border-radius:10px;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;font-size:0.85rem;font-weight:600;">
          <span>✅ All changes published to participants. Last published: ${ev.published_at ? new Date(ev.published_at).toLocaleString() : 'Recently'}</span>
          <span style="font-size:0.75rem;background:#dcfce7;padding:0.2rem 0.5rem;border-radius:9999px;">Live Status: ${ev.status.toUpperCase()}</span>
        </div>
      `}

      <!-- Admin Top Tabs -->
      <div class="nav-tabs" style="margin-bottom:1.5rem;">
        <button class="nav-tab-btn ${state.adminViewTab === 'events' ? 'active' : ''}" onclick="switchAdminTab('events')">
          📁 All Events (${state.allEvents.length})
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'flights' ? 'active' : ''}" onclick="switchAdminTab('flights')">
          ✈️ Flight Groups (${detail?.flights?.length || 0})
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'itinerary' ? 'active' : ''}" onclick="switchAdminTab('itinerary')">
          🕒 Itinerary Schedule (${detail?.itinerary?.length || 0})
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'sections' ? 'active' : ''}" onclick="switchAdminTab('sections')">
          📄 Content & PDF Topics
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'contacts' ? 'active' : ''}" onclick="switchAdminTab('contacts')">
          👥 Guest Care Team (${detail?.contacts?.length || 0})
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'conflicts' ? 'active' : ''}" onclick="switchAdminTab('conflicts')">
          ⚠️ Conflicts & Quality Check
        </button>
        <button class="nav-tab-btn ${state.adminViewTab === 'audit' ? 'active' : ''}" onclick="switchAdminTab('audit')">
          📜 Audit History & Backups
        </button>
      </div>

      <!-- Current Selected Event Card Summary -->
      <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1rem 1.25rem;margin-bottom:1.5rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
        <div>
          <span style="font-size:0.75rem;font-weight:700;color:#c8102e;text-transform:uppercase;">Selected Event for Editing:</span>
          <h2 style="font-size:1.25rem;color:#0f172a;margin-top:0.2rem;">${ev.title || 'Event'}</h2>
          <div style="font-size:0.85rem;color:#64748b;">${ev.date_display} • ${ev.destination}</div>
        </div>
        <div style="display:flex;gap:0.5rem;">
          <button class="btn-secondary" onclick="openEditEventModal('${ev.id}')">✏️ Edit Event Details</button>
          <button class="btn-primary" onclick="duplicateCurrentEvent('${ev.id}')">📑 Duplicate as New Trip</button>
        </div>
      </div>

      <!-- ADMIN SUB-VIEWS -->
      ${state.adminViewTab === 'events' ? renderAdminEventsTab() : ''}
      ${state.adminViewTab === 'flights' ? renderAdminFlightsTab() : ''}
      ${state.adminViewTab === 'itinerary' ? renderAdminItineraryTab() : ''}
      ${state.adminViewTab === 'sections' ? renderAdminSectionsTab() : ''}
      ${state.adminViewTab === 'contacts' ? renderAdminContactsTab() : ''}
      ${state.adminViewTab === 'conflicts' ? renderAdminConflictsTab() : ''}
      ${state.adminViewTab === 'audit' ? renderAdminAuditTab() : ''}

    </div>
  `;
}

// Admin Tab: All Events
function renderAdminEventsTab() {
  return `
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <h3 style="font-size:1.1rem;color:#0f172a;">All Trips & Incentive Events</h3>
        <button class="btn-primary" onclick="openCreateEventModal()">+ Create New Event</button>
      </div>

      <div style="display:flex;flex-direction:column;gap:0.75rem;">
        ${state.allEvents.map(e => `
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
            <div>
              <div style="display:flex;align-items:center;gap:0.5rem;">
                <strong style="font-size:1rem;color:#0f172a;">${e.title}</strong>
                ${e.is_active ? '<span style="background:#16a34a;color:#ffffff;font-size:0.7rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:9999px;">ACTIVE PUBLIC EVENT</span>' : ''}
                <span style="background:${e.status === 'published' ? '#dcfce7' : '#fef3c7'};color:${e.status === 'published' ? '#166534' : '#92400e'};font-size:0.7rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:9999px;text-transform:uppercase;">
                  ${e.status}
                </span>
              </div>
              <div style="font-size:0.85rem;color:#64748b;margin-top:0.25rem;">
                📅 ${e.date_display} • 📍 ${e.destination}
              </div>
            </div>

            <div style="display:flex;gap:0.4rem;">
              <button class="btn-secondary" style="padding:0.35rem 0.65rem;font-size:0.8rem;" onclick="loadAdminEventDetail('${e.id}')">
                Manage Content
              </button>
              ${!e.is_active ? `
                <button class="btn-secondary" style="padding:0.35rem 0.65rem;font-size:0.8rem;" onclick="setActiveEvent('${e.id}')">
                  Set Active
                </button>
                <button class="btn-danger" style="padding:0.35rem 0.65rem;font-size:0.8rem;" onclick="deleteEvent('${e.id}', '${e.title}')">
                  Delete
                </button>
              ` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Admin Tab: Flight Groups Management
function renderAdminFlightsTab() {
  const flights = state.adminEventDetail?.flights || [];

  return `
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
          <h3 style="font-size:1.1rem;color:#0f172a;">Flight Groups (${flights.length})</h3>
          <p style="font-size:0.85rem;color:#64748b;">Manage flight numbers, airlines, departure times, and arrival transfer dependencies.</p>
        </div>
        <button class="btn-primary" onclick="openAddFlightModal()">+ Add Flight Group</button>
      </div>

      <div style="display:flex;flex-direction:column;gap:1rem;">
        ${flights.map(fg => `
          <div style="background:#ffffff;border:2px solid #e2e8f0;border-radius:10px;padding:1.25rem;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
              <div>
                <h4 style="font-size:1.05rem;color:#0f172a;font-weight:700;">${fg.name}</h4>
                <div style="font-size:0.85rem;color:#c8102e;font-weight:600;margin-top:0.2rem;">
                  Airline: ${fg.airline} • Outbound Flight: ${fg.outbound_flight_number}
                </div>
              </div>
              <div style="display:flex;gap:0.4rem;">
                <button class="btn-secondary" style="padding:0.35rem 0.65rem;font-size:0.8rem;" onclick="openEditFlightModal('${fg.id}')">Edit</button>
                <button class="btn-danger" style="padding:0.35rem 0.65rem;font-size:0.8rem;" onclick="deleteFlightGroup('${fg.id}', '${fg.name}')">Delete</button>
              </div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:0.75rem;margin-top:0.85rem;padding:0.75rem;background:#f8fafc;border-radius:8px;font-size:0.85rem;">
              <div>
                <span style="color:#64748b;">Outbound Departure:</span><br/>
                <strong>${fg.departure_time} (${fg.departure_date})</strong><br/>
                <span style="font-size:0.75rem;color:#475569;">${fg.departure_airport}</span>
              </div>
              <div>
                <span style="color:#64748b;">Outbound Arrival:</span><br/>
                <strong>${fg.arrival_time} (${fg.arrival_date})</strong><br/>
                <span style="font-size:0.75rem;color:#475569;">${fg.arrival_airport}</span>
              </div>
              <div>
                <span style="color:#64748b;">Return Flight:</span><br/>
                <strong>${fg.return_flight_number || 'None'} (${fg.return_departure_time || 'N/A'})</strong><br/>
                <span style="font-size:0.75rem;color:#475569;">${fg.return_departure_airport || ''}</span>
              </div>
            </div>

            ${fg.notes ? `
              <div style="margin-top:0.5rem;font-size:0.8rem;color:#92400e;background:#fef3c7;padding:0.4rem 0.6rem;border-radius:4px;">
                📝 <strong>Notes:</strong> ${fg.notes}
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Admin Tab: Itinerary Schedule Management
function renderAdminItineraryTab() {
  const items = state.adminEventDetail?.itinerary || [];

  return `
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
          <h3 style="font-size:1.1rem;color:#0f172a;">Itinerary Activities (${items.length})</h3>
          <p style="font-size:0.85rem;color:#64748b;">Add shared entries for all attendees or flight-specific schedules for each flight group.</p>
        </div>
        <button class="btn-primary" onclick="openAddItineraryModal()">+ Add Activity / Entry</button>
      </div>

      <div style="display:flex;flex-direction:column;gap:0.75rem;">
        ${items.map(it => `
          <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:0.85rem 1rem;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
            <div style="flex:1;min-width:280px;">
              <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.25rem;">
                <span style="background:#0f172a;color:#ffffff;font-size:0.75rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:4px;">
                  ${it.date}
                </span>
                <span style="background:#f1f5f9;color:#334155;font-size:0.75rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:4px;">
                  ⏰ ${it.start_time}${it.end_time ? ` – ${it.end_time}` : ''}
                </span>
                ${it.flight_group_id ? `
                  <span class="timeline-tag tag-flight-group">✈️ ${it.flight_group_name || 'Group Specific'}</span>
                ` : `
                  <span class="timeline-tag tag-shared">🌐 Shared by All Groups</span>
                `}
                <span class="timeline-tag tag-${it.category}">${it.category.toUpperCase()}</span>
              </div>

              <div style="font-weight:700;font-size:0.95rem;color:#0f172a;">${it.title}</div>
              ${it.description ? `<div style="font-size:0.85rem;color:#64748b;margin-top:0.2rem;">${it.description}</div>` : ''}
              ${it.location ? `<div style="font-size:0.8rem;color:#475569;margin-top:0.2rem;">📍 ${it.location}</div>` : ''}
            </div>

            <div style="display:flex;gap:0.35rem;">
              <button class="btn-secondary" style="padding:0.3rem 0.6rem;font-size:0.75rem;" onclick="openEditItineraryModal('${it.id}')">Edit</button>
              <button class="btn-danger" style="padding:0.3rem 0.6rem;font-size:0.75rem;" onclick="deleteItineraryEntry('${it.id}', '${it.title}')">Delete</button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Admin Tab: Content Sections (PDF Topics)
function renderAdminSectionsTab() {
  const sections = state.adminEventDetail?.sections || [];

  return `
    <div class="info-card">
      <div style="margin-bottom:1.25rem;">
        <h3 style="font-size:1.1rem;color:#0f172a;">PDF Reference Topics & Content Sections</h3>
        <p style="font-size:0.85rem;color:#64748b;">
          The permanent topic structure from the attached PDF is protected. You can edit all variable information under each topic without altering the corporate structure.
        </p>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));gap:1rem;">
        ${sections.map(sec => `
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1rem;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <span style="font-size:0.7rem;font-weight:700;color:#c8102e;text-transform:uppercase;">Topic Key: ${sec.section_key}</span>
              <h4 style="font-size:1rem;color:#0f172a;font-weight:700;margin:0.25rem 0 0.5rem 0;">${sec.title}</h4>
              <div style="background:#ffffff;border:1px solid #e2e8f0;padding:0.5rem;border-radius:6px;max-height:100px;overflow:hidden;font-family:monospace;font-size:0.75rem;color:#475569;margin-bottom:0.75rem;">
                ${JSON.stringify(sec.content, null, 2)}
              </div>
            </div>

            <button class="btn-primary" style="padding:0.35rem 0.75rem;font-size:0.8rem;width:100%;justify-content:center;" onclick="openEditSectionModal('${sec.section_key}')">
              ✏️ Edit ${sec.title}
            </button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Admin Tab: Guest Care Team
function renderAdminContactsTab() {
  const contacts = state.adminEventDetail?.contacts || [];

  return `
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
          <h3 style="font-size:1.1rem;color:#0f172a;">Guest Care Team Contacts (${contacts.length})</h3>
          <p style="font-size:0.85rem;color:#64748b;">Manage on-site support leadership, product managers, and district managers.</p>
        </div>
        <button class="btn-primary" onclick="openAddContactModal()">+ Add Contact</button>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));gap:1rem;">
        ${contacts.map(c => `
          <div class="contact-card">
            <div>
              <div class="contact-name">${c.name}</div>
              <div class="contact-title">${c.title}</div>
              <div style="font-size:0.8rem;color:#64748b;margin-bottom:0.4rem;">Category: <strong>${c.category}</strong></div>
              <div style="font-size:0.85rem;font-weight:700;color:#0f172a;">📞 ${c.phone}</div>
            </div>
            <div style="display:flex;gap:0.4rem;margin-top:0.75rem;">
              <button class="btn-secondary" style="flex:1;padding:0.3rem 0.5rem;font-size:0.75rem;" onclick="openEditContactModal('${c.id}')">Edit</button>
              <button class="btn-danger" style="flex:1;padding:0.3rem 0.5rem;font-size:0.75rem;" onclick="deleteContact('${c.id}', '${c.name}')">Delete</button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Admin Tab: Conflicts & Quality Check
function renderAdminConflictsTab() {
  const conflicts = state.conflicts || [];

  return `
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
          <h3 style="font-size:1.1rem;color:#0f172a;">Schedule Conflict Detection & Safeguards</h3>
          <p style="font-size:0.85rem;color:#64748b;">Automatically inspects flight schedules, airport transfer timing, and missing required travel fields.</p>
        </div>
        <button class="btn-secondary" onclick="checkEventConflicts()">🔄 Re-run Quality Audit</button>
      </div>

      ${conflicts.length === 0 ? `
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;padding:1.5rem;border-radius:10px;text-align:center;color:#166534;">
          <div style="font-size:2rem;margin-bottom:0.5rem;">🎉</div>
          <strong>No Conflicts Detected!</strong>
          <p style="font-size:0.85rem;margin-top:0.25rem;">Flight numbers, departure times, and dependent itineraries are aligned without gaps.</p>
        </div>
      ` : `
        <div style="display:flex;flex-direction:column;gap:0.75rem;">
          ${conflicts.map(c => `
            <div style="background:${c.severity === 'error' ? '#fef2f2' : '#fffbeb'};border:1px solid ${c.severity === 'error' ? '#fecaca' : '#fde68a'};padding:0.85rem 1rem;border-radius:8px;display:flex;align-items:center;gap:0.75rem;">
              <span style="font-size:1.25rem;">${c.severity === 'error' ? '🛑' : '⚠️'}</span>
              <div style="flex:1;font-size:0.875rem;color:${c.severity === 'error' ? '#991b1b' : '#92400e'};">
                ${c.message}
              </div>
            </div>
          `).join('')}
        </div>
      `}
    </div>
  `;
}

// Admin Tab: Audit Log & Backups
function renderAdminAuditTab() {
  const logs = state.adminEventDetail?.audit_logs || [];
  const eventId = state.adminEventDetail?.event?.id || state.eventData?.id;

  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:1.5rem;">
      <div class="info-card">
        <h3 style="font-size:1.1rem;color:#0f172a;margin-bottom:0.5rem;">Recent Audit History</h3>
        <p style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">Tamper-evident record of administrator changes.</p>
        <div style="display:flex;flex-direction:column;gap:0.5rem;max-height:400px;overflow-y:auto;">
          ${logs.map(l => `
            <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:0.6rem 0.85rem;border-radius:6px;font-size:0.8rem;">
              <div style="display:flex;justify-content:space-between;font-weight:700;color:#0f172a;">
                <span>${l.action}</span>
                <span style="font-size:0.7rem;color:#64748b;">${new Date(l.timestamp).toLocaleString()}</span>
              </div>
              <div style="color:#475569;margin-top:0.2rem;">${l.details || ''}</div>
              <div style="font-size:0.7rem;color:#94a3b8;margin-top:0.2rem;">By: ${l.admin_user}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="info-card">
        <h3 style="font-size:1.1rem;color:#0f172a;margin-bottom:0.5rem;">Disaster Recovery & JSON Backup</h3>
        <p style="font-size:0.85rem;color:#64748b;margin-bottom:1rem;">
          Export all flight schedules, itineraries, contacts, and configuration as a standalone JSON backup file.
        </p>
        <button class="btn-primary" style="width:100%;justify-content:center;margin-bottom:1rem;" onclick="downloadEventBackup('${eventId}')">
          💾 Download Event Backup (JSON)
        </button>
      </div>
    </div>
  `;
}

// ================= MODALS & FORMS =================

function openModal(title, bodyHtml, onSaveFn) {
  closeModal(); // ensure no duplicates
  const modal = document.createElement('div');
  modal.id = 'active-modal';
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">${title}</div>
        <button style="background:none;border:none;font-size:1.4rem;cursor:pointer;" onclick="closeModal()">×</button>
      </div>
      <div class="modal-body">${bodyHtml}</div>
      <div class="modal-footer">
        <button class="btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn-primary" id="modal-save-btn">Save Changes</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  document.getElementById('modal-save-btn').onclick = async () => {
    try {
      await onSaveFn();
      closeModal();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };
}

function closeModal() {
  const existing = document.getElementById('active-modal');
  if (existing) existing.remove();
}

// Admin Login Modal
function openAdminLoginModal() {
  openModal('Administrator Login', `
    <form id="admin-login-form" onsubmit="event.preventDefault();">
      <div class="form-group">
        <label class="form-label">Username</label>
        <input type="text" id="login-username" class="form-control" placeholder="admin" value="admin" required />
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <input type="password" id="login-password" class="form-control" placeholder="••••••••" value="AdminPassword2026!" required />
      </div>
      <div style="font-size:0.8rem;color:#64748b;margin-top:0.5rem;">
        Default Administrator Credentials:<br/>
        Username: <code>admin</code> | Password: <code>AdminPassword2026!</code>
      </div>
    </form>
  `, async () => {
    const u = document.getElementById('login-username').value;
    const p = document.getElementById('login-password').value;
    const res = await fetchAPI('/api/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username: u, password: p })
    });
    state.adminToken = res.token;
    state.adminUser = res.user;
    state.isAdminLoggedIn = true;
    localStorage.setItem('liptis_admin_token', res.token);
    showToast('Administrator login successful!', 'success');
    await loadAdminInitialData();
    renderApp();
  });
}

function logoutAdmin() {
  if (state.adminToken) {
    fetchAPI('/api/admin/logout', { method: 'POST' }).catch(() => {});
  }
  state.adminToken = null;
  state.adminUser = null;
  state.isAdminLoggedIn = false;
  state.isPreviewMode = false;
  localStorage.removeItem('liptis_admin_token');
  showToast('Logged out.', 'info');
  loadParticipantEvent().then(() => renderApp());
}

function enterPreviewMode() {
  state.isPreviewMode = true;
  renderApp();
  showToast('Entered Viewer Preview Mode', 'info');
}

function exitPreviewMode() {
  state.isPreviewMode = false;
  renderApp();
  showToast('Returned to Administrator Dashboard', 'info');
}

// Load Admin Initial Data
async function loadAdminInitialData() {
  try {
    state.allEvents = await fetchAPI('/api/admin/events');
    const targetId = state.selectedAdminEventId || state.allEvents[0]?.id;
    if (targetId) {
      await loadAdminEventDetail(targetId);
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadAdminEventDetail(eventId) {
  state.selectedAdminEventId = eventId;
  state.adminEventDetail = await fetchAPI(`/api/admin/events/${eventId}`);
  await checkEventConflicts();
  renderApp();
}

function switchAdminTab(tab) {
  state.adminViewTab = tab;
  renderApp();
}

async function checkEventConflicts() {
  if (!state.selectedAdminEventId) return;
  try {
    const res = await fetchAPI(`/api/admin/events/${state.selectedAdminEventId}/conflicts`);
    state.conflicts = res.conflicts || [];
  } catch (err) {
    console.error(err);
  }
}

// Modal: Edit Event Details
function openEditEventModal(eventId) {
  const ev = state.adminEventDetail?.event || {};
  openModal('Edit Event Details', `
    <div class="form-group">
      <label class="form-label">Event Title</label>
      <input type="text" id="ev-title" class="form-control" value="${ev.title || ''}" />
    </div>
    <div class="form-group">
      <label class="form-label">Destination</label>
      <input type="text" id="ev-dest" class="form-control" value="${ev.destination || ''}" />
    </div>
    <div class="form-group">
      <label class="form-label">Date Display Text</label>
      <input type="text" id="ev-date-disp" class="form-control" value="${ev.date_display || ''}" />
    </div>
    <div class="form-group">
      <label class="form-label">Start Date</label>
      <input type="date" id="ev-start" class="form-control" value="${ev.start_date || ''}" />
    </div>
    <div class="form-group">
      <label class="form-label">End Date</label>
      <input type="date" id="ev-end" class="form-control" value="${ev.end_date || ''}" />
    </div>
  `, async () => {
    await fetchAPI(`/api/admin/events/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify({
        title: document.getElementById('ev-title').value,
        destination: document.getElementById('ev-dest').value,
        date_display: document.getElementById('ev-date-disp').value,
        start_date: document.getElementById('ev-start').value,
        end_date: document.getElementById('ev-end').value
      })
    });
    showToast('Event details updated.', 'success');
    await loadAdminInitialData();
  });
}

// Modal: Add Flight Group
function openAddFlightModal() {
  const evId = state.selectedAdminEventId;
  openModal('Add Flight Group', `
    <div class="form-group">
      <label class="form-label">Flight Group Name</label>
      <input type="text" id="fg-name" class="form-control" placeholder="Flight Group 3 (Afternoon Flight XY 590)" required />
    </div>
    <div style="display:flex;gap:0.5rem;">
      <div class="form-group" style="flex:1;">
        <label class="form-label">Airline</label>
        <input type="text" id="fg-airline" class="form-control" placeholder="Flynas" value="Flynas" required />
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">Outbound Flight No.</label>
        <input type="text" id="fg-flightno" class="form-control" placeholder="XY 590" required />
      </div>
    </div>
    <div style="display:flex;gap:0.5rem;">
      <div class="form-group" style="flex:1;">
        <label class="form-label">Departure Airport</label>
        <input type="text" id="fg-dep-air" class="form-control" value="Cairo International Airport, Terminal 1" />
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">Departure Time</label>
        <input type="text" id="fg-dep-time" class="form-control" placeholder="02:30 PM" required />
      </div>
    </div>
    <div style="display:flex;gap:0.5rem;">
      <div class="form-group" style="flex:1;">
        <label class="form-label">Arrival Airport</label>
        <input type="text" id="fg-arr-air" class="form-control" value="King Abdulaziz International Airport, Jeddah" />
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">Arrival Time</label>
        <input type="text" id="fg-arr-time" class="form-control" placeholder="04:55 PM" required />
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Return Flight Details</label>
      <input type="text" id="fg-ret-flight" class="form-control" placeholder="XY 576 (09:15 PM)" value="XY 576" />
    </div>
    <div class="form-group">
      <label class="form-label">Notes for Participants</label>
      <textarea id="fg-notes" class="form-control" rows="2" placeholder="Luggage drop and terminal instructions..."></textarea>
    </div>
  `, async () => {
    await fetchAPI(`/api/admin/events/${evId}/flights`, {
      method: 'POST',
      body: JSON.stringify({
        event_id: evId,
        name: document.getElementById('fg-name').value,
        airline: document.getElementById('fg-airline').value,
        outbound_flight_number: document.getElementById('fg-flightno').value,
        departure_airport: document.getElementById('fg-dep-air').value,
        departure_date: state.adminEventDetail.event.start_date,
        departure_time: document.getElementById('fg-dep-time').value,
        arrival_airport: document.getElementById('fg-arr-air').value,
        arrival_date: state.adminEventDetail.event.start_date,
        arrival_time: document.getElementById('fg-arr-time').value,
        return_flight_number: document.getElementById('fg-ret-flight').value,
        notes: document.getElementById('fg-notes').value
      })
    });
    showToast('Flight group created successfully.', 'success');
    await loadAdminEventDetail(evId);
  });
}

// Modal: Add Itinerary Entry
function openAddItineraryModal() {
  const evId = state.selectedAdminEventId;
  const flights = state.adminEventDetail?.flights || [];

  openModal('Add Itinerary Entry', `
    <div class="form-group">
      <label class="form-label">Target Audience / Flight Group</label>
      <select id="it-flight-group" class="form-control">
        <option value="">🌐 Shared by ALL Flight Groups</option>
        ${flights.map(fg => `<option value="${fg.id}">✈️ Only for ${fg.name} (${fg.outbound_flight_number})</option>`).join('')}
      </select>
    </div>
    <div style="display:flex;gap:0.5rem;">
      <div class="form-group" style="flex:1;">
        <label class="form-label">Date (YYYY-MM-DD)</label>
        <input type="date" id="it-date" class="form-control" value="${state.adminEventDetail?.event?.start_date || '2026-10-15'}" required />
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">Start Time</label>
        <input type="text" id="it-start" class="form-control" placeholder="06:30 AM" required />
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">End Time</label>
        <input type="text" id="it-end" class="form-control" placeholder="09:30 AM" />
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Activity Title</label>
      <input type="text" id="it-title" class="form-control" placeholder="e.g. Breakfast at Rotana Jabal Omar Hotel" required />
    </div>
    <div style="display:flex;gap:0.5rem;">
      <div class="form-group" style="flex:1;">
        <label class="form-label">Category</label>
        <select id="it-cat" class="form-control">
          <option value="meal">Meal / Dining</option>
          <option value="symposium">Symposium / Meeting</option>
          <option value="flight">Flight / Airport</option>
          <option value="transfer">Transfer / Bus / Train</option>
          <option value="hotel">Hotel Check-in / Checkout</option>
          <option value="prayer">Prayer / Umrah</option>
          <option value="culture">Cultural / Museum</option>
          <option value="activity">General Activity</option>
        </select>
      </div>
      <div class="form-group" style="flex:1;">
        <label class="form-label">Location</label>
        <input type="text" id="it-loc" class="form-control" placeholder="El-Rayan Restaurant, 1st floor" />
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Description & Instructions</label>
      <textarea id="it-desc" class="form-control" rows="2" placeholder="Buffet breakfast details..."></textarea>
    </div>
  `, async () => {
    const fgVal = document.getElementById('it-flight-group').value;
    await fetchAPI(`/api/admin/events/${evId}/itinerary`, {
      method: 'POST',
      body: JSON.stringify({
        event_id: evId,
        flight_group_id: fgVal || null,
        date: document.getElementById('it-date').value,
        start_time: document.getElementById('it-start').value,
        end_time: document.getElementById('it-end').value || null,
        title: document.getElementById('it-title').value,
        category: document.getElementById('it-cat').value,
        location: document.getElementById('it-loc').value,
        description: document.getElementById('it-desc').value
      })
    });
    showToast('Itinerary activity added.', 'success');
    await loadAdminEventDetail(evId);
  });
}

// Modal: Edit PDF Topic Section
function openEditSectionModal(sectionKey) {
  const evId = state.selectedAdminEventId;
  const sec = state.adminEventDetail?.sections?.find(s => s.section_key === sectionKey);
  if (!sec) return;

  openModal(`Edit Topic: ${sec.title}`, `
    <div class="form-group">
      <label class="form-label">Section Title</label>
      <input type="text" id="sec-title" class="form-control" value="${sec.title}" />
    </div>
    <div class="form-group">
      <label class="form-label">Structured JSON Content</label>
      <textarea id="sec-json" class="form-control" rows="12" style="font-family:monospace;font-size:0.85rem;">${JSON.stringify(sec.content, null, 2)}</textarea>
    </div>
    <div style="font-size:0.8rem;color:#64748b;">
      Tip: Edit the specific values (e.g. phone numbers, temperatures, addresses) while preserving the JSON format.
    </div>
  `, async () => {
    let parsed;
    try {
      parsed = JSON.parse(document.getElementById('sec-json').value);
    } catch {
      throw new Error('Invalid JSON format. Please verify quotation marks and commas.');
    }
    await fetchAPI(`/api/admin/events/${evId}/sections/${sectionKey}`, {
      method: 'PUT',
      body: JSON.stringify({
        title: document.getElementById('sec-title').value,
        content_json: parsed
      })
    });
    showToast(`Topic '${sec.title}' updated.`, 'success');
    await loadAdminEventDetail(evId);
  });
}

// Modal: Add Contact
function openAddContactModal() {
  const evId = state.selectedAdminEventId;
  openModal('Add Guest Care Contact', `
    <div class="form-group">
      <label class="form-label">Full Name</label>
      <input type="text" id="con-name" class="form-control" placeholder="Dr. Jane Doe" required />
    </div>
    <div class="form-group">
      <label class="form-label">Job Title</label>
      <input type="text" id="con-title" class="form-control" placeholder="Medical Delegation Coordinator" required />
    </div>
    <div class="form-group">
      <label class="form-label">Phone Number (with Country Code)</label>
      <input type="text" id="con-phone" class="form-control" placeholder="+2010XXXXXXXX" required />
    </div>
    <div class="form-group">
      <label class="form-label">Category / Department</label>
      <input type="text" id="con-cat" class="form-control" placeholder="Guest Care" value="Guest Care" />
    </div>
  `, async () => {
    await fetchAPI(`/api/admin/events/${evId}/contacts`, {
      method: 'POST',
      body: JSON.stringify({
        event_id: evId,
        name: document.getElementById('con-name').value,
        title: document.getElementById('con-title').value,
        phone: document.getElementById('con-phone').value,
        category: document.getElementById('con-cat').value
      })
    });
    showToast('Contact added.', 'success');
    await loadAdminEventDetail(evId);
  });
}

// Publish Event
async function publishCurrentEvent(eventId) {
  try {
    await fetchAPI(`/api/admin/events/${eventId}/publish`, { method: 'POST' });
    showToast('All event modifications successfully published to participants!', 'success');
    await loadAdminEventDetail(eventId);
    await loadParticipantEvent();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Duplicate Event for Future Trips
async function duplicateCurrentEvent(eventId) {
  if (!confirm('Duplicate this trip to create an isolated new event for future LIPTIS travel?')) return;
  try {
    const res = await fetchAPI(`/api/admin/events/${eventId}/duplicate`, { method: 'POST' });
    showToast('Event duplicated as new trip template.', 'success');
    await loadAdminInitialData();
    await loadAdminEventDetail(res.new_event_id);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Set Active Event
async function setActiveEvent(eventId) {
  try {
    await fetchAPI(`/api/admin/events/${eventId}/set-active`, { method: 'POST' });
    showToast('Active public event updated.', 'success');
    await loadAdminInitialData();
    await loadParticipantEvent();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Delete Event
async function deleteEvent(eventId, title) {
  if (!confirm(`Are you sure you want to permanently delete event '${title}'? This action cannot be undone.`)) return;
  try {
    await fetchAPI(`/api/admin/events/${eventId}`, { method: 'DELETE' });
    showToast('Event deleted.', 'info');
    await loadAdminInitialData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Delete Flight Group
async function deleteFlightGroup(flightId, name) {
  if (!confirm(`Delete flight group '${name}'? Dependent flight-specific itineraries will also be removed.`)) return;
  try {
    await fetchAPI(`/api/admin/flights/${flightId}`, { method: 'DELETE' });
    showToast('Flight group deleted.', 'info');
    await loadAdminEventDetail(state.selectedAdminEventId);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Delete Itinerary Entry
async function deleteItineraryEntry(entryId, title) {
  if (!confirm(`Delete itinerary activity '${title}'?`)) return;
  try {
    await fetchAPI(`/api/admin/itinerary/${entryId}`, { method: 'DELETE' });
    showToast('Activity removed.', 'info');
    await loadAdminEventDetail(state.selectedAdminEventId);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Delete Contact
async function deleteContact(contactId, name) {
  if (!confirm(`Remove contact '${name}'?`)) return;
  try {
    await fetchAPI(`/api/admin/contacts/${contactId}`, { method: 'DELETE' });
    showToast('Contact removed.', 'info');
    await loadAdminEventDetail(state.selectedAdminEventId);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Download Backup
async function downloadEventBackup(eventId) {
  try {
    const data = await fetchAPI(`/api/admin/events/${eventId}/export`);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `liptis-event-backup-${eventId}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Backup JSON downloaded.', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function attachAdminEvents() {
  // Attached dynamically
}
