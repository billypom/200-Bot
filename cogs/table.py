import vlog_msg
import DBA
import discord
import logging
import requests
import shutil
import urllib
import math
import uuid # create unique filename for pics
import html
import subprocess
from discord.ext import commands
from helpers import Confirm
from helpers.senders import send_to_verification_log
from helpers.senders import send_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.getters import get_tier_id_list
from helpers.getters import get_lounge_queue_channel_id_list
from helpers.getters import get_tier_from_room_range
from helpers.checkers import check_if_uid_is_lounge_banned
from helpers.checkers import check_if_banned_characters
from helpers.handlers import handle_score_input
from helpers.handlers import handle_placement_init
from helpers.wrappers import positive_mmr, negative_mmr, peak_mmr, new_rank
from config import REPORTER_ROLE_ID, LOUNGE, SQ_HELPER_CHANNEL_ID, CATEGORIES_MESSAGE_ID, SQUAD_QUEUE_CHANNEL_ID, MOGI_MEDIA_CHANNEL_ID, PING_DEVELOPER



class TableCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(
        name='table',
        description='Submit a table',
        guild_ids=LOUNGE
    )
    @commands.has_role(REPORTER_ROLE_ID)  # Make sure to define REPORTER_ROLE_ID
    async def table(
        self,
        ctx,
        mogi_format: discord.Option(int, '1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6', required=True),
        scores: discord.Option(str, 'player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)', required=True)
        ):
        await ctx.defer()

        # ------- Perform access checks
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unbanned after <t:{lounge_ban}:D>', delete_after=30)
            return
        # Check scores for bad input
        bad = await check_if_banned_characters(scores)
        if bad:
            await send_to_verification_log(self.client, ctx, scores, vlog_msg.error1)
            await ctx.respond('``Error 32:`` Invalid input. There must be 12 players and 12 scores.')
            return
        # Check if table was submitted from a tier channel or sq
        is_lounge_queue = False
        tier_id_list = await get_tier_id_list()
        lounge_queue_channel_id_list = await get_lounge_queue_channel_id_list()
        valid_channel_ids = tier_id_list + lounge_queue_channel_id_list
        if ctx.channel.id in valid_channel_ids:
            nya_tier_id = ctx.channel.id
            if nya_tier_id in lounge_queue_channel_id_list:
                is_lounge_queue = True
        else:
            # Retrieve SQ Tier ID from categories helper
            # A debug message is posted by the bot in #sq-helper
            # The category is validated here to allow submitting tables from all SQ room channels
            sq_helper_channel = self.client.get_channel(SQ_HELPER_CHANNEL_ID)
            sq_helper_message = await sq_helper_channel.fetch_message(CATEGORIES_MESSAGE_ID)
            if str(ctx.channel.category.id) in sq_helper_message.content:
                nya_tier_id = SQUAD_QUEUE_CHANNEL_ID
            else:
                await ctx.respond('``Error 72a: `/table` must be used from a mogi channel``')
                return


        chunked_list = await handle_score_input(self.client, ctx, scores, mogi_format)
        if not chunked_list:
            await ctx.respond('``Error 73:`` Invalid input. There must be 12 players and 12 scores.')
            return

        # Check the mogi_format
        if mogi_format == 1:
            SPECIAL_TEAMS_INTEGER = 63
            OTHER_SPECIAL_INT = 19
            MULTIPLIER_SPECIAL = 2.1
            table_color = ['#76D7C4', '#A3E4D7']
        elif mogi_format == 2:
            SPECIAL_TEAMS_INTEGER = 142
            OTHER_SPECIAL_INT = 39
            MULTIPLIER_SPECIAL = 3.0000001
            table_color = ['#76D7C4', '#A3E4D7']
        elif mogi_format == 3:
            SPECIAL_TEAMS_INTEGER = 288
            OTHER_SPECIAL_INT = 59
            MULTIPLIER_SPECIAL = 3.1
            table_color = ['#85C1E9', '#AED6F1']
        elif mogi_format == 4:
            SPECIAL_TEAMS_INTEGER = 402
            OTHER_SPECIAL_INT = 79
            MULTIPLIER_SPECIAL = 3.35
            table_color = ['#C39BD3', '#D2B4DE']
        elif mogi_format == 6:
            SPECIAL_TEAMS_INTEGER = 525
            OTHER_SPECIAL_INT = 99
            MULTIPLIER_SPECIAL = 3.5
            table_color = ['#F1948A', '#F5B7B1']
        else:
            await ctx.respond(f'``Error 27:`` Invalid format: {mogi_format}. Please use 1, 2, 3, or 4.')
            return


        # Get the highest MMR ever
        #   There was a very high integer in the formula for calculating mmr on the original google sheet (9998)
        #   A comment about how people "never thought anyone could reach 10k mmr" made me think this very high integer was a
        #       replacement for getting the highest existing mmr (or at least my formula could emulate that high integer 
        #       with some variance :shrug: its probably fine... no1 going 2 read this)

        # this was a bad solution. there needs to be a cap or the high ranks will just gain linearly
        # try:
            # with DBA.DBAccess() as db:
                # h = db.query('SELECT max(mmr) from player where player_id > %s;',(0,))
                # highest_mmr = h[0][0]
        # except Exception as e:
            # await ctx.respond(f'``Error 76:`` `/table` error. Make a <#{config.SUPPORT_CHANNEL_ID}> if you need assistance.')

        # 10999 works very well
        highest_mmr = 10999


        # Get MMR data for each team, calculate team score, and determine team placement
        mogi_score = 0
        logging.info(f'/table | length of chunked list: {len(chunked_list)}')
        logging.info(f'/table | chunked list: {chunked_list}')
        # preserve the original score formatting for
        original_scores = {}
        
        for team in chunked_list:
            logging.info(f'/table | calculating team: {team}')
            temp_mmr = 0
            team_score = 0
            count = 0
            for player in team:
                logging.info(f'/table | calculating player: {player}')
                original_scores[player[0]] = player[1]
                try:
                    with DBA.DBAccess() as db:
                        temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player[0],))
                    if temp[0][0] is None:
                        mmr = 0
                        count += 1 # added this line 10/10/22 because placement players ppl are mad grrr i need my mmr
                    else:
                        mmr = temp[0][0]
                        count+=1
                    temp_mmr += mmr
                    try: 
                        # gave me nice integer
                        team_score += int(player[1])
                    except Exception:
                        # Split the string into sub strings with scores and operations
                        # Do calculation + -
                        current_group = ''
                        sign = ''
                        points = 0
                        for idx, char in enumerate(str(player[1])):
                            logging.info(f'/table | parsing char: {char}')
                            if char.isdigit():
                                current_group += char
                                logging.info(f'/table | parsing char: {char} | IS DIGIT, current_group = {current_group}')
                            elif char == '-' or char == '+':
                                logging.info(f'/table | parsing char: {char} | IS - or +, current_group = {current_group}')
                                points += int(f'{sign}{current_group}')
                                sign = char
                                logging.info(f'/table | player: {player} | points: {points}')
                                current_group = ''
                            else:
                                await ctx.respond(f'``Error 26:``There was an error with the following player: <@{player[0]}>')
                                return
                        # Last item in list needs to be added
                        points += int(f'{sign}{current_group}')
                        if sign == '-':
                            mogi_score += int(current_group)
                        player[1] = points
                        team_score = team_score + points
                        logging.info(f'/table | team_score: {team_score}')
                except Exception as e:
                    # check for all 12 players exist
                    await send_to_debug_channel(self.client, ctx, f'/table Error 24:{e}')
                    await ctx.respond(f'``Error 24:`` There was an error with the following player: <@{player[0]}>')
                    return
            # print(team_score)
            if count == 0:
                count = 1
            team_mmr = temp_mmr/count # COUNT AS DIVISOR TO DETERMINE AVG/TEAM MMR
            team.append(team_score)
            team.append(team_mmr)
            mogi_score += team_score
        # Check for 984 score
        if mogi_score == 984:
            pass
        else:
            await ctx.respond(f'``Error 28:`` `Scores = {mogi_score} `Scores must add up to 984.')
            return


        # Sort the teams in order of score
        # [[players players players], team_score, team_mmr]
        sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-2]))
        sorted_list.reverse() 

        # Create hlorenzi string
        if mogi_format == 1:
            lorenzi_query='-\n'
        else:
            lorenzi_query=''


        # Initialize score and placement values
        prev_team_score = 0
        prev_team_placement = 1
        team_placement = 0
        count_teams = 1
        for team in sorted_list:
            # If team score = prev team score, use prev team placement, else increase placement and use placement
            if team[len(team)-2] == prev_team_score:
                team_placement = prev_team_placement
            else:
                team_placement = count_teams
            count_teams += 1
            team.append(team_placement)
            if mogi_format != 1:
                if count_teams % 2 == 0:
                    lorenzi_query += f'{team_placement} {table_color[0]} \n'
                else:
                    lorenzi_query += f'{team_placement} {table_color[1]} \n'
            for idx, player in enumerate(team):
                if idx > (mogi_format-1):
                    continue
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT player_name, country_code FROM player WHERE player_id = %s;', (player[0],))
                    player_name = temp[0][0]
                    country_code = temp[0][1]
                    # score = player[1]
                # lorenzi_query += f'{player_name} [{country_code}] {score}\n'
                lorenzi_query += f'{player_name} [{country_code}] {original_scores[player[0]]}\n'

            # Assign previous values before looping
            prev_team_placement = team_placement
            prev_team_score = team[len(team)-3]




        # Request a lorenzi table
        lorenzi_table_unique_filename = uuid.uuid4().hex
        lorenzi_table_filename = f'./images/tables/{lorenzi_table_unique_filename}.jpg'
        query_string = urllib.parse.quote(lorenzi_query)
        url = f'https://gb.hlorenzi.com/table.png?data={query_string}'
        response = requests.get(url, stream=True)
        with open(lorenzi_table_filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


        # Ask for table confirmation
        table_view = Confirm(ctx.author.id)
        channel = self.client.get_channel(ctx.channel.id)
        await channel.send(file=discord.File(f'./images/tables/{lorenzi_table_unique_filename}.jpg'), delete_after=300)
        await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)
        # delete this wait????
        await table_view.wait()
        if table_view.value is None:
            await ctx.respond('No response from reporter. Timed out')
        elif table_view.value: # yes
            if is_lounge_queue:
                # Set lounge queue channel table submitted for deletion later
                try:
                    with DBA.DBAccess() as db:
                        db.execute('UPDATE lounge_queue_channel SET is_table_submitted = 1 WHERE channel_id = %s;', (ctx.channel.id,))
                except Exception as e:
                    logging.warning(f'table error | could not update lounge_queue_channel.is_table_submitted | {e}')
                    pass
                
                # Get the min & max mmr for this room
                try:
                    with DBA.DBAccess() as db:
                        room_data = db.query('SELECT min_mmr, max_mmr FROM lounge_queue_channel WHERE channel_id = %s;', (ctx.channel.id,))[0]
                        room_min_mmr = room_data[0]
                        room_max_mmr = room_data[1]
                except Exception as e:
                    logging.warning(f'table error | could not retrieve min or max mmr from lounge queue channel | {e}')
                
                
                nya_tier_id, _ = await get_tier_from_room_range(room_min_mmr, room_max_mmr)
                
                
            
            
            db_mogi_id = 0
            # Create mogi
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);', (mogi_format, nya_tier_id))

            # Get the results channel and tier name for later use
            with DBA.DBAccess() as db:
                temp = db.query('SELECT results_id, tier_name FROM tier WHERE tier_id = %s;', (nya_tier_id,))
                db_results_channel = temp[0][0]
                tier_name = temp[0][1]
            results_channel = await self.client.fetch_channel(db_results_channel)






            # Pre MMR table calculate
            value_table = list()
            for idx, team_x in enumerate(sorted_list):
                working_list = list()
                for idy, team_y in enumerate(sorted_list):
                    pre_mmr = 0.0
                    if idx == idy: # skip value vs. self
                        pass
                    else:
                        team_x_mmr = team_x[len(team_x)-2]
                        team_x_placement = team_x[len(team_x)-1]
                        team_y_mmr = team_y[len(team_y)-2]
                        team_y_placement = team_y[len(team_y)-1]
                        if team_x_placement == team_y_placement:
                            pre_mmr = (SPECIAL_TEAMS_INTEGER*((((team_x_mmr - team_y_mmr)/highest_mmr)**2)**(1/3))**2)
                            # print(f'1pre mmr: {pre_mmr}')
                            if team_x_mmr >= team_y_mmr:
                                pass
                            else: #team_x_mmr < team_y_mmr:
                                pre_mmr = pre_mmr * -1
                        else:
                            if team_x_placement > team_y_placement:
                                pre_mmr = (1 + OTHER_SPECIAL_INT*(1 + (team_x_mmr-team_y_mmr)/highest_mmr)**MULTIPLIER_SPECIAL)
                                # print(f'2pre mmr: {pre_mmr} | teamx:{team_x_mmr} | teamy:{team_y_mmr} ')
                            else: #team_x_placement < team_y_placement
                                pre_mmr = -(1 + OTHER_SPECIAL_INT*(1 + (team_y_mmr-team_x_mmr)/highest_mmr)**MULTIPLIER_SPECIAL)
                                # print(f'3pre mmr: {pre_mmr} | teamx:{team_x_mmr} | teamy:{team_y_mmr} ')
                    working_list.append(pre_mmr)
                value_table.append(working_list)
                # print(f'working list {idx}: {working_list}')
            ############await send_raw_to_debug_channel(self.client, 'MMR calculated', 'value table loaded')

            # Actually calculate the MMR
            logging.info('POP_LOG | Calculating MMR')
            for idx, team in enumerate(sorted_list):
                # logging.info(f'POP_LOG | {idx} | {team}')
                temp_value = 0.0
                for pre_mmr_list in value_table:
                    # logging.info(f'POP_LOG | {pre_mmr_list}')
                    # print(f'{idx}pre mmr list')
                    # print(pre_mmr_list)
                    for idx2, value in enumerate(pre_mmr_list):
                        # logging.info(f'POP_LOG | (idx,idx2)')
                        # logging.info(f'POP_LOG | {idx},{idx2}')
                        # logging.info(f'POP_LOG | {temp_value} += {value}')
                        # logging.info(f'POP_LOG | {temp_value.real} += {value.real}')
                        if idx == idx2:
                            temp_value += value
                        else:
                            pass
                # print(f'appending {temp_value}+={value} | {idx} | {idx2}')
                # logging.info(f'POP_LOG | value = {temp_value}, value.real = {temp_value.real}')
                team.append(math.floor(temp_value.real))

            # Create mmr table string
            if mogi_format == 1:
                string_mogi_format = 'FFA'
            else:
                string_mogi_format = f'{str(mogi_format)}v{str(mogi_format)}'

            mmr_table_string = f'<big><big>{ctx.channel.name} {string_mogi_format}</big></big>\n'
            mmr_table_string += 'PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n'

            for team in sorted_list:
                logging.info(f'POP_LOG | team in sorted_list: {team}')
                ###########await send_raw_to_debug_channel(self.client, 'Updating team', team)
                my_player_place = team[len(team)-2]
                string_my_player_place = str(my_player_place)
                for idx, player in enumerate(team):
                    mmr_table_string += '\n'
                    if idx > (mogi_format-1):
                        break
                    with DBA.DBAccess() as db:
                        temp = db.query('SELECT player_name, mmr, peak_mmr, rank_id, mogi_media_message_id FROM player WHERE player_id = %s;', (player[0],))
                        my_player_name = temp[0][0]
                        my_player_mmr = temp[0][1]
                        my_player_peak = temp[0][2]
                        my_player_rank_id = temp[0][3]
                        mogi_media_message_id = temp[0][4]
                        if my_player_peak is None:
                            # print('its none...')
                            my_player_peak = 0
                    my_player_score = int(player[1])
                    my_player_new_rank = ''


                    # Place the placement players
                    if my_player_mmr is None:
                        placement_name, my_player_mmr = await handle_placement_init(self.client, player, my_player_mmr, my_player_score, ctx.channel.name, results_channel)

                    my_player_mmr_change = team[len(team)-1]
                    my_player_new_mmr = (my_player_mmr + my_player_mmr_change)
                    
                    # Dont go below 0 mmr
                    # Keep mogi history clean - chart doesn't go below 0
                    if my_player_new_mmr <= 0:
                        # if someone gets negative mmr, it is always a loss. add L :pensive:
                        my_player_mmr_change = (my_player_mmr)*-1
                        my_player_new_mmr = 1




                    # Start creating string for MMR table
                    mmr_table_string += f'{string_my_player_place.center(6)}|'
                    mmr_table_string += html.escape(f'{my_player_name.center(18)}|')
                    mmr_table_string += f'{str(my_player_mmr).center(7)}|'




                    # Check sign of mmr delta
                    if my_player_mmr_change >= 0:
                        temp_string = f'+{str(my_player_mmr_change)}'
                        string_my_player_mmr_change = f'{temp_string.center(7)}'
                        formatted_my_player_mmr_change = await positive_mmr(string_my_player_mmr_change)
                    else:
                        string_my_player_mmr_change = f'{str(my_player_mmr_change).center(7)}'
                        formatted_my_player_mmr_change = await negative_mmr(string_my_player_mmr_change)
                    mmr_table_string += f'{formatted_my_player_mmr_change}|'





                    # Check for new peak
                    string_my_player_new_mmr = str(my_player_new_mmr).center(9)
                    # print(f'current peak: {my_player_peak} | new mmr value: {my_player_new_mmr}')
                    if my_player_peak < my_player_new_mmr:
                        formatted_my_player_new_mmr = await peak_mmr(string_my_player_new_mmr)
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE player SET peak_mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
                    else:
                        formatted_my_player_new_mmr = string_my_player_new_mmr
                    mmr_table_string += f'{formatted_my_player_new_mmr}|'






                    # Send updates to DB
                    try:
                        with DBA.DBAccess() as db:
                            # Get ID of the last inserted table
                            temp = db.query('SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;', (nya_tier_id,))
                            db_mogi_id = temp[0][0]
                            # Insert reference record
                            db.execute('INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr) VALUES (%s, %s, %s, %s, %s, %s, %s);', (player[0], db_mogi_id, int(my_player_place), int(my_player_score), int(my_player_mmr), int(my_player_mmr_change), int(my_player_new_mmr)))
                            # Update player record
                            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
                    except Exception as e:
                        # print(e)
                        await send_to_debug_channel(self.client, ctx, f'FATAL TABLE ERROR: {e}')
                        pass
                    


                    # Remove mogi media messages
                    if mogi_media_message_id is None:
                        pass
                    else:
                        channel = self.client.get_channel(MOGI_MEDIA_CHANNEL_ID)
                        message = await channel.fetch_message(mogi_media_message_id)
                        await message.delete()

                    with DBA.DBAccess() as db:
                        db.execute('UPDATE player SET mogi_media_message_id = NULL WHERE player_id = %s;', (player[0],))




                    # Check for rank changes
                    with DBA.DBAccess() as db:
                        db_ranks_table = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s;', (1,))
                    for i in range(len(db_ranks_table)):
                        rank_id = db_ranks_table[i][0]
                        min_mmr = db_ranks_table[i][1]
                        max_mmr = db_ranks_table[i][2]
                        # Rank up - assign roles - update DB
                        try:
                            if my_player_mmr < min_mmr and my_player_new_mmr >= min_mmr:
                                guild = get_lounge_guild(self.client)
                                current_role = guild.get_role(my_player_rank_id)
                                new_role = guild.get_role(rank_id)
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)
                                await member.add_roles(new_role)
                                await results_channel.send(f'<@{player[0]}> has been promoted to {new_role}!')
                                with DBA.DBAccess() as db:
                                    db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                                my_player_new_rank += f'+ {new_role}'
                            # Rank down - assign roles - update DB
                            elif my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr:
                                guild = get_lounge_guild(self.client)
                                current_role = guild.get_role(my_player_rank_id)
                                new_role = guild.get_role(rank_id)
                                member = await guild.fetch_member(player[0])
                                await member.remove_roles(current_role)
                                await member.add_roles(new_role)
                                await results_channel.send(f'<@{player[0]}> has been demoted to {new_role}')
                                with DBA.DBAccess() as db:
                                    db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                                my_player_new_rank += f'- {new_role}'
                        except Exception:
                            # print(e)
                            pass
                            # my_player_rank_id = role_id
                            # guild.get_role(role_id)
                            # guild.get_member(discord_id)
                            # member.add_roles(discord.Role)
                            # member.remove_roles(discord.Role)
                    string_my_player_new_rank = f'{str(my_player_new_rank).center(12)}'
                    formatted_my_player_new_rank = await new_rank(string_my_player_new_rank, my_player_new_mmr)
                    mmr_table_string += f'{formatted_my_player_new_rank}'
                    string_my_player_place = ''






            # correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
            # correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
            # '+swap', '-compose', 'Over', '-composite', '-quality', '100',
            # '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',

            ###########await send_raw_to_debug_channel(self.client, 'TEAMS UPDATED', 'Success')
            # Create imagemagick image
            # https://imagemagick.org/script/color.php
            mmr_unique_filename = uuid.uuid4().hex
            mmr_filename = f'./images/tables/{mmr_unique_filename}.jpg'
            pango_string = f'pango:<tt>{mmr_table_string}</tt>'
            mmr_table_succeeded = False
            try:
                subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, './images/mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
                mmr_table_succeeded = True
            except Exception as e:
                logging.warning(f'/table | Could not generate pango MMR table | {e}')
                mmr_table_succeeded = False
                await results_channel.send(f'Table ID {db_mogi_id} MMR Image could not be created. {PING_DEVELOPER}')
                
            f=discord.File(mmr_filename, filename='mmr.jpg')
            sf=discord.File(lorenzi_table_filename, filename='table.jpg')
            
            # Create embed
            embed2 = discord.Embed(title=f'Tier {tier_name.upper()} Results', color = discord.Color.blurple())
            embed2.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
            embed2.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
            embed2.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
            embed2.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
            embed2.set_image(url='attachment://table.jpg')
            table_message = await results_channel.send(content=None, embed=embed2, file=sf)
            # Table URL for website
            try:
                table_url = table_message.embeds[0].image.url
            except Exception:
                table_url = None
            # Upload table URL & message ID for /zrevert
            try:
                with DBA.DBAccess() as db:
                    db.query('UPDATE mogi SET table_url = %s, table_message_id = %s WHERE mogi_id = %s;', (table_url, table_message.id, db_mogi_id))
            except Exception as e:
                await send_to_debug_channel(self.client, ctx, f'/table | Unable to get table url: {e}')
                pass
            
            if mmr_table_succeeded:
                embed = discord.Embed(title=f'Tier {tier_name.upper()} MMR', color = discord.Color.blurple())
                embed.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
                embed.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
                embed.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
                embed.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
                embed.set_image(url='attachment://mmr.jpg')
                embed_message = await results_channel.send(content=None, embed=embed, file=f)
                # Upload message ID for /zrevert
                try:
                    with DBA.DBAccess() as db:
                        db.query('UPDATE mogi SET mmr_message_id = %s WHERE mogi_id = %s;', (embed_message.id, db_mogi_id))
                except Exception as e:
                    await send_to_debug_channel(self.client, ctx, f'/table | Unable to update mmr_message_id: {e}')
                    pass
                #  discord ansi coloring (doesn't work on mobile)
                # https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
                # https://rebane2001.com/discord-colored-text-generator/ 
            await ctx.respond('`Table Accepted.`')
        else:
            await ctx.respond('`Table Denied.`', delete_after=300)

def setup(client):
    client.add_cog(TableCog(client))
