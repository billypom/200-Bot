import DBA
from helpers.senders import send_raw_to_debug_channel


async def check_if_mkc_user_id_used(client, mkc_user_id: int) -> list[int] | bool:
    """Checks if a MKC Forum ID has already been used by another player in the database

    Returns:
        list[mkc_id, player_id] if a match is found
        or
        False"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT mkc_id, player_id from player WHERE mkc_id = %s;",
                (mkc_user_id,),
            )
            if int(temp[0][0]) == int(mkc_user_id):  # type: ignore
                return [temp[0][0], temp[0][1]]  # type: ignore
            else:
                return False
    except Exception as e:
        await send_raw_to_debug_channel(
            client=client,
            anything=f"check_if_mkc_user_id_used | Database error, mkc_user_id={mkc_user_id}",
            error=e,
        )
        return False
