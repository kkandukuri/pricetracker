#!/usr/bin/env python3
"""Quick script to analyze iHerb page structure"""
import requests
from bs4 import BeautifulSoup

url = "https://www.iherb.com/pr/now-foods-calcium-magnesium-250-tablets/453"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

print(f"Fetching: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    print("="*80)
    print("ANALYZING IHERB PAGE")
    print("="*80)

    # Find product name
    print("\n📝 PRODUCT NAME:")
    print("-"*80)

    # Try common patterns
    h1_tags = soup.find_all('h1')
    for i, h1 in enumerate(h1_tags[:3], 1):
        text = h1.get_text(strip=True)
        if text:
            print(f"{i}. Text: {text[:70]}")
            if h1.get('id'):
                print(f"   Selector: #{h1.get('id')}")
            if h1.get('class'):
                print(f"   Selector: .{h1.get('class')[0]}")

    # Find prices
    print("\n💰 POTENTIAL PRICES:")
    print("-"*80)

    price_elements = soup.find_all(class_=lambda x: x and 'price' in str(x).lower())
    for i, el in enumerate(price_elements[:5], 1):
        text = el.get_text(strip=True)
        if text and ('$' in text or any(c.isdigit() for c in text)):
            print(f"{i}. Text: {text}")
            if el.get('class'):
                print(f"   Selector: .{el.get('class')[0]}")
            if el.get('id'):
                print(f"   Selector: #{el.get('id')}")

    # Find meta tags for structured data
    print("\n🏷️  META TAGS:")
    print("-"*80)

    meta_price = soup.find('meta', property='product:price:amount')
    if meta_price:
        print(f"Price: {meta_price.get('content')}")

    meta_currency = soup.find('meta', property='product:price:currency')
    if meta_currency:
        print(f"Currency: {meta_currency.get('content')}")

    og_title = soup.find('meta', property='og:title')
    if og_title:
        print(f"Title: {og_title.get('content')}")

    og_description = soup.find('meta', property='og:description')
    if og_description:
        print(f"Description: {og_description.get('content')[:100]}...")

    # Find images
    print("\n🖼️  IMAGES:")
    print("-"*80)

    images = soup.find_all('img', alt=lambda x: x and 'now foods' in str(x).lower())
    for i, img in enumerate(images[:3], 1):
        print(f"{i}. src: {img.get('src', 'N/A')[:60]}")
        print(f"   alt: {img.get('alt', 'N/A')}")

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
