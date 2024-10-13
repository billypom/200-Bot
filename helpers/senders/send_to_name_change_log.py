import discord
from constants import NAME_CHANGE_CHANNEL_ID
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import ApplicationContext
    from discord import Bot, Message, TextChannel


async def send_to_name_change_log(
    client: "Bot", ctx: "ApplicationContext", id: int, message: str
) -> "Message":
    """
    Sends an embed to the name change request channel
    """
    channel = cast("TextChannel", client.get_channel(NAME_CHANGE_CHANNEL_ID))
    embed = discord.Embed(
        title="Name Change Request",
        description=f"id: {id}",
        color=discord.Color.blurple(),
    )
    name = ctx.author.display_name
    embed.add_field(name="Current Name: ", value=name, inline=False)
    embed.add_field(name="New Name: ", value=str(message), inline=False)
    embed.add_field(name="Discord ID: ", value=str(ctx.author.id), inline=False)
    try:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    except Exception:
        pass
    x = await channel.send(content=None, embed=embed)
    return x
