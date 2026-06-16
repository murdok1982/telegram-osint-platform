let authToken = null;
let currentUser = null;

const API_BASE = '';

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
        logout();
        throw new Error('Session expired');
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API error');
    }
    
    return response.json();
}

function showLogin() {
    document.getElementById('login-container').style.display = 'flex';
    document.getElementById('register-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'none';
}

function showRegister() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'flex';
    document.getElementById('dashboard-container').style.display = 'none';
}

function showDashboard() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';
    document.getElementById('user-info').textContent = `${currentUser.full_name || currentUser.username} (${currentUser.role})`;
    loadDashboard();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showLogin();
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        authToken = response.access_token;
        currentUser = response.user;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        showDashboard();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const full_name = document.getElementById('reg-fullname').value;
    const password = document.getElementById('reg-password').value;
    
    try {
        await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, full_name, password })
        });
        alert('Registro exitoso. Ahora puedes iniciar sesión.');
        showLogin();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`${section}-section`).classList.add('active');
    event.target.classList.add('active');
    
    if (section === 'dashboard') loadDashboard();
    if (section === 'cases') loadCases();
    if (section === 'messages') loadMessages();
    if (section === 'rules') loadRules();
}

async function loadDashboard() {
    try {
        const stats = await apiCall('/stats/dashboard');
        document.getElementById('stat-messages').textContent = stats.total_messages;
        document.getElementById('stat-cases').textContent = stats.total_cases;
        document.getElementById('stat-open').textContent = stats.cases_by_status.open;
        document.getElementById('stat-high').textContent = stats.risk_distribution.high;
        
        const chart = document.getElementById('risk-chart');
        const total = stats.total_messages || 1;
        const highPct = (stats.risk_distribution.high / total * 100).toFixed(1);
        const medPct = (stats.risk_distribution.medium / total * 100).toFixed(1);
        const lowPct = (stats.risk_distribution.low / total * 100).toFixed(1);
        
        chart.innerHTML = `
            <div style="display:flex;gap:20px;margin-top:15px;">
                <div style="flex:1;">
                    <div style="background:#ef5350;height:20px;width:${highPct}%;border-radius:4px;"></div>
                    <p style="margin-top:5px;color:#ef5350;">Alto: ${highPct}%</p>
                </div>
                <div style="flex:1;">
                    <div style="background:#ffa726;height:20px;width:${medPct}%;border-radius:4px;"></div>
                    <p style="margin-top:5px;color:#ffa726;">Medio: ${medPct}%</p>
                </div>
                <div style="flex:1;">
                    <div style="background:#66bb6a;height:20px;width:${lowPct}%;border-radius:4px;"></div>
                    <p style="margin-top:5px;color:#66bb6a;">Bajo: ${lowPct}%</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadCases() {
    const status = document.getElementById('case-status-filter').value;
    const endpoint = status ? `/cases?status=${status}` : '/cases';
    
    try {
        const cases = await apiCall(endpoint);
        const tbody = document.getElementById('cases-tbody');
        tbody.innerHTML = '';
        
        cases.forEach(c => {
            const riskClass = c.risk_score >= 12 ? 'risk-high' : c.risk_score >= 8 ? 'risk-medium' : 'risk-low';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${c.id}</td>
                <td><span class="status-badge status-${c.status}">${c.status}</span></td>
                <td class="${riskClass}">${c.risk_score.toFixed(1)}</td>
                <td class="text-truncate">${c.user_hash || '-'}</td>
                <td>${new Date(c.created_at).toLocaleString()}</td>
                <td><button class="action-btn" onclick="viewCase(${c.id})">Ver</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

async function viewCase(caseId) {
    try {
        const c = await apiCall(`/cases/${caseId}`);
        const modal = document.getElementById('modal');
        const body = document.getElementById('modal-body');
        
        body.innerHTML = `
            <h2>Caso #${c.id}</h2>
            <p><strong>Estado:</strong> <span class="status-badge status-${c.status}">${c.status}</span></p>
            <p><strong>Riesgo:</strong> ${c.risk_score.toFixed(1)}</p>
            <p><strong>Fecha:</strong> ${new Date(c.created_at).toLocaleString()}</p>
            ${c.summary ? `<p><strong>Resumen:</strong> ${c.summary}</p>` : ''}
            ${c.agent_analysis ? `
                <h3 style="margin-top:20px;">Análisis de Agentes</h3>
                <pre style="background:#0f3460;padding:15px;border-radius:4px;overflow-x:auto;font-size:0.85em;">${JSON.stringify(c.agent_analysis, null, 2)}</pre>
            ` : ''}
            <div style="margin-top:20px;display:flex;gap:10px;">
                <select id="case-status-update" style="padding:8px;background:#0f3460;border:1px solid #333;border-radius:4px;color:#fff;">
                    <option value="open">Abierto</option>
                    <option value="analyzing">En análisis</option>
                    <option value="analyzed">Analizado</option>
                    <option value="closed">Cerrado</option>
                </select>
                <button class="btn-primary" style="width:auto;padding:8px 16px;" onclick="updateCaseStatus(${c.id})">Actualizar</button>
            </div>
        `;
        
        document.getElementById('case-status-update').value = c.status;
        modal.style.display = 'flex';
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function updateCaseStatus(caseId) {
    const status = document.getElementById('case-status-update').value;
    try {
        await apiCall(`/cases/${caseId}`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
        closeModal();
        loadCases();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadMessages() {
    const chatId = document.getElementById('msg-chat-filter').value;
    const userHash = document.getElementById('msg-user-filter').value;
    
    let endpoint = '/messages?';
    if (chatId) endpoint += `chat_id=${chatId}&`;
    if (userHash) endpoint += `user_hash=${userHash}&`;
    
    try {
        const messages = await apiCall(endpoint);
        const tbody = document.getElementById('messages-tbody');
        tbody.innerHTML = '';
        
        messages.forEach(m => {
            const riskClass = m.risk_score >= 12 ? 'risk-high' : m.risk_score >= 8 ? 'risk-medium' : 'risk-low';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${m.id}</td>
                <td>${m.chat_id || '-'}</td>
                <td class="text-truncate" title="${(m.text || '').replace(/"/g, '&quot;')}">${m.text || '-'}</td>
                <td class="${riskClass}">${m.risk_score.toFixed(1)}</td>
                <td>${new Date(m.created_at).toLocaleString()}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

async function loadRules() {
    try {
        const response = await apiCall('/health');
        document.getElementById('rules-languages').textContent = 'es, en, ar, ru, zh, ko';
        document.getElementById('rules-content').innerHTML = `
            <div style="background:#16213e;padding:20px;border-radius:8px;">
                <h3>Reglas Cargadas</h3>
                <ul style="margin-top:15px;list-style:none;">
                    <li>🇪🇸 Español (es.yaml) - Extremismo, narcotráfico, armas</li>
                    <li>🇬🇧 English (en.yaml) - Terrorism, trafficking, extremism</li>
                    <li>🇸🇦 العربية (ar.yaml) - إرهاب، تطرف</li>
                    <li>🇷🇺 Русский (ru.yaml) - Терроризм, экстремизм</li>
                    <li>🇨🇳 中文 (zh.yaml) - 恐怖主义，极端主义</li>
                    <li>🇰🇷 한국어 (ko.yaml) - 테러, 극단주의</li>
                </ul>
                <p style="margin-top:15px;color:#aaa;">Las reglas se recargan automáticamente al reiniciar el worker.</p>
            </div>
        `;
    } catch (error) {
        console.error('Error loading rules:', error);
    }
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

window.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showDashboard();
    } else {
        showLogin();
    }
});
