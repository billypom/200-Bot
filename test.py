import DBA
import aiohttp
import asyncio
from bs4 import BeautifulSoup as Soup


async def my_func():
    pass


def main():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(my_func())]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == "__main__":
    main()
