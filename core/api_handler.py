import httpx
from loguru import logger
from constants import ENDPOINT_BASE

class ApiHandler:
    def __init__(self):
        self.base_url = ENDPOINT_BASE

    def get_all_characters(self):
        """Fetches a list of all character names from the API.  Returns None on failure."""
        try:
            logger.debug(f"requesting endpoint: {self.base_url}/api/characters")
            response = httpx.get(f"{self.base_url}/api/characters")
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            logger.debug("API request successful")
            return response.json()
        except httpx.RequestError as e:
            # Handle network-related errors (e.g., connection refused, timeout).
            logger.error(f"Request failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 404 Not Found, 500 Internal Server Error).
            logger.error(f"Request returned error status {e.response.status_code}: {e}")
            return None
        except Exception as e:
            # Handle unexpected errors during the API call.  Log the full exception for debugging.
            logger.exception(f"An unexpected error occurred: {e}")
            return None

    def get_character_info(self, character_name: str):
        """Fetches detailed information for a specific character.  Returns None on failure."""
        try:
            logger.debug(f"requesting endpoint: {self.base_url}/api/characters/{character_name}")
            response = httpx.get(f"{self.base_url}/api/characters/{character_name}")
            response.raise_for_status()
            logger.debug("API request successful")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Request returned error status {e.response.status_code}: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return None