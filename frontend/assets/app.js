const API_BASE_URL = 'http://127.0.0.1:8000/api';

// --- Submit Page Logic ---
const titleForm = document.getElementById('titleForm');
const titleInput = document.getElementById('titleInput');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const chips = document.querySelectorAll('.chip');

if (titleInput && charCount) {
    titleInput.addEventListener('input', (e) => {
        const length = e.target.value.length;
        charCount.textContent = `${length}/100`;
        if (length > 100) {
            titleInput.value = e.target.value.substring(0, 100);
            charCount.textContent = `100/100`;
        }
    });

    // Chip click logic
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            titleInput.value = chip.textContent;
            charCount.textContent = `${chip.textContent.length}/100`;
            titleInput.focus();
        });
    });
}

if (titleForm) {
    titleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = titleInput.value.trim();
        if (title) {
            submitBtn.classList.add('loading');
            sessionStorage.setItem('submittedTitle', title);
            setTimeout(() => {
                window.location.href = 'results.html';
            }, 300);
        }
    });
}

// --- Results Page Logic ---
const resultsContent = document.getElementById('resultsContent');
const loader = document.getElementById('loader');

if (resultsContent && loader) {
    const titleToVerify = sessionStorage.getItem('submittedTitle');
    
    if (!titleToVerify) {
        window.location.href = 'submit.html';
    } else {
        document.getElementById('submittedTitle').textContent = `"${titleToVerify}"`;
        fetchResults(titleToVerify);
    }
}

async function fetchResults(title) {
    try {
        const response = await fetch(`${API_BASE_URL}/verify-title`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title })
        });
        
        if (!response.ok) {
            throw new Error('API Request Failed');
        }
        
        const data = await response.json();
        
        setTimeout(() => {
            renderResults(data);
        }, 500);
        
    } catch (error) {
        console.error('Error fetching results:', error);
        loader.innerHTML = `<h3 style="color: var(--error-color);">Connection Error</h3>
                            <p style="color: var(--text-muted);">Failed to fetch results. Make sure backend is running (http://127.0.0.1:8000).</p>`;
    }
}

function renderResults(data) {
    loader.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    
    const gauge = document.getElementById('probabilityGauge');
    const probValue = document.getElementById('probabilityValue');
    const statusBanner = document.getElementById('statusBanner');
    
    // 1. Dynamic Colors
    let colorHex = 'var(--accent-color)';
    if (data.approval_probability > 60) {
        colorHex = 'var(--success-color)';
    } else if (data.approval_probability >= 30) {
        colorHex = 'var(--warning-color)';
    } else {
        colorHex = 'var(--error-color)';
    }
    
    // 2. Animate Gauge
    setTimeout(() => {
        gauge.style.setProperty('--value', `${data.approval_probability}%`);
        gauge.style.setProperty('--gauge-color', colorHex);
    }, 100);
    
    probValue.textContent = `${Math.round(data.approval_probability)}%`;
    probValue.style.textShadow = `0 0 20px ${colorHex}80`;

    // 3. Banner Logic & Rejection Badges
    statusBanner.classList.remove('hidden');
    statusBanner.innerHTML = ''; // Clear previous content
    
    const bannerTitle = document.createElement('div');
    bannerTitle.textContent = data.verdict === 'APPROVED' ? '✅ TITLE APPROVED' : '❌ TITLE REJECTED';
    statusBanner.appendChild(bannerTitle);

    if (data.verdict === 'REJECTED') {
        statusBanner.className = 'banner banner-rejected fade-in';
        
        // Add badges for rejection reasons under the verdict
        const badgeContainer = document.createElement('div');
        badgeContainer.style.display = 'flex';
        badgeContainer.style.flexWrap = 'wrap';
        badgeContainer.style.justifyContent = 'center';
        badgeContainer.style.gap = '0.5rem';
        badgeContainer.style.marginTop = '1rem';
        
        data.rejection_reasons.forEach(reason => {
            const badge = document.createElement('span');
            badge.className = 'badge';
            badge.style.backgroundColor = 'rgba(255, 75, 75, 0.2)';
            badge.style.border = '1px solid var(--error-color)';
            badge.style.color = 'white';
            badge.style.fontSize = '0.7rem';
            badge.textContent = reason;
            badgeContainer.appendChild(badge);
        });
        statusBanner.appendChild(badgeContainer);
    } else {
        statusBanner.className = 'banner banner-approved fade-in';
    }

    if (data.approval_probability >= 80) {
        createConfetti();
    }
    
    // 4. Render Rejection Reasons (Cards)
    const reasonsContainer = document.getElementById('reasonsContainer');
    const reasonsList = document.getElementById('reasonsList');
    reasonsList.innerHTML = '';
    
    if (data.rejection_reasons && data.rejection_reasons.length > 0) {
        reasonsContainer.classList.remove('hidden');
        data.rejection_reasons.forEach((reason, index) => {
            const card = document.createElement('div');
            card.className = `reason-card fade-in delay-${(index % 3) + 1}`;
            card.innerHTML = `
                <div class="reason-icon">⚠️</div>
                <div class="reason-text">${reason}</div>
            `;
            reasonsList.appendChild(card);
        });
    } else {
        reasonsContainer.classList.add('hidden');
    }
    
    // 5. Render Similar Titles
    const similarContainer = document.getElementById('similarContainer');
    const similarList = document.getElementById('similarList');
    similarList.innerHTML = '';
    
    if (data.top_similar_titles && data.top_similar_titles.length > 0) {
        similarContainer.classList.remove('hidden');
        data.top_similar_titles.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = `similar-card fade-in delay-${(index % 3) + 1}`;
            
            let barColor = 'var(--error-color)';
            if (item.match_percentage < 40) barColor = 'var(--success-color)';
            else if (item.match_percentage < 70) barColor = 'var(--warning-color)';

            const badgeClass = item.match_type === 'semantic' ? 'badge-fuzzy' : (item.match_type === 'phonetic' ? 'badge-phonetic' : 'badge-fuzzy');
            
            card.innerHTML = `
                <div class="similar-header">
                    <span class="similar-title-name">${item.existing_title}</span>
                    <span class="badge ${badgeClass}">${item.match_type}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: 0%; background: ${barColor};"></div>
                </div>
                <div class="similar-meta">
                    <span>Similarity</span>
                    <span style="font-weight: 700; color: ${barColor};">${item.match_percentage}%</span>
                </div>
            `;
            similarList.appendChild(card);
            setTimeout(() => {
                const bar = card.querySelector('.progress-bar');
                if(bar) bar.style.width = `${item.match_percentage}%`;
            }, 300);
        });
    } else {
        similarContainer.classList.add('hidden');
    }

    // 6. ADD CHECKS BREAKDOWN SECTION
    renderChecksBreakdown(data.checks);
}

function renderChecksBreakdown(checks) {
    const container = document.querySelector('.container');
    
    // Remove existing breakdown if any
    const existing = document.getElementById('checksBreakdown');
    if (existing) existing.remove();
    
    const breakdownSection = document.createElement('div');
    breakdownSection.id = 'checksBreakdown';
    breakdownSection.style.marginTop = '3rem';
    breakdownSection.className = 'fade-in delay-3';
    
    const title = document.createElement('h3');
    title.className = 'section-title';
    title.style.cursor = 'pointer';
    title.innerHTML = '🔍 Checks Breakdown <span style="font-size: 0.8rem; float: right;">(Click to Toggle)</span>';
    
    const content = document.createElement('div');
    content.id = 'breakdownContent';
    content.className = 'hidden';
    content.style.padding = '1.5rem';
    content.style.background = 'var(--card-bg)';
    content.style.border = '1px solid var(--card-border)';
    content.style.borderRadius = '12px';
    content.style.marginTop = '1rem';
    
    // Helper to create breakdown item
    const createItem = (label, score, detail) => {
        return `
            <div style="margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600;">${label}</span>
                    <span style="color: var(--accent-color); font-weight: 700;">${score}</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">${detail}</div>
            </div>
        `;
    };

    content.innerHTML = `
        ${createItem('Phonetic Match', `${checks.phonetic.score}%`, `Sounds like: ${checks.phonetic.matches.map(m => m.existing_title).join(', ') || 'None'}`)}
        ${createItem('Fuzzy Match', `${checks.fuzzy.score}%`, `Spelled like: ${checks.fuzzy.matches.map(m => m.existing_title).join(', ') || 'None'}`)}
        ${createItem('Semantic Match', `${checks.semantic.score}%`, `Meanings like: ${checks.semantic.matches.map(m => m.existing_title).join(', ') || 'None'}`)}
        ${createItem('Rule Violations', checks.rules.violation_count, `Violations: ${checks.rules.violations.join(', ') || 'None'}`)}
    `;
    
    title.addEventListener('click', () => {
        content.classList.toggle('hidden');
    });
    
    breakdownSection.appendChild(title);
    breakdownSection.appendChild(content);
    
    // Insert before actions
    const actions = document.querySelector('.actions');
    container.insertBefore(breakdownSection, actions);
}

function createConfetti() {
    const box = document.getElementById('confettiBox');
    if (!box) return;
    box.classList.remove('hidden');
    const colors = ['#2ecc71', '#5B6AF9', '#f2d74e', '#e74c3c', '#9b59b6'];
    
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animation = `confettiFall ${Math.random() * 3 + 2}s linear forwards`;
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        if (Math.random() > 0.5) confetti.style.borderRadius = '50%';
        box.appendChild(confetti);
    }
    setTimeout(() => {
        box.innerHTML = '';
        box.classList.add('hidden');
    }, 5000);
}
