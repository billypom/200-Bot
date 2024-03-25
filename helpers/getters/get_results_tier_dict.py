import DBA
import logging
from helpers.getters import get_tier_id_list
import asyncio

async def get_results_tier_dict() -> dict:
    """Returns a dictionary of {tier_id: results_id} from the DB tier table"""
    tier_ids = await get_tier_id_list()
    my_dict = {}
    for tier in tier_ids:
        try:
            with DBA.DBAccess() as db:
                my_dict[tier] = db.query('SELECT results_id FROM tier WHERE tier_id = %s;', (tier,))[0][0]
        except Exception as e:
            logging.warning(f'get_results_tier_dict | could not find tier {tier} | {e}')
            return False
    return my_dict

