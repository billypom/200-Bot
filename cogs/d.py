from discord.ext import commands
import DBA
from config import LOUNGE, PING_DEVELOPER
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_uid_in_specific_tier
from helpers.checkers import check_if_uid_can_drop
from helpers.senders import send_to_debug_channel

# Tier specific drop

class DCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='d',
        description='Drop from the mogi',
        guild_ids=LOUNGE
    )
    async def drop_mogi(self, ctx):
        await ctx.defer(ephemeral=True)
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
            return
        else:
            pass

        x = await check_if_uid_in_specific_tier(ctx.author.id, ctx.channel.id)
        if x:
            y = await check_if_uid_can_drop(ctx.author.id)
            if y:
                pass
            else:
                await ctx.respond('You cannot drop from an ongoing mogi')
                return

            with DBA.DBAccess() as db:
                tier_temp = db.query('SELECT t.tier_id, t.tier_name FROM tier as t JOIN lineups as l ON t.tier_id = l.tier_id WHERE player_id = %s AND t.tier_id = %s;', (ctx.author.id, ctx.channel.id))

            try:
                with DBA.DBAccess() as db:
                    db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
                    await ctx.respond(f'You have dropped from tier {tier_temp[0][1]}')
            except Exception as e:
                await send_to_debug_channel(self.bot, ctx, f'/d error 17 cant leave lineup {e}')
                await ctx.respond(f'``Error 17:`` Oops! Something went wrong. Contact {PING_DEVELOPER}')
                return

            try:
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT player_name FROM player WHERE player_id = %s;', (ctx.author.id,))
                    channel = self.bot.get_channel(tier_temp[0][0])
                    await channel.send(f'{temp[0][0]} has dropped from the lineup')
            except Exception as e:
                await send_to_debug_channel(self.bot, ctx, f'/d big error...WHAT! 1 {e}')
                # i should never ever see this...
            return
        else:
            await ctx.respond('You are not in a mogi')
            return

def setup(bot):
    bot.add_cog(DCog(bot))
