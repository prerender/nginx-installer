import os
import sys
import argparse
from crossplane_adapter import load_nginx_config, save_nginx_config
from prerender import add_map_section, add_location_prerenderio, rewrite_root_location

DEFAULT_NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'

def parse_args():
    parser = argparse.ArgumentParser(description="Portable nginx configuration CLI tool")
    parser.add_argument('-f', '--file', help='Path to the nginx configuration file', default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    config_path = None
    config = None
    
    if args.file:
        config_path = args.file
    else:
        # Check if the default nginx configuration file exists
        if os.path.exists(DEFAULT_NGINX_CONFIG_PATH):
            use_default = input(f"Default nginx configuration found at {DEFAULT_NGINX_CONFIG_PATH}. Do you want to use it? (y/n): ")
            if use_default.lower() == 'y':
                config_path = DEFAULT_NGINX_CONFIG_PATH

    while not config_path:
        config_path = input("Please enter the path to the nginx configuration file or type 'exit' to quit: ")
        if config_path.lower() == 'exit':
            print("Exiting...")
            sys.exit(0)
        if not os.path.exists(config_path):
            print(f"The file at {config_path} does not exist. Please try again.")
            config_path = None

    # Load and parse the nginx configuration
    try:
        config = load_nginx_config(config_path)
        print("Nginx Configuration Loaded Successfully:") 
    except Exception as e:
        print(f"Error loading nginx configuration: {e}")
        sys.exit(1)

    # modify = input("Do you want to modify the nginx configuration? (y/n): ")
    if True or modify.lower() == 'y':
        add_map_section(config)
        #add_rewrite_to_root_server_location(config)
        rewrite_root_location(config)
        add_location_prerenderio(config)
        modified_config = save_nginx_config(config, './nginx.conf')
        print("Modified (Parsed) Configuration:")
        print(modified_config)

if __name__ == "__main__":
    main()