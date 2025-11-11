# UPC Price Lookup Guide

This guide explains how to use the UPC Price Lookup tool to fetch product prices from iHerb using UPC codes.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Input Formats](#input-formats)
- [Output Format](#output-format)
- [Rate Limiting](#rate-limiting)
- [AWS Lambda Deployment](#aws-lambda-deployment)
- [API Reference](#api-reference)

---

## Overview

The UPC Price Lookup tool queries the iHerb API to retrieve product information and prices for given UPC codes. It includes:
- Configurable rate limiting (default: 20 calls/minute)
- Browser-like headers to mimic real requests
- Batch processing from files
- CSV export functionality
- AWS Lambda deployment support

---

## Features

✅ **Single or Batch Lookups**: Process one UPC or thousands
✅ **Rate Limiting**: Configurable to avoid API blocking (default 20/min)
✅ **Multiple Input Formats**: Text files, CSV files, or command-line
✅ **Detailed Output**: Price, brand, rating, reviews, stock status, and more
✅ **CSV Export**: Results exported to CSV with timestamps
✅ **AWS Lambda Ready**: Deploy as serverless function
✅ **Progress Tracking**: Real-time progress display
✅ **Error Handling**: Graceful handling of failed lookups

---

## Quick Start

### 1. Look up a single UPC

```bash
python upc_price_lookup.py --upc 733739004536
```

### 2. Look up multiple UPCs from a file

```bash
# From text file
python upc_price_lookup.py --file examples/upcs.txt

# From CSV file
python upc_price_lookup.py --file examples/upcs_sample.csv
```

### 3. Custom rate limit and output

```bash
python upc_price_lookup.py --file upcs.txt --rate-limit 15 --output my_results.csv
```

---

## Usage Examples

### Example 1: Single UPC Lookup

```bash
python upc_price_lookup.py --upc 733739004536
```

**Output**:
```
================================================================================
UPC PRICE LOOKUP TOOL - iHerb API
================================================================================

Looking up 1 UPC codes...
Rate limit: 20 requests/minute
Estimated time: 0.1 minutes

[1/1] Looking up UPC: 733739004536... ✓ Found: NOW Foods, Calcium & Magnesium, 250 Tablets

✅ Results exported to: upc_prices_20241111_143022.csv

================================================================================
SUMMARY
================================================================================
Total UPCs processed: 1
Products found: 1
Not found: 0
Success rate: 100.0%

Results saved to: upc_prices_20241111_143022.csv
================================================================================
```

### Example 2: Multiple UPCs from Command Line

```bash
python upc_price_lookup.py --upc 733739004536 733739004543 NOW-00453
```

### Example 3: Batch Processing from File

```bash
python upc_price_lookup.py --file examples/upcs.txt --rate-limit 20 --output results.csv
```

### Example 4: Different Country/Currency

```bash
python upc_price_lookup.py --file upcs.txt --country CA --currency CAD
```

### Example 5: Quiet Mode (No Progress Output)

```bash
python upc_price_lookup.py --file upcs.txt --quiet
```

---

## Input Formats

### Text File Format (.txt)

Create a file with one UPC per line:

```txt
# Example: upcs.txt
# Lines starting with # are ignored

733739004536
733739004543
NOW-00453
012345678905
```

### CSV File Format (.csv)

Create a CSV with a 'UPC' column:

```csv
UPC,ProductName,Notes
733739004536,NOW Foods Calcium,Main product
733739004543,NOW Foods Magnesium,Secondary
NOW-00453,NOW Foods Supplement,iHerb code
```

**Note**: The tool looks for a column named 'UPC' or 'upc'. If not found, it uses the first column.

---

## Output Format

### CSV Columns

The output CSV contains these columns:

| Column | Description |
|--------|-------------|
| **UPC** | The UPC code searched |
| **Found** | Whether product was found (True/False) |
| **ProductID** | iHerb product ID |
| **Name** | Full product name |
| **Brand** | Brand name |
| **Price** | Current price |
| **ListPrice** | Original list price |
| **Discount** | Discount percentage |
| **Currency** | Currency code (USD, CAD, etc.) |
| **InStock** | Availability status (True/False) |
| **Rating** | Product rating (0-5) |
| **Reviews** | Number of reviews |
| **URL** | Product URL on iHerb |
| **ImageURL** | Product image URL |
| **Error** | Error message if lookup failed |
| **Timestamp** | When lookup was performed |

### Example Output CSV

```csv
UPC,Found,ProductID,Name,Brand,Price,ListPrice,Discount,Currency,InStock,Rating,Reviews,URL,ImageURL,Error,Timestamp
733739004536,True,453,NOW Foods Calcium & Magnesium 250 Tablets,NOW Foods,11.99,14.99,20,USD,True,4.5,1234,https://www.iherb.com/pr/NOW-00453,https://...,,"2024-11-11T14:30:22"
012345678905,False,,,,,,,,,,,,,No products found,2024-11-11T14:30:25
```

---

## Rate Limiting

### Why Rate Limiting?

Rate limiting prevents:
- API blocking from too many requests
- IP bans
- Service degradation

### Configuration

```bash
# Default: 20 calls per minute (3 seconds between calls)
python upc_price_lookup.py --file upcs.txt

# Conservative: 10 calls per minute (6 seconds between calls)
python upc_price_lookup.py --file upcs.txt --rate-limit 10

# Aggressive: 30 calls per minute (2 seconds between calls) - USE WITH CAUTION
python upc_price_lookup.py --file upcs.txt --rate-limit 30

# No rate limit (NOT RECOMMENDED)
python upc_price_lookup.py --file upcs.txt --rate-limit 0
```

### Recommendations

| Scenario | Recommended Rate | Reason |
|----------|-----------------|---------|
| **Testing** | 10 calls/min | Safe for initial tests |
| **Production** | 20 calls/min | Good balance |
| **High Volume** | 15 calls/min | More conservative |
| **24/7 Processing** | 10 calls/min | Safest for continuous use |

### Time Estimates

```
Rate: 20 calls/min = 3 seconds per UPC

100 UPCs  → ~5 minutes
500 UPCs  → ~25 minutes
1000 UPCs → ~50 minutes
5000 UPCs → ~4 hours
```

---

## AWS Lambda Deployment

The UPC Price Lookup tool can be deployed to AWS Lambda for serverless execution.

### Quick Lambda Deployment

```bash
# Make deployment script executable
chmod +x deployment/deploy_lambda.sh

# Deploy to AWS Lambda
./deployment/deploy_lambda.sh

# Test the function
aws lambda invoke \
  --function-name upc-price-lookup \
  --payload '{"upcs": ["733739004536"]}' \
  response.json
```

### Lambda Considerations

- **Timeout**: Set to 5-15 minutes depending on batch size
- **Memory**: 512 MB recommended
- **Max UPCs per invocation**: ~300 (with 15-min timeout)
- **Cost**: ~$1.50/month for 1000 lookups/day (within free tier)

See [AWS Lambda Deployment Guide](AWS_LAMBDA_DEPLOYMENT.md) for complete details.

---

## API Reference

### Command-Line Arguments

```
positional arguments:
  None

options:
  -h, --help            Show help message and exit

  --upc UPC [UPC ...], -u UPC [UPC ...]
                        UPC code(s) to look up

  --file FILE, -f FILE  Input file with UPC codes (.txt or .csv)

  --output OUTPUT, -o OUTPUT
                        Output CSV file (default: upc_prices_TIMESTAMP.csv)

  --rate-limit RATE_LIMIT, -r RATE_LIMIT
                        Maximum API calls per minute (default: 20)

  --country COUNTRY, -c COUNTRY
                        Country code for pricing (default: US)

  --currency CURRENCY   Currency code (default: USD)

  --quiet, -q          Suppress progress output
```

### Python API

```python
from upc_price_lookup import UPCPriceLookup

# Initialize
lookup = UPCPriceLookup(rate_limit=20, country_code="US", currency="USD")

# Single lookup
result = lookup.lookup_upc("733739004536")
print(result)

# Batch lookup
upcs = ["733739004536", "733739004543", "NOW-00453"]
results = lookup.lookup_batch(upcs)

# Export to CSV
lookup.export_to_csv(results, "output.csv")
```

### Lambda Event Format

```json
{
  "upcs": ["733739004536", "733739004543"],
  "rate_limit": 20,
  "country_code": "US",
  "currency": "USD"
}
```

### Lambda Response Format

```json
{
  "success": true,
  "summary": {
    "total": 2,
    "found": 2,
    "not_found": 0,
    "success_rate": 100.0
  },
  "results": [
    {
      "upc": "733739004536",
      "found": true,
      "product_id": "453",
      "name": "NOW Foods, Calcium & Magnesium, 250 Tablets",
      "brand": "NOW Foods",
      "price": 11.99,
      "list_price": 14.99,
      "discount": 20,
      "currency": "USD",
      "in_stock": true,
      "rating": 4.5,
      "reviews": 1234,
      "url": "https://www.iherb.com/pr/NOW-00453",
      "image_url": "https://...",
      "timestamp": "2024-11-11T14:30:22"
    }
  ],
  "metadata": {
    "rate_limit": 20,
    "country_code": "US",
    "currency": "USD",
    "timestamp": "2024-11-11T14:30:22"
  }
}
```

---

## Troubleshooting

### Issue: "No products found" for valid UPCs

**Possible causes**:
1. UPC not in iHerb database
2. Product discontinued
3. Wrong country/currency settings

**Solutions**:
- Try searching on iHerb.com manually
- Check if product is available in your country
- Try different country codes (US, CA, GB, etc.)

### Issue: Rate limit errors (429 responses)

**Symptoms**: API returns errors about too many requests

**Solutions**:
1. Decrease rate limit: `--rate-limit 10`
2. Add longer delays between batches
3. Spread processing over longer time period

### Issue: Slow processing

**Causes**: Rate limiting working as intended

**Solutions**:
1. Increase rate limit carefully: `--rate-limit 30`
2. Process overnight for large batches
3. Use AWS Lambda for parallel processing
4. Run multiple instances with different IPs

### Issue: Connection timeouts

**Causes**: Network issues or API downtime

**Solutions**:
1. Check internet connection
2. Retry failed lookups
3. Check iHerb API status
4. Use VPN if region-blocked

---

## Best Practices

### 1. Start Conservative

```bash
# First run: test with small batch and low rate limit
python upc_price_lookup.py --file test_upcs.txt --rate-limit 10
```

### 2. Monitor Results

- Check CSV output for errors
- Monitor "not found" rate
- Adjust rate limit based on errors

### 3. Use Appropriate Rate Limits

```bash
# For 24/7 continuous processing
--rate-limit 10

# For daytime batch processing
--rate-limit 20

# For one-time large batches
--rate-limit 15
```

### 4. Handle Failures Gracefully

- Save results incrementally
- Keep track of failed UPCs
- Retry failed lookups later

### 5. Respect API Limits

- Don't exceed reasonable rate limits
- Implement backoff on errors
- Monitor for rate limit warnings

---

## Integration with Price Tracker

You can integrate UPC lookup results with the main price tracker:

```bash
# 1. Look up UPCs and get product info
python upc_price_lookup.py --file upcs.txt --output upc_results.csv

# 2. Extract URLs from results
# (Filter for found=True and extract URL column)

# 3. Use URLs with bulk scraper
python bulk_scraper.py urls_from_upcs.txt
```

---

## Support

For issues or questions:
1. Check [AWS Lambda Deployment Guide](AWS_LAMBDA_DEPLOYMENT.md)
2. Review [Troubleshooting](#troubleshooting) section
3. Open an issue on GitHub

---

## API Documentation

### iHerb Catalog API

**Endpoint**: `https://catalog.app.iherb.com/suggestion`

**Parameters**:
- `kw`: Search keyword (UPC code)
- `m`: Mode (1 for search)
- `countryCode`: Country code (US, CA, GB, etc.)
- `currCode`: Currency code (USD, CAD, GBP, etc.)
- `lc`: Language code (en-US, fr-CA, etc.)
- `store`: Store ID (0 for main store)

**Response**: JSON with product array

---

## Changelog

### Version 1.0.0 (2024-11-11)
- Initial release
- Configurable rate limiting
- Batch processing support
- CSV export
- AWS Lambda compatibility
- Browser-like headers
