# How to Scrape Instacart.com - Complete Guide

This guide will help you scrape product information (name, price, description, images) from Instacart.com.

## ⚠️ Important Notes

**Instacart is a JavaScript-heavy website**, which means:
- Product information is loaded dynamically with JavaScript
- You **MUST use the `--selenium` flag** for scraping to work
- Regular HTTP requests won't work properly

**Legal & Ethical:**
- Only scrape for personal use
- Respect Instacart's Terms of Service
- Don't overload their servers (add delays between requests)
- Consider using their official API if available

---

## 🚀 Quick Start

### 1. Install Dependencies

First, make sure you have all required packages:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Chrome and ChromeDriver (for Selenium)
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# On macOS:
brew install chromedriver

# On Windows:
# Download ChromeDriver from https://chromedriver.chromium.org/
```

### 2. Get a Product URL

Go to Instacart.com and find a product. The URL should look like:
```
https://www.instacart.com/store/items/item_12345678
```

### 3. Scrape the Product

**IMPORTANT: Use the `--selenium` flag for Instacart!**

```bash
python main.py add "https://www.instacart.com/store/items/item_12345678" --selenium
```

---

## 🔍 Finding the Correct Selectors

Instacart's HTML structure may change. Here's how to find the current selectors:

### Step 1: Open Product Page

1. Go to https://www.instacart.com
2. Search for a product (e.g., "bananas")
3. Click on a product to open its detail page

### Step 2: Open Developer Tools

1. Right-click on the product name → "Inspect" (or press F12)
2. This opens the browser Developer Tools

### Step 3: Find Product Name

In the Elements/Inspector tab:

1. Look for the `<h1>` tag containing the product name
2. Check for attributes like:
   - `data-testid="product-title"`
   - Class names like `e-1ydh7bl` or similar
3. Note the selector

**Example:**
```html
<h1 data-testid="product-title" class="e-1ydh7bl">Organic Bananas</h1>
```
→ Selector: `h1[data-testid="product-title"]`

### Step 4: Find Price

1. Right-click on the price → Inspect
2. Look for the element containing the price number

**Common patterns:**
```html
<!-- Option 1: data-testid -->
<span data-testid="product-price">$2.99</span>

<!-- Option 2: Class name -->
<span class="e-price">$2.99</span>

<!-- Option 3: Generic price class -->
<div class="product-price-container">
  <span class="current-price">$2.99</span>
</div>
```

### Step 5: Find Description

1. Scroll to product description section
2. Right-click → Inspect
3. Note the selector

**Common patterns:**
```html
<div data-testid="product-description">Fresh organic bananas...</div>
<div class="product-details">Fresh organic bananas...</div>
```

### Step 6: Find Images

1. Right-click on the product image → Inspect
2. Look for `<img>` tag and note the selector

**Common patterns:**
```html
<img data-testid="product-image" src="https://...">
<img class="product-image" src="https://...">
```

---

## 🛠️ Updating Configuration

If the default selectors don't work, update `config/sites.json`:

```json
{
  "instacart.com": {
    "name_selector": "YOUR_SELECTOR_HERE",
    "price_selector": "YOUR_SELECTOR_HERE",
    "description_selector": "YOUR_SELECTOR_HERE",
    "image_selector": "YOUR_SELECTOR_HERE"
  }
}
```

**Test your selectors in the browser console:**

```javascript
// Test if selector finds the element
document.querySelector('h1[data-testid="product-title"]')

// Test if you can get the text
document.querySelector('h1[data-testid="product-title"]').textContent

// Find all matching elements
document.querySelectorAll('[data-testid="product-price"]')
```

---

## 📝 Usage Examples

### Example 1: Track a Single Product

```bash
# Add product with Selenium
python main.py add "https://www.instacart.com/store/items/item_12345" --selenium
```

**Expected output:**
```
================================================================================
Product: Organic Bananas
================================================================================
ID: 1
URL: https://www.instacart.com/store/items/item_12345
Site: instacart.com
Current Price: USD 2.99

Description:
Fresh organic bananas, perfect for snacking or smoothies

Images (3):
  1. https://d2d8wwwkmhfcva.cloudfront.net/...
  2. https://d2d8wwwkmhfcva.cloudfront.net/...
  3. https://d2d8wwwkmhfcva.cloudfront.net/...

✓ Product added successfully!
```

### Example 2: Track Multiple Products

```bash
# Track multiple products
python main.py add "https://www.instacart.com/store/items/item_123" --selenium
python main.py add "https://www.instacart.com/store/items/item_456" --selenium
python main.py add "https://www.instacart.com/store/items/item_789" --selenium

# List all tracked products
python main.py list
```

### Example 3: Monitor Price Changes

```bash
# Add product
python main.py add "https://www.instacart.com/store/items/item_123" --selenium

# Wait some time (hours/days)...

# Update all products to check for price changes
python main.py update --selenium

# View price history
python main.py history 1
```

**Expected output:**
```
Price History for: Organic Bananas
================================================================================
Date                      Price           Change
--------------------------------------------------------------------------------
2025-11-10 10:00:00      USD 2.99
2025-11-10 18:00:00      USD 2.49        -0.50 ↓
2025-11-11 10:00:00      USD 2.99        +0.50 ↑
================================================================================
```

---

## 🐛 Troubleshooting

### Issue 1: "Failed to scrape product"

**Cause:** Not using Selenium for JavaScript-heavy site

**Solution:**
```bash
# Always use --selenium flag for Instacart
python main.py add "URL" --selenium
```

### Issue 2: ChromeDriver not found

**Error:** `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Or download manually and add to PATH
```

### Issue 3: Price shows as 0.0

**Cause:** Wrong selector or price loaded after page load

**Debug steps:**

1. Visit the product page in your browser
2. Open console (F12)
3. Run:
```javascript
// Find all elements with "price" in class/data attribute
Array.from(document.querySelectorAll('[class*="price"], [data-testid*="price"]'))
  .map(el => ({
    selector: el.className || el.getAttribute('data-testid'),
    text: el.textContent.trim()
  }))
```

4. Update the selector in `config/sites.json`

### Issue 4: Wrong product name extracted

**Cause:** Multiple h1 tags or wrong selector

**Solution:**

1. Find the most specific selector:
```javascript
// In browser console
document.querySelectorAll('h1').forEach(h1 => {
  console.log(h1.className, h1.textContent)
})
```

2. Update `name_selector` in config to the most specific one

### Issue 5: "403 Forbidden" or "429 Too Many Requests"

**Cause:** Instacart blocking automated requests

**Solutions:**
- Add delays between requests (already handled by Selenium)
- Use residential IP (not data center IPs)
- Consider using Instacart's API if available
- Reduce scraping frequency

---

## 💡 Pro Tips

### 1. Use Headless Mode

The scraper already runs in headless mode (no browser window). If you want to see the browser:

Edit `src/scraper.py` line 285 and comment out headless:
```python
options = Options()
# options.add_argument('--headless')  # Comment this line
```

### 2. Add Wait Time for Slow Loading

If elements don't load fast enough, edit `src/scraper.py` line 302:

```python
# Change from 3 seconds to 5 or more
time.sleep(5)  # Wait for page to load
```

### 3. Scrape Store-Specific Prices

Instacart prices vary by store. Make sure you:
1. Select your store on Instacart.com first
2. Copy product URL from that specific store
3. The price will be for that store

### 4. Track Price Drops with Automation

Create a cron job or scheduled task:

```bash
# Linux/Mac: Edit crontab
crontab -e

# Add this line to check prices every 6 hours
0 */6 * * * cd /path/to/pricetracker && python main.py update --selenium
```

---

## 🔬 Debug Helper Script

Save this as `debug_instacart.py`:

```python
#!/usr/bin/env python3
"""
Debug helper for finding Instacart selectors
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def debug_instacart(url):
    """Open Instacart product page and print all potential selectors."""

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    try:
        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load

        # JavaScript to find potential selectors
        script = """
        let results = {
            names: [],
            prices: [],
            descriptions: [],
            images: []
        };

        // Find potential product names (h1 tags)
        document.querySelectorAll('h1').forEach(h1 => {
            results.names.push({
                text: h1.textContent.trim().substring(0, 50),
                class: h1.className,
                id: h1.id,
                testid: h1.getAttribute('data-testid')
            });
        });

        // Find potential prices
        document.querySelectorAll('[class*="price"], [data-testid*="price"]').forEach(el => {
            if (el.textContent.includes('$') || el.textContent.match(/\\d+\\.\\d{2}/)) {
                results.prices.push({
                    text: el.textContent.trim(),
                    class: el.className,
                    testid: el.getAttribute('data-testid'),
                    tag: el.tagName
                });
            }
        });

        // Find potential descriptions
        document.querySelectorAll('[data-testid*="description"], [class*="description"]').forEach(el => {
            results.descriptions.push({
                text: el.textContent.trim().substring(0, 100),
                class: el.className,
                testid: el.getAttribute('data-testid')
            });
        });

        // Find images
        document.querySelectorAll('img').forEach(img => {
            if (img.src.includes('cloudfront') || img.alt.toLowerCase().includes('product')) {
                results.images.push({
                    src: img.src,
                    class: img.className,
                    testid: img.getAttribute('data-testid'),
                    alt: img.alt
                });
            }
        });

        return results;
        """

        results = driver.execute_script(script)

        print("\n" + "="*80)
        print("POTENTIAL PRODUCT NAMES:")
        print("="*80)
        for i, name in enumerate(results['names'], 1):
            print(f"\n{i}. Text: {name['text']}")
            if name['class']:
                print(f"   Selector: .{name['class'].split()[0]}")
            if name['id']:
                print(f"   Selector: #{name['id']}")
            if name['testid']:
                print(f"   Selector: [data-testid='{name['testid']}']")

        print("\n" + "="*80)
        print("POTENTIAL PRICES:")
        print("="*80)
        for i, price in enumerate(results['prices'], 1):
            print(f"\n{i}. Text: {price['text']}")
            if price['class']:
                print(f"   Selector: .{price['class'].split()[0]}")
            if price['testid']:
                print(f"   Selector: [data-testid='{price['testid']}']")

        print("\n" + "="*80)
        print("POTENTIAL DESCRIPTIONS:")
        print("="*80)
        for i, desc in enumerate(results['descriptions'][:3], 1):
            print(f"\n{i}. Text: {desc['text']}...")
            if desc['class']:
                print(f"   Selector: .{desc['class'].split()[0]}")
            if desc['testid']:
                print(f"   Selector: [data-testid='{desc['testid']}']")

        print("\n" + "="*80)
        print("IMAGES:")
        print("="*80)
        for i, img in enumerate(results['images'][:5], 1):
            print(f"\n{i}. {img['src'][:60]}...")
            if img['class']:
                print(f"   Selector: img.{img['class'].split()[0]}")
            if img['testid']:
                print(f"   Selector: img[data-testid='{img['testid']}']")

    finally:
        driver.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python debug_instacart.py <instacart-product-url>")
        sys.exit(1)

    debug_instacart(sys.argv[1])
```

**Usage:**
```bash
python debug_instacart.py "https://www.instacart.com/store/items/item_12345"
```

This will show you all potential selectors on the page!

---

## 📊 Expected Data Format

When successfully scraped, you'll get:

```python
Product(
    id=1,
    url="https://www.instacart.com/store/items/item_12345",
    name="Organic Bananas",
    description="Fresh organic bananas, 1 bunch",
    current_price=2.99,
    currency="USD",
    image_urls=[
        "https://d2d8wwwkmhfcva.cloudfront.net/800x800/filters:fill(...)",
        "https://d2d8wwwkmhfcva.cloudfront.net/800x800/filters:fill(...)"
    ],
    site_name="instacart.com",
    created_at=datetime(...),
    updated_at=datetime(...)
)
```

---

## 🎯 Summary

**To scrape Instacart:**

1. ✅ Install Selenium and ChromeDriver
2. ✅ Use `--selenium` flag ALWAYS
3. ✅ Find correct selectors using browser DevTools
4. ✅ Update `config/sites.json` if needed
5. ✅ Test with: `python main.py add "URL" --selenium`
6. ✅ Monitor prices with: `python main.py update --selenium`

**Key commands:**
```bash
# Add product
python main.py add "INSTACART_URL" --selenium

# List products
python main.py list

# View details
python main.py show 1

# View price history
python main.py history 1

# Update all
python main.py update --selenium
```

Good luck with your price tracking! 🚀
