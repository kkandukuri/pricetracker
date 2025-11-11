# Scraping iHerb.com - Complete Guide

Guide for scraping products from iHerb.com.

## 🚀 Quick Start

### Method 1: Command Line

```bash
# Try without Selenium first
python main.py add "https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453"

# If that doesn't work, use Selenium (recommended for iHerb)
python main.py add "https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453" --selenium
```

### Method 2: Web UI

```bash
# Start web server
python web_app.py

# In browser (http://localhost:5000):
# 1. Upload file with iHerb URLs
# 2. Check "Use Selenium" checkbox
# 3. Set delay to 5+ seconds
# 4. Click "Start Scraping"
```

### Method 3: Bulk Scraping

```bash
# Create URL file
cat > iherb_urls.txt << 'EOF'
https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453
https://www.iherb.com/pr/another-product/123
https://www.iherb.com/pr/another-product/456
EOF

# Scrape with Selenium
python bulk_scraper.py iherb_urls.txt --selenium --delay 5
```

---

## ⚙️ Configuration

iHerb configuration has been added to `config/sites.json`:

```json
"iherb.com": {
  "name_selector": "h1#name, h1.product-title, h1[itemprop='name'], h1",
  "price_selector": "#price, .price, .product-price, b[itemprop='price'], span[itemprop='price']",
  "description_selector": "#product-summary, .product-description, [itemprop='description'], div.product-overview",
  "image_selector": "#iherb-product-image, img[itemprop='image'], .product-image img",
  "currency_selector": ".currency, span.currency-symbol"
}
```

---

## 🐛 Troubleshooting

### Issue: "Failed to scrape product"

**Solution 1: Use Selenium**

iHerb loads content dynamically with JavaScript. Use `--selenium` flag:

```bash
python main.py add "URL" --selenium
```

**Solution 2: Install ChromeDriver**

```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Verify installation
which chromedriver
```

**Solution 3: Check if URL is correct**

Make sure the URL is a direct product page:
- ✅ Correct: `https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453`
- ❌ Wrong: `https://www.iherb.com/search?kw=calcium`

---

### Issue: "Price shows as 0.0"

**Find the correct price selector:**

1. Open the product page in your browser
2. Right-click on the price → "Inspect"
3. Look at the HTML element containing the price
4. Note the class or id

**Example:**
```html
<span class="product-price" id="price">$18.50</span>
```

Update `config/sites.json`:
```json
"price_selector": ".product-price, #price"
```

---

### Issue: "Wrong product name extracted"

**Find the correct name selector:**

1. Open product page in browser
2. Right-click on product name → "Inspect"
3. Look for the `<h1>` tag
4. Note the class or id

**Example:**
```html
<h1 id="name" itemprop="name">NOW Foods Calcium & Magnesium</h1>
```

Update `config/sites.json`:
```json
"name_selector": "h1#name, h1[itemprop='name']"
```

---

## 🔍 How to Find Correct Selectors

### Step 1: Open Browser DevTools

1. Go to iHerb product page
2. Press `F12` to open Developer Tools
3. Click the "Select Element" tool (top-left corner icon)

### Step 2: Inspect Elements

**For Product Name:**
- Click on the product name
- Look at the highlighted HTML in DevTools
- Find the selector (e.g., `h1#name`)

**For Price:**
- Click on the price
- Look at the HTML
- Find the selector (e.g., `.product-price`)

**For Description:**
- Click on the description text
- Find the container element
- Note the selector

**For Images:**
- Right-click on product image → Inspect
- Find the `<img>` tag
- Note the class or id

### Step 3: Test in Browser Console

```javascript
// Test product name selector
document.querySelector('h1#name').textContent

// Test price selector
document.querySelector('.product-price').textContent

// Test if selector finds element
document.querySelector('YOUR_SELECTOR')
// Should return an HTML element, not null
```

### Step 4: Update Configuration

Edit `config/sites.json` with your findings:

```bash
nano config/sites.json
```

Update the iHerb section with correct selectors.

---

## 📋 Example: Finding iHerb Selectors

### Real Example

Visit: https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453

**1. Product Name:**
```html
<h1 id="name" itemprop="name">NOW Foods, Calcium & Magnesium, 250 Tablets</h1>
```
→ Selector: `h1#name` or `h1[itemprop='name']`

**2. Price:**
```html
<span class="product-price">
  <b itemprop="price">$18.50</b>
</span>
```
→ Selector: `b[itemprop='price']` or `.product-price b`

**3. Description:**
```html
<div id="product-summary" itemprop="description">
  High quality calcium and magnesium supplement...
</div>
```
→ Selector: `#product-summary` or `[itemprop='description']`

**4. Image:**
```html
<img id="iherb-product-image" itemprop="image" src="..." alt="NOW Foods, Calcium & Magnesium">
```
→ Selector: `#iherb-product-image` or `img[itemprop='image']`

---

## 🎯 Best Practices for iHerb

### 1. Always Use Selenium

iHerb heavily relies on JavaScript:

```bash
# Always use --selenium flag
python main.py add "URL" --selenium
```

### 2. Use Appropriate Delays

```bash
# 5+ seconds between requests
python bulk_scraper.py urls.txt --selenium --delay 5
```

### 3. Handle Regions

iHerb shows different prices based on region. Make sure you're seeing the correct region:

- Check your iHerb region settings
- Prices may vary by country
- Currency may be different

### 4. Respect Rate Limits

```bash
# Don't scrape too fast
# Use 5-10 second delays
python bulk_scraper.py urls.txt --selenium --delay 10
```

---

## 💡 Tips

### Tip 1: Test with Single URL First

```bash
# Test with one product
python main.py add "https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453" --selenium

# Check if it worked
python main.py list
python main.py show 1

# If good, proceed with bulk
```

### Tip 2: Check Product Page Manually

Before scraping, open the product page in your browser:
- Is the page loading correctly?
- Can you see the price?
- Is the product available?
- Are you seeing the right region/currency?

### Tip 3: Export and Verify

```bash
# After scraping
python export_csv.py --output iherb_products.csv

# Open CSV and verify:
# - Are prices correct?
# - Are names correct?
# - Are descriptions present?
```

---

## 🔄 Update Existing Products

```bash
# Update all iHerb products
python main.py update --selenium

# View price changes
python main.py history 1
```

---

## 📊 Sample Workflow

### Complete Example: Scrape 10 iHerb Products

```bash
# 1. Create URL list
cat > iherb_supplements.txt << 'EOF'
https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453
https://www.iherb.com/pr/another-product/123
# ... add more URLs
EOF

# 2. Test with first URL
head -1 iherb_supplements.txt > test.txt
python bulk_scraper.py test.txt --selenium --delay 5

# 3. Check result
python main.py list

# 4. If good, scrape all
python bulk_scraper.py iherb_supplements.txt --selenium --delay 5

# 5. Export to CSV
python export_csv.py --output iherb_products.csv --include-images

# 6. Open CSV in Excel/Google Sheets
# Verify all data looks correct

# Done! 🎉
```

---

## 🆘 Still Not Working?

### Debug Steps

**1. Check if page loads manually:**
```bash
# Try accessing page directly
curl -A "Mozilla/5.0" "https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453"
```

**2. Check Selenium setup:**
```bash
# Verify ChromeDriver
which chromedriver
chromedriver --version

# Test Selenium
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit(); print('✓ Selenium works')"
```

**3. Try with Web UI:**
```bash
python web_app.py
# Upload file with iHerb URLs
# Check "Use Selenium"
# Monitor progress and errors
```

**4. Check logs for errors:**
```bash
# Look for specific error messages
# Share error message for help
```

---

## 📞 Getting Help

**If still having issues:**

1. Check the error message carefully
2. Verify ChromeDriver is installed
3. Make sure using `--selenium` flag
4. Test with a different iHerb product URL
5. Check if iHerb website is accessible from your location

**Provide these details when asking for help:**
- The exact URL you're trying to scrape
- The command you're using
- The error message (complete output)
- Your Python version: `python --version`
- Selenium installed: `pip list | grep selenium`
- ChromeDriver installed: `which chromedriver`

---

## ✅ Quick Checklist

Before scraping iHerb:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] ChromeDriver installed (`sudo apt-get install chromium-chromedriver`)
- [ ] Using `--selenium` flag
- [ ] Using appropriate delay (5+ seconds)
- [ ] Product URL is direct product page
- [ ] Tested with single URL first

---

**Happy Scraping! 🚀**
