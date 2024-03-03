import DBA
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_to_debug_channel
from config import LOUNGE, LOUNGE_QUEUE_JOIN_CHANNEL_ID
import logging

class DropCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='d',
        description='Drop from Lounge Queue',
        guild_ids=LOUNGE
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def d(self, ctx):
        await ctx.defer(ephemeral=False)
        sent_from_channel_id = ctx.channel.id
        player_id = ctx.author.id
        if sent_from_channel_id != LOUNGE_QUEUE_JOIN_CHANNEL_ID:
            await ctx.respond('You cannot use this command in this channel', delete_after=30)
            return
        
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>')
            return
        # Check if player already in queue
        try:
            with DBA.DBAccess() as db:
                retrieved_id = db.query('SELECT player_id FROM lounge_queue_player WHERE player_id = %s;', (player_id,))[0][0]
        except Exception as e:
            logging.warning(f'DropCog error: unable to retrieve data from lounge_queue_player | {e}')
            await ctx.respond('You are not in the queue.', delete_after=30)
            return
        
        # Remove player from the queue
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lounge_queue_player WHERE player_id = %s;', (player_id,))
        except Exception as e:
            logging.warning(f'DropCog error: unable to remove player from lounge_queue_player | {e}')
            return
        
        try:
            with DBA.DBAccess() as db:
                number_of_players = db.query('SELECT COUNT(*) from lounge_queue_player;', ())[0][0]
        except Exception as e:
            logging.warning(f'DropCog error: unable to count player from lounge_queue_player | {e}')
            return

        await ctx.respond(f'You have been removed from the queue `[{number_of_players} players]`')
        
def setup(bot):
    bot.add_cog(DropCog(bot))
