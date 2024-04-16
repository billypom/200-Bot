import vlog_msg
import DBA
from discord import Option, File, Embed, Color
import logging
import requests
import shutil
import urllib
import math
import uuid  # create unique filename for pics
import html
from subprocess import run as subprocessrun
from discord.ext import commands
from helpers import Confirm, create_lorenzi_query
from helpers.senders import send_to_verification_log
from helpers.senders import send_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.getters import get_tier_from_room_range
from helpers.getters import get_mogi_calculation_data_by_format
from helpers.handlers import handle_team_placements_for_lorenzi_table
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_banned_characters
from helpers.checkers import check_if_valid_table_submission_channel
from helpers.handlers import handle_score_input
from helpers.handlers import handle_placement_init
from helpers.wrappers import positive_mmr, negative_mmr, peak_mmr, new_rank
from config import (
    REPORTER_ROLE_ID,
    LOUNGE,
    MOGI_MEDIA_CHANNEL_ID,
    PING_DEVELOPER,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import ApplicationContext


class TableCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name="table", description="Submit a table", guild_ids=LOUNGE
    )
    @commands.has_role(REPORTER_ROLE_ID)  # Make sure to define REPORTER_ROLE_ID
    async def table(
        self,
        ctx: ApplicationContext,
        mogi_format: Option(int, "1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6", required=True),  # type: ignore
        scores: Option(
            str,
            "player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)",
            required=True,
        ),  # type: ignore
    ):
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
        (
            valid,
            is_lounge_queue,
            nya_tier_id,
            room_tier_name,
        ) = await check_if_valid_table_submission_channel(
            self.client,
            ctx.channel,  # type: ignore
            ctx.channel.category,  # type: ignore
        )
        if not valid:
            await ctx.respond(
                "``Error 72a: `/table` must be used from a mogi channel``"
            )
            return
        # Validate score input formatting
        chunked_list = await handle_score_input(
            self.client,
            ctx.channel.id,  # type: ignore
            scores,
            mogi_format,
        )
        if not chunked_list:
            await ctx.respond(
                "``Error 73:`` Invalid input. There must be 12 players and 12 scores."
            )
            return
        # Check the mogi_format
        (
            SPECIAL_TEAMS_INTEGER,
            OTHER_SPECIAL_INT,
            MULTIPLIER_SPECIAL,
            table_color,
        ) = await get_mogi_calculation_data_by_format(mogi_format)
        if SPECIAL_TEAMS_INTEGER == 0:
            await ctx.respond(
                f"``Error 27:`` Invalid format: {mogi_format}. Please use 1, 2, 3, or 4."
            )
            return
        # Get the highest MMR ever
        #   There was a very high integer in the formula for calculating mmr on the original google sheet (9998)
        #   A comment about how people "never thought anyone could reach 10k mmr" made me think this very high integer was a
        #       replacement for getting the highest existing mmr (or at least my formula could emulate that high integer
        #       with some variance :shrug: its probably fine... no1 going 2 read this)
        # 10999 works very well
        highest_mmr = 10999

        (
            data_is_valid,
            error_message,
            mogi_score,
            original_scores,
        ) = await handle_team_placements_for_lorenzi_table(self.client, chunked_list)
        if not data_is_valid:
            await ctx.respond(error_message)
            return
        # Check for 984 score
        if mogi_score != 984:
            await ctx.respond(
                f"``Error 28:`` `Scores = {mogi_score} `Scores must add up to 984."
            )
            return

        # Sort the teams in order of score
        # [[players players players], team_score, team_mmr]
        sorted_list = sorted(
            chunked_list,  # type: ignore
            key=lambda x: int(x[len(chunked_list[0]) - 2]),  # type: ignore
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
        channel = self.client.get_channel(ctx.channel.id)
        await channel.send(
            file=File(f"./images/tables/{lorenzi_table_unique_filename}.jpg"),
            delete_after=300,
        )
        await channel.send(
            "Is this table correct? :thinking:", view=table_view, delete_after=300
        )
        # delete this wait????
        await table_view.wait()
        if table_view.value is None:
            await ctx.respond("No response from reporter. Timed out")
        elif table_view.value:  # yes
            if is_lounge_queue:
                # Set lounge queue channel table submitted for deletion later
                try:
                    with DBA.DBAccess() as db:
                        db.execute(
                            "UPDATE lounge_queue_channel SET is_table_submitted = 1 WHERE channel_id = %s;",
                            (ctx.channel.id,),
                        )
                except Exception as e:
                    logging.warning(
                        f"table error | could not update lounge_queue_channel.is_table_submitted | {e}"
                    )
                    return

                # Get the min & max mmr for this room
                try:
                    with DBA.DBAccess() as db:
                        room_data = db.query(
                            "SELECT min_mmr, max_mmr FROM lounge_queue_channel WHERE channel_id = %s;",
                            (ctx.channel.id,),
                        )[0]
                        room_min_mmr = int(room_data[0])  # type: ignore
                        room_max_mmr = int(room_data[1])  # type: ignore
                except Exception as e:
                    logging.warning(
                        f"table error | could not retrieve min or max mmr from lounge queue channel | {e}"
                    )
                    try:
                        with DBA.DBAccess() as db:
                            db.execute(
                                "UPDATE lounge_queue_channel SET is_table_submitted = 0 WHERE channel_id = %s;",
                                (ctx.channel.id,),
                            )
                    except Exception as e:
                        logging.warning(
                            f"table error | could not update lounge_queue_channel.is_table_submitted | {e}"
                        )
                        return
                    return
                nya_tier_id, room_tier_name = await get_tier_from_room_range(
                    room_min_mmr, room_max_mmr
                )
            db_mogi_id = 0
            # Create mogi
            with DBA.DBAccess() as db:
                db.execute(
                    "INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);",
                    (mogi_format, nya_tier_id),
                )

            # Get the results channel and tier name for later use
            with DBA.DBAccess() as db:
                temp = db.query(
                    "SELECT results_id, tier_name FROM tier WHERE tier_id = %s;",
                    (nya_tier_id,),
                )
                db_results_channel = int(temp[0][0])  # type: ignore
                tier_name = str(temp[0][1])  # type: ignore
            results_channel = await self.client.fetch_channel(db_results_channel)

            # Pre MMR table calculate
            value_table = list()
            for idx, team_x in enumerate(sorted_list):
                working_list = list()
                for idy, team_y in enumerate(sorted_list):
                    pre_mmr = 0.0
                    if idx == idy:  # skip value vs. self
                        pass
                    else:
                        team_x_mmr = team_x[len(team_x) - 2]
                        team_x_placement = team_x[len(team_x) - 1]
                        team_y_mmr = team_y[len(team_y) - 2]
                        team_y_placement = team_y[len(team_y) - 1]
                        if team_x_placement == team_y_placement:
                            pre_mmr = (
                                SPECIAL_TEAMS_INTEGER
                                * (
                                    (((team_x_mmr - team_y_mmr) / highest_mmr) ** 2)
                                    ** (1 / 3)
                                )
                                ** 2
                            )
                            # print(f'1pre mmr: {pre_mmr}')
                            if team_x_mmr >= team_y_mmr:
                                pass
                            else:  # team_x_mmr < team_y_mmr:
                                pre_mmr = pre_mmr * -1
                        else:
                            if team_x_placement > team_y_placement:
                                pre_mmr = (
                                    1
                                    + OTHER_SPECIAL_INT
                                    * (1 + (team_x_mmr - team_y_mmr) / highest_mmr)
                                    ** MULTIPLIER_SPECIAL
                                )
                                # print(f'2pre mmr: {pre_mmr} | teamx:{team_x_mmr} | teamy:{team_y_mmr} ')
                            else:  # team_x_placement < team_y_placement
                                pre_mmr = -(
                                    1
                                    + OTHER_SPECIAL_INT
                                    * (1 + (team_y_mmr - team_x_mmr) / highest_mmr)
                                    ** MULTIPLIER_SPECIAL
                                )
                                # print(f'3pre mmr: {pre_mmr} | teamx:{team_x_mmr} | teamy:{team_y_mmr} ')
                    working_list.append(pre_mmr)
                value_table.append(working_list)
                # print(f'working list {idx}: {working_list}')
            ############await send_raw_to_debug_channel(self.client, 'MMR calculated', 'value table loaded')

            # Actually calculate the MMR
            logging.info("POP_LOG | Calculating MMR")
            for idx, team in enumerate(sorted_list):
                temp_value = 0.0
                for pre_mmr_list in value_table:
                    for idx2, value in enumerate(pre_mmr_list):
                        if idx == idx2:
                            temp_value += value
                        else:
                            pass
                team.append(math.floor(temp_value.real))

            # Create mmr table string
            if mogi_format == 1:
                string_mogi_format = "FFA"
            else:
                string_mogi_format = f"{str(mogi_format)}v{str(mogi_format)}"

            mmr_table_string = (
                f"<big><big>tier-{room_tier_name} {string_mogi_format}</big></big>\n"
            )
            mmr_table_string += (
                "PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n"
            )

            for team in sorted_list:
                logging.info(f"POP_LOG | team in sorted_list: {team}")
                my_player_place = team[len(team) - 2]
                string_my_player_place = str(my_player_place)
                for idx, player in enumerate(team):
                    mmr_table_string += "\n"
                    if idx > (mogi_format - 1):
                        break
                    with DBA.DBAccess() as db:
                        temp = db.query(
                            "SELECT player_name, mmr, peak_mmr, rank_id, mogi_media_message_id FROM player WHERE player_id = %s;",
                            (player[0],),
                        )
                        my_player_name = str(temp[0][0])  # type: ignore
                        my_player_mmr = int(temp[0][1])  # type: ignore
                        my_player_peak = int(temp[0][2])  # type: ignore
                        my_player_rank_id = int(temp[0][3])  # type: ignore
                        mogi_media_message_id = int(temp[0][4])  # type: ignore
                        if my_player_peak is None:
                            # print('its none...')
                            my_player_peak = 0
                    my_player_score = int(player[1])
                    my_player_new_rank = ""

                    # Place the placement players
                    if my_player_mmr is None:
                        _, my_player_mmr = await handle_placement_init(
                            self.client,
                            player,
                            ctx.channel.name,  # type: ignore
                            results_channel,
                        )

                    my_player_mmr_change = team[len(team) - 1]
                    my_player_new_mmr = my_player_mmr + my_player_mmr_change

                    # Dont go below 0 mmr
                    # Keep mogi history clean - chart doesn't go below 0
                    if my_player_new_mmr <= 0:
                        # if someone gets negative mmr, it is always a loss. add L :pensive:
                        my_player_mmr_change = (my_player_mmr) * -1
                        my_player_new_mmr = 1

                    # Start creating string for MMR table
                    mmr_table_string += f"{string_my_player_place.center(6)}|"
                    mmr_table_string += html.escape(f"{my_player_name.center(18)}|")
                    mmr_table_string += f"{str(my_player_mmr).center(7)}|"

                    # Check sign of mmr delta
                    if my_player_mmr_change >= 0:
                        temp_string = f"+{str(my_player_mmr_change)}"
                        string_my_player_mmr_change = f"{temp_string.center(7)}"
                        formatted_my_player_mmr_change = await positive_mmr(
                            string_my_player_mmr_change
                        )
                    else:
                        string_my_player_mmr_change = (
                            f"{str(my_player_mmr_change).center(7)}"
                        )
                        formatted_my_player_mmr_change = await negative_mmr(
                            string_my_player_mmr_change
                        )
                    mmr_table_string += f"{formatted_my_player_mmr_change}|"

                    # Check for new peak
                    string_my_player_new_mmr = str(my_player_new_mmr).center(9)
                    # print(f'current peak: {my_player_peak} | new mmr value: {my_player_new_mmr}')
                    if my_player_peak < my_player_new_mmr:
                        formatted_my_player_new_mmr = await peak_mmr(
                            string_my_player_new_mmr
                        )
                        with DBA.DBAccess() as db:
                            db.execute(
                                "UPDATE player SET peak_mmr = %s WHERE player_id = %s;",
                                (my_player_new_mmr, player[0]),
                            )
                    else:
                        formatted_my_player_new_mmr = string_my_player_new_mmr
                    mmr_table_string += f"{formatted_my_player_new_mmr}|"

                    # Send updates to DB
                    try:
                        with DBA.DBAccess() as db:
                            # Get ID of the last inserted table
                            db_mogi_id = db.query(
                                "SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;",
                                (nya_tier_id,),
                            )[0][0]  # type: ignore
                            # Insert reference record
                            db.execute(
                                "INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                (
                                    player[0],
                                    db_mogi_id,
                                    int(my_player_place),
                                    int(my_player_score),
                                    int(my_player_mmr),
                                    int(my_player_mmr_change),
                                    int(my_player_new_mmr),
                                ),
                            )
                            # Update player record
                            db.execute(
                                "UPDATE player SET mmr = %s WHERE player_id = %s;",
                                (my_player_new_mmr, player[0]),
                            )
                    except Exception as e:
                        # print(e)
                        await send_to_debug_channel(
                            self.client, ctx, f"FATAL TABLE ERROR: {e}"
                        )
                        pass

                    # Remove mogi media messages
                    if mogi_media_message_id is None:
                        pass
                    else:
                        channel = self.client.get_channel(MOGI_MEDIA_CHANNEL_ID)
                        message = await channel.fetch_message(mogi_media_message_id)
                        await message.delete()

                    with DBA.DBAccess() as db:
                        db.execute(
                            "UPDATE player SET mogi_media_message_id = NULL WHERE player_id = %s;",
                            (player[0],),
                        )

                    # Check for rank changes
                    with DBA.DBAccess() as db:
                        db_ranks_table = db.query(
                            "SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s;",
                            (1,),
                        )
                    for i in range(len(db_ranks_table)):
                        rank_id = int(db_ranks_table[i][0])  # type: ignore
                        min_mmr = int(db_ranks_table[i][1])  # type: ignore
                        max_mmr = int(db_ranks_table[i][2])  # type: ignore
                        # Rank up - assign roles - update DB
                        try:
                            if my_player_mmr < min_mmr and my_player_new_mmr >= min_mmr:
                                guild = get_lounge_guild(self.client)
                                current_role = guild.get_role(my_player_rank_id)
                                new_role = guild.get_role(rank_id)
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)
                                await member.add_roles(new_role)
                                await results_channel.send(
                                    f"<@{player[0]}> has been promoted to {new_role}!"
                                )
                                with DBA.DBAccess() as db:
                                    db.execute(
                                        "UPDATE player SET rank_id = %s WHERE player_id = %s;",
                                        (rank_id, player[0]),
                                    )
                                my_player_new_rank += f"+ {new_role}"
                            # Rank down - assign roles - update DB
                            elif (
                                my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr
                            ):
                                guild = get_lounge_guild(self.client)
                                current_role = guild.get_role(my_player_rank_id)
                                new_role = guild.get_role(rank_id)
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)
                                await member.add_roles(new_role)
                                await results_channel.send(
                                    f"<@{player[0]}> has been demoted to {new_role}"
                                )
                                with DBA.DBAccess() as db:
                                    db.execute(
                                        "UPDATE player SET rank_id = %s WHERE player_id = %s;",
                                        (rank_id, player[0]),
                                    )
                                my_player_new_rank += f"- {new_role}"
                        except Exception:
                            # no rankup or rankup broken? idc. pass
                            pass
                    string_my_player_new_rank = f"{str(my_player_new_rank).center(12)}"
                    formatted_my_player_new_rank = await new_rank(
                        string_my_player_new_rank, my_player_new_mmr
                    )
                    mmr_table_string += f"{formatted_my_player_new_rank}"
                    string_my_player_place = ""

            # correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
            # correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
            # '+swap', '-compose', 'Over', '-composite', '-quality', '100',
            # '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',

            # Create imagemagick image
            # https://imagemagick.org/script/color.php
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

            f = File(mmr_filename, filename="mmr.jpg")
            sf = File(lorenzi_table_filename, filename="table.jpg")

            # Create embed
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
