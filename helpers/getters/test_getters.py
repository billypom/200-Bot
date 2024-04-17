import pytest
import config
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# import config
from helpers.getters import get_results_tier_dict
from helpers.getters import get_tier_id_list
from helpers.getters import get_discord_role
from helpers.getters import get_next_match_time


@pytest.mark.asyncio
async def test_get_tier_id_list():
    result = await get_tier_id_list()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_results_tier_dict():
    result = await get_results_tier_dict()
    assert isinstance(result, dict)


# @pytest.mark.asyncio
# async def test_get_next_match_time():
#     current_time = datetime(2000, 1, 1, 0, 0)
#     lounge_queue_start_minute = config.LOUNGE_QUEUE_START_MINUTE
#     with patch(datetime.strftime()) as mock_datetime:
#         mock_datetime.now.return_value = current_time
#         mock_datetime.timedelta = timedelta
#         with patch("config.LOUNGE_QUEUE_START_MINUTE", new=lounge_queue_start_minute):
#             next_match_timestamp = await get_next_match_time()
