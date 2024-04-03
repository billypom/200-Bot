# UNUSED

import DBA


async def check_if_uid_can_drop(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT can_drop FROM lineups WHERE player_id = %s;", (uid,)
            )
            if temp[0][0] is True:  # type: ignore
                return True
            else:
                return False
    except Exception:  # Player not in any lineups?
        return True
