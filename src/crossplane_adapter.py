import crossplane
import logging

logger = logging.getLogger(__name__)

def load_nginx_config(file_path):
    payload = crossplane.parse(file_path,comments=True, single=False, strict=False)

    if not payload:
        raise Exception("Failed to parse configuration.")
    
    if len(payload['config'][0]['errors']):        
        logger.error(payload['config'][0]['errors'])
        raise Exception("Failed to parse configuration.")

    return payload

def save_nginx_config(config, file_path):
    config_str = crossplane.build(config)

    if not config_str:
        raise Exception("Failed to build configuration with crossplane")

    try:
        with open(file_path, 'w') as f:
            f.write(config_str)
    except IOError as e:
        raise Exception(f"Failed to save configuration to {file_path}: {e}")
    