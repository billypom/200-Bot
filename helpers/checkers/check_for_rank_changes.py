import DBA
import logging


async def check_for_rank_changes(
    player_mmr: int, player_new_mmr: int
) -> tuple[bool, bool, int] | None:
    """Checks for a rank up or down, based on given current and new mmr values

    Returns:
    - bool: True if rank has changed, False if rank has not changed
    - bool: True if rank up, False if rank down
    - int: new rank id (discord role id)
    """
    try:
        with DBA.DBAccess() as db:
            db_ranks_table = db.query(
                "SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s;",
                (1,),
            )
    except Exception as e:
        logging.warning(f"ERROR in check_for_rank_changes - db access error - {str(e)}")
        return None
    for i in range(len(db_ranks_table)):
        rank_id = int(db_ranks_table[i][0])  # type: ignore
        min_mmr = int(db_ranks_table[i][1])  # type: ignore
        max_mmr = int(db_ranks_table[i][2])  # type: ignore
        if player_mmr < min_mmr and player_new_mmr >= min_mmr:
            # Rank up
            return True, True, rank_id
        elif player_mmr > max_mmr and player_new_mmr <= max_mmr:
            # Rank down
            return True, False, rank_id
    return False, False, 0
