import DBA
from helpers import calculate_pre_mmr, calculate_mmr
from helpers.handlers import (
    handle_score_input,
    handle_team_placements_for_lorenzi_table,
)
import asyncio
from pprint import pprint


async def function():
    chunked_list = await handle_score_input(
        score_string="1 72 2 120 3 75 4 107 5 91 6 83 7 88 8 75 9 103 10 46 11 32 12 92",
        mogi_format=2,
    )
    await handle_team_placements_for_lorenzi_table(chunked_list)
    print("chunked_list:")
    pprint(chunked_list)
    sorted_list = sorted(chunked_list, key=lambda x: int(x[len(chunked_list[0]) - 2]))
    sorted_list.reverse()
    # [player_id, score], team_score, team_mmr]
    print("sorted list:")
    pprint(sorted_list)
    value_table = await calculate_pre_mmr(2, sorted_list)
    print("value table")
    pprint(value_table)
    # player_id, score, team_score, team_mmr, place, mmr_delta
    await calculate_mmr(sorted_list, value_table)
    print("finished sorted list")
    pprint(sorted_list)


def main():
    with DBA.DBAccess() as db:
        print("creating database")
        with open("sql/development_init.sql", "r") as file:
            sql_file = file.read()
            sql_commands = sql_file.split(";")
        with DBA.DBAccess() as db:
            for command in sql_commands:
                if command.strip():
                    db.execute(command, ())
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(function())]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == "__main__":
    main()
