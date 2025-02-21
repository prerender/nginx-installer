def load_nginx_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config_content = file.read()
        return config_content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def parse_nginx_config(config_content):
    if config_content is None:
        return None
    
    # This is a placeholder for actual parsing logic.
    # You would typically use a library like Crossplane here to parse the config.
    parsed_config = {}
    
    # Example parsing logic (to be replaced with actual implementation)
    lines = config_content.splitlines()
    for line in lines:
        if line and not line.startswith('#'):  # Ignore comments and empty lines
            key_value = line.split(None, 1)  # Split on the first whitespace
            if len(key_value) == 2:
                key, value = key_value
                parsed_config[key] = value.strip()
    
    return parsed_config