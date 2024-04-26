import pytest
import constants
import DBA

# import config
from helpers.handlers import (
    handle_placement_init,
    handle_player_name,
    handle_queued_mmr_penalties,
    handle_score_input,
    handle_suggestion_decision,
    handle_team_placements_for_lorenzi_table,
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
async def test_handle_placement_init():
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_handle_player_name():
    result = await handle_player_name("this is the name")
    assert result == "thisisthename"
    result = await handle_player_name("정말")
    assert result == "jeongmal"
    result = await handle_player_name("日本語のキーボード")
    assert result == "nihongonokiiboo"
    assert len(result) <= 16


@pytest.mark.asyncio
async def test_handle_queued_mmr_penalties(create_database):
    # Player with no penalties
    total_queued_penalties, final_mmr = await handle_queued_mmr_penalties(1, 4000)
    assert total_queued_penalties == 0
    assert final_mmr == 4000
    # Player with queued penalties
    total_queued_penalties, final_mmr = await handle_queued_mmr_penalties(9, 4000)
    assert total_queued_penalties == 200
    assert final_mmr == 3800


@pytest.mark.asyncio
async def test_handle_score_input(create_database):
    result = await handle_score_input(
        score_string="1 82 2 82 3 82 4 82 5 82 6 82 7 82 8 82 9 82 10 82 11 82 12 82",
        mogi_format=2,
    )
    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert isinstance(result[0][0], list)
    assert isinstance(result[0][0][0], int)


@pytest.mark.asyncio
async def test_handle_suggestion_decision():
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_handle_team_placements_for_lorenzi_table(create_database):
    chunked_list = await handle_score_input(
        score_string="1 82 2 81+1 3 82 4 82 5 82 6 82 7 82 8 82 9 82 10 82 11 82 12 82",
        mogi_format=2,
    )
    assert chunked_list = [
        [[1, "82"], [2, "81+1"]],
        [[3, "82"], [4, "82"]],
        [[5, "82"], [6, "82"]],
        [[7, "82"], [8, "82"]],
        [[9, "82"], [10, "82"]],
        [[11, "82"], [12, "82"]],
    ]
    (
        data_is_valid,
        error_message,
        mogi_score,
        original_scores,
    ) = await handle_team_placements_for_lorenzi_table(chunked_list)
    # Scores validation
    for player in original_scores.items():
        assert player[1] == 82
    # handler validation
    assert data_is_valid
    assert isinstance(error_message, str)
    assert mogi_score == 984
    assert isinstance(original_scores, dict)
    for item in original_scores.items():
        assert isinstance(item[1], int)
    # Bad mogi score validation
    chunked_list = await handle_score_input(
        score_string="1 999 2 82 3 82 4 82 5 82 6 82 7 82 8 82 9 82 10 82 11 82 12 82",
        mogi_format=2,
    )
    _, _, mogi_score, _ = await handle_team_placements_for_lorenzi_table(chunked_list)
    assert not mogi_score == 984
