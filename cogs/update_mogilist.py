import discord
from discord.ext import commands, tasks
import time
import datetime
import DBA
import secretly

ml_channel_message_id = 1010644370954924052
ml_lu_channel_message_id = 1010644338499403937

class update_mogilist(commands.Cog):
    def __init__(self, client):
        self.update.start()
        self.client = client

    async def send_raw_to_debug_channel(self, anything, error):
        channel = self.client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description='>.<', color = discord.Color.yellow())
        embed.add_field(name='anything: ', value=anything, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        await channel.send(content=None, embed=embed)

    def cog_unload(self):
        self.update.cancel()

    @tasks.loop(seconds=5)
    async def update(self):
        print('updating mogilist...')
        try:
            MOGILIST = {}
            pre_ml_string = ''
            pre_mllu_string = ''
            remove_chars = {
                39:None, # ,
                91:None, # [
                93:None, # ]
            }
            with DBA.DBAccess() as db:
                temp = db.query('SELECT t.tier_id, p.player_name FROM tier t INNER JOIN lineups l ON t.tier_id = l.tier_id INNER JOIN player p ON l.player_id = p.player_id WHERE p.player_id > %s;', (1,))
            for i in range(len(temp)): # create dictionary {tier_id:[list of players in tier]}
                if temp[i][0] in MOGILIST:
                    MOGILIST[temp[i][0]].append(temp[i][1])
                else:
                    MOGILIST[temp[i][0]]=[temp[i][1]]
            num_active_mogis = len(MOGILIST.keys())
            num_full_mogis = 0
            for k,v in MOGILIST.items():
                pre_ml_string += f'<#{k}> - ({len(v)}/12)\n'
                if len(v) >= 12:
                    num_full_mogis +=1
                mllu_players = str(v).translate(remove_chars)
                pre_mllu_string += f'<#{k}> - ({len(v)}/12) - {mllu_players}\n'
            title = f'There are {num_active_mogis} active mogi and {num_full_mogis} full mogi.\n\n'
            ml_string = f'{title}{pre_ml_string}'
            mllu_string = f'{title}{pre_mllu_string}'

            ml = self.client.get_channel(secretly.mogilist_channel)
            print(f'ml: {type(ml)} | {ml}')
            # returns a Future object. need to get the .result() of the Future (which is the Discord.message object)
            ml_message = await ml.fetch_message(ml_channel_message_id)
            print(f'ml_message: {type(ml_message)} | {ml_message}')
            await ml_message.result().edit(content=f'{ml_string}')

            mllu = self.client.get_channel(secretly.mogilist_lu_channel)
            mllu_message = await mllu.fetch_message(ml_lu_channel_message_id)
            await mllu_message.result().edit(content=f'{mllu_string}')
        except Exception as e:
            print(e)
            await self.send_raw_to_debug_channel('mogilist error', e)
    
    @update.before_loop
    async def before_update(self):
        print('update waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(update_mogilist(client))