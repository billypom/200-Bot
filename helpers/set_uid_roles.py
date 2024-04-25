import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from constants import CHAT_RESTRICTED_ROLE_ID, PLACEMENT_ROLE_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def set_uid_roles(client: "Bot", uid: int) -> tuple[int, str] | tuple[None, None]:
    """Sets roles for a specific guild member (uid)
    ---
    Args:
        client - discord bot
        uid - Discord User ID"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT player_name, mmr, is_chat_restricted FROM player WHERE player_id = %s;",
                (uid,),
            )
        player_name = temp[0][0]  # type: ignore
        mmr = temp[0][1]  # type: ignore - could be null
        is_chat_restricted = temp[0][2]  # type: ignore

        # Get discord.Guild and discord.Member objects
        guild = get_lounge_guild(client)
        member = await guild.fetch_member(uid)

        if is_chat_restricted:  # Add chat restricted role
            restricted_role = guild.get_role(CHAT_RESTRICTED_ROLE_ID)
            await member.add_roles(restricted_role)  # type: ignore

        # Outcome #1

        if mmr is None:  # Add placement role & return
            role = guild.get_role(PLACEMENT_ROLE_ID)
            await member.add_roles(role)  # type: ignore
            return (role.id, role)  # type: ignore

        # Outcome #2

        with DBA.DBAccess() as db:  # Get ranks info
            ranks = db.query("SELECT rank_id, mmr_min, mmr_max FROM ranks", ())

        for rank in ranks:  # Remove any ranks from player
            remove_rank = guild.get_role(rank[0])  # type: ignore
            await member.remove_roles(remove_rank)  # type: ignore

        for i in range(len(ranks)):  # Find their rank, based on MMR
            if mmr >= int(ranks[i][1]) and mmr < int(ranks[i][2]):  # type: ignore
                # Found your rank
                role = guild.get_role(ranks[i][0])  # type: ignore
                await member.add_roles(role)  # type: ignore
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player SET rank_id = %s WHERE player_id = %s;",
                        (ranks[i][0], member.id),  # type: ignore
                    )

        try:  # Edit their discord nickname
            await member.edit(nick=str(player_name))
        except Exception:
            await member.send(
                "Hello. I am lower in the role hierarchy, therefore I cannot edit your nickname for you. I updated the database with your new name, but you will need to right-click and edit your nickname yourself. c:"
            )
            pass
        return (role.id, role)  # type: ignore
    except IndexError:
        return None, None
    except Exception as e:
        await send_raw_to_debug_channel(
            client, f"set_uid_roles exception triggered by <@{uid}>:", e
        )
        return None, None
