import DBA
# Input: ctx, str players&scores, int format
# Output: nicely formatted dict-type list thingie...
async def handle_score_input(client, ctx, score_string, mogi_format):
    # Split into list
    score_list = score_string.split()
    if len(score_list) == 24:
        pass
    else:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`WRONG AMOUNT OF INPUTS:` {len(score_list)}')
        return False
    # Check for player db match
    try:
        for i in range(0, len(score_list), 2):
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (score_list[i],))
                # Replace playernames with playerids
                score_list[i] = temp[0][0]
    except Exception:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`PLAYER DOES NOT EXIST:` {score_list[i]}')
        return False
    
    player_score_chunked_list = []
    for i in range(0, len(score_list), 2):
        player_score_chunked_list.append(score_list[i:i+2])
        # print(player_score_chunked_list)


    # Chunk the list into groups of teams, based on mogi_format and order of scores entry
    chunked_list = []
    for i in range(0, len(player_score_chunked_list), mogi_format):
        chunked_list.append(player_score_chunked_list[i:i+mogi_format])
    return chunked_list