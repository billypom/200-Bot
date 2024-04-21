from discord import Option
from discord.ext import commands
import DBA
from helpers.senders import send_to_verification_log
from helpers.senders import send_to_debug_channel
from helpers.checkers import check_if_banned_characters
from constants import LOUNGE, REPORTER_ROLE_ID
import vlog_msg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class ScoreSwapCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="swapscore",
        description="Swap the score of two players on the same team",
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(REPORTER_ROLE_ID)
    async def swapscore(
        self,
        ctx: "ApplicationContext",
        player1: Option(str, "Player name", required=True),  # type: ignore
        player2: Option(str, "Player name", required=True),  # type: ignore
        mogi_id: Option(int, "Mogi ID", required=True),  # type: ignore
    ):
        await ctx.defer()
        x = await check_if_banned_characters(player1)
        if x:
            await ctx.respond("Invalid player1 name")
            await send_to_verification_log(self.client, ctx, player1, vlog_msg.error1)
            return
        else:
            pass
        y = await check_if_banned_characters(player2)
        if y:
            await ctx.respond("Invalid player2 name")
            await send_to_verification_log(self.client, ctx, player1, vlog_msg.error1)
            return
        else:
            pass
        id1 = 0
        id2 = 0
        idmogi = 0
        try:
            with DBA.DBAccess() as db:
                id1 = db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;", (player1,)
                )[0][0]  # type: ignore
                id2 = db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;", (player2,)
                )[0][0]  # type: ignore
                idmogi = db.query(
                    "SELECT mogi_id FROM mogi WHERE mogi_id = %s;", (mogi_id,)
                )[0][0]  # type: ignore
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f"error 35 {e}")
            await ctx.respond(
                "``Error 35:`` One of your inputs is invalid. Please try again"
            )
            return
        try:
            with DBA.DBAccess() as db:
                id1_score = db.query(
                    "SELECT score FROM player_mogi WHERE player_id = %s AND mogi_id = %s;",
                    (id1, idmogi),
                )[0][0]  # type: ignore
                id2_score = db.query(
                    "SELECT score FROM player_mogi WHERE player_id = %s AND mogi_id = %s;",
                    (id2, idmogi),
                )[0][0]  # type: ignore
                db.execute(
                    "UPDATE player_mogi SET score = %s WHERE player_id = %s AND mogi_id = %s",
                    (id1_score, id2, idmogi),
                )
                db.execute(
                    "UPDATE player_mogi SET score = %s WHERE player_id = %s AND mogi_id = %s",
                    (id2_score, id1, idmogi),
                )
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f"error 36 {e}")
            await ctx.respond("``Error 36:`` Oops! Something went wrong.")
            return
        await ctx.respond(
            f"Scores swapped successfully.\n{player1} {id1_score} -> {id2_score}\n{player2} {id2_score} -> {id1_score}"
        )
        return


def setup(client):
    client.add_cog(ScoreSwapCog(client))
