from helpers.getters import get_lounge_guild
from helpers.getters import get_rank_id_list

# Input: discord user id
# Output:
async def remove_rank_roles_from_uid(client, uid):
    member = await get_lounge_guild(client).fetch_member(uid)
    # Remove any ranks from member
    for rank in get_rank_id_list: 
        remove_rank = get_lounge_guild(client).get_role(rank[0])
        await member.remove_roles(remove_rank)