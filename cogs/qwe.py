from discord.ext import commands
from helpers.getters import get_lounge_guild
from config import LOUNGE, ADMIN_ROLE_ID


class QWECog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='qwe',
        description='popuko testing',
        guild_ids=LOUNGE
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def qwe(self, ctx):
        member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
        print(member)
        await ctx.respond(member)
        

def setup(client):
    client.add_cog(QWECog(client))