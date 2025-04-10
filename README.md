# Price Scanner

Price Scanner is a Python-based tool for scraping product prices and details from various e-commerce websites. It leverages Selenium, BeautifulSoup, and YAML configuration to offer a configurable and extensible framework for web scraping.

## Features

- **Multi-website scraping:** Easily extend the project with new scraper classes.
- **Configurable settings:** Change product, website, logging, and scraping options through a YAML config file.
- **Scheduler integration:** Supports scheduling scraping tasks (APScheduler).
- **Alerting and notifications:** (Future feature) Configure alerts for price changes.

## Project Structure

    price_scanner/
    ├── bot/                      # Telegram bot integration (planned)
    ├── config/                   
    │   ├── config.yaml           # Main configuration file (create manualy)
    │   └── example_config.yaml   # Sample configuration
    ├── analysis/                 # Price analysis and visualization scripts (planned)
    ├── scheduler/                # Job scheduler and related code (planned)
    ├── scrapers/                 
    │   ├── amazon_scraper.py     # Amazon-specific scraping logic
    │   ├── scraper.py            # Base class and registration system
    │   └── __init__.py           # Auto-import scrapers for registration
    ├── storage/                  # Database-related code (planned)
    ├── config_loader.py          # YAML configuration loader 
    ├── requirements.txt          # List of project dependencies
    └── main.py                   # Main entry point for the scraper

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your_username/price_scanner.git
   cd price_scanner
   ```

2. **Set up a virtual environment:**
    - For Command Prompt:

    ```sh
    python -m venv venv
    .\venv\Scripts\activate
    ```

    - For PowerShell:
    
     ```sh
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

3. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```
    

## Configuration

- Update `config/config.yaml` with your Telegram bot credentials, product details, website settings, and other configurations.

- An example configuration is provided in `example_config.yaml`.

## Running the Project

Run the main scraper via:

```sh
python main.py
```
This will start the scraping process as defined in `main.py` and output product data and logs as configured.


## Adding New Scrapers

- Create a new scraper subclass extending ``BaseScraper`` in the scrapers directory.
- Use the ``@register_scraper`` decorator with the appropriate URL pattern.
- Import your new scraper in ``__init__.py`` to ensure it registers automatically.
    

## Logging
The project logs events as defined in your configuration. Check the log file (default: app.log) for runtime details, errors, and info messages.

## Future Enhancements

- **Alerting**: Implement notifications on price drop events.
- **Database Storage**: Save price history to a SQLite database.
- **Analysis and Visualization**: Use collected data for trend analysis.

## Contributing
Feel free to open issues or submit pull requests for improvements or bug fixes.

Happy scraping!