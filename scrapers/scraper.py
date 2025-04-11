import re
from abc import ABC, abstractmethod
from typing import Optional, Dict


# Mapping of URL patterns to scraper classes
SCRAPER_REGISTRY = {}

def register_scraper(pattern: str):
    """Decorator to register scraper classes with a URL pattern."""
    def decorator(cls):
        SCRAPER_REGISTRY[pattern] = cls
        return cls
    return decorator

class BaseScraper(ABC):
    @abstractmethod
    def _extract_price(self, soup) -> Optional[float]:
        """Extract price from page using multiple possible selectors"""
        pass
    def _extract_product_title(self, soup) -> Optional[str]:
        """Extract product title"""
        pass
    def scrape_product(self, url: str) -> Optional[Dict]: 
        """Main scraping method with retry logic"""
        pass
    def get_product_id(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL"""
        pass


def get_scraper(url: str) -> BaseScraper:
    for pattern, scraper_class in SCRAPER_REGISTRY.items():
        if re.search(pattern, url, re.IGNORECASE):
            return scraper_class()
    raise ValueError(f"No scraper available for URL: {url}")
