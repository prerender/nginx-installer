import os

def restart_nginx():
    result = os.system("sudo nginx -s reload")
    if result != 0:
        raise Exception("Failed to reload nginx service.")