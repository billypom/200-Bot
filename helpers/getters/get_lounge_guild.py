from config import LOUNGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot, Guild


# Returns discord.Guild object
def get_lounge_guild(client: "Bot") -> "Guild":
    """Returns the discord.Guild object for the config's LOUNGE guild"""
    guild = client.get_guild(int(LOUNGE[0]))
    return guild  # type: ignore
