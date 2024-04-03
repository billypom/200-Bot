from config import DEBUG_CHANNEL_ID
from discord import Embed, Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def send_raw_to_debug_channel(
    client: Bot, anything: str, error: Exception
) -> None:
    """Sends some text to the debug channel"""
    channel = client.get_channel(DEBUG_CHANNEL_ID)
    await channel.send(f"**>.<**\n{anything}\n{error}")
    # embed = Embed(title="Debug", description=">.<", color=Color.yellow())
    # embed.add_field(name="Details: ", value=anything, inline=False)
    # embed.add_field(name="Traceback: ", value=str(error), inline=False)
    # await channel.send(content=None, embed=embed)
