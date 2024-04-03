# UNUSED

import DBA


# Input: int discord user id, int discord channel id
# Output: Boolean
async def check_if_uid_in_specific_tier(uid, tier):
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;",
                (uid, tier),
            )
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False
