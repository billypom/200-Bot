import DBA
from config import MAX_PLAYERS_IN_MOGI

async def check_if_mogi_is_ongoing(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception:
        return False
    if temp[0][0] >= MAX_PLAYERS_IN_MOGI:
        return True
    else:
        return False