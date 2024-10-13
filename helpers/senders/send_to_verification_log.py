from constants import VERIFICATION_LOG_CHANNEL_ID
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import ApplicationContext
    from discord import Bot, TextChannel


async def send_to_verification_log(
    client: "Bot", ctx: "ApplicationContext", message: str, title: str
):
    """Sends a message to the verification log channel"""
    channel = cast("TextChannel", client.get_channel(VERIFICATION_LOG_CHANNEL_ID))
    await channel.send(f"{title}\nIssued by:{ctx.author.id}\n{message}")
