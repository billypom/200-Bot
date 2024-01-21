import DBA

# Input: int discord user id
# Output: Boolean
async def check_if_uid_exists(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_id = %s;', (uid,))
            if str(temp[0][0]) == str(uid):
                return True
            else:
                return False
    except Exception:
        return False