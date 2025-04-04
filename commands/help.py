from interactions import (
    Extension,
    slash_command,
    SlashContext,
    Embed,
    OptionType,
    slash_option,
    listen
)
from loguru import logger

class HelpCommand(Extension):
    def __init__(self, bot):
        logger.info("Initializing Help extension")
        super().__init__()
        self.bot = bot

        # Define command categories and their descriptions
        self.categories = {
            "general": "General utility commands",
            "character": "Commands related to Resonators and character information",
            "help": "Help and information commands"
        }

        # Command category mapping - maps command names to categories
        self.command_categories = {
            "ping": "general",
            "resonator": "character",
            "help": "help"
        }

        # Command examples and notes - additional information not available from command metadata
        self.command_extras = {
            "ping": {
                "example": "/ping",
            },
            "resonator": {
                "example": "/resonator Chixia",
                "notes": "If no name is provided, lists all available Resonators"
            },
            "help": {
                "example": "/help resonator",
                "notes": "Use without parameters to see all commands"
            }
        }

        # This will be populated dynamically
        self.command_info = {}

    @listen("startup_complete")
    async def on_startup_complete(self, _):
        """Discover commands after the bot has fully started up."""
        logger.info("Help extension: discovering commands")
        logger.debug(f"Bot application commands: {self.bot.application_commands}")
        self._discover_commands()

    def _discover_commands(self):
        """Dynamically discovers all registered commands and their information."""
        # Clear existing commands
        self.command_info = {}

        # Get all application commands
        for cmd in self.bot.application_commands:
            # Skip commands that don't have a name (shouldn't happen, but just in case)
            if not hasattr(cmd, "name"):
                continue

            cmd_name = cmd.name
            logger.debug(f"Processing command: {cmd_name}")

            # Determine category based on command name
            category = self.command_categories.get(cmd_name, "general")

            # Get command options for usage string
            options_str = ""
            if hasattr(cmd, "options") and cmd.options:
                options_str = " " + " ".join([f"[{opt.name}]" for opt in cmd.options])

            # Get extras for this command
            extras = self.command_extras.get(cmd_name, {})

            # Create command info
            self.command_info[cmd_name] = {
                "description": cmd.description or "No description available",
                "usage": f"/{cmd_name}{options_str}",
                "example": extras.get("example", f"/{cmd_name}"),
                "category": category
            }

            # Add notes if available
            if "notes" in extras:
                self.command_info[cmd_name]["notes"] = extras["notes"]

            logger.debug(f"Discovered command: {cmd_name}")

    @slash_command(name="help", description="Get help with bot commands")
    @slash_option(
        name="command",
        description="Specific command to get help with",
        required=False,
        opt_type=OptionType.STRING
    )
    async def handle_help(self, ctx: SlashContext, command: str = None) -> None:
        """Handles the /help command. If no command is specified, shows a list of all commands.
        If a command is specified, shows detailed help for that command.
        """
        if command is None:
            # No specific command requested, show general help
            await self._show_general_help(ctx)
        else:
            # Specific command requested, show detailed help
            await self._show_command_help(ctx, command)

    async def _show_general_help(self, ctx: SlashContext) -> None:
        """Shows a list of all available commands grouped by category."""
        logger.debug(f"Show general help called. Commands: {type(self.command_info)}, {self.command_info}")

        embed = Embed(
            title="Bot Help",
            description="Here are all the available commands. Use `/help [command]` to get detailed information about a specific command.",
            color="#8B008B"
        )

        # If commands is empty or not a dictionary, add a simple field
        if not isinstance(self.command_info, dict) or not self.command_info:
            logger.warning(f"Commands is not a dictionary or is empty: {type(self.command_info)}")
            embed.add_field(
                name="Available Commands",
                value="`/ping` - Check if the bot is alive\n`/resonator` - Get info about resonators\n`/help` - Show this help message",
                inline=False
            )
        else:
            # Group commands by category
            for category, description in self.categories.items():
                logger.debug(f"Processing category: {category}")
                # Get all commands in this category
                category_commands = {cmd: info for cmd, info in self.command_info.items()
                                if info.get("category") == category}

                if category_commands:
                    # Create a field for this category with its commands
                    commands_text = "\n".join([f"`/{cmd}` - {info['description']}"
                                            for cmd, info in category_commands.items()])
                    embed.add_field(name=f"{description}", value=commands_text, inline=False)

        # Add a footer with additional help information
        embed.set_footer(text="Tip: Type /help [command] for detailed information about a specific command")

        await ctx.respond(embed=embed)

    async def _show_command_help(self, ctx: SlashContext, command: str) -> None:
        """Shows detailed help for a specific command."""
        # Remove leading slash if present
        command = command.lstrip('/')

        logger.debug(f"Show command help called for '{command}'. Commands: {type(self.command_info)}")

        # Handle case where self.command_info is not a dictionary
        if not isinstance(self.command_info, dict):
            logger.warning(f"Commands is not a dictionary: {type(self.command_info)}")
            # Provide hardcoded help for known commands
            if command == "ping":
                embed = Embed(
                    title="Help: /ping",
                    description="Check whether the bot is alive",
                    color="#8B008B"
                )
                embed.add_field(name="Usage", value="`/ping`", inline=False)
                embed.add_field(name="Example", value="`/ping`", inline=False)
            elif command == "resonator":
                embed = Embed(
                    title="Help: /resonator",
                    description="Get info about resonators from Wuthering Waves",
                    color="#8B008B"
                )
                embed.add_field(name="Usage", value="`/resonator [name]`", inline=False)
                embed.add_field(name="Example", value="`/resonator Chixia`", inline=False)
                embed.add_field(name="Notes", value="If no name is provided, lists all available Resonators", inline=False)
            elif command == "help":
                embed = Embed(
                    title="Help: /help",
                    description="Get help with bot commands",
                    color="#8B008B"
                )
                embed.add_field(name="Usage", value="`/help [command]`", inline=False)
                embed.add_field(name="Example", value="`/help resonator`", inline=False)
                embed.add_field(name="Notes", value="Use without parameters to see all commands", inline=False)
            else:
                await ctx.respond(f"Command `/{command}` not found. Use `/help` to see all available commands.", ephemeral=True)
                return
        elif command not in self.command_info:
            await ctx.respond(f"Command `/{command}` not found. Use `/help` to see all available commands.", ephemeral=True)
            return
        else:
            # Normal case - self.command_info is a dictionary and command exists
            cmd_info = self.command_info[command]
            embed = Embed(
                title=f"Help: /{command}",
                description=cmd_info["description"],
                color="#8B008B"
            )

            embed.add_field(name="Usage", value=f"`{cmd_info['usage']}`", inline=False)
            embed.add_field(name="Example", value=f"`{cmd_info['example']}`", inline=False)

            if "notes" in cmd_info:
                embed.add_field(name="Notes", value=cmd_info["notes"], inline=False)

        embed.set_footer(text="Use /help to see all available commands")
        await ctx.respond(embed=embed)
