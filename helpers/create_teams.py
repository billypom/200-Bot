import DBA
import random
import math
from config import MAX_PLAYERS_IN_MOGI
from helpers.senders import send_to_debug_channel

# poll_results is [index of the voted on format, a dictionary of format:voters]
# creates teams, finds host, returns a big string formatted...
async def create_teams(client, ctx, poll_results):
    # print('creating teams')
    keys_list = list(poll_results[1])
    winning_format = keys_list[poll_results[0]]
    # print(f'winning format: {winning_format}')
    players_per_team = 0
    if winning_format == 'FFA':
        players_per_team = 1
    elif winning_format == '2v2':
        players_per_team = 2
    elif winning_format == '3v3':
        players_per_team = 3
    elif winning_format == '4v4':
        players_per_team = 4
    elif winning_format == '6v6':
        players_per_team = 6
    else:
        return 0
    response_string=f'`Winner:` {winning_format}\n\n'
    with DBA.DBAccess() as db:
        player_db = db.query('SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    players_list = list()
    room_mmr = 0
    for i in range(len(player_db)):
        players_list.append([player_db[i][0], player_db[i][1], player_db[i][2]])
        if player_db[i][2] is None: # Account for placement ppls
            pass
        else:
            room_mmr = room_mmr + player_db[i][2]
    random.shuffle(players_list) # [[popuko, 7238965417831, 4000],[name, discord id, mmr]]
    room_mmr = room_mmr/MAX_PLAYERS_IN_MOGI
    response_string += f'   `Room MMR:` {math.ceil(room_mmr)}\n'
    # 6v6 /teams string
    if players_per_team != 6:
        # divide the list based on players_per_team
        chunked_list = list()
        for i in range(0, len(players_list), players_per_team):
            chunked_list.append(players_list[i:i+players_per_team])

        # For each divided team, get mmr for all players, average them, append to team
        for team in chunked_list:
            temp_mmr = 0
            count = 0
            for player in team:
                if player[2] is None: # If mmr is null - Account for placement ppls
                    count+=1
                    #pass - commented out and added count+=1 10/10/22 because people mad about playing with placements even tho its 200 and its tier all lol
                else:
                    temp_mmr = temp_mmr + player[2]
                    count += 1
            if count == 0:
                count = 1
            team_mmr = temp_mmr/count
            team.append(team_mmr)

        sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-1]))
        sorted_list.reverse()
        # print(sorted_list)
        player_score_string = f'    `Table:` /table {players_per_team} '
        team_count = 0
        for team in sorted_list:
            team_count+=1
            response_string += f'   `Team {team_count}:` '
            for player in team:
                try:
                    player_score_string += f'{player[0]} 0 '
                    response_string += f'{player[0]} '
                except TypeError:
                    response_string += f'(MMR: {math.ceil(player)})\n'

        response_string+=f'\n{player_score_string}'
    else:
        with DBA.DBAccess() as db:
            captains = db.query('SELECT player_name, player_id FROM (SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s) as mytable ORDER BY mmr DESC LIMIT 2;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
        response_string += f'   `Captains:` <@{captains[0][1]}> & <@{captains[1][1]}>\n'
        response_string += '   `Table:` /table 6 `[Team 1 players & scores]` `[Team 2 players & scores]`\n'
    
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (response_string, ctx.channel.id))
    except Exception as e:
        await send_to_debug_channel(client, ctx, f'team generation error log 1? | {e}')
    # choose a host
    host_string = '    '
    try:
        with DBA.DBAccess() as db:
            host_temp = db.query('SELECT fc, player_id FROM (SELECT p.fc, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s AND p.fc IS NOT NULL AND p.is_host_banned = %s ORDER BY l.create_date LIMIT %s) as fcs_in_mogi ORDER BY RAND() LIMIT 1;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
            host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
    except Exception:
        host_string = '    `No FC found` - Choose amongst yourselves'
    # create a return string
    response_string+=f'\n\n{host_string}'
    return response_string