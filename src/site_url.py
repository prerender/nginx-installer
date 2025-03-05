import requests
import logging

logger = logging.getLogger(__name__)

def check_access(url):
    try:
        response = requests.get(url)
        logger.debug(f"The URL {url} responded with status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(e)
        return False

    return True

def check_integration(url):
    headers = {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}
    try:
        response = requests.get(url, headers=headers)
        logger.debug(f"The URL {url} responded with status code {response.status_code}.")
        if 'x-prerender' in response.headers:
            logger.debug(f"The URL {url} contains the 'x-prerender' header.")
            return True
        else:
            logger.debug(f"The URL {url} does not contain the 'x-prerender' header.")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return False
