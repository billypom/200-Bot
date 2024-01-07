# helpers/wrappers/new_rank.py

# https://imagemagick.org/script/color.php

from helpers import wrappers

# Input: (str, int mmr)
#   Determines color of input text, based on mmr value
# Output: <span> tag
#   See implementation in functions below
async def new_rank(input, mmr):
    if input:
        if mmr < 1500:
            return await wrappers.iron(input)
        elif mmr >= 1500 and mmr < 3000:
            return await wrappers.bronze(input)
        elif mmr >= 3000 and mmr < 4500:
            return await wrappers.silver(input)
        elif mmr >= 4500 and mmr < 6000:
            return await wrappers.gold(input)
        elif mmr >= 6000 and mmr < 7500:
            return await wrappers.platinum(input)
        elif mmr >= 7500 and mmr < 9000:
            return await wrappers.diamond(input)
        elif mmr >= 9000 and mmr < 11000:
            return await wrappers.master(input)
        elif mmr >= 11000:
            return await wrappers.grandmaster(input)
        else:
            return input
    else:
        return input