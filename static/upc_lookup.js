// UPC Lookup Page JavaScript

// Single UPC lookup form handler
document.getElementById('single-upc-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const upc = document.getElementById('upc-input').value.trim();
    const lookupBtn = document.getElementById('lookup-btn');
    const btnText = lookupBtn.querySelector('.btn-text');
    const btnSpinner = lookupBtn.querySelector('.btn-spinner');
    const resultDiv = document.getElementById('single-result');
    const productCard = document.getElementById('product-card');

    // Disable button and show loading
    lookupBtn.disabled = true;
    btnText.textContent = 'Looking up...';
    btnSpinner.style.display = 'inline';

    try {
        const response = await fetch('/api/upc/lookup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                upc: upc,
                rate_limit: 20,
                country: 'US',
                currency: 'USD'
            })
        });

        const result = await response.json();

        if (result.found) {
            // Show product details
            productCard.innerHTML = `
                <div class="product-card">
                    ${result.image_url ? `<img src="${result.image_url}" alt="${result.name}" class="product-image">` : '<div class="product-image" style="background:#f0f0f0;display:flex;align-items:center;justify-content:center;">No Image</div>'}
                    <div class="product-details">
                        <h3 class="product-name">${result.name || 'Unknown Product'}</h3>
                        ${result.brand ? `<div class="product-brand">${result.brand}</div>` : ''}
                        <div>
                            <span class="product-price">$${result.price.toFixed(2)}</span>
                            ${result.list_price > result.price ? `<span class="product-list-price">$${result.list_price.toFixed(2)}</span>` : ''}
                            ${result.discount > 0 ? `<span class="product-discount">${result.discount}% OFF</span>` : ''}
                        </div>
                        <div class="product-meta">
                            <div class="product-meta-item">
                                <span>UPC:</span>
                                <strong>${result.upc}</strong>
                            </div>
                            <div class="product-meta-item">
                                <span>Stock:</span>
                                <strong class="${result.in_stock ? 'in-stock' : 'out-of-stock'}">${result.in_stock ? 'In Stock' : 'Out of Stock'}</strong>
                            </div>
                            ${result.rating > 0 ? `
                            <div class="product-meta-item">
                                <span>Rating:</span>
                                <strong>⭐ ${result.rating}/5 (${result.reviews} reviews)</strong>
                            </div>
                            ` : ''}
                        </div>
                        ${result.url ? `<a href="${result.url}" target="_blank" class="product-link">View on iHerb →</a>` : ''}
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';

            // Update stats
            const totalEl = document.getElementById('upc-total');
            const foundEl = document.getElementById('upc-found');
            totalEl.textContent = parseInt(totalEl.textContent || 0) + 1;
            foundEl.textContent = parseInt(foundEl.textContent || 0) + 1;
        } else {
            productCard.innerHTML = `
                <div class="empty-state" style="padding:30px;">
                    <p style="font-size:1.2rem;color:#ef4444;">❌ Product not found</p>
                    <p style="color:#666;margin-top:10px;">${result.error || 'This UPC code was not found in the iHerb database.'}</p>
                </div>
            `;
            resultDiv.style.display = 'block';

            // Update stats
            const totalEl = document.getElementById('upc-total');
            totalEl.textContent = parseInt(totalEl.textContent || 0) + 1;
        }
    } catch (error) {
        productCard.innerHTML = `
            <div class="empty-state" style="padding:30px;">
                <p style="font-size:1.2rem;color:#ef4444;">❌ Error</p>
                <p style="color:#666;margin-top:10px;">${error.message}</p>
            </div>
        `;
        resultDiv.style.display = 'block';
    } finally {
        // Re-enable button
        lookupBtn.disabled = false;
        btnText.textContent = 'Look Up Price';
        btnSpinner.style.display = 'none';
    }
});

// Batch UPC lookup form handler
document.getElementById('batch-upc-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    alert('Batch UPC lookup coming soon! For now, use the command-line tool:\n\npython upc_price_lookup.py --file upcs.txt');
});
