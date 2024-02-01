from helpers.getters import get_lounge_guild
# Input: client, int discord_id, int role_id
# Output: Boolean
async def check_if_uid_has_role(client, uid, role_id):
    guild = get_lounge_guild(client)
    member = await guild.fetch_member(uid)
    for role in member.roles:
        if role_id == role.id:
            return True
    return False
    
