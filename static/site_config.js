// Site Configuration Editor JavaScript

let sitesConfig = {};
let currentSite = null;
let inspectMode = false;

// Load configuration on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSitesConfig();
    setupEventListeners();
});

function setupEventListeners() {
    // Site selection
    document.getElementById('site-select').addEventListener('change', (e) => {
        loadSiteConfig(e.target.value);
    });

    // New site button
    document.getElementById('new-site-btn').addEventListener('click', () => {
        clearForm();
        document.getElementById('site-domain').disabled = false;
        document.getElementById('delete-site-btn').style.display = 'none';
        currentSite = null;
    });

    // Delete site button
    document.getElementById('delete-site-btn').addEventListener('click', () => {
        if (currentSite && confirm(`Are you sure you want to delete configuration for ${currentSite}?`)) {
            deleteSite(currentSite);
        }
    });

    // Load URL button
    document.getElementById('load-url-btn').addEventListener('click', () => {
        const url = document.getElementById('test-url').value.trim();
        if (url) {
            loadUrlInIframe(url);
        } else {
            alert('Please enter a test URL');
        }
    });

    // Form submission
    document.getElementById('config-form').addEventListener('submit', (e) => {
        e.preventDefault();
        saveConfiguration();
    });

    // Reset button
    document.getElementById('reset-form-btn').addEventListener('click', () => {
        if (currentSite) {
            loadSiteConfig(currentSite);
        } else {
            clearForm();
        }
    });

    // Test buttons
    document.querySelectorAll('.btn-test').forEach(btn => {
        btn.addEventListener('click', () => {
            const field = btn.getAttribute('data-field');
            testSelector(field);
        });
    });

    // Inspect mode
    document.getElementById('inspect-mode-btn').addEventListener('click', () => {
        toggleInspectMode();
    });

    // Refresh iframe
    document.getElementById('refresh-iframe-btn').addEventListener('click', () => {
        const iframe = document.querySelector('#iframe-container iframe');
        if (iframe) {
            iframe.src = iframe.src;
        }
    });
}

async function loadSitesConfig() {
    try {
        const response = await fetch('/api/sites/config');
        sitesConfig = await response.json();

        // Populate dropdown
        const select = document.getElementById('site-select');
        select.innerHTML = '<option value="">-- Select a site to edit --</option>';

        Object.keys(sitesConfig).sort().forEach(site => {
            const option = document.createElement('option');
            option.value = site;
            option.textContent = site;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading sites config:', error);
        alert('Failed to load sites configuration');
    }
}

function loadSiteConfig(siteName) {
    if (!siteName) {
        clearForm();
        return;
    }

    currentSite = siteName;
    const config = sitesConfig[siteName];

    if (!config) {
        alert('Site configuration not found');
        return;
    }

    // Populate form
    document.getElementById('site-domain').value = siteName;
    document.getElementById('site-domain').disabled = true;
    document.getElementById('name-selector').value = config.name_selector || '';
    document.getElementById('price-selector').value = config.price_selector || '';
    document.getElementById('description-selector').value = config.description_selector || '';
    document.getElementById('image-selector').value = config.image_selector || '';
    document.getElementById('currency-selector').value = config.currency_selector || '';
    document.getElementById('upc-selector').value = config.upc_selector || '';

    document.getElementById('delete-site-btn').style.display = 'inline-block';
}

function clearForm() {
    document.getElementById('config-form').reset();
    document.getElementById('site-domain').disabled = false;
    document.getElementById('delete-site-btn').style.display = 'none';
    document.getElementById('test-results').style.display = 'none';
    currentSite = null;
}

async function saveConfiguration() {
    const domain = document.getElementById('site-domain').value.trim();

    if (!domain) {
        alert('Please enter a site domain');
        return;
    }

    // Build configuration object
    const config = {
        name_selector: document.getElementById('name-selector').value.trim(),
        price_selector: document.getElementById('price-selector').value.trim(),
        description_selector: document.getElementById('description-selector').value.trim(),
        image_selector: document.getElementById('image-selector').value.trim()
    };

    // Add optional fields if provided
    const currencySelector = document.getElementById('currency-selector').value.trim();
    if (currencySelector) {
        config.currency_selector = currencySelector;
    }

    const upcSelector = document.getElementById('upc-selector').value.trim();
    if (upcSelector) {
        config.upc_selector = upcSelector;
    }

    // Update local config
    sitesConfig[domain] = config;

    // Save to server
    try {
        const response = await fetch('/api/sites/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sitesConfig)
        });

        const result = await response.json();

        if (response.ok) {
            alert('✅ Configuration saved successfully!');
            await loadSitesConfig();

            // Select the saved site
            document.getElementById('site-select').value = domain;
            loadSiteConfig(domain);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        alert('Failed to save configuration');
    }
}

async function deleteSite(siteName) {
    delete sitesConfig[siteName];

    try {
        const response = await fetch('/api/sites/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sitesConfig)
        });

        const result = await response.json();

        if (response.ok) {
            alert(`✅ Site "${siteName}" deleted successfully!`);
            await loadSitesConfig();
            clearForm();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error deleting site:', error);
        alert('Failed to delete site');
    }
}

async function testSelector(fieldName) {
    const url = document.getElementById('test-url').value.trim();

    if (!url) {
        alert('Please enter a test URL first');
        return;
    }

    const selectorMap = {
        'name': 'name-selector',
        'price': 'price-selector',
        'description': 'description-selector',
        'image': 'image-selector',
        'currency': 'currency-selector',
        'upc': 'upc-selector'
    };

    const selectorId = selectorMap[fieldName];
    const selector = document.getElementById(selectorId).value.trim();

    if (!selector) {
        alert('Please enter a selector to test');
        return;
    }

    // Show loading
    const testResults = document.getElementById('test-results');
    const testOutput = document.getElementById('test-output');
    testResults.style.display = 'block';
    testOutput.innerHTML = '<div style="text-align:center;padding:20px;">Testing selector...</div>';

    try {
        const response = await fetch('/api/sites/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                selector: selector,
                field_type: fieldName === 'image' ? 'image' : 'text'
            })
        });

        const result = await response.json();

        if (response.ok) {
            if (result.found) {
                let html = `
                    <div class="test-result">
                        <strong>✅ ${result.message}</strong>
                    </div>
                `;

                result.results.forEach(item => {
                    html += `
                        <div class="test-result">
                            <strong>Element ${item.index}:</strong> &lt;${item.tag}&gt;
                            ${item.classes.length > 0 ? `<br><small>Classes: ${item.classes.join(', ')}</small>` : ''}
                            <br><code>${item.value}</code>
                        </div>
                    `;
                });

                testOutput.innerHTML = html;
            } else {
                testOutput.innerHTML = `
                    <div class="test-result error">
                        <strong>❌ ${result.message}</strong>
                    </div>
                `;
            }
        } else {
            testOutput.innerHTML = `
                <div class="test-result error">
                    <strong>Error:</strong> ${result.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error testing selector:', error);
        testOutput.innerHTML = `
            <div class="test-result error">
                <strong>Error:</strong> ${error.message}
            </div>
        `;
    }
}

function loadUrlInIframe(url) {
    const container = document.getElementById('iframe-container');

    // Remove placeholder or existing iframe
    container.innerHTML = '';

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = url;
    iframe.sandbox = 'allow-scripts allow-same-origin';
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';

    iframe.onerror = () => {
        container.innerHTML = `
            <div class="iframe-placeholder">
                <p style="color:#ef4444;">❌ Failed to load URL</p>
                <p style="color:#666;">The website may block iframe embedding (CORS policy)</p>
                <p style="color:#666;">Try using browser DevTools to inspect the page instead</p>
            </div>
        `;
    };

    container.appendChild(iframe);

    // Show message about iframe limitations
    alert('Note: Some websites block iframe embedding. If the page doesn\'t load, use browser DevTools to inspect elements instead.');
}

function toggleInspectMode() {
    inspectMode = !inspectMode;

    const btn = document.getElementById('inspect-mode-btn');
    const info = document.getElementById('inspector-info');

    if (inspectMode) {
        btn.textContent = '🔍 Inspect Mode: ON';
        btn.style.background = '#10b981';
        info.style.display = 'block';

        alert('Inspect mode enabled!\n\nNote: Due to browser security, you cannot inspect elements inside the iframe.\n\nInstead:\n1. Right-click the page in the iframe\n2. Select "Inspect" or "Inspect Element"\n3. Use browser DevTools to find CSS selectors');
    } else {
        btn.textContent = '🔍 Inspect Mode';
        btn.style.background = '';
        info.style.display = 'none';
    }
}
