import os
import logging

logger = logging.getLogger(__name__)

def get_backup_path(config_path):
        return f"{config_path}.prerender.backup"

def make_backup(config_path: str, backup_path: str):
    with open(config_path, 'r') as original_file:
            with open(backup_path, 'w') as backup_file:
                backup_file.write(original_file.read())

def validate_backup(backup_path: str) -> bool:
    if not backup_path or not os.path.exists(backup_path) or os.path.getsize(backup_path) == 0:
            return False
    return True
        
def restore_backup(backup_path: str, config_path: str):
    with open(backup_path, 'r') as backup_file:
        with open(config_path, 'w') as config_file:
            config_file.write(backup_file.read())
            
def create_all_backups(main_config_path: str, server_config_path: str):
    main_backup_path = get_backup_path(main_config_path)
    server_backup_path = get_backup_path(server_config_path)
    
    if not validate_backup(main_backup_path):        
        make_backup(main_config_path, main_backup_path)
        logger.info(f"Created backup of {main_config_path} at {main_backup_path}")
    else:
        logger.debug(f"Backup of {main_config_path} already exists")
    
    if main_config_path != server_config_path:
        if not validate_backup(server_backup_path):
            make_backup(server_config_path, server_backup_path)
            logger.info(f"Created backup of {server_config_path} at {server_backup_path}")
        else:
            logger.debug(f"Backup of {server_config_path} already exists")

def restore_all_backups(main_config_path: str, server_config_path: str):
    main_backup_path = get_backup_path(main_config_path)
    server_backup_path = get_backup_path(server_config_path)

    if validate_backup(main_backup_path):
        restore_backup(main_backup_path, main_config_path)
        logger.info(f"Restored backup of {main_config_path}")
        
    if main_config_path != server_config_path and validate_backup(server_backup_path):
        restore_backup(server_backup_path, server_config_path)
        logger.info(f"Restored backup of {server_config_path}")
