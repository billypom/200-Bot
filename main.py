import sys
import os
import discord
from discord.ext import commands
import logging
import DBA
from helpers.senders import send_raw_to_debug_channel
from helpers.getters import get_lounge_guild
from helpers.getters import get_discord_role
from helpers import set_uid_roles
import config

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='200lounge.log', filemode='a', level=logging.INFO, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')

# os, sys | add root dir to python path to allow dynamic imports (aka i dont have to type from ..........helpers.senders.getters.etc import blah)
# i can just type from helpers.checkers import blah
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)


# Bot config
# Intents:  manage roles, manage channels, manage nicknames, read messages/viewchannels, manage events
#           send messages, manage messages, embed links, attach files, read message history, add reactions, use slash commands
intents = discord.Intents(messages=True, guilds=True, message_content=True, members=True, reactions=True)
client = discord.Bot(intents=intents, activity=discord.Game(str('200cc Lounge')))

# Load cogs  
for extension in config.LOOP_EXTENSIONS:
    client.load_extension(f'cogs.{extension}')
    
for extension in config.COMMAND_EXTENSIONS:
    client.load_extension(f'cogs.{extension}')
    
for extension in config.ADMIN_COMMAND_EXTENSIONS:
    client.load_extension(f'cogs.{extension}')

@client.event
async def on_ready():
    channel = client.get_channel(config.DEBUG_CHANNEL_ID)
    embed = discord.Embed(title='Startup', description=':3', color = discord.Color.og_blurple())
    embed.add_field(name='200-Lounge Bot Restarted', value=':D', inline=False)
    await channel.send(content=None, embed=embed)

@client.event
async def on_application_command_error(ctx, error):
    if ctx.guild is None:
        channel = client.get_channel(config.DEBUG_CHANNEL_ID)
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
        channel = client.get_channel(config.DEBUG_CHANNEL_ID)
        embed = discord.Embed(title='Error', description=':eyes:', color = discord.Color.blurple())
        embed.add_field(name='Name: ', value=ctx.author, inline=False)
        embed.add_field(name='Error: ', value=str(error), inline=False)
        embed.add_field(name='Discord ID: ', value=ctx.author.id, inline=False)
        await channel.send(content=None, embed=embed)
        await ctx.respond(f'Sorry! An unknown error occurred. Try again later or make a <#{config.SUPPORT_CHANNEL_ID}> ticket for assistance.')
        # print(traceback.format_exc())
        raise error
        return

@client.event
async def on_message(ctx):
    try:
        if ctx.guild == get_lounge_guild(client): # Only care if messages are in 200 Lounge
            pass
        else:
            return
    except Exception:
        return
    if ctx.author.id == config.BOT_ID: # ignore self messages
        return
    if ctx.channel.id == 558096949337915413: # ignore carl bot logging
        return
    user = await get_lounge_guild(client).fetch_member(ctx.author.id)
    if get_discord_role(client, config.CHAT_RESTRICTED_ROLE_ID) in user.roles: # restricted players
        # We removed allowing certain phrases because people were avoiding this functionality by
        # sending an allowed message, then editing it to harrass players. 

        # if ctx.content in config.CHAT_RESTRICTED_WORDS:
        #     return
        # else:
        await ctx.delete()
        return
    
    # Voting code - keeping this here in case we need to leave 255MP's MogiBot
    # if ctx.channel.id in await get_tier_id_list(): # Only care if messages are in a tier
    #     # If player in lineup, set player chat activity timer   
    #     try:
    #         with DBA.DBAccess() as db:
    #             temp = db.query('SELECT player_id, tier_id FROM lineups WHERE player_id = %s;', (ctx.author.id,))
    #     except Exception as e:
    #         await send_to_debug_channel(client, ctx, f'on_message error 1 | {e}')
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
    #                 await send_to_debug_channel(client, ctx, f'on_message error 2 | {e}')
    #                 return
    #     try:
    #         with DBA.DBAccess() as db:
    #             get_tier = db.query('SELECT voting, tier_id FROM tier WHERE tier_id = %s;', (ctx.channel.id,))
    #     except Exception as e:
    #         await send_to_debug_channel(client, ctx, f'on_message error 3 | {e}')
    #     # Set votes, if tier is currently voting
    #     if get_tier[0][0]:
    #         if get_tier[0][1] == ctx.channel.id:
    #             if str(ctx.content) in ['1', '2', '3', '4', '6']:
    #                 try:
    #                     with DBA.DBAccess() as db:
    #                         temp = db.query('SELECT player_id FROM lineups WHERE player_id = %s AND tier_id = %s ORDER BY create_date LIMIT %s;', (ctx.author.id, ctx.channel.id, MAX_PLAYERS_IN_MOGI)) # limit prevents 13th person from voting
    #                 except Exception as e:
    #                     await send_to_debug_channel(client, ctx, f'on_message error 4 {e}')
    #                     return
    #                 try:
    #                     with DBA.DBAccess() as db:
    #                         db.execute('UPDATE lineups SET vote = %s WHERE player_id = %s;', (int(ctx.content), ctx.author.id))
    #                 except Exception as e:
    #                     await send_to_debug_channel(client, ctx, f'on_message error 5 {e}')
    #                     return

@client.event
async def on_raw_reaction_add(payload):
    if int(payload.user_id) == int(config.BOT_ID):
        # Return if bot reaction
        return
    if payload.channel_id == config.NAME_CHANGE_CHANNEL_ID:
        pass
    else:
        # Return if this isnt a name change approval
        return

    # Stuff relating to the current embed
    guild = client.get_guild(payload.guild_id)
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    try:
        with DBA.DBAccess() as db:
            message_ids = db.query('SELECT embed_message_id, player_id, requested_name FROM player_name_request WHERE was_accepted = %s ORDER BY create_date DESC;', (0,))
    except Exception as e:
        await send_raw_to_debug_channel(client, 'Name change exception 1', e)
        return

    # Look @ all embed message ids
    for i in range(0, len(message_ids)):
        if int(payload.message_id) == int(message_ids[i][0]):
            try:
                # Accept
                if str(payload.emoji) == '✅':
                    # Edit DB player name
                    try:
                        with DBA.DBAccess() as db:
                            # Set record to accepted
                            db.execute('UPDATE player_name_request SET was_accepted = %s WHERE embed_message_id = %s;', (1, int(payload.message_id)))
                            # Change the db username
                            db.execute('UPDATE player SET player_name = %s WHERE player_id = %s;', (message_ids[i][2], message_ids[i][1]))
                    except Exception as e:
                        await send_raw_to_debug_channel(client, 'Name change exception 2', e)
                        pass
                    member = guild.get_member(message_ids[i][1])
                    # Player not in guild
                    if member is None:
                        await send_raw_to_debug_channel(client, 'Name change exception 5', 'User is not in the guild.')
                        return
                    # DM player
                    try:
                        await member.send(f'Your name change [{message_ids[i][2]}] has been approved.')
                    except Exception as e:
                        await send_raw_to_debug_channel(client, 'Name change exception 3', e)
                        pass
                    # Edit discord nickname
                    try:
                        await member.edit(nick=str(message_ids[i][2]))
                    except Exception as e:
                        await send_raw_to_debug_channel(client, 'Name change exception 4', e)
                        pass
                # Deny
                elif str(payload.emoji) == '❌':
                    with DBA.DBAccess() as db:
                        # Remove the db record
                        db.execute('DELETE FROM player_name_request WHERE embed_message_id = %s;', (int(payload.message_id),))
                        # Delete the embed message
                    member = guild.get_member(message_ids[i][1])
                    await member.send(f'Your name change [{message_ids[i][2]}] has been denied.')
                    await message.delete()
                # Any other reaction - Force an exception
                else:
                    x = int('hey')
                    x += x
            except Exception as e:
                await send_raw_to_debug_channel(client, 'Name change exception', e)
                pass
        # Decision was made, delete embed message
        try:
            #await message.remove_reaction(payload.emoji, member)
            await message.delete()
        except Exception:
            pass
    return

@client.event
async def on_member_join(member):
    # Try to set roles on join
    try:
        x = await set_uid_roles(client, member.id)
        if not x:
            return
        logging.info(f'Member joined & found! {member} ')
    except Exception as e:
        logging.info(f'on_member_join exception: {e}')
        return

if __name__ == "__main__":
    client.run(config.TOKEN)























































# # /twitch
# @client.slash_command(
#     name='twitch',
#     description='Link your Twitch stream - Enter your Username',
#     #guild_ids=LOUNGE
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
#     x = await check_if_uid_exists(ctx.author.id)
#     if x:
#         pass
#     else:
#         await ctx.respond('Use `/verify` to register with Lounge')
#         return
#     y = await check_if_banned_characters(username)
#     if y:
#         await ctx.respond("Invalid twitch username")
#         await send_to_verification_log(client, ctx, username, vlog_msg.error1)
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






















# does not matter to put sub in lineups table
# /sub
# @client.slash_command(
#     name='sub',
#     description='Sub out a player',
#     # guild_ids=LOUNGE
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
#                 await ctx.respond(f'``Error 42:`` FATAL ERROR - {config.PING_DEVELOPER} help!!!')
#                 return
#     except Exception as e:
#         await ctx.respond(f'``Error 19:`` Oops! Something went wrong. Please contact {config.PING_DEVELOPER}')
#         await send_to_debug_channel(client, ctx, f'/sub error 19 {e}')
#         return
#     with DBA.DBAccess() as db:
#         db.execute('INSERT INTO sub_leaver (player_id, tier_id) VALUES (%s, %s);', (leaving_player.id, ctx.channel.id))
#     await ctx.respond(f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}>')
#     await send_to_sub_log(client, ctx, f'<@{leaving_player.id}> has been subbed out for <@{subbing_player.id}> in {ctx.channel.mention}')
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
#             'client_id': config.TWITCH_CLIENT_ID,
#             'client_secret': config.TWITCH_CLIENT_SECRET,
#             "grant_type": 'client_credentials'
#         }
#         r = requests.post('https://id.twitch.tv/oauth2/token', body)
#         #data output
#         keys = r.json()
#         #print(keys)
#         headers = {
#             'Client-ID': config.TWITCH_CLIENT_ID,
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
