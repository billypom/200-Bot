from discord import Permissions
from discord.ext import commands
from helpers import set_uid_roles
from constants import LOUNGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class FixRolesCog(commands.Cog):
    """/fix_roles - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="fix_roles",
        description="Fix your player roles and nickname",
        guild_ids=LOUNGE,
        default_member_permissions=(Permissions(administrator=True)),
    )
    async def fix_roles(self, ctx: "ApplicationContext"):
        """Sets discord roles for the command issuer"""
        await ctx.defer()
        response = await set_uid_roles(self.client, ctx.author.id)
        if response:
            await ctx.respond(f"Player roles set for <@{ctx.author.id}>")
        else:
            await ctx.respond("`Error 79b:` Could not set roles")


def setup(client):
    """Adds this command (cog) to the bot (client)"""
    client.add_cog(FixRolesCog(client))
