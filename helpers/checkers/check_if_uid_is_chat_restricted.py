import DBA

# Input: int discord user id
# Output: Boolean
async def check_if_uid_is_chat_restricted(uid):
    with DBA.DBAccess() as db:
        temp = db.query('SELECT is_chat_restricted FROM player WHERE player_id = %s;', (uid,))
    if temp:
        return temp[0][0]
    else:
        return False