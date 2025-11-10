# How Product Detection Works

This document explains the technical mechanism behind how the price tracker detects product information from e-commerce websites.

## 🔄 Detection Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Provides Product URL                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: HTTP Request (with User-Agent header to avoid blocks)  │
│  GET https://www.amazon.com/product/12345                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Receive HTML Response                                   │
│  <!DOCTYPE html>                                                  │
│  <html>                                                           │
│    <h1 id="productTitle">iPhone 15 Pro</h1>                       │
│    <span class="a-price-whole">999</span>                         │
│    ...                                                            │
│  </html>                                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Parse HTML with BeautifulSoup                           │
│  soup = BeautifulSoup(html, 'lxml')                              │
│  Creates a searchable tree structure of the HTML                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Extract Each Field Using 3-Tier Strategy               │
│  • Product Name                                                  │
│  • Price                                                         │
│  • Description                                                   │
│  • Images                                                        │
│  • Currency                                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Return Product Object                                   │
│  Product(                                                         │
│    name="iPhone 15 Pro",                                          │
│    price=999.0,                                                   │
│    description="...",                                             │
│    images=[...],                                                  │
│    currency="USD"                                                 │
│  )                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 3-Tier Detection Strategy

For EACH field (name, price, description, etc.), the scraper tries:

### Tier 1: Site-Specific Configuration ⭐ (Highest Priority)

```python
# Check if we have a custom selector in config/sites.json
if 'name_selector' in self.config:
    element = soup.select_one(self.config['name_selector'])
    if element:
        return element.get_text(strip=True)
```

**Example config/sites.json:**
```json
{
  "amazon.com": {
    "name_selector": "#productTitle"
  }
}
```

If found → ✅ Use this, stop searching

If not found → ⬇️ Continue to Tier 2

---

### Tier 2: Common E-commerce Patterns 🔍 (Medium Priority)

```python
# Try a list of common selectors used by most e-commerce sites
selectors = [
    'h1[itemprop="name"]',        # Schema.org standard
    'h1.product-title',            # Common class name
    'h1#productTitle',             # Amazon, eBay
    'h1.product-name',             # Shopify, WooCommerce
    '[data-testid="product-title"]' # Modern React apps
]

for selector in selectors:
    element = soup.select_one(selector)
    if element:
        return element.get_text(strip=True)
```

If found → ✅ Use this, stop searching

If not found → ⬇️ Continue to Tier 3

---

### Tier 3: Generic Fallback 📦 (Lowest Priority)

```python
# Last resort: find ANY h1 tag
h1 = soup.find('h1')
return h1.get_text(strip=True) if h1 else "Unknown Product"
```

Always returns something (even if it's "Unknown Product")

---

## 📊 Real Example: Detecting from Amazon

Let's trace how each field is detected from an actual Amazon product page:

### HTML Structure (simplified):

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="description" content="Apple iPhone 15 Pro with titanium design">
</head>
<body>
    <div id="dp-container">
        <!-- Product Title -->
        <h1 id="productTitle" class="product-title">
            Apple iPhone 15 Pro (128 GB) - Natural Titanium
        </h1>

        <!-- Price Section -->
        <div id="corePrice">
            <span class="a-price-symbol">$</span>
            <span class="a-price-whole">999</span>
            <span class="a-price-fraction">00</span>
        </div>

        <!-- Description -->
        <div id="productDescription">
            <p>Forged in titanium and featuring the groundbreaking A17 Pro chip...</p>
        </div>

        <!-- Images -->
        <img id="landingImage"
             src="https://m.media-amazon.com/images/I/81dT7CUY6GL._AC_SL1500_.jpg"
             alt="iPhone 15 Pro">

        <div id="altImages">
            <img src="https://m.media-amazon.com/images/I/81KK2NXhp5L._AC_SL1500_.jpg">
            <img src="https://m.media-amazon.com/images/I/71T1u9mjLIL._AC_SL1500_.jpg">
        </div>
    </div>
</body>
</html>
```

### Detection Process:

#### 🏷️ **1. Product Name**

```
Tier 1: Check config/sites.json for "amazon.com"
  → Found: "name_selector": "#productTitle"
  → selector: #productTitle
  → element: <h1 id="productTitle">Apple iPhone 15 Pro (128 GB)...</h1>
  → text: "Apple iPhone 15 Pro (128 GB) - Natural Titanium"
  ✅ SUCCESS - Use this value
```

**Code:** `src/scraper.py:70-76`

---

#### 💰 **2. Price**

```
Tier 1: Check config for "amazon.com"
  → Found: "price_selector": ".a-price-whole"
  → selector: .a-price-whole
  → element: <span class="a-price-whole">999</span>
  → text: "999"
  → Parse: _parse_price("999")
    • Input: "999"
    • Remove non-numeric: "999"
    • Convert to float: 999.0
  ✅ SUCCESS - Return 999.0
```

**Code:** `src/scraper.py:127-133` and `src/scraper.py:162-171`

---

#### 📝 **3. Description**

```
Tier 1: Check config for "amazon.com"
  → Found: "description_selector": "#productDescription"
  → selector: #productDescription
  → element: <div id="productDescription"><p>Forged in titanium...</p></div>
  → text: "Forged in titanium and featuring the groundbreaking A17 Pro chip..."
  ✅ SUCCESS - Use this value
```

**Code:** `src/scraper.py:99-105`

---

#### 🖼️ **4. Image URLs**

```
Tier 1: Check config for "amazon.com"
  → Found: "image_selector": "#landingImage"
  → selector: #landingImage
  → element: <img id="landingImage" src="https://m.media-amazon.com/...">
  → Extract: src attribute → "https://m.media-amazon.com/images/I/81dT7CUY6GL._AC_SL1500_.jpg"

Also find gallery images:
  → selector: #landingImage, #imgTagWrapperId img
  → Find all matching <img> tags
  → Extract src, data-src, data-lazy-src attributes
  → Results: [
      "https://m.media-amazon.com/images/I/81dT7CUY6GL._AC_SL1500_.jpg",
      "https://m.media-amazon.com/images/I/81KK2NXhp5L._AC_SL1500_.jpg",
      "https://m.media-amazon.com/images/I/71T1u9mjLIL._AC_SL1500_.jpg"
    ]
  ✅ SUCCESS - Return list of image URLs (max 5)
```

**Code:** `src/scraper.py:201-249`

---

#### 💱 **5. Currency**

```
Tier 1: Check config
  → Found: "currency_selector": ".a-price-symbol"
  → selector: .a-price-symbol
  → element: <span class="a-price-symbol">$</span>
  → text: "$"

Tier 2: Detect from symbol
  → If '$' in text: return 'USD'
  ✅ SUCCESS - Return "USD"
```

**Code:** `src/scraper.py:173-199`

---

## 🔧 CSS Selector Explanation

CSS selectors are patterns used to find HTML elements:

| Selector Type | Syntax | Example | Matches |
|--------------|--------|---------|---------|
| **ID** | `#id` | `#productTitle` | `<h1 id="productTitle">` |
| **Class** | `.class` | `.price` | `<span class="price">` |
| **Tag** | `tag` | `h1` | `<h1>` |
| **Attribute** | `[attr="value"]` | `[itemprop="name"]` | `<h1 itemprop="name">` |
| **Combination** | `tag.class` | `h1.title` | `<h1 class="title">` |
| **Child** | `parent > child` | `div > span` | Direct child only |
| **Descendant** | `parent child` | `div span` | Any nested level |

### How BeautifulSoup Uses Selectors:

```python
soup = BeautifulSoup(html, 'lxml')

# Find first matching element
element = soup.select_one('#productTitle')
# Returns: <h1 id="productTitle">iPhone 15 Pro</h1>

# Get text content
text = element.get_text(strip=True)
# Returns: "iPhone 15 Pro"

# Find all matching elements
elements = soup.select('.product-image img')
# Returns: [<img src="1.jpg">, <img src="2.jpg">, ...]

# Get attribute value
img_url = element.get('src')
# Returns: "https://example.com/image.jpg"
```

---

## 🎨 Visual Detection Example

```
┌─────────────────────────────────────────────────────────────┐
│  HTML PAGE: https://amazon.com/product/12345                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  <h1 id="productTitle">iPhone 15 Pro</h1>  ◄─── [NAME]     │
│         │                                                    │
│         └─► Selector: #productTitle                         │
│             Tier 1: ✅ Config match                          │
│             Extract: "iPhone 15 Pro"                         │
│                                                              │
│  <span class="a-price-whole">999</span>  ◄───── [PRICE]    │
│         │                                                    │
│         └─► Selector: .a-price-whole                        │
│             Tier 1: ✅ Config match                          │
│             Extract: "999"                                   │
│             Parse: remove "$," → 999.0                       │
│                                                              │
│  <div id="productDescription">                              │
│    <p>Premium smartphone...</p>           ◄───── [DESC]     │
│  </div>                                                      │
│         │                                                    │
│         └─► Selector: #productDescription                   │
│             Tier 1: ✅ Config match                          │
│             Extract: "Premium smartphone..."                │
│                                                              │
│  <img src="https://.../phone.jpg">       ◄────── [IMAGE]   │
│         │                                                    │
│         └─► Selector: img[itemprop="image"]                 │
│             Tier 2: ✅ Common pattern                        │
│             Extract: "https://.../phone.jpg"                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                         ⬇️

┌─────────────────────────────────────────────────────────────┐
│  EXTRACTED PRODUCT OBJECT                                    │
├─────────────────────────────────────────────────────────────┤
│  {                                                           │
│    "name": "iPhone 15 Pro",                                  │
│    "price": 999.0,                                           │
│    "description": "Premium smartphone...",                   │
│    "currency": "USD",                                        │
│    "image_urls": ["https://.../phone.jpg"],                 │
│    "site_name": "amazon.com"                                 │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Adding Brand Detection

Currently, the app doesn't extract brand names, but here's how you would add it:

### 1. Update Model (`src/models.py`):

```python
@dataclass
class Product:
    # ... existing fields ...
    brand: str = ""  # Add this
```

### 2. Update Database (`src/database.py`):

```python
# In _create_tables():
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        ...existing columns...,
        brand TEXT,  # Add this
        ...
    )
""")
```

### 3. Add Extraction Method (`src/scraper.py`):

```python
def _extract_brand(self, soup: BeautifulSoup) -> str:
    """Extract brand name from the page."""
    # Tier 1: Site config
    if 'brand_selector' in self.config:
        element = soup.select_one(self.config['brand_selector'])
        if element:
            return element.get_text(strip=True)

    # Tier 2: Common patterns
    selectors = [
        '[itemprop="brand"]',
        'a.brand',
        '#brand',
        '.product-brand',
        'meta[property="product:brand"]'
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            if element.name == 'meta':
                return element.get('content', '')
            return element.get_text(strip=True)

    return ""
```

### 4. Update Scraping Call:

```python
product = Product(
    # ... existing fields ...
    brand=self._extract_brand(soup),  # Add this
)
```

### 5. Update Config (`config/sites.json`):

```json
{
  "amazon.com": {
    "name_selector": "#productTitle",
    "brand_selector": "a#bylineInfo",  # Amazon brand link
    "price_selector": ".a-price-whole",
    ...
  }
}
```

---

## 🚨 Common Issues & Solutions

### Issue: "Failed to scrape product"

**Causes:**
1. Website blocks scraper (403/429 error)
2. JavaScript-rendered content
3. Wrong selectors

**Solutions:**
```python
# 1. Use Selenium for JavaScript sites
python main.py add "url" --selenium

# 2. Check if selectors are correct in browser console
document.querySelector('#productTitle')

# 3. Update User-Agent header (already done in scraper)
```

### Issue: Price shows as 0.0

**Causes:**
1. Price loaded via JavaScript
2. Wrong selector
3. Price in unexpected format

**Debug:**
```python
# Print HTML around price element
price_elements = soup.select('[class*="price"]')
for el in price_elements:
    print(f"{el.get('class')}: {el.get_text()}")
```

---

## 📚 Summary

**How detection works:**

1. **Fetch HTML** from product URL
2. **Parse** with BeautifulSoup
3. **For each field**, try:
   - Site-specific config selector
   - Common e-commerce patterns
   - Generic fallback
4. **Parse/clean** extracted text
5. **Return** Product object

**Key files:**
- `src/scraper.py` - Detection logic
- `config/sites.json` - Site-specific selectors
- `src/models.py` - Product data structure

**To support new sites:**
1. Inspect page in browser (F12)
2. Find unique selectors
3. Add to `config/sites.json`
4. Test with `python main.py add "url"`

See `docs/SELECTOR_GUIDE.md` for step-by-step instructions!
