from config import HERE_PING_SECONDS_DELTA_LIMIT
from config import TIME_OF_LAST_HERE_PING
from config import set_time_since_last_here_ping
from helpers.getters import get_unix_time_now

async def send_here_ping_message(ctx, message):
    unix_now = await get_unix_time_now()
    new_time = TIME_OF_LAST_HERE_PING + HERE_PING_SECONDS_DELTA_LIMIT
    logging.info(f'send_here_ping_message | unix_now = {unix_now} | new_time = {new_time}')
    logging.info(f'send_here_ping_message | time of last here ping = {TIME_OF_LAST_HERE_PING}')
    if unix_now > new_time:
        await ctx.channel.send(message)
        await set_time_since_last_here_ping(unix_now)
