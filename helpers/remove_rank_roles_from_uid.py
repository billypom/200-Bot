from helpers.getters import get_lounge_guild
from helpers.getters import get_rank_id_list
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def remove_rank_roles_from_uid(client: "Bot", uid: int) -> None:
    member = await get_lounge_guild(client).fetch_member(uid)
    # Remove any ranks from member
    rank_id_list = await get_rank_id_list()
    for rank in rank_id_list:
        remove_rank = get_lounge_guild(client).get_role(rank)
        await member.remove_roles(remove_rank)  # type: ignore
