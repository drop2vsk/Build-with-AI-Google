// Global state
let allJobs = [];
let selectedSkill = null;
let selectedPlatform = 'all';
let searchQuery = '';

// DOM Elements
const jobsContainer = document.getElementById('jobs-container');
const skillsContainer = document.getElementById('skills-container');
const skillsTotalCount = document.getElementById('skills-total-count');
const searchBox = document.getElementById('search-box');
const platformFilter = document.getElementById('platform-filter');
const clearFiltersBtn = document.getElementById('clear-filters-btn');
const refreshBtn = document.getElementById('refresh-btn');
const syncIcon = document.querySelector('.sync-icon');
const updateTimestamp = document.getElementById('update-timestamp');

// Fetch and load data
async function loadData(forceRefresh = false) {
    // Show loading states
    setLoadingState(true);
    if (forceRefresh) {
        syncIcon.classList.add('loading');
    }

    const endpoint = forceRefresh ? '/api/refresh' : '/api/jobs';
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (data.status === 'success') {
            allJobs = data.jobs;
            updateTimestamp.textContent = `Synced: ${data.last_updated}`;
            
            // Clear current filters on full refresh
            if (forceRefresh) {
                resetFilters();
            }
            
            filterAndRender();
        } else {
            showError('Failed to fetch job data from backend.');
        }
    } catch (error) {
        console.error('Error fetching jobs:', error);
        showError('Network error connecting to backend server.');
    } finally {
        setLoadingState(false);
        syncIcon.classList.remove('loading');
    }
}

// Reset filters to default
function resetFilters() {
    selectedSkill = null;
    selectedPlatform = 'all';
    searchQuery = '';
    searchBox.value = '';
    platformFilter.value = 'all';
    clearFiltersBtn.style.display = 'none';
}

// Set visual loading state
function setLoadingState(isLoading) {
    if (isLoading) {
        jobsContainer.innerHTML = `
            <div class="loader-container">
                <div class="spinner"></div>
                <p style="margin-top: 1rem;">Fetching Data Engineering job posts...</p>
            </div>
        `;
        skillsContainer.innerHTML = `
            <div class="loader-container" style="padding: 2rem 0;">
                <div class="spinner" style="width: 30px; height: 30px;"></div>
            </div>
        `;
    }
}

// Show error messages
function showError(message) {
    jobsContainer.innerHTML = `
        <div class="empty-state">
            <h3 style="color: #ef4444;">Connection Error</h3>
            <p>${message}</p>
            <button class="btn" style="margin-top: 1rem;" onclick="loadData()">Retry Connection</button>
        </div>
    `;
    skillsContainer.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 1rem;">Unable to load skills matrix.</p>`;
}

// Aggregate skill frequencies and metadata
function getAggregatedSkills(jobs) {
    const counts = {};
    const metadata = {};
    
    jobs.forEach(job => {
        if (job.skills && Array.isArray(job.skills)) {
            job.skills.forEach(skill => {
                const key = skill.key;
                counts[key] = (counts[key] || 0) + 1;
                if (!metadata[key]) {
                    metadata[key] = {
                        display_name: skill.display_name,
                        w3schools: skill.w3schools,
                        geeksforgeeks: skill.geeksforgeeks
                    };
                }
            });
        }
    });

    // Convert to sorted array by count descending
    return Object.keys(counts)
        .map(key => ({
            key: key,
            count: counts[key],
            ...metadata[key]
        }))
        .sort((a, b) => b.count - a.count);
}

// Apply searches and filter rules
function filterAndRender() {
    // 1. Filter jobs list
    const filteredJobs = allJobs.filter(job => {
        // Platform filter
        if (selectedPlatform !== 'all' && job.platform.toLowerCase() !== selectedPlatform) {
            return false;
        }

        // Selected skill filter
        if (selectedSkill) {
            const hasSkill = job.skills && job.skills.some(s => s.key === selectedSkill);
            if (!hasSkill) {
                return false;
            }
        }

        // Text search filter
        if (searchQuery.trim() !== '') {
            const query = searchQuery.toLowerCase();
            const titleMatch = job.title.toLowerCase().includes(query);
            const companyMatch = job.company.toLowerCase().includes(query);
            const descMatch = job.description.toLowerCase().includes(query);
            const skillMatch = job.skills && job.skills.some(s => s.display_name.toLowerCase().includes(query) || s.key.toLowerCase().includes(query));
            
            if (!titleMatch && !companyMatch && !descMatch && !skillMatch) {
                return false;
            }
        }

        return true;
    });

    // Update filter clearing button visibility
    if (selectedSkill || selectedPlatform !== 'all' || searchQuery.trim() !== '') {
        clearFiltersBtn.style.display = 'block';
    } else {
        clearFiltersBtn.style.display = 'none';
    }

    // 2. Render UI
    renderJobs(filteredJobs);
    
    // We aggregate skills based on the CURRENT filtered jobs list, or the TOTAL jobs?
    // Aggregating based on TOTAL jobs makes it a stable sidebar, which is better for navigation.
    const aggregatedSkills = getAggregatedSkills(allJobs);
    renderSkills(aggregatedSkills);
}

// Render Job Listing Cards
function renderJobs(jobs) {
    if (jobs.length === 0) {
        jobsContainer.innerHTML = `
            <div class="empty-state">
                <h3>No Matching Listings Found</h3>
                <p>Try refining your search terms or clearing the selected skill filter.</p>
            </div>
        `;
        return;
    }

    jobsContainer.innerHTML = '';
    jobs.forEach(job => {
        const card = document.createElement('article');
        card.className = 'job-card';
        card.id = `card-${job.id}`;
        
        // Build badges
        const platformClass = job.platform.toLowerCase();
        const skillBadges = job.skills.map(s => `<span class="skill-tag">${s.key}</span>`).join(' ');
        
        // Build learning tutorial links list
        let learningSection = '';
        if (job.skills && job.skills.length > 0) {
            const tutorialLinksHtml = job.skills.map(s => `
                <a href="${s.geeksforgeeks}" target="_blank" rel="noopener" class="kb-link gfg" title="Learn ${s.key} on GeeksforGeeks">
                    ${s.key} (GFG)
                </a>
                <a href="${s.w3schools}" target="_blank" rel="noopener" class="kb-link w3s" title="Learn ${s.key} on W3Schools">
                    ${s.key} (W3S)
                </a>
            `).join('');
            
            learningSection = `
                <div class="card-kb-section">
                    <span class="card-kb-label">Skill Lessons</span>
                    <div class="card-kb-list">
                        ${tutorialLinksHtml}
                    </div>
                </div>
            `;
        } else {
            learningSection = `
                <div class="card-kb-section">
                    <span class="card-kb-label">Skill Lessons</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">No specific technical skills extracted.</span>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="job-header">
                <div class="job-title-group">
                    <h3>${escapeHtml(job.title)}</h3>
                    <div class="job-meta">
                        <span class="job-company">${escapeHtml(job.company)}</span>
                        <span class="job-location">&bull; ${escapeHtml(job.location)}</span>
                    </div>
                </div>
                <span class="platform-badge ${platformClass}">${job.platform}</span>
            </div>
            
            <div class="job-skills">
                ${skillBadges}
            </div>
            
            <div class="job-description-preview" id="desc-${job.id}">
                ${formatDescription(job.description)}
            </div>
            
            <button class="expand-btn" onclick="toggleCardExpansion('${job.id}')" id="btn-exp-${job.id}">
                Show Description
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </button>
            
            <div class="job-footer">
                ${learningSection}
                <a href="${job.url}" target="_blank" rel="noopener" class="card-apply-link">
                    View Offer
                </a>
            </div>
        `;
        
        jobsContainer.appendChild(card);
    });
}

// Render Skill Sidebar List
function renderSkills(skills) {
    if (skills.length === 0) {
        skillsContainer.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 1rem;">No skills found.</p>`;
        skillsTotalCount.textContent = '0 Skills';
        return;
    }

    skillsTotalCount.textContent = `${skills.length} Skills`;
    skillsContainer.innerHTML = '';
    
    skills.forEach(skill => {
        const item = document.createElement('div');
        item.className = `skill-item ${selectedSkill === skill.key ? 'active' : ''}`;
        
        // Catch clicks on the list item itself to select the filter
        item.addEventListener('click', (e) => {
            // Prevent filter toggle if user clicks direct tutorial anchor links
            if (e.target.tagName.toLowerCase() === 'a') {
                return;
            }
            
            if (selectedSkill === skill.key) {
                selectedSkill = null; // Toggle off
            } else {
                selectedSkill = skill.key; // Set filter
            }
            filterAndRender();
        });

        item.innerHTML = `
            <div class="skill-header">
                <span class="skill-name">${skill.key}</span>
                <span class="skill-count-badge">${skill.count}</span>
            </div>
            <div class="kb-links">
                <a href="${skill.geeksforgeeks}" target="_blank" rel="noopener" class="kb-link gfg" title="GeeksforGeeks Tutorial for ${skill.key}">
                    GeeksforGeeks
                </a>
                <a href="${skill.w3schools}" target="_blank" rel="noopener" class="kb-link w3s" title="W3Schools Tutorial for ${skill.key}">
                    W3Schools
                </a>
            </div>
        `;
        
        skillsContainer.appendChild(item);
    });
}

// Toggle job card expand/collapse
function toggleCardExpansion(jobId) {
    const card = document.getElementById(`card-${jobId}`);
    const btn = document.getElementById(`btn-exp-${jobId}`);
    
    if (card.classList.contains('expanded')) {
        card.classList.remove('expanded');
        btn.innerHTML = `
            Show Description
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        `;
    } else {
        card.className = 'job-card expanded';
        btn.innerHTML = `
            Hide Description
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
        `;
    }
}

// Format newline descriptions to clean paragraphs
function formatDescription(desc) {
    if (!desc) return '';
    return desc.split('\n')
        .map(p => p.trim())
        .filter(p => p.length > 0)
        .map(p => `<p style="margin-bottom: 0.5rem;">${escapeHtml(p)}</p>`)
        .join('');
}

// Escape dangerous HTML tags
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Event Listeners
searchBox.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    filterAndRender();
});

platformFilter.addEventListener('change', (e) => {
    selectedPlatform = e.target.value;
    filterAndRender();
});

clearFiltersBtn.addEventListener('click', () => {
    resetFilters();
    filterAndRender();
});

refreshBtn.addEventListener('click', () => {
    loadData(true);
});

// Run app init on load
window.addEventListener('DOMContentLoaded', () => {
    loadData();
});
