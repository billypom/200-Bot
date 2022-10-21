import DBA
import secretly
import plotting
import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
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
import csv
import urllib.parse
import shutil
import subprocess
import concurrent.futures
from bs4 import BeautifulSoup as Soup
import pykakasi
from korean_romanizer.romanizer import Romanizer

Lounge = [461383953937596416]
mogi_media_channel_id = 1005091507604312074
# mogi_media_message_id = 1005205285817831455
TIER_ID_LIST = list()
RANK_ID_LIST = [791874714434797589, 794262638518730772, 794262898423627857, 794262916627038258, 794262925098745858, 794262959084797984, 794263467581374524, 970028275789365368, 846497627508047872]
MAX_PLAYERS_IN_MOGI = 12
SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT = 604800
NAME_CHANGE_DELTA_LIMIT = 5184000
REPORTER_ROLE_ID = 872770141606273034
ADMIN_ROLE_ID = 461388423572357130
UPDATER_ROLE_ID = 461461018971996162
CHAT_RESTRICTED_ROLE_ID = 845084987417559040
LOUNGELESS_ROLE_ID = 463868896743522304
PLACEMENT_ROLE_ID = 846497627508047872
twitch_thumbnail = 'https://cdn.discordapp.com/attachments/898031747747426344/1005204380208869386/jimmy_neutron_hamburger.jpg'
intents = discord.Intents(messages=True, guilds=True, message_content=True, members=True, reactions=True)
client = discord.Bot(intents=intents, activity=discord.Game(str('200cc Lounge')))
# manage roles, manage channels, manage nicknames, read messages/viewchannels, manage events
# send messages, manage messages, embed links, attach files, read message history, add reactions, use slash commands

initial_extensions = ['cogs.inactivity_check', 'cogs.update_mogilist', 'cogs.mogi_media_check']
for extension in initial_extensions:
    client.load_extension(extension)


# Initialize the TIER_ID_LIST
with DBA.DBAccess() as db:
    get_tier_list = db.query('SELECT tier_id FROM tier WHERE tier_id > %s;', (0,))
    for i in range(len(get_tier_list)):
        TIER_ID_LIST.append(get_tier_list[i][0])

# # Initialize the RANK_ID_LIST
# with DBA.DBAccess() as db:
#     temp = db.query('SELECT rank_id FROM ranks WHERE rank_id > %s;', (0,))
#     for i in range(len(temp)):
#         RANK_ID_LIST.append(temp[i][0])

# Discord UI button - Confirmation button
class Confirm(View):
    def __init__(self, uid):
        super().__init__()
        self.value = None
        self.uid = uid

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Only accept input from user who initiated the interaction
        if self.uid != interaction.user.id:
            return
        await interaction.response.send_message("Confirming...", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Only accept input from user who initiated the interaction
        if self.uid != interaction.user.id:
            return
        await interaction.response.send_message("Denying...", ephemeral=True)
        self.value = False
        self.stop()



# OLD MULTITHREAD CODE
# "threading in python is a bit of a lie, python has a global interpreter lock which means that even if you have multiple threads running, 
# it can only run one thread at a time so if you have two threads running, then python in the background just switches between them"
# - Vike 10/19/2022
# "i delet multi thred"
# - me
# # Not async because of concurrent futures
# def get_live_streamers(temp):
#     list_of_streams = []
#     for i in range(0, len(temp)):
#         streamer_name = temp[i][0]
#         if streamer_name is None:
#             continue
#         else:
#             streamer_name = str(streamer_name).strip().lower()
#         body = {
#             'client_id': secretly.twitch_client_id,
#             'client_secret': secretly.twitch_client_secret,
#             "grant_type": 'client_credentials'
#         }
#         r = requests.post('https://id.twitch.tv/oauth2/token', body)
#         #data output
#         keys = r.json()
#         #print(keys)
#         headers = {
#             'Client-ID': secretly.twitch_client_id,
#             'Authorization': 'Bearer ' + keys['access_token']
#         }
#         #print(headers)
#         stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
#         stream_data = stream.json()
#         try:
#             if len(stream_data['data']) == 1:
#                 is_live = True
#                 streamer_name = stream_data['data'][0]['user_name']
#                 stream_title = stream_data['data'][0]['title']
#                 stream_thumbnail_url = stream_data['data'][0]['thumbnail_url']
#                 list_of_streams.append([streamer_name, stream_title, stream_thumbnail_url, is_live, temp[i][1], temp[i][2]])
#             else:
#                 is_live = False
#                 stream_title = ""
#                 stream_thumbnail_url = ""
#                 list_of_streams.append([streamer_name, stream_title, stream_thumbnail_url, is_live, temp[i][1], temp[i][2]])
#         except Exception as e:
#             continue

#         # name, title, image, is_live, db_mogimediamessageid, db_player_id
        
#     return list_of_streams

# def mogi_media_check():
    # try:
    #     with DBA.DBAccess() as db:
    #         temp = db.query('SELECT p.twitch_link, p.mogi_media_message_id, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.can_drop = 0;', ())
    # except Exception:
    #     return

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future = executor.submit(get_live_streamers, temp)
    #     streams = future.result()
    # # print(f'future.result from thread executor: {streams}')
    # for stream in streams:
    #     try:
    #         # If live
    #         if stream[3]:
    #             # If no mogi media sent yet
    #             if stream[4] is None:
    #                 member_future = asyncio.run_coroutine_threadsafe(GUILD.fetch_member(stream[5]), client.loop)
    #                 member = member_future.result()
    #                 embed = discord.Embed(title=stream[0], description=stream[1], color=discord.Color.purple())
    #                 embed.add_field(name='Link', value=f'https://twitch.tv/{stream[0]}', inline=False)
    #                 embed.set_image(url=stream[2])
    #                 embed.set_thumbnail(url=member.display_avatar)
    #                 mogi_media = client.get_channel(mogi_media_channel_id)
    #                 temp_val = asyncio.run_coroutine_threadsafe(mogi_media.send(embed=embed), client.loop)
    #                 mogi_media_message = temp_val.result()
    #                 with DBA.DBAccess() as db:
    #                     db.execute('UPDATE player SET mogi_media_message_id = %s WHERE player_id = %s;', (mogi_media_message.id, member.id))
    #         # If not live
    #         else:
    #             if stream[4] > 0: 
    #                 member_future = asyncio.run_coroutine_threadsafe(GUILD.fetch_member(stream[5]), client.loop)
    #                 member = member_future.result()               
    #                 channel = client.get_channel(mogi_media_channel_id)
    #                 temp_message = asyncio.run_coroutine_threadsafe(channel.fetch_message(stream[4]), client.loop)
    #                 message = temp_message.result()
    #                 asyncio.run_coroutine_threadsafe(message.delete(), client.loop)
    #                 with DBA.DBAccess() as db:
    #                     db.execute('UPDATE player SET mogi_media_message_id = NULL WHERE player_id = %s;', (member.id,))
    #     except Exception as e:
    #         continue

# def update_mogilist():
#     try:
#         MOGILIST = {}
#         pre_ml_string = ''
#         pre_mllu_string = ''
#         remove_chars = {
#             39:None, # ,
#             91:None, # [
#             93:None, # ]
#         }
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT t.tier_id, p.player_name FROM tier t INNER JOIN lineups l ON t.tier_id = l.tier_id INNER JOIN player p ON l.player_id = p.player_id WHERE p.player_id > %s;', (1,))
#         for i in range(len(temp)): # create dictionary {tier_id:[list of players in tier]}
#             if temp[i][0] in MOGILIST:
#                 MOGILIST[temp[i][0]].append(temp[i][1])
#             else:
#                 MOGILIST[temp[i][0]]=[temp[i][1]]
#         num_active_mogis = len(MOGILIST.keys())
#         num_full_mogis = 0
#         for k,v in MOGILIST.items():
#             pre_ml_string += f'<#{k}> - ({len(v)}/12)\n'
#             if len(v) >= 12:
#                 num_full_mogis +=1
#             mllu_players = str(v).translate(remove_chars)
#             pre_mllu_string += f'<#{k}> - ({len(v)}/12) - {mllu_players}\n'
#         title = f'There are {num_active_mogis} active mogi and {num_full_mogis} full mogi.\n\n'
#         ml_string = f'{title}{pre_ml_string}'
#         mllu_string = f'{title}{pre_mllu_string}'

#         ml = client.get_channel(secretly.mogilist_channel)
#         # returns a Future object. need to get the .result() of the Future (which is the Discord.message object)
#         ml_message = asyncio.run_coroutine_threadsafe(ml.fetch_message(ml_channel_message_id), client.loop)
#         asyncio.run_coroutine_threadsafe(ml_message.result().edit(content=f'{ml_string}'), client.loop)

#         mllu = client.get_channel(secretly.mogilist_lu_channel)
#         mllu_message = asyncio.run_coroutine_threadsafe(mllu.fetch_message(ml_lu_channel_message_id), client.loop)
#         asyncio.run_coroutine_threadsafe(mllu_message.result().edit(content=f'{mllu_string}'), client.loop)
#     except Exception as e:
#         asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel('mogilist error', e), client.loop)

# def inactivity_check():
#     # print('checking inactivity')
#     unix_now = time.mktime(datetime.datetime.now().timetuple())
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT l.player_id, UNIX_TIMESTAMP(l.last_active), l.tier_id, l.wait_for_activity, p.player_name FROM lineups as l JOIN player as p ON l.player_id = p.player_id WHERE l.can_drop = %s;', (1,))
#     except Exception as e:
#         asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'inactivity_check error 1 {secrely.my_discord}', e), client.loop)
#         return
#     for i in range(len(temp)):
#         name = temp[i][4]
#         unix_difference = unix_now - temp[i][1]
#         # print(f'{unix_now} - {temp[i][1]} = {unix_difference}')
#         if unix_difference < 900: # if it has been less than 15 minutes
#             if unix_difference > 600: # if it has been more than 10 minutes
#                 channel = client.get_channel(temp[i][2])
#                 if temp[i][3] == 0: # false we are not waiting for activity
#                     message = f'<@{temp[i][0]}> Type anything in the chat in the next 5 minutes to keep your spot in the mogi.'
#                     asyncio.run_coroutine_threadsafe(channel.send(message, delete_after=300), client.loop)
#                     # set wait_for_activity = 1 means the ping was already sent.
#                     try:
#                         with DBA.DBAccess() as db:
#                             db.execute('UPDATE lineups SET wait_for_activity = %s WHERE player_id = %s;', (1, temp[i][0])) # we are waiting for activity
#                     except Exception as e:
#                         asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'inactivity_check error 2 {secrely.my_discord}', e), client.loop)
#                         return
#             else: # has not been at least 10 minutes yet
#                 continue # does this make it faster? idk
#         elif unix_difference > 1200: # if its been more than 20 minutes
#             # Drop player
#             try:
#                 with DBA.DBAccess() as db:
#                     db.execute('DELETE FROM lineups WHERE player_id = %s;', (temp[i][0],))
#             except Exception as e:
#                 asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'{secrely.my_discord} inactivity_check - cannot delete from lineup',f'{temp[i][0]} | {temp[i][1]} | {temp[i][2]} | {e}'), client.loop)
#                 return
#             # Send message
#             channel = client.get_channel(temp[i][2])
#             message = f'{name} has been removed from the mogi due to inactivity'
#             asyncio.run_coroutine_threadsafe(channel.send(message), client.loop)
#         else:
#             continue

# def lounge_threads():
#     time.sleep(30)
#     while(True):
#         pass
#         # update_mogilist()
#         # inactivity_check()
#         # mogi_media_check()
#         # time.sleep(15)


# poll_thread = threading.Thread(target=lounge_threads)
# poll_thread.start()


@client.event
async def on_ready():
    global GUILD
    global CHAT_RESTRICTED_ROLE
    global LOUNGELESS_ROLE
    GUILD = client.get_guild(Lounge[0])
    CHAT_RESTRICTED_ROLE = GUILD.get_role(CHAT_RESTRICTED_ROLE_ID)
    LOUNGELESS_ROLE = GUILD.get_role(LOUNGELESS_ROLE_ID)

@client.event
async def on_application_command_error(ctx, error):
    if ctx.guild == None:
        channel = client.get_channel(secretly.debug_channel)
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
    elif isinstance(error, commands.MissingRole):
        await ctx.respond('You do not have permission to use this command.', delete_after=20)
        return
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.respond('You do not have permission to use this command.', delete_after=20)
        return
    else:
        channel = client.get_channel(secretly.debug_channel)
        embed = discord.Embed(title='Error', description=':eyes:', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond(f'Sorry! An unknown error occurred. Contact {secretly.my_discord} if you think this is a mistake.')
        # print(traceback.format_exc())
        raise error
        return

@client.event
async def on_message(ctx):
    if ctx.guild == GUILD: # Only care if messages are in 200 Lounge
        pass
    else:
        return
    if ctx.author.id == secretly.bot_id: # ignore self messages
        return
    if ctx.channel.id == 558096949337915413: # ignore carl bot logging
        return
    user = await GUILD.fetch_member(ctx.author.id)
    if CHAT_RESTRICTED_ROLE in user.roles: # restricted players
        if ctx.content in secretly.chat_restricted_words:
            pass
        else:
            await ctx.delete()
    if ctx.channel.id in TIER_ID_LIST: # Only care if messages are in a tier
        # If player in lineup, set player chat activity timer
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id, tier_id FROM lineups WHERE player_id = %s;', (ctx.author.id,))
        except Exception as e:
            await send_to_debug_channel(ctx, f'on_message error 1 | {e}')
            return
        try:
            test_assign = temp[0][0]
        except Exception:
            # player not in lineup talked. dont care
            return
        if temp[0][0] is None:
            return
        else:
            if ctx.channel.id == temp[0][1]: # Type activity in correct channel
                try:
                    with DBA.DBAccess() as db:
                        db.execute('UPDATE lineups SET last_active = %s, wait_for_activity = %s WHERE player_id = %s;', (datetime.datetime.now(), 0, ctx.author.id))
                except Exception as e:
                    await send_to_debug_channel(ctx, f'on_message error 2 | {e}')
                    return
        try:
            with DBA.DBAccess() as db:
                get_tier = db.query('SELECT voting, tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
        except Exception as e:
            await send_to_debug_channel(ctx, f'on_message error 3 | {e}')
        # Set votes, if tier is currently voting
        if get_tier[0][0]:
            if get_tier[0][1] == ctx.channel.id:
                if str(ctx.content) in ['1', '2', '3', '4', '6']:
                    try:
                        with DBA.DBAccess() as db:
                            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s ORDER BY create_date LIMIT %s;', (ctx.author.id, ctx.channel.id, MAX_PLAYERS_IN_MOGI)) # limit prevents 13th person from voting
                    except Exception as e:
                        await send_to_debug_channel(ctx, f'on_message error 4 {e}')
                        return
                    try:
                        with DBA.DBAccess() as db:
                            db.execute('UPDATE lineups SET vote = %s WHERE player_id = %s;', (int(ctx.content), ctx.author.id))
                    except Exception as e:
                        await send_to_debug_channel(ctx, f'on_message error 5 {e}')
                        return

@client.event
async def on_raw_reaction_add(payload):
    if int(payload.user_id) == int(secretly.bot_id): # Return if bot reaction
        return
    if payload.channel_id == secretly.name_change_channel:
        pass
    else: # Return if this isnt a name change approval
        return

    # Stuff relating to the current embed
    guild = client.get_guild(payload.guild_id)
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    try:
        with DBA.DBAccess() as db:
            message_ids = db.query('SELECT embed_message_id, player_id, requested_name FROM player_name_request WHERE was_accepted = %s;', (0,))
    except Exception:
        return

    # Look @ all embed message ids
    for i in range(0, len(message_ids)):
        if int(payload.message_id) == int(message_ids[i][0]):
            # Join
            try:
                if str(payload.emoji) == '✅':
                    with DBA.DBAccess() as db:
                        # Set record to accepted
                        db.execute('UPDATE player_name_request SET was_accepted = %s WHERE embed_message_id = %s;', (1, int(payload.message_id)))
                        # Change the db username
                        db.execute('UPDATE player SET player_name = %s WHERE player_id = %s;', (message_ids[i][2], message_ids[i][1]))
                        # Change the discord username
                    member = guild.get_member(message_ids[i][1])
                    await member.edit(nick=str(message_ids[i][2]))
                    await member.send(f'Your name change has been approved.')
                    # Delete the embed message
                    await message.delete()
                if str(payload.emoji) == '❌':
                    with DBA.DBAccess() as db:
                        # Remove the db record
                        db.execute('DELETE FROM player_name_request WHERE embed_message_id = %s;', (int(payload.message_id),))
                        # Delete the embed message
                    member = guild.get_member(message_ids[i][1])
                    await member.send(f'Your name change has been denied.')
                    await message.delete()
            except Exception:
                pass
        try:
            await message.remove_reaction(payload.emoji, member)
        except Exception:
            pass
    return



# /verify <link>
@client.slash_command(
    name='verify',
    description='Verify your MKC account',
    # guild_ids=Lounge
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
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
            return
        else:
            pass
        response = await set_player_roles(ctx)
        await ctx.respond(response)
        return
    else:
        pass
    # Regex on https://www.mariokartcentral.com/mkc/registry/players/930
    if 'registry' in message:
        regex_pattern = 'players/\d*'
        regex_pattern2 = 'users/\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            reg_array = re.split('/', x)
            mkc_player_id = reg_array[len(reg_array)-1]
        elif re.search(regex_pattern2, str(message.content)):
            regex_group = re.search(regex_pattern2, message.content)
            x = regex_group.group()
            reg_array = re.split('/', x)
            mkc_player_id = reg_array[len(reg_array)-1]
        else:
            await ctx.respond('``Error 2:`` Oops! Something went wrong. Check your link or try again later')
            return
    # Regex on https://www.mariokartcentral.com/forums/index.php?members/popuko.154/
    elif 'forums' in message:
        regex_pattern = 'members/.*\.\d*'
        regex_pattern2 = 'members/\d*'
        if re.search(regex_pattern, str(message)):
            regex_group = re.search(regex_pattern, message)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp)-1])
        elif re.search(regex_pattern2, str(message.content)):
            regex_group = re.search(regex_pattern2, message.content)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp)-1])
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
        await ctx.respond('``Error 8:`` Oops! Something went wrong. Check your link or try again later')
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
        if seconds_since_last_login > SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT:
            verify_description = vlog_msg.error5
            verify_color = discord.Color.red()
            await ctx.respond('``Error 5:`` Please log in to your MKC account, then retry. \n\nIf you are still being refused verification, click this link then try again: https://www.mariokartcentral.com/forums/index.php?members/popuko.154/')
            await send_to_verification_log(ctx, message, verify_color, verify_description)
            return
        else:
            pass
    else:
        verify_description = vlog_msg.error7
        verify_color = discord.Color.red()
        await ctx.respond('``Error 6:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return
    if user_matches_list:
        verify_color = discord.Color.teal()
        await send_to_ip_match_log(ctx, message, verify_color, user_matches_list)
    # All clear. Roll out.
    verify_description = vlog_msg.success
    verify_color = discord.Color.green()
    # Check if someone has verified as this user before...
    x = await check_if_mkc_user_id_used(mkc_user_id)
    if x:
        await ctx.respond(f'``Error 10: Duplicate player`` If you think this is a mistake, please contact {secretly.my_discord} immediately. ')
        verify_description = vlog_msg.error4
        verify_color = discord.Color.red()
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return
    else:
        x = await create_player(ctx, mkc_user_id, country_code)
        await ctx.respond(x)
        await send_to_verification_log(ctx, message, verify_color, verify_description)
        return

# /c
@client.slash_command(
    name='c',
    description='🙋 Can up for a mogi',
    # guild_ids=Lounge
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def c(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    # Player was already in lineup, got subbed out
    with DBA.DBAccess() as db:
        temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (ctx.author.id,))
        if temp:
            if temp[0][0] == ctx.author.id:
                await ctx.respond('Please wait for the mogi you left to finish')
                return
        else:
            pass
    x = await check_if_uid_in_any_tier(ctx.author.id)
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
        await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secretly.my_discord}.')
        await send_to_debug_channel(ctx, f'/c error 18 lineup not found? {e}')
        return
    # ADDITIONAL SUBS SHOULD BE ABLE TO JOIN NEXT MOGI
    # if count == MAX_PLAYERS_IN_MOGI:
    #     await ctx.respond('Mogi is full')
    #     return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
        if temp:
            if temp[0][0] == ctx.author.id:
                await ctx.respond('You are already in the mogi')
                return
            else:
                pass
    except Exception as e:
        pass
        # await ctx.respond(f'``Error 46:`` Something went wrong! Contact {secretly.my_discord}.')
        # await send_to_debug_channel(ctx, e)
        # return
    if ctx.channel.id == 965286774098260029:
        await ctx.respond('Use !c to join squad queue')
        return
    # Add player to lineup
    try:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO lineups (player_id, tier_id, last_active) values (%s, %s, %s);', (ctx.author.id, ctx.channel.id, datetime.datetime.now()))
    except Exception as e:
        await ctx.respond(f'``Error 16:`` Something went wrong! Contact {secretly.my_discord}.')
        await send_to_debug_channel(ctx, f'/c error 16 unable to join {e}')
        return
    await ctx.respond('You have joined the mogi! You can /d in `15 seconds`')
    channel = client.get_channel(ctx.channel.id)
    await channel.send(f'{ctx.author.display_name} has joined the mogi!')
    count+=1
    # Check for full lineup
    if count == MAX_PLAYERS_IN_MOGI:
        # start the mogi, vote on format, create teams
        mogi_started_successfully = await start_mogi(ctx)
        if mogi_started_successfully == 1:
            pass
            # Chooses a host. Says the start time
        elif mogi_started_successfully == 0:
            channel = client.get_channel(ctx.channel.id)
            await channel.send(f'``Error 45:`` Failed to start mogi. {secretly.my_discord}!!!!!!!!!!!!')
            return
        elif mogi_started_successfully == 2:
            channel = client.get_channel(ctx.channel.id)
            await channel.send(f'``Error 54:`` Failed to start mogi. {secretly.my_discord}!!!!!!!!!!!!!!')
            return
    elif count == 6 or count == 11:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'@here +{12-count}')
    return

# /d
@client.slash_command(
    name='d',
    description='Drop from the mogi',
    # guild_ids=Lounge
)
async def d(
    ctx,
    ):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    # Player was already in lineup, got subbed out
    with DBA.DBAccess() as db:
        temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (ctx.author.id,))
        if temp:
            if temp[0][0] == ctx.author.id:
                await ctx.respond('Please wait for the mogi you left to finish')
                return
        else:
            pass
    x = await check_if_uid_in_any_tier(ctx.author.id)
    if x:
        y = await check_if_uid_can_drop(ctx.author.id)
        if y:
            pass
        else:
            await ctx.respond('You cannot drop from an ongoing mogi')
            return
        # No try block - check is above...
        with DBA.DBAccess() as db:
            tier_temp = db.query('SELECT t.tier_id, t.tier_name FROM tier as t JOIN lineups as l ON t.tier_id = l.tier_id WHERE player_id = %s;', (ctx.author.id,))
        try:
            with DBA.DBAccess() as db:
                db.execute('DELETE FROM lineups WHERE player_id = %s;', (ctx.author.id,))
                await ctx.respond(f'You have dropped from tier {tier_temp[0][1]}')
        except Exception as e:
            await send_to_debug_channel(ctx, f'/d error 17 cant leave lineup {e}')
            await ctx.respond(f'``Error 17:`` Oops! Something went wrong. Contact {secretly.my_discord}')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name FROM player WHERE player_id = %s;', (ctx.author.id,))
                channel = client.get_channel(tier_temp[0][0])
                await channel.send(f'{temp[0][0]} has dropped from the lineup')
        except Exception as e:
            await send_to_debug_channel(ctx, f'/d big error...WHAT! 1 {e}')
            # i should never ever see this...
        return
    else:
        await ctx.respond('You are not in a mogi')
        return

# /l
@client.slash_command(
    name='l',
    description='Show the mogi list',
    # guild_ids=Lounge
)
# @commands.command(aliases=['list'])
@commands.cooldown(1, 30, commands.BucketType.user)
async def l(
    ctx
    ):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    try:
        with DBA.DBAccess() as db:
            temp = db.query("SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;", (ctx.channel.id,))
    except Exception as e:
        await ctx.respond(f'``Error 20:`` Oops! Something went wrong. Please contact {secretly.my_discord}')
        return
    response = '`Mogi List`:'
    for i in range(len(temp)):
        response = f'{response}\n`{i+1}.` {temp[i][0]}'
    response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
    await ctx.respond(response, delete_after=30)
    return

# /sub
@client.slash_command(
    name='sub',
    description='Sub out a player',
    # guild_ids=Lounge
)
async def sub(
    ctx,
    leaving_player: discord.Option(discord.Member, 'Leaving player', required=True),
    subbing_player: discord.Option(discord.Member, 'Subbing player', required=True)
    ):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    # Same player
    if leaving_player.id == subbing_player.id:
        await ctx.respond('<:bruh:1006883398607978537>')
        return
    # Player was already in lineup, got subbed out
    with DBA.DBAccess() as db:
        temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (subbing_player.id,))
        if temp:
            if temp[0][0] == subbing_player.id:
                await ctx.respond('Player cannot sub into a mogi after being subbed out.')
                return
        else:
            pass
    # Player exists
    a = await check_if_uid_exists(leaving_player.id)
    if a:
        pass
    else:
        await ctx.respond('Use `/verify <mkc link>` to register for Lounge')
        return
    b = await check_if_uid_exists(subbing_player.id)
    if b:
        pass
    else:
        await ctx.respond(f'{subbing_player.name} is not registered for Lounge')
        return
    x = await check_if_mogi_is_ongoing(ctx)
    if x:
        pass
    else:
        await ctx.respond('Mogi has not started')
        return
    # Only players in the mogi can sub out others
    y = await check_if_uid_in_first_12_of_tier(ctx.author.id, ctx.channel.id)
    if y:
        pass
    else:
        await ctx.respond('You are not in the mogi. You cannot sub out another player')
        return
    z = await check_if_uid_in_specific_tier(leaving_player.id, ctx.channel.id)
    if z:
        pass
    else:
        await ctx.respond(f'<@{leaving_player.id}> is not in this mogi.')
        return
    try:
        with DBA.DBAccess() as db:
            first_12 = db.query('SELECT player_id FROM (SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12) as l WHERE player_id = %s;', (ctx.channel.id, subbing_player.id))
            if first_12: # if there are players in lineup (first 12)
                if first_12[0][0] == subbing_player.id: # if subbing is already in lineup (first 12)
                    await ctx.respond(f'{subbing_player.mention} is already in this mogi')
                    return
                else:
                    pass
            try:
                leaving_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (leaving_player.id,))[0][0]
                subbing_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (subbing_player.id,))[0][0]
                teams_string = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))[0][0]
                teams_string = teams_string.replace(leaving_player_name, subbing_player_name)
                teams_string += f'\n\n`EDITED`: `{leaving_player_name}` -> `{subbing_player_name}`'
                db.execute('DELETE FROM lineups WHERE player_id = %s;', (subbing_player.id,))
                db.execute('UPDATE lineups SET player_id = %s WHERE player_id = %s;', (subbing_player.id, leaving_player.id))
                db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (teams_string, ctx.channel.id))
            except Exception:
                await ctx.respond(f'``Error 42:`` FATAL ERROR - {secretly.my_discord} help!!!')
                return
    except Exception as e:
        await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {secretly.my_discord}')
        await send_to_debug_channel(ctx, f'/sub error 19 {e}')
        return
    with DBA.DBAccess() as db:
        db.execute('INSERT INTO sub_leaver (player_id, tier_id) VALUES (%s, %s);', (leaving_player.id, ctx.channel.id))
    await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
    await send_to_sub_log(ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}> in {ctx.channel.mention}')
    return

# /fc
@client.slash_command(
    name='fc',
    description='Display or set your friend code',
    # guild_ids=Lounge
)
async def fc(
    ctx,
    fc: discord.Option(str, 'XXXX-XXXX-XXXX', required=False)):
    if fc == None:
        await ctx.defer()
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT fc FROM player WHERE player_id = %s;', (ctx.author.id, ))
                await ctx.respond(temp[0][0])
        except Exception as e:
            await ctx.respond('``Error 12:`` No friend code found. Use ``/fc XXXX-XXXX-XXXX`` to set.')
    else:
        await ctx.defer(ephemeral=True)
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
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

# /name
@client.slash_command(
    name='name',
    description='Change your name',
    # guild_ids=Lounge
)
async def name(
    ctx,
    name: discord.Option(str, 'New name', required=True)
    ):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    y = await check_if_player_exists(ctx)
    if y:
        pass
    else:
        await ctx.respond('Use `/verify <mkc link>` to register with Lounge')
        return
    z = await check_if_uid_can_drop(ctx.author.id)
    if z:
        pass
    else:
        await ctx.respond('You cannot change your name while playing a Mogi.')
        return
    x = await check_if_banned_characters(name)
    if x:
        await send_to_verification_log(ctx, name, discord.Color.blurple(), vlog_msg.error1)
        await ctx.respond('You cannot use this name')
        return
    else:
        pass
    input_name = name
    name = await jp_kr_romanize(name)
    name = name.replace(" ", "-")
    if len(name) > 16:
        await ctx.respond(f'Your request: {input_name} -> Conversion: {name} | Name is too long. 16 characters max')
        return
    is_name_taken = True
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (name,))
            if temp[0][0] is None:
                is_name_taken = False
            else:
                is_name_taken = True
    except Exception as e:
        is_name_taken = False
    if is_name_taken:
        await ctx.respond('Name is taken. Please try again.')
        return
    else:
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM player_name_request WHERE player_id = %s;', (ctx.author.id,))
                last_change = temp[0][0]
                unix_now = await get_unix_time_now()
                difference = unix_now - last_change
                # 2 months for every name change
                if difference > NAME_CHANGE_DELTA_LIMIT:
                    pass
                else:
                    await ctx.respond(f'Request denied. You can change your name again on <t:{str(int(last_change) + int(NAME_CHANGE_DELTA_LIMIT))}:F>')
                    return
        except Exception as e:
            await send_to_debug_channel(ctx, f'First name change request from <@{ctx.author.id}>. Still logging this error 34 in case...\n{e}')
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO player_name_request (player_id, requested_name) VALUES (%s, %s);', (ctx.author.id, name))
                temp = db.query('SELECT id FROM player_name_request WHERE player_id = %s AND requested_name = %s ORDER BY create_date DESC LIMIT 1;', (ctx.author.id, name))
                player_name_request_id = temp[0][0]
            request_message = await send_to_name_change_log(ctx, player_name_request_id, name)
            request_message_id = request_message.id
            await request_message.add_reaction('✅')
            await request_message.add_reaction('❌')
        except Exception as e:
            await send_to_debug_channel(ctx, f'Tried name: {name} |\n{e}')
            await ctx.respond(f'``Error 44:`` Oops! Something went wrong. Please try again or contact {secretly.my_discord}')
            return
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player_name_request SET embed_message_id = %s WHERE id = %s;', (request_message_id, player_name_request_id))
            await ctx.respond(f'Your request: {input_name} -> Conversion: {name} | Your name change request was submitted to the staff team for review.')
            return
        except Exception as e:
            await send_to_debug_channel(ctx, f'Tried name: {name} |\n{e}')
            await ctx.respond(f'``Error 35:`` Oops! Something went wrong. Please try again or contact {secretly.my_discord}')
            return

# /table
@client.slash_command(
    name='table',
    description='Submit a table',
    # guild_ids=Lounge
)
@commands.has_role(REPORTER_ROLE_ID)
async def table(
    ctx,
    mogi_format: discord.Option(int, '1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6', required=True),
    scores: discord.Option(str, 'player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)', required=True)
    ):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    bad = await check_if_banned_characters(str(scores))
    if bad:
        await send_to_verification_log(ctx, scores, discord.Color.blurple(), vlog_msg.error1)
        await ctx.respond(f'``Error 32:`` Invalid input. There must be 12 players and 12 scores.')
        return

    # Create list
    score_string = str(scores) #.translate(remove_chars)
    score_list = score_string.split()

    # Check for 12 players
    if len(score_list) == 24:
        pass
    else:
        await ctx.respond(f'``Error 26:`` Invalid input. There must be 12 players and 12 scores.')
        return
    
    # Replace playernames with playerids

    #print(f'score list: {score_list}')
    player_list_check = []
    player_id_list_check = []
    for i in range(0, len(score_list), 2):
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (score_list[i],))
            player_list_check.append(score_list[i])
            score_list[i] = temp[0][0]
            player_id_list_check.append(temp[0][0])

    # Check for if mogi has started
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
            players_in_lineup_count = temp[0][0]
    except Exception as e:
        await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secretly.my_discord}. {e}')
        await send_to_debug_channel(ctx, f'/table Error 18: {e}')
        return
    if players_in_lineup_count < 12:
        await ctx.respond('Mogi has not started. Cannot create a table now')
        return

    
    
    # Check for duplicate players
    has_dupes = await check_for_dupes_in_list(player_list_check)
    if has_dupes:
        await ctx.respond('``Error 37:`` You cannot have duplicate players on a table')
        return
    
    # Check if all 12 players are SUPPOSED to be on the table (1st 12 players. You can't just ignore a player and put the 13th player in the mogi without using the /sub command)
    for player in player_id_list_check:
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT can_drop FROM lineups WHERE player_id = %s AND tier_id = %s;', (player, ctx.channel.id))
                if temp[0][0] == 0:
                    pass
                else:
                    await ctx.respond(f'``Error 52:`` Unexpected player in lineup. Is there a sub among us? Please use the `/sub` command.\n\nCreate a ticket or contact {secretly.my_discord} if you think this is a mistake.')
                    return
        except Exception as e:
            await ctx.respond(f'``Error 53:`` Oops! Something went wrong. | Unexpected player in lineup. Is there a sub among us? Please use the `/sub` command.\n\nCreate a ticket or contact {secretly.my_discord} if you think this is a mistake.')
            await send_to_debug_channel(ctx, f'/table Error 53: temp: {temp}\ne: {e}')
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
        await ctx.respond(f'``Error 27:`` Invalid format: {mogi_format}. Please use 1, 2, 3, 4, or 6.')
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
    mogi_score = 0
    # print(f'length of chunked list: {len(chunked_list)}')
    # print(f'chunked list: {chunked_list}')
    for team in chunked_list:
        temp_mmr = 0
        team_score = 0
        count = 0
        for player in team:
            try:
                with DBA.DBAccess() as db:
                    # This part makes sure that only players in the current channel's lineup can have a table made for them
                    temp = db.query('SELECT mmr FROM (SELECT p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY create_date ASC LIMIT 12) as m JOIN player p on p.player_id = m.player_id WHERE p.player_id = %s;', (ctx.channel.id, player[0]))
                    if temp[0][0] is None:
                        mmr = 0
                        count += 1 # added this line 10/10/22 because placement players ppl are mad grrr i need my mmr
                    else:
                        mmr = temp[0][0]
                        count+=1
                    temp_mmr += mmr
                    try:
                        team_score += int(player[1])
                    except Exception:
                        score_and_pen = str(player[1]).split('-')
                        team_score = team_score + int(score_and_pen[0]) - int(score_and_pen[1])
            except Exception as e:
                # check for all 12 players exist
                await send_to_debug_channel(ctx, f'/table Error 24:{e}')
                await ctx.respond(f'``Error 24:`` There was an error with the following player: <@{player[0]}>. If this is a sub, you must first use the `/sub` command')
                return
        # print(team_score)
        if count == 0:
            count = 1
        team_mmr = temp_mmr/count
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
                score = player[1]
            lorenzi_query += f'{player_name} [{country_code}] {score}\n'

        # Assign previous values before looping
        prev_team_placement = team_placement
        prev_team_score = team[len(team)-3]

    # Request a lorenzi table
    query_string = urllib.parse.quote(lorenzi_query)
    url = f'https://gb.hlorenzi.com/table.png?data={query_string}'
    response = requests.get(url, stream=True)
    with open(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    # Ask for table confirmation
    table_view = Confirm(ctx.author.id)
    channel = client.get_channel(ctx.channel.id)
    await channel.send(file=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png'), delete_after=300)
    await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)
    await table_view.wait()
    if table_view.value is None:
        await ctx.respond('No response from reporter. Timed out')
    elif table_view.value: # yes
        db_mogi_id = 0
        # Create mogi
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);', (mogi_format, ctx.channel.id))

        # Get the results channel and tier name for later use
        with DBA.DBAccess() as db:
            temp = db.query('SELECT results_id, tier_name FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
            db_results_channel = temp[0][0]
            tier_name = temp[0][1]
        results_channel = client.get_channel(db_results_channel)

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
                        pre_mmr = (SPECIAL_TEAMS_INTEGER*((((team_x_mmr - team_y_mmr)/9998)**2)**(1/3))**2)
                        if team_x_mmr >= team_y_mmr:
                            pass
                        else: #team_x_mmr < team_y_mmr:
                            pre_mmr = pre_mmr * -1
                    else:
                        if team_x_placement > team_y_placement:
                            pre_mmr = (1 + OTHER_SPECIAL_INT*(1 + (team_x_mmr-team_y_mmr)/9998)**MULTIPLIER_SPECIAL)
                        else: #team_x_placement < team_y_placement
                            pre_mmr = -(1 + OTHER_SPECIAL_INT*(1 + (team_y_mmr-team_x_mmr)/9998)**MULTIPLIER_SPECIAL)
                working_list.append(pre_mmr)
            value_table.append(working_list)

        # # DEBUG
        # print(f'\nprinting value table:\n')
        # for _list in value_table:
        #     print(_list)

        # Actually calculate the MMR
        for idx, team in enumerate(sorted_list):
            temp_value = 0.0
            for pre_mmr_list in value_table:
                for idx2, value in enumerate(pre_mmr_list):
                    if idx == idx2:
                        temp_value += value
                    else:
                        pass
            team.append(math.floor(temp_value))

        # Create mmr table string
        if mogi_format == 1:
            string_mogi_format = 'FFA'
        else:
            string_mogi_format = f'{str(mogi_format)}v{str(mogi_format)}'

        mmr_table_string = f'<big><big>{ctx.channel.name} {string_mogi_format}</big></big>\n'
        mmr_table_string += f'PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n'

        for team in sorted_list:
            my_player_place = team[len(team)-2]
            string_my_player_place = str(my_player_place)
            for idx, player in enumerate(team):
                mmr_table_string += '\n'
                if idx > (mogi_format-1):
                    break
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT p.player_name, p.mmr, p.peak_mmr, p.rank_id, l.is_sub, p.mogi_media_message_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE p.player_id = %s;', (player[0],))
                    my_player_name = temp[0][0]
                    my_player_mmr = temp[0][1]
                    my_player_peak = temp[0][2]
                    my_player_rank_id = temp[0][3]
                    is_sub = temp[0][4]
                    mogi_media_message_id = temp[0][5]
                    if my_player_peak is None:
                        # print('its none...')
                        my_player_peak = 0
                my_player_score = int(player[1])
                my_player_new_rank = ''

                # Place the placement players
                placement_name = ''
                if my_player_mmr is None:
                    if my_player_score >=111:
                        my_player_mmr = 5250
                        placement_name = 'Gold'
                    elif my_player_score >= 81:
                        my_player_mmr = 3750
                        placement_name = 'Silver'
                    elif my_player_score >= 41:
                        my_player_mmr = 2250
                        placement_name = 'Bronze'
                    else:
                        my_player_mmr = 1000
                        placement_name = 'Iron'
                    with DBA.DBAccess() as db:
                        temp = db.query('SELECT rank_id FROM ranks WHERE placement_mmr = %s;', (my_player_mmr,))
                        init_rank = temp[0][0]
                        db.execute('UPDATE player SET base_mmr = %s, rank_id = %s WHERE player_id = %s;', (my_player_mmr, init_rank, player[0]))
                    discord_member = await GUILD.fetch_member(player[0])
                    init_role = GUILD.get_role(init_rank)
                    placement_role = GUILD.get_role(PLACEMENT_ROLE_ID)
                    await discord_member.add_roles(init_role)
                    await discord_member.remove_roles(placement_role)
                    await results_channel.send(f'<@{player[0]}> has been placed at {placement_name} ({my_player_mmr} MMR)')

                if is_sub: # Subs only gain on winning team
                    if team[len(team)-1] < 0:
                        my_player_mmr_change = 0
                    else:
                        my_player_mmr_change = team[len(team)-1]
                else:
                    my_player_mmr_change = team[len(team)-1]
                my_player_new_mmr = (my_player_mmr + my_player_mmr_change)

                # Start creating string for MMR table
                mmr_table_string += f'{string_my_player_place.center(6)}|'
                mmr_table_string +=f'{my_player_name.center(18)}|'
                mmr_table_string += f'{str(my_player_mmr).center(7)}|'

                # Check sign of mmr delta
                if my_player_mmr_change >= 0:
                    temp_string = f'+{str(my_player_mmr_change)}'
                    string_my_player_mmr_change = f'{temp_string.center(7)}'
                    formatted_my_player_mmr_change = await pos_mmr_wrapper(string_my_player_mmr_change)
                else:
                    string_my_player_mmr_change = f'{str(my_player_mmr_change).center(7)}'
                    formatted_my_player_mmr_change = await neg_mmr_wrapper(string_my_player_mmr_change)
                mmr_table_string += f'{formatted_my_player_mmr_change}|'

                # Check for new peak
                string_my_player_new_mmr = str(my_player_new_mmr).center(9)
                # print(f'current peak: {my_player_peak} | new mmr value: {my_player_new_mmr}')
                if my_player_peak < my_player_new_mmr:
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
                        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
                        # Remove player from lineups
                        db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], ctx.channel.id)) # YOU MUST SUBMIT TABLE IN THE TIER THE MATCH WAS PLAYED
                        # Clear sub leaver table
                        db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
                except Exception as e:
                    # print(e)
                    await send_to_debug_channel(ctx, f'FATAL TABLE ERROR: {e}')
                    pass
                
                # Remove mogi media messages
                if mogi_media_message_id is None:
                    pass
                else:
                    channel = client.get_channel(mogi_media_channel_id)
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
                            guild = client.get_guild(Lounge[0])
                            current_role = guild.get_role(my_player_rank_id)
                            new_role = guild.get_role(rank_id)
                            member = await guild.fetch_member(player[0])
                            await member.remove_roles(current_role)
                            await member.add_roles(new_role)
                            await results_channel.send(f'<@{player[0]}> has been promoted to {new_role}')
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                            my_player_new_rank += f'+ {new_role}'
                        # Rank down - assign roles - update DB
                        elif my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr:
                            guild = client.get_guild(Lounge[0])
                            current_role = guild.get_role(my_player_rank_id)
                            new_role = guild.get_role(rank_id)
                            member = await guild.fetch_member(player[0])
                            await member.remove_roles(current_role)
                            await member.add_roles(new_role)
                            await results_channel.send(f'<@{player[0]}> has been demoted to {new_role}')
                            with DBA.DBAccess() as db:
                                db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
                            my_player_new_rank += f'- {new_role}'
                    except Exception as e:
                        # print(e)
                        pass
                        # my_player_rank_id = role_id
                        # guild.get_role(role_id)
                        # guild.get_member(discord_id)
                        # member.add_roles(discord.Role)
                        # member.remove_roles(discord.Role)
                string_my_player_new_rank = f'{str(my_player_new_rank).center(12)}'
                formatted_my_player_new_rank = await new_rank_wrapper(string_my_player_new_rank, my_player_new_mmr)
                mmr_table_string += f'{formatted_my_player_new_rank}'
                string_my_player_place = ''

        # Create imagemagick image
        # https://imagemagick.org/script/color.php
        pango_string = f'pango:<tt>{mmr_table_string}</tt>'
        mmr_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}mmr.jpg'
        # correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
        correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
        # '+swap', '-compose', 'Over', '-composite', '-quality', '100',
        # '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',
        f=discord.File(mmr_filename, filename='mmr.jpg')
        sf=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png', filename='table.jpg')

        # Create embed
        embed2 = discord.Embed(title=f'Tier {tier_name.upper()} Results', color = discord.Color.blurple())
        embed2.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
        embed2.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
        embed2.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
        embed2.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
        embed2.set_image(url='attachment://table.jpg')
        table_message = await results_channel.send(content=None, embed=embed2, file=sf)
        table_url = table_message.embeds[0].image.url
        try:
            with DBA.DBAccess() as db:
                db.query('UPDATE mogi SET table_url = %s WHERE mogi_id = %s;', (table_url, db_mogi_id))
        except Exception as e:
            await send_to_debug_channel(ctx, f'Unable to get table url: {e}')
            pass

        embed = discord.Embed(title=f'Tier {tier_name.upper()} MMR', color = discord.Color.blurple())
        embed.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
        embed.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
        embed.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
        embed.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
        embed.set_image(url='attachment://mmr.jpg')
        await results_channel.send(content=None, embed=embed, file=f)
        #  discord ansi coloring (doesn't work on mobile)
        # https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
        # https://rebane2001.com/discord-colored-text-generator/ 
        await ctx.respond('`Table Accepted.`', delete_after=300)
    else:
        await ctx.respond('`Table Denied.`', delete_after=300)

# /stats
@client.slash_command(
    name='stats',
    description='Player statistics',
    #guild_ids=Lounge
)
async def stats(
    ctx,
    tier: discord.Option(discord.TextChannel, description='Which tier?', required=False),
    player: discord.Option(discord.Member, description='Which player?', required=False),
    last: discord.Option(int, description='How many mogis?', required=False)
    ):
    if last is None:
        number_of_mogis = 999999
    else:
        number_of_mogis = last
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    mmr_history = [] #
    score_history = [] #
    last_10_wins = 0 #
    last_10_losses = 0 #
    last_10_change = 0 #
    average_score = 0
    partner_average = 0
    top_score = 0 #
    events_played = 0 #
    largest_gain = 0 #
    largest_loss = 0 #
    rank = 0
    count_of_wins = 0
    if player is None:
        my_player_id = ctx.author.id
    else:
        my_player_id = player.id
    # Create matplotlib MMR history graph
    try: # Checks for valid player
        with DBA.DBAccess() as db:
            temp = db.query('SELECT base_mmr, peak_mmr, mmr, player_name FROM player WHERE player_id = %s;', (my_player_id,))
            if temp[0][0] is None:
                base = 0
            else:
                base = temp[0][0]
            peak = temp[0][1]
            mmr = temp[0][2]
            player_name = temp[0][3]
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(*) FROM player WHERE mmr >= %s ORDER BY mmr DESC;', (mmr,))
            rank = temp[0][0]
    except Exception as e:
        await send_to_debug_channel(ctx, f'/stats error 31 | {e}')
        await ctx.respond('``Error 31:`` Player not found.')
        return
    if tier is None:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr_change, score FROM player_mogi pm JOIN mogi m ON pm.mogi_id = m.mogi_id WHERE player_id = %s ORDER BY m.create_date ASC LIMIT %s;', (my_player_id, number_of_mogis))
            try:
                did_u_play_yet = temp[0][0]
            except Exception:
                await ctx.respond('You must play at least 1 match to use `/stats`')
                return
            for i in range(len(temp)):
                mmr_history.append(temp[i][0])
                score_history.append(temp[i][1])
                if i <= 9:
                    last_10_change += mmr_history[i]
                    if mmr_history[i] > 0:
                        last_10_wins += 1
                    else:
                        last_10_losses += 1
        partner_average = await get_partner_avg(my_player_id)
    elif tier.id in TIER_ID_LIST:
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT pm.mmr_change, pm.score FROM player_mogi pm JOIN mogi m ON pm.mogi_id = m.mogi_id WHERE pm.player_id = %s AND m.tier_id = %s ORDER BY m.create_date ASC LIMIT %s;', (my_player_id, tier.id, number_of_mogis))
                for i in range(len(temp)):
                    mmr_history.append(temp[i][0])
                    score_history.append(temp[i][1])
                    if i <= 9:
                        last_10_change += mmr_history[i]
                        if mmr_history[i] > 0:
                            last_10_wins += 1
                        else:
                            last_10_losses += 1
        except Exception as e:
            await send_to_debug_channel(ctx, f'/stats not played in tier | {e}')
            await ctx.respond(f'You have not played in {tier.mention}')
            return
        partner_average = await get_partner_avg(my_player_id, tier.id)
    else:
        await ctx.respond(f'``Error 30:`` {tier.mention} is not a valid tier')
        return

    events_played = len(mmr_history)
    try:
        top_score = max(score_history)
    except Exception as e:
        await ctx.respond(f'You have not played in {tier.mention}')
        return

    try:
        largest_gain = max(mmr_history)
    except Exception:
        largest_gain = 0

    largest_loss = min(mmr_history)
    average_score = sum(score_history)/len(score_history)
    temp_for_average_mmr = base # 3750
    running_sum = base
    for match in mmr_history:
        temp_for_average_mmr += match # x = 3750 + 300 
        running_sum += temp_for_average_mmr
        if match > 0:
            count_of_wins += 1
    average_mmr = running_sum/(len(mmr_history)+1)
    win_rate = count_of_wins/len(mmr_history)*100

    file = plotting.create_plot(base, mmr_history)
    f=discord.File(file, filename='stats.png')

    title='Stats'
    if tier is None:
        pass
    else:
        title+=f' | {tier.name}'
    if last is None:
        pass
    else:
        title+=f' | Last {last}'

    # channel = client.get_channel(ctx.channel.id)
    red, green, blue = 129, 120, 118
    if mmr >= 1500:
        red, green, blue = 230, 126, 34
    if mmr >= 3000:
        red, green, blue = 125, 131, 150
    if mmr >= 4500:
        red, green, blue = 241, 196, 15
    if mmr >= 6000:
        red, green, blue = 0, 162, 184
    if mmr >= 7500:
        red, green, blue = 185, 242, 255
    if mmr >= 9000:
        red, green, blue = 0, 0, 0
    if mmr >= 11000:
        red, green, blue = 163, 2, 44

    rank_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/rank.png'
    stats_rank_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/stats_rank.png'

    correct = subprocess.run(['convert', f'{rank_filename}'], '-fill', f'"rgb({red},{green},{blue})"', '-tint', '100', f'{stats_rank_filename}')
    f=discord.File(rank_filename, filename='rank.jpg')
    sf=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/stats_rank.png', filename='stats_rank.jpg')
    embed.set_thumbnail(url='attachment://stats_rank.jpg')


    embed = discord.Embed(title=f'{title}', description=f'{player_name}', color = discord.Color.from_rgb(red, green, blue)) # website link
    embed.add_field(name='Rank', value=f'{rank}', inline=True)
    embed.add_field(name='MMR', value=f'{mmr}', inline=True)
    embed.add_field(name='Peak MMR', value=f'{peak}', inline=True)
    embed.add_field(name='Win Rate', value=f'{round(win_rate,0)}%', inline=True)
    embed.add_field(name='W-L (Last 10)', value=f'{last_10_wins} - {last_10_losses}', inline=True)
    embed.add_field(name='+/- (Last 10)', value=f'{last_10_change}', inline=True)
    embed.add_field(name='Avg. Score', value=f'{round(average_score, 2)}', inline=True)
    embed.add_field(name='Top Score', value=f'{top_score}', inline=True) # website link
    embed.add_field(name='Partner Avg.', value=f'{partner_average}', inline=True)
    embed.add_field(name='Events Played', value=f'{events_played}', inline=True)
    embed.add_field(name='Largest Gain', value=f'{largest_gain}', inline=True)
    embed.add_field(name='Largest Loss', value=f'{largest_loss}', inline=True)
    embed.add_field(name='Average MMR', value=f'{round(average_mmr,0)}', inline=True)
    embed.add_field(name='Base MMR', value=f'{base}', inline=True)
    embed.set_image(url='attachment://stats.png')
    # await channel.send(file=f, embed=embed)
    await ctx.respond(file=f, embed=embed)
    return

# /mmr
@client.slash_command(
    name='mmr',
    description='Your mmr',
    # guild_ids=Lounge
)
async def mmr(ctx):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    with DBA.DBAccess() as db:
        temp = db.query('SELECT p.mmr, r.rank_name FROM player as p JOIN ranks as r ON p.rank_id = r.rank_id WHERE p.player_id = %s;', (ctx.author.id,))
        mmr = temp[0][0]
        rank_name = temp[0][1]
    if temp:
        pass
    else:
        await ctx.respond('``Error 43:`` Player not found')
        return
    if mmr is None:
        mmr = "n/a"
    await ctx.respond(f'`MMR:` {mmr} | `Rank:` {rank_name}. If this looks wrong, try the `/verify` command.')
    return

# /twitch
@client.slash_command(
    name='twitch',
    description='Link your Twitch stream',
    #guild_ids=Lounge
)
async def twitch(
    ctx,
    username: discord.Option(str, 'Enter your twitch username - your mogi streams will appear in the media channel', required=True)
    ):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    x = await check_if_player_exists(ctx)
    if x:
        pass
    else:
        await ctx.respond('Use `/verify` to register with Lounge')
        return
    y = await check_if_banned_characters(username)
    if y:
        await ctx.respond("Invalid twitch username")
        await send_to_verification_log(ctx, username, discord.Color.blurple(), vlog_msg.error1)
        return
    if len(str(username)) > 25:
        await ctx.respond("Invalid twitch username")
        return
    try:
        with DBA.DBAccess() as db:
            db.execute("UPDATE player SET twitch_link = %s WHERE player_id = %s;", (str(username), ctx.author.id))
            await ctx.respond("Twitch username updated.")
    except Exception:
        await ctx.respond("``Error 33:`` Player not found. Use ``/verify <mkc link>`` to register with Lounge")

# /strikes
@client.slash_command(
    name='strikes',
    description='See your strikes',
    #guild_ids=Lounge
)
async def strikes(ctx):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    x = await check_if_uid_exists(ctx.author.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found. Use `/verify <mkc link>` to register with Lounge')
        return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;', (ctx.author.id, 1))
            if temp[0][0]:
                response = ''
                for i in range(len(temp)):
                    response += f'`Strike {i+1}` Expires: <t:{str(int(temp[i][0]))}:F>\n'
                await ctx.respond(response)
                return
            else:
                pass
    except Exception:
        pass
    await ctx.respond('You have no strikes')
    return

# /teams
@client.slash_command(
    name='teams',
    description='See the teams in the ongoing mogi',
    #guild_ids=Lounge
)
async def teams(ctx):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    x = await check_if_mogi_is_ongoing(ctx)
    if x:
        pass
    else:
        await ctx.respond('There is no ongoing mogi')
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
            if temp:
                response = temp[0][0]
            else:
                response = "Use `/teams` in a tier channel"
    except Exception as e:
        response = "Use `/teams` in a tier channel"
    await ctx.respond(response)

# /zstrikes
@client.slash_command(
    name='zstrikes',
    description='See your strikes',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zstrikes(ctx,
    player: discord.Option(discord.Member, description='Which player?', required=False)
    ):
    await ctx.defer()
    if player is None:
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
        x = await check_if_uid_exists(ctx.author.id)
        if x:
            pass
        else:
            await ctx.respond('Player not found. Use `/verify <mkc link>` to register with Lounge')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;', (ctx.author.id, 1))
                if temp[0][0]:
                    response = ''
                    for i in range(len(temp)):
                        response += f'`Strike {i+1}` Expires: <t:{str(int(temp[i][0]))}:F>\n'
                    await ctx.respond(response)
                    return
                else:
                    pass
        except Exception:
            pass
        await ctx.respond('You have no strikes')
        return
    else:
        lounge_ban = await check_if_uid_is_lounge_banned(player.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
            return
        else:
            pass
        x = await check_if_uid_exists(player.id)
        if x:
            pass
        else:
            await ctx.respond('Player not found.')
            return
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;', (player.id, 1))
                if temp[0][0]:
                    response = ''
                    for i in range(len(temp)):
                        response += f'`Strike {i+1}` Expires: <t:{str(int(temp[i][0]))}:F>\n'
                    await ctx.respond(response)
                    return
                else:
                    pass
        except Exception:
            pass
        await ctx.respond('This player has no strikes')
        return

# /zcancel_mogi
@client.slash_command(
    name='zcancel_mogi',
    description='Cancel an ongoing mogi [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zcancel_mogi(ctx):
    await ctx.defer()
    # Check for ongoing mogi in current channel
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
        if len(temp) == 12:
            pass
        else:
            await ctx.respond('There is no mogi being played in this tier.')
            return
    except Exception as e:
        await send_to_debug_channel(ctx, f'Cancel Error Check: {e}')
        return
    # Delete from lineups & sub_leaver
    try:
        with DBA.DBAccess() as db:
            db.execute('DELETE FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
            db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
        await ctx.respond('The mogi has been cancelled')
    except Exception as e:
        await send_to_debug_channel(ctx, f'Cancel Error Deletion:{e}')
        return

# /zrevert
@client.slash_command(
    name="zrevert",
    description="Undo a table [Admin only]",
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zrevert(
    ctx,
    mogi_id: discord.Option(int, 'Mogi ID / Table ID', required=True)
    ):
    await ctx.defer()
    flag = 0
    # Make sure mogi exists
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mogi_id FROM mogi WHERE mogi_id = %s;', (mogi_id,))
            if temp[0][0] is None:
                await ctx.respond('``Error 34:`` Mogi could not be found.')
                return
    except Exception as e:
        await send_to_debug_channel(ctx, f'zrevert error 35 wrong mogi id? | {e}')
        await ctx.respond('``Error 35:`` Mogi could not be found')
        return

    # Check for rank changes
    with DBA.DBAccess() as db:
        players_mogi = db.query('select p.player_id, p.player_name, p.mmr, pm.mmr_change, p.rank_id, t.results_id FROM player p JOIN player_mogi pm ON p.player_id = pm.player_id JOIN mogi m on pm.mogi_id = m.mogi_id JOIN tier t on t.tier_id = m.tier_id WHERE m.mogi_id = %s', (mogi_id,))
    with DBA.DBAccess() as db:
        db_ranks_table = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s ORDER BY mmr_min DESC LIMIT 8;', (1,))
    for j in range(len(db_ranks_table)):
        for i in range(len(players_mogi)):
            rank_id = db_ranks_table[j][0]
            min_mmr = db_ranks_table[j][1]
            max_mmr = db_ranks_table[j][2]
            my_player_id = players_mogi[i][0]
            my_player_name = players_mogi[i][1]
            my_player_mmr = int(players_mogi[i][2])
            my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3])* -1)
            my_player_rank_id = players_mogi[i][4]
            results_channel_id = players_mogi[i][5]
            results_channel = client.get_channel(results_channel_id)
            # Rank back up
            #print(f'{min_mmr} - {max_mmr} | {my_player_name} {my_player_mmr} + {players_mogi[i][3] * -1} = {my_player_new_mmr}')
            try:
                if my_player_mmr < min_mmr and my_player_new_mmr >= min_mmr and my_player_new_mmr < max_mmr:
                    guild = client.get_guild(Lounge[0])
                    current_role = guild.get_role(my_player_rank_id)
                    new_role = guild.get_role(rank_id)
                    member = await guild.fetch_member(my_player_id)
                    await member.remove_roles(current_role)
                    await member.add_roles(new_role)
                    await results_channel.send(f'<@{my_player_id}> has been promoted to {new_role}')
                    with DBA.DBAccess() as db:
                        db.execute('UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;', (rank_id, my_player_new_mmr, my_player_id))
                # Rank back down
                elif my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr and my_player_new_mmr > min_mmr:
                    guild = client.get_guild(Lounge[0])
                    current_role = guild.get_role(my_player_rank_id)
                    new_role = guild.get_role(rank_id)
                    member = await guild.fetch_member(my_player_id)
                    await member.remove_roles(current_role)
                    await member.add_roles(new_role)
                    await results_channel.send(f'<@{my_player_id}> has been demoted to {new_role}')
                    with DBA.DBAccess() as db:
                        db.execute('UPDATE player SET rank_id = %s, mmr = %s WHERE player_id = %s;', (rank_id, my_player_new_mmr, my_player_id))
            except Exception as e:
                await send_to_debug_channel(ctx, f'/zrevert FATAL ERROR | {e}')
                flag = 1
                pass
    with DBA.DBAccess() as db:
        db.execute('DELETE FROM player_mogi WHERE mogi_id = %s;', (mogi_id,))
        db.execute('DELETE FROM mogi WHERE mogi_id = %s;', (mogi_id,))
    if flag == 1:
        fatal_error = f"FATAL ERROR WHILE UPDATING ROLES. CONTACT {secretly.my_discord}"
    else:
        fatal_error = ""
    await ctx.respond(f'Mogi ID `{mogi_id}` has been removed. {fatal_error}')
    return

# /zswapscore
@client.slash_command(
    name="zswapscore",
    description="Swap the score of two players on the same team [Admin only]",
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zswapscore(
    ctx,
    player1: discord.Option(str, "Player name", required=True),
    player2: discord.Option(str, "Player name", required=True),
    mogi_id: discord.Option(int, "Mogi ID", required = True)
    ):
    await ctx.defer()
    x = await check_if_banned_characters(player1)
    if x:
        await ctx.respond("Invalid player1 name")
        await send_to_verification_log(ctx, player1, discord.Color.blurple(), vlog_msg.error1)
        return
    else:
        pass
    y = await check_if_banned_characters(player2)
    if y:
        await ctx.respond("Invalid player2 name")
        await send_to_verification_log(ctx, player1, discord.Color.blurple(), vlog_msg.error1)
        return
    else:
        pass
    id1=0
    id2=0
    idmogi=0
    try:
        with DBA.DBAccess() as db:
            temp1 = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player1,))
            temp2 = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player2,))
            temp3 = db.query('SELECT mogi_id FROM mogi WHERE mogi_id = %s;', (mogi_id,))
            id1 = temp1[0][0]
            id2 = temp2[0][0]
            idmogi = temp3[0][0]
    except Exception as e:
        await send_to_debug_channel(ctx, f'error 35 {e}')
        await ctx.respond('``Error 35:`` One of your inputs is invalid. Please try again')
    try:
        with DBA.DBAccess() as db:
            temp1 = db.query('SELECT score FROM player_mogi WHERE player_id = %s AND mogi_id = %s;', (id1, idmogi))
            id1_score = temp1[0][0]
            temp2 = db.query('SELECT score FROM player_mogi WHERE player_id = %s AND mogi_id = %s;', (id2, idmogi))
            id2_score = temp2[0][0]
            db.execute('UPDATE player_mogi SET score = %s WHERE player_id = %s AND mogi_id = %s', (id1_score, id2, idmogi))
            db.execute('UPDATE player_mogi SET score = %s WHERE player_id = %s AND mogi_id = %s', (id2_score, id1, idmogi))
    except Exception as e:
        await send_to_debug_channel(ctx, f'error 36 {e}')
        await ctx.respond('``Error 36:`` Oops! Something went wrong.')
    await ctx.respond(f'Scores swapped successfully.\n{player1} {id1_score} -> {id2_score}\n{player2} {id2_score} -> {id1_score}')
    return

# /zstrike
@client.slash_command(
    name='zstrike',
    description='Add strike & -mmr penalty to a player [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zstrike(
    ctx,
    player: discord.Option(discord.Member, description='Which player?', required=True),
    mmr_penalty: discord.Option(int, description='How much penalty to apply?', required=True),
    reason: discord.Option(str, description='Why?', required=True)
    ):
    await ctx.defer()
    if len(reason) > 32:
        await ctx.respond('Reason too long (32 character limit)')
        return
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
        return
    y = await check_if_banned_characters(reason)
    if y:
        await ctx.respond('Invalid reason')
        return
    else:
        pass
    # Send info to strikes table
    mmr_penalty = abs(mmr_penalty)
    # Update player MMR
    current_time = datetime.datetime.now()
    expiration_date = current_time + datetime.timedelta(days=30)
    mmr = 0
    num_of_strikes = 0
    with DBA.DBAccess() as db:
        temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player.id,))
        if temp[0][0] is None:
            mmr = mmr_penalty
        else:
            mmr = temp[0][0]
    with DBA.DBAccess() as db:
        db.execute('INSERT INTO strike (player_id, reason, mmr_penalty, expiration_date) VALUES (%s, %s, %s, %s);', (player.id, reason, mmr_penalty, expiration_date))
        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', ((mmr-mmr_penalty), player.id))
    with DBA.DBAccess() as db:
        temp = db.query('SELECT COUNT(*) FROM strike WHERE player_id = %s AND is_active = %s;', (player.id, 1))
        if temp[0][0] is None:
            num_of_strikes = 0
        else:
            num_of_strikes = temp[0][0]
    if num_of_strikes >= 3:
        times_strike_limit_reached = 0
        with DBA.DBAccess() as db:
            temp = db.query('SELECT times_strike_limit_reached FROM player WHERE player_id = %s;', (player.id,))
            times_strike_limit_reached = temp[0][0] + 1
            db.execute('UPDATE player SET times_strike_limit_reached = %s WHERE player_id = %s;', (temp[0][0], player.id))
        user = await GUILD.fetch_member(player.id)
        await user.add_roles(LOUNGELESS_ROLE)
        channel = client.get_channel(secretly.strikes_channel)
        await channel.send(f'{player.mention} has reached 3 strikes. Loungeless role applied\n`# of offenses:` {times_strike_limit_reached}')
    await ctx.respond(f'Strike applied to {player.mention} | Penalty: {mmr_penalty}')
     
# /zhostban
@client.slash_command(
    name='zhostban',
    description='Add hostban to a player [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zhostban(
    ctx,
    player: discord.Option(discord.Member, description='Which player?', required=True)
    ):
    await ctx.defer()
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
        return
    with DBA.DBAccess() as db:
        temp = db.query('SELECT is_host_banned FROM player WHERE player_id = %s;', (player.id,))
    if temp[0][0]:
        with DBA.DBAccess() as db:
            db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (0, player.id))
            await ctx.respond(f'{player.mention} has been un-host-banned')
    else:
        with DBA.DBAccess() as db:
            db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (1, player.id))
            await ctx.respond(f'{player.mention} has been host-banned')

# /zrestrict
@client.slash_command(
    name='zrestrict',
    description='Chat restrict a player [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zrestrict(
    ctx,
    player: discord.Option(discord.Member, description='Which player?', required=True)
    ):
    await ctx.defer()
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
        return
    user = await GUILD.fetch_member(player.id)
    if CHAT_RESTRICTED_ROLE in user.roles:
        await user.remove_roles(CHAT_RESTRICTED_ROLE)
        await ctx.respond(f'{player.mention} has been unrestricted')
    else:
        await user.add_roles(CHAT_RESTRICTED_ROLE)
        await ctx.respond(f'{player.mention} has been restricted')

# /zloungeless
@client.slash_command(
    name='zloungeless',
    description='Apply the loungeless role [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zloungeless(
    ctx, 
    player: discord.Option(discord.Member, description='Which player?', required=True)
    ):
    await ctx.defer()
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
    user = await GUILD.fetch_member(player.id)
    if LOUNGELESS_ROLE in user.roles:
        await user.remove_roles(LOUNGELESS_ROLE)
        await ctx.respond(f'Loungeless removed from {player.mention}')
    else:
        await user.add_roles(LOUNGELESS_ROLE)
        await ctx.respond(f'Loungeless added to {player.mention}')

# /zmmr_penalty
@client.slash_command(
    name='zmmr_penalty',
    description='Give a player an MMR penalty, with no strike [Admin only]',
    #guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zmmr_penalty(
    ctx,
    player: discord.Option(discord.Member, description='Which player?', required=True),
    mmr_penalty: discord.Option(int, description='How much penalty to apply?', required=True)):
    await ctx.defer()
    mmr_penalty = abs(mmr_penalty)
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
        return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player.id,))
            new_mmr = temp[0][0] - mmr_penalty
            if new_mmr < 0:
                new_mmr = 1
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (new_mmr, player.id))
        await ctx.respond(f'{player.mention} has been given a {mmr_penalty} mmr penalty')
    except Exception as e:
        await send_to_debug_channel(ctx, f'/zmmr_penalty error 38 {e}')
        await ctx.respond('`Error 38:` Could not apply penalty')

# /zsendmsg
@client.slash_command(
    name='zsendmsg',
    description='bot send message here',
    #guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID)
async def zsendmsg(ctx):
    await ctx.defer()
    channel = client.get_channel(ctx.channel.id)
    await channel.send('a')
    await ctx.respond('message sent')

# /zreduce_loss
@client.slash_command(
    name='zreduce_loss',
    description='Reduce the loss for 1 player in 1 mogi',
    # guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zreduce_loss(ctx,
    player: discord.Option(discord.Member, description='Which player?', required=True),
    mogi_id: discord.Option(int, description='Which mogi?', required=True),
    reduction: discord.Option(str, description='Reduction value', required=True)):
    await ctx.defer()
    x = await check_if_uid_exists(player.id)
    if x:
        pass
    else:
        await ctx.respond('Player not found')
        return
    y = await check_if_mogi_exists(mogi_id)
    if y:
        pass
    else:
        await ctx.respond('Mogi ID not found')
        return
    z = await check_if_banned_characters(reduction)
    if z:
        await ctx.respond("Bad input")
        return
    else:
        pass
    # Get the mmr change
    reduce = str(reduction).split("/")
    multiplier = int(reduce[0])/int(reduce[1])
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr_change FROM player_mogi WHERE player_id = %s AND mogi_id = %s;', (player.id, mogi_id))
            temp2 = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player.id,))
            mmr_change = temp[0][0]
            mmr = temp2[0][0]
    except Exception:
        await ctx.respond('``Error 40:`` tell popuko or try again later')
        return
    reverse_mmr_change = mmr_change * -1
    reverted_player_mmr = mmr + reverse_mmr_change
    adjusted_mmr_change = int(math.floor(mmr_change * multiplier))
    adjusted_mmr = int(math.floor(reverted_player_mmr + adjusted_mmr_change))
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE player_mogi SET mmr_change = %s WHERE player_id = %s AND mogi_id = %s;', (adjusted_mmr_change, player.id, mogi_id))
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (adjusted_mmr, player.id))
    except Exception as e:
        await send_to_debug_channel(ctx, f'player: {player} | mogi id: {mogi_id} | reduction: {reduction} | {e}')
        await ctx.respond('``Error 41:`` FATAL ERROR uh oh uh oh uh oh')
        return
    await ctx.respond(f'Loss was reduced for {player.mention}.\nChange: `{mmr_change}` -> `{adjusted_mmr_change}`\nMMR: `{mmr}` -> `{adjusted_mmr}`')
    return

# # /ztable
# @client.slash_command(
#     name='ztable',
#     description='Submit a table [Admin only] ',
#     # guild_ids=Lounge
# )
# @commands.has_any_role(ADMIN_ROLE_ID)
# async def ztable(
#     ctx,
#     mogi_format: discord.Option(int, '1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6', required=True),
#     scores: discord.Option(str, 'player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)', required=True)
#     ):
#     await ctx.defer()
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#         return
#     else:
#         pass
#     bad = await check_if_banned_characters(str(scores))
#     if bad:
#         await send_to_verification_log(ctx, scores, discord.Color.blurple(), vlog_msg.error1)
#         await ctx.respond(f'``Error 32:`` Invalid input. There must be 12 players and 12 scores.')
#         return

#     # Create list
#     score_string = str(scores) #.translate(remove_chars)
#     score_list = score_string.split()

#     # Check for 12 players
#     if len(score_list) == 24:
#         pass
#     else:
#         await ctx.respond(f'``Error 26:`` Invalid input. There must be 12 players and 12 scores.')
#         return
    
#     # Replace playernames with playerids

#     #print(f'score list: {score_list}')
#     player_list_check = []
#     for i in range(0, len(score_list), 2):
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (score_list[i],))
#             player_list_check.append(score_list[i])
#             score_list[i] = temp[0][0]

#     # # Check for if mogi has started
#     # try:
#     #     with DBA.DBAccess() as db:
#     #         temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
#     #         players_in_lineup_count = temp[0][0]
#     # except Exception as e:
#     #     await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secretly.my_discord}. {e}')
#     #     await send_to_debug_channel(ctx, e)
#     #     return
#     # if players_in_lineup_count < 12:
#     #     await ctx.respond('Mogi has not started. Cannot create a table now')
#     #     return

    
    
#     # Check for duplicate players
#     has_dupes = await check_for_dupes_in_list(player_list_check)
#     if has_dupes:
#         await ctx.respond('``Error 37:`` You cannot have duplicate players on a table')
#         return

#     # Check if all 12 players are SUPPOSED to be on the table (1st 12 players. You can't just ignore a player and put the 13th player in the mogi without using the /sub command)
#     # for player in player_list_check:
#     #     try:
#     #         with DBA.DBAccess() as db:
#     #             temp = db.query('SELECT can_drop FROM lineups WHERE player_id = %s AND tier_id = %s ORDER BY create_date ASC LIMIT 12;', (player, ctx.channel.id))
#     #         if temp == 0:
#     #             pass
#     #         else:
#     #             await ctx.respond(f'``Error 52:`` Unexpected player in lineup. Is there a sub among us? Please use the `/sub` command.\n\nCreate a ticket or contact {secretly.my_discord} if you think this is a mistake.')
#     #             return
#     #     except Exception as e:
#     #         await ctx.respond(f'``Error 53:`` Oops! Something went wrong. | Unexpected player in lineup. Is there a sub among us? Please use the `/sub` command.\n\nCreate a ticket or contact {secretly.my_discord} if you think this is a mistake.')
#     #         await send_to_debug_channel(ctx, f'/table Error 53: {e}')
#     #         return

#     # Check the mogi_format
#     if mogi_format == 1:
#         SPECIAL_TEAMS_INTEGER = 63
#         OTHER_SPECIAL_INT = 19
#         MULTIPLIER_SPECIAL = 2.1
#         table_color = ['#76D7C4', '#A3E4D7']
#     elif mogi_format == 2:
#         SPECIAL_TEAMS_INTEGER = 142
#         OTHER_SPECIAL_INT = 39
#         MULTIPLIER_SPECIAL = 3.0000001
#         table_color = ['#76D7C4', '#A3E4D7']
#     elif mogi_format == 3:
#         SPECIAL_TEAMS_INTEGER = 288
#         OTHER_SPECIAL_INT = 59
#         MULTIPLIER_SPECIAL = 3.1
#         table_color = ['#85C1E9', '#AED6F1']
#     elif mogi_format == 4:
#         SPECIAL_TEAMS_INTEGER = 402
#         OTHER_SPECIAL_INT = 79
#         MULTIPLIER_SPECIAL = 3.35
#         table_color = ['#C39BD3', '#D2B4DE']
#     elif mogi_format == 6:
#         SPECIAL_TEAMS_INTEGER = 525
#         OTHER_SPECIAL_INT = 99
#         MULTIPLIER_SPECIAL = 3.5
#         table_color = ['#F1948A', '#F5B7B1']
#     else:
#         await ctx.respond(f'``Error 27:`` Invalid format: {mogi_format}. Please use 1, 2, 3, 4, or 6.')
#         return

#     # Initialize a list so we can group players and scores together
#     player_score_chunked_list = list()
#     for i in range(0, len(score_list), 2):
#         player_score_chunked_list.append(score_list[i:i+2])
#     # print(f'player score chunked list: {player_score_chunked_list}')

#     # Chunk the list into groups of teams, based on mogi_format and order of scores entry
#     chunked_list = list()
#     for i in range(0, len(player_score_chunked_list), mogi_format):
#         chunked_list.append(player_score_chunked_list[i:i+mogi_format])
    
#     # Get MMR data for each team, calculate team score, and determine team placement
#     mogi_score = 0
#     # print(f'length of chunked list: {len(chunked_list)}')
#     # print(f'chunked list: {chunked_list}')
#     for team in chunked_list:
#         temp_mmr = 0
#         team_score = 0
#         count = 0
#         for player in team:
#             try:
#                 with DBA.DBAccess() as db:
#                     # YOU CAN CHOOSE ANY PLAYER BE CAREFUL!!!!!!!!!
#                     temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player[0],))
#                     if temp[0][0] is None:
#                         mmr = 0
#                     else:
#                         mmr = temp[0][0]
#                         count+=1
#                     temp_mmr += mmr
#                     try:
#                         team_score += int(player[1])
#                     except Exception:
#                         score_and_pen = str(player[1]).split('-')
#                         team_score = team_score + int(score_and_pen[0]) - int(score_and_pen[1])
#             except Exception as e:
#                 # check for all 12 players exist
#                 await send_to_debug_channel(ctx, f'/ztable error 24 why are you using this command. dont use this command!!! >:( {e}')
#                 await ctx.respond(f'``Error 24:`` There was an error with the following player: <@{player[0]}>. If this is a sub, you must first use the `/sub` command')
#                 return
#         # print(team_score)
#         if count == 0:
#             count = 1
#         team_mmr = temp_mmr/count
#         team.append(team_score)
#         team.append(team_mmr)
#         mogi_score += team_score
#     # Check for 984 score
#     if mogi_score == 984:
#         pass
#     else:
#         await ctx.respond(f'``Error 28:`` `Scores = {mogi_score} `Scores must add up to 984.')
#         return

#     # Sort the teams in order of score
#     # [[players players players], team_score, team_mmr]
#     sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-2]))
#     sorted_list.reverse() 

#     # Create hlorenzi string
#     if mogi_format == 1:
#         lorenzi_query='-\n'
#     else:
#         lorenzi_query=''

#     # Initialize score and placement values
#     prev_team_score = 0
#     prev_team_placement = 1
#     team_placement = 0
#     count_teams = 1
#     for team in sorted_list:
#         # If team score = prev team score, use prev team placement, else increase placement and use placement
#         if team[len(team)-2] == prev_team_score:
#             team_placement = prev_team_placement
#         else:
#             team_placement = count_teams
#         count_teams += 1
#         team.append(team_placement)
#         if mogi_format != 1:
#             if count_teams % 2 == 0:
#                 lorenzi_query += f'{team_placement} {table_color[0]} \n'
#             else:
#                 lorenzi_query += f'{team_placement} {table_color[1]} \n'
#         for idx, player in enumerate(team):
#             if idx > (mogi_format-1):
#                 continue
#             with DBA.DBAccess() as db:
#                 temp = db.query('SELECT player_name, country_code FROM player WHERE player_id = %s;', (player[0],))
#                 player_name = temp[0][0]
#                 country_code = temp[0][1]
#                 score = player[1]
#             lorenzi_query += f'{player_name} [{country_code}] {score}\n'

#         # Assign previous values before looping
#         prev_team_placement = team_placement
#         prev_team_score = team[len(team)-3]

#     # Request a lorenzi table
#     query_string = urllib.parse.quote(lorenzi_query)
#     url = f'https://gb.hlorenzi.com/table.png?data={query_string}'
#     response = requests.get(url, stream=True)
#     with open(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png', 'wb') as out_file:
#         shutil.copyfileobj(response.raw, out_file)
#     del response

#     # Ask for table confirmation
#     table_view = Confirm(ctx.author.id)
#     channel = client.get_channel(ctx.channel.id)
#     await channel.send(file=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png'), delete_after=300)
#     await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)
#     await table_view.wait()
#     if table_view.value is None:
#         await ctx.respond('No response from reporter. Timed out')
#     elif table_view.value: # yes
#         db_mogi_id = 0
#         # Create mogi
#         with DBA.DBAccess() as db:
#             db.execute('INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);', (mogi_format, ctx.channel.id))

#         # Get the results channel and tier name for later use
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT results_id, tier_name FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
#             db_results_channel = temp[0][0]
#             tier_name = temp[0][1]
#         results_channel = client.get_channel(db_results_channel)

#         # Pre MMR table calculate
#         value_table = list()
#         for idx, team_x in enumerate(sorted_list):
#             working_list = list()
#             for idy, team_y in enumerate(sorted_list):
#                 pre_mmr = 0.0
#                 if idx == idy: # skip value vs. self
#                     pass
#                 else:
#                     team_x_mmr = team_x[len(team_x)-2]
#                     team_x_placement = team_x[len(team_x)-1]
#                     team_y_mmr = team_y[len(team_y)-2]
#                     team_y_placement = team_y[len(team_y)-1]
#                     if team_x_placement == team_y_placement:
#                         pre_mmr = (SPECIAL_TEAMS_INTEGER*((((team_x_mmr - team_y_mmr)/9998)**2)**(1/3))**2)
#                         if team_x_mmr >= team_y_mmr:
#                             pass
#                         else: #team_x_mmr < team_y_mmr:
#                             pre_mmr = pre_mmr * -1
#                     else:
#                         if team_x_placement > team_y_placement:
#                             pre_mmr = (1 + OTHER_SPECIAL_INT*(1 + (team_x_mmr-team_y_mmr)/9998)**MULTIPLIER_SPECIAL)
#                         else: #team_x_placement < team_y_placement
#                             pre_mmr = -(1 + OTHER_SPECIAL_INT*(1 + (team_y_mmr-team_x_mmr)/9998)**MULTIPLIER_SPECIAL)
#                 working_list.append(pre_mmr)
#             value_table.append(working_list)

#         # # DEBUG
#         # print(f'\nprinting value table:\n')
#         # for _list in value_table:
#         #     print(_list)

#         # Actually calculate the MMR
#         for idx, team in enumerate(sorted_list):
#             temp_value = 0.0
#             for pre_mmr_list in value_table:
#                 for idx2, value in enumerate(pre_mmr_list):
#                     if idx == idx2:
#                         temp_value += value
#                     else:
#                         pass
#             team.append(math.floor(temp_value))

#         # Create mmr table string
#         if mogi_format == 1:
#             string_mogi_format = 'FFA'
#         else:
#             string_mogi_format = f'{str(mogi_format)}v{str(mogi_format)}'

#         mmr_table_string = f'<big><big>{ctx.channel.name} {string_mogi_format}</big></big>\n'
#         mmr_table_string += f'PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n'

#         for team in sorted_list:
#             my_player_place = team[len(team)-2]
#             string_my_player_place = str(my_player_place)
#             for idx, player in enumerate(team):
#                 mmr_table_string += '\n'
#                 if idx > (mogi_format-1):
#                     break
#                 with DBA.DBAccess() as db:
#                     temp = db.query('SELECT p.player_name, p.mmr, p.peak_mmr, p.rank_id, l.is_sub, p.mogi_media_message_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE p.player_id = %s;', (player[0],))
#                     my_player_name = temp[0][0]
#                     my_player_mmr = temp[0][1]
#                     my_player_peak = temp[0][2]
#                     my_player_rank_id = temp[0][3]
#                     is_sub = temp[0][4]
#                     mogi_media_message_id = temp[0][5]
#                     if my_player_peak is None:
#                         # print('its none...')
#                         my_player_peak = 0
#                 my_player_score = int(player[1])
#                 my_player_new_rank = ''

#                 # Place the placement players
#                 placement_name = ''
#                 if my_player_mmr is None:
#                     if my_player_score >=111:
#                         my_player_mmr = 5250
#                         placement_name = 'Gold'
#                     elif my_player_score >= 81:
#                         my_player_mmr = 3750
#                         placement_name = 'Silver'
#                     elif my_player_score >= 41:
#                         my_player_mmr = 2250
#                         placement_name = 'Bronze'
#                     else:
#                         my_player_mmr = 1000
#                         placement_name = 'Iron'
#                     with DBA.DBAccess() as db:
#                         temp = db.query('SELECT rank_id FROM ranks WHERE placement_mmr = %s;', (my_player_mmr,))
#                         init_rank = temp[0][0]
#                         db.execute('UPDATE player SET base_mmr = %s, rank_id = %s WHERE player_id = %s;', (my_player_mmr, init_rank, player[0]))
#                     discord_member = await GUILD.fetch_member(player[0])
#                     init_role = GUILD.get_role(init_rank)
#                     placement_role = GUILD.get_role(PLACEMENT_ROLE_ID)
#                     await discord_member.add_roles(init_role)
#                     await discord_member.remove_roles(placement_role)
#                     await results_channel.send(f'<@{player[0]}> has been placed at {placement_name} ({my_player_mmr} MMR)')

#                 if is_sub: # Subs only gain on winning team
#                     if team[len(team)-1] < 0:
#                         my_player_mmr_change = 0
#                     else:
#                         my_player_mmr_change = team[len(team)-1]
#                 else:
#                     my_player_mmr_change = team[len(team)-1]
#                 my_player_new_mmr = (my_player_mmr + my_player_mmr_change)

#                 # Start creating string for MMR table
#                 mmr_table_string += f'{string_my_player_place.center(6)}|'
#                 mmr_table_string +=f'{my_player_name.center(18)}|'
#                 mmr_table_string += f'{str(my_player_mmr).center(7)}|'

#                 # Check sign of mmr delta
#                 if my_player_mmr_change >= 0:
#                     temp_string = f'+{str(my_player_mmr_change)}'
#                     string_my_player_mmr_change = f'{temp_string.center(7)}'
#                     formatted_my_player_mmr_change = await pos_mmr_wrapper(string_my_player_mmr_change)
#                 else:
#                     string_my_player_mmr_change = f'{str(my_player_mmr_change).center(7)}'
#                     formatted_my_player_mmr_change = await neg_mmr_wrapper(string_my_player_mmr_change)
#                 mmr_table_string += f'{formatted_my_player_mmr_change}|'

#                 # Check for new peak
#                 string_my_player_new_mmr = str(my_player_new_mmr).center(9)
#                 # print(f'current peak: {my_player_peak} | new mmr value: {my_player_new_mmr}')
#                 if my_player_peak < my_player_new_mmr:
#                     formatted_my_player_new_mmr = await peak_mmr_wrapper(string_my_player_new_mmr)
#                     with DBA.DBAccess() as db:
#                         db.execute('UPDATE player SET peak_mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
#                 else:
#                     formatted_my_player_new_mmr = string_my_player_new_mmr
#                 mmr_table_string += f'{formatted_my_player_new_mmr}|'

#                 # Send updates to DB
#                 try:
#                     with DBA.DBAccess() as db:
#                         # Get ID of the last inserted table
#                         temp = db.query('SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;', (ctx.channel.id,))
#                         db_mogi_id = temp[0][0]
#                         # Insert reference record
#                         db.execute('INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr, is_sub) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (player[0], db_mogi_id, int(my_player_place), int(my_player_score), int(my_player_mmr), int(my_player_mmr_change), int(my_player_new_mmr), is_sub))
#                         # Update player record
#                         db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
#                         # Remove player from lineups
#                         # db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], ctx.channel.id)) # YOU MUST SUBMIT TABLE IN THE TIER THE MATCH WAS PLAYED
#                         # Clear sub leaver table
#                         db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
#                 except Exception as e:
#                     # print(e)
#                     await send_to_debug_channel(ctx, f'FATAL TABLE ERROR: {e}')
#                     pass
                
#                 # Remove mogi media messages
#                 if mogi_media_message_id is None:
#                     pass
#                 else:
#                     channel = client.get_channel(mogi_media_channel_id)
#                     message = await channel.fetch_message(mogi_media_message_id)
#                     await message.delete()

#                 with DBA.DBAccess() as db:
#                     db.execute('UPDATE player SET mogi_media_message_id = NULL WHERE player_id = %s;', (player[0],))


#                 # Check for rank changes
#                 with DBA.DBAccess() as db:
#                     db_ranks_table = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks WHERE rank_id > %s;', (1,))
#                 for i in range(len(db_ranks_table)):
#                     rank_id = db_ranks_table[i][0]
#                     min_mmr = db_ranks_table[i][1]
#                     max_mmr = db_ranks_table[i][2]
#                     # Rank up - assign roles - update DB
#                     try:
#                         if my_player_mmr < min_mmr and my_player_new_mmr >= min_mmr:
#                             guild = client.get_guild(Lounge[0])
#                             current_role = guild.get_role(my_player_rank_id)
#                             new_role = guild.get_role(rank_id)
#                             member = await guild.fetch_member(player[0])
#                             await member.remove_roles(current_role)
#                             await member.add_roles(new_role)
#                             await results_channel.send(f'<@{player[0]}> has been promoted to {new_role}')
#                             with DBA.DBAccess() as db:
#                                 db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
#                             my_player_new_rank += f'+ {new_role}'
#                         # Rank down - assign roles - update DB
#                         elif my_player_mmr > max_mmr and my_player_new_mmr <= max_mmr:
#                             guild = client.get_guild(Lounge[0])
#                             current_role = guild.get_role(my_player_rank_id)
#                             new_role = guild.get_role(rank_id)
#                             member = await guild.fetch_member(player[0])
#                             await member.remove_roles(current_role)
#                             await member.add_roles(new_role)
#                             await results_channel.send(f'<@{player[0]}> has been demoted to {new_role}')
#                             with DBA.DBAccess() as db:
#                                 db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (rank_id, player[0]))
#                             my_player_new_rank += f'- {new_role}'
#                     except Exception as e:
#                         # print(e)
#                         pass
#                         # my_player_rank_id = role_id
#                         # guild.get_role(role_id)
#                         # guild.get_member(discord_id)
#                         # member.add_roles(discord.Role)
#                         # member.remove_roles(discord.Role)
#                 string_my_player_new_rank = f'{str(my_player_new_rank).center(12)}'
#                 formatted_my_player_new_rank = await new_rank_wrapper(string_my_player_new_rank, my_player_new_mmr)
#                 mmr_table_string += f'{formatted_my_player_new_rank}'
#                 string_my_player_place = ''

#         # Create imagemagick image
#         # https://imagemagick.org/script/color.php
#         pango_string = f'pango:<tt>{mmr_table_string}</tt>'
#         mmr_filename = f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}mmr.jpg'
#         # correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
#         correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
#         # '+swap', '-compose', 'Over', '-composite', '-quality', '100',
#         # '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',
#         f=discord.File(mmr_filename, filename='mmr.jpg')
#         sf=discord.File(f'/home/lounge/200-Lounge-Mogi-Bot/images/{hex(ctx.author.id)}table.png', filename='table.jpg')

#         # Create embed
#         embed2 = discord.Embed(title=f'Tier {tier_name.upper()} Results', color = discord.Color.blurple())
#         embed2.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
#         embed2.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
#         embed2.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
#         embed2.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
#         embed2.set_image(url='attachment://table.jpg')
#         table_message = await results_channel.send(content=None, embed=embed2, file=sf)
#         table_url = table_message.embeds[0].image.url
#         try:
#             with DBA.DBAccess() as db:
#                 db.query('UPDATE mogi SET table_url = %s WHERE mogi_id = %s;', (table_url, db_mogi_id))
#         except Exception as e:
#             await send_to_debug_channel(ctx, f'Unable to get table url: {e}')
#             pass

#         embed = discord.Embed(title=f'Tier {tier_name.upper()} MMR', color = discord.Color.blurple())
#         embed.add_field(name='Table ID', value=f'{str(db_mogi_id)}', inline=True)
#         embed.add_field(name='Tier', value=f'{tier_name.upper()}', inline=True)
#         embed.add_field(name='Submitted by', value=f'<@{ctx.author.id}>', inline=True)
#         embed.add_field(name='View on website', value=f'https://200-lounge.com/mogi/{db_mogi_id}', inline=False)
#         embed.set_image(url='attachment://mmr.jpg')
#         await results_channel.send(content=None, embed=embed, file=f)
#         #  discord ansi coloring (doesn't work on mobile)
#         # https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06
#         # https://rebane2001.com/discord-colored-text-generator/ 
#         await ctx.respond('`Table Accepted.`', delete_after=300)
#     else:
#         await ctx.respond('`Table Denied.`', delete_after=300)

# /zchange_discord_account
@client.slash_command(
    name='zchange_discord_account',
    description='Change a players discord account [Admin only] [Developer mode required]',
    # guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID)
async def zchange_discord_account(
    ctx,
    old_discord_id: discord.Option(str, 'Original Discord ID', required=True),
    new_discord_id: discord.Option(str, 'New Discord ID', required=True)
    ):
    await ctx.defer()
    bad = await check_if_banned_characters(old_discord_id)
    if bad:
        await send_to_danger_debug_channel(ctx, old_discord_id, discord.Color.red(), vlog_msg.error1)
        await ctx.respond('``Error 50:`` Invalid discord ID (Original Discord ID)')
        return
    bad = await check_if_banned_characters(new_discord_id)
    if bad:
        await send_to_danger_debug_channel(ctx, old_discord_id, discord.Color.red(), vlog_msg.error1)
        await ctx.respond('``Error 51:`` Invalid discord ID (New Discord ID)')
        return
    old_discord_id = int(old_discord_id)
    new_discord_id = int(new_discord_id)
    x = await check_if_uid_exists(old_discord_id)
    y = await check_if_uid_exists(new_discord_id)
    z = await check_if_uid_in_any_tier(old_discord_id)
    if not x:
        await ctx.respond(f'``Error 47:`` {old_discord_id} does not exist')
        return
    if y:
        await ctx.respond(f'``Error 48:`` {new_discord_id} already exists')
        return
    if z:
        await ctx.respond(f'``Error 49:`` {old_discord_id} is in a mogi! You cannot delete them.')
    try:
        with DBA.DBAccess() as db:
            # get old player data
            temp = db.query('SELECT * FROM player WHERE player_id = %s;', (old_discord_id,))
            # create new player
            db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code, fc, is_host_banned, mmr, base_mmr, peak_mmr, rank_id, times_strike_limit_reached, twitch_link, mogi_media_message_id, unban_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', (new_discord_id, temp[0][1], temp[0][2], temp[0][3], temp[0][4], temp[0][5], temp[0][6], temp[0][7], temp[0][8], temp[0][9], temp[0][10], temp[0][11], temp[0][12], temp[0][13]))
            # update player_mogi instances
            db.execute('UPDATE player_mogi SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update player_name_request instances
            db.execute('UPDATE player_name_request SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update strike instances
            db.execute('UPDATE strike SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update sub_leaver instances
            db.execute('UPDATE sub_leaver SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # delete old player
            db.execute('DELETE FROM player WHERE player_id = %s;', (old_discord_id,))
    except Exception as e:
        await send_raw_to_debug_channel('change discord account error', e)
        return
    await ctx.respond(f'Successfully moved player `{old_discord_id}` -> `{new_discord_id}`')
    return







# Takes a ctx, returns the a response (used in re-verification when reentering lounge)
async def set_player_roles(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_name, mmr FROM player WHERE player_id = %s;', (ctx.author.id,))
            player_name = temp[0][0]
            mmr = temp[0][1]
        guild = client.get_guild(Lounge[0])
        member = await guild.fetch_member(ctx.author.id)
        if mmr is None:
            role = guild.get_role(PLACEMENT_ROLE_ID)
            with DBA.DBAccess() as db:
                temp = db.query('SELECT rank_id FROM ranks;', ())
                # Remove all potential ranks first
                for rank in temp:
                    remove_rank = guild.get_role(rank[0])
                    await member.remove_roles(remove_rank)
            await member.add_roles(role)
            return f'Welcome back to 200cc Lounge. You have been given the role: `{role}`. Please check your role and use `/mmr` to make sure you have your MMR from Season 4'
            

        with DBA.DBAccess() as db:
            ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
        for i in range(len(ranks)):
            if mmr > int(ranks[i][1]) and mmr < int(ranks[i][2]):
                # Found your rank
                with DBA.DBAccess() as db:
                    temp = db.query('SELECT rank_id FROM ranks;', ())
                # Remove all potential ranks first
                for rank in temp: 
                    remove_rank = guild.get_role(rank[0])
                    await member.remove_roles(remove_rank)
                role = guild.get_role(ranks[i][0])
                await member.add_roles(role)
                break
        # player_name = player_name.replace("-", " ")
        try:
            await member.edit(nick=str(player_name))
        except Exception as e:
            await send_to_debug_channel(ctx, f'CANNOT EDIT NICKNAME OF STAFF MEMBER. I AM BUT A SMOLL ROBOT... {e}')
            pass
        return f'Welcome back to 200cc Lounge. You have been given the role: `{role}`. Please check your role and use `/mmr` to make sure you have your MMR from Season 4'
    except Exception as e:
        await send_to_debug_channel(ctx, e)
        return f'``Error 29:`` Could not re-enter the lounge. Please contact {secretly.my_discord}.'

# Cool&Create
async def create_player(ctx, mkc_user_id, country_code):
    x = await check_if_player_exists(ctx)
    if x:
        return 'Player already registered'
    else:
        insert_name = await jp_kr_romanize(str(ctx.author.display_name))
        # if insert name contains non alphanumerics, return error
        name_still_exists = True
        count = 0
        # Handle duplicate names
        while(name_still_exists):
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (insert_name,))
            if temp:
                insert_name += "_"
            else:
                name_still_exists = False
            count +=1
            if count == 16:
                return f'``Error 39:`` Oops! An unlikely error occured. Contact {secretly.my_discord} if you think this is a mistake.'
        # Handle name too long
        if len(insert_name) > 16:
            temp_name = ""
            count = 0
            for char in insert_name:
                if count == 15:
                    break
                temp_name+=char
                count+=1
            insert_name = temp_name
        
        f = open('/home/lounge/200-Lounge-Mogi-Bot/200lounge.csv',encoding='utf-8-sig') # f is our filename as string
        lines = list(csv.reader(f,delimiter=',')) # lines contains all of the rows from the csv
        f.close()
        for line in lines:
            name = line[0]
            if name.lower() == (ctx.author.display_name).lower():
                altered_name = str(insert_name).replace(" ", "-")
                mmr = int(line[2])
                with DBA.DBAccess() as db:
                    ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
                for i in range(len(ranks)):
                    if mmr > int(ranks[i][1]) and mmr < int(ranks[i][2]):
                        member = GUILD.get_member(ctx.author.id)
                        role = GUILD.get_role(ranks[i][0])
                        await member.add_roles(role)
                        with DBA.DBAccess() as db:
                            db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code, rank_id, mmr, base_mmr) VALUES (%s, %s, %s, %s, %s, %s, %s);', (ctx.author.id, altered_name, mkc_user_id, country_code, ranks[i][0], mmr, mmr))
                        return f'Verified & registered successfully - Assigned {role}'

        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code) VALUES (%s, %s, %s, %s);', (ctx.author.id, insert_name, mkc_user_id, country_code))
            member = await GUILD.fetch_member(ctx.author.id)
            role = GUILD.get_role(PLACEMENT_ROLE_ID)
            await member.add_roles(role)
            return 'Verified & registered successfully'
        except Exception as e:
            await send_to_debug_channel(ctx, f'create_player error 14 {e}')
            return f'``Error 14:`` Oops! An unlikely error occured. Contact {secretly.my_discord} if you think this is a mistake.'
            # 1. a player trying to use someone elses link (could be banned player)
            # 2. a genuine player locked from usage by another player (banned player might have locked them out)
            # 3. someone is verifying multiple times

# Takes a ctx & a string, returns a response
async def update_friend_code(ctx, message):
    fc_pattern = '\d\d\d\d-?\d\d\d\d-?\d\d\d\d'
    if re.search(fc_pattern, message):
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET fc = %s WHERE player_id = %s;', (message, ctx.author.id))
                return 'Friend Code updated'
        except Exception as e:
            await send_to_debug_channel(ctx, f'update_friend_code error 15 {e}')
            return '``Error 15:`` Player not found'
    else:
        return 'Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'

# Takes a ctx, returns 0 if error, returns 1 if good, returns nothing if mogi cancelled
async def start_mogi(ctx):
    channel = client.get_channel(ctx.channel.id)
    removal_passed = await remove_players_from_other_tiers(ctx.channel.id)
    if removal_passed:
        pass
    else:
        await send_to_debug_channel(ctx, 'Failed to remove all players from other lineups...')
        return 0
    # Set the tier to the voting state
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET voting = 1 WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception as e:
        await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 1 | {e}')
        await channel.send(f'`Error 23:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
        return 0
    # Initialize the mogi timer, for mogilist checker minutes since start...
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET mogi_start_time = %s WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12;', (datetime.datetime.now(), ctx.channel.id))
    except Exception as e:
        await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 4 | {e}')
        await channel.send(f'`Error 23.2:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
        return 0
    # Get the first 12 players
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    except Exception as e:
        await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 2 | {e}')
        await channel.send(f'`Error 22:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
        return 0
    # Set 12 players' state to "cannot drop"
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE lineups SET can_drop = 0 WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
    except Exception as e:
        await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 3 | {e}')
        await channel.send(f'`Error 55:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
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
        return 2
        
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
    return 1

# When the voting starts - constantly check for player input
async def check_for_poll_results(ctx, last_joiner_unix_timestamp):
    # print('checking for poll results')
    dtobject_now = datetime.datetime.now()
    unix_now = time.mktime(dtobject_now.timetuple())
    format_list = [0,0,0,0,0]
    while (unix_now - last_joiner_unix_timestamp) < 120:
        # Votes are updated in the on_message event, if mogi is running and player is in tier
        await asyncio.sleep(0.5)
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
        # print(f'{unix_now} - {last_joiner_unix_timestamp}')
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
        # print(f'votes temp: {votes_temp}')
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

async def remove_players_from_other_tiers(channel_id):
    try:
        with DBA.DBAccess() as db:
            players = db.query('SELECT player_id FROM lineups WHERE tier_id = %s;', (channel_id,))
            for player in players:
                player_tier = db.query('SELECT p.player_id, p.player_name, l.tier_id FROM lineups as l JOIN player as p ON l.player_id = p.player_id WHERE p.player_id = %s AND l.tier_id <> %s;', (player[0], channel_id))
                if player_tier:
                    channel = client.get_channel(player_tier[0][2])
                    db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], player_tier[0][2]))
                    await channel.send(f'{player_tier[0][1]} has dropped from the lineup')
        return True
    except:
        return False

# poll_results is [index of the voted on format, a dictionary of format:voters]
# creates teams, finds host, returns a big string formatted...
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
        if player_db[i][2] is None: # Account for placement ppls
            pass
        else:
            room_mmr = room_mmr + player_db[i][2]
    random.shuffle(players_list) # [[popuko, 7238965417831, 4000],[name, discord id, mmr]]
    room_mmr = room_mmr/MAX_PLAYERS_IN_MOGI
    response_string += f'   `Room MMR:` {math.ceil(room_mmr)}\n'
    # 6v6 /teams string
    if players_per_team != 6:
        # divide the list based on players_per_team
        chunked_list = list()
        for i in range(0, len(players_list), players_per_team):
            chunked_list.append(players_list[i:i+players_per_team])

        # For each divided team, get mmr for all players, average them, append to team
        for team in chunked_list:
            temp_mmr = 0
            count = 0
            for player in team:
                if player[2] is None: # If mmr is null - Account for placement ppls
                    count+=1
                    #pass - commented out and added count+=1 10/10/22 because people mad about playing with placements even tho its 200 and its tier all lol
                else:
                    temp_mmr = temp_mmr + player[2]
                    count += 1
            if count == 0:
                count = 1
            team_mmr = temp_mmr/count
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
                    player_score_string += f'{player[0]} 0 '
                    response_string += f'{player[0]} '
                except TypeError:
                    response_string += f'(MMR: {math.ceil(player)})\n'

        response_string+=f'\n{player_score_string}'
    else:
        with DBA.DBAccess() as db:
            captains = db.query('SELECT player_name, player_id FROM (SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s) as mytable ORDER BY mmr DESC LIMIT 2;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
        response_string += f'   `Captains:` <@{captains[0][1]}> & <@{captains[1][1]}>\n'
        response_string += f'   `Table:` /table 6 `[Team 1 players & scores]` `[Team 2 players & scores]`\n'
    
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (response_string, ctx.channel.id))
    except Exception as e:
        await send_to_debug_channel(ctx, f'team generation error log 1? | {e}')
    # choose a host
    host_string = '    '
    try:
        with DBA.DBAccess() as db:
            host_temp = db.query('SELECT fc, player_id FROM (SELECT p.fc, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s AND p.fc IS NOT NULL AND p.is_host_banned = %s ORDER BY l.create_date LIMIT %s) as fcs_in_mogi ORDER BY RAND() LIMIT 1;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
            host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
    except Exception as e:
        host_string = '    `No FC found` - Choose amongst yourselves'
    # create a return string
    response_string+=f'\n\n{host_string}'
    return response_string

async def check_if_mogi_is_ongoing(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
    except Exception:
        return False
    if temp[0][0] >= MAX_PLAYERS_IN_MOGI:
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
    except Exception: # Player not in any lineups?
        return True

async def check_if_uid_in_any_tier(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s;', (uid,))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_uid_in_specific_tier(uid, tier):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;', (uid, tier))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_uid_in_first_12_of_tier(uid, tier):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM (SELECT player_id FROM lineups WHERE tier_id = %s) as derived_table WHERE player_id = %s;', (tier, uid))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_mkc_user_id_used(mkc_user_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mkc_id from player WHERE mkc_id = %s;', (mkc_user_id,))
            if int(temp[0][0]) == int(mkc_user_id):
                return True
            else:
                return False
    except Exception as e:
        # await send_raw_to_debug_channel(mkc_player_id, e)
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

async def check_if_uid_exists(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_id = %s;', (uid, ))
            if temp[0][0] == uid:
                return True
            else:
                return False
    except Exception:
        return False

async def check_if_mogi_exists(mogi_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mogi_id FROM mogi WHERE mogi_id = %s;', (mogi_id,))
        if temp[0][0] == mogi_id:
            return True
        else:
            return False
    except Exception:
        return False

async def check_if_banned_characters(message):
    for value in secretly.BANNED_CHARACTERS:
        if value in message:
            return True
    return False

async def check_for_dupes_in_list(my_list):
    if len(my_list) == len(set(my_list)):
        return False
    else:
        return True

async def check_if_uid_is_lounge_banned(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT UNIX_TIMESTAMP(unban_date) FROM player WHERE player_id = %s;', (uid,))
        if temp[0][0] is None:
            return False
        else:
            return temp[0][0]
    except Exception as e:
        return False

async def get_unix_time_now():
    return time.mktime(datetime.datetime.now().timetuple())

# Takes in ctx, returns avg partner score
async def get_partner_avg(uid, *mogi_format):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT AVG(score) FROM (SELECT player_id, mogi_id, place, score FROM player_mogi WHERE player_id <> %s AND (mogi_id, place) IN (SELECT mogi_id, place FROM player_mogi WHERE player_id = %s)) as table2;', (uid, uid))
            try:
                return round(float(temp[0][0]), 2)
            except Exception as e:
                return 0
    except Exception as e:
        await send_raw_to_debug_channel('partner average error',e)
    return 0

# Takes in ctx, returns mmr
async def get_player_mmr(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (uid,))
    except Exception as e:
        await send_to_debug_channel(ctx, f'get_player_mmr error 1 | {e}')
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
    channel = client.get_channel(secretly.verification_channel)
    embed = discord.Embed(title='Verification', description=verify_description, color = verify_color)
    embed.add_field(name='Name: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Message: ', value=message, inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_debug_channel(ctx, error):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Error', description='>.<', color = discord.Color.blurple())
    embed.add_field(name='Issuer: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_danger_debug_channel(ctx, message, verify_color, verify_description):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Verification', description=verify_description, color = verify_color)
    embed.add_field(name='Name: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Message: ', value=message, inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_raw_to_debug_channel(anything, error):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Error', description='>.<', color = discord.Color.yellow())
    embed.add_field(name='anything: ', value=anything, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_sub_log(ctx, message):
    unix_now = await get_unix_time_now()
    channel = client.get_channel(secretly.sub_channel)
    embed = discord.Embed(title='Sub', description=f'<t:{str(int(unix_now))}:F>', color = discord.Color.blurple())
    embed.add_field(name='Issuer: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Message: ', value=str(message), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_name_change_log(ctx, id, message):
    channel = client.get_channel(secretly.name_change_channel)
    embed = discord.Embed(title='Name Change Request', description=f'id: {id}', color = discord.Color.blurple())
    embed.add_field(name='Current Name: ', value=ctx.author.display_name, inline=False)
    embed.add_field(name='New Name: ', value=str(message), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    embed.set_thumbnail(url=ctx.author.avatar.url)
    x = await channel.send(content=None, embed=embed)
    return x

async def send_to_ip_match_log(ctx, message, verify_color, user_matches_list):
    channel = client.get_channel(secretly.ip_match_channel)
    embed = discord.Embed(title="Verification", description=f'IP Matches for <@{ctx.author.id}>', color=verify_color)
    try:
        embed.add_field(name="Issuer: ", value=ctx.author, inline=False)
        embed.add_field(name='Link sent: ', value=message, inline=False)
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
            'login': str(secretly.mkc_name),
            'password': str(secretly.mkc_password),
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
            'login': str(secretly.mkc_name),
            'password': str(secretly.mkc_password),
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
            'login': str(secretly.mkc_name),
            'password': str(secretly.mkc_password),
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

# romanizes japanese and korean strings
async def jp_kr_romanize(input):
    r = Romanizer(input)
    kr_result = r.romanize()
    kks = pykakasi.kakasi()
    result = kks.convert(kr_result)
    my_string = ""
    for item in result:
        my_string+=item['hepburn']
    return my_string

# https://imagemagick.org/script/color.php
async def new_rank_wrapper(input, mmr):
    # print(f'input: {input}')
    # print(f'mmr: {mmr}')
    if input:
        if mmr < 1500:
            return await iron_wrapper(input)
        elif mmr >= 1500 and mmr < 3000:
            return await bronze_wrapper(input)
        elif mmr >= 3000 and mmr < 4500:
            return await silver_wrapper(input)
        elif mmr >= 4500 and mmr < 6000:
            return await gold_wrapper(input)
        elif mmr >= 6000 and mmr < 7500:
            return await platinum_wrapper(input)
        elif mmr >= 7500 and mmr < 9000:
            return await diamond_wrapper(input)
        elif mmr >= 9000 and mmr < 11000:
            return await master_wrapper(input)
        elif mmr >= 11000:
            return await grandmaster_wrapper(input)
        else:
            return input
    else:
        return input

async def grandmaster_wrapper(input):
    # return (f'[0;2m[0;40m[0;31m{input}[0m[0;40m[0m[0m')
    return (f'<span foreground="DarkRed">{input}</span>')

async def master_wrapper(input):
    # return (f'[2;40m[2;37m{input}[0m[2;40m[0m')
    return (f'<span foreground="black">{input}</span>')

async def diamond_wrapper(input):
    # return (f'[0;2m[0;34m{input}[0m[0m')
    return (f'<span foreground="PowderBlue">{input}</span>')

async def platinum_wrapper(input):
    # return (f'[2;40m[2;36m{input}[0m[2;40m[0m')
    return (f'<span foreground="teal">{input}</span>')

async def gold_wrapper(input):
    # return (f'[2;40m[2;33m{input}[0m[2;40m[0m')
    return (f'<span foreground="gold1">{input}</span>')

async def silver_wrapper(input):
    # return (f'[0;2m[0;42m[0;37m{input}[0m[0;42m[0m[0m')
    return (f'<span foreground="LightBlue4">{input}</span>')

async def bronze_wrapper(input):
    # return (f'[0;2m[0;47m[0;33m{input}[0m[0;47m[0m[0m')
    return (f'<span foreground="DarkOrange2">{input}</span>')

async def iron_wrapper(input):
    # return (f'[0;2m[0;30m[0;47m{input}[0m[0;30m[0m[0m')
    return (f'<span foreground="DarkGray">{input}</span>')

async def pos_mmr_wrapper(input):
    # return (f'[0;2m[0;32m{input}[0m[0m')
    return (f'<span foreground="chartreuse">{input}</span>')

async def neg_mmr_wrapper(input):
    # return (f'[0;2m[0;31m{input}[0m[0m')
    return (f'<span foreground="Red2">{input}</span>')

async def peak_mmr_wrapper(input):
    # return (f'[0;2m[0;41m[0;37m{input}[0m[0;41m[0m[0m')
    return (f'<span foreground="Yellow1"><i>{input}</i></span>')

client.run(secretly.token)