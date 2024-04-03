import DBA


async def check_if_name_is_unique(name: str) -> bool:
    """Checks input against player names in the database

    Returns:
    True if name is unique
    False if name is not unique"""
    with DBA.DBAccess() as db:
        temp = db.query(
            "SELECT player_name FROM player WHERE player_name = %s;", (name,)
        )
    return not temp
