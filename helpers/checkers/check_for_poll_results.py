# UNUSED

import DBA
import random
from helpers.getters import get_unix_time_now
from config import MAX_PLAYERS_IN_MOGI


# When the voting starts - constantly check for player input
async def check_for_poll_results(channel_id: int, last_joiner_unix_timestamp: int):
    unix_now = await get_unix_time_now()
    format_list = [0, 0, 0, 0, 0]
    while (unix_now - last_joiner_unix_timestamp) < 120:
        # Votes are updated in the on_message event, if mogi is running and player is in tier
        # await asyncio.sleep(0.5)
        with DBA.DBAccess() as db:
            ffa_temp = db.query(
                "SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;",
                (channel_id, 1),
            )
            format_list[0] = ffa_temp[0][0]
        with DBA.DBAccess() as db:
            v2_temp = db.query(
                "SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;",
                (channel_id, 2),
            )
            format_list[1] = v2_temp[0][0]
        with DBA.DBAccess() as db:
            v3_temp = db.query(
                "SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;",
                (channel_id, 3),
            )
            format_list[2] = v3_temp[0][0]
        with DBA.DBAccess() as db:
            v4_temp = db.query(
                "SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;",
                (channel_id, 4),
            )
            format_list[3] = v4_temp[0][0]
        with DBA.DBAccess() as db:
            v6_temp = db.query(
                "SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;",
                (channel_id, 6),
            )
            format_list[4] = v6_temp[0][0]
        if 6 in format_list:
            break
        # print(f'{unix_now} - {last_joiner_unix_timestamp}')
        unix_now = get_unix_time_now()
    # print('checking for all zero votes')
    # print(f'format list: {format_list}')
    if all([v == 0 for v in format_list]):
        return [0, {"0": 0}]  # If all zeros, return 0. cancel mogi
    # Close the voting
    # print('closing the voting')
    with DBA.DBAccess() as db:
        db.execute("UPDATE tier SET voting = %s WHERE tier_id = %s;", (0, channel_id))
    if format_list[0] == 6:
        ind = 0
    elif format_list[1] == 6:
        ind = 1
    elif format_list[2] == 6:
        ind = 2
    elif format_list[3] == 6:
        ind = 3
    elif format_list[4] == 6:
        ind = 4
    else:
        # Get the index of the voted on format
        max_val = max(format_list)
        ind = [i for i, v in enumerate(format_list) if v == max_val]

    # Create a dictionary where key=format, value=list of players who voted
    poll_dictionary = {
        "FFA": [],
        "2v2": [],
        "3v3": [],
        "4v4": [],
        "6v6": [],
    }
    with DBA.DBAccess() as db:
        votes_temp = db.query(
            "SELECT l.vote, p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;",
            (channel_id, MAX_PLAYERS_IN_MOGI),
        )
    for i in range(len(votes_temp)):
        # print(f'votes temp: {votes_temp}')
        if votes_temp[i][0] == 1:
            player_format_choice = "FFA"
        elif votes_temp[i][0] == 2:
            player_format_choice = "2v2"
        elif votes_temp[i][0] == 3:
            player_format_choice = "3v3"
        elif votes_temp[i][0] == 4:
            player_format_choice = "4v4"
        elif votes_temp[i][0] == 6:
            player_format_choice = "6v6"
        else:
            continue
        poll_dictionary[player_format_choice].append(votes_temp[i][1])
    # print('created poll dictionary')
    # print(f'{poll_dictionary}')
    # Clear votes after we dont need them anymore...
    # print('clearing votes...')
    with DBA.DBAccess() as db:
        db.execute("UPDATE lineups SET vote = NULL WHERE tier_id = %s;", (channel_id,))
    # I use random.choice to account for ties
    try:
        return [random.choice(ind), poll_dictionary]
    except TypeError:
        return [ind, poll_dictionary]
