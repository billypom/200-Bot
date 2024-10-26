import pytest
from helpers.getters import get_results_tier_dict
from helpers.handlers import handle_team_placements_for_lorenzi_table
from helpers import (
    calculate_mmr,
    calculate_pre_mmr,
    convert_datetime_to_unix_timestamp,
    create_lorenzi_query,
    create_mogi,
    create_player,
    generate_random_name,
    jp_kr_romanize,
)


@pytest.fixture(scope="session")
def create_database():
    """Creates a temporary database for testing"""
    import DBA

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
async def test_calculate_mmr(create_database):
    """Tests the process of creating a 2v2 mmr table

    - sorting
    - mmr calculation
    - final table result"""
    # chunked_list = [[player_id, score], [player_id, score]]...
    chunked_list = [
        [[1, "72"], [2, "120"]],
        [[3, "75"], [4, "107"]],
        [[5, "91"], [6, "83"]],
        [[7, "88"], [8, "75"]],
        [[9, "103"], [10, "46"]],
        [[11, "32"], [12, "92"]],
    ]
    original_chunked_list = [
        [[1, "72"], [2, "120"]],
        [[3, "75"], [4, "107"]],
        [[5, "91"], [6, "83"]],
        [[7, "88"], [8, "75"]],
        [[9, "103"], [10, "46"]],
        [[11, "32"], [12, "92"]],
    ]
    (
        _,
        _,
        _,
        original_scores,
    ) = await handle_team_placements_for_lorenzi_table(chunked_list)
    for team in original_chunked_list:
        for player in team:
            assert original_scores[player[0]] == int(player[1])
    # chunked_list = [player_id, score], team_score, team_mmr]
    sorted_list = sorted(chunked_list, key=lambda x: int(x[-2]))  # type: ignore
    sorted_list.reverse()
    await create_lorenzi_query(sorted_list, original_scores, 2, ["a", "b"])
    # sorted_list = [[player_id, score], [...], team_score, team_mmr, place]
    assert sorted_list == [
        [[1, "72"], [2, "120"], 192, 4000.0, 1],
        [[3, "75"], [4, "107"], 182, 4000.0, 2],
        [[5, "91"], [6, "83"], 174, 4000.0, 3],
        [[7, "88"], [8, "75"], 163, 4000.0, 4],
        [[9, "103"], [10, "46"], 149, 2000.0, 5],
        [[11, "32"], [12, "92"], 124, 4000.0, 6],
    ]
    value_table = await calculate_pre_mmr(2, sorted_list)
    assert value_table == [
        [0.0, -40.0, -40.0, -40.0, -22.359336000524674, -40.0],
        [40.0, 0.0, -40.0, -40.0, -22.359336000524674, -40.0],
        [40.0, 40.0, 0.0, -40.0, -22.359336000524674, -40.0],
        [40.0, 40.0, 40.0, 0.0, -22.359336000524674, -40.0],
        [
            22.359336000524674,
            22.359336000524674,
            22.359336000524674,
            22.359336000524674,
            0.0,
            -65.3776084895605,
        ],
        [40.0, 40.0, 40.0, 40.0, 65.3776084895605, 0.0],
    ]
    # sorted_list = [[player_id, score], [...], team_score, team_mmr, place, mmr_delta]
    await calculate_mmr(sorted_list, value_table)
    assert sorted_list[0][4] == 1
    assert sorted_list[1][4] == 2
    assert sorted_list[2][4] == 3
    assert sorted_list[3][4] == 4
    assert sorted_list[4][4] == 5
    assert sorted_list[5][4] == 6
    # MMR delta assertions
    assert sorted_list[0][5] == 182
    assert sorted_list[1][5] == 102
    assert sorted_list[2][5] == 22
    assert sorted_list[3][5] == -58
    assert sorted_list[4][5] == -25
    assert sorted_list[5][5] == -226


@pytest.mark.asyncio
async def test_create_mogi(create_database):
    """Integration test for mogi creation

    Make sure we get `results channel id` & `tier name`
    """
    import random

    tiers = await get_results_tier_dict()

    for tier in tiers.items():
        mogi_format = random.choice([1, 2, 3, 4, 6])
        results_id, tier_name = await create_mogi(mogi_format, tier[0])
        assert isinstance(results_id, int)
        assert isinstance(tier_name, str)
        assert results_id == tier[1]


@pytest.mark.asyncio
async def test_create_player():
    """can't test this?"""
    # impossible to test
    pass


@pytest.mark.asyncio
async def test_convert_datetime_to_unix_timestamp():
    """Test that unix timestamp is an integer. doi"""
    import datetime

    date = datetime.datetime.now()
    unix = await convert_datetime_to_unix_timestamp(date)
    assert isinstance(unix, int)


@pytest.mark.asyncio
async def test_generate_random_name():
    """Test random name generation"""
    name = await generate_random_name()
    assert isinstance(name, str)


@pytest.mark.asyncio
async def test_jp_kr_romanize():
    """Test japanese & korean romanization with a basic words"""
    result = await jp_kr_romanize("정말")
    assert result == "jeongmal"
    result = await jp_kr_romanize("日本語のキーボード")
    assert result == "nihongonokiiboodo"
