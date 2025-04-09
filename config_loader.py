# config_loader.py

import yaml

def load_config(file_path="config/config.yaml"):
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)
    
    return config