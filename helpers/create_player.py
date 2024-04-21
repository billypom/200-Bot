import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.senders import send_raw_to_verification_log
from helpers.handlers import handle_player_name
from helpers.getters import get_lounge_guild
import logging
from constants import (
    PLACEMENT_ROLE_ID,
    SUPPORT_CHANNEL_ID,
)


async def create_player(client, member, mkc_user_id, country_code):
    """Handles creation of a new player on the leaderboard
    - Handles nickname
    - Adds to database
    - Adds discord role
    - Sends user feedback
    ---
    Args:
        client: discord bot
        member: associated discord member
        mkc_user_id: MKC forum ID
        country_code: Alpha-2 ISO Country Code
    Returns:
        User feedback message - confirmation or error message"""
    logging.info("create_player | start")
    altered_name = await handle_player_name(member.display_name)
    logging.info(f"create_player | Finished handling name: {altered_name}")
    try:
        with DBA.DBAccess() as db:
            db.execute(
                "INSERT INTO player (player_id, player_name, mkc_id, country_code, rank_id) VALUES (%s, %s, %s, %s, %s);",
                (member.id, altered_name, mkc_user_id, country_code, PLACEMENT_ROLE_ID),
            )
    except Exception as e:
        await send_raw_to_debug_channel(
            client, f"create_player error 14 <@{member.id}>", e
        )
        return f"``Error 14:`` Oops! An unlikely error occured. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
        # 1. a player trying to use someone elses link (could be banned player)
        # 2. a genuine player locked from usage by another player (banned player might have locked them out)
        # 3. someone is verifying multiple times because they can't get into their mkc account and they made a second one
    # Edit nickname
    try:
        await member.edit(nick=str(altered_name))
    except Exception as e:
        await send_raw_to_debug_channel(
            client,
            f"create_player error 15 - CANNOT EDIT NICK FOR USER <@{member.id}>",
            e,
        )
    role = get_lounge_guild(client).get_role(PLACEMENT_ROLE_ID)
    logging.info(f"create_player | {altered_name} | Attempted to edit nickname")
    # Add role
    try:
        await member.add_roles(role)
    except Exception as e:
        await send_raw_to_debug_channel(
            client,
            f"create_player error 16 - CANNOT EDIT ROLE FOR USER <@{member.id}>",
            e,
        )
    logging.info(f"create_player | {altered_name} | Attempted to add roles")
    # Confirmation log
    await send_raw_to_verification_log(
        client,
        f"player:<@{member.id}>\nrole:`{role}`\naltered name:`{altered_name}`",
        "**Creating player**",
    )
    # User feedback
    return f":flag_us:\nVerified & registered successfully. :thewman: Assigned <@&{role.id}>\n:flag_jp:認証に成功しました。{role}が割り当てられました。"  # type: ignore
