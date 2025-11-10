#!/usr/bin/env python3
"""
Bulk URL Scraper - Scrape multiple products from a list of URLs

This script processes a list of product URLs with configurable delays
to avoid overloading servers and getting blocked.

Usage:
    python bulk_scraper.py urls.txt
    python bulk_scraper.py urls.txt --delay 5 --selenium
    python bulk_scraper.py urls.csv --format csv --delay 10
"""
import sys
import time
import argparse
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from src.tracker import PriceTracker
from src.scraper import ProductScraper, SeleniumScraper


class BulkScraper:
    """Handle bulk scraping of multiple product URLs."""

    def __init__(self, use_selenium=False, delay=3, config_path=None):
        """
        Initialize bulk scraper.

        Args:
            use_selenium: Whether to use Selenium for scraping
            delay: Delay in seconds between requests
            config_path: Path to site configuration file
        """
        self.use_selenium = use_selenium
        self.delay = delay
        self.tracker = PriceTracker(config_path=config_path)
        self.selenium_scraper = None

        # Statistics
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def read_urls_from_txt(self, file_path: str) -> List[str]:
        """Read URLs from a text file (one URL per line)."""
        urls = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls

    def read_urls_from_csv(self, file_path: str) -> List[Tuple[str, dict]]:
        """
        Read URLs from a CSV file with optional metadata.

        CSV format:
        url,category,notes
        https://example.com/product1,Electronics,Best seller
        https://example.com/product2,Home,On sale
        """
        urls = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url', '').strip()
                if url and not url.startswith('#'):
                    # Include metadata
                    metadata = {k: v for k, v in row.items() if k != 'url'}
                    urls.append((url, metadata))
        return urls

    def scrape_url(self, url: str, metadata: dict = None) -> Tuple[bool, str]:
        """
        Scrape a single URL.

        Args:
            url: Product URL to scrape
            metadata: Optional metadata about the product

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if already exists
            existing = self.tracker.db.get_product_by_url(url)
            if existing:
                return (True, f"Already tracked (ID: {existing.id})")

            # Scrape the product
            product = self.tracker.track_product(url, use_selenium=self.use_selenium)

            if product:
                return (True, f"Added successfully (ID: {product.id})")
            else:
                return (False, "Failed to scrape product")

        except Exception as e:
            return (False, f"Error: {str(e)}")

    def scrape_bulk(self, urls: List, show_progress=True) -> dict:
        """
        Scrape multiple URLs with rate limiting.

        Args:
            urls: List of URLs or list of (URL, metadata) tuples
            show_progress: Whether to show progress information

        Returns:
            Dictionary with statistics
        """
        self.stats['total'] = len(urls)
        start_time = time.time()

        print("="*80)
        print("BULK SCRAPING STARTED")
        print("="*80)
        print(f"Total URLs: {len(urls)}")
        print(f"Delay between requests: {self.delay} seconds")
        print(f"Using Selenium: {self.use_selenium}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print()

        for i, url_data in enumerate(urls, 1):
            # Handle both plain URLs and (URL, metadata) tuples
            if isinstance(url_data, tuple):
                url, metadata = url_data
            else:
                url, metadata = url_data, {}

            # Progress
            if show_progress:
                print(f"\n[{i}/{len(urls)}] Processing: {url}")
                if metadata:
                    print(f"  Metadata: {metadata}")

            # Scrape
            success, message = self.scrape_url(url, metadata)

            # Update statistics
            if success:
                self.stats['success'] += 1
                status = "✓"
            else:
                self.stats['failed'] += 1
                status = "✗"
                self.stats['errors'].append({
                    'url': url,
                    'error': message
                })

            if show_progress:
                print(f"  {status} {message}")

            # Rate limiting - delay between requests
            if i < len(urls):  # Don't delay after last URL
                if show_progress:
                    print(f"  ⏳ Waiting {self.delay} seconds before next request...")
                time.sleep(self.delay)

        # Summary
        elapsed_time = time.time() - start_time
        self.print_summary(elapsed_time)

        return self.stats

    def print_summary(self, elapsed_time: float):
        """Print scraping summary."""
        print("\n" + "="*80)
        print("BULK SCRAPING COMPLETED")
        print("="*80)
        print(f"Total URLs processed: {self.stats['total']}")
        print(f"✓ Successful: {self.stats['success']}")
        print(f"✗ Failed: {self.stats['failed']}")
        print(f"⏱  Time taken: {elapsed_time:.2f} seconds")
        print(f"⚡ Average time per URL: {elapsed_time/self.stats['total']:.2f} seconds")
        print("="*80)

        # Show errors if any
        if self.stats['errors']:
            print("\n" + "="*80)
            print("ERRORS")
            print("="*80)
            for i, error in enumerate(self.stats['errors'], 1):
                print(f"\n{i}. URL: {error['url']}")
                print(f"   Error: {error['error']}")
            print("="*80)

    def save_results_to_file(self, output_file: str):
        """Save scraping results to a file."""
        with open(output_file, 'w') as f:
            f.write("Bulk Scraping Results\n")
            f.write("="*80 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total URLs: {self.stats['total']}\n")
            f.write(f"Successful: {self.stats['success']}\n")
            f.write(f"Failed: {self.stats['failed']}\n")
            f.write("="*80 + "\n\n")

            if self.stats['errors']:
                f.write("Errors:\n")
                f.write("-"*80 + "\n")
                for error in self.stats['errors']:
                    f.write(f"URL: {error['url']}\n")
                    f.write(f"Error: {error['error']}\n\n")

        print(f"\n📄 Results saved to: {output_file}")

    def cleanup(self):
        """Cleanup resources."""
        if self.selenium_scraper:
            self.selenium_scraper.close()
        self.tracker.close()


def main():
    """Main entry point for bulk scraper."""
    parser = argparse.ArgumentParser(
        description='Bulk scrape products from a list of URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape from text file with default 3-second delay
  python bulk_scraper.py urls.txt

  # Scrape with 5-second delay
  python bulk_scraper.py urls.txt --delay 5

  # Scrape using Selenium
  python bulk_scraper.py urls.txt --selenium --delay 10

  # Scrape from CSV file
  python bulk_scraper.py products.csv --format csv --delay 5

  # Save results to file
  python bulk_scraper.py urls.txt --output results.txt

URL File Formats:

  Text file (urls.txt):
    https://distacart.com/products/product1
    https://distacart.com/products/product2
    # This is a comment
    https://distacart.com/products/product3

  CSV file (products.csv):
    url,category,notes
    https://distacart.com/products/product1,Beauty,Best seller
    https://distacart.com/products/product2,Home,On sale
        """
    )

    parser.add_argument('file', help='File containing URLs (txt or csv)')
    parser.add_argument('--format', choices=['txt', 'csv'], default='txt',
                       help='Input file format (default: txt)')
    parser.add_argument('--delay', type=float, default=3.0,
                       help='Delay in seconds between requests (default: 3)')
    parser.add_argument('--selenium', action='store_true',
                       help='Use Selenium for JavaScript-heavy sites')
    parser.add_argument('--config', default='config/sites.json',
                       help='Path to site configuration file')
    parser.add_argument('--output', help='Save results to output file')
    parser.add_argument('--no-progress', action='store_true',
                       help='Disable progress output')

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.file).exists():
        print(f"❌ Error: File '{args.file}' not found")
        sys.exit(1)

    # Initialize scraper
    config_path = args.config if Path(args.config).exists() else None
    scraper = BulkScraper(
        use_selenium=args.selenium,
        delay=args.delay,
        config_path=config_path
    )

    try:
        # Read URLs
        if args.format == 'csv':
            print(f"📄 Reading URLs from CSV file: {args.file}")
            urls = scraper.read_urls_from_csv(args.file)
        else:
            print(f"📄 Reading URLs from text file: {args.file}")
            urls = scraper.read_urls_from_txt(args.file)

        if not urls:
            print("❌ No URLs found in file")
            sys.exit(1)

        print(f"✓ Found {len(urls)} URLs\n")

        # Scrape
        stats = scraper.scrape_bulk(urls, show_progress=not args.no_progress)

        # Save results if requested
        if args.output:
            scraper.save_results_to_file(args.output)

        # Exit with appropriate code
        if stats['failed'] > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        print(f"Processed {scraper.stats['success']} URLs before interruption")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()
