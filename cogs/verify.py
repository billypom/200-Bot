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
from constants import LOUNGE, PING_DEVELOPER, SUPPORT_CHANNEL_ID
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

    async def update_mkc_for_uid(self, uid, mkc_id, country_code):
        """
        Updates a uid's mkc_id and country code, for the new website mkcentral.com

        return True or False on success or failure
        """
        logging.info(f"Updating {uid} - mkc={mkc_id}, country={country_code}")
        try:
            with DBA.DBAccess() as db:
                db.execute(
                    "UPDATE player SET mkc_id = %s, country_code = %s WHERE player_id = %s",
                    (mkc_id, country_code, uid),
                )
            return True
        except Exception as e:
            logging.info(f"verify.py, update_mkc_for_uid | {e}")
            return False

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
        if "mariokartcentral" in message:
            await ctx.respond("Wrong website. Use https://mkcentral.com")
            return
        if "mkcentral.com" not in message:
            await ctx.respond("Please provide a MKCentral profile link")
            return
        if "/registry/players" not in message:
            await ctx.respond("Please provide a MKCentral profile link")
            return

        uid_exists = await check_if_uid_exists(ctx.author.id)
        has_mkc_account = await self.check_if_uid_has_mkc(ctx.author.id)
        if uid_exists and has_mkc_account:
            await send_to_verification_log(
                self.client,
                ctx,
                "UID exists and already has MKC linked",
                "No need to verify",
            )
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
                dm_response = ":flag_us:\nWelcome back to 200cc Lounge.\n\n:flag_jp:\n200ccラウンジにおかえり！"
                try:
                    await member.send(dm_response)
                except Exception:
                    pass
            else:
                await ctx.respond(
                    f"``Error 29:`` Could not re-enter the lounge. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
                )
            return
        else:
            pass
        temp = message.split("/")
        mkc_player_id = int(temp[len(temp) - 1].split("=")[1])
        logging.info(f"MKC ID PARSED: {mkc_player_id}")

        # Request registry data
        data = await self.mkc_api_get(mkc_player_id)
        # mkc_player_id = data["id"]
        country_code = data["country_code"]
        is_banned = data["is_banned"]
        discord_id = 166818526768791552
        # if data["discord"] is None:
        #     verify_description = f"# Error1\nCommand issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nThe MKC link that was given by the command issuer has not attached this discord user to their profile"
        #     await ctx.respond(
        #         "This discord account is not linked to the provided MKCentral account"
        #     )
        #     await send_to_verification_log(
        #         self.client, ctx, message, verify_description
        #     )
        #     return
        #
        # discord_id = int(data["discord"]["discord_id"])
        #
        # if discord_id != ctx.author.id:
        #     verify_description = f"# Error2\nCommand issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nMKC Link connected *DISCORD ID* = {discord_id}\nThe user needs to link the correct discord account to their MKC profile."
        #     verify_description = (
        #         f"Wrong discord:mkc mapping\n{ctx.author.id}:{discord_id}"
        #     )
        #     await ctx.respond(
        #         "This discord account is not linked to the provided MKCentral account"
        #     )
        #     await send_to_verification_log(
        #         self.client, ctx, message, verify_description
        #     )
        #     return

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
        x, asdf = await check_if_mkc_user_id_used(mkc_player_id)
        if x:
            await ctx.respond(
                f"``Error 10:`` Oops! Something went wrong. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
            )
            verify_description = f"# Error3\nCommand issuer *DISCORD ID* = {ctx.author.id}\nCommand issuer *USER* = <@{ctx.author.id}>\nCommand issuer *MKC Link* = {message}\nMKC Link connected *DISCORD ID* = {discord_id}\nThe user needs to link the correct discord account to their MKC profile."
            await send_to_verification_log(
                self.client,
                ctx,
                f"Error 10: {message}",
                f"{verify_description} | <@{x}> is already using MKC ID {mkc_player_id}\n{x} is already using MKC ID {mkc_player_id}",  # type: ignore
            )
            return
        else:
            logging.info(f"ALL CLEAR ROLL OUT\n{mkc_player_id}")
            # All clear. Roll out.
            verify_description = vlog_msg.success
            member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
            if uid_exists:
                await send_to_verification_log(
                    self.client, ctx, "UID already exists", "Passed verification"
                )
                lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
                if lounge_ban:
                    await ctx.respond(f"Unbanned after <t:{lounge_ban}:D>")
                    return
                else:
                    pass
                # update the mkc stuff
                mkc_update_response = await self.update_mkc_for_uid(
                    ctx.author.id, mkc_player_id, country_code
                )
                if not mkc_update_response:
                    await ctx.respond(f"{PING_DEVELOPER} help")
                    return
                # set roles
                response = await set_uid_roles(self.client, ctx.author.id)
                if response:
                    member = await get_lounge_guild(self.client).fetch_member(
                        ctx.author.id
                    )
                    msg_response = f":flag_us:\nWelcome back to 200cc Lounge.\nYou have been given the role: <@&{response[0]}>\n\n:flag_jp:\n`200ccラウンジにおかえり！`\n<@&{response[0]}>`が割り当てられています`"
                    await ctx.respond(msg_response)
                    dm_response = ":flag_us:\nWelcome back to 200cc Lounge.\n\n:flag_jp:\n200ccラウンジにおかえり！"
                    try:
                        await member.send(dm_response)
                    except Exception:
                        pass
                else:
                    await ctx.respond(
                        f"``Error 29:`` Could not re-enter the lounge. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
                    )
                return
            else:
                await send_to_verification_log(
                    self.client, ctx, "Creating new player", "Passed verification"
                )
                x = await create_player(
                    self.client, member, mkc_player_id, country_code
                )
            try:
                await ctx.respond(x)
            except Exception:
                await ctx.respond("oops")
            try:
                await member.send(x)
            except Exception:
                pass
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return


def setup(client):
    client.add_cog(VerifyCog(client))
