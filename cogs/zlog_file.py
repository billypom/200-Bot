import discord
from discord.ext import commands
from config import LOUNGE, ADMIN_ROLE_ID

class LogFileCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zlog_file',
        description='gimme the log file pls thamks',
        guild_ids=LOUNGE
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def zlog_file(self, ctx):
        await ctx.defer()
        await ctx.send(file=discord.File('200lounge.log'))
        await ctx.respond('here u go')
        return

def setup(client):
    client.add_cog(LogFileCog(client))