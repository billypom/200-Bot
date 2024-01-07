from discord.ext import commands, tasks
from datetime import datetime
import DBA
from config import PING_DEVELOPER
from helpers.senders import send_raw_to_debug_channel

class mogi_timer(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(minutes=1)
    async def check(self):
        # Get the current time
        current_time = datetime.now()
        # Check if the current minute is one of the 15-minute intervals
        if current_time.minute % 15 != 0:
            return

        # Query for players in lineup table, sort by create_date ASC - people who can up first have priority
        #   player_id: {mmr, create_date}
        
        # Split lineup list into groups of 12 max (order matters)
        # i.e. [1,2,3,4,5,6,7,8,9,10,11,12], [13,14,15,16,17,18,19,20,21,22,23,24], [25,26,27]
        
        # Lists with exactly 12 items will be sorted by player mmr
        
        # Rooms will be created for each list
        
        # Leftover players will receive a DM or ping to perform some action to stay in the queue for the next scheduled match
        #   i.e. press the can button again, react to a message, or maybe type any message in chat
        
    
    @check.before_loop
    async def before_check(self):
        print('mogi timer started')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(mogi_timer(client))