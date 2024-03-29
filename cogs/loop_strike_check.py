import discord
from discord.ext import commands, tasks
import datetime
import DBA
import config
import logging

class strike_check(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    async def send_embed(self, anything, error):
        channel = self.client.get_channel(config.DEBUG_CHANNEL_ID)
        embed = discord.Embed(title='Hourly Strike Check', description='✅', color = discord.Color.teal())
        embed.add_field(name='Description: ', value=anything, inline=False)
        embed.add_field(name='Strike IDs: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    async def send_error_embed(self, anything, error):
        channel = self.client.get_channel(config.DEBUG_CHANNEL_ID)
        embed = discord.Embed(title='Hourly Strike Check', description='✅', color = discord.Color.red())
        embed.add_field(name='Description: ', value=anything, inline=False)
        embed.add_field(name='Details: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(hours=1)
    async def check(self):
        current_time = datetime.datetime.now()
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT strike_id FROM strike WHERE expiration_date < %s AND is_active = %s;', (current_time, 1))
        except Exception as e:
            logging.info(f'strike_check | ERROR - unable to retrieve strike | {e}')
            await self.send_error_embed(f'strike_check error 1 {config.PING_DEVELOPER}', e)
            return
        if temp:
            logging.info(f'strike_check | Strikes expiring: {str(temp)}')
            await self.send_embed('Strikes expiring by strike_id', str(temp))
            try:
                with DBA.DBAccess() as db:
                    db.execute('UPDATE strike SET is_active = %s WHERE expiration_date < %s;', (0, current_time))
            except Exception as e:
                logging.info(f'strike_check | ERROR - unable to set strikes to inactive | {e}')
                await self.send_error_embed(f'strike_check error 2 {config.PING_DEVELOPER}', e)
                return

    @check.before_loop
    async def before_check(self):
        print('strike waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(strike_check(client))