from discord.ext import commands
import DBA
from config import LOUNGE, PING_DEVELOPER
from helpers.checkers import check_if_uid_is_lounge_banned

class LCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='l',
        description='Show the mogi list',
        guild_ids=LOUNGE
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def mogi_list(self, ctx):
        await ctx.defer()
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
        try:
            with DBA.DBAccess() as db:
                temp = db.query("SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;", (ctx.channel.id,))
        except Exception:
            await ctx.respond(f'``Error 20:`` Oops! Something went wrong. Please contact {PING_DEVELOPER}')
            return
        response = '`Mogi List`:'
        for i in range(len(temp)):
            response = f'{response}\n`{i+1}.` {temp[i][0]}'
        response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
        await ctx.respond(response, delete_after=30)
        return

def setup(bot):
    bot.add_cog(LCog(bot))
