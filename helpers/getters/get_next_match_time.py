from datetime import datetime, timedelta
from config import LOUNGE_QUEUE_START_MINUTE

# Input:
# Output: int unix_timestamp
async def get_next_match_time() -> int:
    """Returns a unix timestamp of the next match time based on the :00 minute from config"""
    # Get the current time
    current_time = datetime.now()
    # Calculate minutes til next match
    minutes_to_next_match = LOUNGE_QUEUE_START_MINUTE - (current_time.minute % LOUNGE_QUEUE_START_MINUTE)
    # If function was ran at a current match time, go to the next match interval
    if minutes_to_next_match == 0:
        minutes_to_next_match = LOUNGE_QUEUE_START_MINUTE
    # Calculate the time difference to the next match in seconds
    time_difference_seconds = minutes_to_next_match * 60
    # Calculate the next match time by adding the time difference to the current time
    next_match_time = current_time + timedelta(seconds=time_difference_seconds)
    # Unix timestamp
    next_match_timestamp = int(next_match_time.timestamp())
    return next_match_timestamp
