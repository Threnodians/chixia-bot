from  interactions import Extension, slash_command, SlashContext, Embed, EmbedField, EmbedAttachment

class GeneralCommands(Extension):
    @slash_command(
        name="ping",
        description="Check whether the bot is alive"
    )
    async def handle_ping(self, ctx: SlashContext) -> None:
        pong_embed = Embed(
            title="Welcome Rover!",
            description="I'm Chixia, your companion! You can ask me about Resonators, Echoes, Builds etc.,",
            fields=[
                EmbedField("Latency", f"`{round(self.bot.latency, 3)}ms`", inline=True),
                EmbedField("Health", "GOOD", inline=True)
            ],
            thumbnail=EmbedAttachment(
                url="https://wutheringlab.com/wp-content/uploads/2023/06/Wuthering-Waves-Chixia.png"
            ),
            color="#8B008B"
        )
        await ctx.respond(embed=pong_embed, ephemeral=False)