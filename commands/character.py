from interactions import (
    Extension,
    slash_command,
    SlashContext,
    Embed,
    # EmbedField,
    OptionType,
    slash_option,
    AutocompleteContext,
    EmbedAttachment,
    listen,
    events
)
from core.api_handler import ApiHandler
from loguru import logger
# from constants import ENDPOINT_BASE
import httpx
import asyncio

class Character(Extension):
    def __init__(self, bot):
        logger.info("Initializing Character extension")
        self.api = ApiHandler()
        self.character_cache = []  # Use a list to store character names for autocomplete.
        super().__init__()
        self.bot = bot

    @listen(events.ExtensionLoad)
    async def on_extension_load(self):
        # Prefetch the character list on extension load to improve initial command response time.
        logger.info("Character extension loaded - pre-fetching character list.")
        await self._get_characters()

    async def _get_characters(self):
        """Retrieves the list of all character names, caching the result to minimize API calls."""
        if not self.character_cache:
            # If cache is empty, fetch from API and populate.
            self.character_cache = self.api.get_all_characters() or [] # Fallback to empty list on API failure
        return self.character_cache

    def _clean_name(self, name: str) -> str:
        """Converts API-formatted character names (e.g., 'the-shorekeeper') to title case ('The Shorekeeper')."""
        return name.replace("-", " ").title()

    @slash_command(name="resonator", description="Get info about resonators from Wuthering Waves")
    @slash_option(
        name="name",
        description="Name of the Resonator",
        required=False,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    async def handle_resonator(self, ctx: SlashContext, name: str = None) -> None:
        """Handles the /resonator command.  If no name is provided, lists all resonators.
        If a name is provided, fetches and displays detailed information about that resonator.
        """

        if name is None:
            # No name provided: display a list of all available resonators.
            logger.info("Main resonator command without name invoked - showing list")
            characters = await self._get_characters()
            if not characters:
                await ctx.respond("Failed to fetch character data. Please try again later.", ephemeral=True)
                return

            embed = Embed(
                title="Available Resonators",
                description="Here are all available Resonators in the database:",
                color="#8B008B"
            )
            cleaned_names = [self._clean_name(char) for char in characters]
            embed.add_field(name="Characters", value=", ".join(cleaned_names))
            embed.set_footer(text="Use /resonator [name] to see detailed information about a specific Resonator.")
            await ctx.respond(embed=embed)

        else:
            # Name provided: fetch and display detailed character information.
            logger.info(f"Resonator command invoked for name: {name}")
            await ctx.defer()  # Defer to avoid "interaction token is invalid" errors for longer operations

            name_slug = name.lower()

            # Implement retry logic to handle transient network or API errors.
            retries = 5
            delay = 2

            for attempt in range(retries):
                character_info = self.api.get_character_info(name_slug)
                if character_info and "errorCode" not in character_info:
                    # Successful API call, proceed to display data.
                    break
                elif character_info and character_info.get("errorCode") == "SCRAPE_ERROR":
                    # API reports it couldn't scrape data for this character; no point in retrying.
                    await ctx.respond(f"Failed to retrieve data for {name}: The API could not find information for this resonator.", ephemeral=True)
                    return
                else:
                    # Log the failure and wait before retrying.
                    logger.info(f"Attempt {attempt + 1}/{retries} failed.  Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
            else:
                # All retries failed; inform the user.
                await ctx.respond(f"Failed to retrieve data for {name} after multiple attempts.  The API may be busy or the character data may not be available yet.", ephemeral=True)
                return

            cleaned_name = self._clean_name(name_slug)
            embed = Embed(
                title=f"{cleaned_name} - Resonator Build Information",
                color="#8B008B"
            )

            # Handle portrait image loading, including potential failures.
            portrait_url = None
            if "portraitUrl" in character_info and character_info["portraitUrl"]:
                portrait_url = f"https://www.prydwen.gg{character_info['portraitUrl']}"
                logger.debug(f"Attempting to fetch image from: {portrait_url}")
                try:
                    # Use an async HTTP client to fetch the image.
                    async with httpx.AsyncClient() as client:
                        response = await client.get(portrait_url)
                        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    embed.thumbnail = EmbedAttachment(url=portrait_url)

                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    # Log the specific error and fall back to a default image.
                    logger.warning(f"Image request failed: {e}")
                    portrait_url = None  # Ensure portrait_url is None if there was an error
                except Exception as e:
                    logger.exception(f"Unexpected error while fetching/setting image: {e}")
                    portrait_url = None

            if portrait_url is None:
                logger.info("Using fallback image.")
                embed.thumbnail = EmbedAttachment(url="https://wutheringlab.com/wp-content/uploads/2023/06/Wuthering-Waves-Chixia.png")

            # Add character information fields to the embed.  The 'if' checks prevent errors if
            # a particular piece of data is missing from the API response.
            if "skillPriority" in character_info and character_info["skillPriority"]:
                embed.add_field(name="⚔️ Skill Priority", value=" > ".join(character_info["skillPriority"]), inline=False)
            elif "skillPriority" in character_info:
                embed.add_field(name="⚔️ Skill Priority", value="No skill priority information available.", inline=False)
            if "substatPriority" in character_info and character_info["substatPriority"]:
                embed.add_field(name="📊 Substat Priority", value=character_info["substatPriority"], inline=False)
            elif "substatPriority" in character_info:
                embed.add_field(name="📊 Substat Priority", value="No substat priority information available.", inline=False)
            if "endgameStats" in character_info and character_info["endgameStats"]:
                stats = character_info["endgameStats"]
                if stats:  # Check if stats dictionary is not empty
                    # Create stats text but check for Discord's 1024 character limit
                    stats_items = [f"**{stat}:** {value}" for stat, value in stats.items()]

                    # Check if the combined text would exceed Discord's limit
                    stats_text = "\n".join(stats_items)
                    if len(stats_text) <= 1024:  # Discord's field value limit
                        embed.add_field(name="🎯 Endgame Stats", value=stats_text, inline=False)
                    else:
                        # Split into multiple fields if too long
                        current_text = ""
                        field_count = 1

                        for item in stats_items:
                            # Check if adding this item would exceed the limit
                            if len(current_text + "\n" + item) > 1024 and current_text:
                                # Add the current field and start a new one
                                embed.add_field(name=f"🎯 Endgame Stats ({field_count})", value=current_text, inline=False)
                                current_text = item
                                field_count += 1
                            else:
                                # Add to current field with a newline if not empty
                                if current_text:
                                    current_text += "\n" + item
                                else:
                                    current_text = item

                        # Add the last field if there's anything left
                        if current_text:
                            embed.add_field(name=f"🎯 Endgame Stats ({field_count})", value=current_text, inline=False)
                else:
                    embed.add_field(name="🎯 Endgame Stats", value="No endgame stats available.", inline=False)
            elif "endgameStats" in character_info:
                embed.add_field(name="🎯 Endgame Stats", value="No endgame stats available.", inline=False)
            if "weaponBuilds" in character_info and character_info["weaponBuilds"]:
                # Limit the number of displayed weapons to avoid overly long embeds.
                weapon_items = [
                    f"**{weapon['name']}** (S{weapon['duplicates']}) - {weapon['percentage']}"
                    for weapon in character_info["weaponBuilds"][:5]
                ]
                weapon_text = "\n".join(weapon_items)

                # Check if the text exceeds Discord's limit
                if len(weapon_text) <= 1024:
                    embed.add_field(name="🗡️ Recommended Weapons", value=weapon_text, inline=False)
                else:
                    # Split into multiple fields if too long
                    current_text = ""
                    field_count = 1

                    for item in weapon_items:
                        if len(current_text + "\n" + item) > 1024 and current_text:
                            embed.add_field(name=f"🗡️ Recommended Weapons ({field_count})", value=current_text, inline=False)
                            current_text = item
                            field_count += 1
                        else:
                            if current_text:
                                current_text += "\n" + item
                            else:
                                current_text = item

                    # Add the last field
                    if current_text:
                        embed.add_field(name=f"🗡️ Recommended Weapons ({field_count})", value=current_text, inline=False)
            elif "weaponBuilds" in character_info:
                # Handle case where weaponBuilds exists but is empty
                embed.add_field(name="🗡️ Recommended Weapons", value="No recommended weapons available.", inline=False)
            if "echoSetBuilds" in character_info and character_info["echoSetBuilds"]:
                echo_items = [
                    f"**{echo['setName']}** ({echo['echoName']}) - {echo['percentage']}"
                    for echo in character_info["echoSetBuilds"]
                ]
                echo_text = "\n".join(echo_items)

                # Check if the text exceeds Discord's limit
                if len(echo_text) <= 1024:
                    embed.add_field(name="🔮 Recommended Echo Sets", value=echo_text, inline=False)
                else:
                    # Split into multiple fields if too long
                    current_text = ""
                    field_count = 1

                    for item in echo_items:
                        if len(current_text + "\n" + item) > 1024 and current_text:
                            embed.add_field(name=f"🔮 Recommended Echo Sets ({field_count})", value=current_text, inline=False)
                            current_text = item
                            field_count += 1
                        else:
                            if current_text:
                                current_text += "\n" + item
                            else:
                                current_text = item

                    # Add the last field
                    if current_text:
                        embed.add_field(name=f"🔮 Recommended Echo Sets ({field_count})", value=current_text, inline=False)
            elif "echoSetBuilds" in character_info:
                # Handle case where echoSetBuilds exists but is empty
                embed.add_field(name="🔮 Recommended Echo Sets", value="No recommended echo sets available.", inline=False)

            embed.set_footer(text="Data from Gathering Wives API | Wuthering Waves")
            await ctx.respond(embed=embed)

    @handle_resonator.autocomplete("name")
    async def resonator_autocomplete(self, ctx: AutocompleteContext):
        """Provides autocomplete suggestions for resonator names.  Filters based on user input."""
        logger.debug(f"Autocomplete triggered with input: {ctx.input_text}")
        characters = await self._get_characters()
        if not characters:
            logger.warning("No characters available for autocomplete.")
            return []

        query = ctx.input_text.lower() if ctx.input_text else ""
        # Suggest characters that match the input, either in the slug or the cleaned name.
        suggestions = [
            {"name": self._clean_name(char), "value": char}
            for char in characters
            if query in char.lower() or query in self._clean_name(char).lower()
        ]
        logger.debug(f"Returning {len(suggestions)} autocomplete suggestions.")
        # Limit suggestions to 25 (Discord's limit).
        await ctx.send(suggestions[:25])