import os
import sys
import argparse
from conf_backup import make_backup, restore_backup, validate_backup
from crossplane_adapter import load_nginx_config, save_nginx_config
from nginx import restart_nginx
from prerender import add_map_section, add_location_prerenderio, rewrite_root_location, get_all_server_blocks_with_names
from site_url import check_access, check_integration
import logging
from temp_file_utils import temp_file_factory

logger = logging.getLogger(__name__)
site_url_data = temp_file_factory("./.prerender_site_url")
token_data = temp_file_factory("./.prerender_token")
nginx_conf_data = temp_file_factory("./.prerender_nginx_conf")

DEFAULT_NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'

VERSION = '0.0.1'

def parse_args():
    parser = argparse.ArgumentParser(description="Portable nginx configuration CLI tool")
    parser.add_argument('-f', '--file', help='Path to the nginx configuration file', default=None)
    parser.add_argument('-o', '--output', help='Path to save the modified nginx configuration file', default=None)
    parser.add_argument('-m', '--modify', help='Modify the nginx configuration', default=False)
    parser.add_argument('-t', '--token', help='Prerender token', default=None)
    parser.add_argument('-u', '--url', help='URL of the site to integrate with Prerender.io', default=None)
    parser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
    return parser.parse_args()

def setup_logging(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    
    # Clear existing handlers
    logging.getLogger().handlers = []
    
    # Create a console handler with a specific log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Create a file handler with a different log level
    file_handler = logging.FileHandler('prerender.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Add both handlers to the root logger
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)
    
def prompt_yes_no(prompt):
    logger.info(prompt)
    while True:
        response = input().lower()
        logger.debug(f"User input for {prompt}: {response}")
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            logger.info("Please enter 'y' or 'n'")

def main():
    args = parse_args()
    setup_logging(args.verbose)
    
    logger.debug(f"Version: {VERSION}")
    logger.debug(f"Arguments: {args}")
        
    config_path = None
    config = None
    output_path = None
    site_url = None
    site_available = False
    
    saved_nginx_config_path = nginx_conf_data.get_data()
    
    # determine the nginx configuration file
    
    if args.file:
        config_path = args.file
    elif saved_nginx_config_path and os.path.exists(saved_nginx_config_path):
        if prompt_yes_no(f"Saved nginx configuration found at {nginx_conf_data.get_data()}. Do you want to use it? (y/n):"):
            config_path = nginx_conf_data.get_data()
    elif os.path.exists(DEFAULT_NGINX_CONFIG_PATH):
        if prompt_yes_no(f"Default nginx configuration found at {DEFAULT_NGINX_CONFIG_PATH}. Do you want to use it? (y/n):"):
            config_path = DEFAULT_NGINX_CONFIG_PATH

    while not config_path:
        config_path = input("Please enter the path to the nginx configuration file or type 'exit' to quit: ")
        if config_path.lower() == 'exit':
            sys.exit(0)
        if not os.path.exists(config_path):
            logger.info(f"The file at {config_path} does not exist. Please try again.")
            config_path = None
            
    nginx_conf_data.save_data(config_path)

    backup_path = f"{config_path}.prerender.backup"
    
    if validate_backup(backup_path):
        logger.info(f"Backup of the nginx configuration file found at {backup_path}")
        if prompt_yes_no("Do you want to restore the original nginx configuration? (y/n): "):
            try:
                restore_backup(backup_path, config_path)
                logger.info(f"Restored the original nginx configuration file from {backup_path}")
                
                try:        
                    restart_nginx()
                except Exception as e:
                    logger.info("Please reload the nginx service manually to complete restore from backup.")                    
                    sys.exit(1)
            except Exception as e:
                logger.info(f"Error restoring the original nginx configuration file: {e}")
                sys.exit(1)
                
            print("Original nginx configuration restored successfully.")
            sys.exit(0)
                
    else:    
        try:
            backup_path = make_backup(config_path, backup_path)
            nginx_conf_data.save_data(config_path)
            logger.info(f"Backup of the nginx configuration file created at {backup_path}")
        except Exception as e:
            logger.info(f"Error creating backup of nginx configuration: {e}")
            logger.info(f"Make sure you have the necessary permissions to modify files at config location.")
            sys.exit(1)
        
    nginx_conf_data.save_data(config_path)
        
    if args.url:
        site_url = args.url
    else:
        site_url = site_url_data.get_data()
        
        if site_url:
            if not prompt_yes_no(f"Do you want to integrate \"{site_url}\"? (y/n):"):
                site_url = None

    while not site_available:
        if not site_url:
            logger.info("Please enter the URL of the site to integrate with Prerender.io. Example https://www.site.com: ")
            site_url = input()
            
        logger.info(f"Checking if the site at {site_url} is accessible...")
        site_available = check_access(site_url)
        if not site_available:
            site_url = None
        else:
            prerender_verified = check_integration(site_url)
            if prerender_verified:
                logger.info(f"Prerender integration exists for {site_url}")           
                sys.exit(0)                    
            
    site_url_data.save_data(site_url)

    if args.output:
        # create new file, mostly for testing cases
        output_path = args.output
    else:
        output_path = config_path

    # Load and parse the nginx configuration
    try:
        config = load_nginx_config(config_path)
        logger.info("Nginx configuration loaded successfully.") 
    except Exception as e:
        logger.info(f"Error loading nginx configuration: {e}")
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

        logger.info("Following server configurations were found:")
        for i, (server_block) in enumerate(server_blocks_with_names):
            logger.info(f"  {i + 1}. {get_server_name(server_block)}")

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
                    logger.info(f"Invalid input: {e}")
                    selected_server_block = None

        logger.info(f"Selected server configuration: {get_server_name(selected_server_block)}")

        # figure out the Prerender token
        prerender_token = None

        if args.token:
            prerender_token = args.token
        else:
            saved_token = token_data.get_data()
            if saved_token:
                if prompt_yes_no(f"A saved Prerender token \"{saved_token}\" was found. Do you want to use it? (y/n): "):
                    prerender_token = saved_token

        if not prerender_token:
            prerender_token = input("Please enter your Prerender token: ")

        if not prerender_token:
            raise Exception("Prerender token is required to proceed.")
        
        # Save the Prerender token to a file
        try:
            token_data.save_data(prerender_token)
        except Exception as e:
            # non-critical 
            logger.debug(f"Error saving Prerender token to file: {e}")

        shall_modify = args.modify

        if not shall_modify:
            if prompt_yes_no("Do you want to modify the nginx configuration? (y/n): "):
                shall_modify = True
        
        if shall_modify:
            # not going to modify anything if no backup available
            if not validate_backup(backup_path):
                logger.error("Unsafe to proceed : backup file is not found or corrupted. Try to re-run the script and contact support if error persist.")
                sys.exit(1)
            
            add_map_section(config)
            rewrite_root_location(selected_server_block[0])
            add_location_prerenderio(selected_server_block[0], prerender_token)
            save_nginx_config(config, output_path)
            is_modified = True
            logger.info(f"Modified nginx configuration saved to {output_path}")

    except Exception as e:
        logger.info(f"Error : {e}")

        if is_modified:
            logger.info(f"Config at {output_path} was modified and may be in an inconsistent state.")
        
            try:
                restore_backup(backup_path, config_path)
                logger.info(f"Restored the original nginx configuration file from {backup_path}")
            except Exception as e:
                logger.info(f"Error restoring the original nginx configuration file: {e}")

    if not is_modified:
        logger.info("No modifications were made to the nginx configuration file.")
        sys.exit(0)        

    try:        
        restart_nginx()
    except Exception as e:
        logger.info("Please reload the nginx service manually and re-run the script to verify the installation.")
        sys.exit(0)
    
    # Verify that the site is accessible and Prerender integration is installed
    try:
        integration_successful = check_integration(site_url)
        if integration_successful:
            logger.info(f"Prerender integration successfully verified for {site_url}")
        else:
            logger.info(f"Prerender integration not found for {site_url}")
    except Exception as e:
        logger.info(f"Error verifying Prerender integration: {e}")
        
    if not integration_successful:
        logger.info("Verification failed. Possible reasons include:\n"
            "- Incorrect routing configuration.\n"
            "- Firewall rules blocking access.\n"
            "- Invalid Prerender token.\n"
            "- Non-standard nginx configuration.\n"
            "Please check your configuration and try again. If the issue persists, contact support. Attach file prerender.log to your support request.\n"
            "To retry verification, please run the script once again.")
        
    if not integration_successful:
        if prompt_yes_no("Do you want to restore the original nginx configuration? (y/n): "):
            try:
                restore_backup(backup_path, config_path)
                logger.info(f"Restored the original nginx configuration file from {backup_path}")
                
                try:        
                    restart_nginx()
                except Exception as e:
                    logger.info("Please reload the nginx service manually and re-run the script to verify the installation.")
                    sys.exit(0)
            except Exception as e:
                logger.info(f"Error restoring the original nginx configuration file: {e}")   
                sys.exit(1)     

if __name__ == "__main__":
    main()