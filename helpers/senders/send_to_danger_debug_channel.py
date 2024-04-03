import discord
from config import DEBUG_CHANNEL_ID
from config import PING_DEVELOPER


async def send_to_danger_debug_channel(
    client, ctx, message, verify_color, verify_description
):
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    embed = discord.Embed(
        title="Debug DANGER:", description=verify_description, color=verify_color
    )
    embed.add_field(name="Name: ", value=ctx.author.mention, inline=False)
    embed.add_field(name="Message: ", value=message, inline=False)
    embed.add_field(name="Discord ID: ", value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)
    await channel.send(f"{PING_DEVELOPER}")
