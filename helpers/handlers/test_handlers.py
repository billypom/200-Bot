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
    result = await handle_queued_mmr_penalties(1, 4000)
