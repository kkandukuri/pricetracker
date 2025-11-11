"""Data models for the price tracker."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Product:
    """Represents a product from an ecommerce website."""
    id: Optional[int] = None
    url: str = ""
    name: str = ""
    description: str = ""
    current_price: float = 0.0
    currency: str = "USD"
    image_urls: List[str] = None
    site_name: str = ""
    upc: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []


@dataclass
class PriceHistory:
    """Represents a historical price record."""
    id: Optional[int] = None
    product_id: int = 0
    price: float = 0.0
    currency: str = "USD"
    recorded_at: Optional[datetime] = None
