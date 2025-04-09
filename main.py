# main.py

import datetime
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from config_loader import load_config

# Load configuration from YAML file
config = load_config()

# Dummy functions for demonstration. Replace these with your actual implementations.
def get_price(url):
    """Dummy function to simulate scraping and returning a price."""
    import random
    return round(random.uniform(50.0, 150.0), 2)

def insert_price(product_name, price, timestamp):
    """Dummy function to simulate inserting price into a database."""
    print(f"Inserted: {product_name}, {price} at {timestamp}")

def get_price_history(product_name):
    """Dummy function that returns a list of (timestamp, price) tuples."""
    now = datetime.datetime.now()
    return [(now, get_price("dummy_url")) for _ in range(10)]

def generate_graph(price_history, product_name):
    """Dummy function to simulate generating and saving a graph. Returns the filename."""
    import matplotlib.pyplot as plt

    # Unpack timestamps and prices
    timestamps, prices = zip(*price_history)
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, prices, marker='o', label=product_name)
    plt.title(f"Price History for {product_name}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    filename = f"{product_name}_price_history.png"
    plt.savefig(filename)
    plt.close()
    return filename

def send_message_with_graph(message, image_path):
    """Dummy function to simulate sending a message and graph via Telegram."""
    print(f"Sending message: {message} with image: {image_path}")

# Set up basic logging using the configuration from YAML
logging.basicConfig(
    filename=config["logging"]["file"],
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

def job():
    """Scheduled job to scrape prices, update database, generate graph, and send notification."""
    logging.info("Job started.")
    for product_name, urls in config["scraper"]["targets"].items():
        logging.info(f"Processing {product_name} from {urls}")
        
        # 1. Scrape current price
        try:
            current_price = get_price(urls)
            logging.info(f"Scraped price for {product_name}: {current_price}")
        except Exception as e:
            logging.error(f"Error scraping {urls}: {e}")
            continue

        # 2. Insert the price into the database with current timestamp
        timestamp = datetime.datetime.now()
        try:
            insert_price(product_name, current_price, timestamp)
        except Exception as e:
            logging.error(f"Error inserting price for {product_name} into database: {e}")
            continue

        # 3. Retrieve price history and generate a graph
        try:
            price_history = get_price_history(product_name)
            graph_file = generate_graph(price_history, product_name)
            logging.info(f"Graph generated for {product_name}: {graph_file}")
        except Exception as e:
            logging.error(f"Error generating graph for {product_name}: {e}")
            continue

        # 4. Build message and send via Telegram bot
        message = f"Latest price for {product_name}: ${current_price}"
        try:
            send_message_with_graph(message, graph_file)
            logging.info(f"Notification sent for {product_name}.")
        except Exception as e:
            logging.error(f"Error sending Telegram message for {product_name}: {e}")
            continue

    logging.info("Job finished.")

def main():
    """Main entry point to start the scheduler."""
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=config["scheduler"]["scrape_interval"])
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")

if __name__ == "__main__":
    main()
