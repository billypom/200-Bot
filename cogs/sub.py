import logging
from discord.ext import commands
import DBA
from config import LOUNGE, LOUNGE_QUEUE_SUB_CHANNEL_ID, TAGS_ROLE_ID
from helpers import SubJoin
from helpers.getters import get_unix_time_now

class SubCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='sub',
        description='Ask for a sub',
        guild_ids=LOUNGE,
    )
    async def sub(self, ctx):
        sub_view = SubJoin(self.client, ctx.channel.id)
        sub_channel = self.client.get_channel(LOUNGE_QUEUE_SUB_CHANNEL_ID)
        mogi_channel = self.client.get_channel(ctx.channel.id)
        try:
            with DBA.DBAccess() as db:
                room_data = db.query('SELECT min_mmr, max_mmr FROM lounge_queue_channel WHERE channel_id = %s;', (ctx.channel.id,))[0]
                min_mmr = room_data[0]
                max_mmr = room_data[1]
        except Exception as e:
            logging.warning(f'/sub error | unable to retrieve data from lounge_queue_channel | {e}')
            
        unix_time_now = await get_unix_time_now()
        delete_message_time = unix_time_now + 1200
        await sub_channel.send(f'<@&{TAGS_ROLE_ID}> - {mogi_channel} is looking for a sub in MMR range: [{min_mmr} - {max_mmr}]\nMessage will auto-delete <t:{delete_message_time}:R>', view=sub_view, delete_after=1200)
        await ctx.respond('Sub has been requested')

def setup(client):
    client.add_cog(SubCog(client))
