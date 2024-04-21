import discord
from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_exists
from constants import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID


class ZStrikesCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zstrikes",
        description="See strikes for a specific player",
        guild_ids=LOUNGE,
        default_member_permissions=(discord.Permissions(moderate_members=True)),
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zstrikes(
        self, ctx, player: discord.Option(str, description="Player name", required=True)
    ):
        await ctx.defer()

        with DBA.DBAccess() as db:
            player_id = db.query(
                "SELECT player_id FROM player WHERE player_name = %s;", (player,)
            )[0][0]

        if player_id:
            pass
        else:
            await ctx.respond("Player not found")
            return

        x = await check_if_uid_exists(player_id)

        if x:
            pass
        else:
            await ctx.respond("Player not found.")
            return

        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;",
                    (player_id, 1),
                )
                if temp[0][0]:
                    response = ""
                    for i in range(len(temp)):
                        response += (
                            f"`Strike {i+1}` Expires: <t:{str(int(temp[i][0]))}:F>\n"
                        )
                    await ctx.respond(response)
                    return
        except Exception:
            pass

        await ctx.respond("This player has no strikes")


def setup(client):
    client.add_cog(ZStrikesCog(client))
