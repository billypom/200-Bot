import DBA
from helpers.senders import send_raw_to_debug_channel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot


async def handle_team_placements_for_lorenzi_table(
    client: Bot,
    chunked_list: list,
) -> tuple[bool, str, int, dict]:
    """Parses the chunked list, determines scores and placements for each team, handles some user input errors...

    Returns:
    data_is_valid: bool, error_message: str, mogi_score: int, original_scores: dict"""
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
            original_scores[player_id] = player_score
            try:
                with DBA.DBAccess() as db:
                    retrieved_mmr = int(
                        db.query(
                            "SELECT mmr FROM player WHERE player_id = %s;",
                            (player_id,),
                        )[0][0]  # type: ignore
                    )
                if retrieved_mmr is None:
                    mmr = 0
                    count += 1  # added this line 10/10/22 because placement players ppl are mad grrr i need my mmr
                else:
                    mmr = retrieved_mmr
                    count += 1
                temp_mmr += mmr
                try:
                    team_score += int(player_score)
                except Exception:
                    # Split the string into sub strings with scores and operations
                    # Do calculation + -
                    current_group = ""
                    sign = ""
                    points = 0
                    for idx, char in enumerate(str(player_score)):
                        print(f"/table | parsing char: {char}")
                        if char.isdigit():
                            current_group += char
                            print(
                                f"/table | parsing char: {char} | IS DIGIT, current_group = {current_group}"
                            )
                        elif char == "-" or char == "+":
                            print(
                                f"/table | parsing char: {char} | IS - or +, current_group = {current_group}"
                            )
                            points += int(f"{sign}{current_group}")
                            sign = char
                            print(f"/table | player: {player} | points: {points}")
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
                    player_score = points
                    team_score = team_score + points
            except Exception as e:
                # check for all 12 players exist
                await send_raw_to_debug_channel(client, "/table Error 24", e)
                return (
                    False,
                    f"``Error 24:`` There was an error with the following player: <@{player_id}>",
                    0,
                    {},
                )
        # print(team_score)
        if count == 0:
            count = 1
        team_mmr = temp_mmr / count  # COUNT AS DIVISOR TO DETERMINE AVG/TEAM MMR
        team.append(team_score)
        team.append(team_mmr)
        mogi_score += team_score
    return True, "OK", mogi_score, original_scores
