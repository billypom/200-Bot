import DBA
import datetime
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_to_debug_channel
from helpers.getters import get_tier_id_list
from helpers import start_mogi
from config import LOUNGE, PING_DEVELOPER, SQUAD_QUEUE_CHANNEL_ID, MAX_PLAYERS_IN_MOGI




class CanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='c',
        description='🙋 Can up for a mogi',
        guild_ids=LOUNGE
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def c(self, ctx):
        await ctx.defer(ephemeral=True)
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
            return
        # Add player to the timed queue
        
        # Retrieve the next queue time
        
        # Provide feedback to player that they have joined the a queue that will start at a particular time
        

        return
        

        

def setup(bot):
    bot.add_cog(CanCog(bot))
