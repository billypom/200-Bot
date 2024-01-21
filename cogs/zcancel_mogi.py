from discord import Permissions
from discord.ext import commands
import DBA
from helpers.senders import send_to_debug_channel
from config import UPDATER_ROLE_ID, ADMIN_ROLE_ID, LOUNGE, MAX_PLAYERS_IN_MOGI

class CancelMogiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='zcancel_mogi',
        description='Cancel an ongoing mogi',
        default_member_permissions=(Permissions(moderate_members=True)),
        guild_ids=LOUNGE 
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zcancel_mogi(self, ctx):
        await ctx.defer()
        # Check for ongoing mogi in current channel
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
    bot.add_cog(CancelMogiCog(bot))
