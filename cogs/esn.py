from discord.ext import commands
import DBA
import math
from config import LOUNGE, MAX_PLAYERS_IN_MOGI
from helpers import get_unix_time_now
from helpers.senders import send_to_debug_channel

class ESNCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='esn',
        description='End (mogi) Start New (mogi)',
        guild_ids=LOUNGE
    )
    async def esn(self, ctx):
        await ctx.defer()

        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT UNIX_TIMESTAMP(mogi_start_time) FROM lineups WHERE tier_id = %s AND can_drop = 0 ORDER BY create_date DESC LIMIT %s;', (ctx.channel.id, 1))
            mogi_start_time = temp[0][0]
        except Exception:
            await ctx.respond('`Error 62:` Mogi has not started')
            return

        unix_now = await get_unix_time_now()
        minutes_since_start = math.floor((unix_now - mogi_start_time) / 60)

        if minutes_since_start > 25:
            pass
        else:
            await ctx.respond(f'Please wait {25 - minutes_since_start} more minutes to use `/esn`')
            return

        try:
            with DBA.DBAccess() as db:
                players = db.query('SELECT player_id FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
                for player in players:
                    with DBA.DBAccess() as db:
                        db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], ctx.channel.id))
                await ctx.respond('New mogi started')
        except Exception as e:
            await send_to_debug_channel(self.bot, ctx, f'esn error 2: {e}')
            await ctx.respond('`Error 63:` esners')
            return

        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
            if len(temp) == 12:
                pass
            else:
                await ctx.respond('There is no mogi being played in this tier.')
                return
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f'Cancel Error Check: {e}')
            return
        # Delete from lineups & sub_leaver
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
                # db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
            await ctx.respond('The mogi has been cancelled')
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f'Cancel Error Deletion:{e}')
            return

def setup(bot):
    bot.add_cog(ESNCog(bot))
