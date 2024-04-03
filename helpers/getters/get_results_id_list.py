import DBA


async def get_results_id_list() -> list:
    """Returns a list of all result_id from DB tier table"""
    # Used to make sure certain actions only happen in the tiers
    results = list()
    with DBA.DBAccess() as db:
        result = db.query("SELECT results_id FROM tier WHERE tier_id > %s;", (0,))
        for i in range(len(result)):
            results.append(result[i][0])  # type: ignore
    return results
