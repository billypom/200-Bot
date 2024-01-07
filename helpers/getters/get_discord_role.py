from helpers.getters import get_lounge_guild

# Input: int role_id
# Output: discord.Role object
def get_discord_role(client, role_id):
    guild = get_lounge_guild(client)
    role = guild.get_role(role_id)
    return role
    