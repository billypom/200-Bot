from discord.ext import commands, tasks
from datetime import datetime
import DBA
import logging
from config import LOUNGE_QUEUE_START_MINUTE, LOUNGE_QUEUE_LIST_CHANNEL_ID
from helpers import convert_datetime_to_unix_timestamp, create_queue_channels_and_categories
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.getters import get_next_match_time
from helpers import delete_discord_channel, delete_discord_category


class lounge_queue(commands.Cog):
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
            return
        
        # Clean up
        logging.info('Cleaning up the lounge queue...')
        
        # Remove channels where table is submitted
        channels_to_delete = []
        try:
            with DBA.DBAccess() as db:
                channels = db.query('SELECT channel_id FROM lounge_queue_channel WHERE is_table_submitted = 1;', ())
                for channel in channels:
                    channels_to_delete.append(channel[0])
        except Exception as e:
            logging.warning(f'loop_mogi_queue | unable to retrieve any channels with submitted tables | {e}')
        # Delete channels from DB
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lounge_queue_channel WHERE is_table_submitted = 1;', ())
        except Exception as e:
            logging.warning(f'loop_mogi_queue | unable to delete from lounge_queue_channel | channel_ids: {channels_to_delete} | {e}')
        
        # Delete discord channels
        for channel in channels_to_delete:
            await delete_discord_channel(self.client, channel)
            
        # Remove categories where has no children
        categories_to_delete = []
        try:
            with DBA.DBAccess() as db:
                categories = db.query('SELECT category_id FROM lounge_queue_category;', ())
            for category in categories:
                categories_to_delete.append(category[0])
        except Exception as e:
            logging.warning(f'loop_mogi_queue | could not retrieve categories from lounge_queue_category | {e}')
            
        # Delete from discord
        guild = get_lounge_guild(self.client)
        for category in guild.categories:
            if not category.channels:
                if category.id in categories_to_delete:
                    await delete_discord_category(self.client, category.id)
        
        
        # Next mogi queue
        
        # Query for players in lounge queue table, sort by create_date ASC - people who can up first have priority
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
            # print(f'Adding player to dict: {player_id} | {mmr} | {create_date}')
            player_dict[player_id] = (mmr, create_date)
        
        # Split lineup list into groups of 12 max (order matters)
        # i.e. [1,2,3,4,5,6,7,8,9,10,11,12], [13,14,15,16,17,18,19,20,21,22,23,24], [25,26,27]
        lounge_queue_list_channel = self.client.get_channel(LOUNGE_QUEUE_LIST_CHANNEL_ID)
        if len(player_dict) < 12:
            logging.warning('Not enough players in queue')
            next_match_time = await get_next_match_time()
            await lounge_queue_list_channel.send(f"Not enough players in queue. Next mogi gathers <t:{next_match_time}:R>")
            # do other stuff Nino mode nino time hi nino
            return
        await lounge_queue_list_channel.send("Sufficient number of players gathered. Creating rooms...")
        
        # handle extra players
        number_of_players_to_pop = len(player_dict) % 12
        popped_players = [] # list of players that were too late for queue: list of tuples: [(player_id, (mmr, create_date))]
        for i in range(number_of_players_to_pop):
            popped_player = player_dict.popitem()
            popped_players.append(popped_player)
        popped_player_ids = [f'<@{player[0]}>' for player in popped_players]
        if popped_player_ids:
            await lounge_queue_list_channel.send(f'The following players will have priority in the next mogi: {", ".join(popped_player_ids)}')
        
        # Rooms will be created for each list
        # Sort the dictionary by mmr in descending order
        sorted_players = sorted(player_dict.items(), key=lambda item: item[1][0], reverse=True)
        number_of_players = len(sorted_players)
        # thank you chatgpt
        groups_of_12 = [sorted_players[i:i + 12] for i in range(0, len(sorted_players), 12)]
        
        await create_queue_channels_and_categories(self.client, number_of_players, groups_of_12)
        
            
    @check.before_loop
    async def before_check(self):
        print('Lounge Queue started')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(lounge_queue(client))
