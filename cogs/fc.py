import discord
from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_banned_characters
from helpers.checkers import check_if_uid_exists
from helpers.senders import send_to_verification_log
from helpers import update_friend_code
import vlog_msg
from config import LOUNGE

class FriendCodeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='fc',
        description='Display or set your friend code',
        guild_ids=LOUNGE,
    )
    async def friend_code(self, ctx, fc: discord.Option(str, 'XXXX-XXXX-XXXX', required=False)):
        if fc is None:
            await ctx.defer()
            lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
            if lounge_ban:
                await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>', delete_after=30)
                return
            else:
                pass
            try:
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT fc FROM player WHERE player_id = %s;', (ctx.author.id, ))
                    await ctx.respond(temp[0][0])
            except Exception:
                await ctx.respond('``Error 12:`` No friend code found. Use ``/fc XXXX-XXXX-XXXX`` to set.')
        else:
            await ctx.defer(ephemeral=True)
            lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
            if lounge_ban:
                await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>', delete_after=30)
                return
            else:
                pass
            y = await check_if_banned_characters(fc)
            if y:
                await send_to_verification_log(self.bot, ctx, fc, vlog_msg.error1)
                return '``Error 13:`` Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'
            x = await check_if_uid_exists(ctx.author.id)
            if x:
                pass
            else:
                return '``Error 25:`` Player does not exist. Use `/verify <mkc link>` to register with the Lounge.'
            confirmation_msg = await update_friend_code(self.client, ctx, fc)
            await ctx.respond(confirmation_msg)

def setup(client):
    client.add_cog(FriendCodeCog(client))
