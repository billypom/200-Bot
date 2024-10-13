import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


async def convert_datetime_to_unix_timestamp(dto: "datetime") -> int:
    """Converts a python datetime object to a unix timestamp

    Args:
    - `dto` (datetime): Datetime object

    Returns:
    - (int): unix timestamp"""
    return int(time.mktime(dto.timetuple()))
