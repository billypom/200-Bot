from config import SQ_HELPER_CHANNEL_ID, CATEGORIES_MESSAGE_ID, SQUAD_QUEUE_CHANNEL_ID
from helpers.getters import (
    get_tier_id_list,
    get_results_id_list,
    get_lounge_queue_channel_id_list,
    get_results_tier_dict,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Bot, CategoryChannel
    from discord.interactions import InteractionChannel


async def check_if_valid_table_submission_channel(
    client: Bot, channel: InteractionChannel, category: CategoryChannel
) -> tuple[bool, bool, int, str]:
    """Checks if the current channel is a valid mogi tier.

    Returns:
    On success: [is_valid: True, is_lounge_queue: Bool, tier_id_to_use: int, tier_name: str]
    On failure: [is_valid: False, is_lounge_queue: Bool, tier_id_to_use: 0, tier_name: '']"""
    is_lounge_queue = False
    room_tier_name = ""
    tier_id_list = await get_tier_id_list()
    results_id_list = await get_results_id_list()
    lounge_queue_channel_id_list = await get_lounge_queue_channel_id_list()
    valid_channel_ids = tier_id_list + lounge_queue_channel_id_list + results_id_list

    if channel.id in valid_channel_ids:
        nya_tier_id = channel.id
        if nya_tier_id in lounge_queue_channel_id_list:  # Lounge Queue
            is_lounge_queue = True
        else:  # Turns results channel into tier channel
            results_tier_dict = await get_results_tier_dict()
            for key, value in results_tier_dict.items():  # type: ignore
                if value == nya_tier_id:
                    nya_tier_id = key
    else:  # Squad queue
        # Retrieve SQ Tier ID from categories helper
        # A debug message is posted by the bot in #sq-helper
        # The category is validated here to allow submitting tables
        # from all SQ room channels
        sq_helper_channel = client.get_channel(SQ_HELPER_CHANNEL_ID)
        sq_helper_message = await sq_helper_channel.fetch_message(CATEGORIES_MESSAGE_ID)  # type: ignore
        if str(category.id) in sq_helper_message.content:
            nya_tier_id = SQUAD_QUEUE_CHANNEL_ID
            room_tier_name = "sq"
        else:
            return False, is_lounge_queue, 0, room_tier_name
    return True, is_lounge_queue, nya_tier_id, room_tier_name
