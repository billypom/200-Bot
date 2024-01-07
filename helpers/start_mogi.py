import DBA
import datetime
from helpers.senders import send_to_debug_channel
from helpers.checkers import check_for_poll_results
from helpers import remove_players_from_other_tiers
from helpers import cancel_mogi
from helpers import create_teams
from config import PING_DEVELOPER, MAX_PLAYERS_IN_MOGI

# Takes a ctx, returns 0 if error, returns 1 if good, returns nothing if mogi cancelled
async def start_mogi(client, ctx):
    channel = client.get_channel(ctx.channel.id)
    removal_passed = await remove_players_from_other_tiers(client, ctx.channel.id)
    if removal_passed:
        pass
    else:
        await send_to_debug_channel(client, ctx, 'Failed to remove all players from other lineups...')
        return 0
    # Set the tier to the voting state
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET voting = 1 WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'start_mogi cannot start format vote | 1 | {e}')
        await channel.send(f'`Error 23:` Could not start the format vote. Contact the admins or {PING_DEVELOPER} immediately')
        return 0
    # Initialize the mogi timer, for mogilist checker minutes since start...
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET mogi_start_time = %s WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12;', (datetime.datetime.now(), ctx.channel.id))
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'start_mogi cannot start format vote | 4 | {e}')
        await channel.send(f'`Error 23.2:` Could not start the format vote. Contact the admins or {PING_DEVELOPER} immediately')
        return 0
    # Get the first 12 players
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'start_mogi cannot start format vote | 2 | {e}')
        await channel.send(f'`Error 22:` Could not start the format vote. Contact the admins or {PING_DEVELOPER} immediately')
        return 0
    # Set 12 players' state to "cannot drop"
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET can_drop = 0 WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'start_mogi cannot start format vote | 3 | {e}')
        await channel.send(f'`Error 55:` Could not start the format vote. Contact the admins or {PING_DEVELOPER} immediately')
        return 0
    response = ''
    for i in range(len(temp)):
        response = f'{response} <@{temp[i][0]}>'
    response = f'''{response} mogi has 12 players\n`Poll Started!`

    `1.` FFA
    `2.` 2v2
    `3.` 3v3
    `4.` 4v4
    `6.` 6v6

    Type a number to vote!
    Poll ends in 2 minutes or when a format reaches 6 votes.'''
    await channel.send(response)
    with DBA.DBAccess() as db:
        unix_temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    # returns the index of the voted on format, and a dictionary of format:voters
    poll_results = await check_for_poll_results(ctx, unix_temp[MAX_PLAYERS_IN_MOGI-1][0])
    if poll_results[0] == -1:
        # Cancel Mogi
        await channel.send('No votes. Mogi will be cancelled.')
        await cancel_mogi(ctx)
        return 2
        
    teams_results = await create_teams(ctx, poll_results)

    ffa_voters = list()
    v2_voters = list()
    v3_voters = list()
    v4_voters = list()
    v6_voters = list()
    # create formatted message
    for player in poll_results[1]['FFA']:
        ffa_voters.append(player)
    for player in poll_results[1]['2v2']:
        v2_voters.append(player)
    for player in poll_results[1]['3v3']:
        v3_voters.append(player)
    for player in poll_results[1]['4v4']:
        v4_voters.append(player)
    for player in poll_results[1]['6v6']:
        v6_voters.append(player)
    remove_chars = {
        39:None,
        91:None,
        93:None,
    }
    poll_results_response = f'''`Poll Ended!`

    `1.` FFA - {len(ffa_voters)} ({str(ffa_voters).translate(remove_chars)})
    `2.` 2v2 - {len(v2_voters)} ({str(v2_voters).translate(remove_chars)})
    `3.` 3v3 - {len(v3_voters)} ({str(v3_voters).translate(remove_chars)})
    `4.` 4v4 - {len(v4_voters)} ({str(v4_voters).translate(remove_chars)})
    `6.` 6v6 - {len(v6_voters)} ({str(v6_voters).translate(remove_chars)})
    {teams_results}
    '''
    await channel.send(poll_results_response)
    return 1
