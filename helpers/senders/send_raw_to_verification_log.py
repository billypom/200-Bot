from constants import VERIFICATION_LOG_CHANNEL_ID
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from discord import Bot, TextChannel


async def send_raw_to_verification_log(
    client: "Bot", message: str, verify_description: str
) -> None:
    """Sends some text to the verification channel"""
    channel: "TextChannel" = cast(
        "TextChannel", client.get_channel(VERIFICATION_LOG_CHANNEL_ID)
    )
    await channel.send(f"{verify_description}\n{message}")
