from discord.ext import commands, tasks
import time
import datetime
import DBA
import config
import math
from helpers.senders import send_raw_to_debug_channel

ML_CHANNEL_MESSAGE_ID = config.ML_CHANNEL_MESSAGE_ID
ML_LU_CHANNEL_MESSAGE_ID = config.ML_LU_CHANNEL_MESSAGE_ID

class update_mogilist(commands.Cog):
    def __init__(self, client):
        self.update.start()
        self.client = client

    def cog_unload(self):
        self.update.cancel()

    @tasks.loop(seconds=5)
    async def update(self):
        # print('updating mogilist...')
        unix_now = time.mktime(datetime.datetime.now().timetuple())
        minutes_since_start = ""
        try:
            MOGILIST = {}
            pre_ml_string = ''
            pre_mllu_string = ''
            # remove_chars = {
            #     39:None, # ,
            #     91:None, # [
            #     93:None, # ]
            # }
            with DBA.DBAccess() as db:
                temp = db.query('SELECT t.tier_id, p.player_name, UNIX_TIMESTAMP(l.mogi_start_time) FROM tier t INNER JOIN lineups l ON t.tier_id = l.tier_id INNER JOIN player p ON l.player_id = p.player_id WHERE p.player_id > %s ORDER BY l.create_date ASC', (1,))
            for i in range(len(temp)): # create dictionary {tier_id:[list of players in tier]}
                if temp[i][0] in MOGILIST: # if we already have tier_id as a key
                    MOGILIST[temp[i][0]].append((temp[i][1], temp[i][2])) # append to current value list
                else:
                    MOGILIST[temp[i][0]]=[(temp[i][1], temp[i][2])] # add new key


            num_active_mogis = len(MOGILIST.keys())
            num_full_mogis = 0
            for k,v in MOGILIST.items():
                mllu_players = ""
                # print(f'unix now: {unix_now}')
                # print('for k,v in mogilist.items()')
                # print(f'k: {k} | v: {v}')
                # print(f'v[0][0]: {v[0][0]} | v[0][1]: {v[0][1]}')
                try:
                    mogi_start_time = int(v[0][1])
                    minutes_since_start = f' - `{str(math.floor((unix_now - mogi_start_time)/60))}m ago`'
                except Exception:
                    minutes_since_start = ""
                    pass
                pre_ml_string += f'<#{k}> - ({len(v)}/12){minutes_since_start}\n'
                if len(v) >= 12:
                    num_full_mogis +=1
                for idx, player in enumerate(v):
                    if idx == len(v)-1:
                        mllu_players += f'{player[0]}'    
                    else:
                        mllu_players += f'{player[0]}, '
                # mllu_players = str(v[0][0]).translate(remove_chars)
                pre_mllu_string += f'<#{k}> - ({len(v)}/12){minutes_since_start} - {mllu_players}\n'
            title = f'There are {num_active_mogis} active mogi and {num_full_mogis} full mogi.\n\n'
            ml_string = f'{title}{pre_ml_string}'
            mllu_string = f'{title}{pre_mllu_string}'

            ml = self.client.get_channel(config.MOGILIST_CHANNEL_ID)
            ml_message = await ml.fetch_message(ML_CHANNEL_MESSAGE_ID)
            await ml_message.edit(content=f'{ml_string}\n<t:{int(unix_now)}:F>')

            mllu = self.client.get_channel(config.MOGILIST_LU_CHANNEL_ID)
            mllu_message = await mllu.fetch_message(ML_LU_CHANNEL_MESSAGE_ID)
            await mllu_message.edit(content=f'{mllu_string}\n<t:{int(unix_now)}:F>')
        except Exception as e:
            # print(e)
            await send_raw_to_debug_channel(self.client, 'mogilist error 1', e)
    
    @update.before_loop
    async def before_update(self):
        print('update waiting...')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(update_mogilist(client))