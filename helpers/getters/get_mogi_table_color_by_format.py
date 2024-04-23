async def get_mogi_table_color_by_format(
    mogi_format: int,
) -> list[str]:
    """Returns data to be used in MMR calculations & some colors for the Lorenzi tables based on the mogi format"""
    if mogi_format == 1:
        table_color = ["#76D7C4", "#A3E4D7"]
    elif mogi_format == 2:
        table_color = ["#76D7C4", "#A3E4D7"]
    elif mogi_format == 3:
        table_color = ["#85C1E9", "#AED6F1"]
    elif mogi_format == 4:
        table_color = ["#C39BD3", "#D2B4DE"]
    elif mogi_format == 6:
        table_color = ["#F1948A", "#F5B7B1"]
    else:
        return [None, None]
    return table_color
