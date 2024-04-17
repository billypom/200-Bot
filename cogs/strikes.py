from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_exists
from config import LOUNGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class StrikesCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="strikes", description="See your strikes", guild_ids=LOUNGE
    )
    async def strikes(self, ctx: 'ApplicationContext'):
        await ctx.defer()
        x = await check_if_uid_exists(ctx.author.id)
        if x:
            pass
        else:
            await ctx.respond(
                "Player not found. Use `/verify <mkc link>` to register with Lounge"
            )
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;",
                    (ctx.author.id, 1),
                )
                if temp[0][0]:  # type: ignore
                    response = ""
                    for i in range(len(temp)):
                        response += (
                            f"`Strike {i+1}` Expires: <t:{str(int(temp[i][0]))}:F>\n"  # type: ignore
                        )
                    await ctx.respond(response)
                    return
                else:
                    pass
        except Exception:
            pass
        await ctx.respond("You have no strikes")
        return


def setup(client):
    client.add_cog(StrikesCog(client))
