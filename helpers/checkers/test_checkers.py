import pytest
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
