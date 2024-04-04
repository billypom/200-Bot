import DBA
import re
from helpers.senders import send_to_debug_channel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot
    from discord.ext.commands import Context


async def update_friend_code(client: Bot, ctx: Context, provided_fc: str) -> str:
    """Updates the issuers friend code in the database
    Returns:
        User feedback"""
    fc_pattern = r"\d\d\d\d-?\d\d\d\d-?\d\d\d\d"
    if re.search(fc_pattern, provided_fc):
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "UPDATE player SET fc = %s WHERE player_id = %s;",
                    (provided_fc, ctx.author.id),  # type: ignore
                )
                return f"Friend Code updated to {provided_fc}"
        except Exception as e:
            await send_to_debug_channel(client, ctx, f"update_friend_code error 15 {e}")
            return "``Error 15:`` Player not found"
    else:
        return "Invalid fc. Use ``/fc XXXX-XXXX-XXXX``"
