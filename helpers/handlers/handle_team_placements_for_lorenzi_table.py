import DBA
import logging
from helpers.senders import send_raw_to_debug_channel


async def handle_team_placements_for_lorenzi_table(
    chunked_list: list,
) -> tuple[bool, str, int, dict]:
    """- Alters `chunked_list` in place, appends team score and team MMR to the team record
    - Saves individual player scores to a dict

    Args:
    - `chunked_list`: list - [[player, score], [player2, score], next team...]

    Returns:
    tuple[bool, str, int, dict]:
    - `data_is_valid`: bool - self explanatory
    - `error_message`: str - error message if something goes wrong
    - `mogi_score`: int - total points in mogi
    - `original_scores`: dict - individual {player_id: score} dict
    """
    # Get MMR data for each team, calculate team score, and determine team placement
    mogi_score = 0
    # Preserve the original score formatting for Lorenzi table
    original_scores = {}
    for team in chunked_list:  # type: ignore
        # chunked_list should ALWAYS be a list if we get to this point
        temp_mmr, team_score, count = 0, 0, 0
        for player in team:
            player_id = player[0]
            player_score = player[1]
            try:  # get mmr, else 0
                with DBA.DBAccess() as db:
                    retrieved_mmr = int(
                        db.query(
                            "SELECT mmr FROM player WHERE player_id = %s;",
                            (player_id,),
                        )[0][0]  # type: ignore
                    )
                    mmr = retrieved_mmr
                    count += 1
                    temp_mmr += mmr
            except TypeError:
                mmr = 0
                count += 1  # added this line 10/10/22 because placement players ppl are mad grrr i need my mmr
            try:  # accumulate team scores
                team_score += int(player_score)
                original_scores[player_id] = int(player_score)
            except Exception:
                # Split the string into sub strings with scores and operations
                # Do calculation + -
                current_group = ""
                sign = ""
                points = 0
                for idx, char in enumerate(str(player_score)):
                    # logging.warning(f"/table | parsing char: {char}")
                    if char.isdigit():
                        current_group += char
                        # logging.warning(
                        #     f"/table | parsing char: {char} | IS DIGIT, current_group = {current_group}"
                        # )
                    elif char == "-" or char == "+":
                        # logging.warning(
                        #     f"/table | parsing char: {char} | IS - or +, current_group = {current_group}"
                        # )
                        points += int(f"{sign}{current_group}")
                        sign = char
                        # logging.warning(f"/table | player: {player} | points: {points}")
                        current_group = ""
                    else:
                        return (
                            False,
                            f"``Error 26:``There was an error with the following player: <@{player_id}>",
                            0,
                            {},
                        )
                # Last item in list needs to be added
                points += int(f"{sign}{current_group}")
                if sign == "-":
                    mogi_score += int(current_group)
                # Make sure to assign the calculated score to
                # the player in original scores
                original_scores[player_id] = points
                team_score = team_score + points
        if count == 0:
            count = 1
        team_mmr = temp_mmr / count  # COUNT AS DIVISOR TO DETERMINE AVG/TEAM MMR
        team.append(team_score)
        team.append(team_mmr)
        mogi_score += team_score
    return True, "OK", mogi_score, original_scores
