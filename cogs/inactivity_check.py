import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import secretly

class inactivity_check(commands.Cog):
    def __init__(self, client):
        self.index = 0
        self.check.start()
        self.client = client

    # def cog_unload(self):
    #     self.printer.cancel()

    # @tasks.loop(seconds=5)
    # async def printer(self):
    #     print(self.index)
    #     self.index +=1

    async def send_raw_to_debug_channel(self, anything, error):
        channel = self.client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description='>.<', color = discord.Color.yellow())
        embed.add_field(name='anything: ', value=anything, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(seconds=5)
    async def check(self):
        print(f'checking inactivity | {secretly.debug_channel}')
        await self.send_raw_to_debug_channel(f'`:` Checking inactivity...', 'Test')
        unix_now = time.mktime(datetime.datetime.now().timetuple())
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT l.player_id, UNIX_TIMESTAMP(l.last_active), l.tier_id, l.wait_for_activity, p.player_name FROM lineups as l JOIN player as p ON l.player_id = p.player_id WHERE l.can_drop = %s;', (1,))
        except Exception as e:
            await send_raw_to_debug_channel(f'inactivity_check error 1 {secrely.my_discord}', e)
            return
        for i in range(len(temp)):
            name = temp[i][4]
            unix_difference = unix_now - temp[i][1]
            # print(f'{unix_now} - {temp[i][1]} = {unix_difference}')
            if unix_difference < 900: # if it has been less than 15 minutes
                if unix_difference > 600: # if it has been more than 10 minutes
                    channel = client.get_channel(temp[i][2])
                    if temp[i][3] == 0: # false we are not waiting for activity
                        message = f'<@{temp[i][0]}> Type anything in the chat in the next 5 minutes to keep your spot in the mogi.'
                        await channel.send(message, delete_after=300)
                        # set wait_for_activity = 1 means the ping was already sent.
                        try:
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE lineups SET wait_for_activity = %s WHERE player_id = %s;', (1, temp[i][0])) # we are waiting for activity
                        except Exception as e:
                            await send_raw_to_debug_channel(f'inactivity_check error 2 {secrely.my_discord}', e)
                            return
                else: # has not been at least 10 minutes yet
                    continue # does this make it faster? idk
            elif unix_difference > 1200: # if its been more than 20 minutes
                # Drop player
                try:
                    with DBA.DBAccess() as db:
                        db.execute('DELETE FROM lineups WHERE player_id = %s;', (temp[i][0],))
                except Exception as e:
                    await send_raw_to_debug_channel(f'{secrely.my_discord} inactivity_check - cannot delete from lineup',f'{temp[i][0]} | {temp[i][1]} | {temp[i][2]} | {e}')
                    return
                # Send message
                channel = client.get_channel(temp[i][2])
                message = f'{name} has been removed from the mogi due to inactivity'
                await channel.send(message)
            else:
                continue

def setup(client):
    client.add_cog(inactivity_check(client))