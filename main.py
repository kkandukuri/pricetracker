#!/usr/bin/env python3
"""
Price Tracker - Track product prices from ecommerce websites
"""
import argparse
import sys
from pathlib import Path

from src.tracker import PriceTracker


def main():
    """Main entry point for the price tracker CLI."""
    parser = argparse.ArgumentParser(
        description='Track product prices from ecommerce websites'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add product command
    add_parser = subparsers.add_parser('add', help='Add a product to track')
    add_parser.add_argument('url', help='Product URL to track')
    add_parser.add_argument('--selenium', action='store_true',
                           help='Use Selenium for JavaScript-heavy sites')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update all tracked products')
    update_parser.add_argument('--selenium', action='store_true',
                              help='Use Selenium for scraping')

    # List command
    subparsers.add_parser('list', help='List all tracked products')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show product details')
    show_parser.add_argument('product_id', type=int, help='Product ID')

    # History command
    history_parser = subparsers.add_parser('history', help='Show price history')
    history_parser.add_argument('product_id', type=int, help='Product ID')
    history_parser.add_argument('--limit', type=int, default=10,
                               help='Number of records to show (default: 10)')

    args = parser.parse_args()

    # Initialize tracker
    config_path = Path('config/sites.json')
    tracker = PriceTracker(config_path=str(config_path) if config_path.exists() else None)

    try:
        if args.command == 'add':
            product = tracker.track_product(args.url, use_selenium=args.selenium)
            if product:
                tracker.display_product_info(product)
                print("\n✓ Product added successfully!")
            else:
                print("\n✗ Failed to add product")
                sys.exit(1)

        elif args.command == 'update':
            tracker.update_all_products(use_selenium=args.selenium)
            print("\n✓ All products updated!")

        elif args.command == 'list':
            products = tracker.get_all_products()
            if not products:
                print("No products tracked yet. Use 'add' command to start tracking.")
                return

            print(f"\nTracked Products ({len(products)}):")
            print("=" * 100)
            print(f"{'ID':<5} {'Name':<40} {'Price':<15} {'Site':<20} {'Updated':<20}")
            print("-" * 100)

            for product in products:
                name = product.name[:37] + "..." if len(product.name) > 40 else product.name
                price = f"{product.currency} {product.current_price:.2f}"
                updated = str(product.updated_at).split('.')[0] if product.updated_at else "N/A"
                print(f"{product.id:<5} {name:<40} {price:<15} {product.site_name:<20} {updated:<20}")

            print("=" * 100)

        elif args.command == 'show':
            product = tracker.get_product_info(args.product_id)
            if product:
                tracker.display_product_info(product)
            else:
                print(f"Product with ID {args.product_id} not found")
                sys.exit(1)

        elif args.command == 'history':
            tracker.display_price_history(args.product_id, args.limit)

        else:
            parser.print_help()

    finally:
        tracker.close()


if __name__ == '__main__':
    main()
