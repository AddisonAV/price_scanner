import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from database.database import DatabaseHandler
from config_loader import load_config
import os

# Load configuration from YAML file
config = load_config()
matplotlib.use('Agg')

def plot_price_history(product_name, save_to_file: bool = True):
    db = DatabaseHandler()
    # Each row is (id, name, url, currency, price, timestamp)
    data = db.fetch_data_by_name(product_name)

    save_path = config['graph']['save_path']
    os.makedirs(save_path, exist_ok=True)
    
    # Parse timestamps and extract prices.
    timestamps = [datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S") for row in data]
    prices = [row[4] for row in data]
    
    # Apply a style for a more appealing look
    plt.style.use('ggplot')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot price history with markers
    ax.plot(timestamps, prices, marker='o', linestyle='-', color='#0099ff', label='Price')
    
    # Annotate each data point with its price value
    for x, y in zip(timestamps, prices):
        ax.annotate(f'{y:.2f}', xy=(x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=10, color='black')
    
    
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
    
    if save_to_file:
        filename = f"{product_name.replace(' ', '_')}_graph.png"
        full_path = os.path.join(save_path, filename)
        plt.savefig(full_path)
        plt.close(fig)
        return full_path
    else:
        plt.show()
        return None
    
if __name__ == "__main__":
      # Required for the trend line calculation
    plot_price_history("Fone de Ouvido Galaxy Buds FE")