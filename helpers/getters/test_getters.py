import pytest
import config
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# import config
from helpers.getters import (
    get_discord_role,
    get_lounge_guild,
    get_mogi_calculation_data_by_format,
    get_next_match_time,
    get_number_of_strikes_for_uid,
    get_partner_avg,
    get_random_name,
    get_rank_id_list,
    get_results_id_list,
    get_results_tier_dict,
    get_tier_from_submission_channel,
    get_tier_id_list,
    get_unix_time_now,
)

@pytest.mark.asyncio
async def test_get_discord_role():
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_get_lounge_guild():
    # impossible to test
    pass

@pytest.mark.asyncio
async def test_get_mogi_calculation_data_by_format():
    for i in range(1, 6):
        a, b, c, d = await get_mogi_calculation_data_by_format(i)
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, float)
        assert isinstance(d, list)
    # only 1st return value is used in /table to determine
    # if output is valid
    a, b, c, d, = await get_mogi_calculation_data_by_format(-1)
    assert a == 0


@pytest.mark.asyncio
async def test_get_number_of_strikes_for_uid():
    pass

@pytest.mark.asyncio
async def test_get_partner_avg():
    pass

@pytest.mark.asyncio
async def test_get_random_name():
    pass

@pytest.mark.asyncio
async def test_get_rank_id_list():
    pass

@pytest.mark.asyncio
async def test_get_results_id_list():
    pass

@pytest.mark.asyncio
async def test_get_results_tier_dict():
    result = await get_results_tier_dict()
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_get_tier_from_submission_channel():

@pytest.mark.asyncio
async def test_get_tier_id_list():
    result = await get_tier_id_list()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def get_test_get_unix_time_now():
    pass
