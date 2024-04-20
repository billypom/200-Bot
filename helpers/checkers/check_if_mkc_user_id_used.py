import DBA
from helpers.senders import send_raw_to_debug_channel
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def check_if_mkc_user_id_used(mkc_user_id: int) -> bool:
    """Checks if a MKC Forum ID has already been used by another player in the database

    Returns: True if used, else False"""
    try:
        with DBA.DBAccess() as db:
            temp = db.query(
                "SELECT mkc_id, player_id from player WHERE mkc_id = %s;",
                (mkc_user_id,),
            )
            if int(temp[0][0]) == int(mkc_user_id):  # type: ignore
                return True
            else:
                return False
    except Exception as e:
        logging.warning(
            f"| ERROR IN check_if_mkc_user_id_used: mkc_user_id={mkc_user_id}: {e}"
        )
        return False
