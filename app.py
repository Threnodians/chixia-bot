import interactions
import constants
from loguru import logger

bot = interactions.Client()
bot.load_extension("commands.general")
bot.load_extension("commands.character")

@interactions.listen()
async def on_startup():
    logger.info("bot is ready...")

bot.start(constants.BOT_TOKEN)