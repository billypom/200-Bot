import DBA

# Input: int discord user id, int discord channel id
# Output: Boolean
async def check_if_uid_in_first_12_of_tier(uid, tier):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM (SELECT player_id FROM lineups WHERE tier_id = %s) as derived_table WHERE player_id = %s;', (tier, uid))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False