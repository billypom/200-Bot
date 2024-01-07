import DBA

# Input: int mogi id
# Output: Boolean
async def check_if_mogi_id_exists(mogi_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mogi_id FROM mogi WHERE mogi_id = %s;', (mogi_id,))
        if temp[0][0] == mogi_id:
            return True
        else:
            return False
    except Exception:
        return False