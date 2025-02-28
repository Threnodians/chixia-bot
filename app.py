from interactions import Client, Intents, listen
from loguru import logger
import constants

# Configure logger for detailed output, rotating log files for manageability.
logger.add("bot.log", rotation="500 MB", level="DEBUG")

bot = Client(
    token=constants.BOT_TOKEN,
    intents=Intents.DEFAULT  # Use default intents; adjust if specific ones are needed.
)

@listen()
async def on_startup():
    # Log bot startup and readiness.
    logger.info("Bot is starting up...")
    logger.info(f"Registered commands: {bot.application_commands}")  # Verify registered commands.
    logger.info("Bot is ready!")

@listen()
async def on_command_error(event):
    # Centralized error handling for all commands; log the error for debugging.
    logger.error(f"Command error: {event.error}")

# Load extensions, handling potential load failures gracefully.
for ext in ["commands.character", "commands.general"]:
    try:
        bot.load_extension(ext)
        logger.info(f"Loaded extension: {ext}")
    except Exception as e:
        logger.error(f"Failed to load extension {ext}: {e}")

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.start()  # Start the bot.