// Products Page JavaScript

// Load products on page load
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    loadProductStats();
});

async function loadProducts() {
    const container = document.getElementById('products-container');

    try {
        const response = await fetch('/api/products/all');
        const products = await response.json();

        if (products.length === 0) {
            container.innerHTML = '<p class="empty-state">No products tracked yet. Start scraping to see products here.</p>';
            return;
        }

        // Create table
        let html = `
            <table class="products-table">
                <thead>
                    <tr>
                        <th>Image</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>UPC</th>
                        <th>Site</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
        `;

        products.forEach(product => {
            const imageUrl = product.images && product.images.length > 0 ? product.images[0] : '';
            html += `
                <tr>
                    <td>
                        ${imageUrl ? `<img src="${imageUrl}" alt="${product.name}">` : '<div style="width:50px;height:50px;background:#f0f0f0;border-radius:6px;"></div>'}
                    </td>
                    <td>
                        <strong>${product.name.substring(0, 60)}${product.name.length > 60 ? '...' : ''}</strong>
                        <br>
                        <small class="product-url-cell" title="${product.url}">${product.url}</small>
                    </td>
                    <td>
                        <strong style="color:#10b981;font-size:1.1rem;">${product.currency} ${product.price.toFixed(2)}</strong>
                    </td>
                    <td>${product.upc || '-'}</td>
                    <td><span style="color:#667eea;">${product.site}</span></td>
                    <td><small>${new Date(product.updated_at).toLocaleString()}</small></td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p class="empty-state" style="color:#ef4444;">Error loading products: ${error.message}</p>`;
    }
}

async function loadProductStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('total-tracked').textContent = stats.total_products;

        // Calculate price statistics (simple version)
        const productsResponse = await fetch('/api/products/all');
        const products = await productsResponse.json();

        if (products.length > 0) {
            const totalPrice = products.reduce((sum, p) => sum + p.price, 0);
            const avgPrice = totalPrice / products.length;
            document.getElementById('avg-price').textContent = `$${avgPrice.toFixed(2)}`;

            // For now, set price drops to 0 (would need price history analysis)
            document.getElementById('price-drops').textContent = '0';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Export CSV button handler
document.getElementById('export-btn').addEventListener('click', async () => {
    alert('CSV export is available via the command line:\n\npython export_csv.py --output products.csv');
});
