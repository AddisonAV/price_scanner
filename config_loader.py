# config_loader.py

import yaml

def load_config(file_path="config/config.yaml"):
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)
        
    print("Telegram Chat ID:", config['telegram']['chat_id'])
    print("First Product:", config['products'][0]['name'])
    
    return config