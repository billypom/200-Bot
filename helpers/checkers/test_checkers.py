import pytest
import DBA
import discord
from datetime import datetime
from helpers.checkers import (
    check_for_dupes_in_list,
    check_if_banned_characters,
    check_if_mkc_user_id_used,
    check_if_mogi_id_exists,
    check_if_name_is_unique,
    check_if_uid_exists,
    check_if_uid_has_role,
    check_if_uid_is_chat_restricted,
    check_if_uid_is_lounge_banned,
    check_if_uid_is_placement,
    check_if_valid_table_submission_channel,
)


@pytest.fixture
def example_data():
    return ["data", "goes", "here"]


def use_example_date():
    data = example_data()
    assert isinstance(data, list)


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
async def test_check_for_dupes_in_list():
    # List without duplicates
    input: list = [1, 2, 3, 4]
    result = await check_for_dupes_in_list(input)
    assert not result
    # List with duplicates
    input: list = [1, 2, 2, 3]
    result = await check_for_dupes_in_list(input)
    assert result


@pytest.mark.asyncio
async def test_check_if_banned_characters():
    # Good input
    input = "this is nice input"
    result = await check_if_banned_characters(input)
    assert bool(result is False)
    # Bad input
    input = "DROP TABLE players"
    result = await check_if_banned_characters(input)
    assert bool(result is True)


@pytest.mark.asyncio
async def test_check_if_mkc_user_id_used(create_database):
    result = await check_if_mkc_user_id_used(1)
    assert result  # true
    result = await check_if_mkc_user_id_used(999)
    assert not result  # false


@pytest.mark.asyncio
async def test_check_if_mogi_id_exists(create_database):
    result = await check_if_mogi_id_exists(1)
    assert result
    result = await check_if_mogi_id_exists(999)
    assert not result


@pytest.mark.asyncio
async def test_check_if_name_is_unique(create_database):
    # need test data
    result = await check_if_name_is_unique("1")
    assert not result
    result = await check_if_name_is_unique("Player_MK")
    assert result
    pass


@pytest.mark.asyncio
async def test_check_if_uid_exists(create_database):
    # need test data
    result = await check_if_uid_exists(1)
    assert result
    result = await check_if_uid_exists(999)
    assert not result


@pytest.mark.asyncio
async def test_check_if_uid_has_role():
    pass
    # impossible to test

    # bot = AsyncMock(spec=discord.Bot)
    # guild = AsyncMock(spec=discord.Guild)
    # member = AsyncMock(spec=discord.Member)
    # role = AsyncMock(spec=discord.Role)
    #
    # bot.guilds = [guild]
    # guild.fetch_member = AsyncMock(return_value=member)
    # role.id = 12345
    # member.roles = [role]
    #
    # result = await check_if_uid_has_role(bot, 1, 12345)
    # assert result


@pytest.mark.asyncio
async def test_check_if_uid_is_chat_restricted(create_database):
    result = await check_if_uid_is_chat_restricted(1)
    assert not result
    result = await check_if_uid_is_chat_restricted(12)
    assert result


@pytest.mark.asyncio
async def test_check_if_uid_is_lounge_banned(create_database):
    result = await check_if_uid_is_lounge_banned(1)
    assert not result
    result = await check_if_uid_is_lounge_banned(11)
    assert result > 0


@pytest.mark.asyncio
async def test_check_if_uid_is_placement(create_database):
    result = await check_if_uid_is_placement(1)
    assert not result
    result = await check_if_uid_is_placement(10)
    assert result


@pytest.mark.asyncio
async def test_check_if_valid_table_submission_channel():
    # set up a category in the db
    with DBA.DBAccess() as db:
        db.execute("INSERT INTO sq_helper (category_id) values (%s);", (1,))
    channels = []  # list of valid channel ids and 1 invalid
    for channel in channels:
        result = await check_if_valid_table_submission_channel(channel, 1)
        assert result
    result = await check_if_valid_table_submission_channel(channels[0], 2)
    assert not result
    result = await check_if_valid_table_submission_channel(3, 3)
    assert not result
