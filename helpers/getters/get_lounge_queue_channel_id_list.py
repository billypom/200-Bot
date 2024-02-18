import DBA

async def get_lounge_queue_channel_id_list() -> list:
    # Used to make sure certain actions only happen in the tiers
    id_list = list() 
    with DBA.DBAccess() as db:
        result = db.query('SELECT channel_id FROM lounge_queue_channel;', ())
        for i in range(len(result)):
            id_list.append(result[i][0])
    return id_list