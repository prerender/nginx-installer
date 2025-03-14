
import os

def make_backup(config_path: str, backup_path: str):
    with open(config_path, 'r') as original_file:
            with open(backup_path, 'w') as backup_file:
                backup_file.write(original_file.read())

def validate_backup(backup_path: str) -> bool:
    if not os.path.exists(backup_path) or os.path.getsize(backup_path) == 0:
            return False
    return True
        
def restore_backup(backup_path: str, config_path: str):
    with open(backup_path, 'r') as backup_file:
        with open(config_path, 'w') as config_file:
            config_file.write(backup_file.read())