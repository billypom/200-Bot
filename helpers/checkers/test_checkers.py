import pytest
import DBA
import discord
from datetime import datetime
from constants import SQUAD_QUEUE_CHANNEL_ID
from helpers.getters import get_results_tier_dict
from helpers.checkers import (
    check_for_dupes_in_list,
    check_for_rank_changes,
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



@pytest.fixture(scope="session")
def create_database():
    """Creates a temp database"""
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
    """Test duplicate values in list for /table command"""
    # List without duplicates
    input: list = [1, 2, 3, 4]
    result = await check_for_dupes_in_list(input)
    assert not result
    # List with duplicates
    input: list = [1, 2, 2, 3]
    result = await check_for_dupes_in_list(input)
    assert result


@pytest.mark.asyncio
async def test_check_for_rank_changes(create_database):
    """Tests rank up/down, account for upper and lower bounds (gm and iron)"""
    # Rank ID: min, max
    ranks = [
        [1041162011536527391, 0, 1499],
        [1041162011536527392, 1500, 2999],
        [1041162011536527393, 3000, 4499],
        [1041162011536527394, 4500, 5999],
        [1041162011536527395, 6000, 7499],
        [1041162011536527396, 7500, 8999],
        [1041162011536527397, 9000, 10999],
        [1041162011536527398, 11000, 99999],
    ]
    for i, rank in enumerate(ranks):
        min_mmr = rank[1]
        max_mmr = rank[2]
        # No change
        (
            rank_changed,
            rank_went_up,
            new_rank_id,
        ) = await check_for_rank_changes(min_mmr, max_mmr)
        assert not rank_changed
        assert not rank_went_up
        assert new_rank_id == 0
        # Rank up
        if rank[0] != 1041162011536527398:  # gm dont go up
            (
                rank_changed,
                rank_went_up,
                new_rank_id,
            ) = await check_for_rank_changes(max_mmr, max_mmr + 1)
            assert rank_changed
            assert rank_went_up
            assert new_rank_id == ranks[i + 1][0]
        # Rank down
        if rank[0] != 1041162011536527391:  # iron dont go down
            (
                rank_changed,
                rank_went_up,
                new_rank_id,
            ) = await check_for_rank_changes(min_mmr, min_mmr - 1)
            assert rank_changed
            assert not rank_went_up
            assert new_rank_id == ranks[i - 1][0]


@pytest.mark.asyncio
async def test_check_if_banned_characters():
    """Test for banned characters"""
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
    """Integration test"""
    result = await check_if_mkc_user_id_used(1)
    assert result  # true
    result = await check_if_mkc_user_id_used(999)
    assert not result  # false


@pytest.mark.asyncio
async def test_check_if_mogi_id_exists(create_database):
    """Integration test"""
    result = await check_if_mogi_id_exists(1)
    assert result
    result = await check_if_mogi_id_exists(999)
    assert not result


@pytest.mark.asyncio
async def test_check_if_name_is_unique(create_database):
    """Integration test"""
    # need test data
    result = await check_if_name_is_unique("1")
    assert not result
    result = await check_if_name_is_unique("Player_MK")
    assert result


@pytest.mark.asyncio
async def test_check_if_uid_exists(create_database):
    """Integration test"""
    # need test data
    result = await check_if_uid_exists(1)
    assert result
    result = await check_if_uid_exists(999)
    assert not result


@pytest.mark.asyncio
async def test_check_if_uid_has_role():
    """can't test this"""
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
    """Integration test"""
    result = await check_if_uid_is_chat_restricted(1)
    assert not result
    result = await check_if_uid_is_chat_restricted(12)
    assert result


@pytest.mark.asyncio
async def test_check_if_uid_is_lounge_banned(create_database):
    """Integration test"""
    result = await check_if_uid_is_lounge_banned(1)
    assert not result
    result = await check_if_uid_is_lounge_banned(11)
    assert result > 0


@pytest.mark.asyncio
async def test_check_if_uid_is_placement(create_database):
    """Integration test"""
    result = await check_if_uid_is_placement(1)
    assert not result
    result = await check_if_uid_is_placement(10)
    assert result


@pytest.mark.asyncio
async def test_check_if_valid_table_submission_channel(create_database):
    """Integration test"""
    # set up a category in the db
    with DBA.DBAccess() as db:
        db.execute("INSERT INTO sq_helper (category_id) values (%s);", (1,))
    channels = []  # list of valid channel ids and 1 invalid
    tier_results = await get_results_tier_dict()
    for key, value in tier_results.items():
        channels.append(key)
        channels.append(value)
    channels.append(SQUAD_QUEUE_CHANNEL_ID)
    # All valid channels, any category
    for idx, channel in enumerate(channels):
        result = await check_if_valid_table_submission_channel(channel, idx)
        assert result
    # Invalid channel + valid sq category
    result = await check_if_valid_table_submission_channel(999, 1)
    assert result
    # Invalid channel + invalid sq category
    result = await check_if_valid_table_submission_channel(999, 2)
    assert not result
