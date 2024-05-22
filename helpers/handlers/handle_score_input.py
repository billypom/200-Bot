import DBA
from collections import Counter


async def handle_score_input(score_string: str, mogi_format: int) -> list:
    """Handles format and scores input from /table command

    Returns a list of lists of lists where the inner list is [player_id, score]
    the middle list is each team, with each player [[player_id, score], [player_id2, score2]]
    and the outer list is a list of all teams (where each team has some list of players)
    i.e. [[[player_id, score], [player_id, score]], [[player_id, score], [player_id, score]]]
    list[0] would be a list all of team 1's players and scores
    list[0][0] would be team 1's 1st player
    list[0][0][0] woudld be team 1's 1st player's ID

    On invalid input, returns an error message in a string at list[0]"""
    # Split into list
    score_list = score_string.split()
    if len(score_list) != 24:
        return [f"`WRONG AMOUNT OF INPUTS:` {len(score_list)}"]
    # Make sure every player in the list is unique
    players_in_list = []
    for i in range(0, len(score_list), 2):
        players_in_list.append(score_list[i])
    duplicates = [k for k,v in Counter(players_in_list).items() if v > 1]
    if duplicates:
        translation = {39: None}
        return [f"Each player must be unique. Duplicate players: \n```{str(duplicates).replace('[', '').replace(']', '').translate(translation)}```"]
    # Make sure every player in the list exists
    for i in range(0, len(score_list), 2):
        try:
            # Checks every value from idx = 0, incrementing by 2 (0,2,4,6,etc)
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;",
                    (score_list[i],),
                )
                # Replace player_name with player_id
                score_list[i] = temp[0][0]  # type: ignore
        except Exception:
            # {i} will never be unbound because the list MUST be 24 in length
            return [f"`PLAYER DOES NOT EXIST:` {score_list[i]}"]
    player_score_chunked_list = []
    for i in range(0, len(score_list), 2):
        player_score_chunked_list.append(score_list[i : i + 2])
    # Chunk the list into groups of teams, based on mogi_format and order of scores entry
    chunked_list = []
    for i in range(0, len(player_score_chunked_list), mogi_format):
        chunked_list.append(player_score_chunked_list[i : i + mogi_format])
    return chunked_list
