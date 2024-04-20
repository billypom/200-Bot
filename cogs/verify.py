from discord import Color, Option
import re
import time
import datetime
import vlog_msg
from discord.ext import commands
from helpers import set_uid_roles
from helpers import create_player
from helpers.getters import get_lounge_guild
from helpers.senders import send_to_ip_match_log
from helpers.senders import send_to_verification_log
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_uid_exists
from helpers.checkers import check_if_mkc_user_id_used
from helpers.jazzy_mkc import mkc_request_forum_info
from helpers.jazzy_mkc import mkc_request_registry_info
from helpers.jazzy_mkc import mkc_request_mkc_player_id
from config import LOUNGE, SUPPORT_CHANNEL_ID
import logging
import configparser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class VerifyCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        self.seconds_since_last_login_delta_limit = config_file["LOUNGE"].getint(
            "SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT"
        )

    @commands.slash_command(
        name="verify", description="Verify your MKC account", guild_ids=LOUNGE
    )
    async def verify(
        self,
        ctx: "ApplicationContext",
        message: Option(
            str,
            "MKC Link | https://www.mariokartcentral.com/mkc/registry/players/930",
            required=True,
        ),  # type: ignore
    ):
        # mkc_player_id = registry id
        # mkc_user_id = forum id
        await ctx.defer(ephemeral=False)
        x = await check_if_uid_exists(ctx.author.id)
        if x:
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
                logging.info(
                    f"POP_LOG | {member.display_name} | Responded to verification message"
                )
                await member.send(msg_response)
                logging.info(f"POP_LOG | {member.display_name} | Sent verification DM")
            else:
                await ctx.respond(
                    f"``Error 29:`` Could not re-enter the lounge. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
                )
            return
        else:
            pass
        # Regex on https://www.mariokartcentral.com/mkc/registry/players/930
        if "registry" in message:
            regex_pattern = "players/\d*"
            regex_pattern2 = "users/\d*"
            if re.search(regex_pattern, str(message)):
                regex_group = re.search(regex_pattern, message)
                x = regex_group.group()
                reg_array = re.split("/", x)
                mkc_player_id = reg_array[len(reg_array) - 1]
            elif re.search(regex_pattern2, str(message)):
                regex_group = re.search(regex_pattern2, message)
                x = regex_group.group()
                reg_array = re.split("/", x)
                mkc_player_id = reg_array[len(reg_array) - 1]
            else:
                await ctx.respond(
                    "``Error 2:`` Oops! Something went wrong. Check your link or try again later"
                )
                return
        # Regex on https://www.mariokartcentral.com/forums/index.php?members/popuko.154/
        elif "forums" in message:
            regex_pattern = "members/.*\.\d*"
            regex_pattern2 = "members/\d*"
            if re.search(regex_pattern, str(message)):
                regex_group = re.search(regex_pattern, message)
                x = regex_group.group()
                temp = re.split("\.|/", x)
                mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp) - 1])
            elif re.search(regex_pattern2, str(message)):
                regex_group = re.search(regex_pattern2, message)
                x = regex_group.group()
                temp = re.split("\.|/", x)
                mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp) - 1])
            else:
                # player doesnt exist on forums
                await ctx.respond(
                    "``Error 3:`` Oops! Something went wrong. Check your link or try again later"
                )
                return
        else:
            await ctx.respond(
                "``Error 80:`` Oops! Something went wrong. Check your link or try again later"
            )
            return
        # Make sure player_id was received properly
        if mkc_player_id != -1:
            pass
        else:
            await ctx.respond(
                "``Error 4:`` Oops! Something went wrong. ```MKC Player ID not transmitted properly.\nMake sure you are signed up in the MKC Registry or try again later.```"
            )
            return
        # Request registry data
        mkc_registry_data = await mkc_request_registry_info(mkc_player_id)
        mkc_user_id = mkc_registry_data[0]
        country_code = mkc_registry_data[1]
        is_banned = mkc_registry_data[2]

        if is_banned:
            # Is banned
            verify_description = vlog_msg.error3
            await ctx.respond(
                "``Error 7:`` Oops! Something went wrong. Check your link or try again later"
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
        # Check for shared ips
        # Check for last seen date
        # If last seen in the last week? pass else: send message (please log in to your mkc account and retry)
        mkc_forum_data = await mkc_request_forum_info(mkc_user_id)
        last_seen_unix_timestamp = float(mkc_forum_data[0])
        # name.mkc_user_id
        user_matches_list = mkc_forum_data[1]

        # Check if seen in last week
        if mkc_forum_data[0] != -1:
            dtobject_now = datetime.datetime.now()
            unix_now = time.mktime(dtobject_now.timetuple())
            seconds_since_last_login = unix_now - last_seen_unix_timestamp
            if seconds_since_last_login > self.seconds_since_last_login_delta_limit:
                verify_description = vlog_msg.error5
                await ctx.respond(
                    "``Error 5:`` Please log in to your MKC account, then retry. \n\nIf you are still being refused verification, click this link then try again: https://www.mariokartcentral.com/forums/index.php?members/popuko.154/"
                )
                await send_to_verification_log(
                    self.client, ctx, message, verify_description
                )
                return
            else:
                pass
        else:
            verify_description = vlog_msg.error7
            verify_color = Color.red()
            await ctx.respond(
                "``Error 6:`` Oops! Something went wrong. Check your link or try again later"
            )
            await send_to_verification_log(
                self.client, ctx, f"Error 6: {message}", verify_description
            )
            return
        if user_matches_list:
            verify_color = Color.teal()
            await send_to_ip_match_log(
                self.client, ctx, message, verify_color, user_matches_list
            )
        # All clear. Roll out.
        verify_description = vlog_msg.success
        verify_color = Color.green()
        # Check if someone has verified as this user before...
        x = await check_if_mkc_user_id_used(mkc_user_id)
        if x:
            await ctx.respond(
                f"``Error 10:`` Oops! Something went wrong. Try again later or make a <#{SUPPORT_CHANNEL_ID}> ticket for assistance."
            )
            verify_description = vlog_msg.error4
            verify_color = Color.red()
            await send_to_verification_log(
                self.client,
                ctx,
                f"Error 10: {message}",
                f"{verify_description} | <@{x[1]}> already using MKC **FORUM** ID {x[0]}",  # type: ignore
            )
            return
        else:
            member = await get_lounge_guild(self.client).fetch_member(ctx.author.id)
            x = await create_player(self.client, member, mkc_user_id, country_code)
            logging.info(
                f"POP_LOG | Created player: discord.Member: {member} | mkc_user_id: {mkc_user_id} | country: {country_code}"
            )
            try:
                await ctx.respond(x)
                logging.info(
                    f"POP_LOG | {member.display_name} | Responded to verification message"
                )
                await member.send(x)
                logging.info(f"POP_LOG | {member.display_name} | Sent verification DM")
            except Exception:
                await ctx.respond("oops")
            await send_to_verification_log(
                self.client, ctx, message, verify_description
            )
            return


def setup(client):
    client.add_cog(VerifyCog(client))
