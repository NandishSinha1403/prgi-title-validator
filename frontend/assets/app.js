const API = 'http://127.0.0.1:8000/api';

// --- Navigation ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`.nav-tab[onclick*="${tabId}"]`).classList.add('active');

    if (tabId === 'stats') loadStats();
    if (tabId === 'admin') loadAdmin();
    if (tabId === 'database') searchDB();
}

function fillInput(val) {
    document.getElementById('titleInput').value = val;
}

// --- Validator ---
document.getElementById('verifyBtn').addEventListener('click', async () => {
    const title = document.getElementById('titleInput').value.trim();
    if (!title) return;

    const loader = document.getElementById('validator-loader');
    const results = document.getElementById('resultsArea');
    loader.classList.remove('hidden');
    results.classList.add('hidden');

    try {
        const resp = await fetch(`${API}/verify-title`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title})
        });
        const data = await resp.json();
        renderResults(data);
    } catch (err) {
        alert('Connection Error');
    } finally {
        loader.classList.add('hidden');
    }
});

function renderResults(data) {
    const results = document.getElementById('resultsArea');
    results.classList.remove('hidden');

    const banner = document.getElementById('statusBanner');
    banner.className = 'banner serif ' + (data.verdict === 'APPROVED' ? 'banner-approved' : 'banner-rejected');
    banner.innerHTML = (data.verdict === 'APPROVED' ? '✓' : '✗') + ' TITLE ' + data.verdict;

    const probNum = document.getElementById('probVal');
    probNum.innerText = Math.round(data.approval_probability) + '%';
    
    if (data.approval_probability < 30) probNum.style.color = 'var(--primary-crimson)';
    else if (data.approval_probability < 70) probNum.style.color = '#f39c12';
    else probNum.style.color = 'var(--success)';

    const reasonsArea = document.getElementById('reasonsArea');
    reasonsArea.innerHTML = '';
    data.rejection_reasons.forEach(r => {
        reasonsArea.innerHTML += `<div class="card reason-card">⚠️ ${r}</div>`;
    });

    const similarArea = document.getElementById('similarTitlesArea');
    similarArea.innerHTML = '';
    
    if (data.priority_matches && data.priority_matches.length > 0) {
        data.priority_matches.forEach(group => {
            const groupTitle = document.createElement('span');
            groupTitle.className = 'priority-label';
            groupTitle.innerText = group.label;
            similarArea.appendChild(groupTitle);

            group.matches.forEach(m => {
                let badgeLabel = m.match_type.replace(/_/g, ' ').toUpperCase();
                let badgeSubtitle = '';
                
                if (m.match_type === 'semantic_cross_language') {
                    badgeLabel = 'SEMANTIC';
                    badgeSubtitle = '<span class="badge-subtitle">Cross-Language</span>';
                } else if (m.match_type === 'semantic_conceptual') {
                    badgeLabel = 'SEMANTIC';
                    badgeSubtitle = '<span class="badge-subtitle">Conceptual Theme</span>';
                }

                similarArea.innerHTML += `
                    <div class="match-row">
                        <div class="match-header">
                            <span class="serif" style="font-size: 18px;">${m.existing_title}</span>
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div class="match-badge">${badgeLabel}${badgeSubtitle}</div>
                                <span style="color: var(--primary-crimson); font-weight: bold;">${Math.round(m.match_percentage)}%</span>
                            </div>
                        </div>
                        <div class="progress-bg"><div class="progress-fill" style="width: ${m.match_percentage}%"></div></div>
                    </div>
                `;
            });
        });
    } else {
        similarArea.innerHTML = '<p style="color: var(--text-secondary); font-size: 14px;">No major similarities detected.</p>';
    }
}

// --- Database ---
async function searchDB() {
    const loader = document.getElementById('db-loader');
    loader.classList.remove('hidden');
    
    const params = new URLSearchParams({
        q: document.getElementById('filter-title').value,
        registration_number: document.getElementById('filter-reg').value,
        owner: document.getElementById('filter-owner').value,
        state: document.getElementById('filter-state').value,
        district: document.getElementById('filter-district').value,
        language: document.getElementById('filter-lang').value,
        limit: document.getElementById('filter-limit').value
    });

    try {
        const resp = await fetch(`${API}/search?${params}`);
        const data = await resp.json();
        renderTable(data);
    } finally {
        loader.classList.add('hidden');
    }
}

function renderTable(data) {
    const body = document.getElementById('dbBody');
    body.innerHTML = '';
    document.getElementById('results-count').innerText = `Showing ${data.length} results`;
    data.forEach((row, i) => {
        body.innerHTML += `
            <tr>
                <td>${i + 1}</td>
                <td class="serif" style="font-weight: bold;">${row.title}</td>
                <td>${row.registration_number || '-'}</td>
                <td>${row.registration_date || '-'}</td>
                <td>${row.language || '-'}</td>
                <td>${row.periodicity || '-'}</td>
                <td>${row.publisher || '-'}</td>
                <td>${row.owner || '-'}</td>
                <td>${row.pub_state || '-'}</td>
            </tr>
        `;
    });
}

function resetFilters() {
    document.querySelectorAll('#database input').forEach(i => i.value = '');
    searchDB();
}

// --- Statistics ---
async function loadStats() {
    const resp = await fetch(`${API}/stats`);
    const data = await resp.json();
    document.getElementById('stat-total-titles').innerText = data.total_titles.toLocaleString();
    document.getElementById('stat-languages').innerText = data.total_languages;
    document.getElementById('stat-states').innerText = data.total_states;
    document.getElementById('stat-disallowed').innerText = data.total_disallowed_words;
    document.getElementById('hero-total-titles').innerText = data.total_titles.toLocaleString();

    const recentResp = await fetch(`${API}/recent`);
    const recentData = await recentResp.json();
    const body = document.getElementById('recentBody');
    body.innerHTML = '';
    recentData.forEach(r => {
        body.innerHTML += `
            <tr>
                <td>${r.title}</td>
                <td><span class="badge ${r.verdict === 'APPROVED' ? 'badge-green' : 'badge-red'}">${r.verdict}</span></td>
                <td style="color: var(--primary-crimson); font-weight: bold;">${Math.round(r.probability)}%</td>
            </tr>
        `;
    });
}

// --- Admin ---
async function loadAdmin() {
    const resp = await fetch(`${API}/disallowed-words`);
    const words = await resp.json();
    const list = document.getElementById('wordList');
    list.innerHTML = '';
    words.forEach(w => {
        list.innerHTML += `
            <div class="pill">
                ${w} <span class="close" onclick="removeWord('${w}')">×</span>
            </div>
        `;
    });
}

async function addWord() {
    const word = document.getElementById('newWordInput').value.trim();
    if (!word) return;
    await fetch(`${API}/disallowed-words`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({word})
    });
    document.getElementById('newWordInput').value = '';
    loadAdmin();
}

async function removeWord(word) {
    await fetch(`${API}/disallowed-words/${word}`, {method: 'DELETE'});
    loadAdmin();
}

// --- Table Sorting ---
function sortTable(n) {
    const table = document.getElementById("dbTable");
    let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    switching = true; dir = "asc";
    while (switching) {
        switching = false; rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) { shouldSwitch = true; break; }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) { shouldSwitch = true; break; }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true; switchcount ++;
        } else {
            if (switchcount == 0 && dir == "asc") { dir = "desc"; switching = true; }
        }
    }
}

function exportData(type) {
    const table = document.getElementById("dbTable");
    let csv = [];
    for (let i = 0; i < table.rows.length; i++) {
        let row = [], cols = table.rows[i].querySelectorAll("td, th");
        for (let j = 0; j < cols.length; j++) row.push('"' + cols[j].innerText + '"');
        csv.push(row.join(","));
    }
    const blob = new Blob([csv.join("
")], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', 'prgi_titles_export.csv');
    a.click();
}

// Init
window.onload = () => {
    loadStats();
};
