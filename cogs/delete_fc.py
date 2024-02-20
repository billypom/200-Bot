import discord
from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_exists
from config import LOUNGE

class DeleteFriendCodeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='delete_fc',
        description='Delete your friend code from the system',
        guild_ids=LOUNGE,
    )
    async def friend_code(self, ctx):
        await ctx.defer(ephemeral=True)
        x = await check_if_uid_exists(ctx.author.id)
        if not x:
            await ctx.respond('``Error 25:`` Player does not exist. Use `/verify <mkc link>` to register with the Lounge.')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('UPDATE player SET friend_code = NULL WHERE player_id = %s;', (ctx.author.id,))
        except Exception as e:
            await ctx.respond('Oops! Unable to remove your friend code...')
            return

def setup(client):
    client.add_cog(DeleteFriendCodeCog(client))
