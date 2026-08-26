/* ═══════════════════════════════════════════════════════════
   TripBudgetBuddy — Multi-Trip Session Manager
   
   All trip data (chat history, names) stored in sessionStorage.
   Data persists until the browser tab is closed.
   Each trip gets its own server-side session via session_id.
   ═══════════════════════════════════════════════════════════ */

const API_BASE = '';
const STORAGE_KEY = 'tripbuddy_trips';

// ── State ────────────────────────────────────────────────────
let trips = [];          // Array of trip objects
let activeTrip = null;   // Currently active trip object

// Trip object shape:
// {
//   id: string,          // unique session ID
//   name: string,        // display name (auto-named from destination or "Trip N")
//   icon: string,        // emoji icon
//   messages: [          // chat history for UI rendering
//     { role: 'user'|'assistant', content: string, time: string }
//   ],
//   createdAt: string    // ISO timestamp
// }

// ── DOM Elements ─────────────────────────────────────────────
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const budgetOverview = document.getElementById('budgetOverview');
const panelPlaceholder = document.getElementById('panelPlaceholder');
const tripInfo = document.getElementById('tripInfo');
const overallBudget = document.getElementById('overallBudget');
const categoryBars = document.getElementById('categoryBars');
const alertsSection = document.getElementById('alertsSection');
const expenseHistory = document.getElementById('expenseHistory');
const expenseList = document.getElementById('expenseList');
const btnStatus = document.getElementById('btnStatus');
const btnNewTrip = document.getElementById('btnNewTrip');
const addTripBtn = document.getElementById('addTripBtn');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const sidebar = document.getElementById('sidebar');
const tripTabsList = document.getElementById('tripTabsList');

// ══════════════════════════════════════════════════════════════
//  SESSION STORAGE
// ══════════════════════════════════════════════════════════════

function saveToStorage() {
    const data = {
        trips: trips,
        activeTripId: activeTrip ? activeTrip.id : null
    };
    try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
        console.warn('sessionStorage write failed:', e);
    }
}

function loadFromStorage() {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (!raw) return false;

        const data = JSON.parse(raw);
        if (data.trips && data.trips.length > 0) {
            trips = data.trips;
            const targetId = data.activeTripId || trips[0].id;
            activeTrip = trips.find(t => t.id === targetId) || trips[0];
            return true;
        }
    } catch (e) {
        console.warn('sessionStorage read failed:', e);
    }
    return false;
}

// ══════════════════════════════════════════════════════════════
//  TRIP MANAGEMENT
// ══════════════════════════════════════════════════════════════

function createTrip() {
    const id = 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
    const tripNum = trips.length + 1;
    const trip = {
        id: id,
        name: `Trip ${tripNum}`,
        icon: getRandomTripIcon(),
        messages: [],
        createdAt: new Date().toISOString()
    };
    trips.push(trip);
    activeTrip = trip;
    saveToStorage();

    // Add welcome message
    addMessageToTrip(trip.id, 'assistant',
        "Hey there! 👋 I'm **TripBudgetBuddy**, your AI travel budget assistant.\n\n" +
        "I can help you:\n" +
        "- 🗺️ **Plan a trip budget**\n" +
        "- 💱 **Convert currencies** with live rates\n" +
        "- 📝 **Log expenses** in local currency\n" +
        "- ⚠️ **Alert you** when spending gets risky\n\n" +
        "Tell me your **destination**, **travel dates**, and **total budget** to start! 🚀"
    );

    renderTabs();
    renderChat();
    resetSidebar();
    refreshSidebar();
    messageInput.focus();
}

function switchTrip(tripId) {
    if (activeTrip && activeTrip.id === tripId) return;

    const trip = trips.find(t => t.id === tripId);
    if (!trip) return;

    activeTrip = trip;
    saveToStorage();

    renderTabs();
    renderChat();
    resetSidebar();
    refreshSidebar();
    messageInput.focus();
}

function closeTrip(tripId) {
    const idx = trips.findIndex(t => t.id === tripId);
    if (idx === -1) return;

    // Clean up server session (fire-and-forget)
    fetch(`${API_BASE}/api/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: tripId })
    }).catch(() => {});

    trips.splice(idx, 1);

    if (trips.length === 0) {
        createTrip();
        return;
    }

    // If we closed the active trip, switch to the nearest
    if (activeTrip && activeTrip.id === tripId) {
        activeTrip = trips[Math.min(idx, trips.length - 1)];
    }

    saveToStorage();
    renderTabs();
    renderChat();
    resetSidebar();
    refreshSidebar();
}

function addMessageToTrip(tripId, role, content) {
    const trip = trips.find(t => t.id === tripId);
    if (!trip) return;

    trip.messages.push({
        role: role,
        content: content,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    saveToStorage();
}

function getRandomTripIcon() {
    const icons = ['✈️', '🌴', '🏖️', '🗼', '🏔️', '🎒', '🚂', '⛩️', '🏰', '🌸'];
    return icons[Math.floor(Math.random() * icons.length)];
}

/** Try to auto-rename the trip from the agent's setup_trip response */
function tryAutoRenameTrip(tripId, assistantResponse) {
    const trip = trips.find(t => t.id === tripId);
    if (!trip) return;
    // Only auto-rename if still using default name
    if (!trip.name.match(/^Trip \d+$/)) return;

    // Look for destination mentions in the response
    const patterns = [
        /trip to\s+\*{0,2}([A-Z][a-zA-Z\s,]+)/i,
        /heading to\s+\*{0,2}([A-Z][a-zA-Z\s,]+)/i,
        /destination.*?:\s*\*{0,2}([A-Z][a-zA-Z\s,]+)/i,
        /📍\s*([A-Z][a-zA-Z\s,]+)/i
    ];

    for (const pat of patterns) {
        const m = assistantResponse.match(pat);
        if (m && m[1]) {
            let name = m[1].trim().replace(/\*+/g, '').replace(/[.!?,]+$/, '').trim();
            if (name.length > 2 && name.length < 40) {
                trip.name = name;
                saveToStorage();
                renderTabs();
                return;
            }
        }
    }
}

// ══════════════════════════════════════════════════════════════
//  RENDERING
// ══════════════════════════════════════════════════════════════

function renderTabs() {
    let html = '';
    for (const trip of trips) {
        const isActive = activeTrip && activeTrip.id === trip.id;
        const msgCount = trip.messages.filter(m => m.role === 'user').length;
        const meta = msgCount > 0 ? `${msgCount} message${msgCount !== 1 ? 's' : ''}` : 'New trip';

        html += `
            <div class="trip-tab ${isActive ? 'active' : ''}" data-trip-id="${trip.id}">
                <span class="trip-tab-icon">${trip.icon}</span>
                <div class="trip-tab-info">
                    <div class="trip-tab-name">${escapeHtml(trip.name)}</div>
                    <div class="trip-tab-meta">${meta}</div>
                </div>
                <button class="trip-tab-close" data-close-id="${trip.id}" title="Close trip">✕</button>
            </div>
        `;
    }
    tripTabsList.innerHTML = html;

    // Attach click handlers
    tripTabsList.querySelectorAll('.trip-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            // Don't switch if clicking close button
            if (e.target.closest('.trip-tab-close')) return;
            switchTrip(tab.dataset.tripId);
        });
    });

    tripTabsList.querySelectorAll('.trip-tab-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.closeId;
            // Only confirm if trip has user messages
            const trip = trips.find(t => t.id === id);
            const hasContent = trip && trip.messages.some(m => m.role === 'user');
            if (!hasContent || confirm('Close this trip? Chat history will be lost.')) {
                closeTrip(id);
            }
        });
    });
}

function renderChat() {
    chatMessages.innerHTML = '';

    if (!activeTrip || activeTrip.messages.length === 0) return;

    for (const msg of activeTrip.messages) {
        appendMessageDOM(msg.role, msg.content, msg.time);
    }
    scrollToBottom();
}

function appendMessageDOM(role, content, time) {
    const div = document.createElement('div');
    div.className = `message ${role}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'assistant' ? '🌍' : '👤';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatMessage(content);

    const timeEl = document.createElement('span');
    timeEl.className = 'message-time';
    timeEl.textContent = time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timeEl);
    div.appendChild(avatar);
    div.appendChild(contentDiv);

    chatMessages.appendChild(div);
}

function resetSidebar() {
    panelPlaceholder.style.display = 'block';
    budgetOverview.style.display = 'none';
    expenseHistory.style.display = 'none';
    tripInfo.innerHTML = '';
    overallBudget.innerHTML = '';
    categoryBars.innerHTML = '';
    alertsSection.innerHTML = '';
    expenseList.innerHTML = '';
}

// ══════════════════════════════════════════════════════════════
//  CHAT / API
// ══════════════════════════════════════════════════════════════

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !activeTrip) return;

    const currentTripId = activeTrip.id;

    // Add user message
    addMessageToTrip(currentTripId, 'user', text);
    appendMessageDOM('user', text);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Update tab meta
    renderTabs();

    // Show typing
    typingIndicator.style.display = 'flex';
    scrollToBottom();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: currentTripId })
        });

        const data = await res.json();

        // Only render if still on the same trip
        if (activeTrip && activeTrip.id === currentTripId) {
            if (data.error) {
                const errMsg = `❌ Error: ${data.error}`;
                addMessageToTrip(currentTripId, 'assistant', errMsg);
                appendMessageDOM('assistant', errMsg);
            } else {
                addMessageToTrip(currentTripId, 'assistant', data.response);
                appendMessageDOM('assistant', data.response);
                tryAutoRenameTrip(currentTripId, data.response);
                await refreshSidebar();
            }
        } else {
            // User switched tabs while waiting — still save the response
            if (data.error) {
                addMessageToTrip(currentTripId, 'assistant', `❌ Error: ${data.error}`);
            } else {
                addMessageToTrip(currentTripId, 'assistant', data.response);
                tryAutoRenameTrip(currentTripId, data.response);
            }
        }
    } catch (err) {
        const errMsg = `❌ Connection error. Is the server running?\n\n\`${err.message}\``;
        addMessageToTrip(currentTripId, 'assistant', errMsg);
        if (activeTrip && activeTrip.id === currentTripId) {
            appendMessageDOM('assistant', errMsg);
        }
    } finally {
        typingIndicator.style.display = 'none';
        sendBtn.disabled = false;
        messageInput.focus();
        renderTabs(); // refresh message count
    }
}

// ══════════════════════════════════════════════════════════════
//  SIDEBAR REFRESH
// ══════════════════════════════════════════════════════════════

async function refreshSidebar() {
    if (!activeTrip) return;

    try {
        const statusRes = await fetch(`${API_BASE}/api/status?session_id=${activeTrip.id}`);
        const status = await statusRes.json();

        if (status.status === 'no_session' || status.status === 'no_trip' || status.status === 'error') {
            return;
        }

        panelPlaceholder.style.display = 'none';
        budgetOverview.style.display = 'block';

        // Trip info
        if (status.trip) {
            const t = status.trip;
            tripInfo.innerHTML = `
                <div class="trip-destination">📍 ${escapeHtml(t.destination)}</div>
                <div class="trip-dates">📅 ${formatDate(t.start_date)} → ${formatDate(t.end_date)}</div>
                <div class="trip-currencies">
                    <span class="currency-tag">${escapeHtml(t.home_currency)}</span>
                    <span style="color: var(--text-muted);">→</span>
                    <span class="currency-tag">${escapeHtml(t.local_currency)}</span>
                </div>
            `;

            // Also auto-rename the trip tab if still default
            const trip = trips.find(tr => tr.id === activeTrip.id);
            if (trip && trip.name.match(/^Trip \d+$/)) {
                trip.name = t.destination;
                saveToStorage();
                renderTabs();
            }
        }

        // Overall budget
        if (status.overall) {
            const o = status.overall;
            const pct = Math.min(o.percent_used, 100);
            const barColor = pct >= 85 ? 'var(--red)' :
                             pct >= 70 ? 'var(--orange)' :
                             pct >= 50 ? 'var(--yellow)' : 'var(--green)';
            overallBudget.innerHTML = `
                <div class="overall-label">Overall Budget</div>
                <div class="overall-amount" style="background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    ${formatCurrency(o.total_remaining)} <span style="font-size: 0.7em; -webkit-text-fill-color: var(--text-muted);">remaining</span>
                </div>
                <div class="overall-bar-track">
                    <div class="overall-bar-fill" style="width: ${pct}%; background: ${barColor};"></div>
                </div>
                <div class="overall-stats">
                    <span>Spent: ${formatCurrency(o.total_spent)}</span>
                    <span>${o.percent_used}% used</span>
                </div>
            `;
        }

        // Category bars
        if (status.categories) {
            const cats = status.categories;
            const icons = { lodging: '🏨', food: '🍽️', transport: '🚕', activities: '🎭', shopping: '🛍️' };
            let barsHtml = '';

            for (const [cat, data] of Object.entries(cats)) {
                const pct = Math.min(data.percent_used, 100);
                const color = data.status === 'over_budget' ? 'var(--red)' :
                              data.status === 'critical' ? 'var(--orange)' :
                              data.status === 'warning' ? 'var(--yellow)' : 'var(--accent-primary)';
                barsHtml += `
                    <div class="cat-item">
                        <div class="cat-header">
                            <span class="cat-name">${icons[cat] || '📌'} ${cat}</span>
                            <span class="cat-amount">${formatCurrency(data.spent)} / ${formatCurrency(data.budget)}</span>
                        </div>
                        <div class="cat-bar-track">
                            <div class="cat-bar-fill" style="width: ${pct}%; background: ${color};"></div>
                        </div>
                    </div>
                `;
            }
            categoryBars.innerHTML = barsHtml;
        }

        // Alerts
        if (status.alerts && status.alerts.length > 0) {
            alertsSection.innerHTML = status.alerts.map(a =>
                `<div class="alert-item alert-${a.severity}">${a.message}</div>`
            ).join('');
        } else {
            alertsSection.innerHTML = '';
        }

        // Expense history
        const expRes = await fetch(`${API_BASE}/api/expenses?session_id=${activeTrip.id}`);
        const expData = await expRes.json();

        if (expData.expenses && expData.expenses.length > 0) {
            expenseHistory.style.display = 'block';
            const recent = expData.expenses.slice(-8).reverse();
            expenseList.innerHTML = recent.map(e => `
                <div class="expense-item">
                    <span class="expense-cat">${escapeHtml(e.category)}</span>
                    <span class="expense-amt">${formatCurrency(e.amount_home)} ${escapeHtml(e.home_currency)}</span>
                </div>
            `).join('');
        } else {
            expenseHistory.style.display = 'none';
        }

    } catch (err) {
        console.log('Sidebar refresh error:', err);
    }
}

// ══════════════════════════════════════════════════════════════
//  FORMATTING HELPERS
// ══════════════════════════════════════════════════════════════

function formatMessage(text) {
    if (!text) return '';

    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    html = '<p>' + html + '</p>';

    // Bullet lists
    html = html.replace(/<p>((?:[-•] .*(?:<br>)?)+)<\/p>/g, (match, list) => {
        const items = list.split('<br>')
            .filter(item => item.trim())
            .map(item => `<li>${item.replace(/^[-•]\s*/, '')}</li>`)
            .join('');
        return `<ul>${items}</ul>`;
    });

    // Numbered lists
    html = html.replace(/<p>((?:\d+\.\s.*(?:<br>)?)+)<\/p>/g, (match, list) => {
        const items = list.split('<br>')
            .filter(item => item.trim())
            .map(item => `<li>${item.replace(/^\d+\.\s*/, '')}</li>`)
            .join('');
        return `<ol>${items}</ol>`;
    });

    return html;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

function formatDate(dateStr) {
    try {
        const d = new Date(dateStr + 'T00:00:00');
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch { return dateStr; }
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return '0';
    return new Intl.NumberFormat('en-IN', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(Math.round(amount));
}

// ══════════════════════════════════════════════════════════════
//  EVENT LISTENERS
// ══════════════════════════════════════════════════════════════

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
});

// Enter to send
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

// Quick actions
btnStatus.addEventListener('click', () => {
    messageInput.value = "Show me my current budget status";
    sendMessage();
});

// Both "New Trip" buttons do the same thing
btnNewTrip.addEventListener('click', () => createTrip());
addTripBtn.addEventListener('click', () => createTrip());

// Mobile menu
mobileMenuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 &&
        sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        e.target !== mobileMenuBtn) {
        sidebar.classList.remove('open');
    }
});

// ══════════════════════════════════════════════════════════════
//  INIT
// ══════════════════════════════════════════════════════════════

(function init() {
    const restored = loadFromStorage();
    if (restored) {
        renderTabs();
        renderChat();
        refreshSidebar();
    } else {
        // First visit — create initial trip
        createTrip();
    }
    messageInput.focus();
})();
