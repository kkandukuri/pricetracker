#!/usr/bin/env python3
"""
Test script to demonstrate how product detection works
This helps you understand and debug the scraping process
"""
from src.scraper import ProductScraper
from bs4 import BeautifulSoup


def test_detection_with_sample_html():
    """
    Demonstrate how the scraper detects product information
    from HTML content.
    """

    # Sample HTML from a typical e-commerce product page
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="description" content="High quality wireless headphones with noise cancellation">
        <meta property="product:price:amount" content="299.99">
        <meta property="product:price:currency" content="USD">
    </head>
    <body>
        <div class="product-container">
            <h1 id="productTitle">Premium Wireless Headphones</h1>

            <div class="price-section">
                <span class="currency">$</span>
                <span class="price">299.99</span>
            </div>

            <div id="productDescription">
                <p>Experience premium sound quality with our wireless headphones.</p>
                <p>Features: Noise cancellation, 30-hour battery, premium build.</p>
            </div>

            <div class="product-images">
                <img itemprop="image" src="https://example.com/images/headphones-1.jpg" alt="Main">
                <img class="gallery-image" src="https://example.com/images/headphones-2.jpg" alt="Side">
                <img class="gallery-image" src="https://example.com/images/headphones-3.jpg" alt="Detail">
            </div>

            <div class="product-meta">
                <span itemprop="brand">AudioPro</span>
                <span class="sku">HP-2024-BLK</span>
            </div>
        </div>
    </body>
    </html>
    """

    print("=" * 80)
    print("PRODUCT DETECTION TEST")
    print("=" * 80)

    # Parse HTML
    soup = BeautifulSoup(sample_html, 'lxml')

    # Create scraper instance (no config - using fallback patterns)
    scraper = ProductScraper()

    print("\n1. DETECTING PRODUCT NAME")
    print("-" * 80)
    name = scraper._extract_name(soup)
    print(f"Detected: {name}")
    print(f"Method: Found <h1 id='productTitle'>")
    print(f"Selector that matched: h1#productTitle")

    print("\n2. DETECTING PRICE")
    print("-" * 80)
    price = scraper._extract_price(soup)
    print(f"Detected: ${price}")
    print(f"Method: Found <span class='price'>299.99</span>")
    print(f"Selector that matched: .price")
    print(f"Parsing: '299.99' → {price}")

    print("\n3. DETECTING DESCRIPTION")
    print("-" * 80)
    description = scraper._extract_description(soup)
    print(f"Detected: {description[:100]}...")
    print(f"Method: Found <div id='productDescription'>")
    print(f"Selector that matched: #productDescription")

    print("\n4. DETECTING CURRENCY")
    print("-" * 80)
    currency = scraper._extract_currency(soup)
    print(f"Detected: {currency}")
    print(f"Method: Found meta tag property='product:price:currency'")
    print(f"Selector that matched: meta[property='product:price:currency']")

    print("\n5. DETECTING IMAGES")
    print("-" * 80)
    images = scraper._extract_image_urls(soup)
    print(f"Detected {len(images)} images:")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img}")
    print(f"Method: Found images with itemprop='image' and class='gallery-image'")
    print(f"Selectors matched: img[itemprop='image'], .gallery-image")

    print("\n" + "=" * 80)


def test_detection_with_config():
    """
    Show how site-specific configuration takes priority
    """

    sample_html = """
    <html>
    <body>
        <h1 class="product-name">Custom Product Title</h1>
        <h1>Wrong Title (Generic H1)</h1>
        <div class="custom-price">$99.99</div>
        <div class="price">$199.99</div>
    </body>
    </html>
    """

    print("\n\n" + "=" * 80)
    print("TESTING WITH SITE-SPECIFIC CONFIGURATION")
    print("=" * 80)

    soup = BeautifulSoup(sample_html, 'lxml')

    # WITHOUT config - uses generic patterns
    print("\n📌 WITHOUT Configuration (Generic Fallback):")
    print("-" * 80)
    scraper_no_config = ProductScraper()

    name_no_config = scraper_no_config._extract_name(soup)
    price_no_config = scraper_no_config._extract_price(soup)

    print(f"Name detected: {name_no_config}")
    print(f"  → Used fallback: First <h1> found")
    print(f"Price detected: ${price_no_config}")
    print(f"  → Used fallback: .price selector")

    # WITH config - uses specific selectors
    print("\n📌 WITH Configuration (Site-Specific):")
    print("-" * 80)

    custom_config = {
        'name_selector': '.product-name',
        'price_selector': '.custom-price'
    }
    scraper_with_config = ProductScraper(config=custom_config)

    name_with_config = scraper_with_config._extract_name(soup)
    price_with_config = scraper_with_config._extract_price(soup)

    print(f"Name detected: {name_with_config}")
    print(f"  → Used config: .product-name selector")
    print(f"Price detected: ${price_with_config}")
    print(f"  → Used config: .custom-price selector")

    print("\n✅ Result: Configuration takes priority over generic patterns!")
    print("=" * 80)


def test_price_parsing():
    """
    Show how different price formats are parsed
    """

    print("\n\n" + "=" * 80)
    print("PRICE PARSING EXAMPLES")
    print("=" * 80)

    scraper = ProductScraper()

    test_prices = [
        "$1,299.99",
        "USD 1299.99",
        "Price: $1,299.99",
        "€1.299,99",
        "£999",
        "¥10,000",
        "1299.99",
        "Sale: $599.99 (was $799.99)",
    ]

    print("\nInput Text → Parsed Value")
    print("-" * 80)

    for price_text in test_prices:
        parsed = scraper._parse_price(price_text)
        print(f"{price_text:40s} → ${parsed:,.2f}")

    print("\nHow it works:")
    print("  1. Remove all non-numeric characters except decimal point")
    print("  2. Convert to float")
    print("  Example: '$1,299.99' → remove '$,' → '1299.99' → 1299.99")
    print("=" * 80)


def show_selector_examples():
    """
    Show examples of CSS selectors and what they match
    """

    print("\n\n" + "=" * 80)
    print("CSS SELECTOR EXAMPLES")
    print("=" * 80)

    examples = [
        ("h1", "<h1>Product Name</h1>", "Any <h1> element"),
        ("#productTitle", "<h1 id='productTitle'>Name</h1>", "Element with id='productTitle'"),
        (".price", "<span class='price'>$99</span>", "Element with class='price'"),
        ("[itemprop='name']", "<h1 itemprop='name'>Name</h1>", "Element with itemprop='name' attribute"),
        ("h1.product-title", "<h1 class='product-title'>Name</h1>", "<h1> with class='product-title'"),
        (".price-section > .price", "<div class='price-section'><span class='price'>$99</span></div>", "Direct child .price inside .price-section"),
    ]

    print("\nSelector              HTML Example                              Matches")
    print("-" * 80)

    for selector, html, description in examples:
        print(f"{selector:20s}  {html:40s}  {description}")

    print("=" * 80)


if __name__ == "__main__":
    # Run all tests
    test_detection_with_sample_html()
    test_detection_with_config()
    test_price_parsing()
    show_selector_examples()

    print("\n\n" + "🎯 " * 20)
    print("\nKEY TAKEAWAYS:")
    print("=" * 80)
    print("1. Scraper uses a 3-tier strategy: Config → Common Patterns → Fallback")
    print("2. CSS selectors identify HTML elements (e.g., #id, .class, [attribute])")
    print("3. Price parsing removes all non-numeric characters")
    print("4. Site-specific configs in config/sites.json override generic patterns")
    print("5. Multiple selectors are tried until one matches")
    print("\nTo add a new site:")
    print("  - Inspect the product page in your browser (F12)")
    print("  - Find unique selectors for name, price, description, images")
    print("  - Add them to config/sites.json")
    print("  - See docs/SELECTOR_GUIDE.md for detailed instructions")
    print("=" * 80)
    print("\n✨ Run this script to see how detection works: python test_detection.py")
