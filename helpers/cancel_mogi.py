import DBA
from config import MAX_PLAYERS_IN_MOGI
from helpers.senders import send_to_debug_channel

async def cancel_mogi(client, ctx):
    # Delete player records for first 12 in lineups table
    try:
        with DBA.DBAccess() as db:
            db.execute('DELETE FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
        return True
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'cancel_mogi error| {e}')
        return False