import DBA


async def handle_score_input(client, ctx, score_string: str, mogi_format: int):
    """Handles format and scores input from /table command

    Returns a list of lists of lists where the inner list is [player_id, score]
    the middle list is each team, with each player [[player_id, score], [player_id2, score2]]
    and the outer list is a list of teams

    On invalid input, returns False"""
    # Split into list
    score_list = score_string.split()
    if len(score_list) != 24:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`WRONG AMOUNT OF INPUTS:` {len(score_list)}')
        return False
    # Make sure every player in the list exists
    try:
        for i in range(0, len(score_list), 2): # Checks every value from idx = 0, incrementing by 2 (0,2,4,6,etc)
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (score_list[i],))
                score_list[i] = temp[0][0] # Replace player_names with player_ids
    except Exception:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`PLAYER DOES NOT EXIST:` {score_list[i]}')
        return False
    player_score_chunked_list = []
    for i in range(0, len(score_list), 2):
        player_score_chunked_list.append(score_list[i:i+2])
    # Chunk the list into groups of teams, based on mogi_format and order of scores entry
    chunked_list = []
    for i in range(0, len(player_score_chunked_list), mogi_format):
        chunked_list.append(player_score_chunked_list[i:i+mogi_format])
    return chunked_list
