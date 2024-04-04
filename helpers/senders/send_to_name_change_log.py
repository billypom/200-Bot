import discord
from config import NAME_CHANGE_CHANNEL_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import Context
    from discord import Bot, Message


async def send_to_name_change_log(
    client: Bot, ctx: Context, id: int, message: str
) -> Message:
    channel = client.get_channel(NAME_CHANGE_CHANNEL_ID)
    embed = discord.Embed(
        title="Name Change Request",
        description=f"id: {id}",
        color=discord.Color.blurple(),
    )
    name = ctx.author.display_name
    embed.add_field(name="Current Name: ", value=name, inline=False)
    embed.add_field(name="New Name: ", value=str(message), inline=False)
    embed.add_field(name="Discord ID: ", value=ctx.author.id, inline=False)
    try:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    except Exception:
        pass
    x = await channel.send(content=None, embed=embed)
    return x
