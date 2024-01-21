from discord import Permissions
from discord.ext import commands
from config import LOUNGE, ADMIN_ROLE_ID
import logging

class TailLogCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='ztail_log',
        description='Last 10 lines of log file',
        guild_ids=LOUNGE,
        default_member_permissions=(Permissions(administrator=True)),
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def ztail_log(self, ctx):
        lines = []
        
        try:
            with open('200lounge.log', 'r') as file:
                # Read all lines into a list
                lines = file.readlines()
        except FileNotFoundError:
            await ctx.respond('File not found')
            return
        except Exception as e:
            await ctx.respond('An error occurred')
            logging.info(f'ztail_log error | {e}')
            return
        
        last_10_lines = lines[-10:]
        # Create string, each line < 100 char long
        response = '\n'.join([line[:200] for line in last_10_lines])
        # Send message
        await ctx.respond(f'```{response}```')
        return
        
        

def setup(client):
    client.add_cog(TailLogCog(client))