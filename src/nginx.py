import os

def restart_nginx():
    result = os.system("sudo systemctl restart nginx")
    if result != 0:
        raise Exception("Failed to reload nginx service.")