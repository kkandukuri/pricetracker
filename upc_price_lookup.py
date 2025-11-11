#!/usr/bin/env python3
"""
UPC Price Lookup Tool - Fetch product prices from iHerb using UPC codes

This script queries the iHerb API to get product information and prices
for a list of UPC codes with configurable rate limiting.

Usage:
    python upc_price_lookup.py --upc 123456789012
    python upc_price_lookup.py --file upcs.txt
    python upc_price_lookup.py --file upcs.csv --rate-limit 20
    python upc_price_lookup.py --upc 123456789012 --output results.csv
"""

import argparse
import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import requests


class UPCPriceLookup:
    """Handles UPC price lookups with rate limiting."""

    def __init__(self, rate_limit: int = 20, country_code: str = "US", currency: str = "USD"):
        """
        Initialize the UPC price lookup tool.

        Args:
            rate_limit: Maximum API calls per minute (default: 20)
            country_code: Country code for pricing (default: US)
            currency: Currency code (default: USD)
        """
        self.rate_limit = rate_limit
        self.country_code = country_code
        self.currency = currency
        self.api_base_url = "https://catalog.app.iherb.com/suggestion"

        # Calculate delay between requests (in seconds)
        self.request_delay = 60.0 / rate_limit if rate_limit > 0 else 0

        # Browser-like headers to mimic real browser requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.iherb.com',
            'Referer': 'https://www.iherb.com/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_request_time = 0

    def _rate_limit_delay(self):
        """Apply rate limiting delay between requests."""
        if self.request_delay > 0:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.request_delay:
                sleep_time = self.request_delay - time_since_last
                time.sleep(sleep_time)

            self.last_request_time = time.time()

    def lookup_upc(self, upc: str) -> Optional[Dict]:
        """
        Look up a single UPC code and return product information.

        Args:
            upc: UPC code to search for

        Returns:
            Dictionary with product information or None if not found
        """
        # Apply rate limiting
        self._rate_limit_delay()

        # Build API URL
        params = {
            'kw': upc,
            'm': '1',
            'countryCode': self.country_code,
            'dscid': '257e210c-9d9a-40a8-ad2d-55a4e076ddd5',
            'ssid': '',
            'currCode': self.currency,
            'lc': 'en-US',
            'credentials': 'true',
            'store': '0'
        }

        try:
            response = self.session.get(
                self.api_base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Parse the response and extract product info
            if data and isinstance(data, dict):
                products = data.get('products', [])

                if products and len(products) > 0:
                    # Get the first matching product
                    product = products[0]

                    return {
                        'upc': upc,
                        'product_id': product.get('id', ''),
                        'name': product.get('name', ''),
                        'url': f"https://www.iherb.com/pr/{product.get('partNumber', '')}",
                        'price': product.get('price', 0),
                        'list_price': product.get('listPrice', 0),
                        'currency': self.currency,
                        'discount': product.get('discount', 0),
                        'rating': product.get('rating', 0),
                        'reviews': product.get('reviews', 0),
                        'in_stock': product.get('inStock', False),
                        'image_url': product.get('image', ''),
                        'brand': product.get('brand', ''),
                        'found': True,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'upc': upc,
                        'found': False,
                        'error': 'No products found',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                return {
                    'upc': upc,
                    'found': False,
                    'error': 'Invalid API response',
                    'timestamp': datetime.now().isoformat()
                }

        except requests.exceptions.RequestException as e:
            return {
                'upc': upc,
                'found': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def lookup_batch(self, upcs: List[str], progress: bool = True) -> List[Dict]:
        """
        Look up multiple UPC codes with rate limiting.

        Args:
            upcs: List of UPC codes to search
            progress: Whether to show progress output

        Returns:
            List of dictionaries with product information
        """
        results = []
        total = len(upcs)

        if progress:
            print(f"\nLooking up {total} UPC codes...")
            print(f"Rate limit: {self.rate_limit} requests/minute")
            print(f"Estimated time: {(total * self.request_delay) / 60:.1f} minutes\n")

        for idx, upc in enumerate(upcs, 1):
            if progress:
                print(f"[{idx}/{total}] Looking up UPC: {upc}...", end=' ')

            result = self.lookup_upc(upc)
            results.append(result)

            if progress:
                if result.get('found'):
                    print(f"✓ Found: {result.get('name', 'Unknown')[:50]}")
                else:
                    print(f"✗ Not found: {result.get('error', 'Unknown error')}")

        return results

    def export_to_csv(self, results: List[Dict], output_file: str):
        """
        Export lookup results to CSV file.

        Args:
            results: List of product information dictionaries
            output_file: Path to output CSV file
        """
        if not results:
            print("No results to export.")
            return

        # Define CSV columns
        columns = [
            'UPC',
            'Found',
            'ProductID',
            'Name',
            'Brand',
            'Price',
            'ListPrice',
            'Discount',
            'Currency',
            'InStock',
            'Rating',
            'Reviews',
            'URL',
            'ImageURL',
            'Error',
            'Timestamp'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for result in results:
                row = {
                    'UPC': result.get('upc', ''),
                    'Found': result.get('found', False),
                    'ProductID': result.get('product_id', ''),
                    'Name': result.get('name', ''),
                    'Brand': result.get('brand', ''),
                    'Price': result.get('price', ''),
                    'ListPrice': result.get('list_price', ''),
                    'Discount': result.get('discount', ''),
                    'Currency': result.get('currency', ''),
                    'InStock': result.get('in_stock', ''),
                    'Rating': result.get('rating', ''),
                    'Reviews': result.get('reviews', ''),
                    'URL': result.get('url', ''),
                    'ImageURL': result.get('image_url', ''),
                    'Error': result.get('error', ''),
                    'Timestamp': result.get('timestamp', '')
                }
                writer.writerow(row)

        print(f"\n✅ Results exported to: {output_file}")


def read_upcs_from_file(file_path: str) -> List[str]:
    """
    Read UPC codes from a file (txt or csv).

    Args:
        file_path: Path to input file

    Returns:
        List of UPC codes
    """
    upcs = []
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == '.csv':
        # Read from CSV (assume first column or 'UPC' column)
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Try to find UPC column
            if 'UPC' in reader.fieldnames:
                for row in reader:
                    upc = row['UPC'].strip()
                    if upc:
                        upcs.append(upc)
            elif 'upc' in reader.fieldnames:
                for row in reader:
                    upc = row['upc'].strip()
                    if upc:
                        upcs.append(upc)
            else:
                # Use first column
                f.seek(0)
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if row and row[0].strip():
                        upcs.append(row[0].strip())
    else:
        # Read from text file (one UPC per line)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                upc = line.strip()
                if upc and not upc.startswith('#'):
                    upcs.append(upc)

    return upcs


def main():
    """Main entry point for UPC price lookup tool."""
    parser = argparse.ArgumentParser(
        description='Look up product prices from iHerb using UPC codes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Look up a single UPC
  python upc_price_lookup.py --upc 123456789012

  # Look up multiple UPCs from a text file
  python upc_price_lookup.py --file upcs.txt

  # Look up from CSV with custom rate limit
  python upc_price_lookup.py --file upcs.csv --rate-limit 20 --output results.csv

  # Change country and currency
  python upc_price_lookup.py --file upcs.txt --country CA --currency CAD

  # Look up multiple UPCs directly
  python upc_price_lookup.py --upc 123456789012 456789012345 789012345678

Input File Formats:
  Text file (.txt):
    One UPC per line
    Lines starting with # are ignored

  CSV file (.csv):
    Must have a 'UPC' or 'upc' column
    Or first column will be used as UPC

Output:
  CSV file with columns:
    - UPC: The UPC code searched
    - Found: Whether product was found
    - Name: Product name
    - Brand: Brand name
    - Price: Current price
    - ListPrice: Original list price
    - Discount: Discount percentage
    - Currency: Currency code
    - InStock: Availability status
    - Rating: Product rating
    - Reviews: Number of reviews
    - URL: Product URL
    - ImageURL: Product image URL
    - Error: Error message if lookup failed
    - Timestamp: When lookup was performed
        """
    )

    parser.add_argument('--upc', '-u', nargs='+',
                       help='UPC code(s) to look up')
    parser.add_argument('--file', '-f',
                       help='Input file with UPC codes (.txt or .csv)')
    parser.add_argument('--output', '-o',
                       default=f'upc_prices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                       help='Output CSV file (default: upc_prices_TIMESTAMP.csv)')
    parser.add_argument('--rate-limit', '-r', type=int, default=20,
                       help='Maximum API calls per minute (default: 20)')
    parser.add_argument('--country', '-c', default='US',
                       help='Country code for pricing (default: US)')
    parser.add_argument('--currency', default='USD',
                       help='Currency code (default: USD)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress progress output')

    args = parser.parse_args()

    # Validate inputs
    if not args.upc and not args.file:
        parser.error("Either --upc or --file must be provided")

    print("="*80)
    print("UPC PRICE LOOKUP TOOL - iHerb API")
    print("="*80)
    print()

    try:
        # Initialize lookup tool
        lookup = UPCPriceLookup(
            rate_limit=args.rate_limit,
            country_code=args.country,
            currency=args.currency
        )

        # Get UPC codes
        upcs = []
        if args.file:
            print(f"Reading UPC codes from: {args.file}")
            upcs = read_upcs_from_file(args.file)
            print(f"Found {len(upcs)} UPC codes")
        elif args.upc:
            upcs = args.upc

        if not upcs:
            print("❌ No UPC codes to process")
            return 1

        # Perform lookups
        results = lookup.lookup_batch(upcs, progress=not args.quiet)

        # Export results
        lookup.export_to_csv(results, args.output)

        # Print summary
        found = sum(1 for r in results if r.get('found'))
        not_found = len(results) - found

        print()
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total UPCs processed: {len(results)}")
        print(f"Products found: {found}")
        print(f"Not found: {not_found}")
        print(f"Success rate: {(found/len(results)*100):.1f}%")
        print()
        print(f"Results saved to: {args.output}")
        print("="*80)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
