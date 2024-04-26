import DBA


async def create_lorenzi_query(
    sorted_list: list, original_scores: dict, mogi_format: int, table_color: list
) -> str:
    """Creates a string to be sent to the lorenzi API for mogi table
    ALTERS THE SORTED LIST IN PLACE - adds team placement

    Params:
    - Sorted list of Teams[Player, score]s
    - Original scores as a dict {player_id: score}
    - Mogi format
    - Table colors list [primary, secondary]

    Returns:
    - a string to be passed to gb.hlorenzi table maker"""
    if mogi_format == 1:
        lorenzi_query = "-\n"
    else:
        lorenzi_query = ""
    # Initialize score and placement values
    prev_team_score = 0
    prev_team_placement = 1
    team_placement = 0
    count_teams = 1
    for team in sorted_list:
        # If team score = prev team score, use prev team placement, else increase placement and use placement
        if team[len(team) - 2] == prev_team_score:
            team_placement = prev_team_placement
        else:
            team_placement = count_teams
        count_teams += 1
        team.append(team_placement)
        if mogi_format != 1:
            if count_teams % 2 == 0:
                lorenzi_query += f"{team_placement} {table_color[0]} \n"
            else:
                lorenzi_query += f"{team_placement} {table_color[1]} \n"
        for idx, player in enumerate(team):
            if idx > (mogi_format - 1):
                continue
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT player_name, country_code FROM player WHERE player_id = %s;",
                    (player[0],),
                )
                player_name = temp[0][0]  # type: ignore
                country_code = temp[0][1]  # type: ignore
            lorenzi_query += (
                f"{player_name} [{country_code}] {original_scores[player[0]]}\n"
            )
        # Assign previous values before looping
        prev_team_placement = team_placement
        prev_team_score = team[len(team) - 3]
    return lorenzi_query
