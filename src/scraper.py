"""Web scraper for extracting product information from ecommerce websites."""
import re
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .models import Product


class ProductScraper:
    """Base scraper for extracting product information."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scraper.

        Args:
            config: Configuration dictionary with CSS selectors for the site
        """
        self.config = config or {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_product(self, url: str) -> Optional[Product]:
        """
        Scrape product information from a URL.

        Args:
            url: Product URL to scrape

        Returns:
            Product object with scraped data, or None if scraping failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            site_name = self._get_site_name(url)

            product = Product(
                url=url,
                name=self._extract_name(soup),
                description=self._extract_description(soup),
                current_price=self._extract_price(soup),
                currency=self._extract_currency(soup),
                image_urls=self._extract_image_urls(soup),
                site_name=site_name,
                upc=self._extract_upc(soup)
            )

            return product

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def _get_site_name(self, url: str) -> str:
        """Extract site name from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from the page."""
        # Try configured selector first
        if 'name_selector' in self.config:
            element = soup.select_one(self.config['name_selector'])
            if element:
                return element.get_text(strip=True)

        # Common selectors for product names
        selectors = [
            'h1[itemprop="name"]',
            'h1.product-title',
            'h1#productTitle',
            'h1.product-name',
            'h1',
            '[data-testid="product-title"]',
            '.product-title',
            '#product-title',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        # Fallback to first h1
        h1 = soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Unknown Product"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract product description from the page."""
        # Try configured selector first
        if 'description_selector' in self.config:
            element = soup.select_one(self.config['description_selector'])
            if element:
                return element.get_text(strip=True)

        # Common selectors for product descriptions
        selectors = [
            '[itemprop="description"]',
            '#productDescription',
            '.product-description',
            '.description',
            '[data-testid="product-description"]',
            'meta[name="description"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # For meta tags, get content attribute
                if element.name == 'meta':
                    return element.get('content', '')
                return element.get_text(strip=True)

        return ""

    def _extract_price(self, soup: BeautifulSoup) -> float:
        """Extract product price from the page."""
        # Try configured selector first
        if 'price_selector' in self.config:
            element = soup.select_one(self.config['price_selector'])
            if element:
                return self._parse_price(element.get_text(strip=True))

        # Common selectors for prices
        selectors = [
            '[itemprop="price"]',
            '.price',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.product-price',
            '[data-testid="product-price"]',
            '.a-price-whole',
            'span.price',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price > 0:
                    return price

        # Try to find price in meta tags
        meta_price = soup.select_one('meta[property="product:price:amount"]')
        if meta_price:
            return float(meta_price.get('content', 0))

        return 0.0

    def _parse_price(self, price_text: str) -> float:
        """Parse price from text."""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', price_text)
            if cleaned:
                return float(cleaned)
        except (ValueError, AttributeError):
            pass
        return 0.0

    def _extract_currency(self, soup: BeautifulSoup) -> str:
        """Extract currency from the page."""
        # Try configured selector first
        if 'currency_selector' in self.config:
            element = soup.select_one(self.config['currency_selector'])
            if element:
                return element.get_text(strip=True)

        # Try meta tags
        meta_currency = soup.select_one('meta[property="product:price:currency"]')
        if meta_currency:
            return meta_currency.get('content', 'USD')

        # Try to detect from price text
        price_element = soup.select_one('[itemprop="price"]')
        if price_element:
            text = price_element.get_text()
            if '$' in text:
                return 'USD'
            elif '€' in text:
                return 'EUR'
            elif '£' in text:
                return 'GBP'
            elif '¥' in text:
                return 'JPY'

        return 'USD'  # Default

    def _extract_image_urls(self, soup: BeautifulSoup) -> list:
        """Extract product image URLs from the page."""
        image_urls = []

        # Try configured selector first
        if 'image_selector' in self.config:
            elements = soup.select(self.config['image_selector'])
            for element in elements:
                img_url = element.get('src') or element.get('data-src')
                if img_url and img_url.startswith('http'):
                    image_urls.append(img_url)
            if image_urls:
                return image_urls

        # Common selectors for product images
        selectors = [
            'img[itemprop="image"]',
            '.product-image img',
            '#landingImage',
            '#imgTagWrapperId img',
            '[data-testid="product-image"]',
            '.gallery-image img',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                img_url = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
                if img_url:
                    # Make absolute URL if relative
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        # Would need base URL for this
                        continue
                    if img_url.startswith('http') and img_url not in image_urls:
                        image_urls.append(img_url)

        # Fallback: find all images in product containers
        if not image_urls:
            product_containers = soup.select('.product, #product, [id*="product"]')
            for container in product_containers:
                images = container.find_all('img')
                for img in images:
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and img_url.startswith('http') and img_url not in image_urls:
                        image_urls.append(img_url)

        return image_urls[:5]  # Return max 5 images

    def _extract_upc(self, soup: BeautifulSoup) -> str:
        """Extract UPC/EAN/GTIN from the page."""
        # Try configured selector first
        if 'upc_selector' in self.config:
            element = soup.select_one(self.config['upc_selector'])
            if element:
                upc = element.get_text(strip=True)
                if self._is_valid_upc(upc):
                    return upc

        # Try meta tags for structured data
        meta_selectors = [
            'meta[property="product:upc"]',
            'meta[itemprop="gtin12"]',
            'meta[itemprop="gtin13"]',
            'meta[itemprop="gtin14"]',
            'meta[itemprop="gtin"]',
            'meta[itemprop="ean"]',
            'meta[itemprop="isbn"]',
            'meta[name="upc"]',
            'meta[name="gtin"]',
        ]

        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta:
                upc = meta.get('content', '')
                if self._is_valid_upc(upc):
                    return upc

        # Common CSS selectors for UPC
        selectors = [
            '.upc',
            '#upc',
            '[data-upc]',
            '.product-upc',
            '.product-code',
            '[itemprop="gtin12"]',
            '[itemprop="gtin13"]',
            '[itemprop="gtin14"]',
            'span:contains("UPC")',
            'span:contains("GTIN")',
            'span:contains("EAN")',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # For data attributes
                if element.has_attr('data-upc'):
                    upc = element.get('data-upc')
                    if self._is_valid_upc(upc):
                        return upc

                # For text content
                text = element.get_text(strip=True)
                upc = self._extract_upc_from_text(text)
                if upc:
                    return upc

        # Search entire page for UPC patterns in product details
        product_sections = soup.select('.product-details, .product-info, #product-details, [id*="product"]')
        for section in product_sections:
            text = section.get_text()
            upc = self._extract_upc_from_text(text)
            if upc:
                return upc

        return ""

    def _extract_upc_from_text(self, text: str) -> str:
        """Extract UPC from text using regex patterns."""
        # Remove whitespace and special characters
        text = text.replace(' ', '').replace('-', '').replace(':', '')

        # Look for UPC/GTIN/EAN followed by digits
        patterns = [
            r'UPC[:\s]*(\d{12,14})',
            r'GTIN[:\s]*(\d{12,14})',
            r'EAN[:\s]*(\d{12,14})',
            r'ISBN[:\s]*(\d{10,13})',
            r'\b(\d{12})\b',  # 12-digit UPC
            r'\b(\d{13})\b',  # 13-digit EAN
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                upc = match.group(1) if match.lastindex else match.group(0)
                if self._is_valid_upc(upc):
                    return upc

        return ""

    def _is_valid_upc(self, upc: str) -> bool:
        """Validate UPC format."""
        # Remove non-digits
        upc = re.sub(r'\D', '', upc)

        # Valid UPC lengths: 10 (ISBN-10), 12 (UPC-A), 13 (EAN-13, ISBN-13), 14 (GTIN-14)
        return len(upc) in [10, 12, 13, 14] and upc.isdigit()


class SeleniumScraper(ProductScraper):
    """Scraper using Selenium for JavaScript-heavy sites."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Selenium scraper."""
        super().__init__(config)
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        if not self.driver:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')

            self.driver = webdriver.Chrome(options=options)

    def scrape_product(self, url: str) -> Optional[Product]:
        """Scrape product using Selenium."""
        try:
            self._init_driver()
            self.driver.get(url)

            # Wait for page to load
            time.sleep(3)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            site_name = self._get_site_name(url)

            product = Product(
                url=url,
                name=self._extract_name(soup),
                description=self._extract_description(soup),
                current_price=self._extract_price(soup),
                currency=self._extract_currency(soup),
                image_urls=self._extract_image_urls(soup),
                site_name=site_name,
                upc=self._extract_upc(soup)
            )

            return product

        except Exception as e:
            print(f"Error scraping {url} with Selenium: {str(e)}")
            return None

    def close(self):
        """Close the Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
