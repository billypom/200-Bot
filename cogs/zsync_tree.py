from discord.ext import commands
from discord import Permissions
from config import LOUNGE, ADMIN_ROLE_ID
import logging

class SyncTreeCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zsync_tree',
        description='Sync guild commands',
        guild_ids=LOUNGE,
        default_member_permissions=(Permissions(moderate_members=True))
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def zsync_tree(self, ctx):
        
        await ctx.respond('N*SYNC')
        return
        
        

def setup(client):
    client.add_cog(SyncTreeCog(client))