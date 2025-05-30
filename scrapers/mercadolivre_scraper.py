import time
import requests
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict
from config_loader import load_config

# Importing the base scraper class that this scraper will extend
from scrapers.scraper import BaseScraper, register_scraper

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Load configuration from YAML file
config = load_config()

# Register the scraper with a URL pattern
@register_scraper(r"mercadolivre\.com(\.br)?")
class MercadoLivreScraper(BaseScraper):
    """MercadoLivre Scraper class to scrape product prices and titles from MercadoLivre pages."""

    def __init__(self):
        self.user_agent = random.choice(config['scraping']['user_agents'])
        self.currency = config['websites']['mercadolivre']['currency']
        self.timeout = config['scraping']['request_timeout']
        self.retry_attempts = config['scraping']['retry_attempts']
        self.delay_range = (1, config['scraping']['timeout_between_requests'])

    def _get_random_delay(self):
        return random.uniform(*self.delay_range)
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract lowest price from page using multiple possible selectors"""
        selectors = [
            'div#price span.andes-money-amount',
            #'div.ui-pdp-price__main-container span.andes-money-amount'
        ]

        prices_found = []

        for selector in selectors:
            main_element = soup.select_one(selector)
            if main_element:
                try:
                    price_text = main_element.get_text(strip=True)
                    prices_value = float(price_text.replace(self.currency, '').replace(',', '.').strip())
                    prices_found.append(prices_value)
                except (ValueError, AttributeError) as e:
                    logging.warning(f"Price extraction failed with selector {selector}: {e} \n\n{price_text}\n\n")
                    continue
        
        # Now, locate the additional offers container and try to extract additional prices
        # This website often selects diferent prices for different sellers so check all displayed prices
        # in the offers container

        offers_container = soup.find("div", class_="ui-pdp-buy-box-offers__desktop")
        if offers_container:
            # Locate the specific sub-container with the second line price
            second_line_container = offers_container.find_all("div", class_="ui-pdp-price__second-line")
            for sec_container in second_line_container:
                offer_prices = sec_container.find("span", class_="andes-money-amount")
                if offer_prices:
                    try:
                        price_text = offer_prices.get_text(strip=True)
                        price_value = float(price_text.replace(self.currency, '').replace(',', '.').strip())
                        prices_found.append(price_value)
                    except (ValueError, AttributeError) as e:
                        logging.warning(f"Offers price extraction failed: {e}")
                        continue
                    
        if prices_found:
            lowest_price = min(prices_found)
            return lowest_price
        logging.error("No valid price element found")
        return None
    

    def _extract_product_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        title_selectors = [
            'h1.ui-pdp-title'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                return title_element.get_text(strip=True)
        return None           
           
            

    def scrape_product(self, url: str) -> Optional[Dict]:
        """Main scraping method with retry logic"""

        for attempt in range(self.retry_attempts):
            try:
                time.sleep(self._get_random_delay())
                
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument(f"user-agent={random.choice(self.user_agent)}")
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                # Set up Selenium WebDriver
                driver = webdriver.Chrome(options=options)
                driver.get(url)                
                
                # Wait for price to load
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#price"))
                )
            
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
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_attempts - 1:
                    logging.error(f"Final scraping failure for {url}")
                    return {
                        'price': None,
                        'title': None,
                        'currency': self.currency,
                        'url': url,
                        'success': False
                    }
            finally:
                driver.quit()
                logging.info("Selenium driver closed")

    def get_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from MercadoLivre URL"""
        # Example URL: https://www.mercadolivre.com.br/p/MLB18390579
        parsed = urlparse(url)
        path_segments = parsed.path.split('/')
        if 'p' in path_segments:
            return path_segments[path_segments.index('p') + 1]
        return None