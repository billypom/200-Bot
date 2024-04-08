import DBA


async def check_if_uid_exists(uid: int) -> bool:
    """Checks if a particular discord user id exists

    Returns:
    True if exists
    False is does not exist"""
    try:
        with DBA.DBAccess() as db:
            player_id = db.query(
                "SELECT player_id FROM player WHERE player_id = %s;", (uid,)
            )[0][0]  # type: ignore
            if str(player_id) == str(uid):
                return True
            else:
                return False
    except Exception:
        return False
