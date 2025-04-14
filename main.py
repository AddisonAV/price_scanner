# main.py

import sys
import asyncio
import logging
from datetime import datetime
#from apscheduler.schedulers.blocking import BlockingScheduler  # Uncomment this line
from apscheduler.schedulers.blocking import BlockingScheduler
from config_loader import load_config
from scrapers import scraper as Scraper
from database.database import DatabaseHandler  # Import the database handler
from analysis.visualizer import plot_price_history
from bot.telegram_bot import send_alert

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load configuration from YAML file
config = load_config()

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

            # Generate graph image and get the file path
            image_path = plot_price_history(product['name'], save_to_file=True)

            # Compose a message with product info
            message = (
                f"Product: {product.get('name', '')}\n"
                f"Price: {product_data.get('currency', '')} {product_data.get('price', 0)}\n"
                f"URL: {product_data.get('url', '')}"
            )
            
            # Send Telegram alert with the graph image
            send_alert(message, image_path)
        
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")

    logging.info("Scheduler job finished.")

if __name__ == "__main__":
    # Schedule the main job using APScheduler to run every 12 hours
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'interval', hours=1, next_run_time=datetime.now())
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()  # Gracefully stop the scheduler.
        logging.info("Scheduler terminated.")