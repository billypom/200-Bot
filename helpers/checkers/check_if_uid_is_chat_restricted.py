import DBA


async def check_if_uid_is_chat_restricted(uid: int) -> bool:
    """Checks if a certain guild member (uid) is chat restricted, according to the database"""
    with DBA.DBAccess() as db:
        is_chat_restricted = db.query(
            "SELECT is_chat_restricted FROM player WHERE player_id = %s;", (uid,)
        )[0][0]  # type: ignore
    if is_chat_restricted:
        return True
    else:
        return False
