/* ═══════════════════════════════════════════════════════════════════════
   AGENTLENS — Frontend Application
   ═══════════════════════════════════════════════════════════════════════ */

const API_BASE = '/api';

// ─── State ──────────────────────────────────────────────────
let allSessions = [];
let allAnalyses = [];
let allIssues = [];
let allMetrics = {};
let currentView = 'dashboard';

// ─── Helpers ────────────────────────────────────────────────
function formatTypeName(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getSeverityBadge(sev) {
    return `<span class="badge badge-${sev}">${sev}</span>`;
}

function getClassBadge(cls) {
    return `<span class="badge badge-${cls.toLowerCase().replace(/ /g, '-')}">${cls}</span>`;
}

// ─── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadAllData();
        setupNavigation();
        setupThemeToggle();
        setupSearch();
        setupRefresh();
        renderDashboard();
    } catch (err) {
        console.error('AGENTLENS init error:', err);
        document.body.innerHTML = `
            <div style="padding:40px;color:#f85149;">
                <h1>⚠️ AGENTLENS Error</h1>
                <p>${err.message}</p>
                <p>Make sure the backend is running: <code>python -m agentlens.main</code></p>
            </div>`;
    }
});

// ─── Data Loading ───────────────────────────────────────────
async function loadAllData() {
    const [sessionsRes, issuesRes, metricsRes, summaryRes] = await Promise.all([
        fetch(`${API_BASE}/sessions`),
        fetch(`${API_BASE}/issues`),
        fetch(`${API_BASE}/metrics`),
        fetch(`${API_BASE}/summary`),
    ]);

    allSessions = await sessionsRes.json();
    const issuesData = await issuesRes.json();
    allIssues = issuesData.issues;
    allMetrics = await metricsRes.json();
    const summaryData = await summaryRes.json();

    // Load analyses for first 20 sessions
    allAnalyses = [];
    for (const s of allSessions.slice(0, 20)) {
        try {
            const r = await fetch(`${API_BASE}/sessions/${s.id}/analysis`);
            const a = await r.json();
            allAnalyses.push(a);
        } catch (_) {}
    }
}

// ─── Navigation ─────────────────────────────────────────────
function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchView(btn.dataset.view);
        });
    });
    document.getElementById('back-btn').addEventListener('click', () => {
        switchView('dashboard');
    });
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('modal-overlay').addEventListener('click', (e) => {
        if (e.target === document.getElementById('modal-overlay')) closeModal();
    });
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    const activeBtn = document.querySelector(`.nav-btn[data-view="${view}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    const target = document.getElementById(`view-${view}`);
    if (target) target.classList.add('active');

    const titles = { dashboard: 'Dashboard', sessions: 'All Sessions', issues: 'Issue Groups', 'session-detail': 'Session Detail' };
    document.getElementById('view-title').textContent = titles[view] || 'Dashboard';

    if (view === 'dashboard') renderDashboard();
    if (view === 'sessions') renderSessionsTable();
    if (view === 'issues') renderIssuesDetail();
}

// ─── Theme ──────────────────────────────────────────────────
function setupThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    const html = document.documentElement;
    btn.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        btn.textContent = next === 'dark' ? '🌙' : '☀️';
        localStorage.setItem('agentlens-theme', next);
    });
    const saved = localStorage.getItem('agentlens-theme') || 'dark';
    html.setAttribute('data-theme', saved);
    btn.textContent = saved === 'dark' ? '🌙' : '☀️';
}

// ─── Search ─────────────────────────────────────────────────
function setupSearch() {
    const input = document.getElementById('session-search');
    input.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        if (currentView === 'sessions') {
            const filtered = allSessions.filter(s =>
                s.id.toLowerCase().includes(q) ||
                s.title.toLowerCase().includes(q) ||
                (s.customer_id && s.customer_id.toLowerCase().includes(q)) ||
                (s.order_id && s.order_id.toLowerCase().includes(q))
            );
            renderSessionsTable(filtered);
        }
    });
}

// ─── Refresh ────────────────────────────────────────────────
function setupRefresh() {
    const btn = document.getElementById('refresh-btn');
    btn.addEventListener('click', async () => {
        btn.textContent = '↻ Loading...';
        btn.disabled = true;
        await loadAllData();
        if (currentView === 'dashboard') renderDashboard();
        if (currentView === 'sessions') renderSessionsTable();
        if (currentView === 'issues') renderIssuesDetail();
        btn.textContent = '↻ Refresh';
        btn.disabled = false;
    });
}

// ═══════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════

async function renderDashboard() {
    const summaryRes = await fetch(`${API_BASE}/summary`);
    const summary = await summaryRes.json();

    animateNumber('stat-total', summary.total_sessions);
    animateNumber('stat-success', summary.successful);
    animateNumber('stat-recovered', summary.recovered);
    animateNumber('stat-failure', summary.likely_failures);
    animateNumber('stat-ambiguous', summary.ambiguous);

    renderClassificationChart(summary);
    renderIssuesChart();
    renderIssuesList();
    renderMetricsBar();
}

async function animateNumber(id, target) {
    const el = document.getElementById(id);
    const duration = 800;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ─── Charts ─────────────────────────────────────────────────
let classificationChart = null;
let issuesChartInstance = null;

async function renderClassificationChart(summary) {
    const ctx = document.getElementById('classification-chart');
    if (!ctx) return;
    if (classificationChart) classificationChart.destroy();

    classificationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Successful', 'Recovered', 'Likely Failure', 'Ambiguous'],
            datasets: [{
                data: [summary.successful, summary.recovered, summary.likely_failures, summary.ambiguous],
                backgroundColor: [
                    'rgba(63, 185, 80, 0.8)',
                    'rgba(57, 210, 192, 0.8)',
                    'rgba(248, 81, 73, 0.8)',
                    'rgba(210, 153, 34, 0.8)',
                ],
                borderColor: ['#3fb950', '#39d2c0', '#f85149', '#d29922'],
                borderWidth: 2,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#8b949e', padding: 16, usePointStyle: true } }
            },
            cutout: '65%',
        }
    });
}

async function renderIssuesChart() {
    const ctx = document.getElementById('issues-chart');
    if (!ctx) return;
    if (issuesChartInstance) issuesChartInstance.destroy();

    const res = await fetch(`${API_BASE}/issues`);
    const data = await res.json();
    const issues = data.issues;

    const labels = issues.map(i => i.type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).slice(0, 25));
    const values = issues.map(i => i.count);
    const bgColors = issues.map(i =>
        i.severity === 'high' ? 'rgba(248, 81, 73, 0.7)' :
        i.severity === 'medium' ? 'rgba(210, 153, 34, 0.7)' :
        'rgba(57, 210, 192, 0.7)'
    );
    const borderColors = issues.map(i =>
        i.severity === 'high' ? '#f85149' :
        i.severity === 'medium' ? '#d29922' : '#39d2c0'
    );

    issuesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{ label: 'Count', data: values, backgroundColor: bgColors, borderColor: borderColors, borderWidth: 1, borderRadius: 4 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(48,54,61,0.5)' }, ticks: { color: '#8b949e' } },
                y: { grid: { display: false }, ticks: { color: '#8b949e', font: { size: 11 } } },
            }
        }
    });
}

// ─── Issues List ────────────────────────────────────────────
async function renderIssuesList() {
    const res = await fetch(`${API_BASE}/issues`);
    const data = await res.json();
    const issues = data.issues;
    const container = document.getElementById('issues-list');

    container.innerHTML = issues.map(issue => `
        <div class="issue-item" onclick="showIssueDetail('${issue.type}')">
            <div class="issue-severity ${issue.severity}"></div>
            <div class="issue-info">
                <div class="issue-type">${formatTypeName(issue.type)}</div>
                <div class="issue-desc">${issue.description}</div>
                <div class="issue-meta">
                    <span>📊 ${issue.count} session${issue.count !== 1 ? 's' : ''}</span>
                    <span>📈 ${(issue.avg_confidence * 100).toFixed(0)}% confidence</span>
                    <span>${issue.sessions.length} sessions</span>
                    ${getSeverityBadge(issue.severity)}
                </div>
            </div>
        </div>
    `).join('');
}

// ─── Issues Detail ──────────────────────────────────────────
async function renderIssuesDetail() {
    const res = await fetch(`${API_BASE}/issues`);
    const data = await res.json();
    const issues = data.issues;
    const container = document.getElementById('issues-detail-list');

    container.innerHTML = issues.map(issue => `
        <div class="card" style="cursor:pointer;" onclick="showIssueDetail('${issue.type}')">
            <div class="card-header">
                <h3>${formatTypeName(issue.type)}</h3>
                ${getSeverityBadge(issue.severity)}
            </div>
            <div class="card-body">
                <p style="margin-bottom:12px;">${issue.description}</p>
                <div style="display:flex;gap:24px;font-size:13px;color:var(--text-secondary);margin-bottom:12px;">
                    <span><strong style="color:var(--text-primary)">${issue.count}</strong> sessions</span>
                    <span><strong style="color:var(--text-primary)">${(issue.avg_confidence * 100).toFixed(0)}%</strong> avg confidence</span>
                </div>
                <p style="font-size:13px;color:var(--accent-blue);">💡 ${issue.recommended_action}</p>
                <div style="margin-top:8px;font-size:11px;color:var(--text-muted);">
                    Sessions: ${issue.sessions.slice(0, 5).join(', ')}${issue.sessions.length > 5 ? ' ...' : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function showIssueDetail(type) {
    const matching = allSessions.filter(s => {
        const analysis = allAnalyses.find(a => a.session_id === s.id);
        return analysis && analysis.findings.some(f => f.type === type);
    });

    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
        <h4 style="margin-bottom:16px;">Sessions with "${formatTypeName(type)}" (${matching.length})</h4>
        ${matching.slice(0, 10).map(s => `
            <div style="padding:12px;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;cursor:pointer;"
                 onclick="openSessionDetail('${s.id}'); closeModal();">
                <strong>${s.id}</strong> — ${s.title}
                <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">
                    Customer: ${s.customer_id || 'N/A'} | Order: ${s.order_id || 'N/A'}
                </div>
            </div>
        `).join('')}
        ${matching.length === 0 ? '<p style="color:var(--text-muted)">No matching sessions.</p>' : ''}
    `;
    document.getElementById('modal-overlay').style.display = 'flex';
}

// ─── Metrics ────────────────────────────────────────────────
function renderMetricsBar() {
    const container = document.getElementById('metrics-bar');
    if (!container || !allMetrics.sessions_analyzed) return;

    const metrics = [
        { label: 'Sessions', value: allMetrics.sessions_analyzed },
        { label: 'Events', value: allMetrics.total_events_analyzed },
        { label: 'AI Analyses', value: allMetrics.ai_analyses_count },
        { label: 'Processing Time', value: `${allMetrics.processing_time_ms.toFixed(0)}ms` },
        { label: 'Avg/Session', value: `${allMetrics.average_processing_time_ms.toFixed(1)}ms` },
        { label: 'Est. AI Cost', value: allMetrics.estimated_ai_cost ? `$${allMetrics.estimated_ai_cost.toFixed(5)}` : '$0.00' },
        { label: 'Throughput', value: `${allMetrics.throughput_sessions_per_min}/min` },
    ];

    container.innerHTML = metrics.map(m => `
        <div class="metric-item">
            <span class="metric-label">${m.label}</span>
            <span class="metric-value">${m.value}</span>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════
// SESSIONS TABLE
// ═══════════════════════════════════════════════════════════════

function renderSessionsTable(filteredSessions) {
    const sessions = filteredSessions || allSessions;
    const tbody = document.getElementById('sessions-table-body');
    document.getElementById('session-count').textContent = `${sessions.length} sessions`;

    tbody.innerHTML = sessions.map(session => {
        const analysis = allAnalyses.find(a => a.session_id === session.id);
        const cls = analysis ? analysis.classification : '—';
        const conf = analysis ? (analysis.overall_confidence * 100).toFixed(0) + '%' : '—';
        const findings = analysis ? analysis.findings.length : 0;
        const clsClass = cls.toLowerCase().replace(/ /g, '-');

        return `
        <tr>
            <td class="mono">${session.id}</td>
            <td>${session.title}</td>
            <td class="mono">${session.customer_id || '—'}</td>
            <td>${getClassBadge(cls)}</td>
            <td class="mono">${conf}</td>
            <td>${findings}</td>
            <td><button class="btn btn-sm" onclick="openSessionDetail('${session.id}')">View</button></td>
        </tr>`;
    }).join('');
}

// ═══════════════════════════════════════════════════════════════
// SESSION DETAIL
// ═══════════════════════════════════════════════════════════════

async function openSessionDetail(sessionId) {
    const [sessionRes, analysisRes] = await Promise.all([
        fetch(`${API_BASE}/sessions/${sessionId}`),
        fetch(`${API_BASE}/sessions/${sessionId}/analysis`),
    ]);

    const session = await sessionRes.json();
    const analysis = await analysisRes.json();

    switchView('session-detail');

    // Title
    document.getElementById('detail-title').textContent = session.title;
    document.getElementById('detail-badges').innerHTML = `
        ${getClassBadge(analysis.classification)}
        <span class="badge badge-info">Confidence: ${(analysis.overall_confidence * 100).toFixed(0)}%</span>
        <span class="badge badge-info">${analysis.findings.length} finding${analysis.findings.length !== 1 ? 's' : ''}</span>
    `;

    // Conversation
    renderConversation(session, analysis);

    // Findings
    renderFindings(analysis);
}

function renderConversation(session, analysis) {
    const container = document.getElementById('conversation-body');
    const messages = session.messages;

    container.innerHTML = messages.map((msg, i) => {
        const isTool = msg.role === 'tool' && msg.tool_call;
        const tc = isTool ? msg.tool_call : null;

        let html = `<div class="msg msg-${msg.role}">`;
        html += `<div class="msg-avatar">${getAvatar(msg.role)}</div>`;
        html += `<div class="msg-content">`;
        html += `<div class="msg-role">${msg.role}</div>`;
        html += `<div class="msg-text">${msg.content}</div>`;

        if (tc) {
            html += `<div class="tool-result">${tc.tool_name}(${JSON.stringify(tc.arguments, null, 2)}) → ${JSON.stringify(tc.result, null, 2)}</div>`;
        }

        html += `<div class="msg-time">${new Date(msg.timestamp).toLocaleString()}</div>`;
        html += `</div></div>`;

        // Check if this message is in a finding
        const finding = analysis.findings.find(f => f.message_indices.includes(i));
        if (finding) {
            html += renderFindingCallout(finding);
        }

        return html;
    }).join('');
}

function getAvatar(role) {
    if (role === 'user') return 'U';
    if (role === 'assistant') return 'AI';
    return '⚙';
}

function renderFindingCallout(finding) {
    const evidenceHtml = finding.evidence.map(e => {
        const hasPending = e.detail && (e.detail.includes('PENDING') || e.detail.includes('pending'));
        return `<div class="finding-evidence">
            <strong>Message #${e.message_index}</strong> (${e.message_role}): ${e.detail}
            ${e.tool_result ? `<div class="tool-result" style="margin-top:6px;font-size:11px;">${JSON.stringify(e.tool_result, null, 2)}</div>` : ''}
        </div>`;
    }).join('');

    return `
        <div class="finding-callout" style="margin-left:48px;">
            <div class="finding-header">
                ${getClassBadge(finding.classification)}
                <span class="finding-type">${formatTypeName(finding.type)}</span>
                <span class="finding-conf">${(finding.confidence * 100).toFixed(0)}% confidence</span>
            </div>
            <div class="finding-reason">${finding.reason}</div>
            ${evidenceHtml}
            <div class="finding-action">💡 ${finding.recommended_action}</div>
        </div>`;
}

function renderFindings(analysis) {
    const card = document.getElementById('findings-card');
    const body = document.getElementById('findings-body');

    if (analysis.findings.length === 0) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';
    body.innerHTML = analysis.findings.map(renderFindingCallout).join('');
}

// ─── Modal ──────────────────────────────────────────────────
function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

// ─── Utility ────────────────────────────────────────────────
function formatTypeName(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
