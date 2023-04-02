import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import secretly


class unban_check(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    async def send_raw_to_debug_channel(self, anything, error):
        channel = self.client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description='>.<', color = discord.Color.orange())
        embed.add_field(name='anything: ', value=anything, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    async def set_player_roles(self, uid):
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT rank_id FROM player WHERE player_id = %s;', (uid,))
            # Remove all potential ranks first
            guild = self.client.get_guild(secretly.Lounge[0])
            role = guild.get_role(temp[0][0])
            member = await guild.fetch_member(uid)
            await member.add_roles(role)
        except Exception as e:
            await self.send_raw_to_debug_channel(f'<@{uid}>', f'set_player_roles exception: {e}')
            return False

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(hours=1)
    async def check(self):
        current_time = datetime.datetime.now()
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM player WHERE unban_date < %s;', (current_time,))
        except Exception as e:
            await self.send_raw_to_debug_channel(f'unban_check error 1 {secretly.my_discord}', e)
            return
        for player in temp:
            try:
                guild = self.client.get_guild(secretly.Lounge[0])
                user = await guild.fetch_member(player[0])
                loungeless_role = guild.get_role(secretly.LOUNGELESS_ROLE_ID)
                await user.remove_roles(loungeless_role)
                await self.set_player_roles(player[0])
                await self.send_raw_to_debug_channel(f'Player unbanned - Loungeless removed', player[0])
            except Exception as e:
                await self.send_raw_to_debug_channel(f'Player unbanned - Not found in server - roles not assigned', player[0])
                pass
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET unban_date = NULL WHERE player_id = %s;', (player[0],))

    @check.before_loop
    async def before_check(self):
        print('unban waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(unban_check(client))