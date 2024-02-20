import DBA
import re
from helpers.senders import send_to_debug_channel

# Takes a ctx & a string, returns a response
async def update_friend_code(client, ctx, message):
    fc_pattern = '\d\d\d\d-?\d\d\d\d-?\d\d\d\d'
    if re.search(fc_pattern, message):
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET fc = %s WHERE player_id = %s;', (message, ctx.author.id))
                return f'Friend Code updated to {message}'
        except Exception as e:
            await send_to_debug_channel(client, ctx, f'update_friend_code error 15 {e}')
            return '``Error 15:`` Player not found'
    else:
        return 'Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'
