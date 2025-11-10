"""Price tracker for monitoring product prices over time."""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from .database import Database
from .scraper import ProductScraper, SeleniumScraper
from .models import Product


class PriceTracker:
    """Main price tracker class."""

    def __init__(self, db_path: str = "data/products.db", config_path: Optional[str] = None):
        """
        Initialize the price tracker.

        Args:
            db_path: Path to the SQLite database
            config_path: Path to the site configuration file
        """
        self.db = Database(db_path)
        self.site_configs = {}

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.site_configs = json.load(f)

    def track_product(self, url: str, use_selenium: bool = False) -> Optional[Product]:
        """
        Start tracking a product by URL.

        Args:
            url: Product URL to track
            use_selenium: Whether to use Selenium for scraping

        Returns:
            Product object if successful, None otherwise
        """
        # Check if product already exists
        existing_product = self.db.get_product_by_url(url)

        # Get site-specific config
        config = self._get_config_for_url(url)

        # Choose scraper
        if use_selenium:
            scraper = SeleniumScraper(config)
        else:
            scraper = ProductScraper(config)

        # Scrape product data
        product = scraper.scrape_product(url)

        if not product:
            print(f"Failed to scrape product from {url}")
            return None

        # Save or update in database
        if existing_product:
            product.id = existing_product.id
            self.db.update_product(product)
            print(f"Updated product: {product.name}")
        else:
            product_id = self.db.add_product(product)
            product.id = product_id
            print(f"Added new product: {product.name} (ID: {product_id})")

        # Clean up Selenium if used
        if use_selenium:
            scraper.close()

        return product

    def update_all_products(self, use_selenium: bool = False):
        """
        Update prices for all tracked products.

        Args:
            use_selenium: Whether to use Selenium for scraping
        """
        products = self.db.get_all_products()
        print(f"Updating {len(products)} products...")

        for product in products:
            print(f"\nUpdating: {product.name}")
            updated_product = self.track_product(product.url, use_selenium)

            if updated_product:
                price_change = updated_product.current_price - product.current_price
                if price_change != 0:
                    symbol = "↑" if price_change > 0 else "↓"
                    print(f"  Price changed: {product.current_price} → "
                          f"{updated_product.current_price} {symbol}")
                else:
                    print(f"  Price unchanged: {product.current_price}")

    def get_product_info(self, product_id: int) -> Optional[Product]:
        """Get product information by ID."""
        return self.db.get_product_by_id(product_id)

    def get_all_products(self) -> List[Product]:
        """Get all tracked products."""
        return self.db.get_all_products()

    def get_price_history(self, product_id: int, limit: int = 100):
        """Get price history for a product."""
        return self.db.get_price_history(product_id, limit)

    def display_product_info(self, product: Product):
        """Display product information in a formatted way."""
        print("\n" + "=" * 80)
        print(f"Product: {product.name}")
        print("=" * 80)
        print(f"ID: {product.id}")
        print(f"URL: {product.url}")
        print(f"Site: {product.site_name}")
        print(f"Current Price: {product.currency} {product.current_price}")
        print(f"\nDescription:")
        print(f"{product.description[:200]}..." if len(product.description) > 200 else product.description)
        print(f"\nImages ({len(product.image_urls)}):")
        for i, img_url in enumerate(product.image_urls, 1):
            print(f"  {i}. {img_url}")
        print(f"\nCreated: {product.created_at}")
        print(f"Updated: {product.updated_at}")
        print("=" * 80)

    def display_price_history(self, product_id: int, limit: int = 10):
        """Display price history for a product."""
        product = self.db.get_product_by_id(product_id)
        if not product:
            print(f"Product {product_id} not found")
            return

        history = self.db.get_price_history(product_id, limit)

        print(f"\nPrice History for: {product.name}")
        print("=" * 80)
        print(f"{'Date':<25} {'Price':<15} {'Change':<15}")
        print("-" * 80)

        prev_price = None
        for record in reversed(history):
            change = ""
            if prev_price is not None:
                diff = record.price - prev_price
                if diff > 0:
                    change = f"+{diff:.2f} ↑"
                elif diff < 0:
                    change = f"{diff:.2f} ↓"
                else:
                    change = "No change"

            print(f"{str(record.recorded_at):<25} "
                  f"{record.currency} {record.price:<12.2f} {change:<15}")
            prev_price = record.price

        print("=" * 80)

    def _get_config_for_url(self, url: str) -> Dict[str, Any]:
        """Get site-specific configuration for a URL."""
        for site_name, config in self.site_configs.items():
            if site_name in url:
                return config
        return {}

    def close(self):
        """Close database connection."""
        self.db.close()
