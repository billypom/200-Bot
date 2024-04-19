import pytest
import DBA
from config import TEST_DTB, TEST_HOST, TEST_PASS, TEST_USER
from unittest.mock import MagicMock, patch
from datetime import datetime
from helpers.checkers import check_for_dupes_in_list
from helpers.checkers import check_if_banned_characters


@pytest.fixture
def example_data():
    return ["data", "goes", "here"]


def use_example_date():
    data = example_data()
    assert isinstance(data, list)


@pytest.fixture(scope="session")
def create_database():
    with DBA.DBAccess(
        db_name=TEST_DTB, db_host=TEST_HOST, db_user=TEST_USER, db_pass=TEST_PASS
    ) as db:
        # create all tables
        # insert test data


@pytest.fixture
def delete_database():
    with DBA.DBAccess(
        db_name=TEST_DTB, db_host=TEST_HOST, db_user=TEST_USER, db_pass=TEST_PASS
    ) as db:
        db.execute("DROP USER 'test_runner'@'localhost';", ())
        # drop all tables
        db.execute("DROP DATABASE 200lounge_dev;", ())


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
async def test_check_if_mkc_user_id_used():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_mogi_id_exists():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_name_is_unique():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_uid_exists():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_uid_has_role():
    # discord mock data
    # hard to test...
    pass


@pytest.mark.asyncio
async def test_check_if_uid_is_chat_restricted():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_uid_is_lounge_banned():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_uid_is_placement():
    # need test data
    pass


@pytest.mark.asyncio
async def test_check_if_valid_table_submission_channel():
    # discord mock data
    # hard to test...
    pass
