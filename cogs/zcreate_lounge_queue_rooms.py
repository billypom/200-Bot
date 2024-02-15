import discord
from discord.ext import commands
from config import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID
from helpers import create_queue_channels_and_categories


class CreateLoungeQueueRoomsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zcreate_lounge_queue_rooms',
        description='test create rooms',
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zcreate_lounge_queue_rooms(self, ctx, number_of_players: discord.Option(int, 'Amount of MMR to add to the player', required=True)):
        await ctx.defer()
        created = await create_queue_channels_and_categories(self.client, number_of_players)
        if created:
            print('YAY')
            await ctx.respond('yay')
        else:
            print('no..........')
            await ctx.respond('no...........')
        return
        

def setup(client):
    client.add_cog(CreateLoungeQueueRoomsCog(client))