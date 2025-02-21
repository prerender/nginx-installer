import os
import sys
import argparse
from config_utils import load_nginx_config
from crossplane_adapter import load_nginx_config, save_nginx_onfig

DEFAULT_NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'

def parse_args():
    parser = argparse.ArgumentParser(description="Portable nginx configuration CLI tool")
    parser.add_argument('-f', '--file', help='Path to the nginx configuration file', default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.file:
        config_path = args.file
    else:
        # Check if the default nginx configuration file exists
        if os.path.exists(DEFAULT_NGINX_CONFIG_PATH):
            use_default = input(f"Default nginx configuration found at {DEFAULT_NGINX_CONFIG_PATH}. Do you want to use it? (y/n): ")
            if use_default.lower() == 'y':
                config_path = DEFAULT_NGINX_CONFIG_PATH
            else:
                config_path = input("Please specify the path to the nginx configuration file: ")
        else:
            config_path = input(f"No default configuration found. Please specify the path to the nginx configuration file: ")

    # Load and parse the nginx configuration
    try:
        config = load_nginx_config(config_path)
        print("Nginx Configuration Loaded Successfully:")
        print(config)
    except Exception as e:
        print(f"Error loading nginx configuration: {e}")
        sys.exit(1)

    # Example modification (this can be expanded based on user input)
    # modify = input("Do you want to modify the nginx configuration? (y/n): ")
    if True or modify.lower() == 'y':
        try:
            # Pass the configuration file path to the adapter for parsing
            modified_config = save_nginx_onfig(config, config_path + '.modified')
            print("Modified (Parsed) Configuration:")
            print(modified_config)
        except Exception as e:
            print(f"Error modifying configuration: {e}")

if __name__ == "__main__":
    main()