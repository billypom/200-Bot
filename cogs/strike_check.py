import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import secretly

class strike_check(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    async def send_raw_to_debug_channel(self, anything, error):
        channel = self.client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description='>.<', color = discord.Color.orange())
        embed.add_field(name='anything: ', value=anything, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(hours=24)
    async def check(self):
        current_time = datetime.datetime.now()
        min_date = current_time - datetime.timedelta(days=30)
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT strike_id FROM strike WHERE expiration_date < %s;', (min_date,))
        except Exception as e:
            await self.send_raw_to_debug_channel(f'strike_check error 1 {secretly.my_discord}', e)
            return
        await self.send_raw_to_debug_channel(f'strike_check pass', str(temp))

    @check.before_loop
    async def before_check(self):
        print('strike waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(strike_check(client))