import crossplane

def load_nginx_config(file_path):
    try:
        payload = crossplane.parse(file_path,comments=True)
        return payload
    except Exception as e:
        raise Exception(f"Failed to parse configuration with crossplane: {e}")

def save_nginx_onfig(payload, file_path):
    try:
        config = crossplane.build(payload['config'][0]['parsed'])

        print(config)

        with open(file_path, 'w') as f:
            f.write(config)
    except Exception as e:
        raise e;
        # raise Exception(f"Failed to save configuration with crossplane: {e}")
    