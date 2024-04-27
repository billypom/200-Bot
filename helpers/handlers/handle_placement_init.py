import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.handlers import handle_queued_mmr_penalties
import logging
from constants import PLACEMENT_ROLE_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot, TextChannel


async def handle_placement_init(
    client: "Bot",
    player_id: int,
    player_score: int,
    tier_name: str,
    results_channel: "TextChannel",
) -> tuple[str, int]:
    """Handles necessary actions to set up a placement player after they have participated in a match
    - Determines the rank to place the player
    - Accounts for any queued penalties
    - Assigns rank role in Discord
    - Updates DB accordingly
    ___
    Args:
        client: the discord bot
        player: [player_id, score] - comes from the chunked list of teams in table.py
        tier_name: name of the tier they just played in - this affects placement
        results_channel: the discord TextChannel object of the results channel that corresponds to the tier they just played in

    Returns:
        1: name of a role i.e., iron, bronze, silver, etc
        2: final MMR value
    """
    logging.info(
        f"handle_placement_init: {player_id} scored {player_score}  | {tier_name}"
    )
    placement_name = ""
    my_player_score = player_score
    if tier_name == "tier-c":
        if my_player_score >= 120:
            my_player_mmr = 5250
            placement_name = "Gold"
        elif my_player_score >= 90:
            my_player_mmr = 3750
            placement_name = "Silver"
        elif my_player_score >= 60:
            my_player_mmr = 2250
            placement_name = "Bronze"
        else:
            my_player_mmr = 1000
            placement_name = "Iron"
    else:
        if my_player_score >= 110:
            my_player_mmr = 5250
            placement_name = "Gold"
        elif my_player_score >= 80:
            my_player_mmr = 3750
            placement_name = "Silver"
        elif my_player_score >= 50:
            my_player_mmr = 2250
            placement_name = "Bronze"
        else:
            my_player_mmr = 1000
            placement_name = "Iron"
    # Initial MMR assignment
    with DBA.DBAccess() as db:
        init_rank = int(
            db.query(  # type: ignore
                "SELECT rank_id FROM ranks WHERE placement_mmr = %s;", (my_player_mmr,)
            )[0][0]
        )
        db.execute(
            "UPDATE player SET base_mmr = %s, rank_id = %s WHERE player_id = %s;",
            (my_player_mmr, init_rank, player_id),
        )
    # Assign rank role
    try:
        discord_member = await get_lounge_guild(client).fetch_member(player_id)
        init_role = get_lounge_guild(client).get_role(init_rank)
        placement_role = get_lounge_guild(client).get_role(PLACEMENT_ROLE_ID)
        await discord_member.add_roles(init_role)  # type: ignore
        await discord_member.remove_roles(placement_role)  # type: ignore
        await results_channel.send(
            f"<@{player_id}> has been placed at {placement_name} ({my_player_mmr} MMR)"
        )
    except Exception as e:
        await send_raw_to_debug_channel(
            client, f"<@{player_id}> did not stick around long enough to be placed", e
        )
    # Potential accumulated MMR penalties
    try:
        (
            total_queued_mmr_penalty,
            my_player_new_queued_strike_adjusted_mmr,
        ) = await handle_queued_mmr_penalties(player_id, my_player_mmr)
        # disclosure
        if total_queued_mmr_penalty == 0:
            pass
        else:
            await results_channel.send(
                f"<@{player_id}> accumulated {total_queued_mmr_penalty} worth of MMR penalties during placement.\nMMR adjustment: ({my_player_mmr} -> {my_player_new_queued_strike_adjusted_mmr})"
            )
    except Exception as e:
        await send_raw_to_debug_channel(
            client,
            f"handle_placement_init | Potential accumulated penalties error for player: {player_id}",
            e,
        )
        return str(e), 0

    return placement_name, my_player_new_queued_strike_adjusted_mmr
