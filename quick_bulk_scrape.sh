#!/bin/bash
# Quick Bulk Scrape Helper Script
# Makes bulk scraping even easier

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Quick Bulk Scraper"
echo "=========================================="
echo ""

# Check if URL file provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quick_bulk_scrape.sh <url-file> [delay]"
    echo ""
    echo "Examples:"
    echo "  ./quick_bulk_scrape.sh urls.txt"
    echo "  ./quick_bulk_scrape.sh urls.txt 5"
    echo "  ./quick_bulk_scrape.sh products.csv 10"
    echo ""
    exit 1
fi

URL_FILE=$1
DELAY=${2:-5}  # Default delay 5 seconds

# Check if file exists
if [ ! -f "$URL_FILE" ]; then
    echo -e "${RED}❌ Error: File '$URL_FILE' not found${NC}"
    exit 1
fi

# Count URLs (excluding comments and empty lines)
URL_COUNT=$(grep -v "^#" "$URL_FILE" | grep -v "^$" | wc -l)

echo "📄 URL File: $URL_FILE"
echo "📊 Total URLs: $URL_COUNT"
echo "⏱️  Delay: $DELAY seconds per request"
echo ""

# Calculate estimated time
ESTIMATED_TIME=$((URL_COUNT * DELAY))
MINUTES=$((ESTIMATED_TIME / 60))
SECONDS=$((ESTIMATED_TIME % 60))

echo "⏰ Estimated time: ${MINUTES}m ${SECONDS}s"
echo ""

# Ask for confirmation
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Starting scrape..."
echo "=========================================="
echo ""

# Determine file format
if [[ $URL_FILE == *.csv ]]; then
    FORMAT_FLAG="--format csv"
else
    FORMAT_FLAG=""
fi

# Run bulk scraper
OUTPUT_FILE="results_$(date +%Y%m%d_%H%M%S).txt"

python bulk_scraper.py "$URL_FILE" $FORMAT_FLAG --delay "$DELAY" --output "$OUTPUT_FILE"

RESULT=$?

echo ""
echo "=========================================="

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Bulk scraping completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Scraping completed with some errors${NC}"
fi

echo "📄 Results saved to: $OUTPUT_FILE"
echo ""
echo "View your products:"
echo "  python main.py list"
echo ""
echo "View details:"
echo "  python main.py show <ID>"
echo ""
echo "Update prices:"
echo "  python main.py update"
echo ""
echo "=========================================="
