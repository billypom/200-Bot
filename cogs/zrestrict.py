import configparser
import discord
from discord.ext import commands
import DBA
import logging
from helpers.getters import get_unix_time_now
from helpers.getters import get_lounge_guild
from helpers.getters import get_discord_role
from helpers.senders import send_raw_to_debug_channel
from helpers.checkers import check_if_uid_is_chat_restricted
from constants import ADMIN_ROLE_ID, UPDATER_ROLE_ID, CHAT_RESTRICTED_ROLE_ID, LOUNGE


class RestrictCog(commands.Cog):
    """/zrestrict - slash command"""

    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.SECONDS_IN_A_DAY = config_file["LOUNGE"].getint("SECONDS_IN_A_DAY")

    @commands.slash_command(
        name="zrestrict",
        description="Chat restrict a player",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
    async def zrestrict(
        self,
        ctx,
        player: discord.Option(str, description="Player name", required=True),  # type: ignore
        reason: discord.Option(
            str,
            description="Explain why (1000 chars). This message is sent to the player",
            required=True,
        ),  # type: ignore
        ban_length: discord.Option(int, description="# of days", required=True),  # type: ignore
    ):
        """
        # STAFF ONLY
        Applied the RESTRICTED (1) punishment to a specific player
        - All messages sent by restricted users are immediately deleted by this bot

        Args:
        - `player` (str): Player name
        - `reason` (str): Official reason why they are getting Restricted
        - `ban_length` (int): Number of days banned
        """
        await ctx.defer()
        # get player
        try:
            with DBA.DBAccess() as db:
                player_id = int(
                    db.query(
                        "SELECT player_id FROM player WHERE player_name = %s;",
                        (player,),
                    )[0][0]  # type: ignore
                )
        except Exception:
            # player does not exist
            await ctx.respond("Player not found")
            return
        user = False
        is_chat_restricted = await check_if_uid_is_chat_restricted(player_id)

        # assign/unassign restricted role if member in server
        try:
            chat_restricted_role = get_discord_role(
                self.client, CHAT_RESTRICTED_ROLE_ID
            )
            user = await get_lounge_guild(self.client).fetch_member(player_id)
        except Exception as e:
            await send_raw_to_debug_channel(
                self.client,
                f"/zrestrict error - member [{player}] not found, roles not assigned.",
                e,
            )
            return
        # Currently chat restricted
        if is_chat_restricted:
            if chat_restricted_role in user.roles:
                # Unrestrict (remove roles)
                try:
                    await user.remove_roles(chat_restricted_role)
                except Exception:
                    pass
        # Not restricted
        else:
            if chat_restricted_role not in user.roles:
                # Restrict (add roles)
                try:
                    await user.add_roles(chat_restricted_role)
                except Exception:
                    pass
                # Notify user
                channel = self.client.get_channel(ctx.channel.id)  # type: ignore
                try:
                    dm_message = f"You have been restricted in MK8DX 200cc Lounge for {ban_length} days\nReason:\n> {reason}"
                    await user.send(dm_message)
                    # Notify staff member using the command that a DM was sent to the player
                    await channel.send(
                        f"<@{user.id}> was sent a DM:\n```{dm_message}```"
                    )
                except Exception:
                    await channel.send(
                        f"I tried to DM the user your message, but their Discord settings do not allow me to DM them."
                    )
                    pass

        # update database for restricted/unrestricted
        if is_chat_restricted:
            # unrestrict
            with DBA.DBAccess() as db:
                db.execute(
                    "UPDATE player SET is_chat_restricted = %s where player_id = %s;",
                    (0, player_id),
                )
            await ctx.respond(f"<@{player_id}> has been unrestricted")
        else:
            # restrict
            unix_now = await get_unix_time_now()
            unix_ban_length = ban_length * self.SECONDS_IN_A_DAY
            unban_date = unix_now + unix_ban_length
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "UPDATE player SET is_chat_restricted = %s where player_id = %s;",
                        (1, player_id),
                    )
            except Exception as e:
                await send_raw_to_debug_channel(
                    self.client,
                    f"/zrestrict error - Failed to set is_chat_restricted from DB. Player [{player}] does not exist maybe?",
                    e,
                )
                return
            try:
                with DBA.DBAccess() as db:
                    db.execute(
                        "INSERT INTO player_punishment (player_id, punishment_id, reason, admin_id, unban_date, ban_length) VALUES (%s, %s, %s, %s, %s, %s);",
                        (player_id, 1, reason, ctx.author.id, unban_date, ban_length),
                    )
            except Exception as e:
                await send_raw_to_debug_channel(
                    self.client,
                    "/zrestrict error - Failed to insert punishment record",
                    e,
                )
                logging.error(
                    f"ERROR: /zrestrict failed to insert punishment record for player [{player}, {player_id}] with length of [{ban_length} days] with message [{reason}]"
                )
                return
            await ctx.respond(f"<@{player_id}> has been restricted")
            return


def setup(client):
    client.add_cog(RestrictCog(client))
