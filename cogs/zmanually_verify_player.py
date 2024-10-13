import discord
from discord.ext import commands
from DBA import DBAccess
from helpers import create_player
from helpers.getters import get_lounge_guild
from helpers.checkers import check_if_uid_exists
from helpers.checkers import check_if_mkc_user_id_used
from helpers.senders import send_to_verification_log
from constants import LOUNGE, ADMIN_ROLE_ID, UPDATER_ROLE_ID, PING_DEVELOPER
import vlog_msg


class ZManuallyVerifyPlayerCog(commands.Cog):
    """/zmanually_verify_player - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="zmanually_verify_player",
        description="Manually verify a player (no mkc api checks)",
        default_member_permissions=(discord.Permissions(moderate_members=True)),
        guild_ids=LOUNGE,
    )
    @commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
    async def zmanually_verify_player(
        self,
        ctx,
        player_id: discord.Option(
            str, "Discord ID of player to be verified", required=True
        ),  # type: ignore
        mkc_id: discord.Option(
            str,
            "Last numbers in MKC forum link. (e.g. popuko mkc_id = 154)",
            required=True,
        ),  # type: ignore
        country_code: discord.Option(
            str,
            "ISO 3166 Alpha-2 Code - https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes",
            required=True,
        ),  # type: ignore
    ):
        """Manually verify a player"""
        # mkc_player_id = registry id
        # mkc_user_id = forum id
        await ctx.defer(ephemeral=True)
        x = await check_if_uid_exists(int(player_id))
        if x:
            await ctx.respond(
                "The player id provided is already registered in the Lounge."
            )
            return
        else:
            pass
        verify_description = vlog_msg.success
        # Check if someone has verified as this user before...
        x = await check_if_mkc_user_id_used(mkc_id)
        if x:
            with DBAccess() as db:
                uh_oh_player = db.query(
                    "SELECT player_id FROM player WHERE mkc_id = %s;", (mkc_id,)
                )[0][0]  # type: ignore
            await ctx.respond(
                f"``Error 82:`` This MKC ID is already in use by {uh_oh_player}"
            )
            verify_description = vlog_msg.error4
            await send_to_verification_log(
                self.client,
                ctx,
                f"Error 82: {player_id} | {mkc_id} | {country_code}",
                f"{verify_description} | <@{uh_oh_player}> already using MKC **FORUM** ID {mkc_id}",
            )
            return
        else:
            # All clear. Roll out.
            try:
                member = await get_lounge_guild(self.client).fetch_member(player_id)
            except Exception:
                await ctx.respond(f"Unknown guild member: <@{player_id}>.")
                return
            try:
                x = await create_player(self.client, member, mkc_id, country_code)
            except Exception:
                await ctx.respond(
                    f"`Error 83:` Database error on create_player. Please create a support ticket and ping {PING_DEVELOPER}"
                )
                return
            try:
                await ctx.respond(x)
                await send_to_verification_log(
                    self.client,
                    ctx,
                    f"Player ID: {player_id}\nMKC ID: {mkc_id}\nCountry Code: {country_code}",
                    verify_description,
                )
            except Exception:
                await ctx.respond(
                    "`Error 84:` I was unable to respond and post in log channels for some reason..."
                )
                return
            return


def setup(client):
    client.add_cog(ZManuallyVerifyPlayerCog(client))
