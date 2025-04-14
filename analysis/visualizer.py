import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from database.database import DatabaseHandler

def plot_price_history(product_name):
    db = DatabaseHandler()
    # Each row is (id, name, url, currency, price, timestamp)
    data = db.fetch_data_by_name(product_name)
    
    # Parse timestamps and extract prices.
    timestamps = [datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S") for row in data]
    prices = [row[4] for row in data]
    
    # Apply a style for a more appealing look
    plt.style.use('ggplot')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot price history with markers
    ax.plot(timestamps, prices, marker='o', linestyle='-', color='#0099ff', label='Price')
    
    
    ax.set_title(f"Price History for {product_name}", fontsize=16)
    ax.set_xlabel("Timestamp", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    
    # Rotate and format x-axis ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
      # Required for the trend line calculation
    plot_price_history("Fone de Ouvido Galaxy Buds FE")