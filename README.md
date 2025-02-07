# Project Structure and Description

This project is a Discord bot built using the `interactions.py` library. It interacts with an external API to fetch information about characters (referred to as "Resonators") in Wuthering Waves

## How to Run

1. **Install Dependencies:**  Make sure you have Python installed. Then, install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

2. **Configuration (Missing `constants.py`):** You'll need a `constants.py` file (which is *not* provided in the code) to store sensitive information and configuration variables. This file should define at least the following:

    ```python
    # constants.py
    BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your bot's token
    ENDPOINT_BASE = "YOUR_API_BASE_URL" # Example: "https://api.example.com"
    ```

    Replace `"YOUR_DISCORD_BOT_TOKEN"` with your actual Discord bot token, and `"YOUR_API_BASE_URL"` with the base URL of the API you want to use.

3. **Run the Bot:** Once you have `constants.py` set up, you can run the bot from the command line:

    ```bash
    python app.py
    ```

## Functionality

- **`/ping`**:  This command provides basic bot status information (latency).

- **`/resonator`**: This is supposed to get the data for the Resonator.
- **`/resonator get`**: This is a subcommand for `/resonator`

- **API Interaction:** The bot is designed to fetch data from an external API.  The `ApiHandler` class handles these requests, including basic error handling.  The API endpoints are constructed using `constants.ENDPOINT_BASE` and relative paths.
