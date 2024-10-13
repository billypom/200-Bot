import discord
from discord.ext import commands
from helpers import (
    set_uid_roles,
)
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE


class FixPlayerCog(commands.Cog):
    """/zfix_player - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zfix_player",
        description="Fixes player roles and nickname",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zfix_player(
        self,
        ctx,
        player: discord.Option(discord.Member, "@User", required=True),  # type: ignore
    ):
        """Sets discord roles for a specific user

        Args:
        - `player` (discord.Member): @user"""
        await ctx.defer()
        response = await set_uid_roles(self.client, player.id)
        if response:
            await ctx.respond(f"Player roles set for <@{player.id}>")
            return
        else:
            await ctx.respond("`Error 79:` Could not set roles")
            return


def setup(client):
    client.add_cog(FixPlayerCog(client))
