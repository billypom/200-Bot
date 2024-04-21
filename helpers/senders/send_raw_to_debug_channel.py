from constants import DEBUG_CHANNEL_ID
from discord import Embed, Color
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import Bot, TextChannel


async def send_raw_to_debug_channel(
    client: "Bot", anything: str, error: Exception | None
) -> None:
    """Sends some text to the debug channel"""
    channel = cast("TextChannel", client.get_channel(DEBUG_CHANNEL_ID))
    await channel.send(f"**>.<**\n{anything}\n{error}")
