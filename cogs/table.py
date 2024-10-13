import vlog_msg
import traceback
import DBA
from discord import Option, File, Embed, Color
import logging
import requests
import shutil
import urllib
import uuid  # create unique filename for pics
import html
from subprocess import run as subprocessrun
from discord.ext import commands
from helpers import (
    Confirm,
    create_lorenzi_query,
    calculate_pre_mmr,
    calculate_mmr,
    create_mogi,
)
from helpers.senders import (
    send_to_verification_log,
    send_to_debug_channel,
    send_raw_to_debug_channel,
)
from helpers.getters import (
    get_lounge_guild,
    get_tier_from_submission_channel,
    get_mogi_table_color_by_format,
)
from helpers.handlers import (
    handle_team_placements_for_lorenzi_table,
    handle_score_input,
    handle_placement_init,
)
from helpers.checkers import (
    check_if_uid_is_lounge_banned,
    check_for_rank_changes,
    check_if_banned_characters,
    check_if_valid_table_submission_channel,
)
from helpers.wrappers import positive_mmr, negative_mmr, peak_mmr, new_rank
from constants import (
    REPORTER_ROLE_ID,
    LOUNGE,
    PING_DEVELOPER,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class TableCog(commands.Cog):
    """/table - slash command"""

    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="table", description="Submit a table", guild_ids=LOUNGE
    )
    @commands.has_role(REPORTER_ROLE_ID)  # Make sure to define REPORTER_ROLE_ID
    async def table(
        self,
        ctx: "ApplicationContext",
        mogi_format: Option(int, "1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6", required=True),  # type: ignore
        scores: Option(
            str,
            "player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)",
            required=True,
        ),  # type: ignore
    ):
        """
        Command to submit a mogi results table
        - Arranges the list of players, queries lorenzi's table maker
        - Posts the table image, then asks issuer for confirmation
        On confirm,
        - Calculates MMR changes, generates a popuko MMR table
        - Posts both tables in embeds in the appropriate results channel

        Tables can only be created from tier/results channels

        Args:
        - `mogi_format` (int): Format of the mogi 1, 2, 3, 4, 6
        - `scores` (str): Player scores (i.e., popuko 12 JPGiviner 42, Technical 180...)
        """
        await ctx.defer()
        # User access check
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f"Unbanned after <t:{lounge_ban}:D>", delete_after=30)
            return
        # Malicious input check
        bad = await check_if_banned_characters(scores)
        if bad:
            await send_to_verification_log(self.client, ctx, scores, vlog_msg.error1)
            await ctx.respond(
                "``Error 32:`` Invalid input. There must be 12 players and 12 scores."
            )
            return
        # Check for valid submission channel
        valid = await check_if_valid_table_submission_channel(
            ctx.channel.id,  # type: ignore
            ctx.channel.category.id,  # type: ignore
        )
        if not valid:
            await ctx.respond(
                "``Error 72a: `/table` must be used from a mogi channel``"
            )
            return
        # Validate score input formatting
        chunked_list = await handle_score_input(scores, mogi_format)
        if isinstance(chunked_list[0], str):
            channel = self.client.get_channel(ctx.channel.id)  # type: ignore
            await channel.send(chunked_list[0])  # send error info
            await ctx.respond(
                "``Error 73:`` Invalid input. There must be 12 players and 12 scores."
            )
            return
        # Check the mogi_format
        table_color = await get_mogi_table_color_by_format(mogi_format)
        if table_color[0] is None:
            await ctx.respond(f"Invalid format: {mogi_format}. Use 1, 2, 3, or 4.")
            return
        # Handle team score & team mmr
        (
            data_is_valid,
            error_message,
            mogi_score,
            original_scores,
        ) = await handle_team_placements_for_lorenzi_table(chunked_list)
        # Validation 1
        if not data_is_valid:
            await ctx.respond(error_message)
            return
        # Validation 2
        if mogi_score != 984:
            await ctx.respond(
                f"``Error 28:`` `Scores = {mogi_score} `Scores must add up to 984."
            )
            return
        # Sort the teams in order of score
        # [[players players players], team_score, team_mmr]
        sorted_list = sorted(
            chunked_list,  # type: ignore
            key=lambda x: int(x[-2]),  # type: ignore
        )
        sorted_list.reverse()
        # Create hlorenzi string
        lorenzi_query = await create_lorenzi_query(
            sorted_list, original_scores, mogi_format, table_color
        )
        # Request a lorenzi table
        lorenzi_table_unique_filename = uuid.uuid4().hex
        lorenzi_table_filename = f"./images/tables/{lorenzi_table_unique_filename}.jpg"
        query_string = urllib.parse.quote(lorenzi_query)  # ?
        url = f"https://gb.hlorenzi.com/table.png?data={query_string}"
        response = requests.get(url, stream=True)
        with open(lorenzi_table_filename, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        # Ask for table confirmation
        table_view = Confirm(ctx.author.id)
        channel = self.client.get_channel(ctx.channel.id)  # type: ignore
        await channel.send(
            file=File(f"./images/tables/{lorenzi_table_unique_filename}.jpg"),
            delete_after=300,
        )
        await channel.send(
            "Is this table correct? :thinking:", view=table_view, delete_after=300
        )
        await table_view.wait()
        if table_view.value is None:
            await ctx.respond("No response from reporter. Timed out")
            return
        elif table_view.value:  # yes
            db_mogi_id = 0
            tier_id = await get_tier_from_submission_channel(channel.id)
            db_results_channel, tier_name = await create_mogi(mogi_format, tier_id)
            results_channel = await self.client.fetch_channel(db_results_channel)
            # Pre MMR table calculate
            value_table = await calculate_pre_mmr(
                mogi_format,
                sorted_list,
            )
            if value_table[0] is None:
                await ctx.respond(f"Invalid format: {mogi_format}. Use 1, 2, 3, or 4.")
                return
            await calculate_mmr(sorted_list, value_table)
            # Create mmr table string
            if mogi_format == 1:
                string_mogi_format = "FFA"
            else:
                string_mogi_format = f"{str(mogi_format)}v{str(mogi_format)}"

            mmr_table_string = (
                f"<big><big>tier-{tier_name.lower()} {string_mogi_format}</big></big>\n"
            )
            mmr_table_string += (
                "PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n"
            )
            # Update MMR in the database, handle placement players,
            # and build the MMR table string
            # [[player_id, score as str], [player_id, score as str], team_score, avg mmr, place, mmr_gain/loss]
            for team in sorted_list:
                player_place = int(team[-2])
                for idx, player in enumerate(team):
                    mmr_table_string += "\n"
                    if idx > (mogi_format - 1):
                        break
                    with DBA.DBAccess() as db:
                        temp = db.query(
                            "SELECT player_name, mmr, peak_mmr, rank_id FROM player WHERE player_id = %s;",
                            (player[0],),
                        )
                        player_name = str(temp[0][0])  # type: ignore
                        player_mmr = temp[0][1]  # type: ignore - could be NULL
                        player_peak = temp[0][2]  # type: ignore - could be NULL
                        player_rank_id = int(temp[0][3])  # type: ignore
                        if player_peak is None:
                            player_peak = 0
                    player_score = int(original_scores[player[0]])
                    # Place the placement players
                    if player_mmr is None:
                        _, player_mmr = await handle_placement_init(
                            self.client,
                            player[0],
                            player_score,
                            ctx.channel.name,  # type: ignore
                            results_channel,
                        )
                    player_mmr_change = team[len(team) - 1]
                    player_new_mmr = player_mmr + player_mmr_change
                    if player_new_mmr <= 0:
                        # if someone gets negative mmr, it is always a loss
                        player_mmr_change = (player_mmr) * -1  # type: ignore
                        player_new_mmr = 1
                    # errors BEGONE
                    player_mmr = int(player_mmr)  # type: ignore
                    player_new_mmr = int(player_new_mmr)
                    # Start creating string for MMR table
                    player_new_rank = ""
                    mmr_table_string += (
                        f"{'      ' if idx != 0 else str(player_place).center(6)}|"
                    )
                    mmr_table_string += html.escape(f"{player_name.center(18)}|")  # type: ignore
                    mmr_table_string += f"{str(player_mmr).center(7)}|"
                    # Check sign of mmr delta
                    if player_mmr_change >= 0:
                        formatted_player_mmr_change = await positive_mmr(
                            (f"+{str(player_mmr_change)}").center(7)
                        )
                    else:
                        formatted_player_mmr_change = await negative_mmr(
                            (f"{str(player_mmr_change).center(7)}")
                        )
                    mmr_table_string += f"{formatted_player_mmr_change}|"
                    # Check for new peak
                    string_my_player_new_mmr = str(player_new_mmr).center(9)
                    if player_peak < player_new_mmr:  # type: ignore
                        formatted_player_new_mmr = await peak_mmr(
                            string_my_player_new_mmr
                        )
                        with DBA.DBAccess() as db:
                            db.execute(
                                "UPDATE player SET peak_mmr = %s WHERE player_id = %s;",
                                (player_new_mmr, player[0]),
                            )
                    else:
                        formatted_player_new_mmr = string_my_player_new_mmr
                    mmr_table_string += f"{formatted_player_new_mmr}|"
                    # Send updates to DB
                    try:
                        with DBA.DBAccess() as db:
                            # Get ID of the last inserted table
                            # Only 1 match is played in 1 tier at a time, so it is reasonable
                            # to assume we can get the mogi we inserted earlier using this
                            db_mogi_id = db.query(
                                "SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;",
                                (tier_id,),
                            )[0][0]  # type: ignore
                            # Insert player_mogi record
                            db.execute(
                                "INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                (
                                    player[0],
                                    db_mogi_id,
                                    int(player_place),
                                    int(player_score),
                                    player_mmr,  # type: ignore
                                    int(player_mmr_change),
                                    int(player_new_mmr),
                                ),
                            )
                            # Update player mmr
                            db.execute(
                                "UPDATE player SET mmr = %s WHERE player_id = %s;",
                                (player_new_mmr, player[0]),
                            )
                    except Exception as e:
                        await send_raw_to_debug_channel(
                            self.client,
                            f"FATAL TABLE ERROR {str(traceback.format_exc())}",
                            e,
                        )
                        logging.error("FATAL TABLE ERROR")
                        logging.error(traceback.format_exc())
                    # Check for rank changes
                    (
                        rank_changed,
                        rank_went_up,
                        new_rank_id,
                    ) = await check_for_rank_changes(player_mmr, player_new_mmr)
                    # Update discord & database on rank changed
                    if rank_changed:
                        if rank_went_up:
                            guild = get_lounge_guild(self.client)
                            current_role = guild.get_role(player_rank_id)  # type: ignore
                            new_role = guild.get_role(new_rank_id)
                            try:
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)  # type: ignore
                                await member.add_roles(new_role)  # type: ignore
                                await results_channel.send(
                                    f"<@{player[0]}> has been promoted to {new_role}!"
                                )
                            except Exception:
                                pass
                            player_new_rank += f"+ {new_role}"
                        else:
                            guild = get_lounge_guild(self.client)
                            current_role = guild.get_role(player_rank_id)  # type: ignore
                            new_role = guild.get_role(new_rank_id)
                            try:
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)  # type: ignore
                                await member.add_roles(new_role)  # type: ignore
                                await results_channel.send(
                                    f"<@{player[0]}> has been demoted to {new_role}"
                                )
                            except Exception:
                                pass
                            player_new_rank += f"- {new_role}"
                        with DBA.DBAccess() as db:
                            db.execute(
                                "UPDATE player SET rank_id = %s WHERE player_id = %s;",
                                (new_rank_id, player[0]),
                            )
                    formatted_player_new_rank = await new_rank(
                        f"{str(player_new_rank).center(12)}", player_new_mmr
                    )
                    mmr_table_string += formatted_player_new_rank

            # finished creating mmr table string
            # imagemagick time
            mmr_unique_filename = uuid.uuid4().hex
            mmr_filename = f"./images/tables/{mmr_unique_filename}.jpg"
            pango_string = f"pango:<tt>{mmr_table_string}</tt>"
            mmr_table_succeeded = False
            try:
                subprocessrun(
                    [
                        "convert",
                        "-background",
                        "None",
                        "-fill",
                        "white",
                        pango_string,
                        "./images/mkbg.jpg",
                        "-compose",
                        "DstOver",
                        "-layers",
                        "flatten",
                        mmr_filename,
                    ],
                    check=True,
                    text=True,
                )
                mmr_table_succeeded = True
            except Exception as e:
                logging.warning(f"/table | Could not generate pango MMR table | {e}")
                mmr_table_succeeded = False
                await results_channel.send(
                    f"Table ID {db_mogi_id} MMR Image could not be created. {PING_DEVELOPER}"
                )
            # Create embeds
            f = File(mmr_filename, filename="mmr.jpg")
            sf = File(lorenzi_table_filename, filename="table.jpg")
            embed2 = Embed(
                title=f"Tier {tier_name.upper()} Results", color=Color.blurple()
            )
            embed2.add_field(name="Table ID", value=f"{str(db_mogi_id)}", inline=True)
            embed2.add_field(name="Tier", value=f"{tier_name.upper()}", inline=True)
            embed2.add_field(
                name="Submitted by", value=f"<@{ctx.author.id}>", inline=True
            )
            embed2.add_field(
                name="View on website",
                value=f"https://200-lounge.com/mogi/{db_mogi_id}",
                inline=False,
            )
            embed2.set_image(url="attachment://table.jpg")
            table_message = await results_channel.send(
                content=None, embed=embed2, file=sf
            )
            # Table URL for website
            try:
                table_url = table_message.embeds[0].image.url
            except Exception:
                table_url = None
            # Upload table URL & message ID for /zrevert
            try:
                with DBA.DBAccess() as db:
                    db.query(
                        "UPDATE mogi SET table_url = %s, table_message_id = %s WHERE mogi_id = %s;",
                        (table_url, table_message.id, db_mogi_id),
                    )
            except Exception as e:
                await send_to_debug_channel(
                    self.client, ctx, f"/table | Unable to get table url: {e}"
                )
                pass
            if mmr_table_succeeded:
                embed = Embed(
                    title=f"Tier {tier_name.upper()} MMR", color=Color.blurple()
                )
                embed.add_field(
                    name="Table ID", value=f"{str(db_mogi_id)}", inline=True
                )
                embed.add_field(name="Tier", value=f"{tier_name.upper()}", inline=True)
                embed.add_field(
                    name="Submitted by", value=f"<@{ctx.author.id}>", inline=True
                )
                embed.add_field(
                    name="View on website",
                    value=f"https://200-lounge.com/mogi/{db_mogi_id}",
                    inline=False,
                )
                embed.set_image(url="attachment://mmr.jpg")
                embed_message = await results_channel.send(
                    content=None, embed=embed, file=f
                )
                # Upload message ID for /zrevert
                try:
                    with DBA.DBAccess() as db:
                        db.query(
                            "UPDATE mogi SET mmr_message_id = %s WHERE mogi_id = %s;",
                            (embed_message.id, db_mogi_id),
                        )
                except Exception as e:
                    await send_to_debug_channel(
                        self.client,
                        ctx,
                        f"/table | Unable to update mmr_message_id: {e}",
                    )
                    pass
                #  discord ansi coloring (doesn't work on mobile)
                # https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
                # https://rebane2001.com/discord-colored-text-generator/
            await ctx.respond("`Table Accepted.`")
        else:
            await ctx.respond("`Table Denied.`", delete_after=300)


def setup(client):
    client.add_cog(TableCog(client))
