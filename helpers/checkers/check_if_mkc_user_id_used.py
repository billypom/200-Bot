import DBA

# Input: int mkc forum id
# Output: Boolean
async def check_if_mkc_user_id_used(mkc_user_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mkc_id, player_id from player WHERE mkc_id = %s;', (mkc_user_id,))
            if int(temp[0][0]) == int(mkc_user_id):
                # return mkc_id, player_id as list
                return [temp[0][0], temp[0][1]]
            else:
                return False
    except Exception as e:
        # await send_raw_to_debug_channel(client, mkc_player_id, e)
        return False