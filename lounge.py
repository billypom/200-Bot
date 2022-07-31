import DBA
import secrets
import discord
from discord.ui import Button, View
from discord.ext import commands
import vlog_msg
import math
import threading
import re
import datetime
import time
import json
import requests
import asyncio
import random
import math
import urllib.parse
import shutil
import concurrent.futures
from bs4 import BeautifulSoup as Soup

Lounge = [461383953937596416]
lounge_id = 999835318104625252
ml_channel_message_id = 1000138727621918872
ml_lu_channel_message_id = 1000138727697424415
symbol_up = '▴'
symbol_down = '▾' 
MOGILIST = {}
TIER_ID_LIST = list()
MAX_PLAYERS_IN_MOGI = 12
SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT = 604800
intents = discord.Intents(messages=True, guilds=True, message_content=True, members=True)
client = discord.Bot(intents=intents, activity=discord.Game(str('200cc Lounge')))

with DBA.DBAccess() as db:
    get_tier_list = db.query('SELECT tier_id FROM tier WHERE tier_id > %s;', (0,))
    for i in range(len(get_tier_list)):
        TIER_ID_LIST.append(get_tier_list[i][0])
    # print(TIER_ID_LIST)

class Confirm(View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message("Calculating MMR...", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Deleting...", ephemeral=True)
        self.value = False
        self.stop()














def update_mogilist():
    with DBA.DBAccess() as db:
        temp = db.query('SELECT t.tier_name, p.player_name FROM tier t INNER JOIN lineups l ON t.tier_id = l.tier_id INNER JOIN player p ON l.player_id = p.player_id WHERE p.player_id > %s;', (1,))
    for i in range(len(temp)):
        if temp[i][0] in MOGILIST:
            MOGILIST[temp[i][0]].append(temp[i][1])
        else:
            MOGILIST[temp[i][0]]=[temp[i][1]]

    # TODO: actually get the right data, format it, and put it in the ml and mllu channels. good enough for now tho

    ml = client.get_channel(secrets.mogilist_channel)
    # returns a Future object. need to get the .result() of the Future (which is the Discord.message object)
    ml_message = asyncio.run_coroutine_threadsafe(ml.fetch_message(ml_channel_message_id), client.loop)
    asyncio.run_coroutine_threadsafe(ml_message.result().edit(content=f'new temp: {str(len(temp))}'), client.loop)


    mllu = client.get_channel(secrets.mogilist_lu_channel)
    mllu_message = asyncio.run_coroutine_threadsafe(mllu.fetch_message(ml_lu_channel_message_id), client.loop)
    asyncio.run_coroutine_threadsafe(mllu_message.result().edit(content=f'new temp: {temp}'), client.loop)

    
    # Create a dictionary
    # tier_name : [player_names]


def lounge_threads():
    time.sleep(10)
    while(True):
        update_mogilist()
        time.sleep(15)


poll_thread = threading.Thread(target=lounge_threads)
poll_thread.start()








@client.event
async def on_application_command_error(ctx, error):
    if ctx.guild == None:
        channel = client.get_channel(secrets.debug_channel)
        embed = discord.Embed(title='Error', description='ctx.guild = None. This message was sent in a DM...?', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond('Sorry! My commands do not work in DMs. Please use 200cc Lounge :)')
        raise error
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error, delete_after=10)
        return
    else:
        channel = client.get_channel(secrets.debug_channel)
        embed = discord.Embed(title='Error', description=':eyes:', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond(f'Sorry! An unknown error occurred. Contact {secrets.my_discord} if you think this is a mistake.')
        # print(traceback.format_exc())
        raise error
        return

@client.event
async def on_message(ctx):
    if ctx.author.id == lounge_id:
        return
    if ctx.channel.id in TIER_ID_LIST:
        with DBA.DBAccess() as db:
            get_tier = db.query('SELECT voting, tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
        if get_tier[0][0]:
            if get_tier[0][1] == ctx.channel.id:
                if str(ctx.content) in ['1', '2', '3', '4', '6']:
                    # print('its in there lol')
                    try:
                        with DBA.DBAccess() as db:
                            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s ORDER BY create_date LIMIT %s;', (ctx.author.id, ctx.channel.id, MAX_PLAYERS_IN_MOGI)) # limit prevents 13th person from voting
                    except Exception as e:
                        await send_to_debug_channel(ctx, e)
                        return
                    try:
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE lineups SET vote = %s WHERE player_id = %s;', (int(ctx.content), ctx.author.id))
                    except Exception as e:
                        await send_to_debug_channel(ctx, e)
                        return
    # get discord id and channel id
    # if user and channel id in lineups
    message = ctx.content
    # print(message)






# Can up - keep track of who is in lineup

# /verify <link>
@client.slash_command(
    name='verify',
    description='Verify your MKC account',
    guild_ids=Lounge
)
async def verify(
    ctx, 
    message: discord.Option(str, 'MKC Link', required=True
    )):
    # mkc_player_id = registry id
    # mkc_user_id = forum id
    await ctx.defer(ephemeral=True)
    x = await check_if_player_exists(ctx)
    if x:
        await ctx.respond(f'``Error 1:`` {str(ctx.author.display_name)} is already verified.')
        return
    else:
        pass
    # Regex on https://www.mariokartcentral.com/mkc/registry/players/930
    if 'registry' in message:
        regex_pattern = 'players/\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            reg_array = re.split('/', x)
            mkc_player_id = reg_array[1]
        else:
            await ctx.respond('``Error 2:`` Oops! Something went wrong. Check your link or try again later')
            return
    # Regex on https://www.mariokartcentral.com/forums/index.php?members/popuko.154/
    elif 'forums' in message:
        regex_pattern = 'members/.*\.\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_forum_name = temp[1]
            mkc_player_id = await mkc_request_mkc_player_id(temp[2])
        else:
            # player doesnt exist on forums
            await ctx.respond('``Error 3:`` Oops! Something went wrong. Check your link or try again later')
            return
    else:
        await ctx.respond('``Error 5:`` Oops! Something went wrong. Check your link or try again later')
        return
    # Make sure player_id was received properly
    if mkc_player_id != -1:
        pass
    else:
        await ctx.respond('``Error 4:`` Oops! Something went wrong. Check your link or try again later')
        return
    # Request registry data
    mkc_registry_data = await mkc_request_registry_info(mkc_player_id)
    mkc_user_id = mkc_registry_data[0]
    country_code = mkc_registry_data[1]
    is_banned = mkc_registry_data[2]

    if is_banned:
        # Is banned
        verify_description = vlog_msg.error3
        verify_color = discord.Color.red()
        await ctx.respond('``Error 7:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return
    elif is_banned == -1:
        # Wrong link probably?
        await ctx.respond('``Error 7:`` Oops! Something went wrong. Check your link or try again later')
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
    
    if mkc_forum_data[0] != -1:
        dtobject_now = datetime.datetime.now()
        unix_now = time.mktime(dtobject_now.timetuple())
        seconds_since_last_login = unix_now - last_seen_unix_timestamp
        if seconds_since_last_login > SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT:
            verify_description = vlog_msg.error5
            verify_color = discord.Color.red()
            await ctx.respond('``Error 5:`` Please log in to your MKC account and retry')
            await send_to_verification_log(ctx, message, verify_color, verify_description)
            return
        else:
            pass
    else:
        verify_description = vlog_msg.error6
        verify_color = discord.Color.red()
        await ctx.respond('``Error 6:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return
    if user_matches_list:
        await ctx.respond('``Error 8:`` Oops! Something went wrong. Check your link or try again later')
        verify_color = discord.Color.teal()
        await send_to_ip_match_log(ctx, message, verify_color, user_matches_list)
        return
    else:
        # All clear. Roll out.
        verify_description = vlog_msg.success
        verify_color = discord.Color.green()
        # Check if someone has verified as this user before...
        x = await check_if_mkc_player_id_used(mkc_player_id)
        if x:
            await ctx.respond(f'``Error 10: Duplicate player`` If you think this is a mistake, please contact {secrets.my_discord} immediately. ')
            verify_description = vlog_msg.error4
            verify_color = discord.Color.red()
            await send_to_verification_log(ctx, message, verify_color, verify_description)
            return
        else:
            x = await create_player(ctx, mkc_user_id, country_code)
            await ctx.respond(x)
            await send_to_verification_log(ctx, message, verify_color, verify_description)
            return


@client.slash_command(
    name='c',
    description='🙋 Can up for a mogi',
    guild_ids=Lounge
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def c(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    x = await check_if_uid_in_tier(ctx.author.id)
    if x:
        await ctx.respond('``Error 11:`` You are already in a mogi. Use /d to drop before canning up again.')
        return
    else:
        pass
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
            count = temp[0][0]
    except Exception as e:
        await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secrets.my_discord}. {e}')
        await send_to_debug_channel(ctx, e)
        return
    # ADDITIONAL SUBS SHOULD BE ABLE TO JOIN NEXT MOGI
    # if count == MAX_PLAYERS_IN_MOGI:
    #     await ctx.respond('Mogi is full')
    #     return
    try:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO lineups (player_id, tier_id) values (%s, %s);', (ctx.author.id, ctx.channel.id))
            await ctx.respond('You have joined the mogi! You can /d in `15 seconds`')
            channel = client.get_channel(ctx.channel.id)
            await channel.send(f'<@{ctx.author.id}> has joined the mogi!')
            count+=1
    except Exception as e:
        await ctx.respond(f'``Error 16:`` Something went wrong! Contact {secrets.my_discord}. {e}')
        await send_to_debug_channel(ctx, e)
        return
    if count >= MAX_PLAYERS_IN_MOGI:
        mogi_started_successfully = await start_mogi(ctx)
        if mogi_started_successfully:
            pass
            # Chooses a host. Says the start time
            # await start_mogi(ctx)
        else:
            return
        # start the mogi, vote on format, create teams
    return

@client.slash_command(
    name='d',
    description='Drop from the mogi',
    guild_ids=Lounge
)
async def d(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    x = await check_if_uid_in_tier(ctx.author.id)
    if x:
        # y = await check_if_uid_can_drop(ctx.author.id)
        # if y:
        #     pass
        # else:
        #     await ctx.respond('You cannot drop from an ongoing mogi')
        #     return
        # No try block - check is above...
        with DBA.DBAccess() as db:
            tier_temp = db.query('SELECT t.tier_id, t.tier_name FROM tier as t JOIN lineups as l ON t.tier_id = l.tier_id WHERE player_id = %s;', (ctx.author.id,))
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lineups WHERE player_id = %s;', (ctx.author.id,))
                await ctx.respond(f'You have dropped from tier {tier_temp[0][1]}')
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            await ctx.respond(f'``Error 17:`` Oops! Something went wrong. Contact {secrets.my_discord}')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name FROM player WHERE player_id = %s;', (ctx.author.id,))
                channel = client.get_channel(tier_temp[0][0])
                await channel.send(f'{temp[0][0]} has dropped from the lineup')
        except Exception as e:
            await send_to_debug_channel(ctx, f'WHAT! 1 {e}')
            # i should never ever see this...
        return
    else:
        await ctx.respond('You are not in a mogi')
        return

@client.slash_command(
    name='l',
    description='Show the mogi lineup',
    guild_ids=Lounge
)
# @commands.command(aliases=['list'])
@commands.cooldown(1, 30, commands.BucketType.user)
async def l(
    ctx
    ):
    await ctx.defer()
    try:
        with DBA.DBAccess() as db:
            temp = db.query("SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;", (ctx.channel.id,))
    except Exception as e:
        await ctx.respond(f'``Error 20:`` Oops! Something went wrong. Please contact {secrets.my_discord}')
        return
    response = '`Mogi List`:'
    for i in range(len(temp)):
        response = f'{response}\n`{i+1}.` {temp[i][0]}'
    response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
    await ctx.respond(response, delete_after=30)
    return


@client.slash_command(
    name='sub',
    description='Sub out a player',
    guild_ids=Lounge
)
async def sub(
    ctx,
    leaving_player: discord.Option(discord.Member, 'Leaving player', required=True),
    subbing_player: discord.Option(discord.Member, 'Subbing player', required=True)
    ):
    await ctx.defer()
    x = await check_if_mogi_is_ongoing(ctx)
    if x:
        pass
    else:
        await ctx.respond('Mogi has not started')
        return
    # Only players in the mogi can sub out others
    y = await check_if_uid_in_tier(ctx.author.id)
    if y:
        pass
    else:
        await ctx.respond('You are not in the mogi. You cannot sub out another player')
        return
    z = await check_if_uid_in_tier(leaving_player.id)
    if z:
        pass
    else:
        await ctx.respond(f'<@{leaving_player.id}> is not in this mogi.')
        return
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET player_id = %s WHERE player_id = %s;', (subbing_player.id, leaving_player.id))
    except Exception as e:
        await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {secrets.my_discord}')
        await send_to_debug_channel(ctx, e)
        return
    await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
    await send_to_sub_log(ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
    return



# /setfc
@client.slash_command(
    name='fc',
    description='Display or set your friend code',
    guild_ids=Lounge
)
async def setfc(
    ctx,
    fc: discord.Option(str, 'XXXX-XXXX-XXXX', required=False)):
    if fc == None:
        await ctx.defer(ephemeral=True)
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT fc FROM player WHERE player_id = %s;', (ctx.author.id, ))
                await ctx.respond(temp[0][0])
        except Exception as e:
            await ctx.respond('``Error 12:`` No friend code found. Use ``/fc XXXX-XXXX-XXXX`` to set.')
            await send_to_debug_channel(ctx, e)
    else:
        await ctx.defer(ephemeral=True)
        y = await check_if_banned_characters(fc)
        if y:
            await send_to_verification_log(ctx, fc, discord.Color.blurple(), vlog_msg.error1)
            return '``Error 13:`` Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'
        x = await check_if_player_exists(ctx)
        if x:
            pass
        else:
            return '``Error 25:`` Player does not exist. Use `/verify <mkc link>` to register with the Lounge.'
        confirmation_msg = await update_friend_code(ctx, fc)
        await ctx.respond(confirmation_msg)


@client.slash_command(
    name='partner_average',
    description='Get the average score of your partners',
    guild_ids=Lounge
)
async def partner_average(
    ctx,
    mogi_format: discord.Option(int, '1, 2, 3, 4, 6', required=False)
    ):
    await ctx.defer()
    return


@client.slash_command(
    name='table',
    description='Submit a table',
    guilds_ids=Lounge
)
async def table(
    ctx,
    mogi_format: discord.Option(int, '1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6', required=True),
    scores: discord.Option(str, '@player scores (i.e. @popuko 12 @Brandon 100 @Maxarx 180...)', required=True)
    ):
    await ctx.defer()
    remove_chars = {
        60:None, #<
        62:None, #>
        33:None, #!
        64:None, #@
    }
    # Check for verified user
    # Check for role? (reporter? or how do i do that...)
    # Check the mogi_format
    if mogi_format == 1:
        SPECIAL_TEAMS_INTEGER = 63
    elif mogi_format == 2:
        SPECIAL_TEAMS_INTEGER = 142
    elif mogi_format == 3:
        SPECIAL_TEAMS_INTEGER = 288
    elif mogi_format == 4:
        SPECIAL_TEAMS_INTEGER = 402
    elif mogi_format == 6:
        SPECIAL_TEAMS_INTEGER = 525
    else:
        await ctx.respond(f'``Error 27:`` Invalid format: {mogi_format}. Please use 1, 2, 3, 4, or 6.')
        return
    # check for score = 984
    score_string = str(scores).translate(remove_chars)
    score_list = score_string.split()
    # check for 12 players
    if len(score_list) == 24:
        pass
    else:
        await ctx.respond(f'``Error 26:`` Invalid input. There must be 12 players and 12 scores.')
        return
    # Initialize a list so we can group players and scores together
    player_score_chunked_list = list()
    for i in range(0, len(score_list), 2):
        player_score_chunked_list.append(score_list[i:i+2])
    # print(f'player score chunked list: {player_score_chunked_list}')

    # Chunk the list into groups of teams, based on mogi_format and order of scores entry
    chunked_list = list()
    for i in range(0, len(player_score_chunked_list), mogi_format):
        chunked_list.append(player_score_chunked_list[i:i+mogi_format])
    

    # Get MMR data for each team, calculate team score, and determine team placement
    count = 0
    mogi_score = 0
    # print(f'length of chunked list: {len(chunked_list)}')
    for team in chunked_list:
        temp_mmr = 0
        team_score = 0
        for player in team:
            try:
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player[0],))
                    mmr = temp[0][0]
                    temp_mmr += mmr
                    try:
                        team_score += int(player[1])
                    except Exception:
                        score_and_pen = str(player[1]).split('-')
                        team_score = team_score + int(score_and_pen[0]) - int(score_and_pen[1])
            except Exception as e:
                # check for all 12 players exist
                await send_to_debug_channel(ctx, e)
                await ctx.respond(f'``Error 24:`` There was an error with the following player: <@{player[0]}>')
                return
        # print(team_score)
        team_mmr = temp_mmr/len(team)
        team.append(team_score)
        team.append(team_mmr)
        mogi_score += team_score
    if mogi_score == 984:
        pass
    else:
        await ctx.respond(f'``Error 28:`` `Scores = {mogi_score} `Scores must add up to 984.')
        return
    # Sort the teams in order of score
    # [[players players players], team_score, team_mmr]
    sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-2]))
    sorted_list.reverse() 
    print(f'sorted list: {sorted_list}')
    # Create hlorenzi string
    lorenzi_query=''
    # Initialize score and placement values
    prev_team_score = 0
    prev_team_placement = 1
    team_placement = 0
    for team in sorted_list:
        # If team score = prev team score, use prev team placement, else increase placement and use placement
        # print('if team score == prev team score')
        # print(f'if {team[len(team)-2]} == {prev_team_score}')
        if team[len(team)-2] == prev_team_score:
            team_placement = prev_team_placement
        else:
            team_placement+=1
        team.append(team_placement)
        if mogi_format != 1:
            lorenzi_query += f'{team_placement} #AAC8F4 \n'
        for idx, player in enumerate(team):
            if idx > (mogi_format-1):
                continue
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name, country_code FROM player WHERE player_id = %s;', (player[0],))
                player_name = temp[0][0]
                country_code = temp[0][1]
                score = player[1]
            lorenzi_query += f'{player_name} [{country_code}] {score}\n'
        # Assign previous values before leaving
        prev_team_placement = team_placement
        prev_team_score = team[len(team)-3]
    # Request a lorenzi table
    query_string = urllib.parse.quote(lorenzi_query)
    url = f'https://gb.hlorenzi.com/table.png?data={query_string}'
    response = requests.get(url, stream=True)
    with open(f'{hex(ctx.author.id)}table.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    # Ask for table confirmation
    table_view = Confirm()
    channel = client.get_channel(ctx.channel.id)
    table_message = await channel.send(file=discord.File(f'{hex(ctx.author.id)}table.png'), delete_after=300)
    await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)
    await table_view.wait()
    if table_view.value is None:
        await ctx.respond('No response from reporter. Timed out')
    elif table_view.value: # yes

        # Create mogi
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);', (mogi_format, ctx.channel.id))

        # Get the results channel and tier name for later use
        with DBA.DBAccess() as db:
            temp = db.query('SELECT results_id, tier_name FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
            db_results_channel = temp[0][0]
            tier_name = temp[0][1]

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
                        pre_mmr = (SPECIAL_TEAMS_INTEGER*((((team_x_mmr - team_y_mmr)/9998)**2)**0.333)**2)
                        if team_x_mmr >= team_y_mmr:
                            pre_mmr = pre_mmr * -1
                        else: #team_x_mmr < team_y_mmr:
                            pass
                    else:
                        pre_mmr = (1 + 19*(1 + (team_y_mmr-team_x_mmr)/9998)**2.1)
                        if team_x_placement > team_y_placement:
                            pass
                        else: #team_x_placement < team_y_placement
                            pre_mmr = pre_mmr * -1
                working_list.append(pre_mmr)
            value_table.append(working_list)

        # Actually calculate the MMR
        for idx, team in enumerate(sorted_list):
            temp_value = 0.0
            for pre_mmr_list in value_table:
                for idx2, value in enumerate(pre_mmr_list):
                    if idx == idx2:
                        temp_value += value
                    else:
                        pass
            team.append(math.ceil(temp_value))

        # Create mmr table string
        mmr_table_string = ''
        for team in sorted_list:
            # print(team)
            for idx, player in enumerate(team):
                if idx > (mogi_format-1):
                    break
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT p.player_name, p.mmr, p.peak_mmr, p.rank_id, l.is_sub FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE p.player_id = %s;', (player[0],))
                    my_player_name = temp[0][0]
                    my_player_mmr = temp[0][1]
                    my_player_peak = temp[0][2]
                    my_player_rank_id = temp[0][3]
                    is_sub = temp[0][4]
                    if my_player_peak is None:
                        # print('its none...')
                        my_player_peak = 0

                my_player_score = player[1]
                my_player_place = team[len(team)-2]
                if is_sub: # Subs only gain on winning team
                    if team[len(team)-1] < 0:
                        my_player_mmr_change = 0
                    else:
                        my_player_mmr_change = team[len(team)-1]
                else:
                    my_player_mmr_change = team[len(team)-1]
                my_player_new_mmr = (my_player_mmr + my_player_mmr_change)

                # Start creating string for MMR table
                mmr_table_string += f'{str(my_player_place).center(3)}|'
                mmr_table_string +=f'{my_player_name.center(18)}|'
                mmr_table_string += f'{str(my_player_mmr).center(7)}|'

                # Check sign of mmr delta
                if my_player_mmr_change >= 0:
                    temp_string = f'+{str(my_player_mmr_change)}'
                    string_my_player_mmr_change = f'{temp_string.center(6)}'
                    formatted_my_player_mmr_change = await pos_mmr_wrapper(string_my_player_mmr_change)
                else:
                    string_my_player_mmr_change = f'{str(my_player_mmr_change).center(6)}'
                    formatted_my_player_mmr_change = await neg_mmr_wrapper(string_my_player_mmr_change)
                mmr_table_string += f'{formatted_my_player_mmr_change}|'

                # Check for new peak
                string_my_player_new_mmr = str(my_player_new_mmr).center(7)
                if my_player_peak < (my_player_new_mmr):
                    # print('its less than')
                    formatted_my_player_new_mmr = await peak_mmr_wrapper(string_my_player_new_mmr)
                    with DBA.DBAccess() as db:
                        db.execute('UPDATE player SET peak_mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
                else:
                    formatted_my_player_new_mmr = string_my_player_new_mmr
                mmr_table_string += f'{formatted_my_player_new_mmr}|'

                # Send updates to DB
                try:
                    with DBA.DBAccess() as db:
                        # Get ID of the last inserted table
                        temp = db.query('SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;', (ctx.channel.id,))
                        db_mogi_id = temp[0][0]
                        # Insert reference record
                        db.execute('INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr, is_sub) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (player[0], db_mogi_id, int(my_player_place), int(my_player_score), int(my_player_mmr), int(my_player_mmr_change), int(my_player_new_mmr), is_sub))
                        # Update player record
                        db.execute('UPDATE player SET mmr = %s, peak_mmr = %s WHERE player_id = %s;', (int(my_player_new_mmr), int(string_my_player_new_mmr), player[0]))
                except Exception as e:
                    print('duplicate player...skipping')
                    pass

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
                            guild = client.get_guild(Lounge[0])
                            print(f'guild: {guild}')
                            current_role = guild.get_role(my_player_rank_id)
                            print(f'current role: {current_role}')
                            new_role = guild.get_role(rank_id)
                            print(f'new role: {new_role}')
                            member = await guild.fetch_member(player[0])
                            print(f'member: {member}')
                            await member.remove_roles(current_role)
                            print('removed role. adding new role')
                            await member.add_roles(new_role)
                            print('added new role')
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                        # Rank down - assign roles - update DB
                        if my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr:
                            guild = client.get_guild(Lounge[0])
                            print(f'guild: {guild}')
                            current_role = guild.get_role(my_player_rank_id)
                            print(f'current role: {current_role}')
                            new_role = guild.get_role(rank_id)
                            print(f'new role: {new_role}')
                            member = await guild.fetch_member(player[0])
                            print(f'member: {member}')
                            await member.remove_roles(current_role)
                            print('removed role. adding new role')
                            await member.add_roles(new_role)
                            print('added new role')
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                    except Exception as e:
                        print(e)
                        print(f'player <@{player[0]}>not found. no rank update')
                        pass
                        # my_player_rank_id = role_id
                        # guild.get_role(role_id)
                        # guild.get_member(discord_id)
                        # member.add_roles(discord.Role)
                        # member.remove_roles(discord.Role)
                mmr_table_string += '\n'

        # Create imagemagick image



        # Create embed
        results_channel = client.get_channel(db_results_channel)
        embed = discord.Embed(title=f'Tier {tier_name.upper()} Results', description=f'```ansi\n{mmr_table_string}```', color = discord.Color.blurple())
        await results_channel.send(content=None, embed=embed)

        # Create MMR Table
        #```ansi



        # 
        # https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
        # https://rebane2001.com/discord-colored-text-generator/ 


        # Send MMR to results channel
        # tier | results
        # placement, player_name, current MMR, mmr_change, new mmr, new rank(if in range)
        # races = 12
        await ctx.respond('`Table Accepted.`', delete_after=300)
    else:
        await ctx.respond('`Table Denied.`', delete_after=300)



















# Takes a ctx, returns a response
async def create_player(ctx, mkc_user_id, country_code):
    x = await check_if_player_exists(ctx)
    if x:
        return 'Player already registered'
    else:
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT placement_mmr FROM ranks WHERE rank_name = %s;', ('Placement',))
                placement_mmr = temp[0][0]
                db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code, mmr) VALUES (%s, %s, %s, %s, %s);', (ctx.author.id, ctx.author.display_name, mkc_user_id, country_code, placement_mmr))
                return 'Verified & registered successfully'
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            return f'``Error 14:`` Oops! An unlikely error occured. Contact {secrets.my_discord} if you think this is a mistake.'
            # 1. a player trying to use someone elses link (could be banned player)
            # 2. a genuine player locked from usage by another player (banned player might have locked them out)
            # 3. someone is verifying multiple times

# Takes a ctx & a string, returns a response
async def update_friend_code(ctx, message):
    fc_pattern = '\d\d\d\d-?\d\d\d\d-?\d\d\d\d'
    if re.search(fc_pattern, message):
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET friend_code = %s WHERE player_id = %s;', (message, ctx.author.id))
                return 'Friend Code updated'
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            return '``Error 15:`` Player not found'
    else:
        return 'Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'

# Takes a ctx, returns 
async def start_mogi(ctx):
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET voting = 1 WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        await channel.send(f'`Error 23:` Could not start the format vote. Contact the admins or {secrets.my_discord} immediately')
        return 0
    channel = client.get_channel(ctx.channel.id)
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
            db.execute('UPDATE lineups SET can_drop = 0 WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        await channel.send(f'`Error 22:` Could not start the format vote. Contact the admins or {secrets.my_discord} immediately')
        return 0
    response = ''
    for i in range(len(temp)):
        response = f'{response} <@{temp[i][0]}>'
    response = f'''{response} mogi has 12 players\n`Poll Started!`

    `1.` FFA
    `2.` 2v2
    `3.` 3v3
    `4.` 4v4
    `6.` 6v6

    Type a number to vote!
    Poll ends in 2 minutes or when a format reaches 6 votes.'''
    await channel.send(response)
    with DBA.DBAccess() as db:
        unix_temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    # returns the index of the voted on format, and a dictionary of format:voters
    poll_results = await check_for_poll_results(ctx, unix_temp[MAX_PLAYERS_IN_MOGI-1][0])
    if poll_results[0] == -1:
        # Cancel Mogi
        await channel.send('No votes. Mogi will be cancelled.')
        await cancel_mogi(ctx)
        return
        
    teams_results = await create_teams(ctx, poll_results)

    ffa_voters = list()
    v2_voters = list()
    v3_voters = list()
    v4_voters = list()
    v6_voters = list()
    # create formatted message
    for player in poll_results[1]['FFA']:
        ffa_voters.append(player)
    for player in poll_results[1]['2v2']:
        v2_voters.append(player)
    for player in poll_results[1]['3v3']:
        v3_voters.append(player)
    for player in poll_results[1]['4v4']:
        v4_voters.append(player)
    for player in poll_results[1]['6v6']:
        v6_voters.append(player)
    remove_chars = {
        39:None,
        91:None,
        93:None,
    }
    poll_results_response = f'''`Poll Ended!`

    `1.` FFA - {len(ffa_voters)} ({str(ffa_voters).translate(remove_chars)})
    `2.` 2v2 - {len(v2_voters)} ({str(v2_voters).translate(remove_chars)})
    `3.` 3v3 - {len(v3_voters)} ({str(v3_voters).translate(remove_chars)})
    `4.` 4v4 - {len(v4_voters)} ({str(v4_voters).translate(remove_chars)})
    `6.` 6v6 - {len(v6_voters)} ({str(v6_voters).translate(remove_chars)})
    {teams_results}
    '''
    await channel.send(poll_results_response)
    return True


async def check_for_poll_results(ctx, last_joiner_unix_timestamp):
    # print('checking for poll results')
    dtobject_now = datetime.datetime.now()
    unix_now = time.mktime(dtobject_now.timetuple())
    format_list = [0,0,0,0,0]
    while (unix_now - last_joiner_unix_timestamp) < 20:
        # Votes are updated in the on_message event, if mogi is running and player is in tier
        await asyncio.sleep(1)
        with DBA.DBAccess() as db:
            ffa_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,1))
            format_list[0] = ffa_temp[0][0]
        with DBA.DBAccess() as db:
            v2_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,2))
            format_list[1] = v2_temp[0][0]
        with DBA.DBAccess() as db:
            v3_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,3))
            format_list[2] = v3_temp[0][0]
        with DBA.DBAccess() as db:
            v4_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,4))
            format_list[3] = v4_temp[0][0]
        with DBA.DBAccess() as db:
            v6_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,6))
            format_list[4] = v6_temp[0][0]
        if 6 in format_list:
            break
        print(f'{unix_now} - {last_joiner_unix_timestamp}')
        dtobject_now = datetime.datetime.now()
        unix_now = time.mktime(dtobject_now.timetuple())
    # print('checking for all zero votes')
    # print(f'format list: {format_list}')
    if all([v == 0 for v in format_list]):
        return [0, { '0': 0 }] # If all zeros, return 0. cancel mogi
    # Close the voting
    # print('closing the voting')
    with DBA.DBAccess() as db:
        db.execute('UPDATE tier SET voting = %s WHERE tier_id = %s;', (0, ctx.channel.id))
    if format_list[0] == 6:
        ind = 0
    elif format_list[1] == 6:
        ind = 1
    elif format_list[2] == 6:
        ind = 2
    elif format_list[3] == 6:
        ind = 3
    elif format_list[4] == 6:
        ind = 4
    else:
        # Get the index of the voted on format
        max_val = max(format_list)
        ind = [i for i, v in enumerate(format_list) if v == max_val]
        # print('got index of last entered')

    # Create a dictionary where key=format, value=list of players who voted
    poll_dictionary = {
        "FFA":[],
        "2v2":[],
        "3v3":[],
        "4v4":[],
        "6v6":[],
    }
    with DBA.DBAccess() as db:
        votes_temp = db.query('SELECT l.vote, p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    for i in range(len(votes_temp)):
        print(f'votes temp: {votes_temp}')
        if votes_temp[i][0] == 1:
            player_format_choice = 'FFA'
        elif votes_temp[i][0] == 2:
            player_format_choice = '2v2'
        elif votes_temp[i][0] == 3:
            player_format_choice = '3v3'
        elif votes_temp[i][0] == 4:
            player_format_choice = '4v4'
        elif votes_temp[i][0] == 6:
            player_format_choice = '6v6'
        else:
            continue
        poll_dictionary[player_format_choice].append(votes_temp[i][1])
    # print('created poll dictionary')
    # print(f'{poll_dictionary}')
    # Clear votes after we dont need them anymore...
    # print('clearing votes...')
    with DBA.DBAccess() as db:
        db.execute('UPDATE lineups SET vote = NULL WHERE tier_id = %s;', (ctx.channel.id,))
    # I use random.choice to account for ties
    try:
        return [random.choice(ind), poll_dictionary]
    except TypeError:
        return [ind, poll_dictionary]

# poll_results is [index of the voted on format, a dictionary of format:voters]
async def create_teams(ctx, poll_results):
    # print('creating teams')
    keys_list = list(poll_results[1])
    winning_format = keys_list[poll_results[0]]
    # print(f'winning format: {winning_format}')
    players_per_team = 0
    if winning_format == 'FFA':
        players_per_team = 1
    elif winning_format == '2v2':
        players_per_team = 2
    elif winning_format == '3v3':
        players_per_team = 3
    elif winning_format == '4v4':
        players_per_team = 4
    elif winning_format == '6v6':
        players_per_team = 6
    else:
        return 0
    response_string=f'`Winner:` {winning_format}\n\n'
    with DBA.DBAccess() as db:
        player_db = db.query('SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    players_list = list()
    room_mmr = 0
    for i in range(len(player_db)):
        players_list.append([player_db[i][0], player_db[i][1], player_db[i][2]])
        room_mmr = room_mmr + player_db[i][2]
    random.shuffle(players_list) # [[popuko, 7238917831, 4000],[2p, 7u3891273812, 4500]]
    room_mmr = room_mmr/MAX_PLAYERS_IN_MOGI
    response_string += f'   `Room MMR:` {math.ceil(room_mmr)}\n'
    # divide the list based on players_per_team
    chunked_list = list()
    for i in range(0, len(players_list), players_per_team):
        chunked_list.append(players_list[i:i+players_per_team])
    # for each divided team, get mmr for all players, average them, append to team
    for team in chunked_list:
        temp_mmr = 0
        for player in team:
            temp_mmr = temp_mmr + player[2]
        team_mmr = temp_mmr/len(team)
        team.append(team_mmr)

    sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-1]))
    sorted_list.reverse()
    # print(sorted_list)
    player_score_string = f'    `Table:` /table {players_per_team} '
    team_count = 0
    for team in sorted_list:
        team_count+=1
        response_string += f'   `Team {team_count}:` '
        for player in team:
            try:
                player_score_string += f'<@{player[1]}> 0 '
                response_string += f'{player[0]} '
            except TypeError:
                response_string += f'(MMR: {math.ceil(player)})\n'

    response_string+=f'\n{player_score_string}'
    # choose a host
    host_string = '    '
    try:
        with DBA.DBAccess() as db:
            host_temp = db.query('SELECT fc, player_id FROM (SELECT p.fc, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s AND p.fc IS NOT NULL AND p.is_host_banned = %s ORDER BY l.create_date LIMIT %s) as fcs_in_mogi ORDER BY RAND() LIMIT 1;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
            host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
    except Exception as e:
        await send_to_debug_channel(ctx, e)
    # create a return string
    response_string+=f'\n\n{host_string}'
    return response_string


async def check_if_mogi_is_ongoing(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception:
        return False
    if temp[0][0] == MAX_PLAYERS_IN_MOGI:
        return True
    else:
        return False

async def check_if_uid_can_drop(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT can_drop FROM lineups WHERE player_id = %s;', (uid,))
            if temp[0][0] == True:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_uid_in_tier(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s;', (uid,))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_mkc_player_id_used(mkc_player_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mkc_id from player WHERE mkc_id = %s;', (mkc_player_id,))
            if int(temp[0][0]) == int(mkc_player_id):
                return True
            else:
                return False
    except Exception as e:
        await send_raw_to_debug_channel(mkc_player_id, e)
        return False

async def check_if_player_exists(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_id = %s;', (ctx.author.id, ))
            if temp[0][0] == ctx.author.id:
                return True
            else:
                return False
    except Exception as e:
        return False

async def check_if_banned_characters(message):
    for value in secrets.BANNED_CHARACTERS:
        if value in message:
            return True
    return False



# Takes in ctx, returns avg partner score
async def get_partner_avg(ctx, mogi_format):
    try:
        with DBA.DBAccess() as db:
            mogis = db.query("SELECT mogi_id, place FROM player_mogi WHERE player_id = %s;", (uid,))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        return -1

    list_of_mogis = list()
    for mogi in mogis:
        list_of_mogi_ids.append([mogi[0], mogi[1]])

    if mogi_format is None: # get all partner avg from specific format
        try:
            with DBA.DBAccess() as db:
                pass
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            return -1
    else: # get all partner avg
        try:
            with DBA.DBAccess() as db:
                pass
        except Exception as e:
            await send_to_debug_channel(ctx, e)
            return -1
    return temp[0][0]

# Takes in ctx, returns mmr
async def get_player_mmr(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (uid,))
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        return -1
    return temp[0][0]

async def cancel_mogi(ctx):
    # Delete player records for first 12 in lineups table
    with DBA.DBAccess() as db:
        db.execute('DELETE FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    return


# Somebody did a bad
# ctx | message | discord.Color.red() | my custom message
async def send_to_verification_log(ctx, message, verify_color, verify_description):
    channel = client.get_channel(secrets.verification_channel)
    embed = discord.Embed(title='Verification', description=verify_description, color = verify_color)
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Message: ', value=message, inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_debug_channel(ctx, error):
    channel = client.get_channel(secrets.debug_channel)
    embed = discord.Embed(title='Error', description='>.<', color = discord.Color.blurple())
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_raw_to_debug_channel(anything, error):
    channel = client.get_channel(secrets.debug_channel)
    embed = discord.Embed(title='Error', description='>.<', color = discord.Color.yellow())
    embed.add_field(name='anything: ', value=anything, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_sub_log(ctx, message):
    channel = client.get_channel(secrets.sub_channel)
    embed = discord.Embed(title='Sub', description=':3', color = discord.Color.blurple())
    embed.add_field(name='Name: ', value=ctx.author, inline=False)
    embed.add_field(name='Message: ', value=str(message), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_ip_match_log(ctx, message, verify_color, user_matches_list):
    channel = client.get_channel(secrets.ip_match_channel)
    embed = discord.Embed(title="Verification", description=f'IP Matches for <@{ctx.author.id}>', color=verify_color)
    try:
        embed.add_field(name="Name: ", value=ctx.author, inline=False)
        embed.add_field(name='Message: ', value=message, inline=False)
        for user in user_matches_list:
            ip_match_forum_link = f'https://www.mariokartcentral.com/forums/index.php?members/{user}'
            embed.add_field(name=f'{user}', value=ip_match_forum_link, inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
    except Exception as e:
        await channel.send(f'TOO MANY MATCHES: {e} {user_matches_list}')














async def mkc_request_forum_info(mkc_user_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_forum_info, mkc_user_id)
        return_value = future.result()
    return return_value

def mt_mkc_request_forum_info(mkc_user_id):
    try:
        # Get shared ips
        login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
        data_url = (f'https://www.mariokartcentral.com/forums/index.php?members/{mkc_user_id}/shared-ips')
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(secrets.mkc_name),
            'password': str(secrets.mkc_password),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
            response_string = str(response.content)
            response_lines = response_string.split('\\n')
            list_of_user_matches = []
            for line in response_lines:
                # this h3 div is only used to show shared ips. so it works as a unique identifier
                if '<h3 class="contentRow-header"><a href="/forums/index.php?members/' in line:
                    regex_pattern = 'members/.*\.\d*'
                    if re.search(regex_pattern, line):
                        regex_group = re.search(regex_pattern, line)
                        x = regex_group.group()
                        reg_array = re.split('/', x)
                        list_of_user_matches.append(reg_array[1])

        data_url = (f'https://www.mariokartcentral.com/forums/index.php?members/{mkc_user_id}')
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(secrets.mkc_name),
            'password': str(secrets.mkc_password),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
            response_string = str(response.content)
            response_lines = response_string.split('\\n')
            # \t\t\t\t\t\t\t\t\t\t\t<time  class="u-dt" dir="auto" datetime="2022-07-30T11:07:30-0400" data-time="1659193650" data-date-string="Jul 30, 2022" data-time-string="11:07 AM" title="Jul 30, 2022 at 11:07 AM">A moment ago</time> <span role="presentation" aria-hidden="true">&middot;</span> Viewing member profile <em><a href="/forums/index.php?members/popuko.154/" dir="auto">popuko</a></em>
            for idx, line in enumerate(response_lines):
                # print(line)
                if 'Last seen' in line:
                    last_seen_string = response_lines[idx+2]
                    regex_pattern = 'data-time="\d*"'
                    if re.search(regex_pattern, last_seen_string):
                        regex_group = re.search(regex_pattern, last_seen_string)
                        x = regex_group.group()
                        reg_array = re.split('"', x)
                        # print(reg_array)
                        last_seen_unix_timestamp = reg_array[1]
                        break
        return [last_seen_unix_timestamp, list_of_user_matches]
    except Exception as e:
        return [-1, [-1, -1]]

async def mkc_request_mkc_player_id(mkc_user_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_mkc_player_id, mkc_user_id)
        return_value = future.result()
    return return_value

def mt_mkc_request_mkc_player_id(mkc_user_id):
    try:
        login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
        data_url = 'https://www.mariokartcentral.com/mkc/api/registry/players/all'
        with requests.Session() as s:
            html = s.get(login_url).content
            soup = Soup(html, 'html.parser')
            token = soup.select_one('[name=_xfToken]').attrs['value']
            payload = {
            'login': str(secrets.mkc_name),
            'password': str(secrets.mkc_password),
            '_xfToken': str(token),
            '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
            }
            response = s.post(login_url, data=payload)
            response = s.get(data_url)
        registry_data = response.json()
        response = json.dumps(registry_data)
        response = json.loads(response)
        for player in response["data"]:
            if player["user_id"] == int(mkc_user_id):
                mkc_player_id = player["player_id"]
                break
            else:
                continue
        if mkc_player_id != None:
            return mkc_player_id
        else:
            return -1
    except Exception:
        return -1

async def mkc_request_registry_info(mkc_player_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_mkc_request_registry_info, mkc_player_id)
        return_value = future.result()
    return return_value

# returs user_id, country_code, is_banned
def mt_mkc_request_registry_info(mkc_player_id):
    try:
        mkcresponse = requests.get("https://www.mariokartcentral.com/mkc/api/registry/players/" + str(mkc_player_id))
        mkc_data = mkcresponse.json()
        buh = json.dumps(mkc_data)
        mkc_data_dict = json.loads(buh)
        return_value = [mkc_data_dict['user_id'], mkc_data_dict['country_code'], mkc_data_dict['is_banned']]
        return return_value
    except Exception:
        return [-1, -1, -1]

# Takes ctx and Discord ID, returns mkc_user_id
async def lounge_request_mkc_user_id(ctx):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(mt_lounge_request_mkc_user_id, ctx)
        return_value = future.result()
    return return_value

def mt_lounge_request_mkc_user_id(ctx):
    try:
        player_id = ctx.author.id
        loungeresponse = requests.get("https://www.mk8dx-lounge.com/api/player?discordId=" + str(player_id))
        lounge_data = loungeresponse.json()
        guh = json.dumps(lounge_data) # dump to a string
        lounge_data_dict = json.loads(guh) # loads to a dict
        mkc_user_id = lounge_data_dict["mkcId"]
    except Exception:
        return -1
    return mkc_user_id


async def grandmaster_wrapper(input):
    return (f'[0;2m[0;40m[0;31m{input}[0m[0;40m[0m[0m')

async def master_wrapper(input):
    return (f'[2;40m[2;37m{input}[0m[2;40m[0m')

async def diamond_wrapper(input):
    return (f'[0;2m[0;34m{input}[0m[0m')

async def platinum_wrapper(input):
    return (f'[2;40m[2;36m{input}[0m[2;40m[0m')

async def gold_wrapper(input):
    return (f'[2;40m[2;33m{input}[0m[2;40m[0m')

async def silver_wrapper(input):
    return (f'[0;2m[0;42m[0;37m{input}[0m[0;42m[0m[0m')

async def bronze_wrapper(input):
    return (f'[0;2m[0;47m[0;33m{input}[0m[0;47m[0m[0m')

async def iron_wrapper(input):
    return (f'[0;2m[0;30m[0;47m{input}[0m[0;30m[0m[0m')

async def pos_mmr_wrapper(input):
    return (f'[0;2m[0;32m{input}[0m[0m')

async def neg_mmr_wrapper(input):
    return (f'[0;2m[0;31m{input}[0m[0m')

async def peak_mmr_wrapper(input):
    return (f'[0;2m[0;41m[0;37m{input}[0m[0;41m[0m[0m')

async def bold_wrapper(input):
    return (f'[0;2m[1;2m{input}[0m[0m')

async def underline_wrapper(input):
    return (f'[0;2m[4;2m{input}[0m[0m')

client.run(secrets.token)