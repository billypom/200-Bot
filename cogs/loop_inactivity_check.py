from discord.ext import commands, tasks
import time
import datetime
import DBA
from config import PING_DEVELOPER, LOUNGE_QUEUE_JOIN_CHANNEL_ID
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_unix_time_now

class inactivity_check(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(seconds=10)
    async def check(self):
        unix_now = await get_unix_time_now()
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT l.player_id, UNIX_TIMESTAMP(l.last_active), l.wait_for_activity, p.player_name FROM lounge_queue_player l JOIN player p ON l.player_id = p.player_id;', ())
        except Exception as e:
            await send_raw_to_debug_channel(self.client, f'inactivity_check error 1 {PING_DEVELOPER}', e)
            return
        for i in range(len(temp)):
            name = temp[i][3]
            try:
                unix_difference = unix_now - temp[i][1]
            except Exception:
                # await send_raw_to_debug_channel(self.client, f'inactivity_check error dev1 {PING_DEVELOPER}', e)
                # print('im devving?')
                return
            # print(f'{unix_now} - {temp[i][1]} = {unix_difference}')
            if unix_difference < 900: # if it has been less than 15 minutes
                if unix_difference > 600: # if it has been more than 10 minutes
                    channel = self.client.get_channel(LOUNGE_QUEUE_JOIN_CHANNEL_ID)
                    if temp[i][2] == 0: # false we are not waiting for activity
                        message = f'<@{temp[i][0]}> Type anything in the chat in the next 10 minutes to keep your spot in the mogi.'
                        await channel.send(message, delete_after=300)
                        # set wait_for_activity = 1 means the ping was already sent.
                        try:
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE lounge_queue_player SET wait_for_activity = %s WHERE player_id = %s;', (1, temp[i][0])) # we are waiting for activity
                        except Exception as e:
                            await send_raw_to_debug_channel(self.client, f'inactivity_check error 2 {PING_DEVELOPER}', e)
                            return
                else: # has not been at least 10 minutes yet
                    continue # does this make it faster? idk
            elif unix_difference > 1200: # if its been more than 20 minutes
                # Drop player
                try:
                    with DBA.DBAccess() as db:
                        db.execute('DELETE FROM lounge_queue_player WHERE player_id = %s;', (temp[i][0],))
                except Exception as e:
                    await send_raw_to_debug_channel(self.client, f'{PING_DEVELOPER} inactivity_check - cannot delete from lounge_queue_player',f'{temp[i][0]} | {temp[i][1]} | {temp[i][2]} | {e}')
                    return
                # Send message
                channel = self.client.get_channel(LOUNGE_QUEUE_JOIN_CHANNEL_ID)
                message = f'{name} has been removed from the lounge queue due to inactivity'
                await channel.send(message, delete_after=300)
            else:
                continue
    
    @check.before_loop
    async def before_check(self):
        print('inactivity check process started')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(inactivity_check(client))
