async def calculate_pre_mmr(
    sorted_list: list,
) -> list:
    """does some stuff on the table of players

    returns a table of values"""
    if mogi_format == 1:
        SPECIAL_TEAMS_INTEGER = 63
        OTHER_SPECIAL_INT = 19
        MULTIPLIER_SPECIAL = 2.1
    elif mogi_format == 2:
        SPECIAL_TEAMS_INTEGER = 142
        OTHER_SPECIAL_INT = 39
        MULTIPLIER_SPECIAL = 3.0000001
    elif mogi_format == 3:
        SPECIAL_TEAMS_INTEGER = 288
        OTHER_SPECIAL_INT = 59
        MULTIPLIER_SPECIAL = 3.1
    elif mogi_format == 4:
        SPECIAL_TEAMS_INTEGER = 402
        OTHER_SPECIAL_INT = 79
        MULTIPLIER_SPECIAL = 3.35
    elif mogi_format == 6:
        SPECIAL_TEAMS_INTEGER = 525
        OTHER_SPECIAL_INT = 99
        MULTIPLIER_SPECIAL = 3.5
    # Get the highest MMR ever
    # There was a very high integer in the formula for
    #   calculating mmr on the original google sheet (9998)
    # A comment about how people "never thought anyone could reach 10k mmr"
    #   made me think this very high integer was a replacement for getting
    #   the highest existing mmr (or at least my formula could emulate that high integer
    #   with some variance :shrug: its probably fine... no1 going 2 read this)

    # Getting the highest mmr made it so the highest ranked players
    #   could endlessly climb somewhat linearly, so i removed that.
    # 10999 works very well
    highest_mmr = 10999
    value_table = list()
    for idx, team_x in enumerate(sorted_list):
        working_list = list()
        for idy, team_y in enumerate(sorted_list):
            pre_mmr = 0.0
            if idx == idy:  # skip value vs. self
                pass
            else:
                team_x_mmr = team_x[len(team_x) - 2]
                team_x_placement = team_x[len(team_x) - 1]
                team_y_mmr = team_y[len(team_y) - 2]
                team_y_placement = team_y[len(team_y) - 1]
                if team_x_placement == team_y_placement:
                    pre_mmr = (
                        SPECIAL_TEAMS_INTEGER
                        * ((((team_x_mmr - team_y_mmr) / highest_mmr) ** 2) ** (1 / 3))
                        ** 2
                    )
                    if team_x_mmr >= team_y_mmr:
                        pass
                    else:  # team_x_mmr < team_y_mmr:
                        pre_mmr = pre_mmr * -1
                else:
                    if team_x_placement > team_y_placement:
                        pre_mmr = (
                            1
                            + OTHER_SPECIAL_INT
                            * (1 + (team_x_mmr - team_y_mmr) / highest_mmr)
                            ** MULTIPLIER_SPECIAL
                        )
                    else:  # team_x_placement < team_y_placement
                        pre_mmr = -(
                            1
                            + OTHER_SPECIAL_INT
                            * (1 + (team_y_mmr - team_x_mmr) / highest_mmr)
                            ** MULTIPLIER_SPECIAL
                        )
            working_list.append(pre_mmr)
        value_table.append(working_list)
    return value_table
