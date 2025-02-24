import crossplane

def load_nginx_config(file_path):
    payload = crossplane.parse(file_path,comments=True,single=True, strict=False)

    try:
        config = payload['config'][0]['parsed']
    except KeyError:
        raise Exception("Can't get parsed config from payload")

    return config

def save_nginx_config(config, file_path):
    config_str = crossplane.build(config)

    if not config_str:
        raise Exception("Failed to build configuration with crossplane")

    with open(file_path, 'w') as f:
        f.write(config_str)
    