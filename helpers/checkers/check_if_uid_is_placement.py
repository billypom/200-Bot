import DBA
import logging


async def check_if_uid_is_placement(uid):
    """Checks if a certain player (uid) is placement, according to the database

    Returns:
    True if placement
    False if not"""
    try:
        with DBA.DBAccess() as db:
            mmr = int(
                db.query("SELECT mmr FROM player WHERE player_id = %s;", (uid,))[0][0]  # type: ignore
            )
        if mmr is None:
            return True
        elif mmr >= 0:
            return False
    except Exception as e:
        logging.warning(
            f"check_if_uid_is_placement | error, could not retrieve mmr for player with uid: {uid} | {e}"
        )
        return True
