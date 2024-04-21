import configparser
from discord import Option
from discord.ext import commands
import DBA
import logging
from constants import REPORTER_ROLE_ID, LOUNGE
from helpers.getters import get_unix_time_now
from helpers.checkers import check_if_uid_is_chat_restricted
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class UnstrikeCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.SECONDS_IN_A_DAY = config_file["LOUNGE"].getint("SECONDS_IN_A_DAY")

    @commands.slash_command(
        name="unstrike_player",
        description="Remove strike by ID",
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(REPORTER_ROLE_ID)
    async def unstrike(
        self,
        ctx: "ApplicationContext",
        strike_id: Option(int, description="Enter the strike ID", required=True),  # type: ignore
    ):
        await ctx.defer()
        is_chat_restricted = await check_if_uid_is_chat_restricted(ctx.author.id)
        if is_chat_restricted:
            await ctx.respond("You cannot use this command")
            return
        # Check if strike exists
        unix_now = await get_unix_time_now()
        with DBA.DBAccess() as db:
            try:
                temp = db.query(
                    "SELECT strike_id, player_id, reason, mmr_penalty, penalty_applied, UNIX_TIMESTAMP(create_date) FROM strike WHERE strike_id = %s;",
                    (strike_id,),
                )
                _ = int(temp[0][0])  # type: ignore
                player_id = int(temp[0][1])  # type: ignore
                _ = str(temp[0][2])  # type: ignore
                mmr_penalty = int(temp[0][3])  # type: ignore
                penalty_applied = bool(temp[0][4])  # type: ignore
                unix_strike = int(temp[0][5])  # type: ignore
            except Exception:
                await ctx.respond("Strike ID not found")
                return
        if unix_now - unix_strike > self.SECONDS_IN_A_DAY:
            await ctx.respond("You cannot remove this strike. Too old")
            return
        if player_id == ctx.author.id:
            await ctx.respond("You cannot unstrike yourself.")
            return
        if penalty_applied:
            # Undo the penalty
            with DBA.DBAccess() as db:
                # Get player mmr
                try:
                    player_mmr = int(
                        db.query(
                            "SELECT mmr FROM player WHERE player_id = %s;", (player_id,)
                        )[0][0]  # type: ignore
                    )
                except Exception:
                    logging.info(f"UNSTRIKE Failed - {player_id} not found")
                    await ctx.respond(
                        "Something went wrong. Player on strike not found."
                    )
                    return

                # Do math to remove penalty
                player_new_mmr = max(player_mmr + mmr_penalty, 1)

                # Update player MMR
                try:
                    db.execute(
                        "UPDATE player SET mmr = %s WHERE player_id = %s;",
                        (player_new_mmr, player_id),
                    )
                except Exception:
                    logging.info(
                        f"UNSTRIKE Failed - {player_id} MMR ({player_mmr}) could not be updated to ({player_new_mmr})"
                    )
                    await ctx.respond(
                        "Something went wrong. Player MMR could not be updated."
                    )

        # Delete the strike
        try:
            with DBA.DBAccess() as db:
                db.execute("DELETE FROM strike WHERE strike_id = %s;", (strike_id,))
        except Exception:
            logging.warning(
                f"/unstrike_player | unable to delete strike id: {strike_id}"
            )
            await ctx.respond("Something went wrong. Strike could not be deleted.")
            return
        await ctx.respond(f"Strike ID {strike_id} has been removed.")


def setup(client):
    client.add_cog(UnstrikeCog(client))
