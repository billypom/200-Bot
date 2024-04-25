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
    pass


@pytest.mark.asyncio
async def test_calculate_pre_mmr():
    pass


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
