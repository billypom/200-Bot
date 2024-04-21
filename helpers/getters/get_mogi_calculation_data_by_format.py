async def get_mogi_calculation_data_by_format(
    mogi_format: int,
) -> tuple[int, int, float, list[str]]:
    """Returns data to be used in MMR calculations & some colors for the Lorenzi tables based on the mogi format"""
    SPECIAL_TEAMS_INTEGER = 0
    OTHER_SPECIAL_INT = 0
    MULTIPLIER_SPECIAL = 0.0
    table_color = ["", ""]
    if mogi_format == 1:
        SPECIAL_TEAMS_INTEGER = 63
        OTHER_SPECIAL_INT = 19
        MULTIPLIER_SPECIAL = 2.1
        table_color = ["#76D7C4", "#A3E4D7"]
    elif mogi_format == 2:
        SPECIAL_TEAMS_INTEGER = 142
        OTHER_SPECIAL_INT = 39
        MULTIPLIER_SPECIAL = 3.0000001
        table_color = ["#76D7C4", "#A3E4D7"]
    elif mogi_format == 3:
        SPECIAL_TEAMS_INTEGER = 288
        OTHER_SPECIAL_INT = 59
        MULTIPLIER_SPECIAL = 3.1
        table_color = ["#85C1E9", "#AED6F1"]
    elif mogi_format == 4:
        SPECIAL_TEAMS_INTEGER = 402
        OTHER_SPECIAL_INT = 79
        MULTIPLIER_SPECIAL = 3.35
        table_color = ["#C39BD3", "#D2B4DE"]
    elif mogi_format == 6:
        SPECIAL_TEAMS_INTEGER = 525
        OTHER_SPECIAL_INT = 99
        MULTIPLIER_SPECIAL = 3.5
        table_color = ["#F1948A", "#F5B7B1"]
    return SPECIAL_TEAMS_INTEGER, OTHER_SPECIAL_INT, MULTIPLIER_SPECIAL, table_color
