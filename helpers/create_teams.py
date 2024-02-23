import DBA
import random
import logging
import math
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_tier_from_room_range

# poll_results is [index of the voted on format, a dictionary of format:voters]
# creates teams, finds host, returns a big string formatted...
async def create_teams(client, player_list, winning_format, average_mmr, min_mmr, max_mmr, channel_name):
    """Shuffles players into teams. Returns the response to send to the room, and the response to send to the list"""
    players_per_team = winning_format
    winning_format_string = f'### Winner: {winning_format}\n\n'
    
    players_list = list()
    for player in player_list:
        try:
            with DBA.DBAccess() as db:
                player_db = db.query('SELECT player_name, player_id, mmr FROM player WHERE player_id = %s;', (player,))
                players_list.append([player_db[0][0], player_db[0][1], player_db[0][2]])
        except Exception as e:
            logging.warning(f'create_teams error: {e}')
            return

    _, room_tier_name = await get_tier_from_room_range(min_mmr, max_mmr)
    random.shuffle(players_list) # [[popuko, 7238965417831, 4000],[name, discord id, mmr]]
    response_string = f'`{channel_name}` MMR: {math.ceil(average_mmr)} - tier-{room_tier_name}\n'

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
    player_score_string = f'**Table:** `/table {players_per_team}` '
    team_count = 0
    for team in sorted_list:
        team_count+=1
        response_string += f'**Team {team_count}:** '
        for player in team:
            try:
                player_score_string += f'{player[0]} 0 '
                response_string += f'{player[0]} '
            except TypeError:
                response_string += f'(MMR: {math.ceil(player)})\n'
    list_response_string = response_string
    response_string+=f'\n{player_score_string}'
    
    # choose a host
    host_string = '    '
    try:
        with DBA.DBAccess() as db:
            host_temp = db.query('SELECT fc, player_id FROM player WHERE fc IS NOT NULL AND is_host_banned = 0 AND player_id IN %s;', (player_list,))
            host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
    except Exception:
        host_string = '`No FC found` - Choose amongst yourselves'
    # create a return string
    response_string+=f'\n\n{host_string}'
    return winning_format_string+response_string, list_response_string
