from config import VERIFICATION_CHANNEL_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def send_raw_to_verification_log(
    client: Bot, message: str, verify_description: str
) -> None:
    """Sends some text to the verification channel"""
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)
    await channel.send(f"{verify_description}\n{message}")
