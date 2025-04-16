# main.py

import sys
import asyncio
import logging
from datetime import datetime
import time
#from apscheduler.schedulers.blocking import BlockingScheduler  # Uncomment this line
from apscheduler.schedulers.background import BackgroundScheduler
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

def job():
    """Job to be run by the scheduler."""
    logging.info("Scheduler job started.")
    
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
        
    except Exception as e:
        logging.error(f"Job error: {e}")
    logging.info("Scheduler job finished.")

def main():
    """Main entry point to start the scheduler."""
    scheduler = BackgroundScheduler()

    # 'cron' for defining the job schedule every day at 9:00 AM
    scheduler.add_job(job, 'cron', hour=9, minute=0, next_run_time=datetime.now())
    scheduler.start()
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        # Main loop waiting to be interrupted.
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Requesting shutdown...")
        # Handle shutdown gracefully
        logging.info("Shutdown requested. Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        logging.info("Scheduler terminated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
    