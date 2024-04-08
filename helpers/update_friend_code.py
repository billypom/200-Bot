import DBA
import re
from helpers.senders import send_raw_to_debug_channel
from typing import TYPE_CHECKING

from helpers.senders.send_raw_to_debug_channel import send_raw_to_debug_channel

if TYPE_CHECKING:
    from discord import Bot


async def update_friend_code(client: Bot, player_id: int, provided_fc: str) -> str:
    """Updates the issuers friend code in the database
    Returns:
        User feedback"""
    fc_pattern = r"\d\d\d\d-?\d\d\d\d-?\d\d\d\d"
    if re.search(fc_pattern, provided_fc):
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "UPDATE player SET fc = %s WHERE player_id = %s;",
                    (provided_fc, player_id),  # type: ignore
                )
                return f"Friend Code updated to {provided_fc}"
        except Exception as e:
            await send_raw_to_debug_channel(client, "update_friend_code error 1", e)
            return "``Error 15:`` Player not found"
    else:
        return "Invalid fc. Use ``/fc XXXX-XXXX-XXXX``"
