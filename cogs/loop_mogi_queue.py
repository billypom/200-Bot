from discord.ext import commands, tasks
from datetime import datetime
import DBA
from config import PING_DEVELOPER, LOUNGE_QUEUE_START_MINUTE
from helpers import convert_datetime_to_unix_timestamp, create_queue_channels_and_categories
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild

class mogi_queue(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(minutes=1)
    async def check(self):
        # Get the current time
        current_time = datetime.now()
        # Check if the current minute is one of the LOUNGE_QUEUE_START_MINUTE intervals
        if current_time.minute % LOUNGE_QUEUE_START_MINUTE != 0:
            pass
            # return
        print('Mogi queue time')

        # Query for players in lineup table, sort by create_date ASC - people who can up first have priority
        #   player_id: {mmr, create_date}
        player_dict = {}
        with DBA.DBAccess() as db:
            temp = db.query('SELECT l.player_id, p.mmr, l.create_date FROM lounge_queue_player l JOIN player p on l.player_id = p.player_id ORDER BY l.create_date ASC;', ())
        
        for player in temp:
            player_id = player[0]
            if player[1] is None:
                mmr = 1000
            else:
                mmr = player[1]
            create_date = await convert_datetime_to_unix_timestamp(player[2])
            print(f'Adding player to dict: {player_id} | {mmr} | {create_date}')
            player_dict[player_id] = (mmr, create_date)
        
        # Split lineup list into groups of 12 max (order matters)
        # i.e. [1,2,3,4,5,6,7,8,9,10,11,12], [13,14,15,16,17,18,19,20,21,22,23,24], [25,26,27]
        
        number_of_players_to_pop = len(player_dict) % 12
        popped_players = [] # list of players that were too late for queue: list of tuples: [(player_id, (mmr, create_date))]
        guild = get_lounge_guild(self.client)
        for i in range(number_of_players_to_pop):
            popped_player = player_dict.popitem()
            popped_players.append(popped_player)
            try:
                member = guild.get_member(popped_player[0])
                member.send('Go next sorry last')
            except Exception as e:
                print(f'member not in guild: {popped_player}')
        
        # Rooms will be created for each list
        # Sort the dictionary by mmr in descending order
        sorted_players = sorted(player_dict.items(), key=lambda item: item[1][0], reverse=True)
        number_of_players = len(sorted_players)
        # thank you chatgpt
        groups_of_12 = [sorted_players[i:i + 12] for i in range(0, len(sorted_players), 12)]
        
        await create_queue_channels_and_categories(self.client, number_of_players, groups_of_12)
        
        

            
    
    @check.before_loop
    async def before_check(self):
        print('mogi queue started')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(mogi_queue(client))
