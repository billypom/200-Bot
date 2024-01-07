import DBA
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_mogi_is_ongoing
from config import LOUNGE

class TeamsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='teams',
        description='See the teams in the ongoing mogi',
        guild_ids=LOUNGE  # Make sure to define LOUNGE
    )
    async def teams(self, ctx):
        await ctx.defer()
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
        x = await check_if_mogi_is_ongoing(ctx)
        if x:
            pass
        else:
            await ctx.respond('There is no ongoing mogi')
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
                if temp:
                    response = temp[0][0]
                else:
                    response = "Use `/teams` in a tier channel"
        except Exception:
            response = "Use `/teams` in a tier channel"
        await ctx.respond(response)

def setup(bot):
    bot.add_cog(TeamsCog(bot))
