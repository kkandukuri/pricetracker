# Bulk Scraping Guide

This guide shows you how to scrape multiple product URLs efficiently and responsibly using the bulk scraper.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Preparing Your URL List](#preparing-your-url-list)
3. [Running the Bulk Scraper](#running-the-bulk-scraper)
4. [Rate Limiting & Best Practices](#rate-limiting--best-practices)
5. [Error Handling](#error-handling)
6. [Advanced Usage](#advanced-usage)

---

## 🚀 Quick Start

### Step 1: Create a URL list file

Create a text file with your URLs (one per line):

**urls.txt:**
```
https://distacart.com/products/product1
https://distacart.com/products/product2
https://distacart.com/products/product3
```

### Step 2: Run the bulk scraper

```bash
python bulk_scraper.py urls.txt
```

That's it! The scraper will:
- Process each URL one by one
- Wait 3 seconds between requests (default)
- Show progress as it goes
- Save all products to the database

---

## 📝 Preparing Your URL List

### Text File Format (Simple)

Create a `.txt` file with one URL per line:

**examples/urls.txt:**
```
# This is a comment - lines starting with # are ignored
https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control
https://distacart.com/products/another-product

# Empty lines are ignored too

https://distacart.com/products/third-product
```

**Tips:**
- Use `#` for comments
- Empty lines are skipped
- Mix URLs from different sites

### CSV File Format (Advanced)

Create a `.csv` file with additional metadata:

**examples/products.csv:**
```csv
url,category,notes,priority
https://distacart.com/products/product1,Beauty,Best seller,high
https://distacart.com/products/product2,Home,On sale,medium
https://distacart.com/products/product3,Electronics,New,low
```

**Benefits:**
- Organize products by category
- Add notes for reference
- Set priorities
- Track additional information

---

## 🔧 Running the Bulk Scraper

### Basic Usage

```bash
# Scrape from text file
python bulk_scraper.py urls.txt

# Scrape from CSV file
python bulk_scraper.py products.csv --format csv
```

### With Custom Delay

**IMPORTANT:** Use appropriate delays to be respectful and avoid getting blocked!

```bash
# 5 second delay (recommended for most sites)
python bulk_scraper.py urls.txt --delay 5

# 10 second delay (safer for sensitive sites)
python bulk_scraper.py urls.txt --delay 10

# 2 second delay (minimum, use carefully)
python bulk_scraper.py urls.txt --delay 2
```

### With Selenium (JavaScript Sites)

```bash
# Use Selenium for JavaScript-heavy sites
python bulk_scraper.py urls.txt --selenium --delay 5

# Required for sites like Instacart
python bulk_scraper.py instacart_urls.txt --selenium --delay 10
```

### Save Results to File

```bash
# Save scraping results to a file
python bulk_scraper.py urls.txt --output results.txt

# The file will contain:
# - Summary statistics
# - List of errors (if any)
# - Timestamp
```

### Quiet Mode (No Progress Output)

```bash
# Minimal output (useful for automation)
python bulk_scraper.py urls.txt --no-progress
```

---

## ⏱️ Rate Limiting & Best Practices

### Why Rate Limiting Matters

**Getting blocked:**
- Sending too many requests too quickly looks like a bot attack
- Websites will block your IP address
- You'll be unable to scrape any data

**Being respectful:**
- Don't overload the website's servers
- Respect the website's resources
- Follow their Terms of Service

### Recommended Delays

| Site Type | Recommended Delay | Example |
|-----------|------------------|---------|
| **Small sites** | 10-15 seconds | Local e-commerce stores |
| **Medium sites** | 5-10 seconds | Regional online shops |
| **Large sites** | 3-5 seconds | Amazon, Walmart, etc. |
| **JavaScript sites** | 5-10 seconds | Instacart, modern SPAs |

### Best Practices

✅ **DO:**
- Start with longer delays and reduce if needed
- Test with 2-3 URLs first
- Run scraping during off-peak hours
- Use `--selenium` only when necessary (slower)
- Monitor for errors and adjust

❌ **DON'T:**
- Use delays less than 2 seconds
- Scrape hundreds of products at once without testing
- Ignore error messages
- Run multiple scrapers simultaneously on the same site
- Scrape during peak business hours

### Example: Safe Bulk Scraping

```bash
# Test with small list first
python bulk_scraper.py test_urls.txt --delay 5

# If successful, run the full list
python bulk_scraper.py all_urls.txt --delay 5 --output results.txt

# For 100 URLs with 5-second delay:
# Total time = 100 * 5 = 500 seconds = ~8 minutes
```

---

## 🐛 Error Handling

The bulk scraper handles errors gracefully and continues processing remaining URLs.

### Common Errors

#### 1. "Failed to scrape product"

**Causes:**
- Wrong URL format
- Product page not accessible
- Incorrect selectors

**Solution:**
```bash
# Try individual URL first to debug
python main.py add "URL"

# Update selectors if needed
python find_selectors.py "URL"
```

#### 2. "403 Forbidden" or "429 Too Many Requests"

**Cause:** Website blocking your requests (too fast)

**Solution:**
```bash
# Increase delay
python bulk_scraper.py urls.txt --delay 10

# Wait 1 hour and try again
```

#### 3. "Connection timeout"

**Cause:** Network issues or slow website

**Solution:**
```bash
# The scraper will skip and continue
# Check the error report at the end
# Retry failed URLs later
```

#### 4. ChromeDriver errors (Selenium)

**Cause:** ChromeDriver not installed

**Solution:**
```bash
# Install ChromeDriver
sudo apt-get install chromium-chromedriver  # Linux
brew install chromedriver  # macOS
```

### Viewing Errors

After scraping completes, you'll see:

```
================================================================================
ERRORS
================================================================================

1. URL: https://distacart.com/products/invalid-product
   Error: Failed to scrape product

2. URL: https://distacart.com/products/another-error
   Error: Connection timeout
================================================================================
```

**To retry failed URLs:**

1. Create a new file with only the failed URLs
2. Increase the delay
3. Try with `--selenium` flag if needed

---

## 🚀 Advanced Usage

### Example 1: Scrape Multiple Sites

**mixed_urls.txt:**
```
https://distacart.com/products/product1
https://www.amazon.com/dp/B08N5WRWNW
https://www.walmart.com/ip/12345
https://distacart.com/products/product2
```

```bash
python bulk_scraper.py mixed_urls.txt --delay 5
```

The scraper automatically detects the site and uses appropriate selectors!

### Example 2: Resume After Interruption

If scraping is interrupted (Ctrl+C or error):

```bash
# Check which products were already added
python main.py list

# The scraper automatically skips already-tracked URLs
# Just run it again with the same file
python bulk_scraper.py urls.txt --delay 5
```

Already-tracked products will show: `✓ Already tracked (ID: 1)`

### Example 3: Automated Daily Scraping

Create a script to scrape new products daily:

**daily_scrape.sh:**
```bash
#!/bin/bash
cd /home/user/pricetracker

# Scrape new products
python bulk_scraper.py daily_urls.txt --delay 5 --output "results_$(date +%Y%m%d).txt"

# Update existing products
python main.py update

# Send notification (optional)
echo "Daily scraping completed" | mail -s "Price Tracker Update" you@email.com
```

Set up cron job:
```bash
crontab -e

# Run every day at 2 AM
0 2 * * * /home/user/pricetracker/daily_scrape.sh
```

### Example 4: Scrape by Category

Organize URLs by category in CSV:

**products_by_category.csv:**
```csv
url,category,priority
https://distacart.com/products/beauty1,Beauty,high
https://distacart.com/products/beauty2,Beauty,high
https://distacart.com/products/home1,Home,medium
https://distacart.com/products/electronics1,Electronics,low
```

```bash
python bulk_scraper.py products_by_category.csv --format csv --delay 5
```

### Example 5: Monitor Specific Products

Track competitor products:

**competitor_products.txt:**
```
# Competitor A
https://distacart.com/products/competitor-a-product1
https://distacart.com/products/competitor-a-product2

# Competitor B
https://distacart.com/products/competitor-b-product1
https://distacart.com/products/competitor-b-product2
```

```bash
# Initial scrape
python bulk_scraper.py competitor_products.txt --delay 5

# Daily updates (cron job)
0 9 * * * cd /home/user/pricetracker && python main.py update
```

---

## 📊 Output Example

Here's what you'll see when running bulk scraper:

```
================================================================================
BULK SCRAPING STARTED
================================================================================
Total URLs: 5
Delay between requests: 5 seconds
Using Selenium: False
Started at: 2025-11-10 14:30:00
================================================================================

[1/5] Processing: https://distacart.com/products/product1
  ✓ Added successfully (ID: 1)
  ⏳ Waiting 5 seconds before next request...

[2/5] Processing: https://distacart.com/products/product2
  ✓ Added successfully (ID: 2)
  ⏳ Waiting 5 seconds before next request...

[3/5] Processing: https://distacart.com/products/product3
  ✓ Already tracked (ID: 1)
  ⏳ Waiting 5 seconds before next request...

[4/5] Processing: https://distacart.com/products/product4
  ✗ Failed to scrape product
  ⏳ Waiting 5 seconds before next request...

[5/5] Processing: https://distacart.com/products/product5
  ✓ Added successfully (ID: 3)

================================================================================
BULK SCRAPING COMPLETED
================================================================================
Total URLs processed: 5
✓ Successful: 4
✗ Failed: 1
⏱  Time taken: 28.45 seconds
⚡ Average time per URL: 5.69 seconds
================================================================================

================================================================================
ERRORS
================================================================================

1. URL: https://distacart.com/products/product4
   Error: Failed to scrape product
================================================================================
```

---

## 💡 Tips & Tricks

### 1. Start Small

```bash
# Test with 3-5 URLs first
head -5 all_urls.txt > test_urls.txt
python bulk_scraper.py test_urls.txt --delay 5
```

### 2. Calculate Time

```bash
# Formula: URLs × Delay = Total seconds
# Example: 100 URLs × 5 seconds = 500 seconds = ~8 minutes
```

### 3. Split Large Lists

```bash
# Split into chunks of 50
split -l 50 all_urls.txt chunk_

# Scrape each chunk separately
python bulk_scraper.py chunk_aa --delay 5
python bulk_scraper.py chunk_ab --delay 5
```

### 4. Monitor System Resources

For Selenium scraping, monitor memory:
```bash
# Check memory usage
free -h

# Limit concurrent Chrome instances
# (Use bulk_scraper.py which handles one at a time)
```

### 5. Backup Database

```bash
# Before bulk scraping
cp data/products.db data/products.db.backup

# If something goes wrong, restore:
cp data/products.db.backup data/products.db
```

---

## 🎯 Complete Workflow Example

Let's scrape 50 distacart.com products:

```bash
# Step 1: Create URL list
cat > distacart_products.txt << 'EOF'
https://distacart.com/products/product1
https://distacart.com/products/product2
# ... add 48 more URLs
EOF

# Step 2: Test with first 3 URLs
head -3 distacart_products.txt > test.txt
python bulk_scraper.py test.txt --delay 5

# Step 3: If successful, run full list
python bulk_scraper.py distacart_products.txt --delay 5 --output results.txt

# Step 4: View results
python main.py list

# Step 5: Check for errors
cat results.txt

# Step 6: Retry failed URLs (if any)
# Extract failed URLs from results.txt
# Create new file with only those URLs
# Run again with longer delay or --selenium

# Step 7: Set up daily updates
crontab -e
# Add: 0 9 * * * cd /home/user/pricetracker && python main.py update
```

**Time calculation:**
- 50 URLs × 5 seconds = 250 seconds = ~4 minutes
- Very reasonable!

---

## ⚖️ Legal & Ethical Considerations

**Always:**
- ✅ Read and respect the website's Terms of Service
- ✅ Check `robots.txt` file
- ✅ Use appropriate delays
- ✅ Scrape only for personal/research use
- ✅ Consider using official APIs if available

**Never:**
- ❌ Overwhelm small websites with requests
- ❌ Scrape copyrighted content for commercial use
- ❌ Ignore robots.txt
- ❌ Use scraped data to harm the business
- ❌ Sell or distribute scraped data

---

## 📚 Quick Reference

```bash
# Basic scraping
python bulk_scraper.py urls.txt

# With custom delay
python bulk_scraper.py urls.txt --delay 5

# With Selenium
python bulk_scraper.py urls.txt --selenium --delay 10

# From CSV
python bulk_scraper.py products.csv --format csv --delay 5

# Save results
python bulk_scraper.py urls.txt --output results.txt

# Quiet mode
python bulk_scraper.py urls.txt --no-progress

# Full example
python bulk_scraper.py distacart_urls.txt --delay 5 --output results.txt
```

---

## 🆘 Getting Help

**If scraping fails:**

1. Test single URL first:
   ```bash
   python main.py add "URL"
   ```

2. Find correct selectors:
   ```bash
   python find_selectors.py "URL"
   ```

3. Try with Selenium:
   ```bash
   python bulk_scraper.py urls.txt --selenium --delay 10
   ```

4. Check documentation:
   ```bash
   cat DISTACART_QUICKSTART.md
   cat docs/HOW_DETECTION_WORKS.md
   ```

**Need more help?** Check the main README.md or create an issue.

Happy scraping! 🚀
