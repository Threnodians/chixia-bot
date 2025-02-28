# Project Structure and Description

This project is a Discord bot built using the `interactions.py` library. It interacts with an external API to fetch information about characters (referred to as "Resonators") in Wuthering Waves.

## How to Run

1. **Install Dependencies:**  Make sure you have Python installed (preferably Python 3.8 or higher). Then, install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

2. **Configuration:**
    - Copy `constants.py.example` to `constants.py`:

        ```bash
        cp constants.py.example constants.py
        ```

    - Open `constants.py` and fill in your *actual* Discord bot token and API base URL.

        ```python
        # constants.py
        BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your bot's token
        ENDPOINT_BASE = "YOUR_API_BASE_URL"  # Example: "https://api.example.com"
        ```

        **Important:**  `BOT_TOKEN` is your bot's secret key.  Keep it confidential and *never* commit it to a public repository.  `ENDPOINT_BASE` is the base URL of the API you're using.

3. **Run the Bot:** Once you have `constants.py` set up, you can run the bot from the command line:

    ```bash
    python app.py
    ```

## Functionality

The bot provides the following commands:

- **`/ping`**:  A simple command to check if the bot is alive and responsive.  It returns an embed message showing the bot's latency and a basic health status.

- **`/resonator`**:  The main command for retrieving information about Resonators.  It has two modes of operation:
  - **`/resonator` (without a name):**  Displays a list of all available Resonators fetched from the API.
  - **`/resonator name: [name]`:**  Fetches and displays detailed build information for the specified Resonator. This includes:
    - Portrait image (with a fallback if the API doesn't provide one or if loading fails)
    - Skill Priority
    - Substat Priority
    - Endgame Stats
    - Recommended Weapons
    - Recommended Echo Sets
  - **Autocomplete:**  The `name` option for the `/resonator` command supports autocomplete.  As you type, the bot will suggest Resonator names based on the data it has fetched from the API.

## API Interaction

- **API Handling:** The bot uses the `ApiHandler` class (in `core/api_handler.py`) to interact with the external API.  This class handles:
  - Constructing API endpoints using the `ENDPOINT_BASE` from `constants.py`.
  - Making HTTP requests using the `httpx` library.
  - Handling potential errors (network errors, HTTP errors, unexpected errors) and logging them using `loguru`.
  - Returning `None` if an API call fails.

- **API Endpoints used by the bot**
  - `/api/characters`: Retrieves a list of all characters from the database
  - `/api/characters/{characterName}`: Retrieves the detailed build information of the requested character.

- **Retry Logic:** The `/resonator` command includes a retry mechanism (up to 5 retries with a 2-second delay) to handle transient network issues or temporary API unavailability.  It also specifically handles the `SCRAPE_ERROR` response from the API, indicating that data for the requested Resonator could not be found.

- **Error Handling:** The bot handles various errors, including:
  - Network errors during API requests.
  - HTTP errors from the API (e.g., 404, 500).
  - Image loading errors.
  - Missing data in API responses.
  - Errors during command execution.

    Errors are logged using `loguru` for debugging and monitoring.

## Project Structure

The project is organized into the following files and directories:

- **`app.py`:** The main entry point of the bot.  Initializes the `interactions.Client`, sets up event listeners, and loads extensions.
- **`commands/`:** Contains the bot's command extensions.
  - **`character.py`:**  Handles the `/resonator` command and its autocomplete functionality.
  - **`general.py`**: Contains general-purpose commands such as `/ping`
- **`core/`:** Contains core functionality.
  - **`api_handler.py`:**  Handles all interactions with the external API.
- **`constants.py`:**  Stores configuration values (bot token, API base URL). *You need to create this file.*
- **`requirements.txt`:**  Lists the Python packages required for the project.
- **`api-info.txt`:**  Provides examples of API requests and responses (useful for understanding the API).

## Logging

The bot uses the `loguru` library for logging.  Logs are written to the `bot.log` file (in the directory where you run the bot), which rotates every 500MB.  The logs include:

- Bot startup and shutdown messages.
- Successful API requests.
- API request errors (including details about the error).
- Command errors.
- Autocomplete activity.
- Image loading errors.
