import pytest
import constants
import DBA

# import config
from helpers.getters import (
    get_discord_role,
    get_lounge_guild,
    get_mogi_table_color_by_format,
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


@pytest.fixture(scope="session")
def create_database():
    with DBA.DBAccess() as db:
        print("creating database")
        with open("sql/development_init.sql", "r") as file:
            sql_file = file.read()
            sql_commands = sql_file.split(";")
        with DBA.DBAccess() as db:
            for command in sql_commands:
                if command.strip():
                    db.execute(command, ())


@pytest.mark.asyncio
async def test_get_discord_role():
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_get_lounge_guild():
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_get_mogi_table_color_by_format():
    for i in [1, 2, 3, 4, 6]:
        result = await get_mogi_table_color_by_format(i)
        assert isinstance(result, list)
        assert result[0] is not None
    result = await get_mogi_table_color_by_format(-1)
    assert isinstance(result, list)
    assert result[0] is None


@pytest.mark.asyncio
async def test_get_number_of_strikes_for_uid():
    pass


@pytest.mark.asyncio
async def test_get_partner_avg():
    pass


@pytest.mark.asyncio
async def test_get_random_name():
    result = await get_random_name()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_get_rank_id_list(create_database):
    result = await get_rank_id_list()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_results_id_list(create_database):
    result = await get_results_id_list()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_results_tier_dict(create_database):
    result = await get_results_tier_dict()
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_tier_from_submission_channel(create_database):
    tier_results = await get_results_tier_dict()
    for key, value in tier_results.items():
        result = await get_tier_from_submission_channel(key)
        assert result == key
        result = await get_tier_from_submission_channel(value)
        assert result == key
    result = await get_tier_from_submission_channel(constants.SQUAD_QUEUE_CHANNEL_ID)
    assert result == constants.SQUAD_QUEUE_CHANNEL_ID


@pytest.mark.asyncio
async def test_get_tier_id_list(create_database):
    result = await get_tier_id_list()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def get_test_get_unix_time_now():
    result = await get_unix_time_now()
    assert isinstance(result, int)
