from config import LOUNGE

# Returns discord.Guild object
def get_lounge_guild(client):
    guild = client.get_guild(LOUNGE[0])
    return guild