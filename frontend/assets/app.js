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
            // Small delay for UI feedback
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
        
        // Add 500ms delay for dramatic effect
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
    
    // Dynamic Colors Logic
    let colorHex = 'var(--accent-color)';
    if (data.probability > 60) {
        colorHex = 'var(--success-color)';
    } else if (data.probability >= 30) {
        colorHex = 'var(--warning-color)';
    } else {
        colorHex = 'var(--error-color)';
    }
    
    // Animate Gauge
    setTimeout(() => {
        gauge.style.setProperty('--value', `${data.probability}%`);
        gauge.style.setProperty('--gauge-color', colorHex);
    }, 100); // slight delay to trigger CSS transition
    
    probValue.textContent = `${data.probability}%`;
    probValue.style.textShadow = `0 0 20px ${colorHex}80`; // 80 is alpha hex

    // Banner Logic
    statusBanner.classList.remove('hidden');
    if (data.probability > 50) {
        statusBanner.textContent = '✅ TITLE APPROVED';
        statusBanner.className = 'banner banner-approved fade-in';
    } else {
        statusBanner.textContent = '❌ TITLE REJECTED';
        statusBanner.className = 'banner banner-rejected fade-in';
    }

    // Confetti Logic
    if (data.probability >= 80) {
        createConfetti();
    }
    
    // Render Rejection Reasons
    if (data.rejection_reasons && data.rejection_reasons.length > 0) {
        const reasonsContainer = document.getElementById('reasonsContainer');
        const reasonsList = document.getElementById('reasonsList');
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
    }
    
    // Render Similar Titles
    if (data.similar_titles && data.similar_titles.length > 0) {
        const similarContainer = document.getElementById('similarContainer');
        const similarList = document.getElementById('similarList');
        similarContainer.classList.remove('hidden');
        
        // Top 5 only
        const top5 = data.similar_titles.slice(0, 5);
        
        top5.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = `similar-card fade-in delay-${(index % 3) + 1}`;
            
            // Dynamic color for the progress bar based on match percentage (inverse logic to probability)
            let barColor = 'var(--error-color)';
            if (item.match_percentage < 40) barColor = 'var(--success-color)';
            else if (item.match_percentage < 70) barColor = 'var(--warning-color)';

            const badgeClass = item.match_type === 'phonetic' ? 'badge-phonetic' : 'badge-fuzzy';
            
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
            
            // Animate progress bar
            setTimeout(() => {
                const bar = card.querySelector('.progress-bar');
                if(bar) bar.style.width = `${item.match_percentage}%`;
            }, 300);
        });
    }
}

function createConfetti() {
    const box = document.getElementById('confettiBox');
    box.classList.remove('hidden');
    const colors = ['#2ecc71', '#5B6AF9', '#f2d74e', '#e74c3c', '#9b59b6'];
    
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animation = `confettiFall ${Math.random() * 3 + 2}s linear forwards`;
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        
        // Random shapes
        if (Math.random() > 0.5) {
            confetti.style.borderRadius = '50%';
        }
        
        box.appendChild(confetti);
    }
    
    // Cleanup
    setTimeout(() => {
        box.innerHTML = '';
        box.classList.add('hidden');
    }, 5000);
}
