from discord import Color, Option
import json
import DBA
import time
import requests
import datetime
import vlog_msg
from discord.ext import commands
from helpers import set_uid_roles
from helpers import create_player
from helpers.getters import get_lounge_guild
from helpers.senders import send_to_verification_log
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_uid_exists
from helpers.checkers import check_if_mkc_user_id_used
from constants import LOUNGE, SUPPORT_CHANNEL_ID
import logging
import configparser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class VerifyCog(commands.Cog):
    """/verify - slash command"""

    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.seconds_since_last_login_delta_limit = config_file["LOUNGE"].getint(
            "SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT"
        )

    async def mkc_api_get(self, mkc_player_id: int) -> dict:
        """get mkc api data for player"""
        headers = {"User-Agent": "200-Lounge Bot"}
        try:
            mkcresponse = requests.get(
                "https://mkcentral.com/api/registry/players/" + str(mkc_player_id),
                headers=headers,
            )
            mkc_data = mkcresponse.json()
            buh = json.dumps(mkc_data)
            mkc_data_dict = json.loads(buh)
            return mkc_data_dict
        except Exception as e:
            print("mkc api get failed")
            print(e)
            return {}

    async def check_if_uid_has_mkc(self, uid: int) -> bool:
        """Check if this uid has a mkc id attached"""
        try:
            with DBA.DBAccess() as db:
                mkc_id = db.query(
                    "SELECT mkc_id FROM player WHERE player_id = %s;", (uid,)
                )[0][0]  # type: ignore
                if int(mkc_id) > 0:
                    return True
                else:
                    return False
        except Exception:
            return False

    @commands.slash_command(
        name="verify", description="Verify your MKC account", guild_ids=LOUNGE
    )
    async def verify(
        self,
        ctx: "ApplicationContext",
        message: Option(
            str,
            "MKC Link | https://mkcentral.com/en-us/registry/players/profile?id=930",
            required=True,
        ),  # type: ignore
    ):
        """Command to register yourself in the 200-Lounge system

        Args:
        - `message` (str): Link to your MKC forum or registry profile"""

        await ctx.defer(ephemeral=False)
        x = await check_if_uid_exists(ctx.author.id)
        has_mkc_account = await self.check_if_uid_has_mkc(ctx.author.id)
        if x and has_mkc_account:
            lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
            if lounge_ban:
                await ctx.respond(f"Unbanned after <t:{lounge_ban}:D>")
                return
            else:
                pass
            response = await set_uid_roles(self.client, ctx.author.id)
            if response:
                member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
                msg_response = f":flag_us:\nWelcome back to 200cc Lounge.\nYou have been given the role: <@&{response[0]}>\n\n:flag_jp:\n`200ccラウンジにおかえり！`\n<@&{response[0]}>`が割り当てられています`"
                await ctx.respond(msg_response)
                await member.send(msg_response)
            else:
                await ctx.respond(
                    f"``Error 29:`` Could not re-enter the lounge. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
                )
            return
        else:
            pass
        temp = message.split("/")
        mkc_player_id = temp[len(temp) - 1].split("=")[1]

        # Request registry data
        data = await self.mkc_api_get(mkc_player_id)
        mkc_user_id = data["id"]
        country_code = data["country_code"]
        is_banned = data["is_banned"]
        if data["discord"] is None:
            verify_description = f"Command issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nThe MKC link that was given by the command issuer has not attached this discord user to their profile"
            await ctx.respond(
                "This discord account is not linked to the provided MKCentral account"
            )
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return

        discord_id = int(data["discord"]["discord_id"])

        if discord_id != ctx.author.id:
            verify_description = f"Command issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nMKC Link connected *DISCORD ID* = {discord_id}\nThe user needs to link the correct discord account to their MKC profile."
            verify_description = (
                f"Wrong discord:mkc mapping\n{ctx.author.id}:{discord_id}"
            )
            await ctx.respond(
                "This discord account is not linked to the provided MKCentral account"
            )
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return

        if is_banned:
            # Is banned
            verify_description = vlog_msg.error3
            await ctx.respond(
                "You are MKC banned and cannot participate in 200cc Lounge"
            )
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return
        elif is_banned == -1:
            # Wrong link probably?
            await ctx.respond(
                "``Error 8:`` Oops! Something went wrong. Check your link or try again later"
            )
            return
        else:
            pass
        # Check if someone has verified as this user before...
        x, asdf = await check_if_mkc_user_id_used(mkc_user_id)
        if x:
            await ctx.respond(
                f"``Error 10:`` Oops! Something went wrong. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
            )
            verify_description = f"Command issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nMKC Link connected *DISCORD ID* = {discord_id}\nThe user needs to link the correct discord account to their MKC profile."
            await send_to_verification_log(
                self.client,
                ctx,
                f"Error 10: {message}",
                f"{verify_description} | <@{x}> is already using MKC ID {mkc_user_id}\n{x} is already using MKC ID {mkc_user_id}",  # type: ignore
            )
            return
        else:
            # All clear. Roll out.
            verify_description = vlog_msg.success
            member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
            x = await create_player(self.client, member, mkc_user_id, country_code)
            try:
                await ctx.respond(x)
                await member.send(x)
            except Exception:
                await ctx.respond("oops")
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return


def setup(client):
    client.add_cog(VerifyCog(client))
