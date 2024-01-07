import DBA
from helpers.senders import send_raw_to_debug_channel

async def remove_players_from_other_tiers(client, channel_id):
    await send_raw_to_debug_channel(client, 'Removing players from other tiers...', channel_id)
    try:
        with DBA.DBAccess() as db:
            players = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC;', (channel_id,))
    except Exception as e:
        await send_raw_to_debug_channel(client, 'No players to remove from other tiers?', e)
        return True
    for player in players:
        with DBA.DBAccess() as db:
            player_tier = db.query('SELECT p.player_id, p.player_name, l.tier_id FROM lineups as l JOIN player as p ON l.player_id = p.player_id WHERE p.player_id = %s AND l.tier_id <> %s;', (player[0], channel_id))
        for tier in player_tier:
            await send_raw_to_debug_channel(client, 'Removing from other tiers', f'{tier[1]} - {tier[2]}')
            channel = client.get_channel(tier[2])
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (tier[0], tier[2]))
            await channel.send(f'{tier[1]} has dropped from the lineup')
    return True