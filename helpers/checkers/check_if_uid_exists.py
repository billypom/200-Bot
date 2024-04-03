import DBA


async def check_if_uid_exists(uid: int) -> bool:
    """Checks if a particular discord user id exists

    Returns:
    True if exists
    False is does not exist"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT player_id FROM player WHERE player_id = %s;", (uid,)
            )
            if str(temp[0][0]) == str(uid):  # type: ignore
                return True
            else:
                return False
    except Exception:
        return False
