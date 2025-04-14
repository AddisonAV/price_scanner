# main.py

import logging
#from apscheduler.schedulers.blocking import BlockingScheduler
from config_loader import load_config
from scrapers import scraper as Scraper
from database.database import DatabaseHandler  # Import the database handler
from analysis.visualizer import plot_price_history

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

# Initialize the database handler
db_handler = DatabaseHandler()

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
            logging.error(f"Scrapping product: {product['name']}")
            
            product_data = dict() # Initialize product data dictionary
            # Scrape each URL for the first product
            for url in product['urls']:

                # Get the appropriate scraper for the URL
                scraper = Scraper.get_scraper(url)
                if not scraper:
                    logging.error(f"No scraper available for URL: {url}")
                    continue
                
                # Scrape the product data
                logging.info(f"Scraping URL: {url}")
                product_data = Scraper.compare_prices(product_data, scraper.scrape_product(url)) 
            if product_data and product_data['success']:
                logging.info(f"Scraped product data: {product_data}")

                # Save data to the database (adjust mapping as needed)
                db_handler.insert_data(
                    name=product.get('name', ''),
                    url=product_data.get('url', ''),
                    currency=product_data.get('currency', ''),
                    price=product_data.get('price', 0)
                )
            else:
                logging.error(f"Failed to scrape product data for {product['name']}")

            # Display the scraped data
            plot_price_history(product['name'])  # Call the function to plot the price history
        
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")

    logging.info("Scheduler finished.")

if __name__ == "__main__":
    main()
