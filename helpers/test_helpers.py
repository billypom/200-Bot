import pytest
import DBA

# import config
from helpers import (
    calculate_mmr,
    calculate_pre_mmr,
    create_lorenzi_query,
    create_mogi,
    create_player,
    convert_datetime_to_unix_timestamp,
    generate_random_name,
    jp_kr_romanize,
)
from helpers.handlers.handle_team_placements_for_lorenzi_table import (
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
async def test_calculate_mmr():
    # [player_id, score], team_score, team_mmr]
    # await handle_team_placements_for_lorenzi_table(sorted_list)
    sorted_list = [
        [[1, "72"], [2, "120"], 192, 6670.0, 1, 80],
        [[3, "75"], [4, "107"], 182, 3792.5, 2, 136],
        [[5, "91"], [6, "83"], 174, 4867.5, 3, -4],
        [[7, "88"], [8, "75"], 163, 3953.0, 4, -35],
        [[9, "103"], [10, "46"], 149, 1640.0, 5, 0],
        [[11, "32"], [12, "92"], 124, 3535.5, 6, -180],
    ]
    value_table = await calculate_pre_mmr(2, sorted_list)
    # player_id, score, team_score, team_mmr, place, mmr_delta
    result = await calculate_mmr(sorted_list, value_table)
    assert sorted_list[0][4] == 1
    assert sorted_list[1][4] == 2
    assert sorted_list[2][4] == 3
    assert sorted_list[3][4] == 4
    assert sorted_list[4][4] == 5
    assert sorted_list[5][4] == 6
    # MMR delta assertions
    assert sorted_list[0][5] == 80
    assert sorted_list[1][5] == 136
    assert sorted_list[2][5] == -4
    assert sorted_list[3][5] == -35
    assert sorted_list[4][5] == 0
    assert sorted_list[5][5] == -180


@pytest.mark.asyncio
async def test_calculate_pre_mmr():
    # [player_id, score], team_score, team_mmr]
    sorted_list = [
        [[1, "72"], [2, "120"], 192, 6670.0, 1, 80],
        [[3, "75"], [4, "107"], 182, 3792.5, 2, 136],
        [[5, "91"], [6, "83"], 174, 4867.5, 3, -4],
        [[7, "88"], [8, "75"], 163, 3953.0, 4, -35],
        [[9, "103"], [10, "46"], 149, 1640.0, 5, 0],
        [[11, "32"], [12, "92"], 124, 3535.5, 6, -180],
    ]
    result = await calculate_pre_mmr(mogi_format=2, sorted_list=sorted_list)
    assert isinstance(result, list)
    # Place assertions
    # player_id, score, team_score, team_mmr, place, mmr_delta


@pytest.mark.asyncio
async def test_create_lorenzi_query():
    pass


@pytest.mark.asyncio
async def test_create_mogi():
    pass


@pytest.mark.asyncio
async def test_create_player():
    pass


@pytest.mark.asyncio
async def test_convert_datetime_to_unix_timestamp():
    pass


@pytest.mark.asyncio
async def test_generate_random_name():
    pass


@pytest.mark.asyncio
async def test_jp_kr_romanize():
    pass
