from helpers.getters import get_lounge_guild


async def check_if_uid_has_role(client, uid: int, role_id: int) -> bool:
    """Checks if a certain user (uid) has a role (role_id)

    Returns:
    True if role is found on user
    False if role not found"""
    guild = get_lounge_guild(client)
    member = await guild.fetch_member(uid)
    for role in member.roles:
        if role_id == role.id:
            return True
    return False
