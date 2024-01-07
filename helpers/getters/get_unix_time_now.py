import time
import datetime
# Returns the current unix timestamp
async def get_unix_time_now() -> int:
    return time.mktime(datetime.datetime.now().timetuple())