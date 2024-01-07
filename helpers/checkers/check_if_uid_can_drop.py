import DBA

# Input: int discord user id
# Output: Boolean
async def check_if_uid_can_drop(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT can_drop FROM lineups WHERE player_id = %s;', (uid,))
            if temp[0][0] is True:
                return True
            else:
                return False
    except Exception: # Player not in any lineups?
        return True