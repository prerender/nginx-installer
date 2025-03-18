import os
import sys
import argparse
import traceback
from conf_backup import create_all_backups, get_backup_path, restore_all_backups, validate_backup
from crossplane_adapter import load_nginx_config, save_nginx_config
from nginx import restart_nginx
from prerender import add_map_section, add_location_prerenderio, rewrite_root_location, get_all_server_blocks_with_attrs
from site_url import check_access, check_integration
import logging
from temp_file_utils import temp_file_factory

logger = logging.getLogger(__name__)
site_url_data = temp_file_factory("./.prerender_site_url")
token_data = temp_file_factory("./.prerender_token")
nginx_conf_data = temp_file_factory("./.prerender_nginx_conf")
server_conf_data = temp_file_factory("./.prerender_server_conf")

DEFAULT_NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'

MSG_VERIFICATION_FAILED_WITH_REASONS = "Verification failed. Possible reasons :\n" \
"- Firewall rules blocking access.\n" \
"- Wrong server block picked.\n" \
"- Invalid Prerender token.\n" \
"Please check your configuration and try again. If the issue persists, contact support. Attach file prerender.log to your support request.\n" \
"To retry verification or restore backup, please run the script once again."

VERSION = '0.0.4'

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
            
def setup():
    args = parse_args()
    setup_logging(args.verbose)
    
    return args

def main(args):    
    logger.debug(f"Version: {VERSION}")
    logger.debug(f"Arguments: {args}")
    logger.debug(f"Operating System: {os.name}")
    logger.debug(f"Platform: {sys.platform}")
    logger.debug(f"Version: {os.uname()}")
        
    main_config_path = None
    server_config_path = None
    parsed_configs = None
    output_path = None
    site_url = None
    site_available = False
    prerender_token = None
    
    # verify integration flow
    
    saved_site_url = site_url_data.get_data()
    
    if not args.modify and site_url_data.get_data():
        if prompt_yes_no(f"Do you want to verify integration of {saved_site_url}? (y/n):"):            
            try:
                prerender_verified = check_integration(saved_site_url)
                if prerender_verified:
                    logger.info(f"Prerender integration successfully verified for {saved_site_url}")
            except Exception as e:
                logger.info(f"Error verifying Prerender integration: {e}")
            
            if not prerender_verified:
                logger.info(MSG_VERIFICATION_FAILED_WITH_REASONS)
            
            sys.exit(0)
    
    # todo move backup flow to separate function / module
    
    saved_nginx_config_path = nginx_conf_data.get_data()
    saved_server_conf_path = server_conf_data.get_data() 
    
    saved_nginx_backup_ready = False
    saved_server_backup_ready = False
    
    saved_nginx_backup_path = get_backup_path(saved_nginx_config_path)
    if validate_backup(saved_nginx_backup_path):
        logger.info(f"Backup of the saved nginx configuration file found at {saved_nginx_backup_path}")
        saved_nginx_backup_ready = True
        
    saved_server_backup_path = get_backup_path(saved_server_conf_path)
    if validate_backup(saved_server_backup_path):
        logger.info(f"Backup of the saved server configuration file found at {saved_server_backup_path}")
        saved_server_backup_ready = True        
    
    if not args.modify and (saved_nginx_backup_ready or saved_server_backup_ready):
        if prompt_yes_no(f"Do you want to restore the original nginx configuration from backup? (y/n): "):    
            restore_all_backups(main_config_path, server_config_path)
                        
            try:        
                restart_nginx()
            except Exception as e:
                logger.info("Please reload the nginx service manually to complete restore from backup.")                    
                sys.exit(1)
                
            print("Original nginx configuration restored successfully.")
            sys.exit(0)     
    
    # decide which nginx configuration file to use
    
    if args.file:
        main_config_path = args.file
    elif saved_nginx_config_path and os.path.exists(saved_nginx_config_path):
        if prompt_yes_no(f"Continue with {saved_nginx_config_path} (y) or try another file? (y/n):"):
            main_config_path = nginx_conf_data.get_data()
    elif os.path.exists(DEFAULT_NGINX_CONFIG_PATH):
        if prompt_yes_no(f"Default nginx configuration found at {DEFAULT_NGINX_CONFIG_PATH}. Do you want to use it? (y/n):"):
            main_config_path = DEFAULT_NGINX_CONFIG_PATH

    while not main_config_path:
        main_config_path = input("Please enter the path to the nginx configuration file or type 'exit' to quit: ")
        if main_config_path.lower() == 'exit':
            sys.exit(0)
        if not os.path.exists(main_config_path):
            logger.info(f"The file at {main_config_path} does not exist. Please specify correct path to nginx.conf file.")
            main_config_path = None          
            
    # Load and parse the nginx configuration
    try:
        parsed_configs = load_nginx_config(main_config_path)
        logger.info("Nginx configuration loaded successfully.") 
    except Exception as e:
        logger.info(f"Error loading nginx configuration: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)
        
    logger.debug(f"Parsed configs: {parsed_configs}")                        
    
    # decide on site URL
        
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
            
    site_url_data.save_data(site_url)

    if args.output:
        # todo – remove this option to avaoid extra flow branching
        # create new file, mostly for testing cases
        output_path = args.output
    else:
        output_path = main_config_path
        
    # figure out the Prerender token
    
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
    
    try:
        token_data.save_data(prerender_token)
    except Exception as e:
        # non-critical 
        logger.debug(f"Error saving Prerender token to file: {e}")    

    is_modified = False
        
    # Get all server blocks with their server names
    selected_server_block = None
    main_config = parsed_configs['config'][0]['parsed']
    
    server_blocks = []
    
    def get_server_name(server_block):
        (server_block, server_name, server_listening) = server_block
        
        server_name = server_name if server_name else "(no server_name)"
        
        return f"{server_name} {server_listening}"
    
    for i, (config) in enumerate(parsed_configs['config']):
        logger.debug(f"Config {i}: {config}")
        
        if not config['status'] == 'ok':
            logger.warning(f"Skipping config {i} due to parsing error")
            continue                

        for server_block in get_all_server_blocks_with_attrs(config['parsed']):
            server_blocks.append({
                "block": server_block,
                "config": config,
                "name": get_server_name(server_block)
            })

    logger.info("Following server configurations were found:")
    for i, (server_block) in enumerate(server_blocks):
        logger.info(f"  {i + 1}. {server_block['name']}")

    if len(server_blocks) == 0:
        raise Exception("No server blocks found in the nginx configuration")
    
    if len(server_blocks) == 1:
        selected_server_block = server_blocks[0]        
    else:
        while not selected_server_block:
            try:
                selected_server_block_index = int(input("Which server do you want to integrate? (1,2,3...): "))
                selected_server_block = server_blocks[selected_server_block_index - 1]
            except Exception as e:
                logger.info(f"Invalid input: {e}")
                selected_server_block = None    
        
    server_config_path = selected_server_block['config']['file']
    
    logger.info(f"Selected server configuration: {selected_server_block['name']} from {server_config_path}")
    
    #make changes to the configuration
    
    add_map_section(main_config)
    rewrite_root_location(selected_server_block['block'][0])
    add_location_prerenderio(selected_server_block['block'][0], prerender_token)
                
    if not args.modify and not prompt_yes_no("We're ready to modify the nginx configuration. Continue? (y/n): "):
        logger.info("Modifications were not saved.")
        sys.exit(0)
        
    # make backups, store state
    
    nginx_conf_data.save_data(main_config_path)
    server_conf_data.save_data(server_config_path)
    create_all_backups(main_config_path, server_config_path)
    
    # save the modified configuration
        
    try:
        save_nginx_config(main_config, output_path)
        if server_config_path != main_config_path:
            save_nginx_config(selected_server_block['config']['parsed'], server_config_path)            
    except Exception as e:
        logger.error(f"Error saving configuration : {e}")
        logger.debug(traceback.format_exc())
        
        logger.info(f"Restoring the original nginx configuration from backup") 
        restore_all_backups(main_config_path, server_config_path)
            
        sys.exit(1)

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
        logger.info(MSG_VERIFICATION_FAILED_WITH_REASONS)
        
if __name__ == "__main__":
    args = setup()
    
    try :
        main(args)
    except Exception as e:
        logger.error(f"Error : {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)