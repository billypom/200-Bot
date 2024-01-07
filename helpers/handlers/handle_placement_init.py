import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.handlers import handle_queued_mmr_penalties
import logging
from config import PLACEMENT_ROLE_ID

# Input: Player object (discord_id, score), their mmr, their score, and the tier name
#   Determines what rank to place a player
#   Updates DB records
#   Assigns rank role
#   Accounts for queued penalties
# Outpit: the name of their rank role, new mmr value
async def handle_placement_init(client, player, my_player_mmr, my_player_score, tier_name, results_channel):
    logging.info(f'POP_LOG | handle_placement_init: {player} | {my_player_mmr} | {my_player_score} | {tier_name}')
    placement_name = ''

    if tier_name == 'tier-c':
        if my_player_score >=120:
            my_player_mmr = 5250
            placement_name = 'Gold'
        elif my_player_score >= 90:
            my_player_mmr = 3750
            placement_name = 'Silver'
        elif my_player_score >= 60:
            my_player_mmr = 2250
            placement_name = 'Bronze'
        else:
            my_player_mmr = 1000
            placement_name = 'Iron'
    else:
        if my_player_score >=110:
            my_player_mmr = 5250
            placement_name = 'Gold'
        elif my_player_score >= 80:
            my_player_mmr = 3750
            placement_name = 'Silver'
        elif my_player_score >= 50:
            my_player_mmr = 2250
            placement_name = 'Bronze'
        else:
            my_player_mmr = 1000
            placement_name = 'Iron'

    # Initial MMR assignment
    with DBA.DBAccess() as db:
        init_rank = db.query('SELECT rank_id FROM ranks WHERE placement_mmr = %s;', (my_player_mmr,))[0][0]
        db.execute('UPDATE player SET base_mmr = %s, rank_id = %s WHERE player_id = %s;', (my_player_mmr, init_rank, player[0]))
    
    # Assign rank role
    try:
        discord_member = await get_lounge_guild(client).fetch_member(player[0])
        init_role = get_lounge_guild(client).get_role(init_rank)
        placement_role = get_lounge_guild(client).get_role(PLACEMENT_ROLE_ID)
        await discord_member.add_roles(init_role)
        await discord_member.remove_roles(placement_role)
        await results_channel.send(f'<@{player[0]}> has been placed at {placement_name} ({my_player_mmr} MMR)')
    except Exception as e:
        await send_raw_to_debug_channel(client, f'<@{player[0]}> did not stick around long enough to be placed',e)

    # Potential accumulated MMR penalties
    try:
        total_queued_mmr_penalty, my_player_new_queued_strike_adjusted_mmr = await handle_queued_mmr_penalties(player[0], my_player_mmr)
        # disclosure
        if total_queued_mmr_penalty == 0:
            pass
        else:
            await results_channel.send(f'<@{player[0]}> accumulated {total_queued_mmr_penalty} worth of MMR penalties during placement.\nMMR adjustment: ({my_player_mmr} -> {my_player_new_queued_strike_adjusted_mmr})')
    except Exception as e:
        await send_raw_to_debug_channel(client, f'Potential accumulated penalties error for player: {player[0]}', e)
    
    return placement_name, my_player_new_queued_strike_adjusted_mmr