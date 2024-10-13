import discord
from discord.ext import commands
import DBA
import logging
from helpers.getters import get_lounge_guild
from constants import LOUNGE, ADMIN_ROLE_ID, PLACEMENT_ROLE_ID


class ZAssignRanks(commands.Cog):
    """/zassign_ranks - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zassign_ranks",
        description="Assigns ranks to every member in guild, if they exist on the leaderboard",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(ADMIN_ROLE_ID)
    async def zassign_ranks(self, ctx):
        """
        # ADMIN ONLY
        Scans the entire guild for all members, assigns leaderboard ranks.
        - Should only be used for season migration
        """
        await ctx.defer()
        guild = get_lounge_guild(self.client)
        with DBA.DBAccess() as db:
            players = db.query("SELECT player_id, mmr FROM player", ())
        with DBA.DBAccess() as db:
            temp = db.query("SELECT rank_id, mmr_min, mmr_max FROM ranks", ())
        for i in range(len(players)):
            if players[i][1] is None:
                try:
                    role = guild.get_role(PLACEMENT_ROLE_ID)
                    member = guild.get_member(players[i][0])
                    await member.add_roles(role)
                except Exception as e:
                    pass
                continue
            for j in range(len(temp)):
                # If MMR > min & MMR < max, assign role
                if players[i][1] > temp[j][1]:
                    pass
                else:
                    continue
                if players[i][1] < temp[j][2]:
                    pass
                else:
                    continue
                try:
                    member = guild.get_member(players[i][0])
                    role = guild.get_role(temp[j][0])
                    await member.add_roles(role)
                    with DBA.DBAccess() as db:
                        db.execute(
                            "UPDATE player SET rank_id = %s WHERE player_id = %s;",
                            (temp[j][0], players[i][0]),
                        )
                    break
                except Exception as e:
                    logging.error(f"zassign_ranks.py | {players[i][0]} | {e}")
                    break
        await ctx.respond("done")


def setup(client):
    client.add_cog(ZAssignRanks(client))
