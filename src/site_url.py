import requests
import logging

logger = logging.getLogger(__name__)

def check_access(url):
    try:
        response = requests.get(url)
        logger.debug(f"The URL {url} responded with status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        logger.debug(e)
        return False

    return True

def check_integration(url):
    headers = {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}
    try:
        response = requests.get(url, headers=headers)
        logger.debug(f"The URL {url} responded with status code {response.status_code}.")
        
        result = True
        
        if response.status_code != 200:
            logger.debug(f"The URL {url} did not respond with status code 200")
            result = False
        
        if 'x-prerender' in response.headers:
            logger.debug(f"The URL {url} contains the 'x-prerender' header.")            
        else:
            logger.debug(f"The URL {url} does not contain the 'x-prerender' header.")
            result = False
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(e)
        return False
