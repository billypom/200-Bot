import discord
from discord.ext import commands
from config import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID
from helpers import delete_queue_channels_and_categories


class DeleteLoungeQueueRoomsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='zdelete_lounge_queue_rooms',
        description='test delete rooms',
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zdelete_lounge_queue_rooms(self, ctx):
        await ctx.defer()
        deleted = await delete_queue_channels_and_categories(self.client)
        if deleted:
            print('YAY')
            await ctx.respond('yay')
        else:
            print('no..........')
            await ctx.respond('no........')


def setup(client):
    client.add_cog(DeleteLoungeQueueRoomsCog(client))