from interactions import Extension, slash_command, SlashContext

class Character(Extension):
    @slash_command(
        name="resonator",
        description="Get info about resonator"
    )
    async def handle_resonator(self, ctx: SlashContext) -> None:
        await ctx.respond("hello", ephemeral=True)

    @handle_resonator.subcommand(
        sub_cmd_name="get",
        group_name="resonator",
        sub_cmd_description="Get info of resonator"
    )
    async def handle_resonator_get(self, ctx: SlashContext) -> None:
        await ctx.respond("Resonator get invoked")