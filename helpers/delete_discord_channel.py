import logging
from typing import TYPE_CHECKING

from discord import TextChannel


if TYPE_CHECKING:
    from discord import Bot
    from discord.threads import Thread
    from discord.abc import PrivateChannel, GuildChannel


async def delete_discord_channel(client: "Bot", channel_id: int):
    """Deletes a discord channel by ID

    Args:
    - `client` (discord.Bot): The bot
    - `channel_id` (int): Channel ID

    Returns:
    - `true`: If the channel was deleted or not found
    - `false`: If there was an exception when deleting the channel"""
    channel = client.get_channel(channel_id)
    if channel:
        try:
            await channel.delete()
            return True
        except Exception:
            return False
    else:
        logging.error(f"delete_discord_channel.py | Channel {channel_id} not found")
        # ok to return true here, dont care if didnt find channel
        return True
