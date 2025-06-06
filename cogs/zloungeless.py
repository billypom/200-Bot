import configparser
import discord

# from i18n import Translator
from discord.ext import commands
import DBA
from helpers import remove_rank_roles_from_uid
from helpers import set_uid_roles
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_unix_time_now
from helpers.getters import get_lounge_guild
from helpers.getters import get_discord_role
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, LOUNGELESS_ROLE_ID, LOUNGE


class LoungelessCog(commands.Cog):
    """/zloungeless - slash command"""

    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.SECONDS_IN_A_DAY = config_file["LOUNGE"].getint("SECONDS_IN_A_DAY")

    @commands.slash_command(
        name="zloungeless",
        description="Apply the loungeless role to a player",
        guild_ids=LOUNGE,
        default_member_permissions=(discord.Permissions(moderate_members=True)),
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zloungeless(
        self,
        ctx,
        player: discord.Option(str, description="Player name", required=True),  # type: ignore
        reason: discord.Option(
            str, description="Explain why (1000 chars)", required=True
        ),  # type: ignore
        ban_length: discord.Option(int, description="# of days", required=True),  # type: ignore
    ):
        """
        # STAFF ONLY
        Applied the LOUNGELESS (2) punishment to a specific player

        Args:
        - `player` (str): Player name
        - `reason` (str): Official reason why they are getting Loungeless
        - `ban_length` (int): Number of days banned
        """
        await ctx.defer()
        # Retrieve player from DB
        with DBA.DBAccess() as db:
            player_id = int(
                db.query(
                    "SELECT player_id FROM player WHERE player_name = %s;", (player,)
                )[0][0]  # type: ignore
            )

        if not player_id:
            await ctx.respond("Player not found")
            return
        # channel we sent admin command from
        channel = self.client.get_channel(ctx.channel.id)  # type: ignore
        guild = get_lounge_guild(self.client)
        loungeless_role = get_discord_role(self.client, LOUNGELESS_ROLE_ID)
        try:
            # Get user information
            user = await guild.fetch_member(player_id)
            await user.add_roles(loungeless_role)
            await remove_rank_roles_from_uid(self.client, player_id)
            # Notify the user of their punishment
            dm_message = f"You have been banned from competing in MK8DX 200cc Lounge.\nBan length: {ban_length} days\nReason:\n> {reason}"
            await user.send(dm_message)
            # Notify the staff member using the command that the player was DM'd
            await channel.send(f"<@{player_id}> was sent a DM:\n```{dm_message}```")
        except Exception as e:
            await channel.send(
                "I tried to DM the user your message, but their Discord settings do not allow me to DM them."
            )
            await send_raw_to_debug_channel(
                self.client,
                "/zloungeless error - Failed to send Direct Message to user",
                e,
            )
        # Regardless of if we can reach the user or not, we need to update the database to apply their punishment
        unix_now = await get_unix_time_now()
        unix_ban_length = ban_length * self.SECONDS_IN_A_DAY
        unban_date = unix_now + unix_ban_length
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "INSERT INTO player_punishment (player_id, punishment_id, reason, admin_id, unban_date, ban_length) VALUES (%s, %s, %s, %s, %s, %s);",
                    (player_id, 2, reason, ctx.author.id, unban_date, ban_length),
                )
        except Exception as e:
            await send_raw_to_debug_channel(
                self.client,
                "/zloungeless error - Failed to insert punishment record",
                e,
            )
        await ctx.respond(f"Loungeless added to <@{player_id}>")


def setup(client):
    client.add_cog(LoungelessCog(client))
