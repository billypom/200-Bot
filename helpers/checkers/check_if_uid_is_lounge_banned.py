import DBA


# Input: int discord user id
# Output: Boolean
async def check_if_uid_is_lounge_banned(uid: int) -> int | bool:
    """Checks if a certain player (uid) is lounge banned

    Returns
    Unix timestamp of loungeless/banned by strikes unban date, if is banned
    False is not banned"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT banned_by_strikes_unban_date FROM player WHERE player_id = %s;",
                (uid,),
            )
        if temp[0][0] is None:  # type: ignore
            return False
        else:
            return temp[0][0]  # type: ignore
    except Exception:
        return False
