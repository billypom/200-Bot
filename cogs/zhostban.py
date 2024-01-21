import discord
from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_exists
from config import LOUNGE, UPDATER_ROLE_ID, ADMIN_ROLE_ID

class ZHostBan(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zhostban',
        description='Add hostban to a player [Admin only]',
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zhostban(
        self,
        ctx,
        player: discord.Member
    ):
        await ctx.defer()
        x = await check_if_uid_exists(player.id)
        if x:
            pass
        else:
            await ctx.respond('Player not found')
            return
        with DBA.DBAccess() as db:
            temp = db.query('SELECT is_host_banned FROM player WHERE player_id = %s;', (player.id,))
        if temp[0][0]:
            with DBA.DBAccess() as db:
                db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (0, player.id))
                await ctx.respond(f'{player.mention} has been un-host-banned')
        else:
            with DBA.DBAccess() as db:
                db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (1, player.id))
                await ctx.respond(f'{player.mention} has been host-banned')

def setup(client):
    client.add_cog(ZHostBan(client))
