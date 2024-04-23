import logging
import math


async def calculate_mmr(sorted_list, value_table):
    # Actually calculate the MMR
    logging.info("POP_LOG | Calculating MMR")
    for idx, team in enumerate(sorted_list):
        temp_value = 0.0
        for pre_mmr_list in value_table:
            for idx2, value in enumerate(pre_mmr_list):
                if idx == idx2:
                    temp_value += value
                else:
                    pass
        team.append(math.floor(temp_value.real))
