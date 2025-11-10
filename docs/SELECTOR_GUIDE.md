"""
Guide: How to Find CSS Selectors for New E-commerce Sites

This guide explains how to find the right CSS selectors for extracting
product information from a new e-commerce website.

=============================================================================
STEP 1: Open Browser Developer Tools
=============================================================================

1. Visit the product page you want to scrape
2. Right-click on the product name → "Inspect" or press F12
3. This opens the browser's Developer Tools

=============================================================================
STEP 2: Find the Product Name Element
=============================================================================

In the Elements/Inspector tab:

1. Hover over HTML elements - the page will highlight corresponding parts
2. Find the element containing the product name
3. Look for unique identifiers:

   Good examples:
   <h1 id="product-title">iPhone 15</h1>
   → Selector: #product-title  or  h1#product-title

   <h1 class="pdp-title">iPhone 15</h1>
   → Selector: .pdp-title  or  h1.pdp-title

   <h1 itemprop="name">iPhone 15</h1>
   → Selector: h1[itemprop="name"]

=============================================================================
STEP 3: Find the Price Element
=============================================================================

1. Right-click on the price → Inspect
2. Look for the element containing the numeric price

   Examples:
   <span class="price-now">$999.99</span>
   → Selector: .price-now

   <div data-price="999.99">$999.99</div>
   → Selector: [data-price]

   <span itemprop="price">999.99</span>
   → Selector: [itemprop="price"]

=============================================================================
STEP 4: Find Description Element
=============================================================================

1. Scroll to product description
2. Right-click → Inspect
3. Find the container element

   Examples:
   <div class="product-description">...</div>
   → Selector: .product-description

   <div id="desc">...</div>
   → Selector: #desc

=============================================================================
STEP 5: Find Image Elements
=============================================================================

1. Right-click on product image → Inspect
2. Look for <img> tags

   Examples:
   <img class="product-img" src="...">
   → Selector: .product-img

   <img data-testid="main-image" src="...">
   → Selector: [data-testid="main-image"]

=============================================================================
STEP 6: Test Your Selectors
=============================================================================

In the browser Console tab, test selectors:

// Test if selector finds the element
document.querySelector('#product-title')

// Test if it gets the right text
document.querySelector('#product-title').textContent

// Test if it finds all images
document.querySelectorAll('.product-img')

=============================================================================
STEP 7: Add to Configuration File
=============================================================================

Edit config/sites.json:

{
  "yoursite.com": {
    "name_selector": "#product-title",
    "price_selector": ".price-now",
    "description_selector": ".product-description",
    "image_selector": ".product-img",
    "currency_selector": ".currency"
  }
}

=============================================================================
CSS SELECTOR CHEAT SHEET
=============================================================================

Type                Example              Matches
-------------------------------------------------------------------
ID                  #productTitle        <... id="productTitle">
Class               .product-name        <... class="product-name">
Tag                 h1                   <h1>
Attribute           [itemprop="name"]    <... itemprop="name">
Data attribute      [data-price]         <... data-price="...">
Combination         h1.title             <h1 class="title">
Child               div > span           <div><span>...</span></div>
Descendant          div span             <div>...<span>...</span></div>

=============================================================================
TIPS FOR FINDING GOOD SELECTORS
=============================================================================

✅ PREFER:
  - IDs: #productTitle (most specific, unique)
  - Data attributes: [data-testid="price"]
  - Semantic attributes: [itemprop="name"]
  - Specific classes: .product-price-final

❌ AVOID:
  - Generic classes: .text, .container, .item
  - Position-based: div:nth-child(3)
  - Overly complex: div > div > div > span.text
  - Dynamic classes: .css-1a2b3c4 (auto-generated)

=============================================================================
EXAMPLE: Adding Support for a Custom Site
=============================================================================

Let's say you want to add "customshop.com":

1. Visit: https://customshop.com/product/12345

2. Inspect and find:
   - Name: <h2 class="product__title">Cool Widget</h2>
   - Price: <span class="money">$49.99</span>
   - Description: <div class="rte">Description here</div>
   - Images: <img class="product__photo" src="...">

3. Add to config/sites.json:

{
  "customshop.com": {
    "name_selector": ".product__title",
    "price_selector": ".money",
    "description_selector": ".rte",
    "image_selector": ".product__photo"
  }
}

4. Test:
python main.py add "https://customshop.com/product/12345"

=============================================================================
TROUBLESHOOTING
=============================================================================

Problem: "Failed to scrape product"
Solution:
  - Check if URL is accessible
  - Verify selectors in browser console
  - Try --selenium flag for JavaScript sites
  - Check if site blocks bots (403/429 errors)

Problem: Price shows as 0.0
Solution:
  - Check if price loads via JavaScript (use --selenium)
  - Verify price selector is correct
  - Check if price is in a different element (sale price, etc.)

Problem: No images found
Solution:
  - Check if images use lazy loading (data-src attribute)
  - Look for <picture> elements instead of <img>
  - Check if images are in JavaScript/JSON data

Problem: Wrong description extracted
Solution:
  - Make selector more specific
  - Check if there are multiple description sections
  - Try different description containers

=============================================================================
ADVANCED: Using Browser Console to Find Selectors
=============================================================================

// Find all elements with "price" in class name
Array.from(document.querySelectorAll('[class*="price"]'))
  .map(el => ({
    class: el.className,
    text: el.textContent.trim(),
    selector: `.${el.className.split(' ')[0]}`
  }))

// Find all images
Array.from(document.querySelectorAll('img'))
  .filter(img => img.src.includes('product'))
  .map(img => ({
    src: img.src,
    class: img.className,
    id: img.id
  }))

=============================================================================
"""

if __name__ == "__main__":
    print(__doc__)
