"""Database operations for the price tracker."""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Product, PriceHistory


class Database:
    """Handles all database operations for the price tracker."""

    def __init__(self, db_path: str = "data/products.db"):
        """Initialize database connection."""
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                current_price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                image_urls TEXT,
                site_name TEXT,
                upc TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrate existing databases by adding upc column if it doesn't exist
        try:
            cursor.execute("SELECT upc FROM products LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE products ADD COLUMN upc TEXT")

        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)

        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_id
            ON price_history (product_id)
        """)

        self.conn.commit()

    def add_product(self, product: Product) -> int:
        """Add a new product to the database."""
        cursor = self.conn.cursor()
        image_urls_json = json.dumps(product.image_urls)

        cursor.execute("""
            INSERT INTO products (url, name, description, current_price,
                                 currency, image_urls, site_name, upc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product.url, product.name, product.description,
              product.current_price, product.currency,
              image_urls_json, product.site_name, product.upc))

        self.conn.commit()
        product_id = cursor.lastrowid

        # Add initial price to history
        self.add_price_history(product_id, product.current_price, product.currency)

        return product_id

    def update_product(self, product: Product) -> bool:
        """Update an existing product."""
        cursor = self.conn.cursor()
        image_urls_json = json.dumps(product.image_urls)

        # Get old price to check if it changed
        old_product = self.get_product_by_url(product.url)

        cursor.execute("""
            UPDATE products
            SET name = ?, description = ?, current_price = ?,
                currency = ?, image_urls = ?, upc = ?, updated_at = CURRENT_TIMESTAMP
            WHERE url = ?
        """, (product.name, product.description, product.current_price,
              product.currency, image_urls_json, product.upc, product.url))

        self.conn.commit()

        # Add to price history if price changed
        if old_product and old_product.current_price != product.current_price:
            self.add_price_history(old_product.id, product.current_price, product.currency)

        return cursor.rowcount > 0

    def get_product_by_url(self, url: str) -> Optional[Product]:
        """Get a product by its URL."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE url = ?", (url,))
        row = cursor.fetchone()

        if row:
            return self._row_to_product(row)
        return None

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a product by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_product(row)
        return None

    def get_all_products(self) -> List[Product]:
        """Get all products from the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY updated_at DESC")
        rows = cursor.fetchall()

        return [self._row_to_product(row) for row in rows]

    def add_price_history(self, product_id: int, price: float, currency: str = "USD"):
        """Add a price history record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO price_history (product_id, price, currency)
            VALUES (?, ?, ?)
        """, (product_id, price, currency))
        self.conn.commit()

    def get_price_history(self, product_id: int, limit: int = 100) -> List[PriceHistory]:
        """Get price history for a product."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        """, (product_id, limit))
        rows = cursor.fetchall()

        return [self._row_to_price_history(row) for row in rows]

    def _row_to_product(self, row) -> Product:
        """Convert database row to Product object."""
        image_urls = json.loads(row['image_urls']) if row['image_urls'] else []

        return Product(
            id=row['id'],
            url=row['url'],
            name=row['name'],
            description=row['description'] or "",
            current_price=row['current_price'],
            currency=row['currency'],
            image_urls=image_urls,
            site_name=row['site_name'],
            upc=row['upc'] or "",
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def _row_to_price_history(self, row) -> PriceHistory:
        """Convert database row to PriceHistory object."""
        return PriceHistory(
            id=row['id'],
            product_id=row['product_id'],
            price=row['price'],
            currency=row['currency'],
            recorded_at=datetime.fromisoformat(row['recorded_at']) if row['recorded_at'] else None
        )

    def close(self):
        """Close the database connection."""
        self.conn.close()
