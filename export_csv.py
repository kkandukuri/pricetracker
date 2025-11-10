#!/usr/bin/env python3
"""
CSV Export Tool - Export scraped products to CSV format

This script exports all tracked products to a CSV file with customizable columns.

Usage:
    python export_csv.py
    python export_csv.py --output products.csv
    python export_csv.py --output products.csv --include-images
"""
import csv
import argparse
from pathlib import Path
from datetime import datetime

from src.database import Database


def create_short_description(description: str, max_length: int = 100) -> str:
    """
    Create a short description from the full description.

    Args:
        description: Full description text
        max_length: Maximum length for short description

    Returns:
        Shortened description with ellipsis if truncated
    """
    if not description:
        return ""

    description = description.strip()

    if len(description) <= max_length:
        return description

    # Truncate at word boundary
    truncated = description[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."


def extract_color_from_description(name: str, description: str) -> str:
    """
    Try to extract color information from product name or description.

    Args:
        name: Product name
        description: Product description

    Returns:
        Color if found, empty string otherwise
    """
    colors = [
        'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple',
        'pink', 'brown', 'grey', 'gray', 'silver', 'gold', 'beige', 'navy',
        'teal', 'maroon', 'olive', 'lime', 'cyan', 'magenta', 'tan', 'violet',
        'indigo', 'turquoise', 'multicolor', 'multi-color', 'assorted'
    ]

    # Search in name first (case insensitive)
    name_lower = name.lower()
    for color in colors:
        if color in name_lower:
            return color.capitalize()

    # Search in description
    desc_lower = description.lower()
    for color in colors:
        if color in desc_lower:
            return color.capitalize()

    return ""


def extract_size_from_description(name: str, description: str) -> str:
    """
    Try to extract size information from product name or description.

    Args:
        name: Product name
        description: Product description

    Returns:
        Size if found, empty string otherwise
    """
    import re

    # Common size patterns
    size_patterns = [
        r'\b(\d+\s*ml)\b',              # 250 ml, 250ml
        r'\b(\d+\s*l)\b',                # 2 l, 2l
        r'\b(\d+\s*g)\b',                # 500 g, 500g
        r'\b(\d+\s*kg)\b',               # 1 kg, 1kg
        r'\b(\d+\s*oz)\b',               # 8 oz, 8oz
        r'\b(\d+\s*lb)\b',               # 2 lb, 2lb
        r'\b(x?s|small)\b',              # XS, S, Small
        r'\b(m|medium)\b',               # M, Medium
        r'\b(x?l|large)\b',              # L, XL, Large
        r'\b(xx?l)\b',                   # XXL, XL
        r'\b(\d+x\d+)\b',                # 10x20
        r'\b(\d+")\b',                   # 10"
        r'\b(\d+\s*inch)\b',             # 10 inch
        r'\b(\d+\s*cm)\b',               # 10 cm
        r'\b(\d+\s*mm)\b',               # 10 mm
    ]

    text = (name + " " + description).lower()

    for pattern in size_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


def extract_category_from_url_or_name(url: str, name: str, description: str) -> tuple:
    """
    Try to extract category information from URL, name, or description.

    Args:
        url: Product URL
        name: Product name
        description: Product description

    Returns:
        Tuple of (category, childCategory)
    """
    # Common categories
    categories = {
        'beauty': ['Beauty', 'Personal Care'],
        'hair': ['Beauty', 'Hair Care'],
        'skin': ['Beauty', 'Skin Care'],
        'makeup': ['Beauty', 'Makeup'],
        'shampoo': ['Beauty', 'Hair Care'],
        'conditioner': ['Beauty', 'Hair Care'],
        'lotion': ['Beauty', 'Skin Care'],
        'cream': ['Beauty', 'Skin Care'],
        'serum': ['Beauty', 'Skin Care'],

        'electronics': ['Electronics', 'General'],
        'phone': ['Electronics', 'Mobile'],
        'laptop': ['Electronics', 'Computers'],
        'computer': ['Electronics', 'Computers'],
        'headphone': ['Electronics', 'Audio'],
        'speaker': ['Electronics', 'Audio'],
        'camera': ['Electronics', 'Photography'],

        'clothing': ['Fashion', 'Clothing'],
        'shirt': ['Fashion', 'Clothing'],
        'pants': ['Fashion', 'Clothing'],
        'dress': ['Fashion', 'Clothing'],
        'shoes': ['Fashion', 'Footwear'],

        'home': ['Home', 'General'],
        'kitchen': ['Home', 'Kitchen'],
        'furniture': ['Home', 'Furniture'],
        'bedding': ['Home', 'Bedroom'],

        'food': ['Grocery', 'Food'],
        'snack': ['Grocery', 'Snacks'],
        'beverage': ['Grocery', 'Beverages'],
        'organic': ['Grocery', 'Organic'],

        'toy': ['Toys', 'General'],
        'game': ['Toys', 'Games'],

        'book': ['Books', 'General'],
        'novel': ['Books', 'Fiction'],

        'sport': ['Sports', 'General'],
        'fitness': ['Sports', 'Fitness'],
    }

    text = (url + " " + name + " " + description).lower()

    for keyword, (category, child_category) in categories.items():
        if keyword in text:
            return (category, child_category)

    return ("", "")


def export_to_csv(output_file: str, include_images: bool = False,
                  include_metadata: bool = False):
    """
    Export all products to CSV file.

    Args:
        output_file: Path to output CSV file
        include_images: Whether to include image URLs
        include_metadata: Whether to include additional metadata columns
    """
    db = Database()

    try:
        products = db.get_all_products()

        if not products:
            print("No products found in database.")
            return

        print(f"Exporting {len(products)} products to CSV...")

        # Define CSV columns in the exact order requested
        columns = [
            'URL',
            'NAME',
            'Description',
            'ShortDescription',
            'Price',
            'color',
            'Size',
            'Category',
            'childCategory'
        ]

        if include_images:
            columns.append('ImageURLs')

        if include_metadata:
            columns.extend(['Currency', 'Site', 'ProductID',
                          'CreatedAt', 'UpdatedAt'])

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for product in products:
                # Extract color and size from description
                color = extract_color_from_description(
                    product.name,
                    product.description
                )
                size = extract_size_from_description(
                    product.name,
                    product.description
                )

                # Extract category information
                category, child_category = extract_category_from_url_or_name(
                    product.url,
                    product.name,
                    product.description
                )

                # Create short description
                short_desc = create_short_description(
                    product.description,
                    max_length=100
                )

                # Build row
                row = {
                    'URL': product.url,
                    'NAME': product.name,
                    'Description': product.description,
                    'ShortDescription': short_desc,
                    'Price': product.current_price,
                    'color': color,
                    'Size': size,
                    'Category': category,
                    'childCategory': child_category
                }

                if include_images:
                    # Join image URLs with semicolon
                    row['ImageURLs'] = '; '.join(product.image_urls)

                if include_metadata:
                    row['Currency'] = product.currency
                    row['Site'] = product.site_name
                    row['ProductID'] = product.id
                    row['CreatedAt'] = str(product.created_at) if product.created_at else ''
                    row['UpdatedAt'] = str(product.updated_at) if product.updated_at else ''

                writer.writerow(row)

        print(f"\n✅ Successfully exported to: {output_file}")
        print(f"   Total products: {len(products)}")
        print(f"   Columns: {', '.join(columns)}")

    finally:
        db.close()


def export_price_history_csv(output_file: str):
    """
    Export price history for all products to CSV.

    Args:
        output_file: Path to output CSV file
    """
    db = Database()

    try:
        products = db.get_all_products()

        if not products:
            print("No products found in database.")
            return

        print(f"Exporting price history for {len(products)} products...")

        columns = [
            'ProductID',
            'ProductName',
            'Date',
            'Price',
            'Currency',
            'PriceChange'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            total_records = 0

            for product in products:
                history = db.get_price_history(product.id, limit=1000)

                prev_price = None
                for record in reversed(history):
                    price_change = ""
                    if prev_price is not None:
                        diff = record.price - prev_price
                        if diff > 0:
                            price_change = f"+{diff:.2f}"
                        elif diff < 0:
                            price_change = f"{diff:.2f}"
                        else:
                            price_change = "0.00"

                    row = {
                        'ProductID': product.id,
                        'ProductName': product.name,
                        'Date': str(record.recorded_at) if record.recorded_at else '',
                        'Price': record.price,
                        'Currency': record.currency,
                        'PriceChange': price_change
                    }

                    writer.writerow(row)
                    prev_price = record.price
                    total_records += 1

        print(f"\n✅ Successfully exported price history to: {output_file}")
        print(f"   Total records: {total_records}")

    finally:
        db.close()


def main():
    """Main entry point for CSV export."""
    parser = argparse.ArgumentParser(
        description='Export scraped products to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export products to default file (products.csv)
  python export_csv.py

  # Export to custom file
  python export_csv.py --output my_products.csv

  # Include image URLs
  python export_csv.py --include-images

  # Include all metadata (currency, site, URL, dates)
  python export_csv.py --include-metadata

  # Export price history
  python export_csv.py --price-history --output price_history.csv

  # Full export with everything
  python export_csv.py --output full_export.csv --include-images --include-metadata

CSV Format:
  Standard columns (always included):
    - URL: Product URL
    - NAME: Product name
    - Description: Full product description
    - ShortDescription: First 100 characters of description
    - Price: Current price (number)
    - color: Extracted color (if found in name/description)
    - Size: Extracted size (if found in name/description)
    - Category: Main category (auto-detected)
    - childCategory: Sub-category (auto-detected)

  With --include-images:
    - ImageURLs: Semicolon-separated image URLs

  With --include-metadata:
    - Currency: Currency code (USD, EUR, etc.)
    - Site: Website domain
    - ProductID: Database ID
    - CreatedAt: When product was first tracked
    - UpdatedAt: Last update timestamp
        """
    )

    parser.add_argument('--output', '-o',
                       default=f'products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                       help='Output CSV file path (default: products_TIMESTAMP.csv)')
    parser.add_argument('--include-images', action='store_true',
                       help='Include image URLs in export')
    parser.add_argument('--include-metadata', action='store_true',
                       help='Include additional metadata (currency, site, URL, dates)')
    parser.add_argument('--price-history', action='store_true',
                       help='Export price history instead of products')

    args = parser.parse_args()

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("CSV EXPORT TOOL")
    print("="*80)
    print()

    try:
        if args.price_history:
            export_price_history_csv(args.output)
        else:
            export_to_csv(
                args.output,
                include_images=args.include_images,
                include_metadata=args.include_metadata
            )

        print()
        print("="*80)
        print("Export completed successfully!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error during export: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
