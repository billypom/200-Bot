import DBA
# Input: int discord user id
# Output: int number of strikes
async def get_number_of_strikes_for_uid(uid) -> int:
    with DBA.DBAccess() as db:
        temp = db.query('SELECT COUNT(*) FROM strike WHERE player_id = %s AND is_active = %s;', (uid, 1))
        if temp[0][0] is None:
            return 0
        else:
            return temp[0][0]