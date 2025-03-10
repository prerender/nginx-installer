import os
import logging

logger = logging.getLogger(__name__)

def restart_nginx():
    logger.info("Reloading nginx service, you may be prompted to enter your sudo password...")
    result = os.system("sudo systemctl restart nginx")
    if result != 0:
        raise Exception("Failed to reload nginx service.")