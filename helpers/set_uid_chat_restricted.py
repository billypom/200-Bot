from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from config import CHAT_RESTRICTED_ROLE_ID
# Input: discord user id
# Output: Boolean
async def set_uid_chat_restricted(client, uid):
    try:
        member = await get_lounge_guild(client).fetch_member(uid)
        role = get_lounge_guild(client).get_role(CHAT_RESTRICTED_ROLE_ID)
        await member.add_roles(role)
        return True
    except Exception:
        await send_raw_to_debug_channel(client, 'Could not set uid to chat restricted', uid)
        return False