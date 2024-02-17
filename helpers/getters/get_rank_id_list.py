import DBA

async def get_rank_id_list() -> list:
    RANK_ID_LIST = list()
    with DBA.DBAccess() as db: # Initialize the RANK_ID_LIST
        result = db.query('SELECT rank_id FROM ranks WHERE rank_id > %s;', (0,))
        for i in range(len(result)):
            RANK_ID_LIST.append(result[i][0])
    return RANK_ID_LIST