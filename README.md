# E-Commerce Price Tracker

A powerful and flexible Python-based price tracker for monitoring product prices across multiple e-commerce websites. Track product information including name, description, price, and images, with full price history tracking.

## Features

- **Multi-site Support**: Works with Amazon, eBay, Walmart, Etsy, Best Buy, and more
- **Flexible Scraping**: Supports both simple HTTP requests and Selenium for JavaScript-heavy sites
- **Price History**: Automatically tracks price changes over time
- **Product Information**: Extracts product name, description, price, currency, and image URLs
- **Site Configuration**: Easy-to-configure site-specific selectors
- **SQLite Database**: Lightweight database for storing products and price history
- **CLI Interface**: Simple command-line interface for managing tracked products

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pricetracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) For Selenium support, install ChromeDriver:
```bash
# On Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# On macOS
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

## Usage

### Track a Product

Add a product to start tracking its price:

```bash
python main.py add "https://www.amazon.com/product-url"
```

For JavaScript-heavy sites, use Selenium:

```bash
python main.py add "https://www.website.com/product" --selenium
```

### List All Tracked Products

View all products you're tracking:

```bash
python main.py list
```

### Show Product Details

Display detailed information about a specific product:

```bash
python main.py show 1
```

### View Price History

See how a product's price has changed over time:

```bash
python main.py history 1

# Show more records
python main.py history 1 --limit 50
```

### Update All Products

Refresh prices for all tracked products:

```bash
python main.py update
```

### Bulk Scraping (Scrape Multiple URLs)

**NEW!** Scrape multiple product URLs from a list with automatic rate limiting:

```bash
# Create a file with URLs (one per line)
# urls.txt:
#   https://distacart.com/products/product1
#   https://distacart.com/products/product2
#   https://distacart.com/products/product3

# Scrape all URLs with 5-second delay between requests
python bulk_scraper.py urls.txt --delay 5

# Or use the quick helper script
./quick_bulk_scrape.sh urls.txt 5
```

**Features:**
- Processes URLs one by one with configurable delays
- Automatically skips already-tracked products
- Shows progress and statistics
- Handles errors gracefully and continues
- Saves results to a file

**See [BULK_SCRAPING_GUIDE.md](BULK_SCRAPING_GUIDE.md) for complete documentation.**

### Web UI (Upload Files & Monitor Progress)

**NEW!** User-friendly web interface with real-time progress tracking:

```bash
# Start the web server
python web_app.py

# Open browser: http://localhost:5000
```

**Features:**
- 📤 Upload URL files (.txt or .csv)
- 📊 Real-time progress monitoring
- 🔄 Background processing (continues even if you close browser)
- 📥 Download CSV results when complete
- 📱 Mobile-friendly interface
- 🎯 Multiple concurrent jobs
- ⚠️ Error tracking and reporting

**Perfect for:**
- Non-technical users
- Long-running bulk scraping
- Remote monitoring
- Team collaboration

**See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for complete documentation.**

## Project Structure

```
pricetracker/
├── config/
│   └── sites.json          # Site-specific CSS selector configurations
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models (Product, PriceHistory)
│   ├── database.py         # SQLite database operations
│   ├── scraper.py          # Web scraping logic
│   └── tracker.py          # Price tracking orchestration
├── data/
│   └── products.db         # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── main.py                 # CLI entry point
└── README.md
```

## How It Works

### Product Scraping

The scraper extracts product information using CSS selectors:

1. **Product Name**: Looks for common heading tags and product title elements
2. **Description**: Extracts from description meta tags or dedicated description sections
3. **Price**: Searches for price elements and parses numeric values
4. **Currency**: Detects from currency symbols or meta tags
5. **Images**: Collects product image URLs from various image containers

### Price Tracking

When you add or update a product:

1. The scraper fetches the current product page
2. Extracts all relevant information
3. Saves product data to the database
4. Records the current price in price history
5. On updates, compares with previous price and logs changes

### Site Configuration

The `config/sites.json` file contains site-specific CSS selectors:

```json
{
  "amazon.com": {
    "name_selector": "#productTitle",
    "price_selector": ".a-price-whole",
    "description_selector": "#productDescription",
    "image_selector": "#landingImage",
    "currency_selector": ".a-price-symbol"
  }
}
```

If no site-specific configuration exists, the scraper falls back to common patterns.

## Scraped Data

For each product, the tracker captures:

- **Product Name**: Full product title
- **Description**: Product description text
- **Current Price**: Latest price as a float
- **Currency**: Currency code (USD, EUR, GBP, etc.)
- **Image URLs**: List of product image URLs
- **Site Name**: Domain name of the e-commerce site
- **Timestamps**: Creation and last update times

## Price History

Every price check is recorded in the database, allowing you to:

- Track price trends over time
- Identify price drops or increases
- View historical pricing data
- Analyze price patterns

## Adding New Sites

To add support for a new e-commerce site:

1. Open `config/sites.json`
2. Add a new entry with the site's domain name
3. Specify CSS selectors for product elements:

```json
{
  "newsite.com": {
    "name_selector": ".product-title",
    "price_selector": ".price-value",
    "description_selector": ".product-description",
    "image_selector": ".product-images img",
    "currency_selector": ".currency"
  }
}
```

You can find the correct selectors by inspecting the site's HTML in your browser's developer tools.

## Examples

### Example 1: Track an Amazon Product

```bash
# Add the product
python main.py add "https://www.amazon.com/dp/B08N5WRWNW"

# View details
python main.py list

# Check price history later
python main.py update
python main.py history 1
```

### Example 2: Monitor Multiple Products

```bash
# Add several products
python main.py add "https://www.amazon.com/product1"
python main.py add "https://www.ebay.com/product2"
python main.py add "https://www.walmart.com/product3"

# Update all at once
python main.py update

# List all with current prices
python main.py list
```

### Example 3: Using as a Python Module

```python
from src.tracker import PriceTracker

# Initialize tracker
tracker = PriceTracker(config_path="config/sites.json")

# Track a product
product = tracker.track_product("https://www.amazon.com/product-url")

# Get all tracked products
products = tracker.get_all_products()

# Get price history
history = tracker.get_price_history(product_id=1)

# Display information
tracker.display_product_info(product)
tracker.display_price_history(product_id=1)

# Close connection
tracker.close()
```

## Limitations & Notes

- **Rate Limiting**: Be respectful of websites. Don't scrape too frequently.
- **Terms of Service**: Check each site's ToS before scraping.
- **Dynamic Content**: Some sites may require Selenium (use `--selenium` flag).
- **Anti-Bot Protection**: Some sites have bot detection that may block scrapers.
- **Selector Changes**: Sites may update their HTML, requiring selector updates.

## Troubleshooting

### "Failed to scrape product"

- The site may have changed its HTML structure
- Try using `--selenium` flag for JavaScript-heavy sites
- Check if the URL is correct and accessible
- Update selectors in `config/sites.json`

### Selenium errors

- Ensure ChromeDriver is installed and in PATH
- Check Chrome/Chromium browser is installed
- Try updating Selenium: `pip install --upgrade selenium`

### Price not detected

- Inspect the site's HTML to find the correct price selector
- Update `config/sites.json` with the correct selector
- Some sites use JavaScript to load prices (use `--selenium`)

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a pull request

## License

This project is for educational purposes. Always respect website terms of service and robots.txt files.

## Disclaimer

This tool is for personal use only. Users are responsible for complying with the terms of service of websites they scrape. The authors are not responsible for any misuse of this software.
