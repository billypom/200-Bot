import DBA
import DBA2
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
import pytz
import json
import requests
import asyncio
import random
import string
import csv
import urllib.parse
import shutil
import subprocess
import concurrent.futures
from bs4 import BeautifulSoup as Soup
import pykakasi
from korean_romanizer.romanizer import Romanizer
import operator
from textwrap import wrap # used to split long messages into multiple parts

import logging
logging.basicConfig(filename='200lounge.log', filemode='a', level=logging.WARNING)

# discord logging separate
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

Lounge = secretly.Lounge
# mogi_media_message_id = 1005205285817831455
TIER_ID_LIST = list()
RANK_ID_LIST = secretly.RANK_ID_LIST
MAX_PLAYERS_IN_MOGI = secretly.MAX_PLAYERS_IN_MOGI
SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT = secretly.SECONDS_SINCE_LAST_LOGIN_DELTA_LIMIT
NAME_CHANGE_DELTA_LIMIT = secretly.NAME_CHANGE_DELTA_LIMIT
REPORTER_ROLE_ID = secretly.REPORTER_ROLE_ID
ADMIN_ROLE_ID = secretly.ADMIN_ROLE_ID
UPDATER_ROLE_ID = secretly.UPDATER_ROLE_ID
CHAT_RESTRICTED_ROLE_ID = secretly.CHAT_RESTRICTED_ROLE_ID
LOUNGELESS_ROLE_ID = secretly.LOUNGELESS_ROLE_ID
PLACEMENT_ROLE_ID = secretly.PLACEMENT_ROLE_ID
CATEGORIES_MESSAGE_ID = secretly.CATEGORIES_MESSAGE_ID
SQ_HELPER_CHANNEL_ID = secretly.SQ_HELPER_CHANNEL_ID
SQ_TIER_ID = secretly.squad_queue_channel
ALLOWED_CHARACTERS = secretly.ALLOWED_CHARACTERS
SEASON_NUMBER_LIST = secretly.SEASON_NUMBER_LIST
SECONDS_IN_A_DAY = 86400
twitch_thumbnail = 'https://cdn.discordapp.com/attachments/898031747747426344/1005204380208869386/jimmy_neutron_hamburger.jpg'
intents = discord.Intents(messages=True, guilds=True, message_content=True, members=True, reactions=True)
client = discord.Bot(intents=intents, activity=discord.Game(str('200cc Lounge')))
# manage roles, manage channels, manage nicknames, read messages/viewchannels, manage events
# send messages, manage messages, embed links, attach files, read message history, add reactions, use slash commands

# initial_extensions = ['cogs.inactivity_check', 'cogs.update_mogilist', 'cogs.mogi_media_check', 'cogs.strike_check']
initial_extensions = ['cogs.strike_check', 'cogs.unban_check']
for extension in initial_extensions:
    client.load_extension(extension)


# Initialize the TIER_ID_LIST
with DBA.DBAccess() as db:
    get_tier_list = db.query('SELECT tier_id FROM tier WHERE tier_id > %s;', (0,))
    for i in range(len(get_tier_list)):
        TIER_ID_LIST.append(get_tier_list[i][0])

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
        await ctx.respond(f'Sorry! An unknown error occurred. Try again later or make a <#{secretly.support_channel}> ticket for assistance.')
        # print(traceback.format_exc())
        raise error
        return

@client.event
async def on_message(ctx):
    try:
        if ctx.guild == GUILD: # Only care if messages are in 200 Lounge
            pass
        else:
            return
    except Exception:
        return
    if ctx.author.id == secretly.bot_id: # ignore self messages
        return
    if ctx.channel.id == 558096949337915413: # ignore carl bot logging
        return
    user = await GUILD.fetch_member(ctx.author.id)
    if CHAT_RESTRICTED_ROLE in user.roles: # restricted players
        if ctx.content in secretly.chat_restricted_words:
            return
        else:
            await ctx.delete()
            return
    # if ctx.channel.id in TIER_ID_LIST: # Only care if messages are in a tier
    #     # If player in lineup, set player chat activity timer
    #     try:
    #         with DBA.DBAccess() as db:
    #             temp = db.query('SELECT player_id, tier_id FROM lineups WHERE player_id = %s;', (ctx.author.id,))
    #     except Exception as e:
    #         await send_to_debug_channel(ctx, f'on_message error 1 | {e}')
    #         return
    #     try:
    #         test_assign = temp[0][0]
    #     except Exception:
    #         # player not in lineup talked. dont care
    #         return
    #     if temp[0][0] is None:
    #         return
    #     else:
    #         if ctx.channel.id == temp[0][1]: # Type activity in correct channel
    #             try:
    #                 with DBA.DBAccess() as db:
    #                     db.execute('UPDATE lineups SET last_active = %s, wait_for_activity = %s WHERE player_id = %s;', (datetime.datetime.now(), 0, ctx.author.id))
    #             except Exception as e:
    #                 await send_to_debug_channel(ctx, f'on_message error 2 | {e}')
    #                 return
    #     try:
    #         with DBA.DBAccess() as db:
    #             get_tier = db.query('SELECT voting, tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
    #     except Exception as e:
    #         await send_to_debug_channel(ctx, f'on_message error 3 | {e}')
    #     # Set votes, if tier is currently voting
    #     if get_tier[0][0]:
    #         if get_tier[0][1] == ctx.channel.id:
    #             if str(ctx.content) in ['1', '2', '3', '4', '6']:
    #                 try:
    #                     with DBA.DBAccess() as db:
    #                         temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s ORDER BY create_date LIMIT %s;', (ctx.author.id, ctx.channel.id, MAX_PLAYERS_IN_MOGI)) # limit prevents 13th person from voting
    #                 except Exception as e:
    #                     await send_to_debug_channel(ctx, f'on_message error 4 {e}')
    #                     return
    #                 try:
    #                     with DBA.DBAccess() as db:
    #                         db.execute('UPDATE lineups SET vote = %s WHERE player_id = %s;', (int(ctx.content), ctx.author.id))
    #                 except Exception as e:
    #                     await send_to_debug_channel(ctx, f'on_message error 5 {e}')
    #                     return

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
            message_ids = db.query('SELECT embed_message_id, player_id, requested_name FROM player_name_request WHERE was_accepted = %s ORDER BY create_date DESC;', (0,))
    except Exception as e:
        await send_raw_to_debug_channel('Name change exception 1', e)
        return

    # Look @ all embed message ids
    for i in range(0, len(message_ids)):
        if int(payload.message_id) == int(message_ids[i][0]):
            # Join
            try:
                if str(payload.emoji) == '✅':
                    try:
                        with DBA.DBAccess() as db:
                            # Set record to accepted
                            db.execute('UPDATE player_name_request SET was_accepted = %s WHERE embed_message_id = %s;', (1, int(payload.message_id)))
                            # Change the db username
                            db.execute('UPDATE player SET player_name = %s WHERE player_id = %s;', (message_ids[i][2], message_ids[i][1]))
                            # Change the discord username
                    except Exception as e:
                        await send_raw_to_debug_channel('Name change exception 2', e)
                        pass
                    member = guild.get_member(message_ids[i][1])
                    if member is None:
                        await send_raw_to_debug_channel('Name change exception 5', 'User is not in the guild.')
                        return
                    try:
                        await member.send(f'Your name change [{message_ids[i][2]}] has been approved.')
                    except Exception as e:
                        await send_raw_to_debug_channel('Name change exception 3', e)
                        pass
                    try:
                        await member.edit(nick=str(message_ids[i][2]))
                    except Exception as e:
                        await send_raw_to_debug_channel('Name change exception 4', e)
                        pass
                elif str(payload.emoji) == '❌':
                    with DBA.DBAccess() as db:
                        # Remove the db record
                        db.execute('DELETE FROM player_name_request WHERE embed_message_id = %s;', (int(payload.message_id),))
                        # Delete the embed message
                    member = guild.get_member(message_ids[i][1])
                    await member.send(f'Your name change [{message_ids[i][2]}] has been denied.')
                    await message.delete()
                else:
                    x = int('hey')
            except Exception as e:
                await send_raw_to_debug_channel('Name change exception', e)
                pass
        try:
            await message.remove_reaction(payload.emoji, member)
            # Delete the embed message
            await message.delete()
        except Exception:
            pass
    return

@client.event
async def on_member_join(member):
    try:
        x = await set_uid_roles(member.id)
        if not x:
            return
        logging.warning(f'Member joined & found! {member} ')
    except Exception as e:
        logging.warning(f'on_member_join exception: {e}')
        return




















# /verify <link>
@client.slash_command(
    name='verify',
    description='Verify your MKC account',
    guild_ids=Lounge
)
async def verify(
    ctx, 
    message: discord.Option(str, 'MKC Link | https://www.mariokartcentral.com/mkc/registry/players/930', required=True)):
    # mkc_player_id = registry id
    # mkc_user_id = forum id
    await ctx.defer(ephemeral=False)
    x = await check_if_uid_exists(ctx.author.id)
    if x:
        lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
        if lounge_ban:
            await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
            return
        else:
            pass
        response = await set_uid_roles(ctx.author.id)
        if response:
            member = await GUILD.fetch_member(ctx.author.id)
            msg_response = f':flag_us:\nWelcome back to 200cc Lounge.\nYou have been given the role: <@&{response[0]}>\n\n:flag_jp:\n`200ccラウンジにおかえり！`\n<@&{response[0]}>`が割り当てられています`'
            await ctx.respond(msg_response)
            logging.warning(f'POP_LOG | {member.display_name} | Responded to verification message')
            await member.send(msg_response)
            logging.warning(f'POP_LOG | {member.display_name} | Sent verification DM')
        else:
            await ctx.respond(f'``Error 29:`` Could not re-enter the lounge. Try again later or make a <#{secretly.support_channel}> ticket for assistance.')        
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
        elif re.search(regex_pattern2, str(message)):
            regex_group = re.search(regex_pattern2, message)
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
        elif re.search(regex_pattern2, str(message)):
            regex_group = re.search(regex_pattern2, message)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp)-1])
        else:
            # player doesnt exist on forums
            await ctx.respond('``Error 3:`` Oops! Something went wrong. Check your link or try again later')
            return
    else:
        await ctx.respond('``Error 80:`` Oops! Something went wrong. Check your link or try again later')
        return
    # Make sure player_id was received properly
    if mkc_player_id != -1:
        pass
    else:
        await ctx.respond('``Error 4:`` Oops! Something went wrong. ```MKC Player ID not transmitted properly.\nMake sure you are signed up in the MKC Registry or try again later.```')
        return
    # Request registry data
    mkc_registry_data = await mkc_request_registry_info(mkc_player_id)
    mkc_user_id = mkc_registry_data[0]
    country_code = mkc_registry_data[1]
    is_banned = mkc_registry_data[2]

    if is_banned:
        # Is banned
        verify_description = vlog_msg.error3
        await ctx.respond('``Error 7:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_description)
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
            await ctx.respond('``Error 5:`` Please log in to your MKC account, then retry. \n\nIf you are still being refused verification, click this link then try again: https://www.mariokartcentral.com/forums/index.php?members/popuko.154/')
            await send_to_verification_log(ctx, message, verify_description)
            return
        else:
            pass
    else:
        verify_description = vlog_msg.error7
        verify_color = discord.Color.red()
        await ctx.respond('``Error 6:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, f'Error 6: {message}', verify_description)
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
        await ctx.respond(f'``Error 10:`` Oops! Something went wrong. Try again later or make a <#{secretly.support_channel}> ticket for assistance.')
        verify_description = vlog_msg.error4
        verify_color = discord.Color.red()
        await send_to_verification_log(ctx, f'Error 10: {message}', f'{verify_description} | <@{x[1]}> already using MKC **FORUM** ID {x[0]}')
        return
    else:
        member = await GUILD.fetch_member(ctx.author.id)
        x = await create_player(member, mkc_user_id, country_code)
        logging.warning(f'POP_LOG | Created player: discord.Member: {member} | mkc_user_id: {mkc_user_id} | country: {country_code}')
        try:
            await ctx.respond(x)
            logging.warning(f'POP_LOG | {member.display_name} | Responded to verification message')
            await member.send(x)
            logging.warning(f'POP_LOG | {member.display_name} | Sent verification DM')
        except Exception as e:
            await ctx.respond('oops')
        await send_to_verification_log(ctx, message, verify_description)
        return


# /name
@client.slash_command(
    name='name',
    description='Change your name',
    # guild_ids=Lounge
)
async def name(
    ctx,
    name: discord.Option(str, 'Enter a new nickname here', required=True)
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
        await send_to_verification_log(ctx, name, vlog_msg.error1)
        await ctx.respond('You cannot use this name')
        return
    else:
        pass
    input_name = name
    name = await jp_kr_romanize(name)
    name = name.replace(" ", "-")
    if len(name) > 16:
        await ctx.respond(f'Your request: {input_name} -> {name} | Name is too long. 16 characters max')
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
                temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM player_name_request WHERE player_id = %s ORDER BY create_date DESC;', (ctx.author.id,))
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
            await ctx.respond(f'``Error 44:`` Oops! Something went wrong. Try again later or make a <#{secretly.support_channel}> ticket for assistance.')
            return
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player_name_request SET embed_message_id = %s WHERE id = %s;', (request_message_id, player_name_request_id))
            await ctx.respond(f'Your request: {input_name} -> {name} | Your name change request was submitted to the staff team for review.')
            return
        except Exception as e:
            await send_to_debug_channel(ctx, f'Tried name: {name} |\n{e}')
            await ctx.respond(f'``Error 35:`` Oops! Something went wrong. Try again later or make a <#{secretly.support_channel}> ticket for assistance.')
            return

# /table
@client.slash_command(
    name='table',
    description='Submit a table',
    guild_ids=Lounge
)
@commands.has_role(REPORTER_ROLE_ID)
async def table(
    ctx,
    mogi_format: discord.Option(int, '1=FFA, 2=2v2, 3=3v3, 4=4v4, 6=6v6', required=True),
    scores: discord.Option(str, 'player scores (i.e. popuko 12 JPGiviner 42 Technical 180...)', required=True)
    ):
    await ctx.defer()
    # ------- Perform access checks
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    # Check scores for bad input
    bad = await check_if_banned_characters(scores)
    if bad:
        await send_to_verification_log(ctx, scores, vlog_msg.error1)
        await ctx.respond(f'``Error 32:`` Invalid input. There must be 12 players and 12 scores.')
        return
    # Check if table was submitted from a tier channel + sq
    with DBA.DBAccess() as db:
        temp = db.query('SELECT tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
    try:
        nya_tier_id = temp[0][0]
    except Exception as e:
        # Retrieve SQ Tier ID from categories helper
        # A debug message is posted by the bot, and read here to allow submitting tables from all room channels
        sq_helper_channel = client.get_channel(SQ_HELPER_CHANNEL_ID)
        sq_helper_message = await sq_helper_channel.fetch_message(CATEGORIES_MESSAGE_ID)
        if str(ctx.channel.category.id) in sq_helper_message.content:
            nya_tier_id = SQ_TIER_ID
        else:
            await ctx.respond(f'``Error 72a: `/table` must be used from a tier channel``')
            return





    chunked_list = await handle_score_input(ctx, scores, mogi_format)
    if not chunked_list:
        await ctx.respond(f'``Error 73:`` Invalid input. There must be 12 players and 12 scores.')
        return
    logging.warning(f'POP_LOG | chunked_list: {chunked_list}')
    
    # Check if mogi has started
    # try:
    #     with DBA.DBAccess() as db:
    #         temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (nya_tier_id,))
    #         players_in_lineup_count = temp[0][0]
    # except Exception as e:
    #     await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secretly.my_discord}. {e}')
    #     await send_to_debug_channel(ctx, f'/table Error 18: {e}')
    #     return
    # does not matter when u make table anymore
    # if players_in_lineup_count < 12:
        # await ctx.respond('Mogi has not started. Cannot create a table now')
        # return


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





    # Get the highest MMR ever
    #   There was a very high integer in the formula for calculating mmr on the original google sheet (9998)
    #   A comment about how people "never thought anyone could reach 10k mmr" made me think this very high integer was a
    #       replacement for getting the highest existing mmr (or at least my formula could emulate that high integer 
    #       with some variance :shrug: its probably fine... no1 going 2 read this)
    # try:
        # with DBA.DBAccess() as db:
            # h = db.query('SELECT max(mmr) from player where player_id > %s;',(0,))
            # highest_mmr = h[0][0]
    # except Exception as e:
        # await ctx.respond(f'``Error 76:`` `/table` error. Make a <#{secretly.support_channel}> if you need assistance.')
    # print(f'player score chunked list: {player_score_chunked_list}')
    highest_mmr = 10999


    








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
                        if char.isdigit():
                            current_group += char
                        elif char == '-' or char == '+':
                            sign = char
                            points += int(f'{sign}{current_group}')
                            current_group = ''
                        else:
                            await ctx.respond(f'``Error 26:``There was an error with the following player: <@{player[0]}>')
                            return
                    # Last item in list needs to be added
                    points += int(f'{sign}{current_group}')
                    player[1] = points
                    team_score = team_score + points
            except Exception as e:
                # check for all 12 players exist
                await send_to_debug_channel(ctx, f'/table Error 24:{e}')
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
                score = player[1]
            lorenzi_query += f'{player_name} [{country_code}] {score}\n'

        # Assign previous values before looping
        prev_team_placement = team_placement
        prev_team_score = team[len(team)-3]








    # Request a lorenzi table
    query_string = urllib.parse.quote(lorenzi_query)
    url = f'https://gb.hlorenzi.com/table.png?data={query_string}'
    response = requests.get(url, stream=True)
    with open(f'./images/{hex(ctx.author.id)}table.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response






    # Ask for table confirmation
    table_view = Confirm(ctx.author.id)
    channel = client.get_channel(ctx.channel.id)
    await channel.send(file=discord.File(f'./images/{hex(ctx.author.id)}table.png'), delete_after=300)
    await channel.send('Is this table correct? :thinking:', view=table_view, delete_after=300)
    await table_view.wait()
    if table_view.value is None:
        await ctx.respond('No response from reporter. Timed out')




    elif table_view.value: # yes
        db_mogi_id = 0
        # Create mogi
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO mogi (mogi_format, tier_id) values (%s, %s);', (mogi_format, nya_tier_id))
        ##########await send_raw_to_debug_channel('Mogi created' , f'{mogi_format} | {nya_tier_id}')
        # Get the results channel and tier name for later use
        with DBA.DBAccess() as db:
            temp = db.query('SELECT results_id, tier_name FROM tier WHERE tier_id = %s;', (nya_tier_id,))
            db_results_channel = temp[0][0]
            tier_name = temp[0][1]
        results_channel = await client.fetch_channel(db_results_channel)
        #############await send_raw_to_debug_channel('Results channel acquired', f'{results_channel}')






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
        ############await send_raw_to_debug_channel('MMR calculated', 'value table loaded')







        # # DEBUG
        # print(f'\nprinting value table:\n')
        # for _list in value_table:
        #     print(_list)

        # Actually calculate the MMR
        logging.warning(f'POP_LOG | Calculating MMR')
        for idx, team in enumerate(sorted_list):
            logging.warning(f'POP_LOG | {idx} | {team}')
            temp_value = 0.0
            for pre_mmr_list in value_table:
                # logging.warning(f'POP_LOG | {pre_mmr_list}')
                # print(f'{idx}pre mmr list')
                # print(pre_mmr_list)
                for idx2, value in enumerate(pre_mmr_list):
                    # logging.warning(f'POP_LOG | (idx,idx2)')
                    # logging.warning(f'POP_LOG | {idx},{idx2}')
                    # logging.warning(f'POP_LOG | {temp_value} += {value}')
                    # logging.warning(f'POP_LOG | {temp_value.real} += {value.real}')
                    if idx == idx2:
                        temp_value += value
                    else:
                        pass
            # print(f'appending {temp_value}+={value} | {idx} | {idx2}')
            logging.warning(f'POP_LOG | value = {temp_value}, value.real = {temp_value.real}')
            team.append(math.floor(temp_value.real))





        # Create mmr table string
        if mogi_format == 1:
            string_mogi_format = 'FFA'
        else:
            string_mogi_format = f'{str(mogi_format)}v{str(mogi_format)}'

        mmr_table_string = f'<big><big>{ctx.channel.name} {string_mogi_format}</big></big>\n'
        mmr_table_string += f'PLACE |       NAME       |  MMR  |  +/-  | NEW MMR |  RANKUPS\n'





        for team in sorted_list:
            logging.warning(f'POP_LOG | team in sorted_list: {team}')
            ###########await send_raw_to_debug_channel('Updating team', team)
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
                    placement_name, my_player_mmr = await handle_placement_init(player, my_player_mmr, my_player_score, ctx.channel.name, results_channel)
                














                # if is_sub: # Subs only gain on winning team
                #     if team[len(team)-1] < 0:
                #         my_player_mmr_change = 0
                #     else:
                #         my_player_mmr_change = team[len(team)-1]
                # else:
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
                        temp = db.query('SELECT mogi_id FROM mogi WHERE tier_id = %s ORDER BY create_date DESC LIMIT 1;', (nya_tier_id,))
                        db_mogi_id = temp[0][0]
                        # Insert reference record
                        db.execute('INSERT INTO player_mogi (player_id, mogi_id, place, score, prev_mmr, mmr_change, new_mmr) VALUES (%s, %s, %s, %s, %s, %s, %s);', (player[0], db_mogi_id, int(my_player_place), int(my_player_score), int(my_player_mmr), int(my_player_mmr_change), int(my_player_new_mmr)))
                        # Update player record
                        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, player[0]))
                        # Remove player from lineups
                        # db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], nya_tier_id)) # YOU MUST SUBMIT TABLE IN THE TIER THE MATCH WAS PLAYED
                        # Clear sub leaver table
                        # subs dont matter anymore
                        # db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (nya_tier_id,))
                except Exception as e:
                    # print(e)
                    await send_to_debug_channel(ctx, f'FATAL TABLE ERROR: {e}')
                    pass
                


                # Remove mogi media messages
                if mogi_media_message_id is None:
                    pass
                else:
                    channel = client.get_channel(secretly.mogi_media_channel_id)
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
                            await results_channel.send(f'<@{player[0]}> has been promoted to {new_role}!')
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







        ###########await send_raw_to_debug_channel('TEAMS UPDATED', 'Success')
        # Create imagemagick image
        # https://imagemagick.org/script/color.php
        pango_string = f'pango:<tt>{mmr_table_string}</tt>'
        mmr_filename = f'./images/{hex(ctx.author.id)}mmr.jpg'
        # correct = subprocess.run(['convert', '-background', 'gray21', '-fill', 'white', pango_string, mmr_filename], check=True, text=True)
        correct = subprocess.run(['convert', '-background', 'None', '-fill', 'white', pango_string, 'mkbg.jpg', '-compose', 'DstOver', '-layers', 'flatten', mmr_filename], check=True, text=True)
        # '+swap', '-compose', 'Over', '-composite', '-quality', '100',
        # '-fill', '#00000040', '-draw', 'rectangle 0,0 570,368',
        f=discord.File(mmr_filename, filename='mmr.jpg')
        sf=discord.File(f'./images/{hex(ctx.author.id)}table.png', filename='table.jpg')

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
        await ctx.respond('`Table Accepted.`')
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
    # tier: discord.Option(discord.TextChannel, description='Which tier?', required=False),
    tier: discord.Option(str, description='Which tier? (a, b, c, all, sq)', required=False),
    mogi_format: discord.Option(int, description='Your choices: (1, 2, 3, 4, 6)', required=False),
    # player: discord.Option(discord.Member, description='Which player?', required=False),
    last: discord.Option(int, description='How many mogis?', required=False),
    player: discord.Option(str, description='Which player?', required=False),
    season: discord.Option(int, description='Season number (5, 6)', required=False)
    ):
    await ctx.defer()
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    # Validate strings
    # Season picker
    if secretly.DTB == 'lounge_dev':
        stats_db = 'lounge_dev'
    else:
        stats_db = f's{secretly.CURRENT_SEASON}200lounge'
        if season is None:
            pass
        else:
            try:
                if season in SEASON_NUMBER_LIST:
                    pass
                else:
                    await send_raw_to_debug_channel(f'/stats invalid season {season}: ', 'lol')
                    await ctx.respond('Invalid season')
                    return
                stats_db = f's{int(season)}200lounge'
            except Exception as e:
                await send_raw_to_debug_channel('Stats parse season db exception: ', e)
                await ctx.respond('Invalid season')
                return
    # Tier picker
    if tier is None:
       pass
    else: # User entered a value, so check it
        bad = await check_if_banned_characters(tier)
        if bad:
            await ctx.respond("Invalid tier")
            await send_to_verification_log(ctx, tier, vlog_msg.error1)
            return
        # Retrieve tier ID and api request the discord.TextChannel object
        try:
            with DBA2.DBAccess(stats_db) as db:
                tier_id = db.query('SELECT tier_id FROM tier WHERE tier_name = %s;', (tier,))[0][0]
                tier_channel = await client.fetch_channel(tier_id)
        except Exception as e: # bad input 2 - no tier by that name
            await send_raw_to_debug_channel(f'/stats invalid tier: {tier}', e)
            await ctx.respond("Invalid tier")
            return
    # Status for self or others
    if player is None:
        pass
    else:
        bad = await check_if_banned_characters(player)
        if bad:
            await ctx.respond("Invalid player")
            await send_to_verification_log(ctx, player, vlog_msg.error1)
            return
        # Retrieve player ID
        try:
            with DBA2.DBAccess(stats_db) as db:
                player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
        except Exception as e: # bad input 2 - no player by that name
            await ctx.respond('Invalid player')
            return
    # Last n mogis
    if last is None:
        number_of_mogis = 999999
    else:
        if last < 0:
            await ctx.respond(f'You will score 180 and gain 99999 MMR in the next {abs(last)} mogi(s).')
            return
        number_of_mogis = last
    
    # Format picker
    mogi_format_list = []
    if mogi_format is None:
        mogi_format_list = [1, 2, 3, 4, 6]
    elif mogi_format in [1, 2, 3, 4, 6]:
        mogi_format_list.append(mogi_format)
    else:
        await ctx.respond(f'Invalid format: `{mogi_format}`')
        return
    mogi_format_string = ','.join(str(e) for e in mogi_format_list)

    
    if ctx.channel.id in secretly.tier_chats:
        await ctx.respond('`/stats` is not available in tier channels.')
        return
    mmr_history = [] #
    score_history = [] #
    mogi_id_history = [] #
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
        my_player_id = player_id


    # Checks for valid player
    try: 
        with DBA2.DBAccess(stats_db) as db:
            temp = db.query('SELECT base_mmr, peak_mmr, mmr, player_name FROM player WHERE player_id = %s;', (my_player_id,))
            if temp[0][0] is None:
                base = 0
            else:
                base = temp[0][0]
            peak = temp[0][1]
            mmr = temp[0][2]
            player_name = temp[0][3]
        with DBA2.DBAccess(stats_db) as db:
            temp = db.query('SELECT COUNT(*) FROM player WHERE mmr >= %s ORDER BY mmr DESC;', (mmr,))
            rank = temp[0][0]
    except Exception as e:
        await send_to_debug_channel(ctx, f'/stats error 31 | {e}')
        await ctx.respond('``Error 31:`` Player not found.')
        return


    # Create matplotlib MMR history graph
    if tier is None:
        with DBA2.DBAccess(stats_db) as db:

            sql = 'SELECT pm.mmr_change, pm.score, pm.mogi_id FROM player_mogi pm JOIN mogi m ON pm.mogi_id = m.mogi_id WHERE pm.player_id = %s AND m.mogi_format IN (%s) ORDER BY m.create_date DESC LIMIT %s;' % ('%s', mogi_format_string, '%s')

            temp = db.query(sql, (my_player_id, number_of_mogis)) # order newest first

            try:
                did_u_play_yet = temp[0][0]
            except Exception:
                await ctx.respond('You must play at least 1 match to use `/stats`')
                return
                
            for i in range(len(temp)):
                mmr_history.append(temp[i][0]) # append to list newest first
                score_history.append(temp[i][1])
                mogi_id_history.append(temp[i][2])
                if i <= 9: # if we are at the last 10 indexes (first 10, newest first)
                    last_10_change += mmr_history[i]
                    if mmr_history[i] > 0:
                        last_10_wins += 1
                    else:
                        last_10_losses += 1
        partner_average = await get_partner_avg(my_player_id, number_of_mogis, mogi_format_string, '%', stats_db)
    elif tier_id in TIER_ID_LIST:
        try:
            with DBA2.DBAccess(stats_db) as db:

                sql = 'SELECT pm.mmr_change, pm.score, pm.mogi_id FROM player_mogi pm JOIN mogi m ON pm.mogi_id = m.mogi_id WHERE pm.player_id = %s AND m.tier_id = %s AND m.mogi_format IN (%s) ORDER BY m.create_date DESC LIMIT %s;' % ('%s', '%s', mogi_format_string, '%s')

                temp = db.query(sql, (my_player_id, tier_id, number_of_mogis))

                for i in range(len(temp)):
                    mmr_history.append(temp[i][0])
                    score_history.append(temp[i][1])
                    mogi_id_history.append(temp[i][2])
                    if i <= 9:
                        last_10_change += mmr_history[i]
                        if mmr_history[i] > 0:
                            last_10_wins += 1
                        else:
                            last_10_losses += 1
        except Exception as e:
            await send_to_debug_channel(ctx, f'/stats not played in tier | {e}')
            await ctx.respond(f'You have not played in {tier_channel}')
            return
        partner_average = await get_partner_avg(my_player_id, number_of_mogis, mogi_format_string, tier_id, stats_db)
    else:
        await ctx.respond(f'``Error 30:`` {tier_channel} is not a valid tier')
        return
    mmr_history.reverse() # reverse list, oldest first for matplotlib
    score_history.reverse()
    mogi_id_history.reverse()

    events_played = len(mmr_history)
    try:
        top_index, top_score = max(enumerate(score_history), key=operator.itemgetter(1))
    except Exception as e:
        await ctx.respond(f'You have not played in {tier_channel}')
        return
    top_mogi_id = mogi_id_history[top_index]

    try:
        largest_gain = max(mmr_history)
    except Exception:
        largest_gain = 0

    largest_loss = min(mmr_history)
    average_score = sum(score_history)/len(score_history)

    # Start at proper value for mmr graph
    if last is None:
        graph_base = base
    else:
        graph_base = mmr + (sum(mmr_history)*-1)

    for match in mmr_history:
        if match > 0:
            count_of_wins += 1
    win_rate = (count_of_wins/len(mmr_history))*100

    file = plotting.create_plot(graph_base, mmr_history)
    f=discord.File(file, filename='stats.png')

    title='Stats'
    if tier is None:
        pass
    else:
        title+=f' | tier-{tier}'

    if mogi_format is None:
        pass
    else:
        if int(mogi_format) == 1:
            title+= f' | FFA'
        else:
            title+= f' | {mogi_format}v'

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

    rank_filename = './images/rank.png'
    stats_rank_filename = './images/stats_rank.png'

    rgb_flag = f'rgb({red},{green},{blue})'
    correct = subprocess.run([f'convert', rank_filename, '-fill', rgb_flag, '-tint', '100', stats_rank_filename])
    # f=discord.File(rank_filename, filename='rank.jpg')
    sf=discord.File(stats_rank_filename, filename='stats_rank.jpg')

    embed = discord.Embed(title=f'{title}', description=f'[{player_name}](https://200-lounge.com/player/{player_name})', color = discord.Color.from_rgb(red, green, blue)) # website link
    embed.add_field(name='Rank', value=f'{rank}', inline=True)
    embed.add_field(name='MMR', value=f'{mmr}', inline=True)
    embed.add_field(name='Peak MMR', value=f'{peak}', inline=True)
    embed.add_field(name='Win Rate', value=f'{round(win_rate,0)}%', inline=True)
    embed.add_field(name='W-L (Last 10)', value=f'{last_10_wins} - {last_10_losses}', inline=True)
    embed.add_field(name='+/- (Last 10)', value=f'{last_10_change}', inline=True)
    embed.add_field(name='Avg. Score', value=f'{round(average_score, 2)}', inline=True)
    embed.add_field(name='Top Score', value=f'[{top_score}](https://200-lounge.com/mogi/{top_mogi_id})', inline=True) # website link
    embed.add_field(name='Partner Avg.', value=f'{partner_average}', inline=True)
    embed.add_field(name='Events Played', value=f'{events_played}', inline=True)
    embed.add_field(name='Largest Gain', value=f'{largest_gain}', inline=True)
    embed.add_field(name='Largest Loss', value=f'{largest_loss}', inline=True)
    embed.add_field(name='Base MMR', value=f'{base}', inline=True)
    embed.set_thumbnail(url='attachment://stats_rank.jpg')
    embed.set_image(url='attachment://stats.png')
    # await channel.send(file=f, embed=embed)
    await ctx.respond(files=[f,sf], embed=embed)
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
    try:
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
    except Exception as e:
        await send_raw_to_debug_channel('/mmr command triggered by player without mmr: ', e)
        await ctx.respond('Use `/verify` to register for Lounge before checking your MMR.')
        return


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

# /suggest
@client.slash_command(
    name='suggest',
    description='Suggest an improvement for the Lounge (1000 characters max)',
    guild_ids=Lounge
)
async def suggest(
    ctx,
    message: discord.Option(str, 'Type your suggestion', required=True)
    ):
    await ctx.defer(ephemeral=True)
    lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
        return
    else:
        pass
    x = await check_if_banned_characters(message)
    if x:
        await ctx.respond(f'Oops! There was an error with your suggestion. Try using less symbols :P')
        return
    try:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO suggestion (content, author_id) VALUES (%s, %s);', (message, ctx.author.id))
            suggestion_id = db.query('SELECT id FROM suggestion WHERE author_id = %s AND content = %s', (ctx.author.id, message))[0][0]
        request_message = await send_to_suggestion_voting_channel(ctx, suggestion_id, message)
        request_message_id = request_message.id
        with DBA.DBAccess() as db:
            db.execute('UPDATE suggestion SET message_id = %s WHERE id = %s;', (request_message_id, suggestion_id))
        await request_message.add_reaction('⬆️')
        await request_message.add_reaction('⬇️')
        await ctx.respond('Your suggestion has been submitted.')
    except Exception as e:
        await send_raw_to_debug_channel('/suggest error: ', e)
        await ctx.respond(f'`Error 81:` There was an issue with your suggestion. Please create a ticket in {secretly.support_channel} with your error number.')
        return


# /approve_suggestion
@client.slash_command(
    name='approve_suggestion',
    description='Approve a suggestion by ID',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def approve(
    ctx,
    suggestion_id: discord.Option(int, 'Suggestion ID', required=True),
    reason: discord.Option(str, 'Type your reason (1000 characters max)', required=True)
    ):
    await ctx.defer(ephemeral=True)
    try:
        with DBA.DBAccess() as db:
            crap = db.query('SELECT id, author_id, content, message_id FROM suggestion WHERE id = %s;', (suggestion_id, ))
    except Exception as e:
        await send_raw_to_debug_channel('/approve_suggestion error 1', e)
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE suggestion SET reason = %s, was_accepted = %s, admin_id = %s WHERE id = %s', (reason, 1, ctx.author.id, suggestion_id))
    except Exception as e:
        await send_raw_to_debug_channel('/approve_suggestion error 2', e)

    # suggestion_id
    suggestion = crap[0][2]
    author_id = crap[0][1]
    message_id = crap[0][3]
    admin_id = ctx.author.id
    # reason

    response = await handle_suggestion_decision(suggestion_id, suggestion, author_id, message_id, admin_id, 1, reason)
    if response:
        await ctx.respond(f'Suggestion #{suggestion_id} approved')
    else:
        await ctx.respond(f'Error...')

# /deny_suggestion
@client.slash_command(
    name='deny_suggestion',
    description='Deny a suggestion by ID',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def deny(
    ctx,
    suggestion_id: discord.Option(int, 'Suggestion ID', required=True),
    reason: discord.Option(str, 'Type your reason (1000 characters max)', required=True)
    ):
    await ctx.defer(ephemeral=True)
    try:
        with DBA.DBAccess() as db:
            crap = db.query('SELECT id, author_id, content, message_id FROM suggestion WHERE id = %s;', (suggestion_id, ))
    except Exception as e:
        await send_raw_to_debug_channel('/deny_suggestion error 1', e)
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE suggestion SET reason = %s, was_accepted = %s, admin_id = %s WHERE id = %s', (reason, 0, ctx.author.id, suggestion_id))
    except Exception as e:
        await send_raw_to_debug_channel('/deny_suggestion error 2', e)

    # suggestion_id
    suggestion = crap[0][2]
    author_id = crap[0][1]
    message_id = crap[0][3]
    admin_id = ctx.author.id
    # reason

    response = await handle_suggestion_decision(suggestion_id, suggestion, author_id, message_id, admin_id, 0, reason)
    if response:
        await ctx.respond(f'Suggestion #{suggestion_id} denied')
    else:
        await ctx.respond(f'Error...')

# /zstrikes
@client.slash_command(
    name='zstrikes',
    description='See strikes for a specific player',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zstrikes(ctx,
    player: discord.Option(str, description='Player name', required=True)
    ):
    await ctx.defer()

    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return

    lounge_ban = await check_if_uid_is_lounge_banned(player_id)
    if lounge_ban:
        await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
        return
    else:
        pass
    x = await check_if_uid_exists(player_id)
    if x:
        pass
    else:
        await ctx.respond('Player not found.')
        return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT UNIX_TIMESTAMP(expiration_date) FROM strike WHERE player_id = %s AND is_active = %s ORDER BY create_date ASC;', (player_id, 1))
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
    guild_ids=Lounge
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
            # db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
        await ctx.respond('The mogi has been cancelled')
    except Exception as e:
        await send_to_debug_channel(ctx, f'Cancel Error Deletion:{e}')
        return

# /zrevert
@client.slash_command(
    name="zrevert",
    description="Undo a table [Admin only]",
    guild_ids=Lounge
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
    for i in range(len(players_mogi)): # this is very bad because i should just loop the other way around
        # but im lazy and still need to make a dev server
        # but also who cares
        my_player_id = players_mogi[i][0]
        my_player_name = players_mogi[i][1]
        my_player_mmr = int(players_mogi[i][2])
        my_player_new_mmr = my_player_mmr + (int(players_mogi[i][3])* -1)
        my_player_rank_id = players_mogi[i][4]
        results_channel_id = players_mogi[i][5]
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_mmr, my_player_id))
        except Exception as e:
            await send_to_debug_channel(ctx, f'/zrevert FATAL ERROR 2 | {e}')
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
    guild_ids=Lounge
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
        await send_to_verification_log(ctx, player1, vlog_msg.error1)
        return
    else:
        pass
    y = await check_if_banned_characters(player2)
    if y:
        await ctx.respond("Invalid player2 name")
        await send_to_verification_log(ctx, player1, vlog_msg.error1)
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
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zstrike(
    ctx,
    player: discord.Option(str, description='Player name', required=True),
    mmr_penalty: discord.Option(int, description='How much penalty to apply?', required=True),
    reason: discord.Option(str, description='Why?', required=True)
    ):
    await ctx.defer()
    if len(reason) > 32:
        await ctx.respond('Reason too long (32 character limit)')
        return
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return
    y = await check_if_banned_characters(reason)
    if y:
        await ctx.respond('Invalid reason')
        return
    # Send info to strikes table
    mmr_penalty = abs(mmr_penalty)
    # Update player MMR
    current_time = datetime.datetime.now()
    expiration_date = current_time + datetime.timedelta(days=30)
    mmr = 0
    num_of_strikes = 0
    # if placement player, insert a strike, penalty applied = 0
    player_is_placement = await check_if_uid_is_placement(player_id)
    if player_is_placement:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO strike (player_id, reason, mmr_penalty, expiration_date, penalty_applied) VALUES (%s, %s, %s, %s, %s);', (player_id, reason, mmr_penalty, expiration_date, 0))
    else:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))
            if temp[0][0] is None:
                await ctx.respond(f'This player has no MMR! Contact {secretly.my_discord}')
                return
            else:
                mmr = temp[0][0]
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO strike (player_id, reason, mmr_penalty, expiration_date) VALUES (%s, %s, %s, %s);', (player_id, reason, mmr_penalty, expiration_date))
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', ((mmr-mmr_penalty), player_id))
    num_of_strikes = await get_number_of_strikes(player_id)
    if num_of_strikes >= 3:
        times_strike_limit_reached = 0
        with DBA.DBAccess() as db:
            temp = db.query('SELECT times_strike_limit_reached FROM player WHERE player_id = %s;', (player_id,))
            times_strike_limit_reached = temp[0][0] + 1
            unban_unix_time = await get_unix_time_now() + 24*60*60*times_strike_limit_reached
            dt = datetime.datetime.utcfromtimestamp(unban_unix_time).strftime('%Y-%m-%d %H:%M:%S')
            db.execute('UPDATE player SET times_strike_limit_reached = %s, unban_date = %s WHERE player_id = %s;', (times_strike_limit_reached, dt, player_id))
        user = await GUILD.fetch_member(player_id)
        await user.add_roles(LOUNGELESS_ROLE)
        ranks_list = await get_list_of_rank_ids()
        for rank in ranks_list:
            bye = GUILD.get_role(rank)
            await user.remove_roles(bye)
        channel = client.get_channel(secretly.strikes_channel)
        await channel.send(f'<@{player_id}> has reached 3 strikes. Loungeless role applied\n`# of offenses:` {times_strike_limit_reached}')
    await ctx.respond(f'Strike applied to <@{player_id}> | Penalty: {mmr_penalty}')
     
# # /zhostban
# @client.slash_command(
#     name='zhostban',
#     description='Add hostban to a player [Admin only]',
#     guild_ids=Lounge
# )
# @commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
# async def zhostban(
#     ctx,
#     player: discord.Option(discord.Member, description='Which player?', required=True)
#     ):
#     await ctx.defer()
#     x = await check_if_uid_exists(player.id)
#     if x:
#         pass
#     else:
#         await ctx.respond('Player not found')
#         return
#     with DBA.DBAccess() as db:
#         temp = db.query('SELECT is_host_banned FROM player WHERE player_id = %s;', (player.id,))
#     if temp[0][0]:
#         with DBA.DBAccess() as db:
#             db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (0, player.id))
#             await ctx.respond(f'{player.mention} has been un-host-banned')
#     else:
#         with DBA.DBAccess() as db:
#             db.execute("UPDATE player SET is_host_banned = %s WHERE player_id = %s;", (1, player.id))
#             await ctx.respond(f'{player.mention} has been host-banned')

# /zrestrict
@client.slash_command(
    name='zrestrict',
    description='Chat restrict a player [Admin only]',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zrestrict(
    ctx,
    player: discord.Option(str, description='Player name', required=True),
    reason: discord.Option(str, description='Explain why (1000 chars)', required=True),
    ban_length: discord.Option(int, description='# of days', required=True)
    ):
    await ctx.defer()
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return
    user = await GUILD.fetch_member(player_id)
    is_chat_restricted = await check_if_uid_is_chat_restricted(player_id)
    # is chat restricted
    if is_chat_restricted:
        # unrestrict
        with DBA.DBAccess() as db:
            db.execute('UPDATE player SET is_chat_restricted = %s where player_id = %s;', (0, player_id))
        if CHAT_RESTRICTED_ROLE in user.roles:
            await user.remove_roles(CHAT_RESTRICTED_ROLE)
        await ctx.respond(f'<@{player_id}> has been unrestricted')
        return
    else:
        # restrict
        unix_now = await get_unix_time_now()
        unix_ban_length = ban_length * SECONDS_IN_A_DAY
        unban_date = unix_now + unix_ban_length
        with DBA.DBAccess() as db:
            db.execute('UPDATE player SET is_chat_restricted = %s where player_id = %s;', (1, player_id))
        if CHAT_RESTRICTED_ROLE in user.roles:
            pass
        else:
            await user.add_roles(CHAT_RESTRICTED_ROLE)
            await user.send(f'You have been restricted in MK8DX 200cc Lounge for {ban_length} days\nReason: `{reason}`')
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO player_punishment (player_id, punishment_id, reason, admin_id, unban_date) VALUES (%s, %s, %s, %s, %s);', (player_id, 1, reason, ctx.author.id, unban_date))
        except Exception as e:
            await send_raw_to_debug_channel('/zrestrict error - Failed to insert punishment record', e)
        await ctx.respond(f'<@{player_id}> has been restricted')
        return

# /zloungeless
@client.slash_command(
    name='zloungeless',
    description='Apply the loungeless role [Admin only]',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zloungeless(
    ctx, 
    player: discord.Option(str, description='Player name', required=True),
    reason: discord.Option(str, description='Explain why (1000 chars)', required=True),
    ban_length: discord.Option(int, description='# of days', required=True)
    ):
    await ctx.defer()
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return
    user = await GUILD.fetch_member(player_id)
    if LOUNGELESS_ROLE in user.roles:
        await user.remove_roles(LOUNGELESS_ROLE)
        await set_uid_roles(player_id)
        await ctx.respond(f'Loungeless removed from <@{player_id}>')
    else:
        unix_now = await get_unix_time_now()
        unix_ban_length = ban_length * SECONDS_IN_A_DAY
        unban_date = unix_now + unix_ban_length
        await user.add_roles(LOUNGELESS_ROLE)
        await remove_rank_roles_from_uid(player_id)
        await user.send(f'You have been lounge banned in MK8DX 200cc Lounge for {ban_length} days\nReason: `{reason}`')
        try:
            with DBA.DBAccess() as db:
                db.execute('INSERT INTO player_punishment (player_id, punishment_id, reason, admin_id, unban_date) VALUES (%s, %s, %s, %s, %s);', (player_id, 2, reason, ctx.author.id, unban_date))
        except Exception as e:
            await send_raw_to_debug_channel('/zloungeless error - Failed to insert punishment record', e)
        await ctx.respond(f'Loungeless added to <@{player_id}>')

# /zmmr_penalty
@client.slash_command(
    name='zmmr_penalty',
    description='Give a player an MMR penalty, with no strike [Admin only]',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zmmr_penalty(
    ctx,
    player: discord.Option(str, description='Which player?', required=True),
    mmr_penalty: discord.Option(int, description='How much penalty to apply?', required=True)):
    await ctx.defer()
    mmr_penalty = abs(mmr_penalty)
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return
    player_is_placement = await check_if_uid_is_placement(player_id)
    if player_is_placement:
        await ctx.respond('Cannot apply mmr penalty to a placement player')
        return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))
            new_mmr = temp[0][0] - mmr_penalty
            if new_mmr <= 0:
                new_mmr = 1
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (new_mmr, player_id))
        await ctx.respond(f'<@{player_id}> has been given a {mmr_penalty} mmr penalty')
        await set_uid_roles(player_id)
    except Exception as e:
        await send_to_debug_channel(ctx, f'/zmmr_penalty error 38 {e}')
        await ctx.respond('`Error 38:` Could not apply penalty')

# /zsendmsg
@client.slash_command(
    name='zsendmsg',
    description='bot send message here',
    guild_ids=Lounge
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
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zreduce_loss(ctx,
    player: discord.Option(str, description='Player name', required=True),
    mogi_id: discord.Option(int, description='Which mogi?', required=True),
    reduction: discord.Option(str, description='Reduction value', required=True)):
    await ctx.defer()
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
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
            temp = db.query('SELECT mmr_change, prev_mmr FROM player_mogi WHERE player_id = %s AND mogi_id = %s;', (player_id, mogi_id))
            temp2 = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))
            mmr_change = temp[0][0]
            prev_mmr = temp[0][1]
            mmr = temp2[0][0]
    except Exception:
        await ctx.respond('``Error 40:`` tell popuko or try again later')
        return
    reverted_mmr_change = mmr_change * -1 # opposite of mmr_change
    reverted_mmr = mmr + reverted_mmr_change # temp variable
    adjusted_mmr_change = int(math.floor(mmr_change * multiplier)) # mmr change * reduction value
    adjusted_mmr = reverted_mmr + adjusted_mmr_change # player mmr
    adjusted_new_mmr = int(math.floor(prev_mmr + adjusted_mmr_change)) # pm new_mmr
    try:
        with DBA.DBAccess() as db:
            db.execute('UPDATE player_mogi SET mmr_change = %s, new_mmr = %s WHERE player_id = %s AND mogi_id = %s;', (adjusted_mmr_change, adjusted_new_mmr, player_id, mogi_id))
            db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (adjusted_mmr, player_id))
    except Exception as e:
        await send_to_debug_channel(ctx, f'player_name: {player} | mogi id: {mogi_id} | reduction: {reduction} | {e}')
        await ctx.respond('``Error 41:`` FATAL ERROR uh oh uh oh uh oh')
        return
    await set_uid_roles(player_id)
    await ctx.respond(f'Loss was reduced for <@{player_id}>.\nChange: `{mmr_change}` -> `{adjusted_mmr_change}`\nMMR: `{mmr}` -> `{adjusted_mmr}`')
    return

# /zchange_discord_account
@client.slash_command(
    name='zchange_discord_account',
    description='Change a players discord account [Admin only] [Developer mode required]',
    guild_ids=Lounge
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
            db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code, fc, is_host_banned, is_chat_restricted, mmr, base_mmr, peak_mmr, rank_id, times_strike_limit_reached, twitch_link, mogi_media_message_id, unban_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', (new_discord_id, temp[0][1], temp[0][2], temp[0][3], temp[0][4], temp[0][5], temp[0][6], temp[0][7], temp[0][8], temp[0][9], temp[0][10], temp[0][11], temp[0][12], temp[0][13], temp[0][14]))
            # update player_mogi instances
            db.execute('UPDATE player_mogi SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update player_name_request instances
            db.execute('UPDATE player_name_request SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update strike instances
            db.execute('UPDATE strike SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # update sub_leaver instances
            # db.execute('UPDATE sub_leaver SET player_id = %s WHERE player_id = %s;', (new_discord_id, old_discord_id))
            # delete old player
            db.execute('DELETE FROM player WHERE player_id = %s;', (old_discord_id,))
    except Exception as e:
        await send_raw_to_debug_channel('change discord account error', e)
        return
    await ctx.respond(f'Successfully moved player `{old_discord_id}` -> `{new_discord_id}`')
    return

@client.slash_command(
    name='zreload_cogs',
    description='[DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING]',
    guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
async def zreload_cogs(ctx):
    for extension in initial_extensions:
        client.reload_extension(extension)
        await send_raw_to_debug_channel('cog reloaded', extension)
    await ctx.respond('Cogs reloaded successfully')

@client.slash_command(
    name='zset_player_name',
    description='Force a player to a new name',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zset_player_name(ctx,
    player: discord.Option(discord.Member, 'Player', required=True),
    name: discord.Option(str, 'New name', required=True)):
    await ctx.defer()
    y = await check_if_uid_exists(player.id)
    if y:
        pass
    else:
        await ctx.respond('Player does not exist.\nIf you want to change a non-placed players name just use the nickname feature in Discord.')
        return
    x = await check_if_banned_characters(name)
    if x:
        await send_to_verification_log(ctx, name, vlog_msg.error1)
        await ctx.respond('You cannot use this name')
        return
    else:
        pass
    input_name = name
    name = await jp_kr_romanize(name)
    name = name.replace(" ", "-")
    if len(name) > 16:
        await ctx.respond(f'Your request: {input_name} -> {name} | Name is too long. 16 characters max')
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
                db.execute('UPDATE player SET player_name = %s WHERE player_id = %s;', (name, player.id))
        except Exception as e:
            await send_raw_to_debug_channel('Could not force name change...', e)
            await ctx.respond('`Error 77:` Could not force player name change.')
            return
        member = await GUILD.fetch_member(player.id)
        try:
            await member.edit(nick=str(name))
        except Exception as e:
            await send_raw_to_debug_channel('Could not force name change 2...', e)
            await ctx.respond('`Error 78:` Could not force player name change.')
            return
        await ctx.respond(f'Name changed for user: <@{player.id}>')
        return

@client.slash_command(
    name='zmanually_verify_banned_player',
    description='Receive the OK from MKC staff before using this',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zmanually_verify_banned_player(
    ctx,
    player_id: discord.Option(str, 'Player to be verified', required=True),
    message: discord.Option(str, 'MKC Link', required=True)
    ):
    await ctx.defer(ephemeral=True)
    try:
        player_id = int(player_id)
    except Exception as e:
        await ctx.respond('Invalid player_id')
        return
    x = await check_if_uid_exists(player_id)
    if x:
        lounge_ban = await check_if_uid_is_lounge_banned(player_id)
        if lounge_ban:
            await ctx.respond(f'This player is Lounge Banned.\nUnban date: <t:{lounge_ban}:F>')
            return
        else:
            await ctx.respond(f'<@{player_id}> already exists. They should be able to `/verify` their own account.')
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
        elif re.search(regex_pattern2, str(message)):
            regex_group = re.search(regex_pattern2, message)
            x = regex_group.group()
            reg_array = re.split('/', x)
            mkc_player_id = reg_array[len(reg_array)-1]
        else:
            await ctx.respond('``Error 65:`` Oops! Something went wrong. Check your link or try again later')
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
        elif re.search(regex_pattern2, str(message)):
            regex_group = re.search(regex_pattern2, message)
            x = regex_group.group()
            temp = re.split('\.|/', x)
            mkc_player_id = await mkc_request_mkc_player_id(temp[len(temp)-1])
        else:
            # player doesnt exist on forums
            await ctx.respond('``Error 66:`` Oops! Something went wrong. Check your link or try again later')
            return
    else:
        await ctx.respond('``Error 67:`` Oops! Something went wrong. Check your link or try again later')
        return
    # Make sure player_id was received properly
    if mkc_player_id != -1:
        pass
    else:
        await ctx.respond('``Error 68:`` Oops! Something went wrong. Check your link or try again later')
        return
    # Request registry data
    mkc_registry_data = await mkc_request_registry_info(mkc_player_id)
    mkc_user_id = mkc_registry_data[0]
    country_code = mkc_registry_data[1]
    is_banned = mkc_registry_data[2]

    if is_banned == -1:
        # Wrong link probably?
        await ctx.respond('``Error 69:`` Oops! Something went wrong. Check your link or try again later')
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
            await ctx.respond('``Error 70:`` Contact the player you are trying to verify. Have them log into their MKC account, then retry. \n\nIf they are still being refused verification, have them click this link then try again: https://www.mariokartcentral.com/forums/index.php?members/popuko.154/')
            await send_to_verification_log(ctx, message, verify_description)
            return
        else:
            pass
    else:
        verify_description = vlog_msg.error7
        verify_color = discord.Color.red()
        await ctx.respond('``Error 71:`` Oops! Something went wrong. Check your link or try again later')
        await send_to_verification_log(ctx, message, verify_description)
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
        await ctx.respond(f'``Error 72: Duplicate player`` This MKC Link is already in use. ')
        verify_description = vlog_msg.error4
        verify_color = discord.Color.red()
        await send_to_verification_log(ctx, f'<@{player_id}> -> {message}', verify_description)
        return
    else:
        y = await set_uid_chat_restricted(player_id)
        if y:
            pass
        else:
            await ctx.respond(f'Could not assign chat restriction to <@{player_id}>. Abandoning player verification')
            return
        member = await GUILD.fetch_member(player_id)
        x = await create_player(member, mkc_user_id, country_code)
        await ctx.respond(x)
        await send_to_verification_log(ctx, f'<@{player_id}> -> {message}', verify_description)
        return

@client.slash_command(
    name='zset_player_roles',
    description='Check for proper player roles',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zset_player_roles(
    ctx,
    player: discord.Option(discord.Member, '@User', required=True)):
    await ctx.defer()
    response = await set_uid_roles(player.id)
    if response:
        await ctx.respond(f'Player roles set for <@{player.id}>')
        return
    else:
        await ctx.respond(f'`Error 79:` Could not set roles ')
        return

@client.slash_command(
    name='zget_player_info',
    description='Get player DB info',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def zget_player_info(
    ctx,
    name: discord.Option(str, 'Name', required=False),
    discord_id: discord.Option(str, 'Discord ID', required=False)):
    await ctx.defer()

    if discord_id:
        pass
    elif name:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (name,))
            discord_id = temp[0][0]
    else:
        await ctx.respond('You must provide a `name` or `discord_id`')
        return
    try:
        with DBA.DBAccess() as db:
            temp = db.query('''SELECT player_id, player_name, mkc_id, mmr, is_chat_restricted, times_strike_limit_reached 
            FROM player 
            WHERE player_id = %s;''', (discord_id,))
            strike_count = db.query('SELECT count(*) FROM strike WHERE player_id = %s;', (discord_id,))[0][0]
            number_of_punishments = db.query('SELECT count(*) from player_punishment WHERE player_id = %s;', (discord_id,))[0][0]
        await ctx.respond(f'''`discord id`: {temp[0][0]}
`name`: {temp[0][1]}
`mkc_forum_id`: {temp[0][2]}
`mmr`: {temp[0][3]}
`chat restricted`: {'y' if temp[0][4] == 1 else 'n'}
`strike limit reached`: {temp[0][5]} times
`total # of strikes`: {strike_count}
`total # of punishments`: {number_of_punishments}
''')
        return
    except Exception as e:
        await ctx.respond(f'Invalid name or discord ID')
        return

@client.slash_command(
    name='zdelete_player',
    description='ADMIN ONLY [DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING]',
    guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID)
async def zdelete_player(
    ctx,
    discord_id: discord.Option(str, 'Discord ID', required=True)):
    await ctx.defer()
    channel = client.get_channel(ctx.channel.id)
    x = await check_if_uid_exists(discord_id)
    if x:
        pass
    else:
        await ctx.respond('Player does not exist')
        return
    with DBA.DBAccess() as db:
        temp = db.query('select p.player_id, p.player_name, p.mmr, r.rank_name FROM player p JOIN ranks r ON p.rank_id = r.rank_id where player_id = %s;', (discord_id,))
    confirmation = Confirm(ctx.author.id)
    await channel.send(f'Are you sure you want to delete this player?\n<@{discord_id}>\n`Name:`{temp[0][1]}\n`MMR:`{temp[0][2]}\n`Rank:`{temp[0][3]}', view=confirmation, delete_after=300)
    await confirmation.wait()
    if confirmation.value is None:
        await ctx.respond('Timed out...')
        return
    elif confirmation.value: # yes
        with DBA.DBAccess() as db:
            db.execute('DELETE FROM player WHERE player_id = %s;', (discord_id,))
        await ctx.respond('Player deleted successfully')
        return
    else:
        await ctx.respond('Operation cancelled.')
        return

@client.slash_command(
    name='zmanually_verify_player',
    description='manually verify a player (no mkc api checks)',
    guild_ids=Lounge
)
async def zmanually_verify_player(
    ctx, 
    player_id: discord.Option(str, 'Discord ID of player to be verified', required=True),
    mkc_id: discord.Option(str, 'Last numbers in MKC forum link. (e.g. popuko mkc_id = 154)', required=True),
    country_code: discord.Option(str, 'ISO 3166 Alpha-2 Code - https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes', required=True)
    ):
    # mkc_player_id = registry id
    # mkc_user_id = forum id
    await ctx.defer(ephemeral=False)
    x = await check_if_uid_exists(int(player_id))
    if x:
        await ctx.respond('The player id provided is already registered in the Lounge.')
        return
    else:
        pass
    # All clear. Roll out.
    verify_description = vlog_msg.success
    verify_color = discord.Color.green()
    # Check if someone has verified as this user before...
    x = await check_if_mkc_user_id_used(mkc_id)
    if x:
        with DBA.DBAccess() as db:
            uh_oh_player = db.query('SELECT player_id FROM player WHERE mkc_id = %s;', (mkc_id,))[0][0]
        await ctx.respond(f'``Error 82:`` This MKC ID is already in use by {uh_oh_player}')
        verify_description = vlog_msg.error4
        verify_color = discord.Color.red()
        await send_to_verification_log(ctx, f'Error 82: {player_id} | {mkc_id} | {country_code}', f'{verify_description} | <@{x[1]}> already using MKC **FORUM** ID {x[0]}')
        return
    else:
        try:
            member = await GUILD.fetch_member(player_id)
        except Exception as e:
            await ctx.respond(f'Unknown guild member: <@{player_id}>.')
            return
        try:
            x = await create_player(member, mkc_id, country_code)
        except Exception as e:
            await ctx.respond(f'`Error 83:` Database error on create_player. Please create a support ticket and ping <@{secretly.my_discord}>')
            return
        try:
            await ctx.respond(x)
            await send_to_verification_log(ctx, f'{player_id} | {mkc_id} | {country_code}', verify_description)
        except Exception as e:
            await ctx.respond(f'`Error 84:` I was unable to respond and post in log channels for some reason...')
            return
        return

# /zget_player_punishments
@client.slash_command(
    name='zget_player_punishments',
    description='See all punishments for a player',
    guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID)
async def zget_player_punishments(
    ctx,
    name: discord.Option(str, 'Name', required=False),
    discord_id: discord.Option(str, 'Discord ID', required=False)):
    await ctx.defer()
    if discord_id:
        with DBA.DBAccess() as db:
            name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (discord_id,))[0][0]
    elif name:
        with DBA.DBAccess() as db:
            discord_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (name,))[0][0]
    else:
        await ctx.respond('You must provide a `name` or `discord_id`')
        return
    try:
        punishment_string = ''
        channel = client.get_channel(ctx.channel.id)
        await ctx.respond(f"# {name}'s punishments")
        with DBA.DBAccess() as db:
            temp = db.query('SELECT pl.player_name, p.punishment_type, pp.reason, pp.id, pp.unban_date FROM punishment p JOIN player_punishment pp ON p.id = pp.punishment_id JOIN player pl ON pp.admin_id = pl.player_id WHERE pp.player_id = %s;', (discord_id,))
            # dynamic list of punishments
            for punishment in temp:
                punishment_string += f'**{punishment[3]}.** {punishment[1]} - {punishment[2]}\n\n unban: <t:{str(punishment[4])}:F>\n`issued by: {punishment[0]}`\n'
            message_array = wrap(punishment_string, 1000)
        # channel = client.get_channel(ctx.channel.id)
        for message in message_array:
            await channel.send(message)
    except Exception as e:
        await ctx.respond(f'Invalid name or discord ID')
        await send_raw_to_debug_channel('Player punishment retrieval error 1', e)
        return

@client.slash_command(
    name='zadd_mmr',
    description='Add MMR to a player',
    guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID, UPDATER_ROLE_ID)
async def zadd_mmr(
    ctx,
    player: discord.Option(str, 'Player name', required=True),
    mmr: discord.Option(int, 'Amount of MMR to add to the player', required=True)):
    await ctx.defer()
    
    # Check if player exists
    with DBA.DBAccess() as db:
        player_id = db.query('SELECT player_id FROM player WHERE player_name = %s;', (player,))[0][0]
    if player_id:
        pass
    else:
        await ctx.respond('Player not found')
        return
    # Get current MMR of player
    with DBA.DBAccess() as db:
        current_mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (player_id,))[0][0]
    # Calculate new MMR
    new_mmr = current_mmr + mmr
    # Update player record
    with DBA.DBAccess() as db:
        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (new_mmr, player_id))
    await ctx.respond(f'{mmr} MMR added to <@{player_id}>\n`{current_mmr}` -> `{new_mmr}`')
    return


@client.slash_command(
    name='zlog_file',
    description='gimme the log file pls thamks',
    guild_ids=Lounge
)
@commands.has_any_role(ADMIN_ROLE_ID)
async def zlog_file(ctx):
    await ctx.defer()
    await ctx.send(file=discord.File('200lounge.log'))
    await ctx.respond('here u go')
    return





# /qwe
@client.slash_command(
    name='qwe',
    description='qwe',
    guild_ids=Lounge
)
@commands.has_any_role(UPDATER_ROLE_ID, ADMIN_ROLE_ID)
async def qwe(
    ctx,
    player: discord.Option(discord.Member, 'player', required=False)):
    await ctx.defer()
    await ctx.respond('qwe')
    


    # member = await GUILD.fetch_member(uid)
    # await ctx.respond(member.display_name)



















async def remove_rank_roles_from_uid(uid):
    member = await GUILD.fetch_member(uid)
    # Get ranks
    with DBA.DBAccess() as db:
        ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
    # Remove any ranks from member
    for rank in ranks: 
        remove_rank = GUILD.get_role(rank[0])
        await member.remove_roles(remove_rank)

# Takes a uid, returns True for completed. returns False for error
async def set_uid_chat_restricted(uid):
    try:
        member = await GUILD.fetch_member(uid)
        role = GUILD.get_role(CHAT_RESTRICTED_ROLE_ID)
        await member.add_roles(role)
        return True
    except Exception as e:
        await send_raw_to_debug_channel('Could not set uid to chat restricted', uid)
        return False

# Takes a ctx, returns the a response (used in re-verification when reentering lounge)
async def set_uid_roles(uid):
    try:
        # Get player info
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_name, mmr, is_chat_restricted FROM player WHERE player_id = %s;', (uid,))
        player_name = temp[0][0]
        mmr = temp[0][1]
        is_chat_restricted = temp[0][2]
        # Get discord.Guild and discord.Member objects
        guild = client.get_guild(Lounge[0])
        member = await guild.fetch_member(uid)
        # handle chat restricted role
        if is_chat_restricted:
            restricted_role = guild.get_role(CHAT_RESTRICTED_ROLE_ID)
            await member.add_roles(restricted_role)

        if mmr is None:
            # with open('200lounge.csv', 'rt', encoding='utf-8-sig') as f: # f is our filename as string
            #     lines = list(csv.reader(f,delimiter=',')) # lines contains all of the rows from the csv
            #     if len(lines) > 0:
            #         for line in lines:
            #             name = line[0]
            #             if name.lower() == (member.display_name).lower():
            #                 mmr = int(line[2])
            #                 with DBA.DBAccess() as db:
            #                     ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
            #                 for rank in ranks:
            #                     if mmr >= int(rank[1]) and mmr < int(rank[2]):
            #                         role = guild.get_role(rank[0])
            #                         await member.add_roles(role)
            #                         with DBA.DBAccess() as db:
            #                             db.execute('UPDATE player set rank_id = %s, mmr = %s, base_mmr = %s, player_name = %s WHERE player_id = %s;', (rank[0], mmr, mmr, member.id))
            #                         return (role.id, role)
            role = guild.get_role(PLACEMENT_ROLE_ID)
            await member.add_roles(role)
            return (role.id, role)
            
        # Get ranks info
        with DBA.DBAccess() as db:
            ranks = db.query('SELECT rank_id, mmr_min, mmr_max FROM ranks', ())
        # Remove any ranks from player
        for rank in ranks: 
            remove_rank = guild.get_role(rank[0])
            await member.remove_roles(remove_rank)
        # Find their rank, based on MMR
        for i in range(len(ranks)):
            if mmr >= int(ranks[i][1]) and mmr < int(ranks[i][2]):
                # Found your rank
                role = guild.get_role(ranks[i][0])
                await member.add_roles(role)
                with DBA.DBAccess() as db:
                    db.execute('UPDATE player SET rank_id = %s WHERE player_id = %s;', (ranks[i][0], member.id))
        # Edit their discord nickname
        try:
            await member.edit(nick=str(player_name))
        except Exception as e:
            await send_raw_to_debug_channel(f'<@{uid}>', f'CANNOT EDIT NICKNAME OF STAFF MEMBER. I AM BUT A SMOLL ROBOT... {e}')
            pass
        return (role.id, role)
    except IndexError:
        return False
    except Exception as e:
        await send_raw_to_debug_channel(f'<@{uid}>', f'set_uid_roles exception: {e}')
        return False

# Cool&Create
async def create_player(member, mkc_user_id, country_code):
    altered_name = await handle_player_name(member.display_name)
    logging.warning(f'POP_LOG | Finished handling name: {altered_name}')
    try:
        with DBA.DBAccess() as db:
            db.execute('INSERT INTO player (player_id, player_name, mkc_id, country_code, rank_id) VALUES (%s, %s, %s, %s, %s);', (member.id, altered_name, mkc_user_id, country_code, PLACEMENT_ROLE_ID))
    except Exception as e:
        await send_raw_to_debug_channel(f'create_player error 14 <@{member.id}>', {e})
        return f'``Error 14:`` Oops! An unlikely error occured. Try again later or make a <#{secretly.support_channel}> ticket for assistance.'
        # 1. a player trying to use someone elses link (could be banned player)
        # 2. a genuine player locked from usage by another player (banned player might have locked them out)
        # 3. someone is verifying multiple times

    # Edit nickname
    try:
        await member.edit(nick=str(altered_name))
    except Exception as e:
        await send_raw_to_debug_channel(f'create_player error 15 - CANNOT EDIT NICK FOR USER <@{member.id}>', {e})
    role = GUILD.get_role(PLACEMENT_ROLE_ID)
    logging.warning(f'POP_LOG | {altered_name} | Attempted to edit nickname')

    # Add role
    try:
        await member.add_roles(role)
    except Exception as e:
        await send_raw_to_debug_channel(f'create_player error 15 - CANNOT EDIT ROLE FOR USER <@{member.id}>', {e})
    logging.warning(f'POP_LOG | {altered_name} | Attempted to add roles')

    # Confirmation log
    await send_raw_to_verification_log(f'player:<@{member.id}>\nrole:`{role}`\naltered name:`{altered_name}`', '**Creating player**')
    return f':flag_us:\nVerified & registered successfully - Assigned <@&{role.id}>\nNew players - check out <#{secretly.welcome_eng_channel}> & <#{secretly.faq_channel}>\n\n:flag_jp:\n認証に成功しました。{role}が割り当てられました。\n新入会員の方は、<#{secretly.welcome_jpn_channel}>と<#{secretly.faq_channel}> チャンネルをお読みください。'

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

async def convert_datetime_to_unix_timestamp(datetime_object):
    return time.mktime(datetime_object.timetuple())

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

async def check_if_uid_in_any_active_tier(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND can_drop = 0;', (uid,))
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

async def check_if_uid_is_chat_restricted(uid):
    with DBA.DBAccess() as db:
        temp = db.query('SELECT is_chat_restricted FROM player WHERE player_id = %s;', (uid,))
    if temp:
        return temp[0][0]
    else:
        return False

async def check_if_mkc_user_id_used(mkc_user_id):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mkc_id, player_id from player WHERE mkc_id = %s;', (mkc_user_id,))
            if int(temp[0][0]) == int(mkc_user_id):
                # return mkc_id, player_id as list
                return [temp[0][0], temp[0][1]]
            else:
                return False
    except Exception as e:
        # await send_raw_to_debug_channel(mkc_player_id, e)
        return False

async def check_if_player_exists(ctx):
    try:
        with DBA.DBAccess() as db:
            pid = db.query('SELECT player_id FROM player WHERE player_id = %s;', (ctx.author.id, ))[0][0]
            if pid == ctx.author.id:
                return True
            else:
                return False
    except Exception as e:
        # await send_to_debug_channel(ctx, f'check_if_player_exists exception: {e}')
        return False

async def check_if_uid_exists(uid):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_id FROM player WHERE player_id = %s;', (uid,))
            if str(temp[0][0]) == str(uid):
                print(f'{temp[0][0]} = {uid}')
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

async def check_if_uid_is_placement(uid):
    try:
        with DBA.DBAccess() as db:
            mmr = db.query('SELECT mmr FROM player WHERE player_id = %s;', (uid,))[0][0]
        if mmr is None:
            return True
        elif mmr >= 0:
            return False
    except Exception as e:
        await send_raw_to_debug_channel('Check if uid is placement error:', e)
        return True

async def check_if_is_unique_name(name):
    with DBA.DBAccess() as db:
        temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (name,))
    return not temp


async def convert_unix_timestamp_to_datetime(self, unix_timestamp):
    return datetime.datetime.utcfromtimestamp(unix_timestamp)

async def convert_datetime_to_unix_timestamp(self, datetime_object):
    return int((datetime_object - datetime.datetime(1970,1,1, tzinfo=pytz.utc)).total_seconds())


# Returns all rank_id from DB in a list()
async def get_list_of_rank_ids():
    my_list = []
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT rank_id FROM ranks;', ())
        for item in temp:
            my_list.append(item[0])
        return my_list
    except Exception:
        return []

# Returns a random player name that is not taken
async def get_random_name():
    logging.warning('POP_LOG | Retrieving random name...')
    name_is_not_unique = True
    while(name_is_not_unique):
        name = await generate_random_name()
        logging.warning(f'POP_LOG | Generated name: {name}')
        test = await check_if_is_unique_name(name)
        if (test):
            logging.warning(f'POP_LOG | Unique name detected')
            name_is_not_unique = False
    return name

# Generates a random name (wow)
async def generate_random_name():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

# Returns the current unix timestamp
async def get_unix_time_now():
    return time.mktime(datetime.datetime.now().timetuple())

# Returns the number of strikes that a uid has
async def get_number_of_strikes(uid):
    with DBA.DBAccess() as db:
        temp = db.query('SELECT COUNT(*) FROM strike WHERE player_id = %s AND is_active = %s;', (uid, 1))
        if temp[0][0] is None:
            return 0
        else:
            return temp[0][0]

# Takes in uid, returns avg partner score
async def get_partner_avg(uid, number_of_mogis, mogi_format_string, tier_id='%', db_name='s6200lounge'):
    # logging.warning(f'POP_LOG | Partner Avg | uid={uid} | #mogis={number_of_mogis} | format={mogi_format_string} | tier={tier_id}')
    try:
        with DBA2.DBAccess(db_name) as db:
            sql = '''
                SELECT pm.mogi_id, pm.place, pm.mmr_change 
                FROM player_mogi as pm 
                JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                WHERE pm.player_id = %s 
                AND m.mogi_format IN (%s)
                AND tier_id like %s 
                ORDER BY m.create_date DESC LIMIT %s
                '''  % ('%s', mogi_format_string, '%s', '%s')
            debug_temp1 = db.query(sql, (uid, tier_id, number_of_mogis))

            sql = '''
                SELECT pm.player_id, pm.mogi_id, pm.place, pm.score, pm.mmr_change 
                FROM player_mogi as pm 
                INNER JOIN 
                    (SELECT pm.mogi_id, pm.place, pm.mmr_change 
                    FROM player_mogi as pm 
                    JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                    WHERE pm.player_id = %s 
                    AND m.mogi_format IN (%s)
                    AND tier_id like %s 
                    ORDER BY m.create_date DESC LIMIT %s) as pm2 
                ON pm2.mogi_id = pm.mogi_id 
                AND pm2.place = pm.place 
                AND pm.mmr_change = pm2.mmr_change
                WHERE player_id <> %s ''' % ('%s', mogi_format_string, '%s', '%s', '%s')
            debug_temp2 = db.query(sql, (uid, tier_id, number_of_mogis, uid))

            sql = '''
            SELECT AVG(score) 
            FROM 
                (SELECT pm.player_id, pm.mogi_id, pm.place, pm.score, pm.mmr_change 
                FROM player_mogi as pm 
                INNER JOIN 
                    (SELECT pm.mogi_id, pm.place, pm.mmr_change 
                    FROM player_mogi as pm 
                    JOIN mogi as m ON pm.mogi_id = m.mogi_id 
                    WHERE pm.player_id = %s 
                    AND m.mogi_format IN (%s)
                    AND tier_id like %s 
                    ORDER BY m.create_date DESC LIMIT %s) as pm2 
                ON pm2.mogi_id = pm.mogi_id 
                AND pm2.place = pm.place 
                AND pm.mmr_change = pm2.mmr_change
                WHERE player_id <> %s) as a''' % ('%s', mogi_format_string, '%s', '%s', '%s')
            temp = db.query(sql, (uid, tier_id, number_of_mogis, uid))

            try:
                # logging.warning(f'POP_LOG | Partner Avg | SQL Debug 1 returned: {debug_temp1}')
                # logging.warning(f'POP_LOG | Partner Avg | SQL Debug 2 returned: {debug_temp2}')
                # logging.warning(f'POP_LOG | Partner Avg | SQL returned: {temp}')
                return round(float(temp[0][0]), 2)
            except Exception as e:
                logging.warning(f'POP_LOG | Partner Avg | SQL did not return any average')
                return 0
    except Exception as e:
        await send_raw_to_debug_channel('partner average error',e)
    return 0

# Takes in: ctx
# Returns: mmr
async def get_player_mmr(ctx):
    try:
        with DBA.DBAccess() as db:
            temp = db.query('SELECT mmr FROM player WHERE player_id = %s;', (uid,))
    except Exception as e:
        await send_to_debug_channel(ctx, f'get_player_mmr error 1 | {e}')
        return -1
    return temp[0][0]

# Takes in: scores from /table
# Returns: nicely formatted dict-type list thingie...
async def handle_score_input(ctx, score_string, mogi_format):
    # Split into list
    score_list = score_string.split()
    if len(score_list) == 24:
        pass
    else:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`WRONG AMOUNT OF INPUTS:` {len(score_list)}')
        return False
    # Check for player db match
    try:
        for i in range(0, len(score_list), 2):
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM player WHERE player_name = %s;', (score_list[i],))
                # Replace playernames with playerids
                score_list[i] = temp[0][0]
    except Exception:
        channel = client.get_channel(ctx.channel.id)
        await channel.send(f'`PLAYER DOES NOT EXIST:` {score_list[i]}')
        return False
    
    player_score_chunked_list = []
    for i in range(0, len(score_list), 2):
        player_score_chunked_list.append(score_list[i:i+2])
        # print(player_score_chunked_list)


    # Chunk the list into groups of teams, based on mogi_format and order of scores entry
    chunked_list = []
    for i in range(0, len(player_score_chunked_list), mogi_format):
        chunked_list.append(player_score_chunked_list[i:i+mogi_format])
    return chunked_list

async def handle_suggestion_decision(suggestion_id, suggestion, author_id, message_id, admin_id, approved, reason):
    try:
        author = await GUILD.fetch_member(author_id)
    except Exception as e:
        logging.warning(f'Suggestion author {author_id} not in server. Suggestion id [{suggestion_id}] will be deleted. - "{suggestion}"')
        channel = client.get_channel(secretly.suggestion_voting_channel)
        suggestion_message_to_delete = await channel.fetch_message(message_id)
        await suggestion_message_to_delete.delete()
        await channel.send(f'Suggestion author not in server. Suggestion id [{suggestion_id}] will be deleted. - "{suggestion}"')
    admin = await GUILD.fetch_member(admin_id)
    if approved is None:
        return
    channel = client.get_channel(secretly.suggestion_voting_channel)
    if approved:
        decision = f'Approved by {admin.display_name}'
        color = discord.Color.green()
    else:
        decision = f'Denied by {admin.display_name}'
        color = discord.Color.red()
    try:
        embed = discord.Embed(title='Suggestion', description=f'', color = color)
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)


        embed.add_field(name=f'#{suggestion_id}', value=suggestion, inline=False)
        embed.add_field(name=decision, value=reason, inline=False)

        suggestion_message = await channel.fetch_message(message_id)
        await suggestion_message.edit(embed=embed)
        dummy_msg = await channel.send('.')
        await dummy_msg.delete()
        return True
    except Exception as e:
        return False

# Takes in: name string 
# Cleans name
# Returns cleaned name (or a new random name)
async def handle_player_name(name):
    logging.warning(f'POP_LOG | Step 1 - Handling name: [{name}]')
    insert_name = ""
    # Romanize the text
    insert_name = await jp_kr_romanize(str(name))
    logging.warning(f'POP_LOG | Step 2 - romanized name: [{insert_name}]')

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
    logging.warning(f'POP_LOG | Step 3 - checked length: [{insert_name}]')

    # Handle ä-type characters (delete them)
    allowed_name = ""
    for char in insert_name:
        if char.lower() in ALLOWED_CHARACTERS:
            allowed_name += char
        else:
            allowed_name += ""
    logging.warning(f'POP_LOG | Step 4 - handled chars: [{allowed_name}]')
    insert_name = allowed_name

    # Handle empty name
    if not insert_name:
        insert_name = await get_random_name()
    logging.warning(f'POP_LOG | Step 5 - handled empty: [{insert_name}]')

    # Handle whitespace name  - generate a random name lol
    if insert_name.isspace():
        insert_name = await get_random_name()
    logging.warning(f'POP_LOG | Step 6 - handled whitespace: [{insert_name}]')
        
    # Handle duplicate names - append underscores
    name_still_exists = True
    count = 0
    while(name_still_exists):
        with DBA.DBAccess() as db:
            temp = db.query('SELECT player_name FROM player WHERE player_name = %s;', (insert_name,))
        if temp:
            insert_name += "_"
        else:
            name_still_exists = False
        count +=1
        if count == 16:
            insert_name = await get_random_name()
    logging.warning(f'POP_LOG | Step 7 - handled duplicates: [{insert_name}]')

    return str(insert_name).replace(" ", "-")

# Takes in: Player object (discord_id, score), their mmr, their score, and the tier name
# Determines what rank to place a player
# Updates DB records
# Assigns rank role
# Accounts for queued penalties
# Returns: the name of their rank role, new mmr value
async def handle_placement_init(player, my_player_mmr, my_player_score, tier_name, results_channel):
    logging.warning(f'POP_LOG | handle_placement_init: {player} | {my_player_mmr} | {my_player_score} | {tier_name}')
    placement_name = ''

    if tier_name == 'tier-c':
        if my_player_score >=120:
            my_player_mmr = 5250
            placement_name = 'Gold'
        elif my_player_score >= 90:
            my_player_mmr = 3750
            placement_name = 'Silver'
        elif my_player_score >= 60:
            my_player_mmr = 2250
            placement_name = 'Bronze'
        else:
            my_player_mmr = 1000
            placement_name = 'Iron'
    else:
        if my_player_score >=110:
            my_player_mmr = 5250
            placement_name = 'Gold'
        elif my_player_score >= 80:
            my_player_mmr = 3750
            placement_name = 'Silver'
        elif my_player_score >= 50:
            my_player_mmr = 2250
            placement_name = 'Bronze'
        else:
            my_player_mmr = 1000
            placement_name = 'Iron'

    # Initial MMR assignment
    with DBA.DBAccess() as db:
        init_rank = db.query('SELECT rank_id FROM ranks WHERE placement_mmr = %s;', (my_player_mmr,))[0][0]
        db.execute('UPDATE player SET base_mmr = %s, rank_id = %s WHERE player_id = %s;', (my_player_mmr, init_rank, player[0]))
    
    # Assign rank role
    try:
        discord_member = await GUILD.fetch_member(player[0])
        init_role = GUILD.get_role(init_rank)
        placement_role = GUILD.get_role(PLACEMENT_ROLE_ID)
        await discord_member.add_roles(init_role)
        await discord_member.remove_roles(placement_role)
        await results_channel.send(f'<@{player[0]}> has been placed at {placement_name} ({my_player_mmr} MMR)')
    except Exception as e:
        await send_raw_to_debug_channel(f'<@{player[0]}> did not stick around long enough to be placed',e)

    # Potential accumulated MMR penalties
    try:
        total_queued_mmr_penalty, my_player_new_queued_strike_adjusted_mmr = await handle_queued_mmr_penalties(player[0], my_player_mmr)
        # disclosure
        if total_queued_mmr_penalty == 0:
            pass
        else:
            await results_channel.send(f'<@{player[0]}> accumulated {total_queued_mmr_penalty} worth of MMR penalties during placement.\nMMR adjustment: ({my_player_mmr} -> {my_player_new_queued_strike_adjusted_mmr})')
    except Exception as e:
        await send_raw_to_debug_channel(f'Potential accumulated penalties error for player: {player[0]}', e)
    
    return placement_name, my_player_new_queued_strike_adjusted_mmr

# Takes in: player_id and that player's current MMR
# Returns: total penalty, and new adjusted mmr value
async def handle_queued_mmr_penalties(player_id, my_player_mmr):
    # Get all records with penalty not applied
    with DBA.DBAccess() as db:
        total_queued_mmr_penalty = db.query('SELECT sum(mmr_penalty) FROM strike WHERE penalty_applied = %s AND player_id = %s;', (0, player_id))[0][0]

    if total_queued_mmr_penalty is None:
        return 0, my_player_mmr

    my_player_new_queued_strike_adjusted_mmr = my_player_mmr - total_queued_mmr_penalty

    # Update players mmr
    with DBA.DBAccess() as db:
        db.execute('UPDATE player SET mmr = %s WHERE player_id = %s;', (my_player_new_queued_strike_adjusted_mmr, player_id))

    # Strike penalty applied = True
    with DBA.DBAccess() as db:
        db.execute('UPDATE strike SET penalty_applied = %s WHERE player_id = %s;', (1, player_id))

    return total_queued_mmr_penalty, my_player_new_queued_strike_adjusted_mmr

# Takes in: string
# Returns: romanized jp/kr string
async def jp_kr_romanize(input):
    r = Romanizer(input)
    kr_result = r.romanize()
    kks = pykakasi.kakasi()
    result = kks.convert(kr_result)
    my_string = ""
    for item in result:
        my_string+=item['hepburn']
    return my_string

# Somebody did a bad
# ctx | message | discord.Color.red() | my custom message
async def send_to_verification_log(ctx, message, verify_description):
    channel = client.get_channel(secretly.verification_channel)
    await channel.send(f'{verify_description}\n{ctx.author.id} | {ctx.author.mention}\n{message}')

async def send_raw_to_verification_log(message, verify_description):
    channel = client.get_channel(secretly.verification_channel)
    await channel.send(f'{verify_description}\n{message}')

async def send_to_debug_channel(ctx, error):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Debug', description='>.<', color = discord.Color.blurple())
    embed.add_field(name='Issuer: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Error: ', value=str(error), inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)

async def send_to_danger_debug_channel(ctx, message, verify_color, verify_description):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Debug DANGER:', description=verify_description, color = verify_color)
    embed.add_field(name='Name: ', value=ctx.author.mention, inline=False)
    embed.add_field(name='Message: ', value=message, inline=False)
    embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
    await channel.send(content=None, embed=embed)
    await channel.send(f'{secretly.my_discord}')

async def send_raw_to_debug_channel(anything, error):
    channel = client.get_channel(secretly.debug_channel)
    embed = discord.Embed(title='Debug', description='>.<', color = discord.Color.yellow())
    embed.add_field(name='Details: ', value=anything, inline=False)
    embed.add_field(name='Traceback: ', value=str(error), inline=False)
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
    try:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    except Exception:
        pass
    x = await channel.send(content=None, embed=embed)
    return x

async def send_to_suggestion_voting_channel(ctx, suggestion_id, message):
    channel = client.get_channel(secretly.suggestion_voting_channel)
    embed = discord.Embed(title='Suggestion', description=f'', color = discord.Color.blurple())
    embed.add_field(name=f'#{suggestion_id}', value=message, inline=False)
    try:
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    except Exception:
        embed.set_author(name=ctx.author.display_name)
    x = await channel.send(content=None, embed=embed)
    return x

async def send_to_suggestion_log_channel(ctx, suggestion_id, message, decision, author_id, admin_id, reason):
    channel = client.get_channel(secretly.suggestion_log_channel)
    member = GUILD.get_member(author_id)
    if decision:
        embed = discord.Embed(title=f'Suggestion #{suggestion_id} Approved', description=f'', color=discord.Color.green())
    else:
        embed = discord.Embed(title=f'Suggestion #{suggestion_id} Denied', description=f'', color=discord.Color.red())
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name='----------', value=message, inline=False)
    embed.add_field(name=f'Reason from {ctx.author.display_name}', value=reason)
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
 
# Requests & async requests

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
    return (f'<span foreground="BlueViolet">{input}</span>')

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

# old crap below...










# # /c
# @client.slash_command(
#     name='c',
#     description='🙋 Can up for a mogi',
#     guild_ids=Lounge
# )
# @commands.cooldown(1, 3, commands.BucketType.user)
# async def c(
#     ctx,
#     ):
#     await ctx.defer(ephemeral=True)
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
#         return
#     else:
#         pass

#     # Get the current lineup count - only players that were not in the last mogi (mogi_start_time not null)
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s AND mogi_start_time is NULL;', (ctx.channel.id,))
#             count = temp[0][0]
#     except Exception as e:
#         await ctx.respond(f'``Error 18:`` Something went VERY wrong! Please contact {secretly.my_discord}.')
#         await send_to_debug_channel(ctx, f'/c error 18 lineup not found? {e}')
#         return
#     # await send_to_debug_channel(ctx, f'count: {count}')

#     # ADDITIONAL SUBS SHOULD BE ABLE TO JOIN NEXT MOGI
#     # if count == MAX_PLAYERS_IN_MOGI:
#     #     await ctx.respond('Mogi is full')
#     #     return

#     # Check for canning in same tier
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
#         if temp:
#             if temp[0][0] == ctx.author.id:
#                 await ctx.respond('You are already in the mogi')
#                 return
#             else:
#                 pass
#     except Exception as e:
#         pass
#         # await ctx.respond(f'``Error 46:`` Something went wrong! Contact {secretly.my_discord}.')
#         # await send_to_debug_channel(ctx, e)
#         # return
    
#     # Check for squad queue channel
#     if ctx.channel.id == secretly.squad_queue_channel:
#         await ctx.respond('Use !c to join squad queue')
#         return
    
#     if ctx.channel.id in TIER_ID_LIST:
#         pass
#     else:
#         tiers = ''
#         for i in TIER_ID_LIST:
#             if i == secretly.squad_queue_channel:
#                 continue
#             tiers += f'<#{i}> '
#         await ctx.respond(f'`/c` only works in tier channels.\n\n{tiers}')
#         return

#     # Add player to lineup
#     try:
#         with DBA.DBAccess() as db:
#             db.execute('INSERT INTO lineups (player_id, tier_id, last_active) values (%s, %s, %s);', (ctx.author.id, ctx.channel.id, datetime.datetime.now()))
#     except Exception as e:
#         await ctx.respond(f'``Error 16:`` Player not registered.\nTry `/verify`.')
#         # await send_to_debug_channel(ctx, f'/c error 16 unable to join {e}')
#         return
#     await ctx.respond('You have joined the mogi! You can /d in `15 seconds`')
#     channel = client.get_channel(ctx.channel.id)
#     await channel.send(f'{ctx.author.display_name} has joined the mogi!', delete_after=300)
#     count+=1
#     # Check for full lineup
#     if count == MAX_PLAYERS_IN_MOGI:
#         # start the mogi, vote on format, create teams
#         mogi_started_successfully = await start_mogi(ctx)
#         if mogi_started_successfully == 1:
#             pass
#             # Chooses a host. Says the start time
#         elif mogi_started_successfully == 0:
#             channel = client.get_channel(ctx.channel.id)
#             await channel.send(f'``Error 45:`` Failed to start mogi. {secretly.my_discord}!!!!!!!!!!!!')
#             return
#         elif mogi_started_successfully == 2:
#             channel = client.get_channel(ctx.channel.id)
#             await channel.send(f'``Error 54:`` Failed to start mogi. {secretly.my_discord}!!!!!!!!!!!!!!')
#             return
#     elif count == 6 or count == 11:
#         channel = client.get_channel(ctx.channel.id)
#         await channel.send(f'@here +{12-count}')
#     return

# # /d
# @client.slash_command(
#     name='d',
#     description='Drop from the mogi',
#     guild_ids=Lounge
# )
# async def d(
#     ctx,
#     ):
#     await ctx.defer(ephemeral=True)
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
#         return
#     else:
#         pass

#     # does not matter. can wherever whenever
#     # Player was already in lineup, got subbed out
#     # with DBA.DBAccess() as db:
#     #     temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (ctx.author.id,))
#     #     if temp:
#     #         if temp[0][0] == ctx.author.id:
#     #             await ctx.respond('Please wait for the mogi you left to finish')
#     #             return
#     #     else:
#     #         pass
#     x = await check_if_uid_in_specific_tier(ctx.author.id, ctx.channel.id)
#     if x:
#         y = await check_if_uid_can_drop(ctx.author.id)
#         if y:
#             pass
#         else:
#             await ctx.respond('You cannot drop from an ongoing mogi')
#             return
#         # No try block - check is above...
#         with DBA.DBAccess() as db:
#             tier_temp = db.query('SELECT t.tier_id, t.tier_name FROM tier as t JOIN lineups as l ON t.tier_id = l.tier_id WHERE player_id = %s AND t.tier_id = %s;', (ctx.author.id, ctx.channel.id))
#         try:
#             with DBA.DBAccess() as db:
#                 db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (ctx.author.id, ctx.channel.id))
#                 await ctx.respond(f'You have dropped from tier {tier_temp[0][1]}')
#         except Exception as e:
#             await send_to_debug_channel(ctx, f'/d error 17 cant leave lineup {e}')
#             await ctx.respond(f'``Error 17:`` Oops! Something went wrong. Contact {secretly.my_discord}')
#             return
#         try:
#             with DBA.DBAccess() as db:
#                 temp = db.query('SELECT player_name FROM player WHERE player_id = %s;', (ctx.author.id,))
#                 channel = client.get_channel(tier_temp[0][0])
#                 await channel.send(f'{temp[0][0]} has dropped from the lineup')
#         except Exception as e:
#             await send_to_debug_channel(ctx, f'/d big error...WHAT! 1 {e}')
#             # i should never ever see this...
#         return
#     else:
#         await ctx.respond('You are not in a mogi')
#         return

# # /l
# @client.slash_command(
#     name='l',
#     description='Show the mogi list',
#     guild_ids=Lounge
# )
# # @commands.command(aliases=['list'])
# @commands.cooldown(1, 30, commands.BucketType.user)
# async def l(
#     ctx
#     ):
#     await ctx.defer()
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#         return
#     else:
#         pass
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query("SELECT p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC;", (ctx.channel.id,))
#     except Exception as e:
#         await ctx.respond(f'``Error 20:`` Oops! Something went wrong. Please contact {secretly.my_discord}')
#         return
#     response = '`Mogi List`:'
#     for i in range(len(temp)):
#         response = f'{response}\n`{i+1}.` {temp[i][0]}'
#     response = f'{response}\n\n\nYou can type `/l` again in 30 seconds'
#     await ctx.respond(response, delete_after=30)
#     return

# # /esn
# @client.slash_command(
#     name='esn',
#     description='End (mogi) Start New (mogi)',
#     guild_ids=Lounge
# )
# async def esn(ctx):
#     await ctx.defer()
#     # Delete player records in this tier where they already played mogi (mogi_start_time not null)
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT UNIX_TIMESTAMP(mogi_start_time) FROM lineups WHERE tier_id = %s AND can_drop = 0 ORDER BY create_date DESC LIMIT %s;', (ctx.channel.id, 1))
#         mogi_start_time = temp[0][0]
#     except Exception as e:
#         # await send_to_debug_channel(ctx, f'esn error 1: {e}')
#         await ctx.respond('`Error 62:` Mogi has not started')
#         return
#     unix_now = await get_unix_time_now()
#     minutes_since_start = math.floor((unix_now - mogi_start_time)/60)
#     if minutes_since_start > 25:
#         pass
#     else:
#         await ctx.respond(f'Please wait {25 - minutes_since_start} more minutes to use `/esn`')
#         return
#     try:
#         with DBA.DBAccess() as db:
#             players = db.query('SELECT player_id FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
#         print(players)
#         for player in players:
#             with DBA.DBAccess() as db:
#                 db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (player[0], ctx.channel.id))
#         await ctx.respond('New mogi started')
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'esn error 2: {e}')
#         await ctx.respond('`Error 63:` esners')
#         return
#     # await ctx.respond('`/esn`@here - New mogi started')

#     # try:
#     #     with DBA.DBAccess() as db:
#     #         temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
#     #     if len(temp) == 12:
#     #         pass
#     #     else:
#     #         await ctx.respond('There is no mogi being played in this tier.')
#     #         return
#     # except Exception as e:
#     #     await send_to_debug_channel(ctx, f'Cancel Error Check: {e}')
#     #     return
#     # # Delete from lineups & sub_leaver
#     # try:
#     #     with DBA.DBAccess() as db:
#     #         db.execute('DELETE FROM lineups WHERE tier_id = %s AND can_drop = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
#     #         # db.execute('DELETE FROM sub_leaver WHERE tier_id = %s;', (ctx.channel.id,))
#     #     await ctx.respond('The mogi has been cancelled')
#     # except Exception as e:
#     #     await send_to_debug_channel(ctx, f'Cancel Error Deletion:{e}')
#     #     return

# @client.slash_command(
#     name='votes',
#     description='See the current votes',
#     guild_ids=Lounge
# )
# async def votes(ctx):
#     await ctx.defer()
#     is_ongoing = await check_if_mogi_is_ongoing(ctx)
#     if is_ongoing:
#         pass
#     else:
#         await ctx.respond('The vote has not started.')
#         return
#     vote_dict = {}
#     return_string = ""
#     remove_chars = {
#         39:None, # '
#         91:None, # [
#         93:None, # ]
#     }
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT p.player_name, l.vote FROM player as p JOIN lineups as l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#         # print(f'temp: {temp}')
#         vote_dict = {1:[],2:[],3:[],4:[],6:[]}
#         for player in temp:
#             # print(player)
#             if player[1] in vote_dict:
#                 vote_dict[player[1]].append(player[0])
#             else:
#                 vote_dict[player[1]] = [player[0]]
#         return_string = f'`FFA:` {vote_dict[1]}\n`2v2:` {vote_dict[2]}\n`3v3:` {vote_dict[3]}\n`4v4:` {vote_dict[4]}\n`6v6:` {vote_dict[6]}'
#         return_string = return_string.translate(remove_chars)
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'/votes | {e}')
#         await ctx.respond('`Error 64:` Could not retrieve the votes')
#     await ctx.respond(return_string)

# # /fc
# @client.slash_command(
#     name='fc',
#     description='Display or set your friend code',
#     # guild_ids=Lounge
# )
# async def fc(
#     ctx,
#     fc: discord.Option(str, 'XXXX-XXXX-XXXX', required=False)):
#     if fc == None:
#         await ctx.defer()
#         lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#         if lounge_ban:
#             await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#             return
#         else:
#             pass
#         try:
#             with DBA.DBAccess() as db:
#                 temp = db.query('SELECT fc FROM player WHERE player_id = %s;', (ctx.author.id, ))
#                 await ctx.respond(temp[0][0])
#         except Exception as e:
#             await ctx.respond('``Error 12:`` No friend code found. Use ``/fc XXXX-XXXX-XXXX`` to set.')
#     else:
#         await ctx.defer(ephemeral=True)
#         lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#         if lounge_ban:
#             await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#             return
#         else:
#             pass
#         y = await check_if_banned_characters(fc)
#         if y:
#             await send_to_verification_log(ctx, fc, vlog_msg.error1)
#             return '``Error 13:`` Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'
#         x = await check_if_player_exists(ctx)
#         if x:
#             pass
#         else:
#             return '``Error 25:`` Player does not exist. Use `/verify <mkc link>` to register with the Lounge.'
#         confirmation_msg = await update_friend_code(ctx, fc)
#         await ctx.respond(confirmation_msg)

# # /twitch
# @client.slash_command(
#     name='twitch',
#     description='Link your Twitch stream - Enter your Username',
#     #guild_ids=Lounge
# )
# async def twitch(
#     ctx,
#     username: discord.Option(str, 'Enter your twitch username - your mogi streams will appear in the media channel', required=True)
#     ):
#     await ctx.defer(ephemeral=True)
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>')
#         return
#     else:
#         pass
#     x = await check_if_player_exists(ctx)
#     if x:
#         pass
#     else:
#         await ctx.respond('Use `/verify` to register with Lounge')
#         return
#     y = await check_if_banned_characters(username)
#     if y:
#         await ctx.respond("Invalid twitch username")
#         await send_to_verification_log(ctx, username, vlog_msg.error1)
#         return
#     if len(str(username)) > 25:
#         await ctx.respond("Invalid twitch username")
#         return
#     try:
#         with DBA.DBAccess() as db:
#             db.execute("UPDATE player SET twitch_link = %s WHERE player_id = %s;", (str(username), ctx.author.id))
#             await ctx.respond("Twitch username updated.")
#     except Exception:
#         await ctx.respond("``Error 33:`` Player not found. Use ``/verify <mkc link>`` to register with Lounge")

# # /teams
# @client.slash_command(
#     name='teams',
#     description='See the teams in the ongoing mogi',
#     guild_ids=Lounge
# )
# async def teams(ctx):
#     await ctx.defer()
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#         return
#     else:
#         pass
#     x = await check_if_mogi_is_ongoing(ctx)
#     if x:
#         pass
#     else:
#         await ctx.respond('There is no ongoing mogi')
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
#             if temp:
#                 response = temp[0][0]
#             else:
#                 response = "Use `/teams` in a tier channel"
#     except Exception as e:
#         response = "Use `/teams` in a tier channel"
#     await ctx.respond(response)



























# # Takes a ctx & a string, returns a response
# async def update_friend_code(ctx, message):
#     fc_pattern = '\d\d\d\d-?\d\d\d\d-?\d\d\d\d'
#     if re.search(fc_pattern, message):
#         try:
#             with DBA.DBAccess() as db:
#                 db.execute('UPDATE player SET fc = %s WHERE player_id = %s;', (message, ctx.author.id))
#                 return 'Friend Code updated'
#         except Exception as e:
#             await send_to_debug_channel(ctx, f'update_friend_code error 15 {e}')
#             return '``Error 15:`` Player not found'
#     else:
#         return 'Invalid fc. Use ``/fc XXXX-XXXX-XXXX``'



# # Takes a ctx, returns 0 if error, returns 1 if good, returns nothing if mogi cancelled
# async def start_mogi(ctx):
#     channel = client.get_channel(ctx.channel.id)
#     removal_passed = await remove_players_from_other_tiers(ctx.channel.id)
#     if removal_passed:
#         pass
#     else:
#         await send_to_debug_channel(ctx, 'Failed to remove all players from other lineups...')
#         return 0
#     # Set the tier to the voting state
#     try:
#         with DBA.DBAccess() as db:
#             db.execute('UPDATE tier SET voting = 1 WHERE tier_id = %s;', (ctx.channel.id,))
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 1 | {e}')
#         await channel.send(f'`Error 23:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
#         return 0
#     # Initialize the mogi timer, for mogilist checker minutes since start...
#     try:
#         with DBA.DBAccess() as db:
#             db.execute('UPDATE lineups SET mogi_start_time = %s WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12;', (datetime.datetime.now(), ctx.channel.id))
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 4 | {e}')
#         await channel.send(f'`Error 23.2:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
#         return 0
#     # Get the first 12 players
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 2 | {e}')
#         await channel.send(f'`Error 22:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
#         return 0
#     # Set 12 players' state to "cannot drop"
#     try:
#         with DBA.DBAccess() as db:
#             db.execute('UPDATE lineups SET can_drop = 0 WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'start_mogi cannot start format vote | 3 | {e}')
#         await channel.send(f'`Error 55:` Could not start the format vote. Contact the admins or {secretly.my_discord} immediately')
#         return 0
#     response = ''
#     for i in range(len(temp)):
#         response = f'{response} <@{temp[i][0]}>'
#     response = f'''{response} mogi has 12 players\n`Poll Started!`

#     `1.` FFA
#     `2.` 2v2
#     `3.` 3v3
#     `4.` 4v4
#     `6.` 6v6

#     Type a number to vote!
#     Poll ends in 2 minutes or when a format reaches 6 votes.'''
#     await channel.send(response)
#     with DBA.DBAccess() as db:
#         unix_temp = db.query('SELECT UNIX_TIMESTAMP(create_date) FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     # returns the index of the voted on format, and a dictionary of format:voters
#     poll_results = await check_for_poll_results(ctx, unix_temp[MAX_PLAYERS_IN_MOGI-1][0])
#     if poll_results[0] == -1:
#         # Cancel Mogi
#         await channel.send('No votes. Mogi will be cancelled.')
#         await cancel_mogi(ctx)
#         return 2
        
#     teams_results = await create_teams(ctx, poll_results)

#     ffa_voters = list()
#     v2_voters = list()
#     v3_voters = list()
#     v4_voters = list()
#     v6_voters = list()
#     # create formatted message
#     for player in poll_results[1]['FFA']:
#         ffa_voters.append(player)
#     for player in poll_results[1]['2v2']:
#         v2_voters.append(player)
#     for player in poll_results[1]['3v3']:
#         v3_voters.append(player)
#     for player in poll_results[1]['4v4']:
#         v4_voters.append(player)
#     for player in poll_results[1]['6v6']:
#         v6_voters.append(player)
#     remove_chars = {
#         39:None,
#         91:None,
#         93:None,
#     }
#     poll_results_response = f'''`Poll Ended!`

#     `1.` FFA - {len(ffa_voters)} ({str(ffa_voters).translate(remove_chars)})
#     `2.` 2v2 - {len(v2_voters)} ({str(v2_voters).translate(remove_chars)})
#     `3.` 3v3 - {len(v3_voters)} ({str(v3_voters).translate(remove_chars)})
#     `4.` 4v4 - {len(v4_voters)} ({str(v4_voters).translate(remove_chars)})
#     `6.` 6v6 - {len(v6_voters)} ({str(v6_voters).translate(remove_chars)})
#     {teams_results}
#     '''
#     await channel.send(poll_results_response)
#     return 1
















# async def cancel_mogi(ctx):
#     # Delete player records for first 12 in lineups table
#     with DBA.DBAccess() as db:
#         db.execute('DELETE FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     return



# # When the voting starts - constantly check for player input
# async def check_for_poll_results(ctx, last_joiner_unix_timestamp):
#     # print('checking for poll results')
#     dtobject_now = datetime.datetime.now()
#     unix_now = time.mktime(dtobject_now.timetuple())
#     format_list = [0,0,0,0,0]
#     while (unix_now - last_joiner_unix_timestamp) < 120:
#         # Votes are updated in the on_message event, if mogi is running and player is in tier
#         await asyncio.sleep(0.5)
#         with DBA.DBAccess() as db:
#             ffa_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,1))
#             format_list[0] = ffa_temp[0][0]
#         with DBA.DBAccess() as db:
#             v2_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,2))
#             format_list[1] = v2_temp[0][0]
#         with DBA.DBAccess() as db:
#             v3_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,3))
#             format_list[2] = v3_temp[0][0]
#         with DBA.DBAccess() as db:
#             v4_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,4))
#             format_list[3] = v4_temp[0][0]
#         with DBA.DBAccess() as db:
#             v6_temp = db.query('SELECT COUNT(vote) FROM lineups WHERE tier_id = %s AND vote = %s;', (ctx.channel.id,6))
#             format_list[4] = v6_temp[0][0]
#         if 6 in format_list:
#             break
#         # print(f'{unix_now} - {last_joiner_unix_timestamp}')
#         dtobject_now = datetime.datetime.now()
#         unix_now = time.mktime(dtobject_now.timetuple())
#     # print('checking for all zero votes')
#     # print(f'format list: {format_list}')
#     if all([v == 0 for v in format_list]):
#         return [0, { '0': 0 }] # If all zeros, return 0. cancel mogi
#     # Close the voting
#     # print('closing the voting')
#     with DBA.DBAccess() as db:
#         db.execute('UPDATE tier SET voting = %s WHERE tier_id = %s;', (0, ctx.channel.id))
#     if format_list[0] == 6:
#         ind = 0
#     elif format_list[1] == 6:
#         ind = 1
#     elif format_list[2] == 6:
#         ind = 2
#     elif format_list[3] == 6:
#         ind = 3
#     elif format_list[4] == 6:
#         ind = 4
#     else:
#         # Get the index of the voted on format
#         max_val = max(format_list)
#         ind = [i for i, v in enumerate(format_list) if v == max_val]

#     # Create a dictionary where key=format, value=list of players who voted
#     poll_dictionary = {
#         "FFA":[],
#         "2v2":[],
#         "3v3":[],
#         "4v4":[],
#         "6v6":[],
#     }
#     with DBA.DBAccess() as db:
#         votes_temp = db.query('SELECT l.vote, p.player_name FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     for i in range(len(votes_temp)):
#         # print(f'votes temp: {votes_temp}')
#         if votes_temp[i][0] == 1:
#             player_format_choice = 'FFA'
#         elif votes_temp[i][0] == 2:
#             player_format_choice = '2v2'
#         elif votes_temp[i][0] == 3:
#             player_format_choice = '3v3'
#         elif votes_temp[i][0] == 4:
#             player_format_choice = '4v4'
#         elif votes_temp[i][0] == 6:
#             player_format_choice = '6v6'
#         else:
#             continue
#         poll_dictionary[player_format_choice].append(votes_temp[i][1])
#     # print('created poll dictionary')
#     # print(f'{poll_dictionary}')
#     # Clear votes after we dont need them anymore...
#     # print('clearing votes...')
#     with DBA.DBAccess() as db:
#         db.execute('UPDATE lineups SET vote = NULL WHERE tier_id = %s;', (ctx.channel.id,))
#     # I use random.choice to account for ties
#     try:
#         return [random.choice(ind), poll_dictionary]
#     except TypeError:
#         return [ind, poll_dictionary]

# async def remove_players_from_other_tiers(channel_id):
#     await send_raw_to_debug_channel('Removing players from other tiers...', channel_id)
#     try:
#         with DBA.DBAccess() as db:
#             players = db.query('SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC;', (channel_id,))
#     except Exception as e:
#         await send_raw_to_debug_channel('No players to remove from other tiers?', e)
#         return True
#     for player in players:
#         with DBA.DBAccess() as db:
#             player_tier = db.query('SELECT p.player_id, p.player_name, l.tier_id FROM lineups as l JOIN player as p ON l.player_id = p.player_id WHERE p.player_id = %s AND l.tier_id <> %s;', (player[0], channel_id))
#         for tier in player_tier:
#             await send_raw_to_debug_channel('Removing from other tiers', f'{tier[1]} - {tier[2]}')
#             channel = client.get_channel(tier[2])
#             with DBA.DBAccess() as db:
#                 db.execute('DELETE FROM lineups WHERE player_id = %s AND tier_id = %s;', (tier[0], tier[2]))
#             await channel.send(f'{tier[1]} has dropped from the lineup')
#     return True

# # poll_results is [index of the voted on format, a dictionary of format:voters]
# # creates teams, finds host, returns a big string formatted...
# async def create_teams(ctx, poll_results):
#     # print('creating teams')
#     keys_list = list(poll_results[1])
#     winning_format = keys_list[poll_results[0]]
#     # print(f'winning format: {winning_format}')
#     players_per_team = 0
#     if winning_format == 'FFA':
#         players_per_team = 1
#     elif winning_format == '2v2':
#         players_per_team = 2
#     elif winning_format == '3v3':
#         players_per_team = 3
#     elif winning_format == '4v4':
#         players_per_team = 4
#     elif winning_format == '6v6':
#         players_per_team = 6
#     else:
#         return 0
#     response_string=f'`Winner:` {winning_format}\n\n'
#     with DBA.DBAccess() as db:
#         player_db = db.query('SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#     players_list = list()
#     room_mmr = 0
#     for i in range(len(player_db)):
#         players_list.append([player_db[i][0], player_db[i][1], player_db[i][2]])
#         if player_db[i][2] is None: # Account for placement ppls
#             pass
#         else:
#             room_mmr = room_mmr + player_db[i][2]
#     random.shuffle(players_list) # [[popuko, 7238965417831, 4000],[name, discord id, mmr]]
#     room_mmr = room_mmr/MAX_PLAYERS_IN_MOGI
#     response_string += f'   `Room MMR:` {math.ceil(room_mmr)}\n'
#     # 6v6 /teams string
#     if players_per_team != 6:
#         # divide the list based on players_per_team
#         chunked_list = list()
#         for i in range(0, len(players_list), players_per_team):
#             chunked_list.append(players_list[i:i+players_per_team])

#         # For each divided team, get mmr for all players, average them, append to team
#         for team in chunked_list:
#             temp_mmr = 0
#             count = 0
#             for player in team:
#                 if player[2] is None: # If mmr is null - Account for placement ppls
#                     count+=1
#                     #pass - commented out and added count+=1 10/10/22 because people mad about playing with placements even tho its 200 and its tier all lol
#                 else:
#                     temp_mmr = temp_mmr + player[2]
#                     count += 1
#             if count == 0:
#                 count = 1
#             team_mmr = temp_mmr/count
#             team.append(team_mmr)

#         sorted_list = sorted(chunked_list, key = lambda x: int(x[len(chunked_list[0])-1]))
#         sorted_list.reverse()
#         # print(sorted_list)
#         player_score_string = f'    `Table:` /table {players_per_team} '
#         team_count = 0
#         for team in sorted_list:
#             team_count+=1
#             response_string += f'   `Team {team_count}:` '
#             for player in team:
#                 try:
#                     player_score_string += f'{player[0]} 0 '
#                     response_string += f'{player[0]} '
#                 except TypeError:
#                     response_string += f'(MMR: {math.ceil(player)})\n'

#         response_string+=f'\n{player_score_string}'
#     else:
#         with DBA.DBAccess() as db:
#             captains = db.query('SELECT player_name, player_id FROM (SELECT p.player_name, p.player_id, p.mmr FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s ORDER BY l.create_date ASC LIMIT %s) as mytable ORDER BY mmr DESC LIMIT 2;', (ctx.channel.id, MAX_PLAYERS_IN_MOGI))
#         response_string += f'   `Captains:` <@{captains[0][1]}> & <@{captains[1][1]}>\n'
#         response_string += f'   `Table:` /table 6 `[Team 1 players & scores]` `[Team 2 players & scores]`\n'
    
#     try:
#         with DBA.DBAccess() as db:
#             db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (response_string, ctx.channel.id))
#     except Exception as e:
#         await send_to_debug_channel(ctx, f'team generation error log 1? | {e}')
#     # choose a host
#     host_string = '    '
#     try:
#         with DBA.DBAccess() as db:
#             host_temp = db.query('SELECT fc, player_id FROM (SELECT p.fc, p.player_id FROM player p JOIN lineups l ON p.player_id = l.player_id WHERE l.tier_id = %s AND p.fc IS NOT NULL AND p.is_host_banned = %s ORDER BY l.create_date LIMIT %s) as fcs_in_mogi ORDER BY RAND() LIMIT 1;', (ctx.channel.id, 0, MAX_PLAYERS_IN_MOGI))
#             host_string += f'`Host:` <@{host_temp[0][1]}> | {host_temp[0][0]}'
#     except Exception as e:
#         host_string = '    `No FC found` - Choose amongst yourselves'
#     # create a return string
#     response_string+=f'\n\n{host_string}'
#     return response_string

# async def check_if_mogi_is_ongoing(ctx):
#     try:
#         with DBA.DBAccess() as db:
#             temp = db.query('SELECT COUNT(player_id) FROM lineups WHERE tier_id = %s;', (ctx.channel.id,))
#     except Exception:
#         return False
#     if temp[0][0] >= MAX_PLAYERS_IN_MOGI:
#         return True
#     else:
#         return False







# # Initialize the RANK_ID_LIST
# with DBA.DBAccess() as db:
#     temp = db.query('SELECT rank_id FROM ranks WHERE rank_id > %s;', (0,))
#     for i in range(len(temp)):
#         RANK_ID_LIST.append(temp[i][0])







# does not matter to put sub in lineups table
# /sub
# @client.slash_command(
#     name='sub',
#     description='Sub out a player',
#     # guild_ids=Lounge
# )
# async def sub(
#     ctx,
#     leaving_player: discord.Option(discord.Member, 'Leaving player', required=True),
#     subbing_player: discord.Option(discord.Member, 'Subbing player', required=True)
#     ):
#     await ctx.defer()
#     lounge_ban = await check_if_uid_is_lounge_banned(ctx.author.id)
#     if lounge_ban:
#         await ctx.respond(f'Unban date: <t:{lounge_ban}:F>', delete_after=30)
#         return
#     else:
#         pass
#     # Same player
#     if leaving_player.id == subbing_player.id:
#         await ctx.respond('<:bruh:1006883398607978537>')
#         return
#     # Player was already in lineup, got subbed out
#     with DBA.DBAccess() as db:
#         temp = db.query('SELECT player_id FROM sub_leaver WHERE player_id = %s;', (subbing_player.id,))
#         if temp:
#             if temp[0][0] == subbing_player.id:
#                 await ctx.respond('Player cannot sub into a mogi after being subbed out.')
#                 return
#         else:
#             pass
#     # Player exists
#     a = await check_if_uid_exists(leaving_player.id)
#     if a:
#         pass
#     else:
#         await ctx.respond('Use `/verify <mkc link>` to register for Lounge')
#         return
#     b = await check_if_uid_exists(subbing_player.id)
#     if b:
#         pass
#     else:
#         await ctx.respond(f'{subbing_player.name} is not registered for Lounge')
#         return
#     x = await check_if_mogi_is_ongoing(ctx)
#     if x:
#         pass
#     else:
#         await ctx.respond('Mogi has not started')
#         return
#     # Only players in the mogi can sub out others
#     y = await check_if_uid_in_first_12_of_tier(ctx.author.id, ctx.channel.id)
#     if y:
#         pass
#     else:
#         await ctx.respond('You are not in the mogi. You cannot sub out another player')
#         return
#     z = await check_if_uid_in_specific_tier(leaving_player.id, ctx.channel.id)
#     if z:
#         pass
#     else:
#         await ctx.respond(f'<@{leaving_player.id}> is not in this mogi.')
#         return
#     try:
#         with DBA.DBAccess() as db:
#             first_12 = db.query('SELECT player_id FROM (SELECT player_id FROM lineups WHERE tier_id = %s ORDER BY create_date ASC LIMIT 12) as l WHERE player_id = %s;', (ctx.channel.id, subbing_player.id))
#             if first_12: # if there are players in lineup (first 12)
#                 if first_12[0][0] == subbing_player.id: # if subbing is already in lineup (first 12)
#                     await ctx.respond(f'{subbing_player.mention} is already in this mogi')
#                     return
#                 else:
#                     pass
#             try:
#                 leaving_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (leaving_player.id,))[0][0]
#                 subbing_player_name = db.query('SELECT player_name FROM player WHERE player_id = %s;', (subbing_player.id,))[0][0]
#                 teams_string = db.query('SELECT teams_string FROM tier WHERE tier_id = %s;', (ctx.channel.id,))[0][0]
#                 teams_string = teams_string.replace(leaving_player_name, subbing_player_name)
#                 teams_string += f'\n\n`EDITED`: `{leaving_player_name}` -> `{subbing_player_name}`'
#                 db.execute('DELETE FROM lineups WHERE player_id = %s;', (subbing_player.id,))
#                 db.execute('UPDATE lineups SET player_id = %s WHERE player_id = %s;', (subbing_player.id, leaving_player.id))
#                 db.execute('UPDATE tier SET teams_string = %s WHERE tier_id = %s;', (teams_string, ctx.channel.id))
#             except Exception:
#                 await ctx.respond(f'``Error 42:`` FATAL ERROR - {secretly.my_discord} help!!!')
#                 return
#     except Exception as e:
#         await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {secretly.my_discord}')
#         await send_to_debug_channel(ctx, f'/sub error 19 {e}')
#         return
#     with DBA.DBAccess() as db:
#         db.execute('INSERT INTO sub_leaver (player_id, tier_id) VALUES (%s, %s);', (leaving_player.id, ctx.channel.id))
#     await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
#     await send_to_sub_log(ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}> in {ctx.channel.mention}')
#     return








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
    #                 mogi_media = client.get_channel(secretly.mogi_media_channel_id)
    #                 temp_val = asyncio.run_coroutine_threadsafe(mogi_media.send(embed=embed), client.loop)
    #                 mogi_media_message = temp_val.result()
    #                 with DBA.DBAccess() as db:
    #                     db.execute('UPDATE player SET mogi_media_message_id = %s WHERE player_id = %s;', (mogi_media_message.id, member.id))
    #         # If not live
    #         else:
    #             if stream[4] > 0: 
    #                 member_future = asyncio.run_coroutine_threadsafe(GUILD.fetch_member(stream[5]), client.loop)
    #                 member = member_future.result()               
    #                 channel = client.get_channel(secretly.mogi_media_channel_id)
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
#         asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'inactivity_check error 1 {secretly.my_discord}', e), client.loop)
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
#                         asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'inactivity_check error 2 {secretly.my_discord}', e), client.loop)
#                         return
#             else: # has not been at least 10 minutes yet
#                 continue # does this make it faster? idk
#         elif unix_difference > 1200: # if its been more than 20 minutes
#             # Drop player
#             try:
#                 with DBA.DBAccess() as db:
#                     db.execute('DELETE FROM lineups WHERE player_id = %s;', (temp[i][0],))
#             except Exception as e:
#                 asyncio.run_coroutine_threadsafe(send_raw_to_debug_channel(f'{secretly.my_discord} inactivity_check - cannot delete from lineup',f'{temp[i][0]} | {temp[i][1]} | {temp[i][2]} | {e}'), client.loop)
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







