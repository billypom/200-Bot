import time
# Input: datetime object
# Output: UNIX timestamp
async def convert_datetime_to_unix_timestamp(datetime_object):
    return time.mktime(datetime_object.timetuple())