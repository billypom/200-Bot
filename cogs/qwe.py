from discord.ext import commands
from helpers.getters import get_lounge_guild
from config import LOUNGE, ADMIN_ROLE_ID
import requests

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
        headers = {'User-Agent': '200 Lounge Bot'}
        response = requests.get(f'https://200-lounge.com/api/all_players?player_id={ctx.author.id}', headers=headers)
        response = response.json()
        member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
        await ctx.respond(f'{member} ```json\n{response}\n```')
        
        

def setup(client):
    client.add_cog(QWECog(client))