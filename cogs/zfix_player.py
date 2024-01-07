import discord
from discord.ext import commands
from helpers import set_uid_roles  # Replace 'your_module' with the actual name of your module
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID

class FixPlayerCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zfix_player',
        description='Fixes player roles and nickname'
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zfix_player(
        self,
        ctx,
        player: discord.Option(discord.Member, '@User', required=True)
    ):
        await ctx.defer()
        response = await set_uid_roles(self.client, player.id)
        if response:
            await ctx.respond(f'Player roles set for <@{player.id}>')
            return
        else:
            await ctx.respond('`Error 79:` Could not set roles')
            return

def setup(client):
    client.add_cog(FixPlayerCog(client))