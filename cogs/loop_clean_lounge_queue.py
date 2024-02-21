from discord.ext import commands, tasks
from datetime import datetime
import DBA
import logging
from helpers.getters import get_lounge_guild
from helpers import delete_discord_channel, delete_discord_category


class CleanLoungeQueueCog(commands.Cog):
    def __init__(self, client):
        self.check.start()
        self.client = client

    def cog_unload(self):
        self.check.cancel()
    
    @tasks.loop(minutes=1)
    async def check(self):
        # Clean the lounge queue at :33
        current_time = datetime.now()
        if current_time.minute == 0:
            return
        if current_time.minute % 33 != 0:
            return
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
        if not channels_to_delete:
            return
            
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
        
            
    @check.before_loop
    async def before_check(self):
        print('Lounge queue cleaning process started')
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(CleanLoungeQueueCog(client))
        
        
        
        
        
