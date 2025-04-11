# main.py

import logging
#from apscheduler.schedulers.blocking import BlockingScheduler
from config_loader import load_config
from scrapers.scraper import get_scraper

# Load configuration from YAML file
config = load_config()

# Test the configuration
print("Telegram Chat ID:", config['telegram']['chat_id'])
print("First Product:", config['products'][0]['name'])

# Set up basic logging using the configuration from YAML
logging.basicConfig(
    filename=config["logging"]["file"],
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

def main():
    """Main entry point to start the scheduler."""

    logging.info("Scheduler started. Press Ctrl+C to exit.")
    try:

        products = config['products']
        if not products:
            logging.error("No products found in the configuration.")
            return
        
        for product in products:
            if not product.get('urls'):
                logging.error(f"No URLs found for product: {product['name']}")
                continue
            logging.info(f"Scrapping product: {product['name']}")
            
            # Scrape each URL for the first product
            for url in product['urls']:

                # Get the appropriate scraper for the URL
                scraper = get_scraper(url)
                if not scraper:
                    logging.error(f"No scraper available for URL: {url}")
                    continue
                
                # Scrape the product data
                logging.info(f"Scraping URL: {url}")
                product_data = scraper.scrape_product(url)
                if product_data and product_data['success']:
                    logging.info(f"Scraped product data: {product_data}")
                else:
                    print("Failed to scrape product")
        
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")

if __name__ == "__main__":
    main()
