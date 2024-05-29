from helpers import generate_random_name
from helpers.checkers import check_if_name_is_unique
import logging


async def get_random_name() -> str:
    """Returns a random name that is not taken in the database"""
    name_is_not_unique = True
    name = ""
    while name_is_not_unique:
        name = await generate_random_name()
        test = await check_if_name_is_unique(name)
        if test:
            name_is_not_unique = False
    return name
