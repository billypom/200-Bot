import DBA

# Input: int discord user id
# Output: Boolean
async def check_if_uid_is_lounge_banned(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT UNIX_TIMESTAMP(unban_date) FROM player WHERE player_id = %s;', (uid,))
        if temp[0][0] is None:
            return False
        else:
            return temp[0][0]
    except Exception:
        return False