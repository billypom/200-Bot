import DBA
import logging
from constants import SQUAD_QUEUE_CHANNEL_ID
from helpers.getters import get_results_tier_dict


async def get_tier_from_submission_channel(channel_id: int):
    """Returns tier_id  given a channel that /table was submitted from

    This is necessary because the channel that people submit
    a /table from is not always a tier channel"""
    # Submission from normal tier channel
    results_tier_dict = await get_results_tier_dict()
    for key, value in results_tier_dict.items():
        if channel_id == key:
            # channel_id = tier_id
            try:
                with DBA.DBAccess() as db:
                    tier_id = int(
                        db.query(
                            "SELECT tier_id FROM tier WHERE tier_id = %s;",
                            (channel_id,),
                        )[0][0]  # type: ignore
                    )
                    return tier_id
            except Exception as e:
                logging.warning(f"ERROR in get_tier_from_submission_channel | {e}")
                return 0
        elif channel_id == value:
            # channel_id = results_id
            try:
                with DBA.DBAccess() as db:
                    tier_id = int(
                        db.query(
                            "SELECT tier_id FROM tier WHERE results_id = %s;",
                            (channel_id,),
                        )[0][0]  # type: ignore
                    )
                    return tier_id
            except Exception as e:
                logging.warning(f"ERROR in get_tier_from_submission_channel | {e}")
                return 0
    # Submission from SQ channel
    # We can safely assume this is a SQ channel
    # because we run this function AFTER
    # running check_if_valid_tier_submission_channel
    return SQUAD_QUEUE_CHANNEL_ID
