#!/usr/bin/env python3
"""
Example usage of the Price Tracker as a Python module
"""
from src.tracker import PriceTracker


def main():
    """Demonstrate how to use the price tracker programmatically."""

    # Initialize the tracker
    tracker = PriceTracker(
        db_path="data/products.db",
        config_path="config/sites.json"
    )

    print("=== Price Tracker Example ===\n")

    # Example 1: Track a new product
    print("1. Adding a new product...")
    product_url = "https://www.amazon.com/example-product"  # Replace with real URL

    # Note: This is just an example. Replace with a real product URL to test
    print(f"   URL: {product_url}")
    print("   (Use a real product URL when testing)")

    # Uncomment to actually scrape:
    # product = tracker.track_product(product_url)
    # if product:
    #     tracker.display_product_info(product)

    # Example 2: List all tracked products
    print("\n2. Listing all tracked products...")
    products = tracker.get_all_products()

    if products:
        print(f"   Found {len(products)} tracked products:")
        for p in products:
            print(f"   - [{p.id}] {p.name} - {p.currency} {p.current_price}")
    else:
        print("   No products tracked yet.")

    # Example 3: Get specific product info
    if products:
        print("\n3. Getting detailed info for first product...")
        first_product = products[0]
        tracker.display_product_info(first_product)

        # Example 4: View price history
        print("\n4. Viewing price history...")
        tracker.display_price_history(first_product.id, limit=5)

    # Example 5: Update all products
    print("\n5. Updating all products...")
    print("   (Commented out to avoid unnecessary requests)")
    # tracker.update_all_products()

    # Example 6: Direct database access
    print("\n6. Direct database operations...")
    from src.database import Database
    from src.models import Product

    db = Database("data/products.db")

    # Get product by URL
    # product = db.get_product_by_url("https://example.com/product")

    # Get price history
    # history = db.get_price_history(product_id=1, limit=10)

    db.close()

    # Example 7: Using custom scraper
    print("\n7. Using custom configuration...")
    from src.scraper import ProductScraper

    custom_config = {
        "name_selector": "h1.product-title",
        "price_selector": ".price-value",
        "description_selector": ".description",
        "image_selector": ".product-image img"
    }

    scraper = ProductScraper(config=custom_config)
    # result = scraper.scrape_product("https://example.com/product")

    # Example 8: Using Selenium for JavaScript-heavy sites
    print("\n8. Using Selenium scraper...")
    from src.scraper import SeleniumScraper

    # selenium_scraper = SeleniumScraper(config=custom_config)
    # result = selenium_scraper.scrape_product("https://example.com/product")
    # selenium_scraper.close()  # Important: always close Selenium driver

    print("\n=== Example Complete ===")
    print("\nNext steps:")
    print("1. Add a real product URL to test scraping")
    print("2. Run: python main.py add 'https://www.amazon.com/product-url'")
    print("3. Check results: python main.py list")
    print("4. View history: python main.py history 1")

    # Clean up
    tracker.close()


if __name__ == "__main__":
    main()
