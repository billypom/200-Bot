import time
import datetime


async def get_unix_time_now() -> int:
    """Returns the current unix timestamp"""
    return int(time.mktime(datetime.datetime.now().timetuple()))
