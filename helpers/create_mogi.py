import DBA


async def create_mogi(mogi_format: int, tier_id: int) -> tuple[int, str]:
    """Creates a mogi record

    Returns the results channel id and name of the tier"""
    # Create mogi
    with DBA.DBAccess() as db:
        db.execute(
            "INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);",
            (mogi_format, tier_id),
        )
    # Get the results channel and tier name for later use
    with DBA.DBAccess() as db:
        temp = db.query(
            "SELECT results_id, tier_name FROM tier WHERE tier_id = %s;",
            (tier_id,),
        )
        results_id = int(temp[0][0])  # type: ignore
        tier_name = str(temp[0][1])  # type: ignore
    return results_id, tier_name
