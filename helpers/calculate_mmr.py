import logging
import math


async def calculate_mmr(sorted_list: list, value_table: list) -> None:
    """Alters the sorted list in place, based on the MMR value table
    a
    Adds the mmr delta to the sorted list"""
    # Actually calculate the MMR
    for idx, team in enumerate(sorted_list):
        temp_value = 0.0
        for pre_mmr_list in value_table:
            for idx2, value in enumerate(pre_mmr_list):
                if idx == idx2:
                    temp_value += value
                else:
                    pass
        team.append(math.floor(temp_value.real))
