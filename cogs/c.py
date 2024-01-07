import DBA
import datetime
from discord.ext import commands
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.senders import send_to_debug_channel
from helpers.getters import get_tier_id_list
from helpers import start_mogi
from config import LOUNGE, PING_DEVELOPER, SQUAD_QUEUE_CHANNEL_ID, MAX_PLAYERS_IN_MOGI

# Tier specific can up


class CCog(commands.Cog):
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
        else:
            pass

        # Get the current lineup count - only players that were not in the last mogi (mogi_start_time not null)
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s AND mogi_start_time is NULL;', (ctx.channel.id,))
                count = temp[0][0]
        except Exception as e:
            await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {PING_DEVELOPER}.')
            await send_to_debug_channel(self.client, ctx, f'/c error 18 lineup not found? {e}')
            return
        # await send_to_debug_channel(client, ctx, f'count: {count}')

        # ADDITIONAL SUBS SHOULD BE ABLE TO JOIN NEXT MOGI
        # if count == MAX_PLAYERS_IN_MOGI:
        #     await ctx.respond('Mogi is full')
        #     return

        # Check for canning in same tier
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
            if temp:
                if temp[0][0] == ctx.author.id:
                    await ctx.respond('You are already in the mogi')
                    return
                else:
                    pass
        except Exception:
            pass
            # await ctx.respond(f'``Error 46:`` Something went wrong! Contact {config.PING_DEVELOPER}.')
            # await send_to_debug_channel(client, ctx, e)
            # return
        
        # Check for squad queue channel
        if ctx.channel.id == SQUAD_QUEUE_CHANNEL_ID:
            await ctx.respond('Use !c to join squad queue')
            return
        
        if ctx.channel.id in await get_tier_id_list():
            pass
        else:
            tiers = ''
            for i in await get_tier_id_list():
                if i == SQUAD_QUEUE_CHANNEL_ID:
                    continue
                tiers += f'<#{i}> '
            await ctx.respond(f'`/c` only works in tier channels.\n\n{tiers}')
            return

        # Add player to lineup
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO lineups (player_id, tier_id, last_active) values (%s, %s, %s);', (ctx.author.id, ctx.channel.id, datetime.datetime.now()))
        except Exception as e:
            await ctx.respond('``Error 16:`` Player not registered.\nTry `/verify`.')
            await send_to_debug_channel(self.client, ctx, f'/c error 16 unable to join {e}')
            return
        await ctx.respond('You have joined the mogi! You can /d in `15 seconds`')
        channel = self.client.get_channel(ctx.channel.id)
        await channel.send(f'{ctx.author.display_name} has joined the mogi!', delete_after=300)
        count+=1
        # Check for full lineup
        if count == MAX_PLAYERS_IN_MOGI:
            # start the mogi, vote on format, create teams
            mogi_started_successfully = await start_mogi(ctx)
            if mogi_started_successfully == 1:
                pass
                # Chooses a host. Says the start time
            elif mogi_started_successfully == 0:
                channel = self.client.get_channel(ctx.channel.id)
                await channel.send(f'``Error 45:`` Failed to start mogi. {PING_DEVELOPER}!!!!!!!!!!!!')
                return
            elif mogi_started_successfully == 2:
                channel = self.client.get_channel(ctx.channel.id)
                await channel.send(f'``Error 54:`` Failed to start mogi. {PING_DEVELOPER}!!!!!!!!!!!!!!')
                return
        elif count == 6 or count == 11:
            channel = self.client.get_channel(ctx.channel.id)
            await channel.send(f'@here +{12-count}')
        return


        return

def setup(bot):
    bot.add_cog(CCog(bot))
