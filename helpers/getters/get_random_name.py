from helpers import generate_random_name
from helpers.checkers import check_if_name_is_unique
import logging
# Returns a random player name that is not taken
async def get_random_name() -> str:
    logging.info('POP_LOG | Retrieving random name...')
    name_is_not_unique = True
    while(name_is_not_unique):
        name = await generate_random_name()
        logging.info(f'POP_LOG | Generated name: {name}')
        test = await check_if_name_is_unique(name)
        if (test):
            logging.info('POP_LOG | Unique name detected')
            name_is_not_unique = False
    return name