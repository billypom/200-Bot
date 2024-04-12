from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from config import CHAT_RESTRICTED_ROLE_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def set_uid_chat_restricted(client: "Bot", uid: int):
    """Adds the chat restricted role to a user, given a discord ID
    ---
    Args:
        client - discord bot
        uid - Discord User ID"""
    try:
        member = await get_lounge_guild(client).fetch_member(uid)
        role = get_lounge_guild(client).get_role(CHAT_RESTRICTED_ROLE_ID)
        await member.add_roles(role)  # type: ignore
        return True
    except Exception as e:
        await send_raw_to_debug_channel(
            client, "Could not set uid [{uid}] to chat restricted", e
        )
        return False
