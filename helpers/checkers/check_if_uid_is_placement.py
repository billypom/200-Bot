import DBA
import logging

# Input: int discord user id
# Output: Boolean
async def check_if_uid_is_placement(uid):
    try:
        with DBA.DBAccess() as db:
            mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (uid,))[0][0]
        if mmr is None:
            return True
        elif mmr >= 0:
            return False
    except Exception as e:
        logging.warning(f'check_if_uid_is_placement | error, could not retrieve mmr for player with uid: {uid} | {e}')
        return True