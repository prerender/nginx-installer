import os
import sys
import argparse
from crossplane_adapter import load_nginx_config, save_nginx_config
from prerender import add_map_section, add_location_prerenderio, rewrite_root_location, get_all_server_blocks_with_names
from site_url import check_access, check_integration
import logging
from temp_file_utils import temp_file_factory

logger = logging.getLogger(__name__)
site_url_data = temp_file_factory("./.prerender_site_url")
token_data = temp_file_factory("./.prerender_token")

DEFAULT_NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'

def parse_args():
    parser = argparse.ArgumentParser(description="Portable nginx configuration CLI tool")
    parser.add_argument('-f', '--file', help='Path to the nginx configuration file', default=None)
    parser.add_argument('-o', '--output', help='Path to save the modified nginx configuration file', default=None)
    parser.add_argument('-m', '--modify', help='Modify the nginx configuration', default=False)
    parser.add_argument('-t', '--token', help='Prerender token', default=None)
    parser.add_argument('-u', '--url', help='URL of the site to integrate with Prerender.io', default=None)
    parser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    config_path = None
    config = None
    output_path = None
    site_url = None
    site_available = False

    if args.url:
        site_url = args.url
    else:
        site_url = site_url_data.get_data()
        
        if site_url:
            proceed = input(f"Do you want to integrate {site_url}? (y/n): ")
            if proceed.lower() != 'y':
                site_url = None 
                site_url_data.cleanup()

    while not site_available:
        if not site_url:
            site_url = input("Please enter the URL of the site to integrate with Prerender.io: ")
        print(f"Checking if the site at {site_url} is accessible...")
        site_available = check_access(site_url)
        if not site_available:
            site_url = None
        else:
            prerender_verified = check_integration(site_url)
            if prerender_verified:
                print(f"Prerender integration exists for {site_url}")
                print("Do you want to integrate another site (y/n)?")                
                if input().lower() == 'n':
                    site_url = None
                    site_url_data.cleanup()
                    site_available = False
                else:
                    sys.exit(0)
            
    site_url_data.save_data(site_url)
    
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
            sys.exit(0)
        if not os.path.exists(config_path):
            print(f"The file at {config_path} does not exist. Please try again.")
            config_path = None

    # Make a backup of the nginx configuration file
    backup_index = 1
    backup_path = f"{config_path}.backup-{backup_index}"
    while os.path.exists(backup_path):
        backup_index += 1
        backup_path = f"{config_path}.backup-{backup_index}"
    
    try:
        with open(config_path, 'r') as original_file:
            with open(backup_path, 'w') as backup_file:
                backup_file.write(original_file.read())
        print(f"Backup of the nginx configuration file created at {backup_path}")
    except Exception as e:
        print(f"Error creating backup of nginx configuration: {e}")
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        output_path = config_path

    # Load and parse the nginx configuration
    try:
        config = load_nginx_config(config_path)
        print("Nginx Configuration Loaded Successfully.") 
    except Exception as e:
        print(f"Error loading nginx configuration: {e}")
        sys.exit(1)

    is_modified = False

    try:
        # Get all server blocks with their server names
        selected_server_block = None
        server_blocks_with_names = get_all_server_blocks_with_names(config)

        def get_server_name(server_block):
            if server_block[1]:
                return server_block[1]
            
            return "default (no server_name)"

        print("Following server configurations were found:")
        for i, (server_block) in enumerate(server_blocks_with_names):
            print(f"  {i + 1}. {get_server_name(server_block)}")

        if not server_blocks_with_names:
            raise Exception("No server blocks found in the nginx configuration")
        
        if len(server_blocks_with_names) == 1:
            selected_server_block = server_blocks_with_names[0]
        else:
            while not selected_server_block:
                try:
                    selected_server_block_index = int(input("Which server do you want to integrate? (1,2,3...): "))
                    selected_server_block = server_blocks_with_names[selected_server_block_index - 1]
                except Exception as e:
                    print(f"Invalid input: {e}")
                    selected_server_block = None

        print(f"Selected server configuration: {get_server_name(selected_server_block)}")

        # figure out the Prerender token
        prerender_token = None

        if args.token:
            prerender_token = args.token
        else:
            saved_token = token_data.get_data()
            if saved_token:
                use_saved_token = input(f"A saved Prerender token \"{saved_token}\" was found. Do you want to use it? (y/n): ")
                if use_saved_token.lower() == 'y':
                    prerender_token = saved_token

        if not prerender_token:
            prerender_token = input("Please enter your Prerender token: ")

        if not prerender_token:
            raise Exception("Prerender token is required to proceed.")
        
        # Save the Prerender token to a file
        try:
            token_data.save_data(prerender_token)
        except Exception as e:
            logger.debug(f"Error saving Prerender token to file: {e}")

        shall_modify = args.modify

        if not shall_modify:
            input_modify = input("Do you want to modify the nginx configuration? (y/n): ")
            if input_modify.lower() == 'y':
                shall_modify = True

        if not os.path.exists(backup_path) or os.path.getsize(backup_path) == 0:
            raise Exception("Unsafe to proceed : backup file is not found or corrupted")
        
        if shall_modify:
            add_map_section(config)
            rewrite_root_location(selected_server_block[0])
            add_location_prerenderio(selected_server_block[0], prerender_token)
            save_nginx_config(config, output_path)
            is_modified = True
            print(f"Modified nginx configuration saved to {output_path}")

    except Exception as e:
        print(f"Error : {e}")

        if is_modified:
            print(f"Config at {output_path} was modified and may be in an inconsistent state.")
        
            # Restore the backup file
            restore_backup = input("Do you want to restore the original nginx configuration file from backup? (y/n): ")
            if restore_backup.lower() == 'y':
                try:
                    os.remove(config_path)
                    os.rename(backup_path, config_path)
                    print(f"Restored the original nginx configuration file from {backup_path}")
                except Exception as e:
                    print(f"Error restoring the original nginx configuration file: {e}")

    if not is_modified:
        print("No modifications were made to the nginx configuration file.")
        sys.exit(0)

    # Try to restart nginx service
    try:
        print("Reloading nginx service, you may be prompted to enter your sudo password...")
        result = os.system("sudo nginx -s reload")
        if result != 0:
            raise Exception("Failed to reload nginx service. Please check if 'nginx' is available and try again.")
        print("Nginx service reloaded successfully.")
    except Exception as e:
        print("Please reload the nginx service manually and re-run the script to verify the installation.")
        sys.exit(0)
    
    # Verify that the site is accessible and Prerender integration is installed
    try:
        integration_successful = check_integration(site_url)
        if integration_successful:
            print(f"Prerender integration successfully verified for {site_url}")
        else:
            raise Exception("Prerender integration verification failed.")
    except Exception as e:
        print(f"Error verifying Prerender integration: {e}")
        
    print("Installation completed successfully.")
    
    site_url_data.cleanup()
    token_data.cleanup()

if __name__ == "__main__":
    main()