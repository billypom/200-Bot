import discord
from discord.ext import commands
import DBA
from helpers.checkers import check_if_uid_is_placement
from helpers.senders import send_to_debug_channel
from helpers import set_uid_roles
from config import REPORTER_ROLE_ID, LOUNGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class MMRPenaltyCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="mmr_penalty",
        description="Give a player an MMR penalty, with no strike",
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(REPORTER_ROLE_ID)
    async def mmr_penalty(
        self,
        ctx: ApplicationContext,
        player: discord.Option(str, description="Which player?", required=True),  # type: ignore
        mmr_penalty: discord.Option(
            int,
            description="How much penalty to apply? (positive number)",
            required=True,
        ),  # type: ignore
    ):
        """/mmr_penalty slash command - gives a player an mmr penalty"""
        await ctx.defer()
        mmr_penalty = abs(mmr_penalty)
        with DBA.DBAccess() as db:
            player_id = db.query(
                "SELECT player_id FROM player WHERE player_name = %s;", (player,)
            )[0][0]  # type: ignore
        if player_id:
            pass
        else:
            await ctx.respond("Player not found")
            return
        player_is_placement = await check_if_uid_is_placement(player_id)
        if player_is_placement:
            await ctx.respond("Cannot apply mmr penalty to a placement player")
            return
        try:
            with DBA.DBAccess() as db:
                curr_mmr = db.query(
                    "SELECT mmr FROM player WHERE player_id = %s;", (player_id,)
                )[0][0]  # type: ignore
                new_mmr = curr_mmr - mmr_penalty
                if new_mmr <= 0:
                    new_mmr = 1
                db.execute(
                    "UPDATE player SET mmr = %s WHERE player_id = %s;",
                    (new_mmr, player_id),
                )
            await ctx.respond(
                f"<@{player_id}> has been given a {mmr_penalty} mmr penalty"
            )
            await set_uid_roles(self.client, player_id)  # type: ignore
        except Exception as e:
            await send_to_debug_channel(self.client, ctx, f"/mmr_penalty error 38 {e}")
            await ctx.respond("`Error 38:` Could not apply penalty")


def setup(client):
    client.add_cog(MMRPenaltyCog(client))
