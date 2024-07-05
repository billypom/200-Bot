import DBA
import logging
from helpers.getters import (
    get_results_id_list,
)


async def check_if_is_results_channel(channel_id: int) -> bool:
    """Checks if the current channel is a valid results channel

    Returns:
    True or False
    """
    results_id_list = await get_results_id_list()

    if channel_id in results_id_list:
        # Results channel submission
        return True
    return False
