import DBA

# Input: str
# Output: Boolean
async def check_if_name_is_unique(name):
    with DBA.DBAccess() as db:
        temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (name,))
    return not temp