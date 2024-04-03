import DBA


async def get_tier_id_list() -> list:
    """Returns a list of all channel ids (tier_id) from the database"""
    # Used to make sure certain actions only happen in the tiers
    TIER_ID_LIST = list()
    with DBA.DBAccess() as db:
        result = db.query("SELECT tier_id FROM tier WHERE tier_id > %s;", (0,))
        for i in range(len(result)):
            TIER_ID_LIST.append(result[i][0])  # type: ignore
    return TIER_ID_LIST
