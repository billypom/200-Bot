import DBA
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_to_debug_channel
from config import LOUNGE, PING_DEVELOPER
import logging

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='l',
        description='List players in Lounge Queue',
        guild_ids=LOUNGE
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def listcog(self, ctx):
        await ctx.defer(ephemeral=False)
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query("SELECT p.player_name FROM player p JOIN lounge_queue_player l ON p.player_id = l.player_id ORDER BY l.create_date ASC;", ())
        except Exception:
            await ctx.respond(f'``Error 20:`` Oops! Something went wrong. {PING_DEVELOPER} help!!!!!')
            return
        response = '`Mogi List`:'
        for i in range(len(temp)):
            response = f'{response}\n`{i+1}.` {temp[i][0]}'
        response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
        await ctx.respond(response, delete_after=30)
        
        
        
def setup(bot):
    bot.add_cog(ListCog(bot))
