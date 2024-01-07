from discord.ext import commands
from config import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOOP_EXTENSIONS, COMMAND_EXTENSIONS, ADMIN_COMMAND_EXTENSIONS

class ReloadCogsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zreload_cogs',
        description='[DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING]'
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zreload_cogs(self, ctx):
        for extension in LOOP_EXTENSIONS:
            self.client.reload_extension(f'cogs.{extension}')
            # await send_raw_to_debug_channel(client, 'Loop cogs reloaded', extension)
            
        for extension in COMMAND_EXTENSIONS:
            self.client.reload_extension(f'cogs.{extension}')
            # await send_raw_to_debug_channel(client, 'Command cogs reloaded', extension)
            
        for extension in ADMIN_COMMAND_EXTENSIONS:
            self.client.reload_extension(f'cogs.{extension}')
            # await send_raw_to_debug_channel(client, 'Admin command cogs reloaded', extension)
            
        await ctx.respond('All cogs reloaded successfully :smile:')

def setup(client):
    client.add_cog(ReloadCogsCog(client))
