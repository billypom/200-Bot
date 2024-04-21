import DBA


async def handle_queued_mmr_penalties(
    player_id: int, my_player_mmr: int
) -> tuple[int, int]:
    """Handles updating a players MMR, accounting for their accumulated penalties"""
    # Get all player strike records where penalty has not been applied yet
    try:
        with DBA.DBAccess() as db:
            total_queued_mmr_penalty = int(
                db.query(  # type: ignore
                    "SELECT sum(mmr_penalty) FROM strike WHERE penalty_applied = %s AND player_id = %s;",
                    (0, player_id),
                )[0][0]
            )
    # When there are no strikes
    except TypeError:
        return 0, my_player_mmr
    if total_queued_mmr_penalty is None:
        return int(0), my_player_mmr
    # Calculate
    my_player_new_queued_strike_adjusted_mmr = my_player_mmr - total_queued_mmr_penalty
    # Update players mmr
    with DBA.DBAccess() as db:
        db.execute(
            "UPDATE player SET mmr = %s WHERE player_id = %s;",
            (my_player_new_queued_strike_adjusted_mmr, player_id),
        )
    # Strike penalty applied = True
    with DBA.DBAccess() as db:
        db.execute(
            "UPDATE strike SET penalty_applied = %s WHERE player_id = %s;",
            (1, player_id),
        )
    return total_queued_mmr_penalty, my_player_new_queued_strike_adjusted_mmr
