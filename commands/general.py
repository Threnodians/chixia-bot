from interactions import (
    Embed,
    EmbedAttachment,
    EmbedField,
    Extension,
    SlashContext,
    slash_command,
)

# Define latency threshold for health check
LATENCY_THRESHOLD = 200


class GeneralCommands(Extension):
    @slash_command(name="ping", description="Check whether the bot is alive")
    async def handle_ping(self, ctx: SlashContext) -> None:
        # Calculate latency
        latency_ms = round(self.bot.latency * 1000, 3)

        # Determine health status and color
        health_status = "GOOD" if latency_ms < LATENCY_THRESHOLD else "POOR"
        color = "#38b000" if health_status == "GOOD" else "#d62828"

        # Create the embed with dynamic content
        pong_embed = Embed(
            title="Ping Response",
            description="This is a quick check to see if I'm still active!",
            fields=[
                EmbedField(name="Latency", value=f"`{latency_ms}ms`", inline=True),
                EmbedField(name="Health", value=health_status, inline=True),
            ],
            thumbnail=EmbedAttachment(
                url="https://wutheringlab.com/wp-content/uploads/2023/06/Wuthering-Waves-Chixia.png"
            ),
            color=color,
        )

        # Respond with the embed
        await ctx.respond(embed=pong_embed, ephemeral=False)
