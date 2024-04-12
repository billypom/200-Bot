from helpers.getters import get_lounge_guild
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Role
    from discord import Bot


def get_discord_role(client: "Bot", role_id: int) -> "Role":
    """Returns a discord.Role object given an integer role_id"""
    guild = get_lounge_guild(client)
    role = guild.get_role(role_id)
    return role  # type: ignore
