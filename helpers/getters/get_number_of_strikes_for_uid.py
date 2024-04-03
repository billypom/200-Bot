import DBA


async def get_number_of_strikes_for_uid(uid: int) -> int:
    """Returns a number of strikes a certain player (uid) has"""
    with DBA.DBAccess() as db:
        num_strikes = int(
            db.query(  # type: ignore
                "SELECT COUNT(*) FROM strike WHERE player_id = %s AND is_active = %s;",
                (uid, 1),
            )[0][0]
        )
        if num_strikes is None:
            return 0
        else:
            return num_strikes
