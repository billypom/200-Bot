import DBA


async def check_if_mogi_id_exists(mogi_id: int) -> bool:
    """Checks for the existence of a particular mogi id"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query("SELECT mogi_id FROM mogi WHERE mogi_id = %s;", (mogi_id,))
        if temp[0][0] == mogi_id:  # type: ignore
            return True
        else:
            return False
    except Exception:
        return False
