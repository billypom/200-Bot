import DBA

# Input: int discord user id
# Output: Boolean
async def check_if_uid_in_any_active_tier(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND can_drop = 0;', (uid,))
        if temp[0][0] == uid:
            return True
        else:
            return False
    except Exception:
        return False