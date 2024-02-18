import time
import datetime
# Returns the current unix timestamp
async def get_unix_time_now() -> int:
    return int(time.mktime(datetime.datetime.now().timetuple()))