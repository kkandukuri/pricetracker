#!/usr/bin/env python3
"""
Selector Finder - Automatically find CSS selectors for any e-commerce site

Usage:
    python find_selectors.py <product-url>
    python find_selectors.py <product-url> --selenium

Examples:
    python find_selectors.py "https://www.distacart.com/product/12345"
    python find_selectors.py "https://www.instacart.com/store/items/item_123" --selenium
"""
import sys
import argparse


def find_with_requests(url):
    """Find selectors using simple HTTP request."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    print(f"Fetching: {url}")
    print("Method: HTTP Request (BeautifulSoup)\n")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        analyze_page(soup, url)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try using --selenium flag for JavaScript-heavy sites")


def find_with_selenium(url):
    """Find selectors using Selenium (for JavaScript sites)."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    import time

    print(f"Fetching: {url}")
    print("Method: Selenium (Chrome Headless)\n")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        print("⏳ Waiting for JavaScript to load...")
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        analyze_page(soup, url)

    except Exception as e:
        print(f"❌ Error: {e}")
        if "chromedriver" in str(e).lower():
            print("\n💡 ChromeDriver not found. Install with:")
            print("   Ubuntu/Debian: sudo apt-get install chromium-chromedriver")
            print("   macOS: brew install chromedriver")
    finally:
        if driver:
            driver.quit()


def analyze_page(soup, url):
    """Analyze the page and suggest selectors."""

    # Extract domain
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace('www.', '')

    print("="*80)
    print(f"ANALYZING: {domain}")
    print("="*80)

    # 1. Find product names
    print("\n📝 POTENTIAL PRODUCT NAMES (h1 tags):")
    print("-"*80)

    h1_tags = soup.find_all('h1')
    if h1_tags:
        for i, h1 in enumerate(h1_tags[:5], 1):
            text = h1.get_text(strip=True)
            if text:
                print(f"\n{i}. Text: {text[:70]}")

                selectors = []
                if h1.get('id'):
                    selectors.append(f"#{h1.get('id')}")
                if h1.get('class'):
                    selectors.append(f".{h1.get('class')[0]}")
                if h1.get('data-testid'):
                    selectors.append(f"[data-testid='{h1.get('data-testid')}']")

                if selectors:
                    print(f"   Suggested selectors: {', '.join(selectors)}")
                else:
                    print(f"   Suggested selector: h1")
    else:
        print("   ⚠️  No h1 tags found")

    # 2. Find prices
    print("\n💰 POTENTIAL PRICES:")
    print("-"*80)

    price_candidates = []

    # Find by class/id containing "price"
    for element in soup.find_all(class_=lambda x: x and 'price' in str(x).lower()):
        text = element.get_text(strip=True)
        if text and ('$' in text or '€' in text or '£' in text or any(c.isdigit() for c in text)):
            price_candidates.append({
                'element': element,
                'text': text,
                'method': 'class'
            })

    # Find by data-testid
    for element in soup.find_all(attrs={'data-testid': lambda x: x and 'price' in str(x).lower()}):
        text = element.get_text(strip=True)
        if text:
            price_candidates.append({
                'element': element,
                'text': text,
                'method': 'data-testid'
            })

    # Find by itemprop
    for element in soup.find_all(attrs={'itemprop': 'price'}):
        text = element.get_text(strip=True)
        if text:
            price_candidates.append({
                'element': element,
                'text': text,
                'method': 'itemprop'
            })

    if price_candidates:
        seen_texts = set()
        for i, candidate in enumerate(price_candidates[:10], 1):
            text = candidate['text']
            if text in seen_texts:
                continue
            seen_texts.add(text)

            print(f"\n{i}. Text: {text}")

            element = candidate['element']
            selectors = []

            if element.get('id'):
                selectors.append(f"#{element.get('id')}")
            if element.get('class'):
                selectors.append(f".{element.get('class')[0]}")
            if element.get('data-testid'):
                selectors.append(f"[data-testid='{element.get('data-testid')}']")
            if element.get('itemprop'):
                selectors.append(f"[itemprop='{element.get('itemprop')}']")

            if selectors:
                print(f"   Suggested selectors: {', '.join(selectors)}")
    else:
        print("   ⚠️  No price elements found")

    # 3. Find descriptions
    print("\n📄 POTENTIAL DESCRIPTIONS:")
    print("-"*80)

    desc_candidates = []

    # Find by class/id containing "description"
    for element in soup.find_all(class_=lambda x: x and 'description' in str(x).lower()):
        text = element.get_text(strip=True)
        if text and len(text) > 20:
            desc_candidates.append(element)

    # Find by data-testid
    for element in soup.find_all(attrs={'data-testid': lambda x: x and 'description' in str(x).lower()}):
        text = element.get_text(strip=True)
        if text:
            desc_candidates.append(element)

    # Find by itemprop
    for element in soup.find_all(attrs={'itemprop': 'description'}):
        text = element.get_text(strip=True)
        if text:
            desc_candidates.append(element)

    if desc_candidates:
        for i, element in enumerate(desc_candidates[:5], 1):
            text = element.get_text(strip=True)
            print(f"\n{i}. Text: {text[:100]}...")

            selectors = []
            if element.get('id'):
                selectors.append(f"#{element.get('id')}")
            if element.get('class'):
                selectors.append(f".{element.get('class')[0]}")
            if element.get('data-testid'):
                selectors.append(f"[data-testid='{element.get('data-testid')}']")

            if selectors:
                print(f"   Suggested selectors: {', '.join(selectors)}")
    else:
        print("   ⚠️  No description elements found")

    # 4. Find images
    print("\n🖼️  PRODUCT IMAGES:")
    print("-"*80)

    img_tags = soup.find_all('img')
    product_images = []

    for img in img_tags:
        src = img.get('src', '')
        alt = img.get('alt', '').lower()

        # Filter likely product images
        if ('product' in alt or 'item' in alt or
            'product' in str(img.get('class', '')).lower() or
            any(x in src.lower() for x in ['product', 'item', 'image', 'img'])):
            product_images.append(img)

    if product_images:
        for i, img in enumerate(product_images[:5], 1):
            src = img.get('src', 'N/A')
            print(f"\n{i}. src: {src[:70]}...")
            print(f"   alt: {img.get('alt', 'N/A')[:50]}")

            selectors = []
            if img.get('id'):
                selectors.append(f"img#{img.get('id')}")
            if img.get('class'):
                selectors.append(f"img.{img.get('class')[0]}")
            if img.get('data-testid'):
                selectors.append(f"img[data-testid='{img.get('data-testid')}']")

            if selectors:
                print(f"   Suggested selectors: {', '.join(selectors)}")
    else:
        print("   ⚠️  No product images found")
        print(f"   Total images on page: {len(img_tags)}")

    # 5. Generate config
    print("\n" + "="*80)
    print("SUGGESTED CONFIGURATION")
    print("="*80)

    # Build suggested config
    name_sel = ""
    if h1_tags and h1_tags[0].get('id'):
        name_sel = f"#{h1_tags[0].get('id')}"
    elif h1_tags and h1_tags[0].get('class'):
        name_sel = f".{h1_tags[0].get('class')[0]}"
    else:
        name_sel = "h1"

    price_sel = ""
    if price_candidates:
        el = price_candidates[0]['element']
        if el.get('class'):
            price_sel = f".{el.get('class')[0]}"
        elif el.get('data-testid'):
            price_sel = f"[data-testid='{el.get('data-testid')}']"

    desc_sel = ""
    if desc_candidates:
        el = desc_candidates[0]
        if el.get('class'):
            desc_sel = f".{el.get('class')[0]}"
        elif el.get('id'):
            desc_sel = f"#{el.get('id')}"

    img_sel = ""
    if product_images:
        img = product_images[0]
        if img.get('class'):
            img_sel = f"img.{img.get('class')[0]}"
        elif img.get('id'):
            img_sel = f"img#{img.get('id')}"

    print(f"""
Add this to config/sites.json:

{{
  "{domain}": {{
    "name_selector": "{name_sel or 'h1'}",
    "price_selector": "{price_sel or '.price'}",
    "description_selector": "{desc_sel or '.description'}",
    "image_selector": "{img_sel or 'img'}"
  }}
}}
""")

    print("="*80)
    print("\n✅ Analysis complete!")
    print("\n💡 Next steps:")
    print(f"   1. Update config/sites.json with the suggested configuration")
    print(f"   2. Test with: python main.py add \"{url}\"")
    print(f"   3. Adjust selectors if needed based on results")


def main():
    parser = argparse.ArgumentParser(
        description='Find CSS selectors for scraping e-commerce product pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python find_selectors.py "https://www.distacart.com/product/12345"
  python find_selectors.py "https://www.amazon.com/dp/B08N5WRWNW"
  python find_selectors.py "https://www.instacart.com/store/items/item_123" --selenium
        """
    )

    parser.add_argument('url', help='Product URL to analyze')
    parser.add_argument('--selenium', action='store_true',
                       help='Use Selenium for JavaScript-heavy sites')

    args = parser.parse_args()

    if args.selenium:
        find_with_selenium(args.url)
    else:
        find_with_requests(args.url)


if __name__ == "__main__":
    main()
