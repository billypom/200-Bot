import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild, get_unix_time_now
from constants import CHAT_RESTRICTED_ROLE_ID, LOUNGELESS_ROLE_ID, PLACEMENT_ROLE_ID
from typing import TYPE_CHECKING
from helpers import remove_rank_roles_from_uid

if TYPE_CHECKING:
    from discord import Bot


async def set_uid_roles(client: "Bot", uid: int) -> tuple[int, str] | tuple[None, None]:
    """Sets roles for a specific guild member (uid)
    ---
    Args:
        client - discord bot
        uid - Discord User ID"""
    role = None
    try:
        # Get discord.Guild and discord.Member objects
        guild = get_lounge_guild(client)
        member = await guild.fetch_member(uid)
    except Exception as e:
        # member not in server
        # await send_raw_to_debug_channel(client, f'{uid} not found in server. Not setting roles', e)
        return None, None

    try:  # Edit their discord nickname
        with DBA.DBAccess() as db:
            data = db.query(
                "SELECT player_name, mkc_id FROM player WHERE player_id = %s;",
                (uid,),
            )[0]  # type: ignore
            player_name = data[0]
            mkc_id = int(data[1])
    except Exception as e:
        # member not in leaderboard
        # await send_raw_to_debug_channel(client, f'{uid} not found in leaderboard. Not setting roles', e)
        return None, None
    if mkc_id == 0:
        return None, None
    try:
        await member.edit(nick=str(player_name))
    except Exception:
        try:
            await member.send(
                "Hello. I am lower in the role hierarchy, therefore I cannot edit your nickname for you. I updated the database with your new name, but you will need to right-click and edit your nickname yourself. c:"
            )
        except Exception:
            pass
        pass

    try:  # chat restricted
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT player_name, mmr, is_chat_restricted FROM player WHERE player_id = %s;",
                (uid,),
            )
        player_name = temp[0][0]  # type: ignore
        mmr = temp[0][1]  # type: ignore - could be null
        is_chat_restricted = temp[0][2]  # type: ignore

        if is_chat_restricted:  # Add chat restricted role
            role = guild.get_role(CHAT_RESTRICTED_ROLE_ID)
            await member.add_roles(role)  # type: ignore
    except Exception as e:
        await send_raw_to_debug_channel(
            client, f"set_uid_roles exception triggered by <@{uid}>:", e
        )
        return None, None
    is_loungeless = False
    try:  # loungeless
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT punishment_id, unban_date FROM player_punishment WHERE player_id = %s ORDER BY create_date DESC LIMIT 1;",
                (uid,),
            )
            punishment_id = temp[0][0]
            unban_date = temp[0][1]
            unix_now = await get_unix_time_now()
            role = None
            if unban_date > unix_now and punishment_id == 2:
                role = guild.get_role(LOUNGELESS_ROLE_ID)
                await member.add_roles(role)
                is_loungeless = True
                await remove_rank_roles_from_uid(client, uid)
    except Exception:  # no punishments exist
        pass
    # Loungeless people do not get their rank roles
    if not is_loungeless:
        # Outcome #1
        if mmr is None:  # Add placement role & return
            role = guild.get_role(PLACEMENT_ROLE_ID)
            await member.add_roles(role)
            return (role.id, role)

        # Outcome #2
        with DBA.DBAccess() as db:  # Get ranks info
            ranks = db.query("SELECT rank_id, mmr_min, mmr_max FROM ranks", ())

        for rank in ranks:  # Remove any ranks from player
            remove_rank = guild.get_role(rank[0])
            try:
                await member.remove_roles(remove_rank)
            except AttributeError:
                pass

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

    return (role.id, role)  # type: ignore
