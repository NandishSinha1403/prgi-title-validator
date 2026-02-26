const API_BASE_URL = 'http://127.0.0.1:8000/api';

// --- Submit Page Logic ---
const titleForm = document.getElementById('titleForm');
const titleInput = document.getElementById('titleInput');
const charCount = document.getElementById('charCount');
const errorMsg = document.getElementById('errorMsg');

if (titleInput && charCount) {
    titleInput.addEventListener('input', (e) => {
        const length = e.target.value.length;
        charCount.textContent = `${length}/100`;
        if (length > 100) {
            titleInput.value = e.target.value.substring(0, 100);
            charCount.textContent = `100/100`;
        }
    });
}

if (titleForm) {
    titleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = titleInput.value.trim();
        if (title) {
            sessionStorage.setItem('submittedTitle', title);
            window.location.href = 'results.html';
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
        renderResults(data);
    } catch (error) {
        console.error('Error fetching results:', error);
        loader.textContent = 'Failed to fetch results. Make sure backend is running (http://127.0.0.1:8000).';
        loader.style.color = 'var(--error-color)';
    }
}

function renderResults(data) {
    loader.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    
    // Update Gauge
    const gauge = document.getElementById('probabilityGauge');
    const probValue = document.getElementById('probabilityValue');
    
    // Animate logic using CSS variables and conic-gradient
    gauge.style.setProperty('--value', `${data.probability}%`);
    probValue.textContent = `${data.probability}%`;
    
    // Set gauge color based on probability
    if (data.probability < 40) {
        gauge.style.setProperty('--accent-color', 'var(--error-color)');
    } else if (data.probability >= 75) {
        gauge.style.setProperty('--accent-color', 'var(--success-color)');
    }
    
    // Render Rejection Reasons
    if (data.rejection_reasons && data.rejection_reasons.length > 0) {
        const reasonsContainer = document.getElementById('reasonsContainer');
        const reasonsList = document.getElementById('reasonsList');
        reasonsContainer.classList.remove('hidden');
        
        data.rejection_reasons.forEach(reason => {
            const card = document.createElement('div');
            card.className = 'card';
            card.textContent = reason;
            reasonsList.appendChild(card);
        });
    }
    
    // Render Similar Titles
    if (data.similar_titles && data.similar_titles.length > 0) {
        const similarContainer = document.getElementById('similarContainer');
        const similarList = document.getElementById('similarList');
        similarContainer.classList.remove('hidden');
        
        // Show top 5 matches
        data.similar_titles.slice(0, 5).forEach(item => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const titleSpan = document.createElement('span');
            titleSpan.textContent = item.existing_title;
            
            const matchSpan = document.createElement('span');
            matchSpan.className = 'match-percent';
            matchSpan.textContent = `${item.match_percentage}% Match (${item.match_type})`;
            
            card.appendChild(titleSpan);
            card.appendChild(matchSpan);
            similarList.appendChild(card);
        });
    }
    
    if ((!data.rejection_reasons || data.rejection_reasons.length === 0) && 
        (!data.similar_titles || data.similar_titles.length === 0)) {
        document.getElementById('successMessage').classList.remove('hidden');
    }
}
