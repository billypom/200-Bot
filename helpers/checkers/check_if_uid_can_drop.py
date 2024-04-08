# UNUSED

import DBA


async def check_if_uid_can_drop(uid):
    try:
        with DBA.DBAccess() as db:
            can_drop = db.query(
                "SELECT can_drop FROM lineups WHERE player_id = %s;", (uid,)
            )[0][0]  # type: ignore
            if can_drop is True:
                return True
            else:
                return False
    except Exception:  # Player not in any lineups?
        return True
