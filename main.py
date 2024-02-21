import sys
import os
import discord
from discord.ext import commands
import logging
import DBA
import datetime
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
#           send messages, manage messages, embed links, attach files, add reactions, use slash commands
intents = discord.Intents(guilds=True, messages=True, members=True, reactions=True)
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
        await ctx.respond('Sorry! My commands do not work in DMs. Please use 200cc Lounge :)')
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
    if ctx.author == client.user: # ignore bot messages
        return
    if ctx.channel.id == 558096949337915413: # ignore carl bot logging
        return
    guild = get_lounge_guild(client)
    try:
        if ctx.guild != guild: # Only care if messages are in 200 Lounge
            return
    except Exception:
        return
    user = await guild.fetch_member(ctx.author.id)
    try:
        if get_discord_role(client, config.CHAT_RESTRICTED_ROLE_ID) in user.roles: # restricted players
            await ctx.delete()
            return
    except Exception as e:
        logging.warning(f'on_message error - could not compare chat restricted role')
    # Only care if message is in lounge queue join channel
    if ctx.channel.id == config.LOUNGE_QUEUE_JOIN_CHANNEL_ID:
        logging.info('LOUNGE QUEUE CHAT ACTIVITY DETECTED: {ctx.author}')
        # If player in lineup, set player chat activity timer
        try:
            with DBA.DBAccess() as db:
                temp = db.query('SELECT player_id FROM lounge_queue_player WHERE player_id = %s AND wait_for_activity = %s;', (ctx.author.id, 1))
        except Exception as e:
            logging.warning(f'on_message error - could not select player from lounge_queue_player | {e}')
            return
        try:
            with DBA.DBAccess() as db:
                db.execute('UPDATE lounge_queue_player SET last_active = %s, wait_for_activity = %s WHERE player_id = %s;', (datetime.datetime.now(), 0, ctx.author.id))
        except Exception as e:
            logging.warning(f'on_message error - could not update player in lounge_queue_player activity | {e}')
            await send_raw_to_debug_channel(client, ctx, f'on_message error 2 | could not update lounge_queue_player record for chat activity | {e}')
            return

@client.event
async def on_raw_reaction_add(payload):
    if int(payload.user_id) == int(client.user.id):
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
