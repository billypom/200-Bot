import discord
import logging
from discord.ext import commands
from helpers.getters import get_lounge_guild, get_rank_id_list
from constants import LOUNGE, ADMIN_ROLE_ID


class ZRemoveAllRanks(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zremove_all_ranks",
        description="Removes all rank roles from all players in guild (iron bronze silver gold placement diamond etc)",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def zremove_all_ranks(self, ctx):
        """Scans every member in the guild. Removes all ranks.
        - Only used in season migration"""
        await ctx.defer()
        guild = get_lounge_guild(self.client)
        rank_id_list = await get_rank_id_list()
        for member in guild.members:
            for i in range(len(rank_id_list)):
                try:
                    test_role = guild.get_role(rank_id_list[i])
                    if test_role in member.roles:
                        await member.remove_roles(test_role)
                        logging.info(f"removed {test_role} from {member}")
                except Exception as e:
                    logging.info(e)
        await ctx.respond("All player rank roles have been removed")


def setup(client):
    client.add_cog(ZRemoveAllRanks(client))
