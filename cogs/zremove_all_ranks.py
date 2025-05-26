import discord
import logging
from discord.ext import commands
from helpers.getters import get_lounge_guild, get_rank_id_list
from constants import LOUNGE, ADMIN_ROLE_ID


class ZRemoveAllRanks(commands.Cog):
    """/zremove_all_ranks - slash command"""

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
        """
        # ADMIN ONLY
        Scans every member in the guild. Removes all ranks.
        - Only used in season migration
        """
        await ctx.defer()
        guild = get_lounge_guild(self.client)
        rank_id_list = await get_rank_id_list()
        role_list = []
        for rank in rank_id_list:
            role_list.append(guild.get_role(rank))
        for member in guild.members:
            for role in role_list:
                if role in member.roles:
                    try:
                        await member.remove_roles(role)
                    except Exception as e:
                        logging.error(
                            f"zremove_all_ranks | could not remove {role} from {member} | {e}"
                        )
            logging.info(f"removed roles from {member}")

        await ctx.respond("All player rank roles have been removed")


def setup(client):
    client.add_cog(ZRemoveAllRanks(client))
