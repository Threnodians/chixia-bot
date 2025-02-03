import httpx
import constants
from typing import List
from loguru import logger

class ApiHandler:
    def __init__(self):
        self.all_chars_route = "/api/characters"

    def get_all_characters(self) -> List[str]:
        endpoint = constants.ENDPOINT_BASE + self.all_chars_route
        logger.debug(f"requesting endpoint: {endpoint}")
        request = httpx.get(endpoint)
        if request.status_code != 200:
            logger.error("api response returned non-ok status")
            return None
        else:
            logger.debug("api request successful")
        return [str(i) for i in request.json()]
    
    def get_character_info(self, character_slug: str) -> any:
        endpoint = constants.ENDPOINT_BASE + self.all_chars_route + "/" + character_slug
        logger.debug(f"requesting endpoint: {endpoint}")
        request = httpx.get(endpoint)
        if request.status_code != 200:
            logger.error("api response returned non-ok status")
            return None
        else:
            logger.debug("api request successful")
        return request.json()