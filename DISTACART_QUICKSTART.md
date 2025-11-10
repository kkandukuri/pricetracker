# Quick Start: Scraping Distacart.com

This guide shows you how to scrape product information from distacart.com.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Product URL

Go to distacart.com and copy a product URL. It should look something like:
```
https://www.distacart.com/product/...
```

### 3. Scrape the Product

Try without Selenium first:
```bash
python main.py add "https://www.distacart.com/product/YOUR-PRODUCT-URL"
```

If that doesn't work (site uses JavaScript), use Selenium:
```bash
# Install ChromeDriver first (see below)
python main.py add "https://www.distacart.com/product/YOUR-PRODUCT-URL" --selenium
```

---

## 📋 Step-by-Step Instructions

### Step 1: Find the Right Selectors

Since I don't have access to distacart.com's current structure, you'll need to find the correct CSS selectors:

1. **Open a product page on distacart.com**
2. **Right-click on the product name** → "Inspect" (or press F12)
3. **Look for the HTML element** containing the product name

**Example - you might see:**
```html
<h1 class="product-title">Organic Apples</h1>
```

4. **Note the selector**: `.product-title` or `h1.product-title`

5. **Repeat for:**
   - Price element
   - Description element
   - Image elements

### Step 2: Test Selectors in Browser Console

Open browser console (F12 → Console tab) and test:

```javascript
// Test product name selector
document.querySelector('h1.product-title').textContent

// Test price selector
document.querySelector('.product-price').textContent

// Test if multiple selectors work
document.querySelectorAll('.product-image img')
```

### Step 3: Update Configuration (if needed)

If the default selectors don't work, edit `config/sites.json`:

```json
{
  "distacart.com": {
    "name_selector": "YOUR_NAME_SELECTOR",
    "price_selector": "YOUR_PRICE_SELECTOR",
    "description_selector": "YOUR_DESCRIPTION_SELECTOR",
    "image_selector": "YOUR_IMAGE_SELECTOR"
  }
}
```

**Replace with the actual selectors you found.**

### Step 4: Test Scraping

```bash
python main.py add "YOUR_DISTACART_PRODUCT_URL"
```

**Expected output:**
```
================================================================================
Product: Organic Apples
================================================================================
ID: 1
URL: https://www.distacart.com/product/12345
Site: distacart.com
Current Price: USD 4.99

Description:
Fresh organic apples, crisp and delicious

Images (2):
  1. https://distacart.com/images/apple1.jpg
  2. https://distacart.com/images/apple2.jpg

Created: 2025-11-10 12:00:00
Updated: 2025-11-10 12:00:00
================================================================================

✓ Product added successfully!
```

---

## 🛠️ Common Commands

### Track a product
```bash
python main.py add "DISTACART_URL"
```

### List all tracked products
```bash
python main.py list
```

### View product details
```bash
python main.py show 1
```

### View price history
```bash
python main.py history 1
```

### Update all products (check for price changes)
```bash
python main.py update
```

---

## 🐛 Troubleshooting

### Issue: "Failed to scrape product"

**Try using Selenium:**
```bash
python main.py add "URL" --selenium
```

**Install ChromeDriver:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver
```

### Issue: Price shows as 0.0

The selector might be wrong. Debug with:

```bash
# Create a test script
cat > test_distacart.py << 'EOF'
import requests
from bs4 import BeautifulSoup

url = "YOUR_DISTACART_URL"
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'lxml')

# Find all elements with "price" in class
price_elements = soup.find_all(class_=lambda x: x and 'price' in x.lower())
for i, el in enumerate(price_elements, 1):
    print(f"{i}. Class: {el.get('class')}")
    print(f"   Text: {el.get_text(strip=True)}")
    print()
EOF

python test_distacart.py
```

This will show you all elements with "price" in their class name.

### Issue: Wrong data extracted

1. **Check the URL** - Make sure you're on a product page
2. **Inspect the HTML** - Right-click → Inspect to see actual HTML structure
3. **Update selectors** in `config/sites.json`
4. **Use Selenium** if the site loads content with JavaScript

---

## 📊 Finding Selectors - Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│  DISTACART.COM PRODUCT PAGE                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  <h1 class="product-title">Organic Apples</h1>             │
│       ↑                                                      │
│       └─ Selector: .product-title or h1.product-title      │
│                                                              │
│  <div class="price-container">                              │
│    <span class="product-price">$4.99</span>                │
│           ↑                                                  │
│           └─ Selector: .product-price                       │
│  </div>                                                      │
│                                                              │
│  <div class="product-description">                          │
│    Fresh organic apples...                                  │
│    ↑                                                         │
│    └─ Selector: .product-description                        │
│  </div>                                                      │
│                                                              │
│  <img class="product-image" src="/images/apple.jpg">       │
│       ↑                                                      │
│       └─ Selector: .product-image or img.product-image     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Helper Script: Find Selectors Automatically

Save this as `find_distacart_selectors.py`:

```python
#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    print("Usage: python find_distacart_selectors.py <distacart-url>")
    sys.exit(1)

url = sys.argv[1]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching: {url}\n")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'lxml')

print("="*80)
print("POTENTIAL PRODUCT NAMES (h1 tags):")
print("="*80)
for i, h1 in enumerate(soup.find_all('h1')[:5], 1):
    print(f"\n{i}. Text: {h1.get_text(strip=True)[:60]}")
    if h1.get('class'):
        print(f"   Selector: h1.{h1.get('class')[0]}")
    if h1.get('id'):
        print(f"   Selector: h1#{h1.get('id')}")

print("\n" + "="*80)
print("POTENTIAL PRICES:")
print("="*80)
price_elements = soup.find_all(class_=lambda x: x and 'price' in str(x).lower())
for i, el in enumerate(price_elements[:10], 1):
    text = el.get_text(strip=True)
    if text and ('$' in text or any(c.isdigit() for c in text)):
        print(f"\n{i}. Text: {text}")
        if el.get('class'):
            print(f"   Selector: .{el.get('class')[0]}")

print("\n" + "="*80)
print("POTENTIAL DESCRIPTIONS:")
print("="*80)
desc_elements = soup.find_all(class_=lambda x: x and 'description' in str(x).lower())
for i, el in enumerate(desc_elements[:5], 1):
    print(f"\n{i}. Text: {el.get_text(strip=True)[:80]}...")
    if el.get('class'):
        print(f"   Selector: .{el.get('class')[0]}")

print("\n" + "="*80)
print("IMAGES:")
print("="*80)
for i, img in enumerate(soup.find_all('img')[:10], 1):
    print(f"\n{i}. src: {img.get('src', 'N/A')[:60]}")
    if img.get('class'):
        print(f"   Selector: img.{img.get('class')[0]}")
    print(f"   alt: {img.get('alt', 'N/A')}")

print("\n" + "="*80)
print("\nUpdate config/sites.json with the selectors you found!")
```

**Run it:**
```bash
python find_distacart_selectors.py "https://www.distacart.com/product/12345"
```

This will show you all potential selectors!

---

## ✅ Complete Example Workflow

```bash
# 1. Find selectors using helper script
python find_distacart_selectors.py "https://www.distacart.com/product/12345"

# 2. Update config/sites.json with correct selectors (if needed)
nano config/sites.json

# 3. Track the product
python main.py add "https://www.distacart.com/product/12345"

# 4. View the tracked product
python main.py list

# 5. Check price history later
python main.py update
python main.py history 1
```

---

## 📞 Need Help?

If you're still having issues:

1. **Check the URL** - Make sure it's a valid product page
2. **Look at the HTML** - Right-click → Inspect on the product page
3. **Run the helper script** - `find_distacart_selectors.py` to find selectors
4. **Try Selenium** - Use `--selenium` flag if JavaScript is involved
5. **Check the docs** - See `docs/HOW_DETECTION_WORKS.md` for details

Good luck with your price tracking! 🎯
