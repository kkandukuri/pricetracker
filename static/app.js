// Price Tracker Web UI - Frontend JavaScript

let pollingInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadJobs();
    setupFormHandler();

    // Poll for updates every 2 seconds
    pollingInterval = setInterval(() => {
        loadStats();
        loadJobs();
    }, 2000);
});

// Setup form submission
function setupFormHandler() {
    const form = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const btnText = uploadBtn.querySelector('.btn-text');
    const btnSpinner = uploadBtn.querySelector('.btn-spinner');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const fileInput = document.getElementById('file-input');
        const delayInput = document.getElementById('delay-input');
        const seleniumInput = document.getElementById('selenium-input');

        if (!fileInput.files.length) {
            alert('Please select a file');
            return;
        }

        // Disable button and show spinner
        uploadBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline';

        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('delay', delayInput.value);
        formData.append('selenium', seleniumInput.checked);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert(`Job started! Scraping ${data.total_urls} URLs. Job ID: ${data.job_id}`);
                form.reset();
                loadJobs(); // Refresh job list immediately
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            // Re-enable button
            uploadBtn.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
        }
    });
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('total-products').textContent = stats.total_products;
        document.getElementById('running-jobs').textContent = stats.running_jobs;
        document.getElementById('completed-jobs').textContent = stats.completed_jobs;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load jobs list
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const jobs = await response.json();

        const container = document.getElementById('jobs-container');

        if (jobs.length === 0) {
            container.innerHTML = '<p class="empty-state">No jobs yet. Upload a file to start scraping.</p>';
            return;
        }

        // Sort jobs by created date (newest first)
        jobs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        container.innerHTML = jobs.map(job => renderJob(job)).join('');
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

// Render single job
function renderJob(job) {
    const progress = job.total > 0 ? Math.round((job.current / job.total) * 100) : 0;
    const statusClass = `status-${job.status}`;

    let actionsHtml = '';
    if (job.status === 'completed' && job.download_file) {
        actionsHtml = `
            <div class="job-actions">
                <a href="/api/download/${job.id}" class="btn btn-success" download>
                    📥 Download CSV
                </a>
            </div>
        `;
    } else if (job.status === 'running') {
        actionsHtml = `
            <div class="job-actions">
                <button class="btn btn-danger" onclick="cancelJob('${job.id}')">
                    ❌ Cancel Job
                </button>
            </div>
        `;
    }

    let currentUrlHtml = '';
    if (job.status === 'running' && job.current_url) {
        currentUrlHtml = `
            <div class="current-url">
                <strong>Current URL:</strong> ${escapeHtml(job.current_url)}
            </div>
        `;
    }

    let errorsHtml = '';
    if (job.errors && job.errors.length > 0) {
        const errorsList = job.errors.slice(0, 5).map(err => `
            <div class="error-item">
                <strong>URL:</strong> ${escapeHtml(err.url)}<br>
                <strong>Error:</strong> ${escapeHtml(err.error)}
            </div>
        `).join('');

        const moreErrors = job.errors.length > 5 ? `<p><em>...and ${job.errors.length - 5} more errors</em></p>` : '';

        errorsHtml = `
            <div class="errors-container">
                <div class="errors-title">⚠️ Errors (${job.errors.length}):</div>
                ${errorsList}
                ${moreErrors}
            </div>
        `;
    }

    return `
        <div class="job-item">
            <div class="job-header">
                <div class="job-title">
                    📄 ${escapeHtml(job.filename)}
                </div>
                <div class="job-status ${statusClass}">
                    ${job.status}
                </div>
            </div>

            <div class="job-info">
                <div class="info-item">
                    <div class="info-label">Progress</div>
                    <div class="info-value">${job.current} / ${job.total}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Success</div>
                    <div class="info-value" style="color: #10b981">${job.success}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Failed</div>
                    <div class="info-value" style="color: #ef4444">${job.failed}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Delay</div>
                    <div class="info-value">${job.delay}s</div>
                </div>
            </div>

            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%">
                        ${progress}%
                    </div>
                </div>
            </div>

            ${currentUrlHtml}

            <div class="job-info" style="margin-top: 15px">
                <div class="info-item">
                    <div class="info-label">Created</div>
                    <div class="info-value" style="font-size: 0.9rem">${formatDate(job.created_at)}</div>
                </div>
                ${job.completed_at ? `
                    <div class="info-item">
                        <div class="info-label">Completed</div>
                        <div class="info-value" style="font-size: 0.9rem">${formatDate(job.completed_at)}</div>
                    </div>
                ` : ''}
                ${job.started_at && job.completed_at ? `
                    <div class="info-item">
                        <div class="info-label">Duration</div>
                        <div class="info-value" style="font-size: 0.9rem">${formatDuration(job.started_at, job.completed_at)}</div>
                    </div>
                ` : ''}
            </div>

            ${errorsHtml}
            ${actionsHtml}
        </div>
    `;
}

// Cancel job
async function cancelJob(jobId) {
    if (!confirm('Are you sure you want to cancel this job?')) {
        return;
    }

    try {
        const response = await fetch(`/api/jobs/${jobId}/cancel`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            alert('Job cancelled');
            loadJobs();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDuration(startString, endString) {
    const start = new Date(startString);
    const end = new Date(endString);
    const diff = Math.abs(end - start);

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    } else {
        return `${seconds}s`;
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
});
