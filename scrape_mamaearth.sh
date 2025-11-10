#!/bin/bash
# Quick script to scrape Mamaearth Onion Shampoo from distacart.com

PRODUCT_URL="https://distacart.com/products/mamaearth-onion-shampoo-for-hair-fall-control"

echo "=========================================="
echo "Scraping Mamaearth Onion Shampoo"
echo "=========================================="
echo ""

# Check if dependencies are installed
echo "Step 1: Checking dependencies..."
if ! python -c "import bs4" 2>/dev/null; then
    echo "❌ BeautifulSoup4 not installed"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Find selectors
echo "Step 2: Finding CSS selectors..."
echo "Running: python find_selectors.py \"$PRODUCT_URL\""
echo ""
python find_selectors.py "$PRODUCT_URL"

echo ""
echo "=========================================="
echo "Step 3: Scraping the product..."
echo "=========================================="
echo ""

# Try scraping
python main.py add "$PRODUCT_URL"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "✅ Success! Product added."
    echo ""
    echo "View your tracked products:"
    echo "  python main.py list"
    echo ""
    echo "View product details:"
    echo "  python main.py show 1"
    echo ""
    echo "View price history:"
    echo "  python main.py history 1"
else
    echo ""
    echo "❌ Scraping failed. Try with Selenium:"
    echo "  python main.py add \"$PRODUCT_URL\" --selenium"
    echo ""
    echo "Make sure ChromeDriver is installed:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-chromedriver"
    echo "  macOS: brew install chromedriver"
fi

echo ""
echo "=========================================="
