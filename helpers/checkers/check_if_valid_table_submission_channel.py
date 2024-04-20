import DBA
import logging
from helpers.getters import (
    get_tier_id_list,
    get_results_id_list,
)


async def check_if_valid_table_submission_channel(
    channel_id: int, category_id: int
) -> bool:
    """Checks if the current channel is a valid mogi tier.

    Depends on SQ bot to add each open category to the database

    Returns:
    True or False
    """
    tier_id_list = await get_tier_id_list()
    results_id_list = await get_results_id_list()

    if channel_id in tier_id_list:
        # Tier channel submission
        return True
    if channel_id in results_id_list:
        # Results channel submission
        return True
    try:
        # SQ any channel within valid category submission
        with DBA.DBAccess() as db:
            retrieved_category_id = db.query(
                "SELECT category_id FROM sq_helper WHERE category_id = %s;",
                (category_id,),
            )[0][0]  # type: ignore
            if category_id == retrieved_category_id:
                return True
            else:
                return False
    except Exception as e:
        logging.warning(f"ERROR in check_if_valid_table_submission_channel | {e}")
        return False
