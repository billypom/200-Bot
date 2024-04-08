from config import HERE_PING_SECONDS_DELTA_LIMIT
import time
import datetime
import logging
import configparser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import TextChannel


async def send_here_ping_message(channel: TextChannel, message: str) -> None:
    # Read from config.ini file
    config = configparser.ConfigParser()
    config.read("config.ini")
    TIME_OF_LAST_HERE_PING = config["MOGI"].getint("TIME_OF_LAST_HERE_PING")
    # Compare times
    unix_now = int(time.mktime(datetime.datetime.now().timetuple()))
    new_time = TIME_OF_LAST_HERE_PING + HERE_PING_SECONDS_DELTA_LIMIT
    # If enough time has passed, allow sending ping
    if unix_now > new_time:
        await channel.send(message)
        try:
            config["MOGI"]["TIME_OF_LAST_HERE_PING"] = str(unix_now)
            with open("config.ini", "w") as configfile:
                config.write(configfile)
        except Exception as e:
            logging.warning(f"send_here_ping_message | {e}")
