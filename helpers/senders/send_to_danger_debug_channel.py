import discord
from constants import DEBUG_CHANNEL_ID, PING_DEVELOPER
from typing import TYPE_CHECKING


async def send_to_danger_debug_channel(
    client: discord.Bot,
    ctx: discord.ApplicationContext,
    message: str,
    verify_color: discord.Color,
    verify_description: str,
):
    """Sends a danger alert message to the developer debug channel

    Args:
    - `client` (discord.Bot): The bot
    - `ctx` (discord.ApplicationContext): The context of the command
    - `message` (str): A message
    - `verify_color` (discord.Color): Color of the embed
    - `verify_description` (str): A description"""
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    if not isinstance(channel, discord.abc.GuildChannel):
        return
    embed = discord.Embed(
        title="Debug DANGER:", description=verify_description, color=verify_color
    )
    embed.add_field(name="Name: ", value=ctx.author.mention, inline=False)
    embed.add_field(name="Message: ", value=message, inline=False)
    embed.add_field(name="Discord ID: ", value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)
    await channel.send(f"{PING_DEVELOPER}")
