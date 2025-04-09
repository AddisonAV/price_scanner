# scrapers/amazon_scraper.py
import requests
import random
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict
import logging
from config_loader import load_config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from YAML file
config = load_config()

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': random.choice(config['scraping']['user_agents']),
            'Accept-Language': config['scraping']['headers']['Accept-Language'],
            'Accept-Encoding': config['scraping']['headers']['Accept-Encoding'],
            'X-Forwarded-For' : config['scraping']['headers']['X-Forwarded-For']
        }
        self.base_url = config['websites']['amazon']['base_url']
        self.currency = config['websites']['amazon']['currency']
        self.timeout = config['scraping']['request_timeout']
        self.retry_attempts = config['scraping']['retry_attempts']
        self.delay_range = config['scraping']['delay_between_requests']

    def _get_random_delay(self):
        return random.uniform(self.delay_range, self.delay_range + 2)  # Adding a small jitter to the delay

    def _validate_url(self, url: str) -> bool:
        """Validate Amazon product URL structure"""
        parsed = urlparse(url)
        if not parsed.netloc.endswith(('amazon.com', 'amazon.com.br')):
            logger.error(f"Invalid Amazon domain: {parsed.netloc}")
            return False
        if '/dp/' not in url and '/product/' not in url:
            logger.error("URL doesn't contain product identifier")
            return False
        return True

    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from page using multiple possible selectors"""
        selectors = [
            'span#subscriptionPrice span.a-price span.a-offscreen',
            'div#centerCol span.a-price span.a-offscreen',
            'span.a-price span[aria-hidden="true"]'
            #'span.a-price span.a-offscreen',  # Most common
            #'span#priceblock_ourprice',
            #'span#priceblock_dealprice',
            #'div#apex_desktop span.a-price-whole',
            #'span.aok-offscreen',
            #'span#tp_price_block_total_price_ww'
        ]

        for selector in selectors:
            price_element = soup.select_one(selector)
            if price_element:
                try:
                    price_text = price_element.get_text(strip=True)
                    return float(price_text.replace(self.currency, '').replace(',', '.').strip())
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Price extraction failed with selector {selector}: {e} \n\n{price_text}\n\n")
                    continue

        logger.error("No valid price element found")
        return None

    def _extract_product_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        title_selectors = [
            'span#productTitle',
            'h1#title'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                return title_element.get_text(strip=True)
        return None           
           
            

    def scrape_product(self, url: str) -> Optional[Dict]:
        """Main scraping method with retry logic"""
        if not self._validate_url(url):
            return None

        for attempt in range(self.retry_attempts):
            try:
                
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument(f"user-agent={random.choice(self.headers['User-Agent'])}")
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                # Set up Selenium WebDriver
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                logger.info(f"Accessing URL: {url} with Selenium")
                
                
                # Wait for price to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#centerCol"))
                )
                driver.save_screenshot('last_page.png')
                # 3. Get fully rendered page source
                page_source = driver.page_source
                
                # 4. Switch to BeautifulSoup for parsing
                soup = BeautifulSoup(page_source, 'lxml')
                
                
                return {
                    'price': self._extract_price(soup),
                    'title': self._extract_product_title(soup),
                    'currency': self.currency,
                    'url': url,
                    'success': True
                }
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Final scraping failure for {url}")
                    return {
                        'price': None,
                        'title': None,
                        'currency': self.currency,
                        'url': url,
                        'success': False
                    }
            finally:
                driver.quit()
                logger.info("Selenium driver closed")

    def get_product_id(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL"""
        parsed = urlparse(url)
        path_segments = parsed.path.split('/')
        if 'dp' in path_segments:
            return path_segments[path_segments.index('dp') + 1]
        return None