// Site Configuration Editor JavaScript

let sitesConfig = {};
let currentSite = null;

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

    // Open URL button (opens in new tab)
    document.getElementById('open-url-btn').addEventListener('click', () => {
        const url = document.getElementById('test-url').value.trim();
        if (url) {
            openUrlInNewTab(url);
        } else {
            alert('Please enter a test URL first');
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

function openUrlInNewTab(url) {
    // Validate URL
    try {
        new URL(url);
    } catch (e) {
        alert('Please enter a valid URL (e.g., https://example.com/product/123)');
        return;
    }

    // Open URL in new tab
    const newTab = window.open(url, '_blank');

    if (newTab) {
        // Show instructions after a brief delay
        setTimeout(() => {
            alert('✅ Website opened in new tab!\n\n' +
                  '📋 Next Steps:\n\n' +
                  '1. Right-click on the element you want to select (product name, price, etc.)\n\n' +
                  '2. Select "Inspect" or "Inspect Element"\n\n' +
                  '3. In DevTools, right-click the highlighted HTML element\n\n' +
                  '4. Select "Copy → Copy selector"\n\n' +
                  '5. Paste the selector into the appropriate field here\n\n' +
                  '6. Click "Test" to verify it works!\n\n' +
                  'Tip: You can switch between tabs using Alt+Tab (Windows) or Cmd+Tab (Mac)');
        }, 500);
    } else {
        alert('⚠️ Pop-up blocked!\n\nYour browser blocked the new tab. Please:\n\n' +
              '1. Allow pop-ups for this site\n2. Or manually copy and paste the URL into a new tab');
    }
}
