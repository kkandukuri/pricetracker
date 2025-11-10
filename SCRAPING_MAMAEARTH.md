# Scraping Mamaearth Onion Shampoo from Distacart.com

## Product URL
https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control

## Step-by-Step Instructions

### Step 1: Install Dependencies

First, make sure all required packages are installed:

```bash
cd /home/user/pricetracker
pip install -r requirements.txt
```

### Step 2: Find the Correct Selectors

Run the automatic selector finder to analyze the page:

```bash
python find_selectors.py "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"
```

This will show you:
- Product name element and selector
- Price element and selector
- Description element and selector
- Image URLs and selectors

**If the page uses JavaScript to load content**, use Selenium:

```bash
# Install ChromeDriver first (if not already installed)
sudo apt-get install chromium-chromedriver  # Ubuntu/Debian
# OR
brew install chromedriver  # macOS

# Then run with Selenium
python find_selectors.py "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control" --selenium
```

### Step 3: Update Configuration (if needed)

If the selector finder suggests different selectors than the defaults, update `config/sites.json`:

```bash
nano config/sites.json
```

The tool will give you the exact configuration to add.

### Step 4: Scrape the Product

Try scraping without Selenium first:

```bash
python main.py add "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"
```

If that doesn't work (JavaScript-loaded content), use Selenium:

```bash
python main.py add "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control" --selenium
```

### Step 5: View the Results

```bash
# List all tracked products
python main.py list

# View detailed information
python main.py show 1

# View price history
python main.py history 1
```

## Expected Output

You should see something like:

```
================================================================================
Product: Mamaearth Onion Shampoo For Hair Fall Control
================================================================================
ID: 1
URL: https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control
Site: distacart.com
Current Price: USD 399.00

Description:
Mamaearth Onion Hair Fall Shampoo for Hair Growth & Hair Fall Control with
Onion Oil & Plant Keratin...

Images (3):
  1. https://distacart.com/cdn/shop/products/onion-shampoo-1.jpg
  2. https://distacart.com/cdn/shop/products/onion-shampoo-2.jpg
  3. https://distacart.com/cdn/shop/products/onion-shampoo-3.jpg

Created: 2025-11-10 12:00:00
Updated: 2025-11-10 12:00:00
================================================================================

✓ Product added successfully!
```

## Monitoring Price Changes

To track price changes over time:

```bash
# Update all products (run this periodically)
python main.py update

# Or for Selenium sites
python main.py update --selenium

# View price history
python main.py history 1
```

### Automate Price Checks

Create a cron job to check prices automatically:

```bash
# Edit crontab
crontab -e

# Add this line to check every 6 hours
0 */6 * * * cd /home/user/pricetracker && python main.py update

# Or for Selenium
0 */6 * * * cd /home/user/pricetracker && python main.py update --selenium
```

## Troubleshooting

### If scraping fails:

1. **Check if dependencies are installed:**
   ```bash
   pip list | grep -E "beautifulsoup4|requests|selenium"
   ```

2. **Run the selector finder to debug:**
   ```bash
   python find_selectors.py "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"
   ```

3. **Try with Selenium (if JavaScript is used):**
   ```bash
   python main.py add "URL" --selenium
   ```

4. **Check the actual HTML structure:**
   - Open the product page in your browser
   - Right-click → "Inspect" (F12)
   - Look for product name, price, description elements
   - Update selectors in `config/sites.json`

### Common Issues:

**Issue: "ModuleNotFoundError: No module named 'bs4'"**
```bash
pip install -r requirements.txt
```

**Issue: "Failed to scrape product"**
- Try using `--selenium` flag
- Check if the URL is accessible
- Verify selectors with find_selectors.py

**Issue: "Price shows as 0.0"**
- Price might be loaded with JavaScript (use --selenium)
- Or selector might be wrong (use find_selectors.py to debug)

## Quick Command Reference

```bash
# 1. Find selectors
python find_selectors.py "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"

# 2. Scrape product
python main.py add "https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"

# 3. List products
python main.py list

# 4. View details
python main.py show 1

# 5. Update prices
python main.py update

# 6. View price history
python main.py history 1
```

## Next Steps

After successfully scraping this product, you can:

1. **Track more products:**
   ```bash
   python main.py add "https://distacart.com/products/another-product"
   ```

2. **Monitor all products:**
   ```bash
   python main.py update
   ```

3. **Export data programmatically:**
   ```python
   from src.tracker import PriceTracker

   tracker = PriceTracker()
   products = tracker.get_all_products()

   for product in products:
       print(f"{product.name}: {product.current_price}")
   ```

Good luck! 🚀
