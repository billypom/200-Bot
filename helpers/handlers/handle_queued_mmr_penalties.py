import DBA
# Input: (int discord user id, int user's current MMR)
# Returns: (int total penalty, int new adjusted mmr value)
async def handle_queued_mmr_penalties(player_id, my_player_mmr):
    # Get all records with penalty not applied
    with DBA.DBAccess() as db:
        total_queued_mmr_penalty = db.query('SELECT sum(mmr_penalty) FROM strike WHERE penalty_applied = %s AND player_id = %s;', (0, player_id))[0][0]

    if total_queued_mmr_penalty is None:
        return 0, my_player_mmr

    my_player_new_queued_strike_adjusted_mmr = my_player_mmr - total_queued_mmr_penalty

    # Update players mmr
    with DBA.DBAccess() as db:
        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_queued_strike_adjusted_mmr, player_id))

    # Strike penalty applied = True
    with DBA.DBAccess() as db:
        db.execute('UPDATE strike SET penalty_applied = %s WHERE player_id = %s;', (1, player_id))

    return total_queued_mmr_penalty, my_player_new_queued_strike_adjusted_mmr