import discord
from discord.ext import commands
import DBA
import logging
from helpers.senders import send_raw_to_debug_channel

# from helpers.getters import get_lounge_guild
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGE


class WarnCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zwarn",
        description="Used to log warnings sent to players",
        guild_ids=LOUNGE,
        default_member_permissions=(discord.Permissions(moderate_members=True)),
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zwarn(
        self,
        ctx,
        player: discord.Option(str, description="Player name", required=True),  # type: ignore
        reason: discord.Option(
            str,
            description="What did you say to the player? (this does not get sent to them)",
            required=True,
        ),  # type: ignore
    ):
        await ctx.defer()
        # get player
        with DBA.DBAccess() as db:
            player_id = db.query(
                "SELECT player_id FROM player WHERE player_name = %s;", (player,)
            )[0][0]  # type: ignore
        if not player_id:
            await ctx.respond("Player not found")
            return

        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "INSERT INTO player_punishment (player_id, punishment_id, reason, admin_id, unban_date) VALUES (%s, %s, %s, %s, %s);",
                    (player_id, 3, reason, ctx.author.id, None),
                )
        except Exception as e:
            await send_raw_to_debug_channel(
                self.client, "/zwarn error - Failed to insert punishment record", e
            )
            logging.error(
                f"ERROR: /zwarn failed to insert punishment record for player [{player_id}] with message [{reason}]"
            )

        try:
            # user = await get_lounge_guild(self.client).fetch_member(player_id)
            await ctx.respond(f"<@{player_id}> has been warned: `{reason}`")
        except Exception as e:
            await ctx.respond(f"{player} has been warned: `{reason}`")
            await send_raw_to_debug_channel(
                self.client, f"/zwarn error - member [{player}] not found", e
            )
            logging.error(f"/zwarn error - member [{player}] not found")


def setup(client):
    client.add_cog(WarnCog(client))
